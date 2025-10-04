"""
Master Ingestion Script for Caliper V2 on LlamaCloud

This script is responsible for:
1.  Reading local source documents.
2.  Loading and parsing rich metadata from CSV files.
3.  Processing documents using LlamaParse for structured text.
4.  Merging documents with their corresponding metadata.
5.  Defining and creating a LlamaCloud ingestion pipeline that uses Cohere's
    `embed-v4.0` model.
6.  Uploading the enriched documents to the pipeline for indexing.
"""
import os
import sys
from pathlib import Path

import pandas as pd
import typer
from dotenv import load_dotenv
from loguru import logger

# --- Constants ---
# Using Path from pathlib for OS-agnostic paths
# Assuming the script is run from the root of the project
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "knowledge_base"
METADATA_DIR = PROJECT_ROOT / "data_v2" / "metadata"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

app = typer.Typer(
    name="cloud_ingest",
    help="A CLI for ingesting documents and metadata into LlamaCloud with Cohere embeddings.",
    no_args_is_help=True,
)


def setup_logging():
    """Configure Loguru for rich logging."""
    logger.add(
        sys.stderr,
        format="{time} {level} {message}",
        level="INFO",
    )
    logger.info("Logging setup complete.")


def load_and_prepare_metadata(metadata_path: Path) -> pd.DataFrame:
    """
    Loads all CSV files from the metadata directory, concatenates them,
    and prepares a unified DataFrame.
    """
    logger.info(f"Reading metadata from: {metadata_path}")
    all_csvs = list(metadata_path.glob("*.csv"))
    if not all_csvs:
        logger.warning("No CSV files found in the metadata directory. Proceeding without metadata.")
        return pd.DataFrame()

    df_list = [pd.read_csv(f) for f in all_csvs]
    metadata_df = pd.concat(df_list, ignore_index=True)

    # TODO: Implement logic to create a clean, searchable key, e.g., from 'file_name'.
    # This will depend on the exact structure of the CSV files.
    # For now, we'll assume a 'file_name' column exists.
    if "file_name" not in metadata_df.columns:
        logger.error("A 'file_name' column is required in the metadata CSVs to map to documents.")
        raise typer.Exit(1)

    logger.success(f"Successfully loaded and merged {len(metadata_df)} metadata records from {len(all_csvs)} files.")
    return metadata_df


def configure_and_run_pipeline(pipeline_name: str, documents_with_metadata: list):
    """
    Configures and executes the LlamaCloud ingestion pipeline.
    """
    logger.info(f"Configuring LlamaCloud pipeline '{pipeline_name}'...")

    # Placeholder for LlamaCloud client initialization
    # from llama_cloud import LlamaCloud
    # client = LlamaCloud(api_key=os.getenv("LLAMA_CLOUD_API_KEY"))

    # --- Phase 1: Define the Pipeline ---
    # This is where we will specify the Cohere embedding model.
    # The exact API call will be based on the LlamaCloud documentation.
    pipeline_config = {
        "pipeline_name": pipeline_name,
        "embedding_config": {
            "type": "COHERE_EMBEDDING",
            "model": "embed-v4.0",
            # This component structure will need to be verified with the exact API spec.
            "component": {
                "api_key": os.getenv("COHERE_API_KEY"),
            },
        },
        # ... other pipeline settings like parsing, etc.
    }
    logger.info(f"Pipeline configured to use Cohere model: {pipeline_config['embedding_config']['model']}")

    # --- Phase 2: Upload enriched documents ---
    # This will involve iterating through `documents_with_metadata` and using
    # the LlamaCloud client's `upload` or `run_pipeline` method.
    logger.info(f"Uploading {len(documents_with_metadata)} documents to the pipeline...")
    # for doc in documents_with_metadata:
    #     client.upload(pipeline_name=pipeline_name, document=doc)

    logger.success("Placeholder for pipeline execution complete.")


@app.command()
def run(
    pipeline_name: str = typer.Option(
        "caliper-cohere-agentic-index",
        "--name",
        "-n",
        help="The name for the LlamaCloud pipeline and index.",
    ),
    force_reparse: bool = typer.Option(
        False, "--force-reparse", help="Force reparsing of documents even if cached."
    ),
):
    """
    Execute the full ingestion process: load metadata, parse documents,
    and run the LlamaCloud pipeline.
    """
    load_dotenv()
    if not os.getenv("LLAMA_CLOUD_API_KEY") or not os.getenv("COHERE_API_KEY"):
        logger.error("LLAMA_CLOUD_API_KEY and COHERE_API_KEY must be set in your .env file.")
        raise typer.Exit(1)
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional

# Robust .env loader (works without python-dotenv too)
try:
    from caliper_v2.core.env import load_env, require_env  # type: ignore
