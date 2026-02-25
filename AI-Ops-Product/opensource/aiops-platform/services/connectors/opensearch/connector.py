"""OpenSearch connector — log/event search and alerting plugin."""

from datetime import datetime
from typing import Any

from services.connectors.base import ConnectorPlugin, PluginManifest


class OpenSearchConnector(ConnectorPlugin):
    """Fetches events and alerts from OpenSearch.

    Required config:
        base_url: OpenSearch cluster URL
        username, password: credentials (or api_key)
    """

    def manifest(self) -> PluginManifest:
        return PluginManifest(
            name="opensearch",
            version="1.0.0",
            plugin_type="connector",
            capabilities=["events"],
            required_secrets=["username", "password"],
        )

    def fetch_events(self, since: datetime | None = None) -> list[dict[str, Any]]:
        # TODO: POST /_search with range filter on @timestamp
        return []

    def health_check(self) -> dict[str, Any]:
        return {"healthy": False, "message": "Not connected (stub)"}
