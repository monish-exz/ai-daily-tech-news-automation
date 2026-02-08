"""
Universal Scraper Orchestrator.
Automatically detects source type and routes to the appropriate extractor.
"""

import logging
from typing import List, Dict, Any
from datetime import datetime
import validators

from src.models import ContentItem, SourceConfig, SourceType
from src.detection.source_detector import SourceDetector
from src.extractors.rss_extractor import RSSExtractor
from src.extractors.html_extractor import HTMLExtractor
from src.extractors.dynamic_extractor import DynamicExtractor
from src.utils.user_agent_manager import UserAgentManager
from src.utils.rate_limiter import RateLimiter
from src.utils.text_cleaner import get_domain_name


class UniversalScraper:
    """
    God-Mode Scraping Engine.
    Orchestrates the detection and extraction of any URL.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.detector = SourceDetector()
        self.ua_manager = UserAgentManager()
        self.rate_limiter = RateLimiter(requests_per_minute=20)
        
        # Register extractors
        self.extractors = {
            SourceType.RSS_FEED: RSSExtractor(),
            SourceType.ATOM_FEED: RSSExtractor(),
            SourceType.STATIC_HTML: HTMLExtractor(),
            SourceType.DYNAMIC_HTML: DynamicExtractor(),
            SourceType.REDDIT: DynamicExtractor(),
            SourceType.STACKOVERFLOW: DynamicExtractor(),
        }
        self.fallback_extractor = HTMLExtractor()

    def scrape_url(self, url: str, limit: int = 10, name: str = "") -> List[Dict[str, Any]]:
        """
        Scrape a single URL and return standardized results.
        
        Args:
            url: The URL to scrape
            limit: Max articles to fetch (if applicable)
            name: Human-readable name for the source
            
        Returns:
            List of standardized dictionaries
        """
        # Validate URL
        if not validators.url(url):
            self.logger.error(f"Invalid URL provided: {url}")
            return []

        # Special handling for Reddit: use RSS for subreddits/user feeds
        if "reddit.com/r/" in url or "reddit.com/user/" in url:
            if not url.endswith(".rss") and "/comments/" not in url:
                # Remove trailing slash if present and append .rss
                clean_url = url.strip().rstrip("/")
                rss_url = f"{clean_url}.rss"
                self.logger.info(f"Subreddit/User feed detected. Redirecting to RSS: {rss_url}")
                url = rss_url
                source_type = SourceType.RSS_FEED
            elif "/comments/" in url:
                source_type = SourceType.REDDIT
        # Special handling for StackOverflow: use RSS for questions
        elif "stackoverflow.com" in url:
            if "/questions" in url and not url.endswith(".rss"):
                # Redirect to stackoverflow feed
                # Note: Stackoverflow RSS is usually via /feeds/ or tag-based
                # For basic questions list: https://stackoverflow.com/feeds
                self.logger.info(f"StackOverflow detected. Redirecting to RSS feed for reliability.")
                url = "https://stackoverflow.com/feeds"
                source_type = SourceType.RSS_FEED
        else:
            # Detect source type normally
            source_type = self.detector.detect(url)
        
        self.logger.info(f"Routing {url} to {source_type.value} extractor")

        # Create config
        config = SourceConfig(url=url, name=name or url, max_items=limit, source_type=source_type)

        # Rate limit check
        self.rate_limiter.wait(url)

        try:
            # Route to extractor
            extractor = self.extractors.get(source_type, self.fallback_extractor)
            items = extractor.extract(config)
            
            # Convert to standardized schema: {"title": str, "link": str, "content": str, "date": str, "source": str}
            results = []
            for item in items:
                date_val = item.published_at if item.published_at else datetime.now()
                source_name = name or item.metadata.get("source_name")
                if not source_name or source_name == source_type.value:
                    source_name = get_domain_name(url)
                
                results.append({
                    "title": item.title,
                    "link": item.source_url,
                    "content": item.content,
                    "date": date_val.strftime("%Y-%m-%d"),
                    "source": source_name
                })
            
            return results

        except Exception as e:
            self.logger.error(f"Error scraping {url}: {str(e)}")
            return []

    def scrape_all(self, urls: List[str], limit: int = 8) -> List[Dict[str, Any]]:
        """Scrape multiple URLs."""
        all_results = []
        for url in urls:
            if url.strip():
                all_results.extend(self.scrape_url(url, limit))
        return all_results


def scrape_all_websites(urls: List[str] = None, limit: int = 8):
    """
    Backward compatible wrapper for the original system.
    If no URLs passed, it might be called by legacy code expecting a hardcoded list.
    """
    scraper = UniversalScraper()
    
    if urls is None:
        # Legacy hardcoded fallback for compatibility
        urls = [
            "https://techcrunch.com/tag/artificial-intelligence/feed/",
            "https://www.technologyreview.com/feed/",
            "https://analyticsindiamag.com/feed/"
        ]
        
    results_raw = scraper.scrape_all(urls, limit)
    
    # The existing system expects a list of lists: [title, today, source_name, link, summary]
    # We should return what the legacy system expects if it's being used by main.py
    # OR we refactor main.py to handle the new dict format.
    # The prompt asks to ensure existing excel_handler and google_sheets work seamlessly.
    
    # Compatibility mapping:
    # Existing handler expects: [title, date, source, link, summary]
    legacy_formatted = []
    for r in results_raw:
        legacy_formatted.append([
            r['title'],
            r['date'],
            r['source'],
            r['link'],
            r['content']
        ])
        
    return legacy_formatted