except Exception:
    # Fallback: naive loader if module import fails (shouldn't happen in normal runs)
    def load_env(*_args, **_kwargs) -> bool:
        return False

    def require_env(keys: Iterable[str]) -> None:
        missing = [k for k in keys if not os.getenv(k)]
        if missing:
            raise RuntimeError("Missing environment variables: " + ", ".join(missing))


# Logging
try:
    from loguru import logger
except Exception:
    class _StdLogger:
        def info(self, *args, **kwargs): print(*args)
        def warning(self, *args, **kwargs): print(*args)
        def error(self, *args, **kwargs): print(*args)
        def debug(self, *args, **kwargs): print(*args)
        def success(self, *args, **kwargs): print(*args)
    logger = _StdLogger()  # type: ignore


@dataclass
class IngestStats:
    discovered_files: int = 0
    parsed_files: int = 0
    uploaded_files: int = 0
    failures: int = 0
    index_id: Optional[str] = None
    notes: Optional[str] = None


def normalize_key(name: str) -> str:
    base = Path(name).name.strip().lower().replace(" ", "_")
    return base.rsplit(".", 1)[0]


def load_metadata(dir_path: Path) -> Dict[str, Dict]:
    rows: Dict[str, Dict] = {}
    if not dir_path.exists():
        return rows
    for csv_path in dir_path.glob("*.csv"):
        try:
            import pandas as pd  # heavy dep guarded
        except Exception as exc:
            logger.warning("pandas not available; skipping metadata load for {}", csv_path)
            continue
        try:
            df = pd.read_csv(csv_path)
        except Exception as exc:
            logger.warning("Failed reading {}: {}", csv_path, exc)
            continue
        if "file_name" not in df.columns:
            logger.warning("CSV {} missing required 'file_name' column; skipping", csv_path)
            continue
        df["doc_key"] = df["file_name"].map(normalize_key)
        for _, row in df.iterrows():
            key = str(row.get("doc_key") or "").strip()
            if not key:
                continue
            rows[key] = {k: (None if (pd.isna(v) if hasattr(pd, "isna") else v is None) else v) for k, v in row.items()}
    return rows


def parse_document(path: Path, cache_dir: Path) -> Optional[str]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    # Cache key by file name + mtime to avoid re-parsing unchanged docs
    cache_file = cache_dir / f"{path.name}.{path.stat().st_mtime_ns}.md"
    if cache_file.exists():
        try:
            return cache_file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            pass

    if path.suffix.lower() in {".md", ".txt"}:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
            cache_file.write_text(text, encoding="utf-8")
            return text
        except Exception as exc:
            logger.warning("Failed to read {}: {}", path, exc)
            return None

    try:
        from llama_parse import LlamaParse  # type: ignore
    except Exception as exc:
        logger.error("llama-parse not installed: {}. Install to enable PDF/DOCX parsing.", exc)
        return None

    # Try newer parameter names, fallback for older versions
    parser = None
    for kwargs in (
        dict(result_type="markdown", verbose=True, content_guideline_instruction="Preserve section headings and extract tables in Markdown."),
        dict(result_type="markdown", verbose=True, complemental_formatting_instruction="Preserve section headings and extract tables in Markdown."),
        dict(result_type="markdown", verbose=True, parsing_instruction="Preserve section headings and extract tables in Markdown."),
    ):
        try:
            parser = LlamaParse(**kwargs)
            break
        except TypeError:
            parser = None
    if parser is None:
        logger.error("Failed to initialize LlamaParse with known parameter sets.")
        return None

    # Basic retry with exponential backoff
    for attempt in range(3):
        try:
            docs = parser.load_data(str(path))
            text_parts: List[str] = []
            for d in docs:
                try:
                    t = getattr(d, "text", "")
                    if t:
                        text_parts.append(t)
                except Exception:
                    continue
            text = "\n\n".join(text_parts).strip()
            cache_file.write_text(text, encoding="utf-8")
            return text
        except Exception as exc:
            if attempt == 2:
                logger.error("Parse failed for {}: {}", path, exc)
                return None
            sleep_for = 2 ** attempt
            logger.warning("Parse attempt {} failed for {}; retrying in {}s ...", attempt + 1, path, sleep_for)
            time.sleep(sleep_for)
    return None


def build_enriched_docs(kb_dir: Path, meta: Dict[str, Dict], cache_dir: Path) -> List[Dict]:
    enriched: List[Dict] = []
    for p in kb_dir.rglob("*"):
        if p.is_dir():
            continue
        if p.suffix.lower() not in {".pdf", ".docx", ".md", ".txt"}:
            continue
        doc_key = normalize_key(p.name)
        text = parse_document(p, cache_dir=cache_dir)
        if not text:
            continue
        m = meta.get(doc_key, {}) if meta else {}
        metadata = {
            "file_name": p.name,
            "file_path": str(p),
            "doc_key": doc_key,
            "title": m.get("title") or m.get("document_title"),
            "authors": m.get("authors") or m.get("author"),
            "publisher": m.get("publisher") or m.get("agency") or m.get("organization"),
            "jurisdiction": m.get("jurisdiction"),
            "chapter": m.get("chapter"),
            "tags": m.get("tags"),
            "source": "knowledge_base",
        }
        enriched.append({"text": text, "metadata": metadata})
    return enriched


