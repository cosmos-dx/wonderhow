from __future__ import annotations

import random
import logging
from wonderhow.knowledge.news_fetcher import NewsFetcher
from wonderhow.knowledge.web_search import WebSearcher

logger = logging.getLogger(__name__)

SEED_TOPICS = {
    "geopolitics": [
        "India's foreign policy and relations with neighboring countries",
        "India's stance on global climate change agreements",
        "India-China border tensions and diplomatic developments",
        "India's role in BRICS and multilateral organizations",
        "Digital India initiatives and their impact",
        "Indian defense modernization and self-reliance",
    ],
    "entertainment": [
        "Latest Bollywood releases and box office performance",
        "Rise of OTT platforms in India",
        "Indie cinema vs mainstream Bollywood debate",
        "K-drama and anime influence on Indian youth",
        "South Indian cinema going national",
        "Evolution of comedy in Indian entertainment",
    ],
    "science": [
        "ISRO's latest missions and India's space ambitions",
        "AI and its impact on Indian job market",
        "India's semiconductor manufacturing push",
        "Climate change effects on Indian agriculture",
        "Quantum computing research in India",
        "Indian contributions to global scientific research",
    ],
    "music": [
        "Classical music vs modern fusion debate",
        "Rise of Indian hip-hop and rap scene",
        "Bollywood music quality over the decades",
        "Independent music scene in India",
        "AI-generated music and its implications",
        "Regional music going mainstream",
    ],
}


class TopicTracker:
    """Tracks and generates discussion topics for groups."""

    def __init__(self, news_fetcher: NewsFetcher, web_searcher: WebSearcher):
        self.news_fetcher = news_fetcher
        self.web_searcher = web_searcher
        self._used_topics: dict[str, set[str]] = {}

    async def get_trending_topic(self, theme: str) -> str | None:
        news = await self.news_fetcher.fetch_news(category=theme, max_articles=3)
        for article in news:
            title = article.get("title", "")
            if title and title not in self._used_topics.get(theme, set()):
                self._used_topics.setdefault(theme, set()).add(title)
                return title
        return self._get_seed_topic(theme)

    def _get_seed_topic(self, theme: str) -> str:
        seeds = SEED_TOPICS.get(theme, SEED_TOPICS["geopolitics"])
        used = self._used_topics.get(theme, set())
        unused = [s for s in seeds if s not in used]
        if not unused:
            self._used_topics[theme] = set()
            unused = seeds
        chosen = random.choice(unused)
        self._used_topics.setdefault(theme, set()).add(chosen)
        return chosen

    def get_random_seed(self, theme: str) -> str:
        return self._get_seed_topic(theme)
