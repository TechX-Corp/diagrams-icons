# Plugin Architecture

> **Version:** 2.0.0 | **Status:** Draft | **Date:** 2026-02-25

## Overview

The AIOps platform uses a **two-tier plugin architecture**. The core platform never imports vendor SDKs. All external integrations and extensible intelligence logic are implemented as plugins.

## Two-Tier Design

```
┌────────────────────────────────────────────────────────┐
│                    AIOps Core                           │
│  ┌────────────┐  ┌────────────┐  ┌─────────────────┐  │
│  │ Topology   │  │ Correlation│  │ RCA Engine       │  │
│  │ Graph      │←─│ Engine     │←─│ (graph + scoring)│  │
│  └─────┬──────┘  └─────┬──────┘  └────────┬────────┘  │
│        │               │                   │           │
│  ┌─────┴───────────────┴───────────────────┴────────┐  │
│  │              CDM Contracts (canonical)            │  │
│  └──────────┬─────────────────────────┬─────────────┘  │
│             │                         │                │
│  ═══════════╪═════════════════════════╪═══════════════ │
│      Tier 1 │                  Tier 2 │                │
│  ┌──────────┴──────────┐  ┌──────────┴──────────┐     │
│  │  ConnectorPlugin    │  │  ProcessorPlugin     │     │
│  │  (data ingestion)   │  │  (intelligence)      │     │
│  └──────────┬──────────┘  └──────────┬──────────┘     │
│             │                        │                 │
│  ┌──────────┴──────┐      ┌─────────┴──────────┐     │
│  │ Observability   │      │ Blast Radius       │     │
│  │ ├─ Dynatrace    │      │ Noise Reducer      │     │
│  │ ├─ SolarWinds   │      │ Change Scorer      │     │
│  │ ├─ Splunk       │      └────────────────────┘     │
│  │ ├─ OpenSearch   │                                  │
│  │ ├─ InfluxDB     │                                  │
│  │ CI/CD           │                                  │
│  │ ├─ Jenkins      │                                  │
│  │ ├─ GitLab CI    │                                  │
│  │ ├─ GitHub Actions│                                 │
│  │ ├─ ArgoCD       │                                  │
│  │ └─ Azure DevOps │                                  │
│  │ ITSM            │                                  │
│  │ ├─ Jira         │                                  │
│  │ └─ Confluence   │                                  │
│  └─────────────────┘                                  │
└────────────────────────────────────────────────────────┘
```

## Tier 1 — ConnectorPlugin

Connector plugins ingest data from external systems and normalize it into CDM contracts.

### Interface

```python
class ConnectorPlugin(ABC):
    def manifest(self) -> PluginManifest: ...
    def discover_capabilities(self) -> list[str]: ...
    def fetch_entities(self, since=None) -> list[dict]: ...
    def fetch_relations(self, since=None) -> list[dict]: ...
    def fetch_events(self, since=None) -> list[dict]: ...
    def fetch_signals(self, since=None) -> list[dict]: ...
    def fetch_changes(self, since=None) -> list[dict]: ...
    def checkpoint(self) -> dict: ...
    def restore_checkpoint(self, state: dict) -> None: ...
    def health_check(self) -> dict: ...
```

### Capabilities

Each connector declares its capabilities in its manifest:

| Capability | Description |
|-----------|-------------|
| `entities` | Discovers infrastructure/application entities |
| `relations` | Discovers topology relationships |
| `events` | Fetches alerts and events |
| `signals` | Fetches pre-correlated signals |
| `changes` | Fetches deployment/change events |

### Plugin Manifest

```python
PluginManifest(
    name="dynatrace",
    version="1.0.0",
    plugin_type="connector",
    capabilities=["entities", "relations", "events"],
    required_secrets=["api_token"],
    min_platform_version="1.0.0",
)
```

### Connector Directory Structure

Each connector lives in its own directory:

```
services/connectors/
  base.py                    # ConnectorPlugin + ProcessorPlugin ABCs
  registry.py                # Unified PluginRegistry
  dynatrace/
    __init__.py
    connector.py             # DynatraceConnector
  solarwinds/
    __init__.py
    connector.py             # SolarWindsConnector
  splunk/
    connector.py
  opensearch/
    connector.py
  influxdb/
    connector.py
  jira/
    connector.py
  confluence/
    connector.py
  cicd/
    base_plugin.py           # CICDPlugin (extends ConnectorPlugin)
    jenkins_plugin.py
    gitlab_ci_plugin.py
    github_actions_plugin.py
    argocd_plugin.py
    azure_devops_plugin.py
```

