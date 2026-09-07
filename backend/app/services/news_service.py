"""
External news aggregation service.

Fetches financial news from multiple African sources via RSS feeds,
supplemented by NewsAPI for global coverage.
"""

import hashlib
from datetime import datetime, timezone
from typing import Optional

import httpx
from bs4 import BeautifulSoup

from app.config import get_settings
from app.shared.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


RSS_FEEDS = [
    {"name": "Nairametrics", "url": "https://nairametrics.com/feed", "region": "Nigeria", "category": "finance"},
    {"name": "BusinessDay", "url": "https://businessday.ng/feed", "region": "Nigeria", "category": "business"},
    {"name": "TechCabal", "url": "https://techcabal.com/feed", "region": "Nigeria", "category": "technology"},
    {"name": "Ventures Africa", "url": "https://venturesafrica.com/feed", "region": "Pan-Africa", "category": "business"},
    {"name": "Bloomberg Africa", "url": "https://www.bloomberg.com/feeds/africa", "region": "Global", "category": "markets"},
    {"name": "CNBC Africa", "url": "https://www.cnbcafrica.com/feed", "region": "Pan-Africa", "category": "business"},
]


class RSSReader:
    """Parse RSS/Atom feeds to extract news items."""

    async def fetch_feed(self, feed_url: str, timeout: int = 15) -> list[dict]:
        try:
            async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
                resp = await client.get(feed_url, headers={"User-Agent": "EcoFinwize/1.0"})
                if resp.status_code != 200:
                    logger.warning("RSS fetch failed %d: %s", resp.status_code, feed_url)
                    return []
                return self._parse_feed(resp.text, feed_url)
        except httpx.TimeoutException:
            logger.warning("RSS timeout: %s", feed_url)
            return []
        except Exception as e:
            logger.debug("RSS error %s: %s", feed_url, e)
            return []

    def _parse_feed(self, content: str, feed_url: str) -> list[dict]:
        items = []
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(content)

            # Try RSS 2.0
            for item in root.iter("item"):
                parsed = self._parse_rss_item(item)
                if parsed:
                    items.append(parsed)

            # Try Atom
            if not items:
                ns = {"atom": "http://www.w3.org/2005/Atom"}
                for entry in root.iter("{http://www.w3.org/2005/Atom}entry"):
                    parsed = self._parse_atom_entry(entry)
                    if parsed:
                        items.append(parsed)
        except ET.ParseError:
            pass
        return items

    def _parse_rss_item(self, item) -> Optional[dict]:
        def _tag_text(tag):
            el = item.find(tag)
            return el.text.strip() if el is not None and el.text else ""

        title = _tag_text("title")
        link = _tag_text("link")
        pub_date_str = _tag_text("pubDate")
        description = _tag_text("description")

        if not title or not link:
            return None

        pub_date = datetime.now(timezone.utc)
        if pub_date_str:
            try:
                from email.utils import parsedate_to_datetime
                pub_date = parsedate_to_datetime(pub_date_str)
            except Exception:
                pass

        return {
            "title": title,
            "url": link,
            "summary": BeautifulSoup(description, "html.parser").get_text()[:500] if description else "",
            "published_date": pub_date,
            "source": feed_url,
        }

    def _parse_atom_entry(self, entry) -> Optional[dict]:
        def _tag_text(tag):
            el = entry.find(f"{{http://www.w3.org/2005/Atom}}{tag}")
            return el.text.strip() if el is not None and el.text else ""

        title = _tag_text("title")
        link_el = entry.find("{http://www.w3.org/2005/Atom}link")
        link = link_el.attrib.get("href", "") if link_el is not None else ""
        published = _tag_text("published")
        summary = _tag_text("summary")

        if not title or not link:
            return None

        pub_date = datetime.now(timezone.utc)
        if published:
            try:
                pub_date = datetime.fromisoformat(published.replace("Z", "+00:00"))
            except Exception:
                pass

        return {
            "title": title,
            "url": link,
            "summary": BeautifulSoup(summary, "html.parser").get_text()[:500] if summary else "",
            "published_date": pub_date,
            "source": "atom",
        }


class NewsAPIService:
    """NewsAPI.org integration for supplemental global financial news."""

    def __init__(self):
        self.api_key = settings.newsapi_key
        self.base_url = "https://newsapi.org/v2"

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def fetch_financial_news(self, query: str = "African finance", page_size: int = 20) -> list[dict]:
        if not self.is_configured:
            return []
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"{self.base_url}/everything",
                    params={
                        "q": query,
                        "language": "en",
                        "sortBy": "publishedAt",
                        "pageSize": page_size,
                        "apiKey": self.api_key,
                    },
                )
                if resp.status_code == 200:
                    articles = resp.json().get("articles", [])
                    return [
                        {
                            "title": a["title"],
                            "url": a["url"],
                            "summary": a.get("description", "")[:500],
                            "published_date": a.get("publishedAt", ""),
                            "source": a["source"].get("name", "NewsAPI"),
                            "image_url": a.get("urlToImage"),
                        }
                        for a in articles
                    ]
                logger.warning("NewsAPI error %d: %s", resp.status_code, resp.text[:100])
                return []
        except Exception as e:
            logger.debug("NewsAPI error: %s", e)
            return []


async def aggregate_news() -> list[dict]:
    """Fetch news from all configured sources and merge."""
    reader = RSSReader()
    all_items = []

    for feed in RSS_FEEDS:
        items = await reader.fetch_feed(feed["url"])
        for item in items:
            item["category"] = feed.get("category", "general")
            item["region"] = feed.get("region", "Pan-Africa")
            item["source_name"] = feed["name"]
            all_items.append(item)

    newsapi = NewsAPIService()
    if newsapi.is_configured:
        api_items = await newsapi.fetch_financial_news()
        for item in api_items:
            item["category"] = "markets"
            item["region"] = "Global"
            item["source_name"] = item.get("source", "NewsAPI")
            all_items.append(item)

    all_items.sort(key=lambda x: x.get("published_date", ""), reverse=True)

    seen = set()
    unique = []
    for item in all_items:
        key = hashlib.md5(item["title"].encode()).hexdigest()
        if key not in seen:
            seen.add(key)
            unique.append(item)

    return unique[:50]
