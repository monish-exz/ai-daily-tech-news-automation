"""
Rate limiting system.
Prevents overwhelming target servers with too many requests.
"""

import time
import logging
from typing import Dict
from urllib.parse import urlparse
from threading import Lock


class RateLimiter:
    """
    Per-domain rate limiter using token bucket algorithm.
    """
    
    def __init__(self, requests_per_minute: int = 30, default_delay: float = 2.0):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_minute: Maximum requests per domain per minute
            default_delay: Default delay between requests in seconds
        """
        self.requests_per_minute = requests_per_minute
        self.default_delay = default_delay
        self.min_delay = 60.0 / requests_per_minute if requests_per_minute > 0 else default_delay
        
        # Track last request time per domain
        self.last_request: Dict[str, float] = {}
        self.lock = Lock()
        self.logger = logging.getLogger(__name__)
    
    def wait(self, url: str, custom_delay: float = None):
        """
        Wait if necessary before making a request.
        
        Args:
            url: URL being requested
            custom_delay: Custom delay override for this request
        """
        domain = self._extract_domain(url)
        delay = custom_delay or self.default_delay
        
        with self.lock:
            current_time = time.time()
            
            if domain in self.last_request:
                elapsed = current_time - self.last_request[domain]
                required_delay = max(self.min_delay, delay)
                
                if elapsed < required_delay:
                    sleep_time = required_delay - elapsed
                    self.logger.debug(f"Rate limiting {domain}: sleeping {sleep_time:.2f}s")
                    time.sleep(sleep_time)
                    current_time = time.time()
            
            self.last_request[domain] = current_time
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL for per-domain tracking."""
        try:
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return url
    
    def reset(self):
        """Reset all rate limiting state."""
        with self.lock:
            self.last_request.clear()
