# AIOps Platform Roadmap

## v1.0 — Foundation (Month 1–3)

| Capability | Target | Acceptance Criteria |
|---|---|---|
| Topology discovery | Dynatrace + SolarWinds | ≥80% of production entities in graph |
| Event mapping | Splunk alerts → CDM events | ≥90% of alerts mapped to CDM schema |
| Correlation | Fingerprint dedup + time-window grouping | Duplicates collapsed, related events grouped within 5min window |
| RCA | Graph-traversal scoring | ≥60% precision on ≥30 known historical incidents |
| ITSM integration | Jira ticket creation | P1/P2 auto-create tickets within 60s |
| Latency | End-to-end | Event→incident ≤5min (P95), RCA ≤30s (P95) |
| Deployment | Local dev | docker-compose, one-command startup |

**Exit criteria**: Load test 500 events/s for 1hr, no data loss. Runbooks written.

## v2.0 — Intelligence (Month 4–8)

| Capability | Target | Acceptance Criteria |
|---|---|---|
| Topology expansion | +InfluxDB +OpenSearch | ≥95% entity coverage |
| ML correlation | Anomaly grouping | ≥80% grouping accuracy on held-out data |
| RCA | Causal inference | ≥75% precision, automated weekly retraining |
| Noise reduction | Dedup + correlation | ≥70% alert volume reduction (7-day window) |
| KB integration | Confluence runbooks | ≥50% of incident types get auto-suggested runbook |
| Self-observability | Platform monitoring | Structured logging, Prometheus, OTel tracing |
| Deployment | Kubernetes | Helm chart, HA (≥2 replicas), HPA, zero-downtime |

**Exit criteria**: Chaos test (pod failure, no data loss). 2,000 events/s for 1hr.

## v3.0 — Autonomy (Month 9–14)

| Capability | Target | Acceptance Criteria |
|---|---|---|
| Predictive | Trend detection | ≥50% slow-burn incidents detected ≥15min early |
| Auto-remediation | Approved runbook execution | Gated by approval policy, full audit log |
| Feedback loop | Operator action ingestion | ≥5pp precision improvement per quarter |
| Noise reduction | Advanced compression | ≥85% alert compression |
| RCA precision | Explainable RCA | ≥85% precision with explainability scores |
| Multi-tenancy | Tenant isolation | Data isolation, tenant-scoped RBAC, rate limiting |
| Compliance | SOC 2 readiness | Audit logging, encryption, access reviews |

**Exit criteria**: 5,000 events/s, 10 tenants. Pen-test clean. SOC 2 Type I evidence.

```
Month  1  2  3  4  5  6  7  8  9 10 11 12 13 14
       ├──v1.0──┤  ├─────v2.0──────┤  ├─────v3.0───────┤
```
