"""Change Scorer Processor — scores entities by recent deployment activity."""

from typing import Any

from services.connectors.base import ProcessorPlugin, PluginManifest


class ChangeScorerProcessor(ProcessorPlugin):
    """Enriches RCA candidates with change-based risk scores.

    Scores are based on:
    - Recency of deployment relative to incident
    - Deployment status (failed > succeeded)
    - Number of affected entities in the deployment
    """

    def manifest(self) -> PluginManifest:
        return PluginManifest(
            name="change_scorer",
            version="1.0.0",
            plugin_type="processor",
            capabilities=["score", "enrich"],
        )

    def process(self, message: dict[str, Any]) -> dict[str, Any]:
        return message

    def enrich(self, entity: dict[str, Any]) -> dict[str, Any]:
        """Add change_risk_score to entity attributes."""
        changes = entity.get("recent_changes", [])
        if changes:
            entity.setdefault("attributes", {})["change_risk_score"] = self.score(
                {"changes": changes}
            )
        return entity

    def score(self, context: dict[str, Any]) -> float:
        """Score 0-1 based on change risk factors."""
        changes = context.get("changes", [])
        if not changes:
            return 0.0

        max_score = 0.0
        for change in changes:
            base = 0.5
            if change.get("status") == "failed":
                base = 1.0
            elif change.get("status") == "rolled_back":
                base = 0.9
            elif change.get("status") == "succeeded":
                base = 0.6

            affected_count = len(change.get("affected_entities", []))
            breadth_bonus = min(affected_count * 0.05, 0.2)
            max_score = max(max_score, min(base + breadth_bonus, 1.0))

        return round(max_score, 4)

    def health_check(self) -> dict[str, Any]:
        return {"healthy": True, "message": "OK"}
