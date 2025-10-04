"""Graph builder for constructing knowledge graphs from documents.

Handles entity detection, relation extraction, and graph persistence using
LlamaIndex's KnowledgeGraphIndex and storage context.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from collections import defaultdict
import hashlib
import os

from loguru import logger

try:
    from llama_index.core import Document, StorageContext, load_index_from_storage
    from llama_index.core.indices import KnowledgeGraphIndex
    from llama_index.core.graph_stores import SimpleGraphStore
    from llama_index.core.schema import NodeWithScore, TextNode
except ImportError as e:
    logger.error(f"LlamaIndex not properly installed: {e}")
    raise

from .schema import (
    EntityNode, SectionNode, GraphEdge, EntityMention, GraphMetadata,
    RelationType, ExtractorType
)


class GraphBuilder:
    """Builds and manages knowledge graphs from document corpus.

    Also supports CSV/XLSX ingestion by converting a preview to Markdown and attaching
    column/unit metadata to aid retrieval and later numeric checks.

    New (resumable) builder capabilities:
    - Incremental, checkpointed graph construction with periodic persistence
    - Exponential backoff retries on transient LLM errors (e.g., 5xx)
    - Safe resume on re-run (skips already processed sections)
    """

    def __init__(
        self,
        corpus_dir: str = "knowledge_base",
        out_dir: str = "data_v2/graph",
        relation_mode: str = "heuristic",
        llm_provider: str = "cohere",  # default provider
        min_entity_conf: float = 0.5,
        min_relation_conf: float = 0.6,
        k_hop: int = 2,
        max_llm_calls: int = 0,
        rebuild: bool = False,
        graph_backend: str = "memory",
        # Resumability and reliability controls
        resume: bool = True,
        persist_every: int = 25,
        retry_max: int = 4,
        retry_backoff_base_s: float = 2.0,
        # Tabular ingest controls
        as_table_markdown: bool = True,
        table_max_rows: int = 30,
        excel_all_sheets: bool = True,
        table_rows_strategy: str = "head",  # head|tail|head_tail|sample|all
    ):
        self.corpus_dir = Path(corpus_dir)
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)

        self.relation_mode = relation_mode
        self.llm_provider = llm_provider
        self.min_entity_conf = min_entity_conf
        self.min_relation_conf = min_relation_conf
        self.k_hop = k_hop
        self.max_llm_calls = max_llm_calls
        self.rebuild = rebuild
        self.graph_backend = graph_backend

        # Resumability
        self.resume = resume
        self.persist_every = max(1, int(persist_every))
        self.retry_max = max(0, int(retry_max))
        self.retry_backoff_base_s = max(0.1, float(retry_backoff_base_s))
        self.progress_path = self.out_dir / ".build_progress.json"
        self._progress: Dict[str, Any] = {"processed_sections": [], "errors": {}}
        if self.resume and self.progress_path.exists() and not self.rebuild:
            try:
                self._progress = json.loads(self.progress_path.read_text(encoding="utf-8"))
            except Exception:
                self._progress = {"processed_sections": [], "errors": {}}

        # Tabular ingest options
        self.as_table_markdown: bool = as_table_markdown
        self.table_max_rows: int = int(table_max_rows)
        self.excel_all_sheets: bool = bool(excel_all_sheets)
        self.table_rows_strategy: str = str(table_rows_strategy).lower().strip() or "head"

        # Storage paths
        self.graph_store_path = self.out_dir / "graph_store.json"
        self.metadata_path = self.out_dir / "manifest.json"
        self.hash_cache_path = self.out_dir / "file_hashes.json"

        # Graph components
        self.graph_store = None
        self.storage_context = None
        self.kg_index = None
        self.metadata = GraphMetadata(
            corpus_dir=str(corpus_dir),
            relation_mode=relation_mode,
            k_hop_depth=k_hop,
            min_entity_conf=min_entity_conf,
            min_relation_conf=min_relation_conf
        )

        # Entity and section tracking
        self.entities: Dict[str, EntityNode] = {}
        self.sections: Dict[str, SectionNode] = {}
        self.edges: List[GraphEdge] = []
        self.file_hashes: Dict[str, str] = {}

        # Load existing hashes if not rebuilding
        if not rebuild and self.hash_cache_path.exists():
            with open(self.hash_cache_path, 'r') as f:
                self.file_hashes = json.load(f)

    def build(self) -> Dict[str, Any]:
        """Build the knowledge graph from corpus documents."""
        logger.info(f"Building graph from {self.corpus_dir}")

        # Initialize / load graph store and index (for resume)
        self._initialize_graph_store()
        self._load_or_init_index()

        # Process documents
        documents = self._load_documents()
        sections = self._sectionize_documents(documents)

        # Entity detection
        self._detect_entities(sections)

        # Relation extraction
        if self.relation_mode == "heuristic":
            self._extract_heuristic_relations(sections)
        elif self.relation_mode == "llm":
            self._extract_llm_relations(sections)
        elif self.relation_mode == "hybrid":
            self._extract_heuristic_relations(sections)
            self._extract_llm_relations(sections, budget=self.max_llm_calls)

        # Incremental KG build with retries + checkpoints
        self._build_llamaindex_graph_incremental(sections)
        stats = self._persist_graph()

        return stats

    def _get_llm(self):
        """Helper to get the configured LLM."""
        if self.llm_provider == "cohere":
            from llama_index.llms.cohere import Cohere
            return Cohere(model="command-r-plus", api_key=os.environ.get("COHERE_API_KEY"))
        elif self.llm_provider == "openai":
            from llama_index.llms.openai import OpenAI
            # Use a widely available current model
            return OpenAI(model="gpt-4o", api_key=os.environ.get("OPENAI_API_KEY"))
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")


    def _load_tabular_as_markdown(self, file_path: Path, file_hash: str) -> Dict[str, Any]:
        """Load a CSV/XLSX into a Markdown preview and attach column/unit metadata.

        - CSV: single preview table
        - XLSX: when excel_all_sheets=True, concatenate previews for all sheets with headings
        """
        import pandas as pd  # type: ignore
        import re
        try:
            if file_path.suffix.lower() == ".csv":
                df = pd.read_csv(file_path)
                units_map: Dict[str, str] = {}
                clean_cols: List[str] = []
                for col in df.columns:
                    m = re.search(r"^\s*(.*?)\s*\(([^)]+)\)\s*$", str(col))
                    if m:
                        name, unit = m.group(1), m.group(2)
                        units_map[str(name)] = str(unit)
                        clean_cols.append(str(name))
                    else:
                        clean_cols.append(str(col))
                if clean_cols != list(df.columns):
                    df.columns = clean_cols
                # Select preview rows using strategy
                _df = df
                if self.table_rows_strategy == "all":
                    _df = df
                elif self.table_rows_strategy == "tail":
                    _df = df.tail(self.table_max_rows)
                elif self.table_rows_strategy == "head_tail":
                    h = max(1, int(self.table_max_rows // 2))
                    _df = pd.concat([df.head(h), df.tail(max(0, self.table_max_rows - h))])
                elif self.table_rows_strategy == "sample":
                    stride = max(1, int(len(df) / max(1, self.table_max_rows)))
                    _df = df.iloc[::stride].head(self.table_max_rows)
                else:
                    _df = df.head(self.table_max_rows)
                # Prefer markdown table, but gracefully fall back when 'tabulate' is missing
                try:
                    md_table = _df.to_markdown(index=False)
                except Exception:
                    md_table = _df.to_csv(index=False)
                text = f"# Table Preview: {file_path.name}\n\n" + md_table
                return {
                    'file_path': str(file_path),
                    'file_name': file_path.name,
                    'text': text,
                    'hash': file_hash,
                    'metadata': {
                        'columns': clean_cols,
                        'units': units_map,
                        'rows_previewed': min(len(df), self.table_max_rows),
                        'rows_total_est': int(len(df)),
                        'table_source': 'csv',
                    }
                }
            else:
                # Excel: possibly load all sheets
                text_parts: List[str] = [f"# Workbook: {file_path.name}"]
                sheets_meta: List[Dict[str, Any]] = []
                try:
                    if self.excel_all_sheets:
                        # Dict of sheet -> DataFrame
                        dfs = pd.read_excel(file_path, sheet_name=None)
                    else:
                        # Single default sheet
                        dfs = {"Sheet1": pd.read_excel(file_path)}
                except Exception:
                    if self.excel_all_sheets:
                        dfs = pd.read_excel(file_path, sheet_name=None, engine="openpyxl")
                    else:
                        dfs = {"Sheet1": pd.read_excel(file_path, engine="openpyxl")}

                for sheet_name, df in dfs.items():
                    # Normalize columns and extract units
                    units_map: Dict[str, str] = {}
                    clean_cols: List[str] = []
                    for col in df.columns:
                        m = re.search(r"^\s*(.*?)\s*\(([^)]+)\)\s*$", str(col))
                        if m:
                            name, unit = m.group(1), m.group(2)
                            units_map[str(name)] = str(unit)
                            clean_cols.append(str(name))
                        else:
                            clean_cols.append(str(col))
                    if clean_cols != list(df.columns):
                        df.columns = clean_cols
                    # Build markdown for this sheet (markdown if available, else CSV)
                    text_parts.append(f"\n## Sheet: {sheet_name}\n")
                    # Select preview rows using strategy
                    _df = df
                    if self.table_rows_strategy == "all":
                        _df = df
                    elif self.table_rows_strategy == "tail":
                        _df = df.tail(self.table_max_rows)
                    elif self.table_rows_strategy == "head_tail":
                        h = max(1, int(self.table_max_rows // 2))
                        _df = pd.concat([df.head(h), df.tail(max(0, self.table_max_rows - h))])
                    elif self.table_rows_strategy == "sample":
                        stride = max(1, int(len(df) / max(1, self.table_max_rows)))
                        _df = df.iloc[::stride].head(self.table_max_rows)
                    else:
                        _df = df.head(self.table_max_rows)
                    try:
                        preview_table = _df.to_markdown(index=False)
                    except Exception:
                        preview_table = _df.to_csv(index=False)
                    text_parts.append(preview_table)
                    # Collect meta for this sheet
                    sheets_meta.append({
                        'name': str(sheet_name),
                        'columns': clean_cols,
                        'rows_previewed': min(len(df), self.table_max_rows),
                        'rows_total_est': int(len(df)),
                        'units': units_map,
                    })

                text = "\n\n".join(text_parts)
                return {
                    'file_path': str(file_path),
                    'file_name': file_path.name,
                    'text': text,
                    'hash': file_hash,
                    'metadata': {
                        'workbook': file_path.name,
                        'sheets': sheets_meta,
                        'table_source': 'xlsx',
                    }
                }
        except Exception as exc:
            logger.warning(f"Failed to parse table {file_path}: {exc}")
            return {
                'file_path': str(file_path),
                'file_name': file_path.name,
                'text': f"[Failed to parse table: {exc}]",
                'hash': file_hash,
            }

    def _initialize_graph_store(self):
        """Initialize the graph store and storage context."""
        if self.graph_backend == "memory":
            self.graph_store = SimpleGraphStore()
        else:
            raise NotImplementedError(f"Graph backend {self.graph_backend} not implemented")

        # If resuming from a previous run, we'll overwrite this with a loaded storage
        self.storage_context = StorageContext.from_defaults(
            graph_store=self.graph_store
        )

    def _load_or_init_index(self) -> None:
        """Load an existing KG index from out_dir if present (and not rebuilding),
        else initialize a fresh empty KG index bound to the current storage_context.
        """
        from llama_index.core.data_structs.data_structs import KG as _KG  # type: ignore
        try:
            # Attempt to load when resuming and persisted artifacts exist
            if self.resume and not self.rebuild and self.out_dir.exists() and any(self.out_dir.iterdir()):
                try:
                    storage = StorageContext.from_defaults(persist_dir=str(self.out_dir))
                    from llama_index.core import load_index_from_storage as _load  # type: ignore
                    self.kg_index = _load(storage)
                    self.storage_context = storage
                    logger.info("Loaded existing KG index from {}", self.out_dir)
                    return
                except Exception as exc:
                    logger.warning("Failed to load existing index (will initialize new): {}", exc)
            # Fresh index with empty KG structure
            from llama_index.core.indices import KnowledgeGraphIndex as _KGIndex  # type: ignore
            self.kg_index = _KGIndex(
                index_struct=_KG(),
                storage_context=self.storage_context,
                llm=self._get_llm(),
                include_embeddings=True,
                show_progress=True,
            )
            logger.info("Initialized new KG index")
        except Exception as exc:
            logger.exception("KG index init failed: {}", exc)
            raise

    def _load_documents(self) -> List[Dict[str, Any]]:
        """Load documents from corpus directory, including .md and tabular files."""
        documents: List[Dict[str, Any]] = []

        paths: List[Path] = []
        for pattern in ("*.md", "*.csv", "*.xlsx"):
            paths.extend(list(self.corpus_dir.rglob(pattern)))
        for file_path in sorted(set(paths)):
            # Check hash cache
            file_hash = self._compute_file_hash(file_path)
            if not self.rebuild and str(file_path) in self.file_hashes:
                if self.file_hashes[str(file_path)] == file_hash:
                    logger.debug(f"Skipping unchanged file: {file_path}")
                    continue

            # Load document
            try:
                if file_path.suffix.lower() == ".md":
                    text = file_path.read_text(encoding='utf-8', errors='ignore')
                    doc = {
                        'file_path': str(file_path),
                        'file_name': file_path.name,
                        'text': text,
                        'hash': file_hash
                    }
                else:
                    doc = self._load_tabular_as_markdown(file_path, file_hash)
                documents.append(doc)
                self.file_hashes[str(file_path)] = file_hash
            except Exception as e:
                logger.error(f"Failed to load {file_path}: {e}")

        logger.info(f"Loaded {len(documents)} documents (md/csv/xlsx)")
        return documents

    def _compute_file_hash(self, file_path: Path) -> str:
        """Compute SHA256 hash of file content."""
        return hashlib.sha256(file_path.read_bytes()).hexdigest()

    def _sectionize_documents(self, documents: List[Dict]) -> List[SectionNode]:
        """Split documents into sections based on headings."""
        sections = []

        for doc in documents:
            # Split by markdown headings
            heading_pattern = r'^(#{1,6})\s+(.+)$'
            lines = doc['text'].split('\n')

            current_section = []
            current_heading = None
            section_index = 0

            for line in lines:
                heading_match = re.match(heading_pattern, line, re.MULTILINE)

                if heading_match:
                    # Save previous section if exists
                    if current_section:
                        section_text = '\n'.join(current_section).strip()
                        if section_text:
                            section = SectionNode(
                                file_path=doc['file_path'],
                                file_name=doc['file_name'],
                                document_title=doc['file_name'].replace('.md', ''),
                                section_index=section_index,
                                heading=current_heading,
                                text=section_text
                            )
                            sections.append(section)
                            self.sections[section.node_id] = section
                            section_index += 1

                    # Start new section
                    current_heading = heading_match.group(2)
                    current_section = []
                else:
                    current_section.append(line)

            # Save final section
            if current_section:
                section_text = '\n'.join(current_section).strip()
                if section_text:
                    section = SectionNode(
                        file_path=doc['file_path'],
                        file_name=doc['file_name'],
                        document_title=doc['file_name'].replace('.md', ''),
                        section_index=section_index,
                        heading=current_heading,
                        text=section_text
                    )
                    sections.append(section)
                    self.sections[section.node_id] = section

        logger.info(f"Created {len(sections)} sections from documents")
        return sections

    def _detect_entities(self, sections: List[SectionNode]):
        """Detect entities in document sections using heuristics."""
        entity_mentions = defaultdict(list)

        # Common stop words to filter out
        STOP_WORDS = {
            'the', 'this', 'that', 'these', 'those', 'and', 'but', 'for',
            'with', 'from', 'into', 'through', 'during', 'before', 'after',
            'above', 'below', 'between', 'under', 'section', 'page', 'figure',
            'table', 'chapter', 'appendix', 'data', 'system', 'process'
        }

        # Patterns for entity detection
        acronym_pattern = r'\b[A-Z]{2,}\b'
        title_case_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'

        logger.info(f"Detecting entities in {len(sections)} sections...")

        for section in sections:
            text = section.text

            # Find acronyms
            for match in re.finditer(acronym_pattern, text):
                entity_text = match.group()
                if len(entity_text) >= 2 and entity_text.lower() not in STOP_WORDS:  # Filter stop words   
                    mention = EntityMention(
                        surface_form=entity_text,
                        start_span=match.start(),
                        end_span=match.end(),
                        confidence=0.9
                    )
                    entity_mentions[entity_text.upper()].append((section.node_id, mention))

            # Find title-case phrases
            for match in re.finditer(title_case_pattern, text):
                entity_text = match.group()
                # Filter: max 4 words, not a stop word
                if (len(entity_text.split()) <= 4 and
                    entity_text.lower() not in STOP_WORDS and
                    not all(w.lower() in STOP_WORDS for w in entity_text.split())):
                    mention = EntityMention(
                        surface_form=entity_text,
                        start_span=match.start(),
                        end_span=match.end(),
                        confidence=0.7
                    )
                    canonical = entity_text.lower().replace(' ', '_')
                    entity_mentions[canonical].append((section.node_id, mention))

        # Create entity nodes with better filtering
        MIN_FREQUENCY = 3  # Require at least 3 mentions (was 2)
        MAX_ENTITIES = 2000  # Cap total entities for performance
        MIN_ENTITY_LENGTH = 2  # Skip single-char entities

        # Filter and sort by frequency
        filtered_entities = {
            name: mentions for name, mentions in entity_mentions.items()
            if len(mentions) >= MIN_FREQUENCY and len(name) >= MIN_ENTITY_LENGTH
        }

        # Sort by frequency and take top entities
        sorted_entities = sorted(filtered_entities.items(), key=lambda x: len(x[1]), reverse=True)

        logger.info(f"Filtered from {len(entity_mentions)} to {len(filtered_entities)} entities (min freq={MIN_FREQUENCY})")
        for canonical_name, mentions in sorted_entities[:MAX_ENTITIES]:
            entity = EntityNode(
                canonical_name=canonical_name,
                frequency=len(mentions),
                confidence=max(m[1].confidence for m in mentions)
            )

            # Determine entity type
            if canonical_name.isupper():
                entity.entity_type = "ACRONYM"
            elif '_' in canonical_name:
                entity.entity_type = "PHRASE"

            self.entities[entity.node_id] = entity

            # Create mention edges
            for section_id, mention in mentions:
                edge = GraphEdge(
                    source_id=section_id,
                    target_id=entity.node_id,
                    relation_type=RelationType.MENTIONS,
                    confidence=mention.confidence,
                    extractor=ExtractorType.HEURISTIC,
                    provenance=[{
                        'section_id': section_id,
                        'surface': mention.surface_form,
                        'spans': [mention.start_span, mention.end_span]
                    }]
                )
                self.edges.append(edge)

        logger.info(f"Detected {len(self.entities)} entities with {len(self.edges)} mentions")

    def _extract_heuristic_relations(self, sections: List[SectionNode]):
        """Extract co-occurrence relations between entities."""
        logger.info("Extracting co-occurrence relations...")

        # Group entities by section
        section_entities = defaultdict(set)

        for edge in self.edges:
            if edge.relation_type == RelationType.MENTIONS:
                section_entities[edge.source_id].add(edge.target_id)

        # Create co-occurrence edges
        cooccurrence_count = 0
        total_sections = len(section_entities)

        for idx, (section_id, entity_ids) in enumerate(section_entities.items()):
            entity_list = list(entity_ids)

            # Log progress more frequently with INFO level so it shows
            if idx % 5 == 0 or idx == total_sections - 1:
                logger.info(f"Processing co-occurrences: section {idx+1}/{total_sections} ({len(entity_list)} entities in this section)")
            # Limit co-occurrences per section to avoid explosion
            MAX_COOCCURRENCES_PER_SECTION = 20  # Reduced from 50
            cooccurrences_in_section = 0

            # Skip sections with too many entities to avoid quadratic explosion
            if len(entity_list) > 100:
                logger.warning(f"Skipping section {section_id} with {len(entity_list)} entities (too many)")
                continue

            for i in range(len(entity_list)):
                if cooccurrences_in_section >= MAX_COOCCURRENCES_PER_SECTION:
                    break  # Break outer loop when limit reached

                for j in range(i + 1, len(entity_list)):
                    if cooccurrences_in_section >= MAX_COOCCURRENCES_PER_SECTION:
                        break

                    # Calculate co-occurrence confidence based on section length
                    section = self.sections.get(section_id)
                    if section:
                        # Simple confidence: inverse of text length (normalized)
                        confidence = min(1.0, 100.0 / len(section.text.split()))

                        edge = GraphEdge(
                            source_id=entity_list[i],
                            target_id=entity_list[j],
                            relation_type=RelationType.COOCCURS_IN,
                            confidence=confidence,
                            extractor=ExtractorType.HEURISTIC,
                            provenance=[{'section_id': section_id}]
                        )

                        if confidence >= self.min_relation_conf:
                            self.edges.append(edge)
                            cooccurrence_count += 1
                            cooccurrences_in_section += 1

        logger.info(f"Extracted {cooccurrence_count} co-occurrence relations")

    def _extract_llm_relations(self, sections: List[SectionNode], budget: Optional[int] = None):
        """Extract semantic relations using LLM (placeholder for now)."""
        # This would use KnowledgeGraphIndex's built-in triplet extraction
        # For MVP, we'll skip this and rely on heuristic relations
        logger.warning("LLM relation extraction not yet implemented")

    def _build_llamaindex_graph_incremental(self, sections: List[SectionNode]):
        """Build the KG fast without per-chunk LLM calls.

        Strategy:
        - Build LlamaIndex nodes from sections using from_documents with a no-op
          kg_triplet_extract_fn (so no LLM triplet extraction is invoked).
        - Upsert our heuristic edges (co-occurrence) into the KG graph store.
        - Persist periodically.
        """
        logger.info("Building LlamaIndex graph index (incremental mode)...")

        # Set up embedding model - prefer Cohere when key is present (for future vector ops)
        try:
            from llama_index.core import Settings
            import os as _os
            if _os.getenv("COHERE_API_KEY"):
                try:
                    from llama_index.embeddings.cohere import CohereEmbedding
                    raw_model = _os.getenv("COHERE_EMBED_MODEL", "embed-v4.0").strip()
                    m_lower = raw_model.lower()
                    alias_map = {"embed-english-v4.0": "embed-v4.0", "embed-english-v4": "embed-v4.0", "embed-v4": "embed-v4.0"}
                    model_norm = alias_map.get(m_lower, raw_model)
                    try:
                        Settings.embed_model = CohereEmbedding(model=model_norm, api_key=_os.getenv("COHERE_API_KEY"), input_type="search_document")
                    except TypeError:
                        Settings.embed_model = CohereEmbedding(model_name=model_norm, api_key=_os.getenv("COHERE_API_KEY"), input_type="search_document")
                    logger.info("Configured Cohere embeddings ({}).", model_norm)
                except Exception as _exc:
                    logger.warning("Cohere embeddings setup failed, continuing: {}", _exc)
        except Exception as e:
            logger.warning("Could not configure embeddings: {}", e)

        # 1) Create LlamaIndex Documents from the provided sections (no LLM extraction)
        from llama_index.core import Document  # type: ignore
        docs: List[Document] = []
        MAX_SECTION_LENGTH = 8000
        for sec in sections:
            text = sec.text[:MAX_SECTION_LENGTH]
            if len(sec.text) > MAX_SECTION_LENGTH:
                text += "... [truncated]"
            docs.append(
                Document(
                    text=text,
                    metadata={
                        "file_path": sec.file_path,
                        "file_name": sec.file_name,
                        "section_index": sec.section_index,
                        "heading": sec.heading or "",
                    },
                    id_=sec.node_id,
                )
            )
        logger.info("Prepared {} section-documents for indexing (no-op triplet extraction)", len(docs))

        # 2) Build KG index with no-op triplet extractor (avoids LLM calls)
        try:
            from llama_index.core.indices import KnowledgeGraphIndex as _KGIndex  # type: ignore
            self.kg_index = _KGIndex.from_documents(
                docs,
                storage_context=self.storage_context,
                llm=None,
                kg_triplet_extract_fn=lambda _text: [],
                include_embeddings=False,
                show_progress=True,
            )
            logger.info("Indexed {} documents without LLM triplet extraction", len(docs))
        except Exception as exc:
            logger.exception("Failed to build KG index from documents: {}", exc)
            raise

        # 3) Upsert heuristic edges into the KG (entity co-occurrences) and mention links to sections
        inserted = 0
        for e in self.edges:
            try:
                if e.relation_type == RelationType.COOCCURS_IN:
                    # entity <-> entity co-occurrence
                    src_ent = self.entities.get(e.source_id)
                    tgt_ent = self.entities.get(e.target_id)
                    if not src_ent or not tgt_ent:
                        continue
                    subj = src_ent.canonical_name  # graph uses canonical names for entity nodes
                    obj = tgt_ent.canonical_name
                    pred = e.relation_type.value
                    self.kg_index.upsert_triplet((subj, pred, obj), include_embeddings=False)
                    inserted += 1
                elif e.relation_type == RelationType.MENTIONS:
                    # section -> entity mention; also add reverse "defined_in" so we can traverse from entity to section
                    section_id = e.source_id  # already like "section:<path>:<idx>"
                    ent = self.entities.get(e.target_id)
                    if not ent:
                        continue
                    ent_name = ent.canonical_name
                    # forward mention (section -> entity)
                    self.kg_index.upsert_triplet((section_id, RelationType.MENTIONS.value, ent_name), include_embeddings=False)
                    # reverse link to let retrieval start from entity and reach sections
                    self.kg_index.upsert_triplet((ent_name, RelationType.DEFINED_IN.value, section_id), include_embeddings=False)
                    inserted += 2
                # else: ignore other edge types for now
                if inserted and inserted % 5000 == 0:
                    logger.info("Upserted {} heuristic edges into KG...", inserted)
            except Exception:
                # continue on any bad edge
                continue
        logger.info("Heuristic/mention edges upserted: {}", inserted)

        # 4) Persist once at the end (checkpoint)
        try:
            self._persist_checkpoint()
        except Exception as _exc:
            logger.warning("Final checkpoint persist failed: {}", _exc)

        logger.info("Incremental build complete (no-op LLM). Sections: {}", len(sections))

    def _persist_checkpoint(self) -> None:
        """Persist storage context + progress + file hash cache for idempotent resume."""
        # Persist LlamaIndex artifacts
        self.storage_context.persist(persist_dir=str(self.out_dir))
        # Write progress file
        try:
            self.progress_path.write_text(json.dumps(self._progress, indent=2), encoding="utf-8")
        except Exception:
            pass
        # Update file hash cache continuously
        try:
            with open(self.hash_cache_path, 'w') as f:
                json.dump(self.file_hashes, f, indent=2)
        except Exception:
            pass

    def _persist_graph(self) -> Dict[str, Any]:
        """Persist graph artifacts and return build stats."""
        logger.info("Persisting graph artifacts...")

        # Calculate stats
        stats = {
            'documents': len(set(s.file_path for s in self.sections.values())),
            'sections': len(self.sections),
            'entities': len(self.entities),
            'edges': len(self.edges),
            'edge_types': defaultdict(int)
        }

        for edge in self.edges:
            stats['edge_types'][edge.relation_type.value] += 1

        stats['edge_types'] = dict(stats['edge_types'])

        # Update metadata
        self.metadata.stats = stats

        # Save metadata
        with open(self.metadata_path, 'w') as f:
            json.dump(self.metadata.to_dict(), f, indent=2)

        # Save file hashes
        with open(self.hash_cache_path, 'w') as f:
            json.dump(self.file_hashes, f, indent=2)

        # Persist storage context
        self.storage_context.persist(persist_dir=str(self.out_dir))

        logger.info(f"Graph persisted to {self.out_dir}")
        logger.info(f"Stats: {json.dumps(stats, indent=2)}")

        return stats
