"""
Standard HTML extractor implementation using trafilatura.
Provides boilerplate-free extraction.
"""

from typing import List
import trafilatura
from datetime import datetime
import json

from src.extractors.base_extractor import BaseExtractor, ExtractionError
from src.models import ContentItem, SourceConfig, SourceType


class HTMLExtractor(BaseExtractor):
    """
    Extracts content from standard HTML pages.
    Uses trafilatura for automatic boilerplate removal and content detection.
    """
    
    def can_handle(self, url: str) -> bool:
        # Default fallback for most web pages
        return url.startswith(('http://', 'https://'))
    
    def extract(self, source_config: SourceConfig) -> List[ContentItem]:
        self.logger.info(f"Extracting HTML from: {source_config.url}")
        
        try:
            # Download and extract content
            downloaded = trafilatura.fetch_url(source_config.url)
            
            if not downloaded:
                self.logger.warning(f"[DOWNLOAD_FAILED] Trafilatura failed to download content for {source_config.url}. The site might be blocking standard requests or is currently offline.")
                return []
            
            # Extract metadata and content to JSON for structured access
            result_json = trafilatura.extract(
                downloaded, 
                output_format='json',
                include_comments=False,
                include_tables=True,
                include_links=False
            )
            
            if not result_json:
                self.logger.warning(f"[EXTRACTION_FAILED] Trafilatura could not find meaningful text content on {source_config.url}. This usually happens on pages with very little text or complex non-standard layouts.")
                return []
            
            data = json.loads(result_json)
            
            # Handle potential multi-item lists if the tool supports it, 
            # but usually it's single article extraction.
            # For listing pages, trafilatura might just get the collective text.
            
            content = data.get('text', '')
            title = data.get('title', 'No Title')
            author = data.get('author', 'Unknown')
            date_str = data.get('date', None)
            
            published_at = None
            if date_str:
                try:
                    published_at = datetime.fromisoformat(date_str)
                except:
                    pass
            
            item = self._create_content_item(
                url=source_config.url,
                title=title,
                content=content,
                source_type=SourceType.STATIC_HTML,
                published_at=published_at,
                author=author,
                metadata={'source_name': source_config.name}
            )
            
            return [item]
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"[HTML_EXTRACTION_ERROR] Internal error while processing {source_config.url}: {error_msg}")
            raise ExtractionError(f"Failed to extract HTML: {error_msg}")
