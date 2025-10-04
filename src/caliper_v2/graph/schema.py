"""Graph schema definitions for Graph RAG.

Defines node and edge schemas for the knowledge graph:
- EntityNode: Represents entities with canonical names and aliases
- SectionNode: Represents document sections with full metadata
- GraphEdge: Represents relationships between nodes with provenance
- GraphMetadata: Stores graph version and build configuration
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from enum import Enum


class RelationType(Enum):
    """Types of relationships between entities."""
    COOCCURS_IN = "cooccurs_in"
    REFERS_TO = "refers_to"
    DEFINED_IN = "defined_in"
    GOVERNS = "governs"
    CITES = "cites"
    MENTIONS = "mentions"  # section->entity edge


class ExtractorType(Enum):
    """Source of relation extraction."""
    HEURISTIC = "heuristic"
    LLM = "llm"
    HYBRID = "hybrid"


@dataclass
class EntityNode:
    """Represents an entity in the knowledge graph."""
    canonical_name: str
    aliases: List[str] = field(default_factory=list)
    frequency: int = 0
    confidence: float = 1.0
    entity_type: Optional[str] = None  # e.g., "ACRONYM", "ORGANIZATION", "REGULATION"

    @property
    def node_id(self) -> str:
        """Unique identifier for the entity node."""
        return f"entity:{self.canonical_name.lower().replace(' ', '_')}"


@dataclass
class SectionNode:
    """Represents a document section in the knowledge graph."""
    file_path: str
    file_name: str
    document_title: str
    section_index: int
    heading: Optional[str] = None
    page: Optional[int] = None
    start_offset: int = 0
    end_offset: int = 0
    text: str = ""

    @property
    def node_id(self) -> str:
        """Unique identifier for the section node."""
        return f"section:{self.file_path}:{self.section_index}"


@dataclass
class EntityMention:
    """Represents a mention of an entity in a section."""
    surface_form: str
    start_span: int
    end_span: int
    confidence: float = 1.0


@dataclass
class GraphEdge:
    """Represents an edge in the knowledge graph."""
    source_id: str
    target_id: str
    relation_type: RelationType
    confidence: float = 1.0
    extractor: ExtractorType = ExtractorType.HEURISTIC
    provenance: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def edge_id(self) -> str:
        """Unique identifier for the edge."""
        return f"{self.source_id}->{self.relation_type.value}->{self.target_id}"


@dataclass
class GraphMetadata:
    """Metadata about the knowledge graph."""
    graph_version: str = "1.0.0"
    build_timestamp: datetime = field(default_factory=datetime.now)
    corpus_dir: str = "knowledge_base"
    relation_mode: str = "heuristic"
    k_hop_depth: int = 2
    min_entity_conf: float = 0.5
    min_relation_conf: float = 0.6
    predicate_weights: Dict[str, float] = field(default_factory=lambda: {
        "cooccurs_in": 0.4,
        "refers_to": 0.8,
        "defined_in": 0.9,
        "governs": 0.9,
        "cites": 0.7,
        "mentions": 0.6
    })
    stats: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary for JSON serialization."""
        return {
            "graph_version": self.graph_version,
            "build_timestamp": self.build_timestamp.isoformat(),
            "corpus_dir": self.corpus_dir,
            "relation_mode": self.relation_mode,
            "k_hop_depth": self.k_hop_depth,
            "min_entity_conf": self.min_entity_conf,
            "min_relation_conf": self.min_relation_conf,
            "predicate_weights": self.predicate_weights,
            "stats": self.stats
        }
