"""Tests for EntityResolver."""

from services.normalization.entity_resolver import EntityResolver


def test_canonical_id_is_deterministic():
    r = EntityResolver()
    id1 = r.generate_canonical_id("host", "prod-web-01.example.com")
    id2 = r.generate_canonical_id("host", "prod-web-01.example.com")
    assert id1 == id2
    assert id1.startswith("ent:host:")


def test_different_inputs_different_ids():
    r = EntityResolver()
    id1 = r.generate_canonical_id("host", "prod-web-01")
    id2 = r.generate_canonical_id("host", "prod-web-02")
    assert id1 != id2


def test_different_types_different_ids():
    r = EntityResolver()
    id1 = r.generate_canonical_id("host", "server-01")
    id2 = r.generate_canonical_id("vm", "server-01")
    assert id1 != id2


def test_resolve_creates_entity():
    r = EntityResolver()
    raw = {
        "entity_type": "host",
        "display_name": "test-host",
        "native_id": "H-001",
        "attributes": {"os": "Linux"},
        "tags": ["env:test"],
        "first_seen": "2026-01-01T00:00:00Z",
        "last_seen": "2026-02-25T00:00:00Z",
    }
    entity = r.resolve(raw, "dynatrace")
    assert entity["canonical_id"].startswith("ent:host:")
    assert entity["source_refs"][0]["source_system"] == "dynatrace"
    assert entity["lifecycle_state"] == "active"


def test_merge_entities():
    existing = {
        "canonical_id": "ent:host:abc123",
        "entity_type": "host",
        "display_name": "test-host",
        "source_refs": [{"source_system": "dynatrace", "native_id": "H-001"}],
        "attributes": {"os": "Linux", "cpu": 4},
        "tags": ["env:prod"],
        "first_seen": "2026-01-01T00:00:00Z",
        "last_seen": "2026-02-20T00:00:00Z",
        "confidence_score": 0.9,
    }
    incoming = {
        "canonical_id": "ent:host:abc123",
        "entity_type": "host",
        "display_name": "test-host",
        "source_refs": [{"source_system": "solarwinds", "native_id": "node:42"}],
        "attributes": {"ip": "10.0.0.1"},
        "tags": ["env:prod", "dc:us-east"],
        "first_seen": "2026-01-15T00:00:00Z",
        "last_seen": "2026-02-25T00:00:00Z",
    }

    merged = EntityResolver.merge_entities(existing, incoming)
    assert len(merged["source_refs"]) == 2
    assert merged["attributes"]["os"] == "Linux"
    assert merged["attributes"]["ip"] == "10.0.0.1"
    assert "dc:us-east" in merged["tags"]
    assert merged["first_seen"] == "2026-01-01T00:00:00Z"
    assert merged["last_seen"] == "2026-02-25T00:00:00Z"
    assert merged["confidence_score"] == 1.0  # 0.8 + 0.1 * 2
