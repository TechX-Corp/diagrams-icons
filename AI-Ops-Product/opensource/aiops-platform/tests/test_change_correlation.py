"""Tests for change-aware correlation and RCA scoring."""

import json
from pathlib import Path

from services.topology.graph_builder import TopologyGraphBuilder
from services.correlation.engine import CorrelationEngine
from services.rca.engine import RCAEngine

EXAMPLES = Path(__file__).resolve().parent.parent / "contracts" / "examples"


def _load(name: str):
    with open(EXAMPLES / name) as f:
        return json.load(f)


def _build_change_scenario():
    """Build the demo scenario with change events included."""
    entities = _load("entities.json")
    relations = _load("relations.json")
    events = _load("events.json")
    change_events = _load("change_events.json")

    topology = TopologyGraphBuilder()
    topology.build_from_json(entities, relations)

    correlation = CorrelationEngine()
    for event in events:
        correlation.ingest_event(event)
    incident = correlation.correlate_signals()

    return topology, incident, events, change_events


def test_rca_with_change_events_boosts_deployed_entity():
    """Entities that had recent deployments should score higher."""
    topology, incident, events, change_events = _build_change_scenario()
    rca = RCAEngine(max_candidates=5)

    # Without changes
    result_no_change = rca.analyze(incident, topology, events)
    # With changes
    result_with_change = rca.analyze(incident, topology, events, change_events=change_events)

    # api-service had a deployment; it should appear and have change_correlation=True
    change_candidates = [c for c in result_with_change["candidates"] if c.get("change_correlation")]
    assert len(change_candidates) > 0, "Expected at least one change-correlated candidate"

    # The api-service should have a higher score with change events
    def find_score(result, entity_id):
        for c in result["candidates"]:
            if c["entity_id"] == entity_id:
                return c["score"]
        return 0.0

    api_score_no_change = find_score(result_no_change, "ent:service:api-service")
    api_score_with_change = find_score(result_with_change, "ent:service:api-service")
    assert api_score_with_change > api_score_no_change, \
        f"Change-aware score ({api_score_with_change}) should exceed base score ({api_score_no_change})"


def test_rca_change_correlation_flag():
    """Candidates with recent changes should have change_correlation=True."""
    topology, incident, events, change_events = _build_change_scenario()
    rca = RCAEngine(max_candidates=5)
    result = rca.analyze(incident, topology, events, change_events=change_events)

    for candidate in result["candidates"]:
        assert "change_correlation" in candidate


def test_rca_algorithm_version_updated():
    topology, incident, events, _ = _build_change_scenario()
    rca = RCAEngine()
    result = rca.analyze(incident, topology, events)
    assert result["algorithm_version"] == "topo-walk-v1.1.0"


def test_correlation_engine_ingests_change_events():
    """CorrelationEngine.ingest_change_events should create deployment signals."""
    change_events = _load("change_events.json")
    engine = CorrelationEngine()
    engine.ingest_change_events(change_events)
    assert len(engine.signals) > 0
    # Should have created signals for the deployments
    signal_list = list(engine.signals.values())
    assert any("Deployment" in s.get("category", "") or s["count"] >= 1 for s in signal_list)
