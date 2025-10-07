from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
import os
from typing import Any, Dict, List, Optional, Sequence, Tuple

from typing import Literal
from pydantic import BaseModel, Field, field_validator
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# -------------------------
# Pydantic Schemas
# -------------------------

class ClaimSpan(BaseModel):
    start: int
    end: int

class ClaimItem(BaseModel):
    id: str
    text: str
    heading: Optional[str] = None
    span: ClaimSpan
    claim_type: Optional[str] = Field(default=None)

class ClaimsInput(BaseModel):
    type: Literal["claims"] = "claims"
    version: Literal[1] = 1
    doc_path: Optional[str] = None
    claims: List[ClaimItem]

class EvidenceItem(BaseModel):
    file: Optional[str] = None
    page: Optional[str] = None
    section: Optional[str] = None
    quote: Optional[str] = None

    # Coerce numeric (or other) page values to string to avoid validation failures when JSON has ints
    @field_validator("page", mode="before")
    def _coerce_page(cls, v):  # type: ignore[override]
        if v is None:
            return v
        return str(v)

class ClaimVerdict(BaseModel):
    id: str
    heading: Optional[str] = None
    text: str
    span: ClaimSpan
    supported: str  # supported|partial|false
    citations_valid: Optional[bool] = None
    evidence: List[EvidenceItem] = Field(default_factory=list)
    rationale: Optional[str] = None
    risk: Optional[str] = None  # low|medium|high

class JudgmentMetrics(BaseModel):
    total_claims: int
    support_rate: float
    strict_precision: float
    citation_coverage: float
    unique_sources_cited: int
    avg_evidence_per_claim: float

class JudgmentReportV2(BaseModel):
    type: Literal["judgment_report"] = "judgment_report"
    version: Literal[2] = 2
    created_at: str
    context_path: str
    doc_path: str
    metrics: JudgmentMetrics
    claims: List[ClaimVerdict]
    follow_up_retrieves: List[str]

# -------------------------
# Utilities
# -------------------------

STOPWORDS = {
    "the","and","for","with","that","this","from","into","over","are","was","were","is",
    "to","of","in","on","by","at","as","an","or","be","it","a","we","you","they","their",
}

def tokenize(text: str) -> List[str]:
    return [t for t in re.findall(r"[A-Za-z0-9]{2,}", (text or "").lower()) if t not in STOPWORDS]

# -------------------------
# BM25 Implementation (simple)
# -------------------------

@dataclass
class BM25Index:
    docs_tokens: List[List[str]]
    idf: Dict[str, float]
    avgdl: float
    k1: float = 1.5
    b: float = 0.75

    def score(self, query_tokens: Sequence[str], doc_idx: int) -> float:
        tokens = self.docs_tokens[doc_idx]
        dl = len(tokens) or 1
        tf: Dict[str, int] = {}
        for t in tokens:
            tf[t] = tf.get(t, 0) + 1
        s = 0.0
        for q in query_tokens:
            if q not in self.idf:
                continue
            f = tf.get(q, 0)
            if f == 0:
                continue
            idf = self.idf[q]
            denom = f + self.k1 * (1 - self.b + self.b * dl / self.avgdl)
            s += idf * (f * (self.k1 + 1)) / (denom or 1)
        return s


def build_bm25(texts: List[str]) -> BM25Index:
    docs_tokens = [tokenize(t) for t in texts]
    N = max(1, len(docs_tokens))
    df: Dict[str, int] = {}
    total_len = 0
    for toks in docs_tokens:
        total_len += len(toks)
        seen = set()
        for t in toks:
            if t in seen:
                continue
            df[t] = df.get(t, 0) + 1
            seen.add(t)
    idf: Dict[str, float] = {}
    for term, dfi in df.items():
        idf[term] = math.log(1 + (N - dfi + 0.5) / (dfi + 0.5))
    avgdl = total_len / N
    return BM25Index(docs_tokens=docs_tokens, idf=idf, avgdl=avgdl)

# -------------------------
# Embedding Utilities (llama_index Settings)
# -------------------------

def compute_embeddings(texts: List[str]) -> Optional[List[List[float]]]:
    try:
        from llama_index.core import Settings as _Settings  # type: ignore
    except Exception:
        return None
    embed_model = getattr(_Settings, "embed_model", None)
    if embed_model is None:
        return None
    # Try batch first, then fallback element-wise
    try:
        if hasattr(embed_model, "get_text_embedding_batch"):
            return embed_model.get_text_embedding_batch(texts)
    except Exception:
        pass
    try:
        if hasattr(embed_model, "get_text_embedding"):
            return [embed_model.get_text_embedding(t) for t in texts]
    except Exception:
        return None
    return None


