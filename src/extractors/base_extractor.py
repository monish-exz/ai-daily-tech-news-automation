"""
Base extractor interface.
All extractors must implement this interface.
"""

from abc import ABC, abstractmethod
from typing import List
import logging

from src.models import ContentItem, SourceConfig


class BaseExtractor(ABC):
    """
    Abstract base class for all content extractors.
    Defines the contract that all extractors must follow.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def can_handle(self, url: str) -> bool:
        """
        Determine if this extractor can handle the given URL.
        
        Args:
            url: The URL to check
            
        Returns:
            True if this extractor can process the URL, False otherwise
        """
        pass
    
    @abstractmethod
    def extract(self, source_config: SourceConfig) -> List[ContentItem]:
        """
        Extract content from the source.
        
        Args:
            source_config: Configuration for the source to scrape
            
        Returns:
            List of ContentItem objects
            
        Raises:
            ExtractionError: If extraction fails
        """
        pass
    
    def extract_single(self, url: str, source_name: str = "") -> ContentItem:
        """
        Extract a single article/page.
        
        Args:
            url: URL to extract
            source_name: Optional name for the source
            
        Returns:
            Single ContentItem
            
        Raises:
            ExtractionError: If extraction fails
        """
        source_config = SourceConfig(
            url=url,
            name=source_name or self.__class__.__name__,
            max_items=1
        )
        results = self.extract(source_config)
        if results:
            return results[0]
        raise ExtractionError(f"Failed to extract content from {url}")
    
    def _create_content_item(
        self,
        url: str,
        title: str,
        content: str,
        source_type,
        **kwargs
    ) -> ContentItem:
        """
        Helper method to create a ContentItem with consistent formatting.
        
        Args:
            url: Source URL
            title: Content title
            content: Main content text
            source_type: SourceType enum value
            **kwargs: Additional fields (published_at, author, metadata)
            
        Returns:
            ContentItem instance
        """
        return ContentItem(
            source_url=url,
            source_type=source_type,
            title=title,
            content=content,
            published_at=kwargs.get('published_at'),
            author=kwargs.get('author'),
            metadata=kwargs.get('metadata', {})
        )


class ExtractionError(Exception):
    """Exception raised when extraction fails."""
    pass
