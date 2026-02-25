"""InfluxDB connector — time-series metric events."""

from datetime import datetime
from typing import Any

from services.connectors.base import ConnectorPlugin, PluginManifest


class InfluxDBConnector(ConnectorPlugin):
    """Fetches metric threshold events from InfluxDB.

    Required config:
        url: InfluxDB URL
        token: API token
        org: Organization name
        bucket: Default bucket
    """

    def manifest(self) -> PluginManifest:
        return PluginManifest(
            name="influxdb",
            version="1.0.0",
            plugin_type="connector",
            capabilities=["events"],
            required_secrets=["token"],
        )

    def fetch_events(self, since: datetime | None = None) -> list[dict[str, Any]]:
        # TODO: Flux query against checks/alerts bucket
        return []

    def health_check(self) -> dict[str, Any]:
        return {"healthy": False, "message": "Not connected (stub)"}
