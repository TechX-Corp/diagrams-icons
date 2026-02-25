"""Base plugin interfaces for Tier 1 (Connectors) and Tier 2 (Processors).

The core platform only interacts through these interfaces.
All vendor-specific logic lives in plugin implementations.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any


class PluginManifest:
    """Describes a plugin's identity and capabilities."""

    def __init__(
        self,
        name: str,
        version: str,
        plugin_type: str,
        capabilities: list[str],
        required_secrets: list[str] | None = None,
        min_platform_version: str = "1.0.0",
    ) -> None:
        self.name = name
        self.version = version
        self.plugin_type = plugin_type  # "connector" or "processor"
        self.capabilities = capabilities
        self.required_secrets = required_secrets or []
        self.min_platform_version = min_platform_version

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "plugin_type": self.plugin_type,
            "capabilities": self.capabilities,
            "required_secrets": self.required_secrets,
            "min_platform_version": self.min_platform_version,
        }


class ConnectorPlugin(ABC):
    """Tier 1 — Data ingestion connectors.

    Each connector fetches raw data from an external system and normalizes
    it into CDM contracts. The core platform never imports vendor SDKs.

    Capabilities (declared via manifest):
        entities, relations, events, signals, changes
    """

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self._enabled = config.get("enabled", True)
        self._rate_limit_rpm = config.get("rate_limit_rpm", 60)
        self._checkpoint_state: dict[str, Any] = {}

    @abstractmethod
    def manifest(self) -> PluginManifest:
        """Return plugin identity, version, and declared capabilities."""

    def discover_capabilities(self) -> list[str]:
        """Return the list of capabilities this connector supports."""
        return self.manifest().capabilities

    def fetch_entities(self, since: datetime | None = None) -> list[dict[str, Any]]:
        """Fetch entities from the source. Override if capability declared."""
        return []

    def fetch_relations(self, since: datetime | None = None) -> list[dict[str, Any]]:
        """Fetch relations/topology edges from the source."""
        return []

    def fetch_events(self, since: datetime | None = None) -> list[dict[str, Any]]:
        """Fetch events/alerts from the source."""
        return []

    def fetch_signals(self, since: datetime | None = None) -> list[dict[str, Any]]:
        """Fetch pre-correlated signals (if source supports them)."""
        return []

    def fetch_changes(self, since: datetime | None = None) -> list[dict[str, Any]]:
        """Fetch deployment/change events from the source."""
        return []

    def checkpoint(self) -> dict[str, Any]:
        """Return checkpoint state for resumable fetching."""
        return dict(self._checkpoint_state)

    def restore_checkpoint(self, state: dict[str, Any]) -> None:
        """Restore from a previous checkpoint."""
        self._checkpoint_state = dict(state)

    @abstractmethod
    def health_check(self) -> dict[str, Any]:
        """Check connectivity. Returns {"healthy": bool, "message": str}."""

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def name(self) -> str:
        return self.manifest().name


class ProcessorPlugin(ABC):
    """Tier 2 — Intelligence/processing plugins.

    Processors operate on CDM data that has already been ingested and
    normalized. They add enrichment, scoring, or analysis capabilities
    without any vendor coupling.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config

    @abstractmethod
    def manifest(self) -> PluginManifest:
        """Return plugin identity and capabilities."""

    @abstractmethod
    def process(self, message: dict[str, Any]) -> dict[str, Any] | None:
        """Process an incoming CDM message. Return enriched/modified message or None to drop."""

    def enrich(self, entity: dict[str, Any]) -> dict[str, Any]:
        """Enrich an entity with additional context. Default: passthrough."""
        return entity

    def score(self, context: dict[str, Any]) -> float:
        """Compute a score given a context dict. Default: 0.0."""
        return 0.0

    @abstractmethod
    def health_check(self) -> dict[str, Any]:
        """Check plugin health."""


# Backward compat alias
BaseConnector = ConnectorPlugin
