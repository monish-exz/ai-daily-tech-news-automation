"""
Source type detection system.
Automatically determines the type of content source from a URL.
"""

import re
import logging
from typing import Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from src.models import SourceType


class SourceDetector:
    """
    Detects the type of content source from a URL.
    Uses multiple heuristics for accurate classification.
    """
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
        
        # Platform-specific URL patterns
        self.platform_patterns = {
            SourceType.REDDIT: [
                r'reddit\.com/r/\w+',
                r'reddit\.com/user/\w+',
            ],
            SourceType.STACKOVERFLOW: [
                r'stackoverflow\.com/questions',
                r'stackoverflow\.com/search',
                r'stackoverflow\.com/questions/tagged',
            ],
        }
        
        # RSS/Atom feed indicators in URL
        self.feed_patterns = [
            r'/feed/?$',
            r'/rss/?$',
            r'/atom/?$',
            r'\.xml$',
            r'\.rss$',
        ]
    
    def detect(self, url: str) -> SourceType:
        """
        Detect the source type of a URL.
        
        Strategy:
        1. Check URL patterns for known platforms
        2. Check URL for feed indicators
        3. Make HEAD request to check Content-Type
        4. Parse initial content if needed
        5. Default to STATIC_HTML
        
        Args:
            url: URL to analyze
            
        Returns:
            SourceType enum value
        """
        try:
            # Step 1: Platform-specific pattern matching
            platform_type = self._check_platform_patterns(url)
            if platform_type:
                self.logger.info(f"Detected {platform_type.value} via URL pattern: {url}")
                return platform_type
            
            # Step 2: Feed URL pattern matching
            if self._is_feed_url(url):
                self.logger.info(f"Detected feed via URL pattern: {url}")
                return SourceType.RSS_FEED
            
            # Step 3: HEAD request to check Content-Type
            content_type = self._get_content_type(url)
            if content_type:
                if any(feed_type in content_type for feed_type in ['xml', 'rss', 'atom']):
                    self.logger.info(f"Detected feed via Content-Type: {url}")
                    return SourceType.RSS_FEED
            
            # Step 4: Sample content and analyze
            source_type = self._analyze_content(url)
            if source_type:
                return source_type
            
            # Step 5: Default to static HTML
            self.logger.info(f"Defaulting to STATIC_HTML: {url}")
            return SourceType.STATIC_HTML
            
        except Exception as e:
            self.logger.warning(f"Detection error for {url}: {e}. Defaulting to STATIC_HTML")
            return SourceType.STATIC_HTML
    
    def _check_platform_patterns(self, url: str) -> Optional[SourceType]:
        """Check if URL matches known platform patterns."""
        for source_type, patterns in self.platform_patterns.items():
            for pattern in patterns:
                if re.search(pattern, url, re.IGNORECASE):
                    return source_type
        return None
    
    def _is_feed_url(self, url: str) -> bool:
        """Check if URL looks like an RSS/Atom feed."""
        for pattern in self.feed_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        return False
    
    def _get_content_type(self, url: str) -> Optional[str]:
        """
        Make a HEAD request to get Content-Type header.
        Returns None if request fails.
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.head(url, timeout=self.timeout, headers=headers, allow_redirects=True)
            return response.headers.get('Content-Type', '').lower()
        except Exception as e:
            self.logger.debug(f"HEAD request failed for {url}: {e}")
            return None
    
    def _analyze_content(self, url: str) -> Optional[SourceType]:
        """
        Fetch and analyze initial content to determine type.
        Looks for RSS/Atom indicators in the HTML/XML.
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, timeout=self.timeout, headers=headers)
            content = response.text[:5000]  # Only check first 5KB
            
            # Check for RSS/Atom feed markers
            if any(marker in content for marker in ['<rss', '<feed', 'xmlns:atom', 'xmlns="http://www.w3.org/2005/Atom']):
                return SourceType.RSS_FEED
            
            # Try parsing as XML
            try:
                soup = BeautifulSoup(content, 'xml')
                if soup.find('rss') or soup.find('feed'):
                    return SourceType.RSS_FEED
            except:
                pass
            
            # Check for indicators of dynamic content (React, Vue, Angular)
            if any(marker in content for marker in ['__NEXT_DATA__', 'vue-server-renderer', 'ng-version']):
                self.logger.info(f"Detected dynamic content in: {url}")
                return SourceType.DYNAMIC_HTML
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Content analysis failed for {url}: {e}")
            return None
    
    def is_supported(self, url: str) -> bool:
        """
        Check if the URL is supported for scraping.
        
        Args:
            url: URL to check
            
        Returns:
            True if supported, False otherwise
        """
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False
            return True
        except:
            return False
