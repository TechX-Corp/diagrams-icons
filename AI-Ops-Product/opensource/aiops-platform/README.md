# AIOps Platform

Enterprise-grade AIOps platform for hybrid infrastructure. Ingests observability data from multiple sources via a two-tier plugin architecture, builds a unified topology graph, correlates events into incidents, and performs change-aware explainable root cause analysis.

## Quick Start

```bash
make setup    # Create venv and install dependencies
make demo     # Run the change-aware RCA demo
make test     # Run tests
```

## Architecture

```
Source Systems → Tier 1 Connectors → Normalization → Topology Graph
                                                    → Event Hub → Correlation → RCA
                                   Tier 2 Processors → Enrichment → Scoring ──↗
```

### Core Principle

**The core platform never imports vendor SDKs.** All external systems are implemented as plugins.

### Two-Tier Plugin Architecture

- **Tier 1 — ConnectorPlugin** (data ingestion): Dynatrace, SolarWinds, Splunk, InfluxDB, OpenSearch, Jira, Confluence, Jenkins, GitLab CI, GitHub Actions, ArgoCD, Azure DevOps
- **Tier 2 — ProcessorPlugin** (intelligence): Blast Radius, Noise Reducer, Change Scorer
- **Normalization**: Transforms raw data into a Canonical Data Model (CDM) with identity resolution
- **Topology Graph**: In-memory MultiDiGraph (NetworkX) of entities and relationships
- **Correlation Engine**: Fingerprint-based dedup + time-window grouping + change-aware correlation
- **RCA Engine**: Graph traversal + 4-factor scoring (reachability, severity, temporal, change correlation)

See [docs/architecture.md](docs/architecture.md) for the full architecture.

## Project Structure

```
aiops-platform/
├── contracts/
│   ├── schemas/              # JSON Schema definitions for CDM types
│   └── examples/             # Realistic example payloads
├── services/
│   ├── connectors/           # Tier 1 — Data source connectors
│   │   ├── base.py           # ConnectorPlugin + ProcessorPlugin ABCs
│   │   ├── registry.py       # Unified PluginRegistry
│   │   ├── dynatrace/        # Smartscape topology + APM events
│   │   ├── solarwinds/       # LLDP/CDP network topology
│   │   ├── splunk/           # Log events and alerts
│   │   ├── opensearch/       # Event search
│   │   ├── influxdb/         # Metric threshold events
│   │   ├── jira/             # Incident ticket sync
│   │   ├── confluence/       # Runbook search
│   │   └── cicd/             # CI/CD plugins
│   │       ├── jenkins_plugin.py
│   │       ├── gitlab_ci_plugin.py
│   │       ├── github_actions_plugin.py
│   │       ├── argocd_plugin.py
│   │       └── azure_devops_plugin.py
│   ├── processors/           # Tier 2 — Intelligence plugins
│   │   ├── blast_radius.py
│   │   ├── noise_reducer.py
│   │   └── change_scorer.py
│   ├── normalization/        # Entity resolution and CDM transformation
│   ├── topology/             # Graph builder and query service
│   ├── correlation/          # Event → Signal → Incident correlation
│   └── rca/                  # Root cause analysis engine + demo
├── tests/                    # Unit tests
├── infra/                    # Docker Compose, Dockerfile
├── docs/                     # Architecture, CDM, governance, roadmap
├── Makefile                  # Build targets
└── pyproject.toml            # Project config
```

## Running the RCA Demo

The demo loads example data representing a real scenario: *web application latency caused by database connection pool exhaustion following a deployment*.

```bash
make demo
```

Output shows:
1. 8 entities loaded (app, service, pod, host, database, VM, switch, LB)
2. Topology graph built (10 edges)
3. Recent deployments displayed (Jenkins + ArgoCD change events)
4. 6 events + 2 change events correlated into signals
5. Incident created from correlated signals
6. **Change-aware RCA**: Top 3 candidates with scores, evidence paths, change correlation flags

## Adding a New Plugin

### Tier 1 — Connector

1. Create `services/connectors/myvendor/connector.py`
2. Extend `ConnectorPlugin` from `services/connectors/base.py`
3. Implement `manifest()` declaring capabilities and required secrets
4. Implement the relevant fetch methods (`fetch_entities()`, `fetch_events()`, etc.)
5. Implement `health_check()`
6. Register via config: `{"myvendor": {"enabled": true, "class": "services.connectors.myvendor.connector:MyConnector"}}`

### Tier 2 — Processor

1. Create `services/processors/myprocessor.py`
2. Extend `ProcessorPlugin`
3. Implement `manifest()`, `process()`, and optionally `enrich()` / `score()`

## Documentation

| Document | Description |
|----------|-------------|
| [plugin-architecture.md](docs/plugin-architecture.md) | Two-tier plugin framework design |
| [architecture.md](docs/architecture.md) | Detailed system architecture |
| [canonical-model.md](docs/canonical-model.md) | Canonical Data Model v1 |
| [identity-resolution.md](docs/identity-resolution.md) | Entity identity resolution policy |
| [security.md](docs/security.md) | Security architecture, RBAC, data protection |
| [threat-model.md](docs/threat-model.md) | STRIDE analysis and mitigations |
| [governance.md](docs/governance.md) | RFC process, schema evolution, release train |
| [roadmap.md](docs/roadmap.md) | v1/v2/v3 milestones with acceptance criteria |
| [kpis-slos.md](docs/kpis-slos.md) | Platform KPIs and operational SLOs |
| [operational-readiness.md](docs/operational-readiness.md) | On-call, DR, change management |

## Technology Stack

- **Python 3.11+** with FastAPI, Pydantic, NetworkX
- **In-memory MultiDiGraph** (upgradeable to Neo4j)
- **SQLite/PostgreSQL** for state persistence
- **Docker Compose** for local development
- **uv** for Python package management
