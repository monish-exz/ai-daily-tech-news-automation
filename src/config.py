"""
Configuration management for the universal scraping system.
"""

from typing import List
from src.models import SourceConfig, SourceType


def get_default_sources() -> List[SourceConfig]:
    """
    Default source configuration.
    Maintains backward compatibility with original RSS-only system.
    """
    return [
        SourceConfig(
            url="https://techcrunch.com/tag/artificial-intelligence/feed/",
            name="TechCrunch",
            source_type=SourceType.RSS_FEED,
            max_items=8
        ),
        SourceConfig(
            url="https://www.technologyreview.com/feed/",
            name="MIT Technology Review",
            source_type=SourceType.RSS_FEED,
            max_items=8
        ),
        SourceConfig(
            url="https://analyticsindiamag.com/feed/",
            name="Analytics India Magazine",
            source_type=SourceType.RSS_FEED,
            max_items=8
        ),
    ]


def migrate_legacy_config(rss_feeds: List[dict]) -> List[SourceConfig]:
    """
    Migrate old RSS feed configuration to new SourceConfig format.
    
    Args:
        rss_feeds: List of dicts with 'name' and 'url' keys
        
    Returns:
        List of SourceConfig objects
    """
    sources = []
    for feed in rss_feeds:
        sources.append(SourceConfig(
            url=feed["url"],
            name=feed["name"],
            source_type=SourceType.RSS_FEED,
            max_items=8
        ))
    return sources
