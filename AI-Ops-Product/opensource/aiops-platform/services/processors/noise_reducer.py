"""Noise Reducer Processor — filters and deduplicates low-value events."""

from typing import Any

from services.connectors.base import ProcessorPlugin, PluginManifest


class NoiseReducerProcessor(ProcessorPlugin):
    """Reduces alert noise by suppressing duplicate and low-severity events.

    Configuration:
        min_severity: minimum severity to pass through (default: "low")
        dedup_window_seconds: time window for dedup (default: 300)
    """

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)
        self._min_severity = config.get("min_severity", "low")
        self._severity_rank = {"critical": 1, "high": 2, "medium": 3, "low": 4, "info": 5}
        self._seen_fingerprints: set[str] = set()

    def manifest(self) -> PluginManifest:
        return PluginManifest(
            name="noise_reducer",
            version="1.0.0",
            plugin_type="processor",
            capabilities=["process"],
        )

    def process(self, message: dict[str, Any]) -> dict[str, Any] | None:
        """Return None to drop noisy events, or pass through significant ones."""
        severity = message.get("severity", "info")
        min_rank = self._severity_rank.get(self._min_severity, 4)

        if self._severity_rank.get(severity, 5) > min_rank:
            return None  # Drop below threshold

        fingerprint = message.get("fingerprint", "")
        if fingerprint and fingerprint in self._seen_fingerprints:
            return None  # Drop duplicate
        if fingerprint:
            self._seen_fingerprints.add(fingerprint)

        return message

    def score(self, context: dict[str, Any]) -> float:
        """Return noise reduction ratio."""
        total = context.get("total_events", 1)
        suppressed = context.get("suppressed_events", 0)
        return suppressed / total if total > 0 else 0.0

    def health_check(self) -> dict[str, Any]:
        return {"healthy": True, "message": f"Tracking {len(self._seen_fingerprints)} fingerprints"}
