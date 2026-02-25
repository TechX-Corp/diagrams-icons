"""Confluence connector — runbook and knowledge base search."""

from datetime import datetime
from typing import Any

from services.connectors.base import ConnectorPlugin, PluginManifest


class ConfluenceConnector(ConnectorPlugin):
    """Searches Confluence for runbooks and resolution hints.

    Required config:
        base_url: Confluence Cloud/Server URL
        email: User email
        api_token: API token
        space_key: Default space for runbook search
    """

    def manifest(self) -> PluginManifest:
        return PluginManifest(
            name="confluence",
            version="1.0.0",
            plugin_type="connector",
            capabilities=["entities"],
            required_secrets=["email", "api_token"],
        )

    def fetch_entities(self, since: datetime | None = None) -> list[dict[str, Any]]:
        # TODO: GET /wiki/rest/api/content?spaceKey=...&type=page
        # Returns runbook pages as knowledge entities
        return []

    def health_check(self) -> dict[str, Any]:
        return {"healthy": False, "message": "Not connected (stub)"}
