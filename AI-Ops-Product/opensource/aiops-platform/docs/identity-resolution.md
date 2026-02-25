# Identity Resolution Policy

## Overview

Identity resolution ensures that the same real-world entity (host, service, device) seen from multiple source systems maps to a single canonical entity with a stable `canonical_id`.

## Canonical ID Generation

Format: `ent:<entity_type>:<deterministic_hash>`

The hash is computed as: `SHA-256(entity_type + ":" + primary_key)` where `primary_key` is determined by the source priority matrix.

Example: A host with FQDN `prod-web-01.dc1.example.com`:
```
canonical_id = "ent:host:" + sha256("host:prod-web-01.dc1.example.com")[:16]
            = "ent:host:a1b2c3d4e5f67890"
```

## Source Priority Matrix

| Entity Type | Primary Key | Priority 1 (authoritative) | Priority 2 | Priority 3 |
|-------------|------------|---------------------------|-----------|-----------|
| host | FQDN | Dynatrace (hostname) | SolarWinds (sysName) | InfluxDB (host tag) |
| vm | hypervisor_id:vm_name | Dynatrace (HOST entity) | SolarWinds (node) | — |
| container | container_id | Dynatrace (CONTAINER entity) | — | — |
| pod | namespace:pod_name | Dynatrace (K8S_POD) | — | — |
| service | service_name | Dynatrace (SERVICE entity) | — | — |
| application | app_name | Dynatrace (APPLICATION) | — | — |
| network_device | SNMP sysName or mgmt_ip | SolarWinds (node) | — | — |
| network_interface | device_id:ifIndex | SolarWinds (interface) | — | — |
| database | host:port:db_name | Dynatrace (DB entity) | InfluxDB (measurement tag) | — |

## Conflict Resolution Rules

When two sources disagree on entity attributes:

1. **Source priority wins**: Higher-priority source's value is used as the "canonical" value
2. **All values retained**: Lower-priority values stored in `source_refs[].attributes` for reference
3. **Confidence scoring**: Disagreement lowers `confidence_score` proportionally to the number of conflicting attributes
4. **Timestamp tiebreak**: If same priority, most recently observed value wins
5. **Manual override**: Admin can pin any attribute value, which always wins (stored as `source_system: "manual"`)

## Identity Resolution Pipeline

```
  Discover → Match → Merge → Publish
```

1. **Discover**: Connector delivers raw entity with `source_system` + `native_id`
2. **Match**: EntityResolver looks up existing entity by:
   - Exact match on `source_refs[].source_system + native_id`
   - Fuzzy match on primary key (FQDN, IP, service name) with configurable threshold
3. **Merge**: If match found → update attributes per priority rules, append source_ref. If no match → create new entity.
4. **Publish**: Emit entity upsert event for topology graph update

## Merge/Split Policies

### Merge
- **Auto-merge**: When two entities from different sources resolve to the same primary key
- **Manual merge**: Admin links two entities; lower-confidence entity's source_refs absorbed
- **Merge audit**: All merges logged with reason, timestamp, actor

### Split
- **Auto-split**: When an entity's primary key changes (e.g., VM migrated to new host)
- **Manual split**: Admin splits a wrongly merged entity; creates new canonical_id for separated portion

## Soft Delete & Versioning

- Entities not seen for `staleness_window` (default: 24h) transition to `inactive`
- Entities not seen for `decommission_window` (default: 7d) transition to `decommissioned`
- `soft_deleted` state set manually or by provisioning adapter
- Entity history retained for `retention_period` (default: 90d)
- All state transitions logged in audit

## Example Scenarios

### Same host from Dynatrace + SolarWinds
- Dynatrace reports HOST entity with hostname "prod-web-01.dc1.example.com", IP 10.1.2.34
- SolarWinds reports node with sysName "prod-web-01", mgmt IP 10.1.2.34
- Match on FQDN (Dynatrace is priority 1 for hosts)
- Result: Single entity with both source_refs, Dynatrace attributes as canonical, confidence 0.95+

### Same service from Dynatrace + trace discovery
- Dynatrace reports SERVICE entity "checkout-svc" with detected process group
- Trace data shows service "checkout-svc" calling "orders-db"
- Match on service_name → merge into single entity
- Relation "calls" added from trace data
