# KPIs & SLOs

## Platform KPIs

| KPI | Definition | v1 Target | v2 Target | v3 Target |
|-----|-----------|-----------|-----------|-----------|
| Entity Discovery Rate | % of known production entities in topology | ≥80% | ≥95% | ≥99% |
| Event Mapping Rate | % of source events mapped to CDM | ≥90% | ≥95% | ≥98% |
| Alert-to-Incident Ratio | Compression factor (raw alerts / incidents) | ≥5:1 | ≥10:1 | ≥20:1 |
| Mean Time to Detect (MTTd) | Time from first event to incident creation | ≤5 min | ≤2 min | ≤1 min |
| Mean Time to Root Cause (MTTrc) | Time from incident to RCA result | ≤30s | ≤15s | ≤10s |
| RCA Precision | % of correct root cause in top-3 candidates | ≥60% | ≥75% | ≥85% |
| False Positive Rate | % of incidents auto-closed as noise | ≤20% | ≤10% | ≤5% |

## Operational SLOs

| SLO | Target | Measurement |
|-----|--------|-------------|
| Event ingestion availability | 99.9% | % of minutes with successful event processing |
| P95 event processing latency | ≤2s | From connector receipt to Event Hub write |
| P95 RCA computation latency | ≤30s | From incident creation to RCA result |
| P95 API response time | ≤500ms | All API endpoints |
| Topology freshness | ≤5 min | Max age of entity/relation data |
| Event lag | ≤60s | Time between source event and CDM event |
| RPO (Recovery Point Objective) | ≤1 hr | Max data loss in disaster |
| RTO (Recovery Time Objective) | ≤15 min | Max downtime in disaster |

## Self-Observability

### Structured Logging
- JSON format with: timestamp, level, service, event, trace_id, duration_ms
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Correlation IDs propagated across services

### Prometheus Metrics
| Metric | Type | Labels |
|--------|------|--------|
| aiops_events_ingested_total | counter | source, event_type |
| aiops_events_deduplicated_total | counter | source |
| aiops_connector_poll_duration_seconds | histogram | connector, source |
| aiops_signals_active | gauge | severity |
| aiops_incidents_active | gauge | severity |
| aiops_rca_duration_seconds | histogram | model_version |
| aiops_topology_entities_total | gauge | entity_type |
| aiops_api_request_duration_seconds | histogram | method, path, status |

### Health Endpoints
- `GET /health` — liveness (200 if alive)
- `GET /health/ready` — readiness (200 if DB connected, connectors healthy)

### Distributed Tracing (v2)
- OpenTelemetry SDK, W3C Trace Context propagation
- Key spans: connector poll, normalization, correlation, RCA, integration action
