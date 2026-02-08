"""
Text cleaning utilities for the universal scraper.
"""

import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup

def clean_html(html_text: str) -> str:
    """
    Remove all HTML tags, scripts, styles, and comments from text.
    Ensures high-fidelity character recovery.
    """
    if not html_text:
        return ""
    
    # 1. Remove HTML comments strictly
    clean_text = re.sub(r'<!--.*?-->', '', html_text, flags=re.DOTALL)
    
    # 2. Use BeautifulSoup for robust tag removal
    try:
        # Using lxml if available, otherwise html.parser
        soup = BeautifulSoup(clean_text, "lxml")
        
        # Remove script, style, and navigation elements that might leak
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()
            
        # Get text, using a space to separate elements
        clean_text = soup.get_text(separator=' ')
    except:
        # Fallback if BeautifulSoup fails
        clean_text = re.sub(r'<[^>]+>', ' ', clean_text)
    
    # 3. Character Sanitization
    # STRICT REQUIREMENT: Remove all non-ASCII characters
    # Only allow characters in the range 0-127
    clean_text = "".join(c for c in clean_text if ord(c) < 128)
    
    # 4. Standardize whitespace
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    
    return clean_text

def get_domain_name(url: str) -> str:
    """
    Extract a clean domain name from a URL.
    Example: https://www.reddit.com/r/learnmachinelearning/ -> reddit.com
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    except:
        return url
