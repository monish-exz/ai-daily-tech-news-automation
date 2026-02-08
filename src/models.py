"""
Data models for the universal web scraping system.
Defines unified data structures that all extractors must return.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List


class SourceType(Enum):
    """Enumeration of supported source types."""
    RSS_FEED = "rss_feed"
    ATOM_FEED = "atom_feed"
    STATIC_HTML = "static_html"
    DYNAMIC_HTML = "dynamic_html"
    REDDIT = "reddit"
    STACKOVERFLOW = "stackoverflow"
    GENERIC_FORUM = "generic_forum"
    UNSUPPORTED = "unsupported"
    UNKNOWN = "unknown"


@dataclass
class ContentItem:
    """
    Unified content item model.
    All extractors must return data in this format.
    """
    source_url: str
    source_type: SourceType
    title: str
    content: str
    published_at: Optional[datetime] = None
    author: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_excel_row(self) -> List[str]:
        """
        Convert to format compatible with existing Excel handler.
        Format: [Title, Date, Source, Link, Summary]
        """
        date_str = self.published_at.strftime("%Y-%m-%d") if self.published_at else datetime.now().strftime("%Y-%m-%d")
        source_name = self.metadata.get("source_name", self.source_type.value)
        
        return [
            self.title,
            date_str,
            source_name,
            self.source_url,
            self.content
        ]
    
    def to_sheets_row(self) -> List[str]:
        """
        Convert to format compatible with existing Google Sheets uploader.
        Same format as Excel for consistency.
        """
        return self.to_excel_row()


@dataclass
class SourceConfig:
    """Configuration for a content source."""
    url: str
    name: str
    source_type: Optional[SourceType] = None  # Auto-detect if None
    max_items: int = 10
    custom_headers: Optional[Dict[str, str]] = None
    enabled: bool = True
    use_dynamic_rendering: bool = False  # Force Playwright usage
    
    def __post_init__(self):
        """Validate configuration."""
        if not self.url or not self.url.startswith(("http://", "https://")):
            raise ValueError(f"Invalid URL: {self.url}")
        if self.max_items < 1:
            raise ValueError("max_items must be at least 1")


@dataclass
class ExtractionResult:
    """Result of an extraction operation."""
    source_config: SourceConfig
    items: List[ContentItem]
    success: bool
    error: Optional[str] = None
    extraction_time: float = 0.0
    items_extracted: int = 0
    
    def __post_init__(self):
        if self.items:
            self.items_extracted = len(self.items)
