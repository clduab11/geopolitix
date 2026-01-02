"""
Data types for the Web Signals Feedforward Layer.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import enum


class ProviderType(enum.Enum):
    TAVILY = "tavily"
    FIRECRAWL = "firecrawl"
    JINA = "jina"
    UNKNOWN = "unknown"


@dataclass
class SearchHit:
    """Represents a single search result or discovered URL."""

    url: str
    title: Optional[str] = None
    snippet: Optional[str] = None
    score: float = 0.0
    published_date: Optional[str] = None
    provider: ProviderType = ProviderType.UNKNOWN
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Document:
    """Represents a processed document from a web source."""

    url: str
    content_markdown: str
    title: Optional[str] = None
    provider: ProviderType = ProviderType.UNKNOWN
    fetched_at: datetime = field(default_factory=datetime.utcnow)
    content_hash: str = ""
    chunk_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProviderTrace:
    """Trace information for a provider execution."""

    provider: str
    action: str  # search, crawl, extract
    status: str
    duration_ms: float
    items_count: int
    error: Optional[str] = None


@dataclass
class EvidencePack:
    """
    The final output package containing all gathered evidence, documents,
    embeddings, and metadata for a specific query/contract.
    """

    query: str
    run_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    search_hits: List[SearchHit] = field(default_factory=list)
    documents: List[Document] = field(default_factory=list)
    embeddings: List[Dict[str, Any]] = field(default_factory=list)
    doc_count: int = 0
    embedding_count: int = 0
    provider_traces: List[ProviderTrace] = field(default_factory=list)
    config_snapshot: Dict[str, Any] = field(default_factory=dict)
