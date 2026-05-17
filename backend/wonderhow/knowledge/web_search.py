from __future__ import annotations

import logging
import httpx

from wonderhow.config import settings

logger = logging.getLogger(__name__)


class WebSearcher:
    """Web search using Tavily API with DuckDuckGo fallback."""

    def __init__(self):
        self._client = httpx.AsyncClient(timeout=15.0)

    async def search(self, query: str, max_results: int = 5) -> list[dict]:
        if settings.tavily_api_key:
            return await self._tavily_search(query, max_results)
        return await self._duckduckgo_search(query, max_results)

    async def _tavily_search(self, query: str, max_results: int) -> list[dict]:
        try:
            resp = await self._client.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": settings.tavily_api_key,
                    "query": query,
                    "max_results": max_results,
                    "include_answer": True,
                    "search_depth": "basic",
                },
            )
            resp.raise_for_status()
            data = resp.json()
            results = []
            if data.get("answer"):
                results.append({
                    "title": "AI Summary",
                    "content": data["answer"],
                    "url": "",
                    "source": "tavily",
                })
            for r in data.get("results", [])[:max_results]:
                results.append({
                    "title": r.get("title", ""),
                    "content": r.get("content", ""),
                    "url": r.get("url", ""),
                    "source": "tavily",
                })
            return results
        except Exception:
            logger.warning("Tavily search failed for: %s", query, exc_info=True)
            return await self._duckduckgo_search(query, max_results)

    async def _duckduckgo_search(self, query: str, max_results: int) -> list[dict]:
        try:
            resp = await self._client.get(
                "https://api.duckduckgo.com/",
                params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 1},
            )
            resp.raise_for_status()
            data = resp.json()
            results = []
            if data.get("AbstractText"):
                results.append({
                    "title": data.get("Heading", ""),
                    "content": data["AbstractText"],
                    "url": data.get("AbstractURL", ""),
                    "source": "duckduckgo",
                })
            for topic in data.get("RelatedTopics", [])[:max_results]:
                if isinstance(topic, dict) and "Text" in topic:
                    results.append({
                        "title": topic.get("Text", "")[:80],
                        "content": topic.get("Text", ""),
                        "url": topic.get("FirstURL", ""),
                        "source": "duckduckgo",
                    })
            return results
        except Exception:
            logger.warning("DuckDuckGo search failed for: %s", query, exc_info=True)
            return []

    async def close(self):
        await self._client.aclose()
