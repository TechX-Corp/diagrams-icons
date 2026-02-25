"""Runnable RCA demo — loads example data, builds graph, runs change-aware analysis.

Usage: python -m services.rca.demo (from the aiops-platform directory)
"""

import json
from pathlib import Path

from services.topology.graph_builder import TopologyGraphBuilder
from services.correlation.engine import CorrelationEngine
from services.rca.engine import RCAEngine


def load_json(filename: str) -> list | dict:
    path = Path(__file__).resolve().parent.parent.parent / "contracts" / "examples" / filename
    with open(path) as f:
        return json.load(f)


def main() -> None:
    print("=" * 70)
    print("  AIOps Platform — Change-Aware Root Cause Analysis Demo")
    print("=" * 70)

    # 1. Load example data
    print("\n[1/6] Loading example data...")
    entities = load_json("entities.json")
    relations = load_json("relations.json")
    events = load_json("events.json")
    change_events = load_json("change_events.json")
    print(f"  Loaded {len(entities)} entities, {len(relations)} relations, "
          f"{len(events)} events, {len(change_events)} change events")

    # 2. Build topology graph
    print("\n[2/6] Building topology graph...")
    topology = TopologyGraphBuilder()
    topology.build_from_json(entities, relations)
    print(f"  Graph: {topology.entity_count} nodes, {topology.relation_count} edges")

    # 3. Show change events
    print("\n[3/6] Recent deployments (ChangeEvents):")
    for ce in change_events:
        print(f"  [{ce['source_system']}] {ce['pipeline']} -> {ce['service_canonical_id']}")
        print(f"    version={ce['version']}, status={ce['status']}, "
              f"time={ce['timestamp_start']} .. {ce['timestamp_end']}")

    # 4. Create signals from events
    print("\n[4/6] Correlating events into signals...")
    correlation = CorrelationEngine(time_window_seconds=600)
    for event in events:
        signal = correlation.ingest_event(event)
        print(f"  Event '{event['title'][:50]}...' -> Signal {signal['signal_id']} "
              f"(count={signal['count']}, fingerprint={signal['fingerprint'][:20]})")

    # Also ingest change events into correlation
    correlation.ingest_change_events(change_events)
    print(f"  Total signals: {len(correlation.signals)}")

    # 5. Create incident from signals
    print("\n[5/6] Grouping signals into incident...")
    incident = correlation.correlate_signals()
    print(f"  Incident: {incident['incident_id']}")
    print(f"  Title: {incident['title']}")
    print(f"  Severity: {incident['severity']}")
    print(f"  Affected entities: {len(incident['affected_entities'])}")
    for eid in incident["affected_entities"]:
        entity = topology.get_entity(eid)
        name = entity.get("display_name", eid) if entity else eid
        print(f"    - {name}")

    # 6. Run change-aware RCA
    print("\n[6/6] Running Change-Aware Root Cause Analysis...")
    rca = RCAEngine(max_candidates=3, max_depth=5)
    result = rca.analyze(incident, topology, events, change_events=change_events)

    print(f"\n{'=' * 70}")
    print(f"  RCA Result: {result['rca_id']}")
    print(f"  Algorithm: {result['algorithm_version']}")
    print(f"  Confidence: {result['confidence']:.2%}")
    print(f"{'=' * 70}")

    for i, candidate in enumerate(result["candidates"], 1):
        entity = topology.get_entity(candidate["entity_id"])
        name = entity.get("display_name", candidate["entity_id"]) if entity else candidate["entity_id"]
        change_flag = " [CHANGE CORRELATED]" if candidate.get("change_correlation") else ""
        print(f"\n  #{i} — {name}{change_flag}")
        print(f"  Score: {candidate['score']:.4f}")
        print(f"  Evidence path: {' -> '.join(candidate['evidence_path'])}")
        print(f"  Explanation: {candidate['explanation']}")

    print(f"\n{'=' * 70}")
    print("  Demo complete. See docs/ for full architecture documentation.")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
