"""Topology graph builder using NetworkX for in-memory graph operations."""

from typing import Any

import networkx as nx


class TopologyGraphBuilder:
    """Builds and maintains an in-memory topology graph of entities and relations.

    Entities are stored as nodes with attributes. Relations are stored as
    directed edges. Supports graph queries for RCA traversal.
    """

    def __init__(self) -> None:
        self.graph = nx.MultiDiGraph()

    def add_entity(self, entity: dict[str, Any]) -> None:
        """Add an entity as a node in the graph."""
        self.graph.add_node(entity["canonical_id"], **entity)

    def add_relation(self, relation: dict[str, Any]) -> None:
        """Add a relation as a directed edge in the graph."""
        self.graph.add_edge(
            relation["source_entity_id"],
            relation["target_entity_id"],
            **relation,
        )

    def build_from_json(
        self, entities: list[dict[str, Any]], relations: list[dict[str, Any]]
    ) -> None:
        """Build the graph from lists of entity and relation dicts."""
        for entity in entities:
            self.add_entity(entity)
        for relation in relations:
            self.add_relation(relation)

    def get_entity(self, entity_id: str) -> dict[str, Any] | None:
        """Get entity attributes by canonical_id."""
        if entity_id in self.graph.nodes:
            return dict(self.graph.nodes[entity_id])
        return None

    def get_neighbors(self, entity_id: str, direction: str = "both") -> list[str]:
        """Get neighboring entity IDs.

        Args:
            direction: "in" (predecessors), "out" (successors), "both"
        """
        neighbors: set[str] = set()
        if direction in ("out", "both"):
            neighbors.update(self.graph.successors(entity_id))
        if direction in ("in", "both"):
            neighbors.update(self.graph.predecessors(entity_id))
        return list(neighbors)

    def get_subgraph(self, entity_ids: list[str]) -> "TopologyGraphBuilder":
        """Extract a subgraph containing only the specified entities."""
        sub = TopologyGraphBuilder()
        sub.graph = self.graph.subgraph(entity_ids).copy()
        return sub

    def get_path(self, source_id: str, target_id: str) -> list[str] | None:
        """Find shortest path between two entities (ignoring edge direction)."""
        try:
            return nx.shortest_path(self.graph.to_undirected(), source_id, target_id)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None

    def get_all_reachable(self, entity_id: str, max_depth: int = 5) -> set[str]:
        """Get all entities reachable from the given entity (undirected BFS)."""
        undirected = self.graph.to_undirected()
        reachable: set[str] = set()
        if entity_id not in undirected:
            return reachable
        for node in nx.bfs_tree(undirected, entity_id, depth_limit=max_depth):
            if node != entity_id:
                reachable.add(node)
        return reachable

    def to_dict(self) -> dict[str, Any]:
        """Serialize the graph to a dict."""
        return {
            "entities": [
                {"canonical_id": n, **self.graph.nodes[n]} for n in self.graph.nodes
            ],
            "relations": [
                {**data, "source_entity_id": u, "target_entity_id": v}
                for u, v, data in self.graph.edges(data=True)
            ],
        }

    @property
    def entity_count(self) -> int:
        return self.graph.number_of_nodes()

    @property
    def relation_count(self) -> int:
        return self.graph.number_of_edges()