def embed_query(text: str) -> Optional[List[float]]:
    try:
        from llama_index.core import Settings as _Settings  # type: ignore
    except Exception:
        return None
    embed_model = getattr(_Settings, "embed_model", None)
    if embed_model is None:
        return None
    try:
        if hasattr(embed_model, "get_query_embedding"):
            return embed_model.get_query_embedding(text)
        if hasattr(embed_model, "get_text_embedding"):
            return embed_model.get_text_embedding(text)
    except Exception:
        return None
    return None


def cosine(a: Sequence[float], b: Sequence[float]) -> float:
    if not a or not b:
        return 0.0
    num = 0.0
    da = 0.0
    db = 0.0
    for x, y in zip(a, b):
        num += x * y
        da += x * x
        db += y * y
    if da <= 0 or db <= 0:
        return 0.0
    return max(-1.0, min(1.0, num / math.sqrt(da * db)))

# -------------------------
# LLM Adjudication
# -------------------------

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type(Exception),
)
def llm_adjudicate(claim_text: str, candidates: List[EvidenceItem], max_evidence: int = 3) -> Optional[Dict[str, Any]]:
    """Call configured LLM to adjudicate a claim. Returns dict or None on failure."""
    try:
        from llama_index.core import Settings as _Settings  # type: ignore
    except Exception:
        return None
    # Accessing Settings.llm can trigger default model resolution requiring API keys.
    # Guard it to avoid failures in keyless test environments.
    try:
        llm = getattr(_Settings, "llm", None)
    except Exception:
        llm = None
    if llm is None:
        return None
    snippets = []
    for c in candidates[: max(1, max_evidence * 3)]:
        # keep short quotes in prompt
        quote = (c.quote or "")[:400]
        meta = f"file={c.file or ''}; page={c.page or ''}; section={c.section or ''}"
        snippets.append(f"- {meta}\n  quote: {quote}")
    prompt = (
        "Return ONLY JSON with keys supported, evidence, rationale, risk.\n"
        f"Claim: {claim_text}\n"
        f"Candidate snippets (each has file/page/section/quote):\n" + "\n".join(snippets) + "\n"
        "A claim is supported only if at least one snippet directly and explicitly states the claim."
        " Otherwise use partial (indirect or incomplete) or false.\n"
        f"Return up to {max_evidence} evidence snippets that directly support the claim, copying the exact quote text.\n"
        "Risk reflects downstream risk if the claim is wrong: low|medium|high."
    )
    try:
        if hasattr(llm, "complete_json"):
            resp = llm.complete_json(prompt)  # type: ignore[attr-defined]
            raw = getattr(resp, "text", getattr(resp, "json", "{}"))
        else:
            resp = llm.complete(prompt)
            raw = getattr(resp, "text", str(resp))
        data = json.loads(raw)
        if isinstance(data, dict) and "supported" in data:
            return data
    except Exception:
        # one minimal repair attempt
        try:
            repair = "Return only JSON with keys supported,evidence,rationale,risk; supported in {supported,partial,false}."
            resp2 = llm.complete(repair)
            data2 = json.loads(getattr(resp2, "text", str(resp2)))
            if isinstance(data2, dict) and "supported" in data2:
                return data2
        except Exception:
            return None
    return None

# -------------------------
# Command Synthesis
# -------------------------

