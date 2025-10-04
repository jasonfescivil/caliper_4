from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import json
from loguru import logger

from llama_index.core import Settings, StorageContext, load_index_from_storage


class GraphRetriever:
    """Lightweight subgraph retriever over a persisted KnowledgeGraphIndex.

    - Loads the KG from data_v2/graph (persisted by GraphBuilder)
    - Performs simple entity matching on the query
    - Expands 1 hop via adjacency in the graph store
    - Returns a list of snippet dicts shaped like Caliper retrieval nodes
    """

    def __init__(self, persist_dir: str = "data_v2/graph", hops: int = 1, limit: int = 200):
        self.persist_dir = Path(persist_dir)
        self.hops = max(0, int(hops))
        self.limit = max(1, int(limit))
        self.storage: Optional[StorageContext] = None
        self.kg = None

    def _load(self) -> None:
        if self.storage is not None and self.kg is not None:
            return
        self.storage = StorageContext.from_defaults(persist_dir=str(self.persist_dir))
        # Prefer loading a single KnowledgeGraphIndex; handle multi-index stores gracefully
        try:
            self.kg = load_index_from_storage(self.storage)
            return
        except Exception as exc:
            # If multiple indices exist, select the KG one by inspecting index_store.json
            try:
                import json
                idx_path = self.persist_dir / "index_store.json"
                if idx_path.exists():
                    data = json.loads(idx_path.read_text(encoding="utf-8", errors="ignore"))
                    # Common shapes across versions
                    candidates = []
                    # v0.12.x style: {"index_store": {"index_id_to_struct": {id: {"type": "..."}}}}
                    try:
                        id_map = (data.get("index_store") or {}).get("index_id_to_struct") or {}
                        for k, v in (id_map.items() if isinstance(id_map, dict) else []):
                            t = str((v.get("type") or v.get("index_type") or "")).lower()
                            candidates.append((k, t))
                    except Exception:
                        pass
                    # fallback: try top-level mapping
                    if not candidates and isinstance(data, dict):
                        # Case A: direct children with type/index_type
                        for k, v in list(data.items()):
                            if isinstance(v, dict):
                                t = str((v.get("type") or v.get("index_type") or "")).lower()
                                if k and t:
                                    candidates.append((k, t))
                        # Case B: observed schema: key "index_store/data" maps to {index_id: {"__type__": "kg", ...}}
                        try:
                            nested = data.get("index_store/data")
                            if isinstance(nested, dict):
                                for k, v in nested.items():
                                    t = str((v.get("__type__") or "")).lower()
                                    if k and t:
                                        candidates.append((k, t))
                        except Exception:
                            pass
                    # Choose a candidate containing 'kg'/'graph' first; else last entry
                    selected_id = None
                    for k, t in candidates:
                        if any(s in t for s in ("kg", "graph", "knowledge")):
                            selected_id = k
                            break
                    if not selected_id and candidates:
                        selected_id = candidates[-1][0]
                    if selected_id:
                        self.kg = load_index_from_storage(self.storage, index_id=selected_id)
                        return
            except Exception:
                pass
            # Re-raise original error if no selection worked
            raise exc

    def _candidate_entities(self, query: str) -> List[str]:
        """Very simple entity detection: title-cased tokens and ALLCAPS tokens.

        Returns both graph node ids (canonical names used in graph store) and the
        'entity:<canonical>' form for potential future compatibility. The graph
        store built by GraphBuilder uses plain canonical names for entity nodes.
        """
        import re

        toks = set()
        for m in re.finditer(r"\b[A-Z]{2,}\b", query):
            toks.add(m.group(0))
        for m in re.finditer(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", query):
            toks.add(m.group(0))
        # canonicalize similar to builder
        ids = []
        for t in sorted(toks):
            # canonical entity name used in graph store triplets
            canonical = t if t.isupper() else t.lower().replace(" ", "_")
            # add plain canonical (graph store) and prefixed variant
            if canonical:
                ids.append(canonical)
                ids.append(f"entity:{canonical}")
        return ids[:30]

    def _neighbors(self, node_ids: List[str]) -> List[str]:
        # Access the internal graph store via docstore; fall back to naive scan when unavailable
        try:
            g = self.storage.graph_store  # type: ignore[attr-defined]
        except Exception:
            g = None
        seen = set(node_ids)
        frontier = list(node_ids)
        out: List[str] = []
        for _ in range(self.hops):
            nxt: List[str] = []
            for nid in frontier:
                try:
                    edges = g.get_out_edges(nid) if g else []  # type: ignore
                except Exception:
                    edges = []
                for e in edges:
                    tgt = getattr(e, "dest", None) or getattr(e, "to", None) or getattr(e, "dest_node_id", None)
                    if isinstance(tgt, str) and tgt not in seen:
                        seen.add(tgt)
                        nxt.append(tgt)
                        out.append(tgt)
                if len(out) >= self.limit:
                    return out
            frontier = nxt
            if not frontier:
                break
        return out

    def _hydrate_nodes(self, ids: List[str]) -> List[Dict[str, Any]]:
        ds = self.storage.docstore if self.storage else None
        results: List[Dict[str, Any]] = []
        # Load persisted docstore JSON to support hydration when ds.get(id) is unavailable
        import json, os
        docstore_path = os.path.join(str(self.persist_dir), 'docstore.json')
        persisted = None
        try:
            persisted = json.loads(open(docstore_path, 'r', encoding='utf-8', errors='ignore').read())
        except Exception:
            persisted = None
        for nid in ids:
            n = None
            # 1) Try normal in-memory docstore first
            if ds is not None:
                try:
                    n = ds.get(nid)
                except Exception:
                    n = None
            if n is not None:
                md = getattr(n, "metadata", {}) or {}
                text = None
                gt = getattr(n, "get_text", None)
                if callable(gt):
                    try:
                        text = gt()
                    except Exception:
                        text = None
                if text is None:
                    text = getattr(n, "text", "") or ""
                results.append({
                    "id": getattr(n, "node_id", None) or getattr(n, "id_", None) or nid,
                    "text": text,
                    "metadata": {
                        "file_name": md.get("file_name") or md.get("file_path"),
                        "file_path": md.get("file_path") or md.get("file_name"),
                        "section": md.get("heading") or md.get("section") or md.get("header"),
                    },
                    "score": None,
                })
            elif persisted is not None:
                # 2a) Hydrate by following ref_doc_info -> node_ids -> data when given a section id
                try:
                    ref = (persisted.get('docstore/ref_doc_info') or {}).get(nid)
                    node_ids = (ref or {}).get('node_ids') or []
                    for uuid in node_ids:
                        data_entry = (persisted.get('docstore/data') or {}).get(uuid) or {}
                        dd = data_entry.get('__data__') or data_entry or {}
                        text = dd.get('text') or ''
                        md = dd.get('metadata') or {}
                        results.append({
                            "id": uuid,
                            "text": text,
                            "metadata": {
                                "file_name": md.get("file_name") or md.get("file_path"),
                                "file_path": md.get("file_path") or md.get("file_name"),
                                "section": md.get("heading") or md.get("section") or md.get("header"),
                            },
                            "score": None,
                        })
                        if len(results) >= self.limit:
                            break
                except Exception:
                    # 2b) Or hydrate directly when nid is a node UUID present in data
                    try:
                        data_entry = (persisted.get('docstore/data') or {}).get(nid)
                        if data_entry:
                            dd = data_entry.get('__data__') or data_entry or {}
                            text = dd.get('text') or ''
                            md = dd.get('metadata') or {}
                            results.append({
                                "id": nid,
                                "text": text,
                                "metadata": {
                                    "file_name": md.get("file_name") or md.get("file_path"),
                                    "file_path": md.get("file_path") or md.get("file_name"),
                                    "section": md.get("heading") or md.get("section") or md.get("header"),
                                },
                                "score": None,
                            })
                    except Exception:
                        pass
            if len(results) >= self.limit:
                break
        return results

    def _keyword_fallback(self, question: str) -> List[Dict[str, Any]]:
        """Scan docstore for sections likely relevant to DMR/I&I style queries.
        This is a pragmatic fallback until we add proper semantic retrieval over the graph.
        """
        # Try via in-memory docstore first (may not expose docs attribute consistently across versions)
        ds = self.storage.docstore if self.storage else None
        prefer_files = [
            'dmr.xlsx', 'full_dmr_monthly_summaries.xlsx', 'main_dmr_grid_data_v2.csv'
        ]
        keywords = [
            'dmr', 'infiltration', 'inflow', 'i&i', 'rdi/i', 'aadf', 'mgd', 'peak', 'wet', 'baseflow',
            'permit', 'exceedance', 'daily', 'monthly', 'flow', 'influent'
        ]
        ids: List[str] = []
        # Path-based scan of persisted docstore for robustness
        try:
            import json, os, re
            p = os.path.join(str(self.persist_dir), 'docstore.json')
            data = json.loads(open(p, 'r', encoding='utf-8', errors='ignore').read())
            meta = data.get('docstore/metadata') or {}
            # First, prioritize our target files' sections
            for k in meta.keys():
                kl = str(k).lower()
                if not kl.startswith('section:'):
                    continue
                if any(f in kl for f in prefer_files):
                    ids.append(k)
            # If question mentions specific years, try to pull nodes whose text contains those years
            years = set(re.findall(r"\b(?:19|20)\d{2}\b", question))
            if years and len(ids) < self.limit:
                data_entries = data.get('docstore/data') or {}
                for uuid, entry in data_entries.items():
                    if len(ids) >= self.limit:
                        break
                    dd = (entry.get('__data__') or entry) or {}
                    md = dd.get('metadata') or {}
                    fn = str(md.get('file_name') or md.get('file_path') or '').lower()
                    if not any(f in fn for f in prefer_files):
                        continue
                    txt = (dd.get('text') or '').lower()
                    if any(y.lower() in txt for y in years):
                        ids.append(uuid)
            # If still room, do a coarse keyword pass by loading a few candidate nodes' text
            if len(ids) < self.limit and ds is not None:
                for k in list(meta.keys()):
                    if len(ids) >= self.limit:
                        break
                    kl = str(k).lower()
                    if not kl.startswith('section:'):
                        continue
                    try:
                        n = ds.get(k)
                        txt = (getattr(n, 'text', '') or '').lower()
                    except Exception:
                        txt = ''
                    if any(kw in txt for kw in keywords):
                        ids.append(k)
        except Exception:
            # As a last resort, try iterating whatever the docstore exposes
            try:
                items = list(getattr(ds, 'docs', {}).items()) if ds else []
                scored: List[tuple[int,str]] = []
                for nid, node in items:
                    try:
                        md = getattr(node, 'metadata', {}) or {}
                        fp = str(md.get('file_path') or md.get('file_name') or '').lower()
                        fn = str(md.get('file_name') or md.get('file_path') or '').lower()
                        text = (getattr(node, 'text', '') or '').lower()
                    except Exception:
                        continue
                    score = 0
                    if any(p in fp or p in fn for p in prefer_files):
                        score += 5
                    kw_matches = sum(1 for k in keywords if k in text)
                    score += min(kw_matches, 5)
                    if score > 0:
                        scored.append((score, nid))
                scored.sort(key=lambda x: x[0], reverse=True)
                ids = [nid for _s, nid in scored[: self.limit]]
            except Exception:
                ids = []
        # Dedup and hydrate
        seen = set()
        deduped = []
        for i in ids:
            if i not in seen:
                seen.add(i)
                deduped.append(i)
        return self._hydrate_nodes(deduped[: self.limit])

    def retrieve(self, question: str) -> Dict[str, Any]:
        self._load()
        seeds = self._candidate_entities(question)
        ids: List[str]
        if not seeds:
            ids = []
        else:
            ids = seeds + self._neighbors(seeds)
        hydrated = self._hydrate_nodes(ids)
        if not hydrated:
            hydrated = self._keyword_fallback(question)
        # If still empty, return a handful of arbitrary nodes to avoid empty context
        if not hydrated:
            try:
                ds = self.storage.docstore if self.storage else None
                ids = list(ds.docs.keys())[: self.limit] if ds else []  # type: ignore
                hydrated = self._hydrate_nodes(ids)
            except Exception:
                hydrated = []
        return {
            "type": "retrieval_session",
            "question": question,
            "retrieval": {"nodes": hydrated},
            "source": {"graph": str(self.persist_dir), "mixed": False},
        }