def write_jsonl(items: List[Dict], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for it in items:
            json.dump(it, f, ensure_ascii=False)
            f.write("\n")


def main() -> None:
    # Ensure .env is loaded; this will pick up C:\\repos\\caliper_3\\.env when present
    load_env()

    kb_dir = Path(os.getenv("CALIPER_KB_DIR", "knowledge_base")).resolve()
    meta_dir = Path(os.getenv("CALIPER_METADATA_DIR", "data_v2/metadata")).resolve()
    cache_dir = Path(os.getenv("CALIPER_PARSE_CACHE", "data_v2/ingest/cache")).resolve()
    out_dir = Path(os.getenv("CALIPER_INGEST_OUT", "data_v2/ingest")).resolve()
    jsonl_path = out_dir / "enriched_docs.jsonl"
    manifest_path = out_dir / "manifest.json"

    logger.info("Starting ingestion")
    logger.info("KB: {}", kb_dir)
    logger.info("Metadata: {}", meta_dir)
    logger.info("Cache: {}", cache_dir)
    logger.info("Output: {}", out_dir)

    stats = IngestStats()
    files = [p for p in kb_dir.rglob("*") if p.is_file() and p.suffix.lower() in {".pdf", ".docx", ".md", ".txt"}]
    stats.discovered_files = len(files)
    logger.info("Discovered {} candidate files", stats.discovered_files)

    metadata_map = load_metadata(meta_dir)
    enriched = build_enriched_docs(kb_dir, metadata_map, cache_dir)
    stats.parsed_files = len(enriched)
    logger.info("Parsed {} files", stats.parsed_files)

    # Write artifacts for inspection and potential upload step
    write_jsonl(enriched, jsonl_path)

    # Optional: attempt upload if an index ID and API key are present and client is available
    index_id = os.getenv("LLAMA_CLOUD_INDEX_ID")
    api_key = os.getenv("LLAMA_CLOUD_API_KEY")
    uploaded = 0
    if api_key and index_id:
        try:
            # Attempt a best-effort upload using llama_cloud_services if it exposes a client
            # This path is intentionally conservative to avoid hard failures across versions.
            import llama_cloud_services  # type: ignore

            client = getattr(llama_cloud_services, "Client", None) or getattr(llama_cloud_services, "client", None)
            if callable(client):
                cli = client(api_key=api_key)  # type: ignore
                # Try common method names
                bulk_up = getattr(cli, "upload_documents", None) or getattr(cli, "bulk_upload", None)
                if callable(bulk_up):
                    bulk_up(index_id=index_id, documents=enriched)  # type: ignore
                    uploaded = len(enriched)
                    stats.index_id = index_id
                    logger.success("Uploaded {} documents to index {}", uploaded, index_id)
                else:
                    logger.warning("llama_cloud_services client does not expose an upload method; skipping upload.")
            else:
                logger.warning("llama_cloud_services client not found; skipping upload.")
        except Exception as exc:
            logger.warning("Upload step failed (non-fatal): {}", exc)
    else:
        logger.info("Upload skipped (set LLAMA_CLOUD_API_KEY and LLAMA_CLOUD_INDEX_ID to enable)")

    stats.uploaded_files = uploaded
    stats.notes = "Artifacts written; connect upload step as needed."

    manifest = {
        "stats": asdict(stats),
        "paths": {
            "jsonl": str(jsonl_path),
            "cache_dir": str(cache_dir),
        },
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    logger.success("Ingestion complete. Manifest: {}", manifest_path)


if __name__ == "__main__":
    main()
    # 1. Load Metadata
    metadata_df = load_and_prepare_metadata(METADATA_DIR)

    # 2. Process Documents and Merge Metadata
    # Placeholder for document processing logic
    logger.info("Starting document processing and metadata merging...")
    # This will involve:
    # - Walking through KNOWLEDGE_BASE_DIR
    # - For each file, running LlamaParse
    # - Looking up the parsed document's metadata in `metadata_df`
    # - Creating a list of "enriched" document objects
    documents_with_metadata = [] # This list will hold the final objects for upload.
    logger.success("Placeholder for document processing complete.")


    # 3. Configure and Run LlamaCloud Pipeline
    configure_and_run_pipeline(pipeline_name, documents_with_metadata)

    logger.info("Ingestion process finished.")


if __name__ == "__main__":
    app()