## Tier 2 — ProcessorPlugin

Processor plugins operate on CDM data after ingestion. They add intelligence without vendor coupling.

### Interface

```python
class ProcessorPlugin(ABC):
    def manifest(self) -> PluginManifest: ...
    def process(self, message: dict) -> dict | None: ...
    def enrich(self, entity: dict) -> dict: ...
    def score(self, context: dict) -> float: ...
    def health_check(self) -> dict: ...
```

### Built-in Processors

| Processor | Purpose |
|-----------|---------|
| `BlastRadiusProcessor` | Computes impact assessment for incidents |
| `NoiseReducerProcessor` | Filters duplicate and low-severity events |
| `ChangeScorerProcessor` | Scores entities by deployment risk |

## Plugin Registry

The unified `PluginRegistry` manages both tiers:

```python
registry = PluginRegistry()
registry.load_from_config({
    # Tier 1 — Connectors
    "dynatrace": {"enabled": True, "api_token": "${DT_TOKEN}"},
    "jenkins": {"enabled": True, "base_url": "https://jenkins.example.com"},
    # Tier 2 — Processors
    "blast_radius": {"enabled": True},
    "noise_reducer": {"enabled": True, "min_severity": "low"},
})

# Access connectors
for name, connector in registry.get_all_connectors().items():
    entities = connector.fetch_entities()

# Access processors
proc = registry.get_processor("blast_radius")
enriched = proc.process(incident)
```

### Dynamic Loading

Plugins are loaded by class path notation (`module.path:ClassName`). Custom plugins can be registered without modifying core code:

```yaml
plugins:
  my_custom_source:
    enabled: true
    class: "myorg.plugins.custom:MyCustomConnector"
    base_url: "https://..."
```

## Plugin Lifecycle

1. **Registration**: Plugin class loaded and instantiated from config
2. **Manifest validation**: Required secrets checked, version compatibility verified
3. **Health check**: Initial connectivity verified
4. **Operational**: Periodic fetch cycles with checkpoint support
5. **Degraded**: Health check failures trigger circuit breaker
6. **Disabled**: Admin can disable via config without restart

## Security Controls

- **Credential isolation**: Each plugin receives only its declared required_secrets
- **Rate limiting**: Configurable `rate_limit_rpm` per plugin
- **Error isolation**: Plugin exceptions are caught and logged, never crash core
- **Audit trail**: All data fetches logged with plugin attribution

## Adding a Custom Plugin

1. Create `services/connectors/myplugin/connector.py`
2. Extend `ConnectorPlugin`
3. Implement `manifest()`, declared fetch methods, `health_check()`
4. Register via config with `class` path
5. Declare `required_secrets` in manifest for credential injection

## ChangeEvent Contract

CI/CD plugins emit `ChangeEvent` objects (see `contracts/schemas/change_event.schema.json`):

| Field | Type | Description |
|-------|------|-------------|
| change_id | string | Unique identifier |
| source_system | enum | jenkins, gitlab_ci, github_actions, argocd, azure_devops, custom |
| service_canonical_id | string | CDM entity being deployed |
| environment | enum | dev, staging, production, canary |
| version | string | Version being deployed |
| status | enum | started, succeeded, failed, rolled_back |
| affected_entities | array | CDM entity IDs affected |
| metadata | object | Plugin-specific data |

## How Plugins Feed RCA

```
ConnectorPlugins ──fetch──→ CDM Contracts ──→ Correlation Engine ──→ RCA Engine
                                                    ↑                      ↑
ProcessorPlugins ──enrich/score──────────────────────┘                     │
                                                                           │
ChangeScorerProcessor ──score──────────────────────────────────────────────┘
```

1. Connector plugins ingest entities, events, and changes into CDM format
2. Processor plugins enrich events and compute supplementary scores
3. Correlation engine groups events into signals and incidents
4. RCA engine uses graph traversal + change correlation for root cause analysis
