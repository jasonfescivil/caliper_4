from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple
import hashlib

from loguru import logger

try:
    import llama_cloud_services as lcs  # type: ignore
except Exception as exc:  # pragma: no cover
    lcs = None  # type: ignore
    logger.warning("llama_cloud_services not available: {}", exc)


@dataclass
class CloudDoc:
    index: str
    doc_id: str
    title: Optional[str]
    meta: Dict[str, str]


class LlamaCloudExporter:
    """Export documents from LlamaCloud to a local Markdown corpus.

    Notes:
    - You must set LLAMA_CLOUD_API_KEY in your environment.
    - This PoC targets a simple API surface: list documents and fetch text chunks.
    - It writes a manifest and a small cache for resumability.
    """

    def __init__(self, out_corpus: str, indexes: List[str], layer: str = "base",
                 max_docs: Optional[int] = None, resume: bool = True, sleep_s: float = 0.25):
        self.out = Path(out_corpus).resolve()
        self.out.mkdir(parents=True, exist_ok=True)
        self.indexes = indexes
        self.layer = layer
        self.max_docs = max_docs
        self.resume = resume
        self.sleep_s = sleep_s
        self.manifest = self.out / "manifest.json"
        self.cache = self.out / ".export_cache.json"
        self.client = None
        self._state: Dict[str, Dict[str, str]] = {}  # {index: {doc_id: sha}}

        if self.cache.exists():
            try:
                self._state = json.loads(self.cache.read_text(encoding="utf-8"))
            except Exception:
                self._state = {}

    # --- LlamaCloud API bootstrap ---
    def _ensure_client(self):
        if self.client is not None:
            return
        api_key = os.getenv("LLAMA_CLOUD_API_KEY")
        if not api_key:
            raise RuntimeError("LLAMA_CLOUD_API_KEY not set")
        if lcs is None:
            raise RuntimeError("llama_cloud_services client not available in environment")
        # Prefer Index client for listing/fetching
        try:
            # Attempt to detect whether we identify by project_id or name
            self.client = lcs.index  # module namespace; we will instantiate per index
        except Exception as exc:
            raise RuntimeError(f"llama_cloud_services.index not available: {exc}")

    # --- Discovery ---
    def _resolve_cloud_identifiers(self, index: str) -> Dict[str, str]:
        """Return constructor kwargs for LlamaCloudIndex.
        Prioritizes explicit index IDs from env (e.g., STATE_BASE_ID / STATE_SUMMARY_ID),
        else uses the provided name.
        """
        name = (index or "").strip()
        lname = name.lower()
        # If suffix indicates summary, try SUMMARY_ID
        if lname.endswith("_summary"):
            base = lname[:-9]
            raw_key = f"{base.upper()}_SUMMARY_ID"
            san_key = raw_key.replace("-", "_")
            env_id = os.getenv(raw_key) or os.getenv(san_key)
            if env_id:
                return {"index_id": env_id}
        # Base env id
        raw_key = f"{lname.upper()}_BASE_ID"
        san_key = raw_key.replace("-", "_")
        env_id = os.getenv(raw_key) or os.getenv(san_key)
        if env_id:
            return {"index_id": env_id}
        # Fallback to name only
        return {"name": name}

    def _new_llama_index(self, ident: Dict[str, str]):
        """Construct LlamaCloudIndex with org/project/api if provided in env."""
        from llama_cloud_services.index import LlamaCloudIndex  # type: ignore

        ctor: Dict[str, str] = {}
        ctor.update(ident)
        org = os.getenv("LLAMA_CLOUD_ORGANIZATION_ID")
        if org:
            ctor["organization_id"] = org
        proj_name = os.getenv("LLAMA_CLOUD_PROJECT_NAME")
        if proj_name:
            ctor["project_name"] = proj_name
        api_key = os.getenv("LLAMA_CLOUD_API_KEY")
        if api_key:
            ctor["api_key"] = api_key
        return LlamaCloudIndex(**ctor)  # type: ignore[arg-type]

    def _iter_docstore_nodes_any(self, ds) -> Iterable[object]:
        """Yield nodes from a docstore across versions/backends without logging or assumptions."""
        try:
            get_all = getattr(ds, "get_all", None)
            if callable(get_all):
                data = get_all()
                if isinstance(data, dict):
                    for v in data.values():
                        if v is not None:
                            yield v
                    return
                elif isinstance(data, list):
                    for v in data:
                        if v is not None:
                            yield v
                    return
        except Exception:
            pass
        for attr in ("_data", "docs"):
            try:
                m = getattr(ds, attr, None)
                if isinstance(m, dict):
                    for v in m.values():
                        if v is not None:
                            yield v
                    return
            except Exception:
                continue
        try:
            # last resort: iterate keys if available
            keys = list(getattr(ds, "keys", lambda: [])())
            for k in keys:
                try:
                    v = ds.get(k)  # type: ignore[call-arg]
                    if v is not None:
                        yield v
                except Exception:
                    continue
        except Exception:
            pass
        return

    def list_documents(self, index: str) -> List[CloudDoc]:
        self._ensure_client()
        docs: List[CloudDoc] = []
        try:
            ident = self._resolve_cloud_identifiers(index)
            idx = self._new_llama_index(ident)
            # Attempt docstore discovery first (may be empty for managed indices)
            try:
                ds = getattr(idx, "docstore", None)
                if ds is not None:
                    found: Dict[str, CloudDoc] = {}
                    for node in self._iter_docstore_nodes_any(ds):
                        try:
                            md = getattr(node, "metadata", {}) or {}
                            did_val = md.get("ref_doc_id") or md.get("doc_id") or md.get("ref_doc") or md.get("document_id")
                            did = str(did_val) if did_val is not None else ""
                            if not did:
                                continue
                            if did not in found:
                                title = None
                                fname = md.get("file_name") or md.get("file_path") or md.get("source")
                                if isinstance(fname, str) and fname.strip():
                                    title = Path(str(fname)).name
                                # keep minimal meta (string-only)
                                meta: Dict[str, str] = {}
                                for k in ("file_name", "file_path", "source"):
                                    v = md.get(k)
                                    if isinstance(v, str):
                                        meta[k] = v
                                found[did] = CloudDoc(index=index, doc_id=did, title=title, meta=meta)
                        except Exception:
                            continue
                    docs = list(found.values())
            except Exception:
                docs = []

            # Fallback: use REST listing via internal client when docstore yields nothing
            if not docs:
                try:
                    client = getattr(idx, "_client", None)
                    pipeline = getattr(idx, "pipeline", None)
                    pipeline_id = getattr(pipeline, "id", None)
                    if client and pipeline_id:
                        skip = 0
                        limit = 100
                        found: Dict[str, CloudDoc] = {}
                        while True:
                            batch = client.pipelines.list_pipeline_documents(
                                pipeline_id=pipeline_id, skip=skip, limit=limit
                            )
                            if not batch:
                                break
                            for d in batch:
                                try:
                                    did = str(getattr(d, "id", None) or "")
                                    if not did or did in found:
                                        continue
                                    md = getattr(d, "metadata", {}) or {}
                                    title = None
                                    fname = md.get("file_name") or md.get("file_path") or md.get("source")
                                    if isinstance(fname, str) and fname.strip():
                                        title = Path(str(fname)).name
                                    meta: Dict[str, str] = {}
                                    for k in ("file_name", "file_path", "source"):
                                        v = md.get(k)
                                        if isinstance(v, str):
                                            meta[k] = v
                                    found[did] = CloudDoc(index=index, doc_id=did, title=title, meta=meta)
                                except Exception:
                                    continue
                            skip += limit
                        docs = list(found.values())
                except Exception:
                    docs = []
        except Exception as exc:
            logger.warning("Failed to list docs for index {}: {}", index, exc)
        return docs

    # --- Fetch ---
    def fetch_chunks(self, index: str, doc_id: str) -> List[Dict[str, str]]:
        """Return a list of {text, page, section, file_name} dicts."""
        self._ensure_client()
        chunks: List[Dict[str, str]] = []
        try:
            ident = self._resolve_cloud_identifiers(index)
            idx = self._new_llama_index(ident)
            # Try docstore-only iteration first
            try:
                ds = getattr(idx, "docstore", None)
                if ds is not None:
                    for n in self._iter_docstore_nodes_any(ds):
                        try:
                            md = getattr(n, "metadata", {}) or {}
                            md_doc = str(md.get("ref_doc_id") or md.get("doc_id") or md.get("ref_doc") or md.get("document_id") or "")
                            if md_doc != str(doc_id):
                                continue
                            text = None
                            gt = getattr(n, "get_text", None)
                            if callable(gt):
                                try:
                                    text = gt()
                                except Exception:
                                    text = None
                            if text is None:
                                text = getattr(n, "text", "") or ""
                            chunks.append({
                                "text": text,
                                "page": md.get("page_label") or md.get("page"),
                                "section": md.get("section") or md.get("header") or md.get("heading"),
                                "file_name": md.get("file_name") or md.get("file_path") or md.get("source") or f"{doc_id}.md",
                            })
                        except Exception:
                            continue
            except Exception:
                chunks = []

            # Fallback: REST get document content + page segmentation
            if not chunks:
                client = getattr(idx, "_client", None)
                pipeline = getattr(idx, "pipeline", None)
                pipeline_id = getattr(pipeline, "id", None)
                d = None
                if client and pipeline_id:
                    try:
                        d = client.pipelines.get_pipeline_document(
                            pipeline_id=pipeline_id, document_id=str(doc_id)
                        )
                    except Exception:
                        d = None
                if d is not None:
                    text_all = getattr(d, "text", None) or ""
                    md = getattr(d, "metadata", {}) or {}
                    file_hint = md.get("file_name") or md.get("file_path") or md.get("source") or f"{doc_id}.md"
                    positions = getattr(d, "page_positions", None)
                    if isinstance(positions, list) and positions:
                        # Ensure positions are sorted and unique within bounds
                        try:
                            L = len(text_all)
                        except Exception:
                            L = None
                        pos = [p for p in sorted(set(int(x) for x in positions if isinstance(x, (int, float)))) if p >= 0]
                        if L is not None:
                            pos = [p for p in pos if p < L]
                        # Add start and end sentinels
                        starts = [0] + pos
                        ends = pos + ([L] if L is not None else [None])
                        for i, (s, e) in enumerate(zip(starts, ends), start=1):
                            try:
                                segment = text_all[s:e] if (e is not None) else text_all[s:]
                            except Exception:
                                segment = text_all
                            chunks.append({
                                "text": segment or "",
                                "page": i,
                                "section": None,
                                "file_name": file_hint,
                            })
                    else:
                        chunks.append({
                            "text": text_all or "",
                            "page": None,
                            "section": None,
                            "file_name": file_hint,
                        })
        except Exception as exc:
            logger.warning("Failed to fetch chunks for {}/{}: {}", index, doc_id, exc)
        return chunks

    # --- Render ---
    def _render_markdown(self, doc: CloudDoc, chunks: List[Dict[str, str]]) -> str:
        lines: List[str] = []
        title = doc.title or doc.doc_id
        lines.append(f"# {title}")
        lines.append("")
        cur_section = None
        for c in chunks:
            sec = c.get("section")
            if sec and sec != cur_section:
                lines.append(f"## {sec}")
                cur_section = sec
            text = (c.get("text") or "").strip()
            if text:
                lines.append(text)
                lines.append("")
        return "\n".join(lines)

    # --- Export orchestration ---
    def export(self) -> Dict[str, any]:
        exported = 0
        errors = 0
        self._ensure_client()
        for idx in self.indexes:
            out_idx = self.out / idx
            out_idx.mkdir(parents=True, exist_ok=True)
            docs = self.list_documents(idx)
            if self.max_docs:
                docs = docs[: self.max_docs]
            for d in docs:
                try:
                    # resumable
                    if self.resume and idx in self._state and d.doc_id in self._state[idx]:
                        continue
                    chunks = self.fetch_chunks(idx, d.doc_id)
                    md = self._render_markdown(d, chunks)
                    # write
                    fname = out_idx / f"{d.doc_id}.md"
                    fname.write_text(md, encoding="utf-8")
                    # update state with content hash
                    content_hash = hashlib.sha256(md.encode("utf-8")).hexdigest()
                    self._state.setdefault(idx, {})[d.doc_id] = content_hash
                    self.cache.write_text(json.dumps(self._state, indent=2), encoding="utf-8")
                    exported += 1
                    time.sleep(self.sleep_s)
                except Exception as exc:
                    logger.warning("Export failed for {}/{}: {}", idx, d.doc_id, exc)
                    errors += 1
        # manifest
        man = {"indexes": self.indexes, "layer": self.layer, "exported": exported, "errors": errors}
        self.manifest.write_text(json.dumps(man, indent=2), encoding="utf-8")
        return man
