"""
RSS and Atom feed extractor implementation.
"""

from typing import List
import feedparser
from datetime import datetime
import time

from src.extractors.base_extractor import BaseExtractor, ExtractionError
from src.models import ContentItem, SourceConfig, SourceType


class RSSExtractor(BaseExtractor):
    """
    Extracted content from RSS/Atom feeds.
    Uses feedparser for robust XML parsing.
    """
    
    def can_handle(self, url: str) -> bool:
        """RSS detector is handled by the SourceDetector, but we keep this for direct routing."""
        return url.endswith(('.xml', '.rss', '/feed', '/rss', '/atom'))
    
    def extract(self, source_config: SourceConfig) -> List[ContentItem]:
        self.logger.info(f"Extracting RSS/Atom from: {source_config.url}")
        
        try:
            # Parse the feed
            feed = feedparser.parse(source_config.url)
            
            if feed.bozo:
                reason = str(feed.bozo_exception)
                self.logger.warning(f"Feed parsing warning (bozo bit set) for {source_config.url}: {reason}")
                # We still try to proceed unless it's a critical error
            
            if not feed.entries:
                self.logger.warning(f"[EMPTY_FEED] No entries found in RSS feed: {source_config.url}. Check if the URL is a valid active feed.")
            
            items = []
            count = 0
            
            for entry in feed.entries:
                if count >= source_config.max_items:
                    break
                
                # Extract title
                title = entry.get('title', 'No Title')
                
                # Extract link and ensure it's absolute
                link = entry.get('link', source_config.url)
                if link and not link.startswith('http'):
                    from urllib.parse import urljoin
                    link = urljoin(source_config.url, link)
                
                # Extract date and standardize
                published_at = None
                date_struct = entry.get('published_parsed') or entry.get('updated_parsed')
                if date_struct:
                    # ISO local date
                    published_at = datetime.fromtimestamp(time.mktime(date_struct))
                
                # Extract content/summary
                # RSS feeds sometimes have 'summary', 'description', or 'content'
                summary = entry.get('summary', '') or entry.get('description', '')
                if not summary and 'content' in entry:
                    summary = entry.content[0].value
                
                # Clean HTML from summary if needed, but feedparser usually gives a decent preview
                # We can refine this later if needed
                
                items.append(self._create_content_item(
                    url=link,
                    title=title,
                    content=summary,
                    source_type=SourceType.RSS_FEED,
                    published_at=published_at,
                    author=entry.get('author'),
                    metadata={'source_name': source_config.name}
                ))
                
                count += 1
                
            return items
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"[RSS_EXTRACTION_FAILED] Could not extract from {source_config.url}. Reason: {error_msg}")
            raise ExtractionError(f"Failed to extract RSS: {error_msg}")
