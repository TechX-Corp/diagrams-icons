"""Root Cause Analysis engine — graph traversal + scoring with explainability.

v1.1: Added change-aware scoring. Deployments that occurred shortly before
symptoms get a significant confidence boost.
"""

import uuid
from datetime import datetime, timezone
from typing import Any

from services.topology.graph_builder import TopologyGraphBuilder


SEVERITY_WEIGHT = {"critical": 1.0, "high": 0.8, "medium": 0.5, "low": 0.3, "info": 0.1}
ALGORITHM_VERSION = "topo-walk-v1.1.0"

# Scoring weights (must sum to 1.0)
W_REACHABILITY = 0.30
W_SEVERITY = 0.25
W_TEMPORAL = 0.20
W_CHANGE = 0.25


class RCAEngine:
    """Performs root cause analysis on incidents using topology graph traversal.

    Algorithm:
    1. For each entity in the graph, compute a "root cause score" based on:
       a) How many affected entities are reachable from this candidate (30%)
       b) Severity of events directly on this candidate (25%)
       c) Temporal proximity — earlier events score higher (20%)
       d) Change correlation — recent deployments to this entity (25%)
    2. Rank candidates by composite score
    3. Return top-N with evidence paths and human-readable explanations
    """

    def __init__(self, max_candidates: int = 3, max_depth: int = 5) -> None:
        self.max_candidates = max_candidates
        self.max_depth = max_depth

    def analyze(
        self,
        incident: dict[str, Any],
        topology: TopologyGraphBuilder,
        events: list[dict[str, Any]] | None = None,
        change_events: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Run RCA on an incident.

        Args:
            incident: CDM Incident dict with affected_entities and signals.
            topology: TopologyGraphBuilder with the current graph.
            events: Optional list of CDM events for temporal scoring.
            change_events: Optional list of CDM ChangeEvents for change-aware scoring.

        Returns:
            RCAResult dict with ranked candidates.
        """
        affected = set(incident.get("affected_entities", []))
        event_map = self._build_event_map(events or [])
        change_map = self._build_change_map(change_events or [])

        # Determine incident time window for change correlation
        incident_start = self._earliest_event_time(events or [])

        candidates: list[dict[str, Any]] = []

        for node_id in topology.graph.nodes:
            reachable = topology.get_all_reachable(node_id, max_depth=self.max_depth)
            reachable_affected = reachable & affected

            if not reachable_affected and node_id not in affected:
                continue

            # (a) Reachability score
            reach_score = len(reachable_affected) / len(affected) if affected else 0.0

            # (b) Severity score
            entity_events = event_map.get(node_id, [])
            sev_score = max(
                (SEVERITY_WEIGHT.get(e.get("severity", "info"), 0.1) for e in entity_events),
                default=0.0,
            )

            # (c) Temporal score
            temporal_score = self._compute_temporal_score(entity_events, event_map, affected)

            # (d) Change correlation score
            change_score = self._compute_change_score(node_id, change_map, incident_start)

            # Composite score
            score = (
                W_REACHABILITY * reach_score
                + W_SEVERITY * sev_score
                + W_TEMPORAL * temporal_score
                + W_CHANGE * change_score
            )

            if score > 0:
                evidence_path = self._build_evidence_path(node_id, affected, topology)
                change_correlated = change_score > 0
                explanation = self._build_explanation(
                    node_id, topology, entity_events, reachable_affected,
                    reach_score, change_map.get(node_id, []),
                )
                candidates.append({
                    "entity_id": node_id,
                    "score": round(score, 4),
                    "evidence_path": evidence_path,
                    "explanation": explanation,
                    "change_correlation": change_correlated,
                })

        candidates.sort(key=lambda c: c["score"], reverse=True)
        top_candidates = candidates[: self.max_candidates]

        return {
            "rca_id": f"rca-{uuid.uuid4().hex[:8]}",
            "incident_id": incident.get("incident_id", ""),
            "candidates": top_candidates,
            "algorithm_version": ALGORITHM_VERSION,
            "computed_at": datetime.now(timezone.utc).isoformat(),
            "confidence": top_candidates[0]["score"] if top_candidates else 0.0,
        }

    @staticmethod
    def _build_event_map(events: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        event_map: dict[str, list[dict[str, Any]]] = {}
        for event in events:
            entity_ref = event.get("entity_ref", "")
            if entity_ref:
                event_map.setdefault(entity_ref, []).append(event)
        return event_map

    @staticmethod
    def _build_change_map(change_events: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        """Index change events by affected entities."""
        change_map: dict[str, list[dict[str, Any]]] = {}
        for ce in change_events:
            # Index by service_canonical_id
            svc = ce.get("service_canonical_id", "")
            if svc:
                change_map.setdefault(svc, []).append(ce)
            # Also index by each affected entity
            for eid in ce.get("affected_entities", []):
                if eid != svc:
                    change_map.setdefault(eid, []).append(ce)
        return change_map

    @staticmethod
    def _earliest_event_time(events: list[dict[str, Any]]) -> str:
        if not events:
            return ""
        return min(e.get("timestamp", "9999") for e in events)

    @staticmethod
    def _compute_change_score(
        entity_id: str,
        change_map: dict[str, list[dict[str, Any]]],
        incident_start: str,
    ) -> float:
        """Score based on whether a change was deployed to/affecting this entity
        shortly before the incident started.
        """
        changes = change_map.get(entity_id, [])
        if not changes or not incident_start:
            return 0.0

        best_score = 0.0
        for change in changes:
            change_end = change.get("timestamp_end") or change.get("timestamp_start", "")
            if not change_end:
                continue

            # Change must have occurred before (or during) the incident
            if change_end <= incident_start:
                # Closer in time = higher score. Perfect if within 30 min.
                best_score = max(best_score, 0.9)
            elif change.get("timestamp_start", "") <= incident_start:
                # Change was in progress when incident started
                best_score = max(best_score, 1.0)

            # Failed or rolled-back deployments are strong signals
            if change.get("status") in ("failed", "rolled_back"):
                best_score = max(best_score, 1.0)

        return best_score

    @staticmethod
    def _compute_temporal_score(
        entity_events: list[dict[str, Any]],
        event_map: dict[str, list[dict[str, Any]]],
        affected: set[str],
    ) -> float:
        if not entity_events:
            return 0.0

        earliest_here = min(e.get("timestamp", "9999") for e in entity_events)
        earlier_count = 0
        total_affected_with_events = 0

        for eid in affected:
            other_events = event_map.get(eid, [])
            if other_events:
                total_affected_with_events += 1
                earliest_other = min(e.get("timestamp", "9999") for e in other_events)
                if earliest_here <= earliest_other:
                    earlier_count += 1

        if total_affected_with_events == 0:
            return 0.5
        return earlier_count / total_affected_with_events

    @staticmethod
    def _build_evidence_path(
        candidate_id: str, affected: set[str], topology: TopologyGraphBuilder
    ) -> list[str]:
        path = [candidate_id]
        for target_id in affected:
            if target_id == candidate_id:
                continue
            found = topology.get_path(candidate_id, target_id)
            if found and len(found) > len(path):
                path = found
        return path

    @staticmethod
    def _build_explanation(
        node_id: str,
        topology: TopologyGraphBuilder,
        entity_events: list[dict[str, Any]],
        reachable_affected: set[str],
        reach_score: float,
        changes: list[dict[str, Any]],
    ) -> str:
        entity = topology.get_entity(node_id)
        name = entity.get("display_name", node_id) if entity else node_id
        entity_type = entity.get("entity_type", "entity") if entity else "entity"

        parts = [f"{name} ({entity_type}) is a root cause candidate."]

        if entity_events:
            top_event = max(entity_events, key=lambda e: SEVERITY_WEIGHT.get(e.get("severity", "info"), 0))
            parts.append(f"It has a {top_event['severity']} event: \"{top_event['title']}\".")

        if reachable_affected:
            parts.append(
                f"It is topologically connected to {len(reachable_affected)} "
                f"affected entities ({reach_score:.0%} reachability)."
            )

        if changes:
            latest = max(changes, key=lambda c: c.get("timestamp_start", ""))
            parts.append(
                f"A deployment (v{latest.get('version', '?')}, status={latest.get('status', '?')}) "
                f"occurred at {latest.get('timestamp_start', '?')}, shortly before symptoms."
            )

        if entity_events:
            earliest = min(e.get("timestamp", "") for e in entity_events)
            parts.append(f"Earliest event at {earliest}, suggesting it may be the origin.")

        return " ".join(parts)
