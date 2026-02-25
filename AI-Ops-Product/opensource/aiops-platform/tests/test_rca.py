"""Tests for RCAEngine."""

import json
from pathlib import Path

from services.topology.graph_builder import TopologyGraphBuilder
from services.correlation.engine import CorrelationEngine
from services.rca.engine import RCAEngine

EXAMPLES = Path(__file__).resolve().parent.parent / "contracts" / "examples"


def _load(name: str):
    with open(EXAMPLES / name) as f:
        return json.load(f)


def _build_scenario():
    """Build the full demo scenario: graph + incident + events."""
    entities = _load("entities.json")
    relations = _load("relations.json")
    events = _load("events.json")

    topology = TopologyGraphBuilder()
    topology.build_from_json(entities, relations)

    correlation = CorrelationEngine()
    for event in events:
        correlation.ingest_event(event)
    incident = correlation.correlate_signals()

    return topology, incident, events


def test_rca_returns_candidates():
    topology, incident, events = _build_scenario()
    rca = RCAEngine(max_candidates=3)
    result = rca.analyze(incident, topology, events)

    assert result["incident_id"] == incident["incident_id"]
    assert len(result["candidates"]) > 0
    assert len(result["candidates"]) <= 3


def test_rca_candidates_have_scores():
    topology, incident, events = _build_scenario()
    rca = RCAEngine(max_candidates=3)
    result = rca.analyze(incident, topology, events)

    for candidate in result["candidates"]:
        assert candidate["score"] > 0
        assert 0 <= candidate["score"] <= 1
        assert len(candidate["evidence_path"]) >= 1
        assert len(candidate["explanation"]) > 0


def test_rca_top_candidate_is_plausible():
    """The postgres-host or postgres-primary should rank high (root cause of the scenario)."""
    topology, incident, events = _build_scenario()
    rca = RCAEngine(max_candidates=5)
    result = rca.analyze(incident, topology, events)

    top_ids = [c["entity_id"] for c in result["candidates"][:3]]
    # At least one of the database-related entities should be in top 3
    db_related = {"ent:vm:postgres-host", "ent:database:postgres-primary"}
    assert db_related & set(top_ids), f"Expected DB entity in top 3, got {top_ids}"


def test_rca_has_algorithm_version():
    topology, incident, events = _build_scenario()
    rca = RCAEngine()
    result = rca.analyze(incident, topology, events)
    assert result["algorithm_version"] == "topo-walk-v1.1.0"
    assert result["computed_at"] is not None
    assert 0 <= result["confidence"] <= 1
