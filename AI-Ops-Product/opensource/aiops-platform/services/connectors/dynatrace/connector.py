"""Dynatrace connector — Smartscape topology + APM events."""

from datetime import datetime
from typing import Any

from services.connectors.base import ConnectorPlugin, PluginManifest


class DynatraceConnector(ConnectorPlugin):
    """Fetches entities, relations, and events from Dynatrace.

    Required config:
        base_url: Dynatrace environment URL
        api_token: API token with entities.read, problems.read scopes
    """

    def manifest(self) -> PluginManifest:
        return PluginManifest(
            name="dynatrace",
            version="1.0.0",
            plugin_type="connector",
            capabilities=["entities", "relations", "events"],
            required_secrets=["api_token"],
        )

    def fetch_entities(self, since: datetime | None = None) -> list[dict[str, Any]]:
        # TODO: GET /api/v2/entities?entitySelector=type("HOST"),type("SERVICE"),...
        return []

    def fetch_relations(self, since: datetime | None = None) -> list[dict[str, Any]]:
        # TODO: Extract from entity toRelationships/fromRelationships
        return []

    def fetch_events(self, since: datetime | None = None) -> list[dict[str, Any]]:
        # TODO: GET /api/v2/problems?from=now-1h
        return []

    def health_check(self) -> dict[str, Any]:
        # TODO: GET /api/v1/config/clusterversion
        return {"healthy": False, "message": "Not connected (stub)"}
