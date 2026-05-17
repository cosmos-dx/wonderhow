from __future__ import annotations

import logging
from datetime import datetime, timedelta

import httpx

from wonderhow.config import settings

logger = logging.getLogger(__name__)

INDIA_NEWS_CATEGORIES = {
    "geopolitics": "india politics defense diplomacy",
    "entertainment": "bollywood india entertainment movies",
    "science": "india science space ISRO technology",
    "music": "india music bollywood indie",
}


class NewsFetcher:
    """Fetch trending news for topic seeding."""

    def __init__(self):
        self._client = httpx.AsyncClient(timeout=15.0)

    async def fetch_news(
        self, category: str = "general", max_articles: int = 5
    ) -> list[dict]:
        if settings.newsapi_key:
            return await self._newsapi_fetch(category, max_articles)
        return await self._free_news_fetch(category, max_articles)

    async def _newsapi_fetch(self, category: str, max_articles: int) -> list[dict]:
        query = INDIA_NEWS_CATEGORIES.get(category, category)
        from_date = (datetime.utcnow() - timedelta(days=2)).strftime("%Y-%m-%d")
        try:
            resp = await self._client.get(
                "https://newsapi.org/v2/everything",
                params={
                    "q": query,
                    "from": from_date,
                    "sortBy": "relevancy",
                    "pageSize": max_articles,
                    "language": "en",
                    "apiKey": settings.newsapi_key,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return [
                {
                    "title": a.get("title", ""),
                    "description": a.get("description", ""),
                    "url": a.get("url", ""),
                    "source": a.get("source", {}).get("name", ""),
                    "published_at": a.get("publishedAt", ""),
                }
                for a in data.get("articles", [])
            ]
        except Exception:
            logger.warning("NewsAPI fetch failed for: %s, falling back to free search", category)
            return await self._free_news_fetch(category, max_articles)

    async def _free_news_fetch(self, category: str, max_articles: int) -> list[dict]:
        """Fallback: use DuckDuckGo news-style search."""
        query = INDIA_NEWS_CATEGORIES.get(category, category) + " news today"
        try:
            resp = await self._client.get(
                "https://api.duckduckgo.com/",
                params={"q": query, "format": "json", "no_html": 1},
            )
            resp.raise_for_status()
            data = resp.json()
            results = []
            for topic in data.get("RelatedTopics", [])[:max_articles]:
                if isinstance(topic, dict) and "Text" in topic:
                    results.append({
                        "title": topic.get("Text", "")[:100],
                        "description": topic.get("Text", ""),
                        "url": topic.get("FirstURL", ""),
                        "source": "web",
                        "published_at": datetime.utcnow().isoformat(),
                    })
            return results
        except Exception:
            logger.warning("Free news fetch failed", exc_info=True)
            return []

    async def close(self):
        await self._client.aclose()
