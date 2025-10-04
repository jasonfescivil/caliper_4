from __future__ import annotations

import hashlib
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional, Tuple

from loguru import logger

# Import settings from caliper_v2
try:
    from caliper_v2.core.config import settings  # type: ignore
except Exception as exc:  # pragma: no cover
    logger.warning("Failed to import caliper_v2.core.config.settings: {}", exc)
    settings = None  # type: ignore


@dataclass(frozen=True)
class IndexPaths:
    """
    Resolve index paths under settings.data_dir.

    Why:
      Single source of truth for where FAISS (and related) artifacts live for v2,
      keeping paths deterministic and container-friendly.
    """

    root: Path
    index_name: str

    @property
    def base(self) -> Path:
        return self.root / "indexes" / self.index_name

    @property
    def faiss_dir(self) -> Path:
        # Directory to store FAISS artifacts (file naming will be delegated to LlamaIndex adapter)
        return self.base / "faiss"

    @property
    def bm25_file(self) -> Path:
        # File to store BM25 index (pickle format)
        return self.base / "bm25_index.pkl"

    @property
    def meta_dir(self) -> Path:
        # Directory to store auxiliary metadata (if needed later)
        return self.base / "meta"


class IndexPathResolver:
    """
    Resolve index paths using project settings with safe fallbacks.
    """

    def __init__(self, data_root: Optional[Path] = None):
        # V2 MUST use its own data directory to avoid conflicts with v1
        default_root = Path("./data_v2").resolve()
        root = None
        try:
            root_val = getattr(settings, "data_dir", None)
            if root_val:
                # Convert to string first to handle any Path-like objects
                root_str = str(root_val)
                # Replace Docker paths with local equivalents
                if root_str.startswith("/app/"):
                    root_str = root_str.replace("/app/", "./")
                # Use the path as-is since we only have v2 now
                root = Path(root_str).resolve()
        except Exception as exc:  # pragma: no cover
            logger.debug("Could not read settings.data_dir: {}", exc)
        self._root = data_root or root or default_root
        # Ensure the directory exists
        self._root.mkdir(parents=True, exist_ok=True)
        logger.debug("IndexPathResolver using data root: {}", self._root)

    def resolve(self, index_name: str) -> IndexPaths:
        return IndexPaths(root=self._root, index_name=index_name)


class HashCache:
    """
    SQLite-backed file hash cache to enable idempotent ingest.

    Schema:
      table file_hashes(
        index_name TEXT NOT NULL,
        file_path  TEXT NOT NULL,
        sha256     TEXT NOT NULL,
        PRIMARY KEY(index_name, file_path)
      )
    """

    def __init__(self, db_path: Optional[Path] = None) -> None:
        # V2 MUST use its own database to avoid conflicts with v1
        default_db = Path("./data_v2/app_v2.db").resolve()
        dbp = None
        try:
            db_val = getattr(settings, "db_path", None)
            if db_val:
                # Convert to string first to handle any Path-like objects
                db_str = str(db_val)
                # Replace Docker paths with local equivalents
                if db_str.startswith("/app/"):
                    db_str = db_str.replace("/app/", "./")
                # CRITICAL: Use v2-specific database
                db_str = db_str.replace("app.db", "app_v2.db").replace("/data/", "/data_v2/")
                dbp = Path(db_str).resolve()
        except Exception as exc:  # pragma: no cover
            logger.debug("Could not read settings.db_path: {}", exc)
        self.db_path = db_path or dbp or default_db
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS file_hashes(
                  index_name TEXT NOT NULL,
                  file_path  TEXT NOT NULL,
                  sha256     TEXT NOT NULL,
                  PRIMARY KEY(index_name, file_path)
                )
                """
            )
            conn.commit()

    @staticmethod
    def sha256_of_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
        h = hashlib.sha256()
        with path.open("rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                h.update(chunk)
        return h.hexdigest()

    def upsert_hash(self, index_name: str, file_path: Path, sha256: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO file_hashes(index_name, file_path, sha256)
                VALUES (?, ?, ?)
                ON CONFLICT(index_name, file_path)
                DO UPDATE SET sha256=excluded.sha256
                """,
                (index_name, str(file_path), sha256),
            )
            conn.commit()

    def get_hash(self, index_name: str, file_path: Path) -> Optional[str]:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                "SELECT sha256 FROM file_hashes WHERE index_name=? AND file_path=?",
                (index_name, str(file_path)),
            )
            row = cur.fetchone()
            return row[0] if row else None

    def changed_files(
        self, index_name: str, files: Iterable[Path]
    ) -> Tuple[list[Path], list[Tuple[Path, str]]]:
        """
        Return (unchanged_files, changed_files_with_hash) given current cache state.
        changed_files_with_hash entries are (path, new_sha256).
        """
        unchanged: list[Path] = []
        changed: list[Tuple[Path, str]] = []
        for p in files:
            try:
                new_hash = self.sha256_of_file(p)
            except FileNotFoundError:
                # Treat missing files as changed to let caller decide how to handle
                logger.debug("File not found during hashing: {}", p)
                changed.append((p, ""))
                continue
            old_hash = self.get_hash(index_name, p)
            if old_hash == new_hash:
                unchanged.append(p)
            else:
                changed.append((p, new_hash))
        return unchanged, changed

    def commit_hashes(self, index_name: str, changed: Iterable[Tuple[Path, str]]) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.executemany(
                """
                INSERT INTO file_hashes(index_name, file_path, sha256)
                VALUES (?, ?, ?)
                ON CONFLICT(index_name, file_path)
                DO UPDATE SET sha256=excluded.sha256
                """,
                ((index_name, str(p), h) for p, h in changed if h),
            )
            conn.commit()
