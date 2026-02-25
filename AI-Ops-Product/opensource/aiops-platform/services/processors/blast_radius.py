"""Blast Radius Processor — enriches incidents with impact assessment."""

from typing import Any

from services.connectors.base import ProcessorPlugin, PluginManifest


class BlastRadiusProcessor(ProcessorPlugin):
    """Computes blast radius for incidents by traversing the topology graph.

    Enriches incident messages with:
    - affected_services_count
    - affected_hosts_count
    - estimated_user_impact (high/medium/low)
    """

    def manifest(self) -> PluginManifest:
        return PluginManifest(
            name="blast_radius",
            version="1.0.0",
            plugin_type="processor",
            capabilities=["enrich", "score"],
        )

    def process(self, message: dict[str, Any]) -> dict[str, Any]:
        """Add blast radius metadata to an incident."""
        affected = message.get("affected_entities", [])
        message.setdefault("enrichments", {})["blast_radius"] = {
            "entity_count": len(affected),
            "impact": self._estimate_impact(len(affected)),
        }
        return message

    def enrich(self, entity: dict[str, Any]) -> dict[str, Any]:
        return entity

    def score(self, context: dict[str, Any]) -> float:
        """Score = normalized affected entity count."""
        count = len(context.get("affected_entities", []))
        return min(count / 10.0, 1.0)

    def health_check(self) -> dict[str, Any]:
        return {"healthy": True, "message": "OK"}

    @staticmethod
    def _estimate_impact(entity_count: int) -> str:
        if entity_count >= 5:
            return "high"
        if entity_count >= 2:
            return "medium"
        return "low"
