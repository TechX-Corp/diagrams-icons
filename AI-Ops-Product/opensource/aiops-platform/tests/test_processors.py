"""Tests for Tier 2 processor plugins."""

from services.processors.blast_radius import BlastRadiusProcessor
from services.processors.noise_reducer import NoiseReducerProcessor
from services.processors.change_scorer import ChangeScorerProcessor
from services.connectors.base import ProcessorPlugin


def test_blast_radius_enriches_incident():
    proc = BlastRadiusProcessor({})
    incident = {"affected_entities": ["a", "b", "c", "d", "e"]}
    result = proc.process(incident)
    assert result["enrichments"]["blast_radius"]["entity_count"] == 5
    assert result["enrichments"]["blast_radius"]["impact"] == "high"


def test_blast_radius_score():
    proc = BlastRadiusProcessor({})
    assert proc.score({"affected_entities": list(range(10))}) == 1.0
    assert proc.score({"affected_entities": ["a", "b"]}) == 0.2


def test_noise_reducer_drops_info_events():
    proc = NoiseReducerProcessor({"min_severity": "low"})
    info_event = {"severity": "info", "fingerprint": "fp1"}
    assert proc.process(info_event) is None


def test_noise_reducer_passes_critical():
    proc = NoiseReducerProcessor({"min_severity": "low"})
    critical_event = {"severity": "critical", "fingerprint": "fp2"}
    assert proc.process(critical_event) is not None


def test_noise_reducer_deduplicates():
    proc = NoiseReducerProcessor({})
    event = {"severity": "high", "fingerprint": "fp-dup"}
    assert proc.process(event) is not None  # First pass
    assert proc.process(event) is None  # Duplicate


def test_change_scorer_failed_deploy():
    proc = ChangeScorerProcessor({})
    score = proc.score({"changes": [{"status": "failed", "affected_entities": ["a"]}]})
    assert score == 1.0


def test_change_scorer_succeeded_deploy():
    proc = ChangeScorerProcessor({})
    score = proc.score({"changes": [{"status": "succeeded", "affected_entities": ["a", "b", "c"]}]})
    assert score > 0.6


def test_change_scorer_no_changes():
    proc = ChangeScorerProcessor({})
    assert proc.score({"changes": []}) == 0.0


def test_all_processors_implement_interface():
    for cls in [BlastRadiusProcessor, NoiseReducerProcessor, ChangeScorerProcessor]:
        proc = cls({})
        assert isinstance(proc, ProcessorPlugin)
        m = proc.manifest()
        assert m.plugin_type == "processor"
