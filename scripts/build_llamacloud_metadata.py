"""
Standalone builder for LlamaCloud metadata CSV.

- Scans a root directory for .md artifacts (e.g., LlamaParse outputs)
- Extracts metadata via heuristics
- Optionally enriches missing fields using a local LLM via LM Studio (OpenAI-compatible API)
- Writes a CSV with columns [file_path, metadata] suitable for LlamaCloud → Files → Import Metadata

This script is intentionally standalone and does not modify any existing Caliper files.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import pandas as pd


# ------------------------------- Heuristics & Regex -------------------------------
_CITATION_RX = re.compile(
    r"(WAC\s*\d{3}-\d{3}(?:-\d+)?|RCW\s*\d{2}\.\d{2}\.\d{3}|\d+\s*CFR\s*\d+(?:\.\d+)*)",
    re.IGNORECASE,
)
_DATE_RX = re.compile(
    r"\b(Revised|Issued|Adopted|Last\s*Update)\s*[:\-]?\s*("  # label
    r"[A-Za-z]+\s+\d{4}"                                     # Month YYYY
    r"|\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}"                 # M/D/YYYY or similar
    r")",
    re.IGNORECASE,
)
_PUB_RX = re.compile(r"\b(Publication\s*#|Pub(?:lication)?\s*No\.?|EPA\/[A-Z0-9\-]+)\s*([A-Za-z0-9\.\-\/]+)?", re.IGNORECASE)

_AGENCY_HINTS = [
    r"Washington State Department of Ecology",
    r"\bDepartment of Ecology\b",
    r"\bEcology\b",
    r"\bEPA\b",
    r"Environmental Protection Agency",
    r"Department of Commerce",
]

_PROGRAM_HINTS: List[Tuple[str, str]] = [
    (r"\bSRF\b", "SRF"),
    (r"\bPWTF\b", "PWTF"),
    (r"\bUSDA\b", "USDA RD"),
    (r"\bWIFIA\b", "WIFIA"),
]

_DOC_TYPES: List[str] = [
    "regulation",
    "statute",
    "guidance",
    "permit",
    "plan",
    "spec",
]

# Content allow-list and boilerplate patterns
_ALLOW_TYPES = {"heading", "title", "paragraph", "text", "list_item", "table"}
_COMMON_BOILERPLATE_RX = [
    r"^\s*(page|p\.)\s*\d+(\s*of\s*\d+)?\s*$",
    r"^\s*this page intentionally left blank\s*$",
    r"^\s*copyright\b.*$",
    r"^\s*confidential\b.*$",
    r"^\s*(revised|issued|adopted|last\s*update)\s*[:\-].*$",
    r"^[\-\u2013\u2014\_.]{3,}\s*$",
    r"^\s*(washington state department of ecology|department of ecology|epa)\s*$",
]
_CBP = [re.compile(rx, re.IGNORECASE) for rx in _COMMON_BOILERPLATE_RX]


def _read_text(path: str) -> str:
    try:
        return open(path, "r", encoding="utf-8", errors="ignore").read()
    except Exception:
        return ""


def _slugify_topic(s: str) -> Optional[str]:
    s = re.sub(r"[\s\u2013\u2014\-]+", "_", s.strip().lower())
    s = re.sub(r"[^a-z0-9_]", "", s)
    if not s or len(s) < 3:
        return None
    # filter generic headings
    GENERIC = {
        "definitions",
        "introduction",
        "overview",
        "purpose",
        "scope",
        "appendix",
        "table_of_contents",
        "toc",
        "references",
        "acronyms",
    }
    return None if s in GENERIC else s


def _extract_md_fields(md_text: str) -> Tuple[Optional[str], Optional[str], List[str], List[str], Optional[str], str]:
    """Return (title, month_year, citations, topics, agency, program)."""
    # Some MD artifacts are JSON wrappers like {"markdown": "..."}
    try:
        test = md_text.strip()
        if test.startswith("{") and test.endswith("}"):
            maybe = json.loads(test)
            if isinstance(maybe, dict):
                md_text = str(maybe.get("markdown") or maybe.get("text") or md_text)
    except Exception:
        pass
    title: Optional[str] = None
    for line in md_text.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break

    m_date = _DATE_RX.search(md_text)
    month_year = m_date.group(2) if m_date else None

    cites = sorted(set(_CITATION_RX.findall(md_text)))

    # Collect H2 and H3 headings as topic candidates
    topics_raw: List[str] = []
    for rx in (r"^##\s+(.+)$", r"^###\s+(.+)$"):
        topics_raw.extend([m.group(1) for m in re.finditer(rx, md_text, re.MULTILINE)])
    topics_slugs: List[str] = []
    seen: set[str] = set()
    for t in topics_raw:
        slug = _slugify_topic(t)
        if slug and slug not in seen:
            topics_slugs.append(slug)
            seen.add(slug)

    agency: Optional[str] = None
    for rx in _AGENCY_HINTS:
        m = re.search(rx, md_text, re.IGNORECASE)
        if m:
            g = m.group(0)
            agency = "WA Ecology" if "Ecology" in g else ("EPA" if "EPA" in g else g)
            break

    program = "None"
    for rx, tag in _PROGRAM_HINTS:
        if re.search(rx, md_text, re.IGNORECASE):
            program = tag
            break

    return title, month_year, cites, topics_slugs, agency, program


def _json_topics(json_path: str) -> List[str]:
    try:
        data = json.load(open(json_path, "r", encoding="utf-8"))
    except Exception:
        return []

    topics: List[str] = []

    def _add_topic(s: str) -> None:
        slug = _slugify_topic(s)
        if slug:
            topics.append(slug)

    for key in ("headings", "outline", "toc", "sections"):
        if isinstance(data.get(key), list):
            for h in data[key]:
                text = h.get("text") if isinstance(h, dict) else str(h)
                _add_topic(text)

    # Fallback: pages/elements structure commonly emitted by LlamaParse
    if not topics and isinstance(data.get("pages"), list):
        try:
            for page in data["pages"]:
                for el in page.get("elements", []):
                    el_type = str(el.get("type", "")).lower()
                    if el_type in ("heading", "title"):
                        _add_topic(el.get("text", ""))
        except Exception:
            pass

    if not topics and "title" in data:
        _add_topic(str(data["title"]))

    seen_t: set[str] = set()
    uniq: List[str] = []
    for t in topics:
        if t not in seen_t:
            uniq.append(t)
            seen_t.add(t)
    return uniq[:12]


def _normalize_agency(value: Optional[str]) -> Optional[str]:
    if not value:
        return value
    v = str(value).strip().lower()
    if "ecology" in v:
        return "WA Ecology"
    if "epa" in v or "environmental protection agency" in v:
        return "EPA"
    return value


def _normalize_topics(topics: List[str], max_topics: int = 8) -> List[str]:
    """Normalize topic slugs: strip numeric prefixes, tidy common terms, dedupe, cap.

    Assumes inputs are already slug-like (lowercase with underscores) from _slugify_topic/_json_topics.
    """
    cleaned: List[str] = []
    seen: set[str] = set()
    for t in topics:
        if not t:
            continue
        s = re.sub(r"^\d+_+", "", t)  # drop leading chapter numbers like '80_'
        if s == "references":
            s = "refs"
        # drop very short slugs
        if len(s) < 3:
            continue
        if s not in seen:
            cleaned.append(s)
            seen.add(s)
        if len(cleaned) >= max_topics:
            break
    return cleaned


def _json_text(json_path: str, max_chars: int = 60000) -> str:
    """Extract a plain-text snippet from a LlamaParse JSON (pages/elements).

    Collects heading/title/paragraph/list/text-like elements and joins them.
    """
    try:
        data = json.load(open(json_path, "r", encoding="utf-8"))
    except Exception:
        return ""

    parts: List[str] = []
    try:
        if isinstance(data.get("pages"), list):
            for page_idx, page in enumerate(data["pages"]):
                # Prefer items; fallback to elements
                items = page.get("items") or page.get("elements") or []
                for el in items:
                    el_type = str(el.get("type", "")).lower()
                    if el_type not in _ALLOW_TYPES:
                        continue
                    if el_type == "table":
                        # Optionally convert rows to simple TSV lines for topic hints
                        rows = el.get("rows") or []
                        if rows and isinstance(rows, list):
                            try:
                                for r in rows[:10]:
                                    if isinstance(r, list):
                                        parts.append("\t".join(str(c) for c in r))
                            except Exception:
                                pass
                        continue
                    t = (el.get("md") or el.get("value") or el.get("text") or "").strip()
                    if t:
                        parts.append(str(t))

                # Last resort: page-level md/text when no structured items
                if not items:
                    for k in ("md", "text"):
                        if page.get(k):
                            parts.append(str(page[k]))
                            break
    except Exception:
        pass

    text = "\n\n".join(parts)
    if len(text) > max_chars:
        text = text[:max_chars]
    return text


def _extract_text_fields(text: str) -> Tuple[Optional[str], Optional[str], List[str], Optional[str], str]:
    """Return (month_year, citations, agency, program) from generic text.

    Title is not derived for generic text, so we return None for it.
    """
    m_date = _DATE_RX.search(text)
    month_year = m_date.group(2) if m_date else None

    cites = sorted(set(_CITATION_RX.findall(text)))

    agency: Optional[str] = None
    for rx in _AGENCY_HINTS:
        m = re.search(rx, text, re.IGNORECASE)
        if m:
            g = m.group(0)
            agency = "WA Ecology" if "Ecology" in g else ("EPA" if "EPA" in g else g)
            break

    program = "None"
    for rx, tag in _PROGRAM_HINTS:
        if re.search(rx, text, re.IGNORECASE):
            program = tag
            break

    return month_year, cites, agency, program


def _scan_header_footer_for_meta(page_md: str, meta: Dict[str, object]) -> None:
    if not page_md:
        return
    m = _DATE_RX.search(page_md)
    if m and not meta.get("effective_date"):
        meta["effective_date_raw"] = m.group(2)
    p = _PUB_RX.search(page_md)
    if p and not meta.get("publication_id"):
        meta["publication_id"] = (p.group(2) or p.group(1)).strip()


def _dedupe_short_repeaters(lines: List[str], min_len: int = 25, repeat_threshold: float = 0.5) -> List[str]:
    from collections import Counter
    normalized = [re.sub(r"\s+", " ", ln.strip()) for ln in lines if ln and ln.strip()]
    ctr = Counter(normalized)
    total = max(1, len(normalized))
    drop = {ln for ln, c in ctr.items() if len(ln) < min_len and (c / total) > repeat_threshold}
    return [ln for ln in lines if re.sub(r"\s+", " ", (ln or "").strip()) not in drop]


def _guess_doc_type(name: str, path: str, cites: Sequence[str]) -> str:
    low = (name + " " + path).lower()
    if any("cfr" in c.lower() for c in cites) or "federal" in low:
        return "regulation"
    if "wac" in low:
        return "regulation"
    if "rcw" in low:
        return "statute"
    if re.search(r"permit|npdes|fact\s*sheet", low):
        return "permit"
    if re.search(r"plan|engineering\s*report|facility\s*plan", low):
        return "plan"
    if re.search(r"guidance|manual|handbook|criteria|standard|policy", low):
        return "guidance"
    return "spec"


def _guess_jurisdiction(cites: Sequence[str], path: str) -> str:
    low = path.lower()
    if any((("wac" in c.lower()) or ("rcw" in c.lower())) for c in cites) or "washington" in low or re.search(r"\bwa\b", low):
        return "WA"
    if any("cfr" in c.lower() for c in cites) or "federal" in low or "epa" in low:
        return "US"
    return "Unknown"


def _norm_effective_date(month_year: Optional[str]) -> Optional[str]:
    if not month_year:
        return None
    try:
        dt = pd.to_datetime(month_year, errors="coerce")
        return dt.strftime("%Y-%m-01") if pd.notna(dt) else None
    except Exception:
        return None


def _pick_source(base: str, preferred_extensions: Sequence[str]) -> str:
    """Return best source path by checking for existing files in order.

    Falls back to the first preferred extension if none found.
    """
    for ext in preferred_extensions:
        ext_norm = ext if ext.startswith(".") else f".{ext}"
        cand = base + ext_norm
        if os.path.exists(cand):
            return cand
    # fallback to first option
    first_ext = preferred_extensions[0] if preferred_extensions else ".pdf"
    first_ext = first_ext if str(first_ext).startswith(".") else f".{first_ext}"
    return base + str(first_ext)


def _llm_enrich_if_needed(meta: Dict[str, object], md_text: str, url: str, model: str) -> Dict[str, object]:
    needed_keys = [
        k
        for k in ("agency", "jurisdiction", "doc_type", "effective_date", "program")
        if meta.get(k) in (None, "", "Unknown")
    ]
    if not needed_keys:
        return meta

    print(f" [LLM enriching {len(needed_keys)} fields]", end="", flush=True)
    try:
        from openai import OpenAI  # type: ignore

        # Allow OpenAI or LM Studio interchangeable via URL and environment
        api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("LM_STUDIO_API_KEY") or "lm-studio"
        client = OpenAI(base_url=url, api_key=api_key)
        snippet_blocks = md_text.split("\n\n", 80)
        snippet = "\n\n".join(snippet_blocks[:80])

        allowed_doc_types = ", ".join(_DOC_TYPES)
        allowed_programs = ", ".join([p for _, p in _PROGRAM_HINTS] + ["None"])

        sys_msg = (
            "You label wastewater-planning documents for retrieval. "
            "Output ONLY a minified JSON object with exactly the requested keys. "
            "If unknown, use null (or 'None' for program). No prose."
        )
        user_msg = (
            f"Fill ONLY these keys: {', '.join(needed_keys)}\n"
            "Rules:\n"
            f"- doc_type ∈ [{allowed_doc_types}]\n"
            "- jurisdiction \"WA\" or \"US\" when obvious\n"
            "- effective_date must be ISO YYYY-MM-DD or null\n"
            f"- program ∈ [{allowed_programs}]\n\n"
            "TEXT:\n<<<\n" + snippet + "\n>>>"
        )

        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": sys_msg}, {"role": "user", "content": user_msg}],
            temperature=0.2,
            max_tokens=400,
        )
        raw = resp.choices[0].message.content.strip()
        if not raw.startswith("{") and "{" in raw and "}" in raw:
            raw = raw[raw.find("{") : raw.rfind("}") + 1]
        data = json.loads(raw)

        if data.get("doc_type") not in _DOC_TYPES:
            data["doc_type"] = None

        valid_programs = [p for _, p in _PROGRAM_HINTS] + ["None"]
        if data.get("program") not in valid_programs:
            data["program"] = "None"

        if isinstance(data.get("jurisdiction"), str):
            j = str(data["jurisdiction"]).upper()
            data["jurisdiction"] = "WA" if "WA" in j else ("US" if ("US" in j or "UNITED" in j) else None)

        if data.get("effective_date"):
            try:
                dt = pd.to_datetime(data["effective_date"], errors="coerce")
                data["effective_date"] = dt.strftime("%Y-%m-%d") if pd.notna(dt) else None
            except Exception:
                data["effective_date"] = None

        for k in needed_keys:
            v = data.get(k)
            if v not in (None, "", [], {}):
                meta[k] = v
    except Exception:
        # Silent failure: enrichment is optional
        pass
    return meta


@dataclass
class Args:
    root: str
    out: str
    use_llm: bool
    lmstudio_url: str
    lmstudio_model: str
    source_ext: str
    file_path_mode: str  # basename | relative | full
    include_json_only: bool


def _parse_args() -> Args:
    ap = argparse.ArgumentParser(description="Build LlamaCloud metadata CSV from parsed artifacts")
    ap.add_argument("--root", required=True, help="Root directory containing .md artifacts (recursive)")
    ap.add_argument("--out", required=True, help="Output CSV path for LlamaCloud Import Metadata")
    ap.add_argument("--use-llm", action="store_true", help="Use LM Studio to fill unknown fields")
    ap.add_argument("--lmstudio-url", default="http://localhost:1234/v1", help="LM Studio base URL")
    ap.add_argument("--lmstudio-model", default="local-model-id", help="LM Studio model id")
    ap.add_argument(
        "--source-ext",
        default=".pdf",
        help="Extension for the original uploaded files to map metadata to (default: .pdf)",
    )
    ap.add_argument(
        "--file-path-mode",
        choices=["basename", "relative", "full"],
        default="basename",
        help="How to emit file_path in the CSV (default: basename, matching common LlamaCloud behavior)",
    )
    ap.add_argument(
        "--include-json-only",
        action="store_true",
        help="Also include documents that only have a .json (no .md) artifact",
    )
    a = ap.parse_args()
    return Args(
        root=a.root,
        out=a.out,
        use_llm=bool(a.use_llm),
        lmstudio_url=a.lmstudio_url,
        lmstudio_model=a.lmstudio_model,
        source_ext=a.source_ext if a.source_ext.startswith(".") else f".{a.source_ext}",
        file_path_mode=a.file_path_mode,
        include_json_only=bool(a.include_json_only),
    )


def _build_row_for_md(md_path: str, args: Args) -> Optional[Dict[str, object]]:
    base, _ = os.path.splitext(md_path)
    # Prefer the requested source extension, but auto-detect if others exist
    preferred_exts = [args.source_ext, ".pdf", ".docx", ".pptx"]
    source_path = _pick_source(base, preferred_exts)
    json_path = base + ".json"

    md = _read_text(md_path)
    title, month_year, cites, topics_md, agency_md, program_md = _extract_md_fields(md)
    topics_json = _json_topics(json_path) if os.path.exists(json_path) else []
    # Prefer JSON headings; fallback to MD headings; only then default to ["design"].
    topics_combined: List[str] = topics_json or topics_md
    if not topics_combined:
        topics_combined = ["design"]
    # Normalize, de-duplicate, cap
    topics = _normalize_topics(topics_combined, max_topics=8)
    if not topics:
        topics = ["engineering_report", "effluent_limits", "hydraulic_loading"]

    doc_type = _guess_doc_type(os.path.basename(md_path), md_path, cites)
    jurisdiction = _guess_jurisdiction(cites, md_path)
    effective = _norm_effective_date(month_year)

    agency = _normalize_agency(agency_md) or ("WA Ecology" if jurisdiction == "WA" else ("EPA" if jurisdiction == "US" else "Unknown"))
    program = program_md or "None"
    quality = "gold" if doc_type in ("regulation", "statute") else "secondary"

    meta: Dict[str, object] = {
        "doc_type": doc_type,
        "agency": agency,
        "jurisdiction": jurisdiction,
        "program": program,
        "topic": topics,
        "citation": "; ".join(cites),
        "effective_date": effective,
        "version": "from_md",
        "is_superseded": False,
        "quality": quality,
    }

    if args.use_llm:
        meta = _llm_enrich_if_needed(meta, md, args.lmstudio_url, args.lmstudio_model)

    # Jurisdiction fallback: EPA implies US
    if (agency == "EPA") and (jurisdiction in (None, "", "Unknown")):
        jurisdiction = "US"

    # Compute file_path as requested
    if args.file_path_mode == "basename":
        file_path_out = os.path.basename(source_path)
    elif args.file_path_mode == "relative":
        rel = os.path.relpath(source_path, args.root)
        file_path_out = rel.replace("\\", "/")
    else:  # full
        file_path_out = source_path

    return {"file_path": file_path_out, "metadata": json.dumps(meta, separators=(",", ":"))}


def _build_row_for_json(json_path: str, args: Args) -> Optional[Dict[str, object]]:
    base, _ = os.path.splitext(json_path)
    preferred_exts = [args.source_ext, ".pdf", ".docx", ".pptx"]
    source_path = _pick_source(base, preferred_exts)
    
    # Extract content blocks and header/footer metadata
    try:
        data = json.load(open(json_path, "r", encoding="utf-8"))
    except Exception:
        data = {"pages": []}

    texts: List[str] = []
    # Scan first 3 pages' headers/footers for metadata only
    meta_from_hf: Dict[str, object] = {}
    for i, page in enumerate(data.get("pages", [])):
        if i < 3:
            for hk in ("pageHeaderMarkdown", "pageFooterMarkdown"):
                if page.get(hk):
                    _scan_header_footer_for_meta(str(page.get(hk)), meta_from_hf)

        # Gather content from items/elements, skipping headers/footers
        items = page.get("items") or page.get("elements") or []
        for el in items:
            t = str(el.get("type", "")).lower()
            if t not in _ALLOW_TYPES:
                continue
            if t == "table":
                # Convert a few rows to inline text for topic hints
                rows = el.get("rows") or []
                for r in rows[:10]:
                    if isinstance(r, list):
                        texts.append("\t".join(str(c) for c in r))
                continue
            txt = (el.get("md") or el.get("value") or el.get("text") or "").strip()
            if txt:
                texts.append(txt)

        if not items:
            for k in ("md", "text"):
                if page.get(k):
                    texts.append(str(page[k]))
                    break

    # Light boilerplate removal
    per_line = []
    for t in texts:
        per_line.extend([ln for ln in (t.splitlines()) if ln and ln.strip()])
    per_line = _dedupe_short_repeaters(per_line, min_len=25, repeat_threshold=0.5)
    cleaned_text = "\n".join(per_line)

    topics_raw = _json_topics(json_path)
    topics = _normalize_topics(topics_raw, max_topics=8)
    if not topics:
        topics = ["engineering_report", "effluent_limits", "hydraulic_loading"]
    month_year, cites, agency_j, program_j = _extract_text_fields(cleaned_text)

    doc_type = _guess_doc_type(os.path.basename(json_path), json_path, cites)
    jurisdiction = _guess_jurisdiction(cites, json_path)
    effective = _norm_effective_date(month_year)

    agency = _normalize_agency(agency_j) or ("WA Ecology" if jurisdiction == "WA" else ("EPA" if jurisdiction == "US" else "Unknown"))
    program = program_j or "None"
    quality = "gold" if doc_type in ("regulation", "statute") else "secondary"

    meta: Dict[str, object] = {
        "doc_type": doc_type,
        "agency": agency,
        "jurisdiction": jurisdiction,
        "program": program,
        "topic": topics[:12] or ["design"],
        "citation": "; ".join(cites),
        "effective_date": effective,
        "version": "from_json",
        "is_superseded": False,
        "quality": quality,
    }
    # Jurisdiction fallback: EPA implies US
    if (agency == "EPA") and (jurisdiction in (None, "", "Unknown")):
        jurisdiction = "US"

    # Merge early header/footer-derived metadata
    if meta_from_hf.get("effective_date_raw") and not meta.get("effective_date"):
        meta["effective_date"] = _norm_effective_date(str(meta_from_hf["effective_date_raw"]))
    if meta_from_hf.get("publication_id"):
        meta["publication_id"] = meta_from_hf["publication_id"]

    if args.use_llm:
        meta = _llm_enrich_if_needed(meta, cleaned_text, args.lmstudio_url, args.lmstudio_model)

    if args.file_path_mode == "basename":
        file_path_out = os.path.basename(source_path)
    elif args.file_path_mode == "relative":
        rel = os.path.relpath(source_path, args.root)
        file_path_out = rel.replace("\\", "/")
    else:
        file_path_out = source_path

    return {"file_path": file_path_out, "metadata": json.dumps(meta, separators=(",", ":"))}


def main() -> None:
    args = _parse_args()

    rows: List[Dict[str, object]] = []
    total_md = 0
    seen_basenames: set[str] = set()
    print(f"Scanning {args.root} for artifacts...")
    for dirpath, _, files in os.walk(args.root):
        for fn in files:
            # Skip hidden/dotfile artifacts like '.md' that can appear from malformed downloads
            if fn.startswith('.'):
                continue
            if fn.lower().endswith(".md"):
                total_md += 1
                md_path = os.path.join(dirpath, fn)
                print(f"Processing: {fn}", end="", flush=True)
                row = _build_row_for_md(md_path, args)
                if row is not None:
                    rows.append(row)
                    seen_basenames.add(os.path.splitext(os.path.basename(md_path))[0])
                    print(" ✓")
                else:
                    print(" (skipped)")

    if args.include_json_only:
        print("\nScanning for JSON-only documents...")
        for dirpath, _, files in os.walk(args.root):
            for fn in files:
                if fn.startswith('.'):
                    continue
                if not fn.lower().endswith(".json"):
                    continue
                base_no_ext = os.path.splitext(fn)[0]
                if base_no_ext in seen_basenames:
                    continue  # already handled via .md neighbor
                json_path = os.path.join(dirpath, fn)
                print(f"Processing JSON-only: {fn}", end="", flush=True)
                row = _build_row_for_json(json_path, args)
                if row is not None:
                    rows.append(row)
                    print(" ✓")
                else:
                    print(" (skipped)")

    pd.DataFrame(rows).to_csv(args.out, index=False)
    print(f"\nScanned {total_md} .md files; wrote {len(rows)} rows → {args.out}")


if __name__ == "__main__":
    main()


