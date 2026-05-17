from __future__ import annotations

import logging
import chromadb
from chromadb.config import Settings as ChromaSettings

from wonderhow.config import settings

logger = logging.getLogger(__name__)


class SemanticMemory:
    """ChromaDB-backed vector memory for semantic retrieval."""

    def __init__(self):
        self._client: chromadb.ClientAPI | None = None
        self._collections: dict[str, chromadb.Collection] = {}

    def connect(self):
        try:
            self._client = chromadb.HttpClient(
                host=settings.chroma_host,
                port=settings.chroma_port,
                settings=ChromaSettings(anonymized_telemetry=False),
            )
            self._client.heartbeat()
            logger.info("Connected to ChromaDB at %s:%s", settings.chroma_host, settings.chroma_port)
        except Exception:
            logger.warning("ChromaDB unavailable, using ephemeral client")
            self._client = chromadb.EphemeralClient()

    def _get_collection(self, agent_id: str) -> chromadb.Collection:
        if agent_id not in self._collections:
            safe_name = f"agent_{agent_id.replace('-', '_')[:48]}"
            self._collections[agent_id] = self._client.get_or_create_collection(
                name=safe_name,
                metadata={"hnsw:space": "cosine"},
            )
        return self._collections[agent_id]

    def store(self, agent_id: str, doc_id: str, text: str, metadata: dict | None = None):
        if not self._client:
            return
        try:
            coll = self._get_collection(agent_id)
            coll.upsert(
                ids=[doc_id],
                documents=[text],
                metadatas=[metadata or {}],
            )
        except Exception:
            logger.warning("Semantic store failed for agent %s", agent_id, exc_info=True)

    def query(self, agent_id: str, query_text: str, n_results: int = 5) -> list[dict]:
        if not self._client:
            return []
        try:
            coll = self._get_collection(agent_id)
            if coll.count() == 0:
                return []
            results = coll.query(query_texts=[query_text], n_results=min(n_results, coll.count()))
            docs = results.get("documents", [[]])[0]
            metas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]
            return [
                {"text": doc, "metadata": meta, "distance": dist}
                for doc, meta, dist in zip(docs, metas, distances)
            ]
        except Exception:
            logger.warning("Semantic query failed for agent %s", agent_id, exc_info=True)
            return []
