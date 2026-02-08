"""
User-Agent rotation system.
Provides realistic browser user agents to avoid detection.
"""

import random
from typing import Optional


class UserAgentManager:
    """Manages user agent rotation for requests."""
    
    # Curated list of legitimate browser user agents
    USER_AGENTS = [
        # Chrome on Windows
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        
        # Chrome on macOS
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        
        # Firefox on Windows
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
        
        # Firefox on macOS
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
        
        # Safari on macOS
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        
        # Edge on Windows
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
    ]
    
    def __init__(self, custom_user_agent: Optional[str] = None):
        """
        Initialize user agent manager.
        
        Args:
            custom_user_agent: Custom user agent to always use (disables rotation)
        """
        self.custom_user_agent = custom_user_agent
    
    def get_user_agent(self) -> str:
        """
        Get a user agent string.
        
        Returns:
            User agent string (random from pool or custom)
        """
        if self.custom_user_agent:
            return self.custom_user_agent
        return random.choice(self.USER_AGENTS)
    
    def get_headers(self, additional_headers: Optional[dict] = None) -> dict:
        """
        Get complete request headers with user agent.
        
        Args:
            additional_headers: Additional headers to include
            
        Returns:
            Dictionary of headers
        """
        headers = {
            'User-Agent': self.get_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        if additional_headers:
            headers.update(additional_headers)
        
        return headers
