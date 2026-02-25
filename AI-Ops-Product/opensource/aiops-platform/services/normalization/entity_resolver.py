"""Entity identity resolution — maps raw entities to canonical CDM entities."""

import hashlib
from typing import Any


class EntityResolver:
    """Resolves raw entities from source systems into canonical CDM entities.

    Generates deterministic canonical IDs and handles entity merging
    when the same real-world entity is seen from multiple sources.
    """

    def __init__(self) -> None:
        self._entity_store: dict[str, dict[str, Any]] = {}

    def resolve(self, raw_entity: dict[str, Any], source_system: str) -> dict[str, Any]:
        """Transform a raw entity into a CDM entity with canonical ID.

        Args:
            raw_entity: Entity data from a connector (source-native format).
            source_system: Name of the source system (e.g., "dynatrace").

        Returns:
            CDM entity dict with canonical_id resolved.
        """
        entity_type = raw_entity.get("entity_type", "host")
        display_name = raw_entity.get("display_name", "unknown")
        canonical_id = self.generate_canonical_id(entity_type, display_name)

        entity = {
            "canonical_id": canonical_id,
            "entity_type": entity_type,
            "display_name": display_name,
            "source_refs": [
                {"source_system": source_system, "native_id": raw_entity.get("native_id", "")}
            ],
            "attributes": raw_entity.get("attributes", {}),
            "tags": raw_entity.get("tags", []),
            "first_seen": raw_entity.get("first_seen", ""),
            "last_seen": raw_entity.get("last_seen", ""),
            "confidence_score": 1.0,
            "lifecycle_state": "active",
        }

        if canonical_id in self._entity_store:
            entity = self.merge_entities(self._entity_store[canonical_id], entity)

        self._entity_store[canonical_id] = entity
        return entity

    @staticmethod
    def generate_canonical_id(entity_type: str, primary_key: str) -> str:
        """Generate a deterministic canonical ID from entity type and primary key.

        The ID is stable across runs for the same input.
        """
        raw = f"{entity_type}:{primary_key}"
        hash_hex = hashlib.sha256(raw.encode()).hexdigest()[:16]
        return f"ent:{entity_type}:{hash_hex}"

    @staticmethod
    def merge_entities(existing: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
        """Merge an incoming entity observation into an existing entity.

        - Source refs are appended (deduped by source_system)
        - Attributes are merged (incoming overwrites on conflict)
        - Tags are unioned
        - Timestamps are updated (first_seen = min, last_seen = max)
        """
        merged = dict(existing)

        existing_sources = {ref["source_system"] for ref in merged.get("source_refs", [])}
        for ref in incoming.get("source_refs", []):
            if ref["source_system"] not in existing_sources:
                merged["source_refs"].append(ref)

        merged_attrs = dict(merged.get("attributes", {}))
        merged_attrs.update(incoming.get("attributes", {}))
        merged["attributes"] = merged_attrs

        merged_tags = list(set(merged.get("tags", []) + incoming.get("tags", [])))
        merged["tags"] = merged_tags

        if incoming.get("first_seen") and (
            not merged.get("first_seen") or incoming["first_seen"] < merged["first_seen"]
        ):
            merged["first_seen"] = incoming["first_seen"]
        if incoming.get("last_seen") and (
            not merged.get("last_seen") or incoming["last_seen"] > merged["last_seen"]
        ):
            merged["last_seen"] = incoming["last_seen"]

        num_sources = len(merged["source_refs"])
        merged["confidence_score"] = min(1.0, 0.8 + 0.1 * num_sources)

        return merged
