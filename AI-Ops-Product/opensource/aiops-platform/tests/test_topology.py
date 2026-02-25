"""Tests for TopologyGraphBuilder."""

import json
from pathlib import Path

from services.topology.graph_builder import TopologyGraphBuilder

EXAMPLES = Path(__file__).resolve().parent.parent / "contracts" / "examples"


def _load(name: str):
    with open(EXAMPLES / name) as f:
        return json.load(f)


def test_build_from_json():
    g = TopologyGraphBuilder()
    g.build_from_json(_load("entities.json"), _load("relations.json"))
    assert g.entity_count == 8
    assert g.relation_count == 10


def test_get_entity():
    g = TopologyGraphBuilder()
    g.build_from_json(_load("entities.json"), _load("relations.json"))
    entity = g.get_entity("ent:database:postgres-primary")
    assert entity is not None
    assert entity["entity_type"] == "database"
    assert entity["display_name"] == "postgres-primary (orders-db)"


def test_get_neighbors():
    g = TopologyGraphBuilder()
    g.build_from_json(_load("entities.json"), _load("relations.json"))
    neighbors = g.get_neighbors("ent:service:api-service", direction="both")
    assert len(neighbors) >= 2  # at least postgres + lb or web-app


def test_get_path():
    g = TopologyGraphBuilder()
    g.build_from_json(_load("entities.json"), _load("relations.json"))
    path = g.get_path("ent:application:web-app", "ent:database:postgres-primary")
    assert path is not None
    assert path[0] == "ent:application:web-app"
    assert path[-1] == "ent:database:postgres-primary"


def test_get_path_nonexistent():
    g = TopologyGraphBuilder()
    g.add_entity({"canonical_id": "a", "entity_type": "host", "display_name": "a"})
    g.add_entity({"canonical_id": "b", "entity_type": "host", "display_name": "b"})
    # No edge between a and b
    path = g.get_path("a", "b")
    assert path is None


def test_to_dict():
    g = TopologyGraphBuilder()
    g.build_from_json(_load("entities.json"), _load("relations.json"))
    d = g.to_dict()
    assert len(d["entities"]) == 8
    assert len(d["relations"]) == 10
