"""CI/CD plugin base — extends ConnectorPlugin for CI/CD systems.

All CI/CD plugins implement ConnectorPlugin with the 'changes' capability.
The normalize_change() method provides source-specific transformation.
"""

from abc import abstractmethod
from datetime import datetime
from typing import Any

from services.connectors.base import ConnectorPlugin, PluginManifest


class CICDPlugin(ConnectorPlugin):
    """Base for CI/CD connector plugins.

    Subclasses must implement:
        - manifest()
        - source_system (property)
        - _fetch_raw_changes(since) -> list of raw events
        - normalize_change(raw_event) -> CDM ChangeEvent dict
        - health_check()
    """

    @property
    @abstractmethod
    def source_system(self) -> str:
        """Return the source_system identifier (e.g. 'jenkins', 'gitlab_ci')."""

    def fetch_changes(self, since: datetime | None = None) -> list[dict[str, Any]]:
        """Fetch and normalize change events."""
        raw = self._fetch_raw_changes(since or datetime.min)
        return [self.normalize_change(e) for e in raw]

    def _fetch_raw_changes(self, since: datetime) -> list[dict[str, Any]]:
        """Fetch raw change data from the CI/CD system. Override in subclass."""
        return []

    @abstractmethod
    def normalize_change(self, raw_event: dict[str, Any]) -> dict[str, Any]:
        """Transform a raw CI/CD event into a CDM ChangeEvent."""

    # Convenience alias for backward compat
    def fetch_and_normalize(self, since: datetime) -> list[dict[str, Any]]:
        return self.fetch_changes(since)