def windows_retrieve_command(
    query: str,
    indexes: List[str],
    out_path: str,
    top_k: int = 40,
    rerank_top_n: int = 20,
    llm_provider: Optional[str] = None,
    llm_model: Optional[str] = None,
    *,
    # Advanced retrieval flags (all optional; included only when provided)
    retrieval_mode: Optional[str] = None,
    dense_k: Optional[int] = None,
    sparse_k: Optional[int] = None,
    alpha: Optional[float] = None,
    include_terms: Optional[str] = None,
    exclude_sections: Optional[str] = None,
    filters: Optional[str] = None,
    infer_filters: Optional[bool] = None,
    expand_queries: Optional[int] = None,
    hyde: Optional[bool] = None,
) -> str:
    idx = ",".join(indexes) if indexes else "design"
    q = query.replace('"', '\\"')
    # Use only supported flags on the CLI
    # Prefer cohere reranker when key is present; else disable
    use_cohere = bool(os.getenv("COHERE_API_KEY"))
    rerank_flag = "cohere" if use_cohere else "none"
    prov_flags = ""
    if llm_provider:
        prov_flags += f" --llm-provider {llm_provider}"
    if llm_model:
        prov_flags += f" --llm-model {llm_model}"
    adv = []
    if retrieval_mode:
        adv.append(f"--retrieval-mode {retrieval_mode}")
    if isinstance(dense_k, int):
        adv.append(f"--dense-k {int(dense_k)}")
    if isinstance(sparse_k, int):
        adv.append(f"--sparse-k {int(sparse_k)}")
    if isinstance(alpha, (int, float)):
        adv.append(f"--alpha {float(alpha)}")
    if include_terms and include_terms.strip():
        adv.append(f"--include-terms \"{include_terms.strip()}\"")
    if exclude_sections and exclude_sections.strip():
        adv.append(f"--exclude-sections \"{exclude_sections.strip()}\"")
    if filters and filters.strip():
        # Pass as-is; user must provide valid JSON
        adv.append(f"--filters '{filters.strip()}'")
    if infer_filters is True:
        adv.append("--infer-filters")
    if isinstance(expand_queries, int):
        adv.append(f"--expand-queries {int(expand_queries)}")
    if hyde is False:
        adv.append("--no-hyde")
    elif hyde is True:
        adv.append("--hyde")
    adv_str = (" " + " ".join(adv)) if adv else ""
    return (
        f"poetry run caliper_v2{prov_flags} retrieve \"{q}\" --indexes \"{idx}\" --cloud "
        f"--top-k {top_k} --reranker {rerank_flag} --reranker-top-n {rerank_top_n}{adv_str} --out \"{out_path}\""
    )


def windows_retrieve_argv(
    query: str,
    indexes: List[str],
    out_path: str,
    top_k: int = 40,
    rerank_top_n: int = 20,
    llm_provider: Optional[str] = None,
    llm_model: Optional[str] = None,
    *,
    retrieval_mode: Optional[str] = None,
    dense_k: Optional[int] = None,
    sparse_k: Optional[int] = None,
    alpha: Optional[float] = None,
    include_terms: Optional[str] = None,
    exclude_sections: Optional[str] = None,
    filters: Optional[str] = None,
    infer_filters: Optional[bool] = None,
    expand_queries: Optional[int] = None,
    hyde: Optional[bool] = None,
) -> List[str]:
    """Windows-safe argv for retrieval CLI (avoids shell quoting issues)."""
    idx = ",".join(indexes) if indexes else "design"
    use_cohere = bool(os.getenv("COHERE_API_KEY"))
    rerank_flag = "cohere" if use_cohere else "none"

    argv: List[str] = ["poetry", "run", "caliper_v2"]
    if llm_provider:
        argv += ["--llm-provider", llm_provider]
    if llm_model:
        argv += ["--llm-model", llm_model]
    argv += [
        "retrieve",
        query,
        "--indexes", idx,
        "--cloud",
        "--top-k", str(int(top_k)),
        "--reranker", rerank_flag,
        "--reranker-top-n", str(int(rerank_top_n)),
    ]
    # Advanced flags appended only when provided
    if retrieval_mode:
        argv += ["--retrieval-mode", retrieval_mode]
    if isinstance(dense_k, int):
        argv += ["--dense-k", str(int(dense_k))]
    if isinstance(sparse_k, int):
        argv += ["--sparse-k", str(int(sparse_k))]
    if isinstance(alpha, (int, float)):
        argv += ["--alpha", str(float(alpha))]
    if include_terms and include_terms.strip():
        argv += ["--include-terms", include_terms.strip()]
    if exclude_sections and exclude_sections.strip():
        argv += ["--exclude-sections", exclude_sections.strip()]
    if filters and filters.strip():
        argv += ["--filters", filters.strip()]
    if infer_filters is True:
        argv += ["--infer-filters"]
    if isinstance(expand_queries, int):
        argv += ["--expand-queries", str(int(expand_queries))]
    if hyde is False:
        argv += ["--no-hyde"]
    elif hyde is True:
        argv += ["--hyde"]
    argv += ["--out", out_path]
    return argv
