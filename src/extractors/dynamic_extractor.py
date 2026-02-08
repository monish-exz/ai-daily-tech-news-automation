"""
Dynamic HTML extractor implementation using Playwright.
Handles JavaScript-heavy sites and SPAs.
"""

from typing import List
from datetime import datetime
import trafilatura
import json
import logging

from src.extractors.base_extractor import BaseExtractor, ExtractionError
from src.models import ContentItem, SourceConfig, SourceType


class DynamicExtractor(BaseExtractor):
    """
    Extracts content from dynamic JavaScript-heavy pages.
    Uses Playwright to render the page before processing.
    """
    
    def can_handle(self, url: str) -> bool:
        # Targeted at known dynamic platforms
        platforms = ['reddit.com', 'stackoverflow.com', 'instagram.com', 'twitter.com', 'x.com']
        return any(p in url for p in platforms)
    
    def extract(self, source_config: SourceConfig) -> List[ContentItem]:
        self.logger.info(f"Extracting dynamic content from: {source_config.url}")
        
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            self.logger.error("Playwright not installed. Dynamic extraction unavailable.")
            raise ExtractionError("Playwright dependency missing.")
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                # Create context with a realistic user agent
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
                page = context.new_page()
                
                # Navigate and wait for network idle
                page.goto(source_config.url, wait_until="networkidle", timeout=30000)
                
                # Special handling for Reddit
                if "reddit.com" in source_config.url:
                    page.wait_for_timeout(3000) 
                    # If it's a reddit post, wait for the actual post content
                    try:
                        page.wait_for_selector('shreddit-post', timeout=5000)
                    except:
                        pass
                
                content_html = page.content()
                
                # Check if we got an empty page or bot detection page
                if "Checking if the site connection is secure" in content_html or "Verification" in content_html or "Access Denied" in content_html:
                    self.logger.error(f"[BOT_DETECTION] Cloudflare or similar protection triggered for {source_config.url}")
                    browser.close()
                    return []
                
                browser.close()
            
            if not content_html:
                self.logger.error(f"[EMPTY_PAGE] Playwright rendered an empty page for {source_config.url}")
                return []
            
            # Extract content from rendered HTML
            item_data = trafilatura.extract(content_html, output_format='json')
            
            if not item_data:
                self.logger.warning(f"[PARSING_FAILED] Trafilatura found no content in the rendered HTML from {source_config.url}")
                return []
            
            data = json.loads(item_data)
            
            published_at = None
            if data.get('date'):
                try:
                    published_at = datetime.fromisoformat(data['date'])
                except:
                    pass
            
            title = data.get('title', 'No Title')
            content = data.get('text', '')
            
            # If trafilatura fails to get meaningful content, try a basic selector fallback
            if (not content or len(content) < 50) and "reddit.com" in source_config.url:
                # We can't use BeautifulSoup on raw page.content() easily to find dynamic content
                # but trafilatura usually handles it. If it fails, maybe we just didn't wait enough.
                pass

            item = self._create_content_item(
                url=source_config.url,
                title=title,
                content=content,
                source_type=SourceType.DYNAMIC_HTML,
                published_at=published_at,
                author=data.get('author'),
                metadata={'source_name': source_config.name}
            )
            
            return [item]
            
        except Exception as e:
            error_msg = str(e)
            if "Timeout 30000ms exceeded" in error_msg:
                self.logger.error(f"[TIMEOUT] Page load timed out for {source_config.url}. The site might be too slow or blocking headless browsers.")
            else:
                self.logger.error(f"[DYNAMIC_ERROR] Failed for {source_config.url}: {error_msg}")
            raise ExtractionError(f"Failed to extract dynamic content: {error_msg}")
