from __future__ import annotations

import json
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from loguru import logger


@dataclass(frozen=True)
class KBPaths:
    db_path: Path


class LocalKnowledgeBase:
    """
    Minimal, local KB backed by SQLite with a simple ontology:
      - documents(id, path, title, hash)
      - sections(id, document_id, section_index, heading, text, start_offset, end_offset, page)
      - entities(id, canonical_name, aliases_json)
      - mentions(section_id, entity_id, start_offset, end_offset, surface, confidence)
    """

    def __init__(self, db_path: Optional[Path] = None) -> None:
        default_db = Path("data_v2/kb_v1.sqlite")
        self.paths = KBPaths(db_path=db_path or default_db)
        self.paths.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.paths.db_path)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def _ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS documents(
                  id INTEGER PRIMARY KEY,
                  path TEXT NOT NULL UNIQUE,
                  title TEXT,
                  hash TEXT
                );

                CREATE TABLE IF NOT EXISTS sections(
                  id INTEGER PRIMARY KEY,
                  document_id INTEGER NOT NULL,
                  section_index INTEGER NOT NULL,
                  heading TEXT,
                  text TEXT NOT NULL,
                  start_offset INTEGER,
                  end_offset INTEGER,
                  page INTEGER,
                  FOREIGN KEY(document_id) REFERENCES documents(id),
                  UNIQUE(document_id, section_index)
                );

                CREATE TABLE IF NOT EXISTS entities(
                  id INTEGER PRIMARY KEY,
                  canonical_name TEXT NOT NULL UNIQUE,
                  aliases_json TEXT
                );

                CREATE TABLE IF NOT EXISTS mentions(
                  section_id INTEGER NOT NULL,
                  entity_id INTEGER NOT NULL,
                  start_offset INTEGER,
                  end_offset INTEGER,
                  surface TEXT,
                  confidence REAL,
                  FOREIGN KEY(section_id) REFERENCES sections(id),
                  FOREIGN KEY(entity_id) REFERENCES entities(id),
                  UNIQUE(section_id, entity_id, start_offset, end_offset)
                );

                CREATE INDEX IF NOT EXISTS idx_sections_doc ON sections(document_id);
                CREATE INDEX IF NOT EXISTS idx_mentions_section ON mentions(section_id);
                CREATE INDEX IF NOT EXISTS idx_entities_name ON entities(canonical_name);
                """
            )
            conn.commit()

    # -------- Ingest --------
    def upsert_document(self, path: Path, title: Optional[str], sha256: Optional[str]) -> int:
        with self._connect() as conn:
            cur = conn.execute("SELECT id, hash FROM documents WHERE path=?", (str(path),))
            row = cur.fetchone()
            if row:
                doc_id, old_hash = row
                if sha256 and old_hash != sha256:
                    conn.execute(
                        "UPDATE documents SET hash=?, title=? WHERE id=?",
                        (sha256, title, doc_id),
                    )
                return int(doc_id)
            cur = conn.execute(
                "INSERT INTO documents(path, title, hash) VALUES(?,?,?)",
                (str(path), title, sha256),
            )
            return int(cur.lastrowid)

    def upsert_section(
        self,
        document_id: int,
        section_index: int,
        heading: Optional[str],
        text: str,
        start_offset: Optional[int],
        end_offset: Optional[int],
        page: Optional[int] = None,
    ) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                "SELECT id FROM sections WHERE document_id=? AND section_index=?",
                (document_id, section_index),
            )
            row = cur.fetchone()
            if row:
                section_id = int(row[0])
                conn.execute(
                    "UPDATE sections SET heading=?, text=?, start_offset=?, end_offset=?, page=? WHERE id=?",
                    (heading, text, start_offset, end_offset, page, section_id),
                )
                return section_id
            cur = conn.execute(
                """
                INSERT INTO sections(document_id, section_index, heading, text, start_offset, end_offset, page)
                VALUES(?,?,?,?,?,?,?)
                """,
                (document_id, section_index, heading, text, start_offset, end_offset, page),
            )
            return int(cur.lastrowid)

    def upsert_entity(self, canonical_name: str, aliases: Optional[List[str]] = None) -> int:
        name = canonical_name.strip()
        if not name:
            raise ValueError("Empty canonical_name")
        with self._connect() as conn:
            cur = conn.execute(
                "SELECT id, aliases_json FROM entities WHERE canonical_name=?",
                (name,),
            )
            row = cur.fetchone()
            if row:
                entity_id = int(row[0])
                old_aliases = json.loads(row[1] or "[]")
                merged = sorted(set(old_aliases) | set(aliases or []))
                conn.execute(
                    "UPDATE entities SET aliases_json=? WHERE id=?",
                    (json.dumps(merged), entity_id),
                )
                return entity_id
            cur = conn.execute(
                "INSERT INTO entities(canonical_name, aliases_json) VALUES(?,?)",
                (name, json.dumps(sorted(set(aliases or [])))),
            )
            return int(cur.lastrowid)

    def add_mention(
        self,
        section_id: int,
        entity_id: int,
        start_offset: Optional[int],
        end_offset: Optional[int],
        surface: Optional[str],
        confidence: float = 0.9,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO mentions(section_id, entity_id, start_offset, end_offset, surface, confidence)
                VALUES(?,?,?,?,?,?)
                """,
                (section_id, entity_id, start_offset, end_offset, surface, confidence),
            )
            conn.commit()

    # -------- Simple extraction --------
    _ACRONYM = re.compile(r"\b[A-Z][A-Z0-9]{1,}\b")
    _TITLE_WORD = re.compile(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})\b")

    def _extract_entities(self, text: str) -> List[Tuple[str, Tuple[int, int]]]:
        hits: List[Tuple[str, Tuple[int, int]]] = []
        for m in self._ACRONYM.finditer(text):
            hits.append((m.group(0), m.span()))
        for m in self._TITLE_WORD.finditer(text):
            span_text = m.group(1)
            if len(span_text.split()) == 1 and span_text.lower() in {"the", "section"}:
                continue
            hits.append((span_text, m.span(1)))
        return hits

    def _split_sections(self, text: str) -> List[Tuple[Optional[str], str, Tuple[int, int]]]:
        # Split on markdown headings; fallback to paragraph splits
        sections: List[Tuple[Optional[str], str, Tuple[int, int]]] = []
        lines = text.splitlines()
        buf: List[str] = []
        heading: Optional[str] = None
        start = 0
        cursor = 0
        for line in lines:
            if line.strip().startswith("#"):
                if buf:
                    body = "\n".join(buf).strip()
                    end = cursor
                    if body:
                        sections.append((heading, body, (start, end)))
                heading = line.strip("# ").strip() or None
                buf = []
                start = cursor + len(line) + 1
            else:
                buf.append(line)
            cursor += len(line) + 1
        if buf:
            body = "\n".join(buf).strip()
            end = cursor
            if body:
                sections.append((heading, body, (start, end)))
        if not sections and text.strip():
            sections = [(None, text.strip(), (0, len(text)))]
        return sections

    # -------- Corpus ingest --------
    def index_corpus(self, corpus_dir: Path, file_hashes: Optional[Dict[Path, str]] = None) -> Dict[str, int]:
        """
        Ingest .md/.txt files under corpus_dir into the KB.

        If file_hashes is provided, only files present in that dict are processed
        (unchanged files are skipped). When a file is processed with a hash, its
        prior sections/mentions are dropped to rebuild idempotently.
        """
        corpus_dir = corpus_dir.resolve()
        files_processed = 0
        sections_count = 0
        mentions = 0

        for path in sorted(list(corpus_dir.rglob("*"))):
            if not path.is_file():
                continue
            if path.suffix.lower() not in {".md", ".txt"}:
                continue
            # Skip unchanged files when hash cache provided
            if file_hashes is not None and path not in file_hashes:
                continue

            sha = (file_hashes or {}).get(path)
            title = path.stem.replace("_", " ").title()
            doc_id = self.upsert_document(path, title, sha)

            if sha:
                # Rebuild sections/mentions for changed files
                with self._connect() as conn:
                    conn.execute(
                        "DELETE FROM mentions WHERE section_id IN (SELECT id FROM sections WHERE document_id=?)",
                        (doc_id,),
                    )
                    conn.execute("DELETE FROM sections WHERE document_id=?", (doc_id,))
                    conn.commit()

            text = path.read_text(encoding="utf-8", errors="ignore")
            for idx, (heading, body, (start, end)) in enumerate(self._split_sections(text)):
                sec_id = self.upsert_section(doc_id, idx, heading, body, start, end, page=None)
                sections_count += 1
                for surface, (s, e) in self._extract_entities(body):
                    canon = surface.strip()
                    if not canon:
                        continue
                    ent_id = self.upsert_entity(canon, aliases=[surface])
                    self.add_mention(sec_id, ent_id, s, e, surface, 0.9)
                    mentions += 1

            files_processed += 1

        return {"documents": files_processed, "sections": sections_count, "mentions": mentions}

    def ingest_ofm_spreadsheet(self, ofm_path: Path) -> Dict[str, int]:
        """
        Ingests a Washington OFM population spreadsheet.
        Assumes a format with columns like 'County', 'Year', 'Population'.
        Each row is ingested as a separate section in the KB.
        """
        try:
            import pandas as pd
        except ImportError:
            logger.error("pandas is not installed. Please install it with 'poetry install'")
            return {"documents": 0, "sections": 0, "mentions": 0}

        if not ofm_path.exists():
            logger.error(f"OFM spreadsheet not found at: {ofm_path}")
            return {"documents": 0, "sections": 0, "mentions": 0}

        # Treat the spreadsheet as a single document in the KB
        doc_id = self.upsert_document(
            ofm_path, title=f"OFM Population Data: {ofm_path.name}", sha256=None
        )

        try:
            df = pd.read_excel(ofm_path)
        except Exception as e:
            logger.error(f"Failed to read Excel file {ofm_path}: {e}")
            return {"documents": 1, "sections": 0, "mentions": 0}

        # Normalize column names for robustness
        df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

        county_col = next((c for c in df.columns if "county" in c), None)
        year_col = next((c for c in df.columns if "year" in c), None)
        pop_col = next((c for c in df.columns if "population" in c), None)

        if not all([county_col, year_col, pop_col]):
            logger.error(
                f"Could not find required columns (county, year, population) in {ofm_path}. "
                f"Available columns: {df.columns.tolist()}"
            )
            return {"documents": 1, "sections": 0, "mentions": 0}

        sections_added = 0
        for index, row in df.iterrows():
            try:
                county = row[county_col]
                year = row[year_col]
                population = row[pop_col]

                if pd.isna(county) or pd.isna(year) or pd.isna(population):
                    continue

                heading = f"Population for {county}, {year}"
                text = f"The projected population for {county} in {year} is {int(population)}."

                self.upsert_section(
                    document_id=doc_id,
                    section_index=index,
                    heading=heading,
                    text=text,
                    start_offset=None,
                    end_offset=None,
                    page=None,
                )
                sections_added += 1
            except (KeyError, ValueError, TypeError) as e:
                logger.warning(f"Skipping row {index} in {ofm_path} due to error: {e}")
                continue

        logger.info(f"Ingested {sections_added} population records from {ofm_path}")
        return {"documents": 1, "sections": sections_added, "mentions": 0}

    # -------- Retrieval --------
    def _question_terms(self, q: str) -> List[str]:
        return [t.lower() for t in re.findall(r"[A-Za-z0-9][A-Za-z0-9\-/]{2,}", q)]

    def _question_entities(self, q: str) -> List[str]:
        ents = set()
        for m in self._ACRONYM.finditer(q):
            ents.add(m.group(0))
        for m in self._TITLE_WORD.finditer(q):
            ents.add(m.group(1))
        return sorted(ents)

    def search(self, question: str, limit: int = 10) -> List[Dict]:
        terms = self._question_terms(question)
        q_ents = self._question_entities(question)
        term_like = "%" + "%".join(terms[:3]) + "%" if terms else "%"
        results: List[Tuple[float, Dict]] = []

        with self._connect() as conn:
            cur = conn.execute(
                """
                SELECT s.id, s.document_id, s.section_index, s.heading, s.text, d.path, d.title
                FROM sections s
                JOIN documents d ON d.id=s.document_id
                WHERE s.text LIKE ?
                LIMIT 200
                """,
                (term_like,),
            )
            rows = cur.fetchall()

        for (sid, _doc_id, sidx, heading, text, path, title) in rows:
            text_l = text.lower()
            score = 0.0
            for t in terms:
                if t in text_l:
                    score += 1.0
            ent_bonus = 0.0
            if q_ents:
                with self._connect() as conn:
                    q_marks = ",".join("?" * len(q_ents))
                    cur = conn.execute(
                        f"""
                        SELECT COUNT(*) FROM mentions m
                        JOIN entities e ON e.id=m.entity_id
                        WHERE m.section_id=? AND e.canonical_name IN ({q_marks})
                        """,
                        (sid, *q_ents),
                    )
                    cnt = int(cur.fetchone()[0] or 0)
                    ent_bonus = 0.5 * cnt

            score += ent_bonus
            if score <= 0:
                continue

            results.append(
                (
                    score,
                    {
                        "score": score,
                        "section_id": int(sid),
                        "metadata": {
                            "file_path": str(path),
                            "file_name": Path(path).name,
                            "document_title": title,
                            "section_index": int(sidx),
                            "heading": heading,
                        },
                        "text": text[:4000],
                    },
                )
            )

        results.sort(key=lambda x: x[0], reverse=True)
        return [r for _, r in results[: max(1, limit)]]

    # -------- Fusion --------
    @staticmethod
    def fuse(
        kb_hits: List[Dict],
        text_hits: List[Dict],
        kb_weight: float = 0.5,
        k: int = 60,
        limit: int = 20,
    ) -> List[Dict]:
        """
        Reciprocal Rank Fusion of KB hits and text hits, keyed by (file, section_index).
        """
        def key(h: Dict) -> Tuple[str, Optional[int]]:
            md = h.get("metadata", {}) or {}
            return (
                str(md.get("file_path") or md.get("source") or md.get("file_name") or ""),
                md.get("section_index"),
            )

        def rrf(rank: int, k: int = 60) -> float:
            return 1.0 / (k + rank)

        pool: Dict[Tuple[str, Optional[int]], Dict] = {}
        scores: Dict[Tuple[str, Optional[int]], float] = {}

        for i, h in enumerate(kb_hits, 1):
            kk = key(h)
            pool[kk] = h
            scores[kk] = scores.get(kk, 0.0) + kb_weight * rrf(i, k)

        for i, h in enumerate(text_hits, 1):
            kk = key(h)
            pool.setdefault(kk, h)
            scores[kk] = scores.get(kk, 0.0) + (1.0 - kb_weight) * rrf(i, k)

        ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
        out: List[Dict] = []
        for (kk, sc) in ranked[:limit]:
            h = dict(pool[kk])
            h["fused_score"] = sc
            out.append(h)
        return out
