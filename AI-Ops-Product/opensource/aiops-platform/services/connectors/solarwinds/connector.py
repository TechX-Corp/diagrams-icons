"""SolarWinds connector — LLDP/CDP network topology discovery."""

from datetime import datetime
from typing import Any

from services.connectors.base import ConnectorPlugin, PluginManifest


class SolarWindsConnector(ConnectorPlugin):
    """Fetches network topology from SolarWinds via SWIS REST API.

    Required config:
        base_url: SolarWinds Orion server URL
        username, password: credentials
    """

    def manifest(self) -> PluginManifest:
        return PluginManifest(
            name="solarwinds",
            version="1.0.0",
            plugin_type="connector",
            capabilities=["entities", "relations", "events"],
            required_secrets=["username", "password"],
        )

    def fetch_entities(self, since: datetime | None = None) -> list[dict[str, Any]]:
        # TODO: SWIS query for Orion.Nodes + Orion.NPM.Interfaces
        return []

    def fetch_relations(self, since: datetime | None = None) -> list[dict[str, Any]]:
        # TODO: SWIS query for LLDP/CDP entries
        return []

    def fetch_events(self, since: datetime | None = None) -> list[dict[str, Any]]:
        # TODO: SWIS query for Orion.AlertActive
        return []

    def health_check(self) -> dict[str, Any]:
        return {"healthy": False, "message": "Not connected (stub)"}
