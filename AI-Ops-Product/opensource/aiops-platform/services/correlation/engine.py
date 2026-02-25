"""Correlation engine — groups events into signals and signals into incidents."""

import hashlib
import uuid
from datetime import datetime, timezone
from typing import Any


class CorrelationEngine:
    """Basic correlation engine using fingerprint-based deduplication
    and time-window grouping.

    Events with the same fingerprint (entity_ref + event category) are
    collapsed into Signals. Signals within a time window affecting
    related entities are grouped into Incidents.
    """

    def __init__(self, time_window_seconds: int = 300) -> None:
        self.time_window_seconds = time_window_seconds
        self.signals: dict[str, dict[str, Any]] = {}
        self.incidents: list[dict[str, Any]] = []

    def compute_fingerprint(self, event: dict[str, Any]) -> str:
        """Compute a deduplication fingerprint for an event.

        Based on entity_ref + severity + event_type + title keywords.
        """
        raw = ":".join([
            event.get("entity_ref", ""),
            event.get("event_type", ""),
            event.get("title", "").lower().split()[0] if event.get("title") else "",
        ])
        return "fp:" + hashlib.sha256(raw.encode()).hexdigest()[:12]

    def ingest_event(self, event: dict[str, Any]) -> dict[str, Any]:
        """Ingest an event and return the corresponding signal (created or updated)."""
        fingerprint = self.compute_fingerprint(event)

        if fingerprint in self.signals:
            signal = self.signals[fingerprint]
            signal["source_events"].append(event["event_id"])
            signal["count"] += 1
            signal["last_occurrence"] = event["timestamp"]
            if self._severity_rank(event["severity"]) < self._severity_rank(signal["severity"]):
                signal["severity"] = event["severity"]
        else:
            signal = self.create_signal(event, fingerprint)
            self.signals[fingerprint] = signal

        return signal

    def create_signal(self, event: dict[str, Any], fingerprint: str) -> dict[str, Any]:
        """Create a new signal from an event."""
        category = self._infer_category(event)
        return {
            "signal_id": f"sig-{uuid.uuid4().hex[:6]}",
            "source_events": [event["event_id"]],
            "entity_refs": [event["entity_ref"]] if event.get("entity_ref") else [],
            "severity": event["severity"],
            "category": category,
            "fingerprint": fingerprint,
            "first_occurrence": event["timestamp"],
            "last_occurrence": event["timestamp"],
            "count": 1,
            "enrichments": {},
        }

    def ingest_change_events(self, change_events: list[dict[str, Any]]) -> None:
        """Ingest CI/CD change events as deployment signals for correlation."""
        for ce in change_events:
            event = {
                "event_id": ce["change_id"],
                "entity_ref": ce.get("service_canonical_id", ""),
                "severity": "high" if ce.get("status") == "failed" else "info",
                "event_type": "state_change",
                "title": f"Deployment {ce.get('version', '')} ({ce.get('status', '')})",
                "timestamp": ce.get("timestamp_start", ""),
            }
            self.ingest_event(event)

    def correlate_signals(self) -> dict[str, Any]:
        """Group all current signals into an incident based on time-window proximity."""
        if not self.signals:
            return self._empty_incident()

        all_signals = list(self.signals.values())
        affected = set()
        signal_ids = []
        max_severity = "info"

        for sig in all_signals:
            signal_ids.append(sig["signal_id"])
            affected.update(sig["entity_refs"])
            if self._severity_rank(sig["severity"]) < self._severity_rank(max_severity):
                max_severity = sig["severity"]

        incident = {
            "incident_id": f"inc-{uuid.uuid4().hex[:8]}",
            "title": self._generate_title(all_signals),
            "severity": max_severity,
            "status": "open",
            "signals": signal_ids,
            "affected_entities": list(affected),
            "root_cause_candidates": [],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "owner": None,
            "external_refs": [],
        }
        self.incidents.append(incident)
        return incident

    @staticmethod
    def _severity_rank(severity: str) -> int:
        return {"critical": 1, "high": 2, "medium": 3, "low": 4, "info": 5}.get(severity, 5)

    @staticmethod
    def _infer_category(event: dict[str, Any]) -> str:
        title = event.get("title", "").lower()
        if any(w in title for w in ["cpu", "memory", "disk", "capacity"]):
            return "resource"
        if any(w in title for w in ["connection", "pool", "timeout"]):
            return "connectivity"
        if any(w in title for w in ["latency", "response", "slow"]):
            return "performance"
        if any(w in title for w in ["packet", "network", "interface"]):
            return "network"
        return "general"

    @staticmethod
    def _generate_title(signals: list[dict[str, Any]]) -> str:
        categories = list({s["category"] for s in signals})
        entity_count = len({e for s in signals for e in s["entity_refs"]})
        return f"Correlated incident: {', '.join(categories)} issues across {entity_count} entities"

    def _empty_incident(self) -> dict[str, Any]:
        return {"incident_id": "", "title": "No signals", "severity": "info",
                "status": "closed", "signals": [], "affected_entities": [],
                "root_cause_candidates": [], "created_at": "", "updated_at": "",
                "owner": None, "external_refs": []}
