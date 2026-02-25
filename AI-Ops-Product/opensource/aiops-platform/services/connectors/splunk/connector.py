"""Splunk connector — log events and saved search alerts."""

from datetime import datetime
from typing import Any

from services.connectors.base import ConnectorPlugin, PluginManifest


class SplunkConnector(ConnectorPlugin):
    """Fetches events from Splunk via REST API or HEC webhook.

    Required config:
        base_url: Splunk instance URL
        token: Bearer token or HEC token
    """

    def manifest(self) -> PluginManifest:
        return PluginManifest(
            name="splunk",
            version="1.0.0",
            plugin_type="connector",
            capabilities=["events", "signals"],
            required_secrets=["token"],
        )

    def fetch_events(self, since: datetime | None = None) -> list[dict[str, Any]]:
        # TODO: POST /services/search/jobs with SPL query
        return []

    def fetch_signals(self, since: datetime | None = None) -> list[dict[str, Any]]:
        # TODO: GET /services/saved/searches with triggered_alerts
        return []

    def health_check(self) -> dict[str, Any]:
        return {"healthy": False, "message": "Not connected (stub)"}
