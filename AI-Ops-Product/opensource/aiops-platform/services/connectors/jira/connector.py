"""Jira connector — incident ticket sync and change tracking."""

from datetime import datetime
from typing import Any

from services.connectors.base import ConnectorPlugin, PluginManifest


class JiraConnector(ConnectorPlugin):
    """Syncs incident tickets and change requests from Jira.

    Required config:
        base_url: Jira Cloud/Server URL
        email: User email (Cloud) or username (Server)
        api_token: API token or password
        project_key: Default project for incident tickets
    """

    def manifest(self) -> PluginManifest:
        return PluginManifest(
            name="jira",
            version="1.0.0",
            plugin_type="connector",
            capabilities=["events", "changes"],
            required_secrets=["email", "api_token"],
        )

    def fetch_events(self, since: datetime | None = None) -> list[dict[str, Any]]:
        # TODO: GET /rest/api/3/search?jql=updated>=...
        return []

    def fetch_changes(self, since: datetime | None = None) -> list[dict[str, Any]]:
        # TODO: Query change request issues
        return []

    def health_check(self) -> dict[str, Any]:
        return {"healthy": False, "message": "Not connected (stub)"}
