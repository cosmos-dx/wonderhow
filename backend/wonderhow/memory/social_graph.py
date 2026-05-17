from __future__ import annotations

import json
import logging
import networkx as nx

logger = logging.getLogger(__name__)


class SocialGraph:
    """Agent relationship graph using NetworkX with JSON persistence."""

    def __init__(self):
        self.graph = nx.DiGraph()

    def add_agent(self, agent_id: str, name: str):
        self.graph.add_node(agent_id, name=name)

    def update_relationship(
        self,
        from_agent: str,
        to_agent: str,
        trust_delta: float = 0.0,
        interaction_type: str = "neutral",
    ):
        if self.graph.has_edge(from_agent, to_agent):
            data = self.graph[from_agent][to_agent]
            data["trust"] = max(-1.0, min(1.0, data.get("trust", 0.0) + trust_delta))
            data["interactions"] = data.get("interactions", 0) + 1
            data["last_interaction"] = interaction_type
        else:
            self.graph.add_edge(
                from_agent, to_agent,
                trust=max(-1.0, min(1.0, trust_delta)),
                interactions=1,
                last_interaction=interaction_type,
            )

    def get_trust(self, from_agent: str, to_agent: str) -> float:
        if self.graph.has_edge(from_agent, to_agent):
            return self.graph[from_agent][to_agent].get("trust", 0.0)
        return 0.0

    def get_relationships(self, agent_id: str) -> list[dict]:
        relationships = []
        for _, target, data in self.graph.out_edges(agent_id, data=True):
            target_name = self.graph.nodes[target].get("name", target)
            relationships.append({
                "agent_id": target,
                "agent_name": target_name,
                "trust": data.get("trust", 0.0),
                "interactions": data.get("interactions", 0),
                "last_interaction": data.get("last_interaction", "none"),
            })
        return relationships

    def get_allies(self, agent_id: str, threshold: float = 0.3) -> list[str]:
        return [
            target for _, target, data in self.graph.out_edges(agent_id, data=True)
            if data.get("trust", 0.0) >= threshold
        ]

    def get_rivals(self, agent_id: str, threshold: float = -0.2) -> list[str]:
        return [
            target for _, target, data in self.graph.out_edges(agent_id, data=True)
            if data.get("trust", 0.0) <= threshold
        ]

    def most_influential(self, top_n: int = 5) -> list[tuple[str, float]]:
        if not self.graph.nodes:
            return []
        try:
            scores = nx.pagerank(self.graph, weight="trust")
            sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            return sorted_scores[:top_n]
        except Exception:
            return []

    def to_dict(self) -> dict:
        return nx.node_link_data(self.graph)

    def from_dict(self, data: dict):
        if data:
            try:
                self.graph = nx.node_link_graph(data)
            except Exception:
                logger.warning("Failed to restore social graph from dict")
                self.graph = nx.DiGraph()

    def get_visualization_data(self) -> dict:
        nodes = [
            {"id": n, "name": self.graph.nodes[n].get("name", n)}
            for n in self.graph.nodes
        ]
        edges = [
            {
                "source": u,
                "target": v,
                "trust": data.get("trust", 0.0),
                "interactions": data.get("interactions", 0),
            }
            for u, v, data in self.graph.edges(data=True)
        ]
        return {"nodes": nodes, "edges": edges}
