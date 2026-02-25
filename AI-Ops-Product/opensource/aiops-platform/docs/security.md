# Security Architecture

> **Version:** 1.0.0 | **Status:** Draft | **Date:** 2026-02-25

## Overview

This document defines the security controls, access model, and data protection strategy for the AIOps platform. See also [threat-model.md](threat-model.md) for STRIDE analysis.

## Authentication

### API Authentication Modes

| Mode | Use Case | Implementation |
|------|----------|----------------|
| API Key | Service-to-service, connectors | `X-API-Key` header, SHA-256 hashed at rest |
| JWT Bearer | Human users, UI sessions | RS256 signed, 1h expiry, refresh rotation |
| OIDC/SAML | Enterprise SSO integration | Delegated to IdP (v2+) |

### Plugin Credential Isolation

Each connector plugin receives **only its own credentials** via config. The registry enforces:
- Credentials are injected at plugin instantiation from a secrets backend
- Plugins cannot access other plugins' config objects
- No shared credential store between plugins
- Audit log entry on every credential access

## Authorization (RBAC)

### Roles

| Role | Description |
|------|-------------|
| `admin` | Full platform management, plugin enable/disable, user management |
| `operator` | Incident management, RCA execution, runbook access |
| `viewer` | Read-only dashboard, topology view, incident history |
| `connector_service` | API access for connector plugins (machine identity) |

### Permission Matrix

| Resource | admin | operator | viewer | connector_service |
|----------|-------|----------|--------|-------------------|
| Topology (read) | Y | Y | Y | Y |
| Topology (write) | Y | N | N | Y |
| Incidents (read) | Y | Y | Y | N |
| Incidents (manage) | Y | Y | N | N |
| RCA (execute) | Y | Y | N | N |
| Plugins (manage) | Y | N | N | N |
| Users (manage) | Y | N | N | N |
| Audit logs (read) | Y | N | N | N |

## Data Protection

### Data Classification

| Classification | Examples | Controls |
|---------------|----------|----------|
| **Confidential** | API tokens, credentials, PII | Encrypted at rest (AES-256), masked in logs |
| **Internal** | Topology data, events, incidents | Access-controlled, audit logged |
| **Public** | API docs, schema definitions | No restrictions |

### Encryption

- **At rest**: AES-256-GCM for secrets, database-level encryption for state store
- **In transit**: TLS 1.2+ for all API communication, mTLS for internal service mesh (v2+)
- **Secrets management**: Environment variables (v1) → Docker Secrets (v1.1) → HashiCorp Vault (v2)

## Audit Logging

All security-relevant events are logged in structured JSON:

```json
{
  "timestamp": "2026-02-25T12:00:00Z",
  "event_type": "auth.login_success",
  "actor": "user:admin@example.com",
  "resource": "/api/v1/incidents",
  "action": "read",
  "source_ip": "10.1.1.50",
  "user_agent": "AIOps-UI/1.0"
}
```

### Audited Events

- Authentication success/failure
- Authorization denials
- Plugin enable/disable
- Credential access
- Incident state changes
- RCA executions
- Configuration changes
- Data exports

### Retention

| Log Type | Retention | Storage |
|----------|-----------|---------|
| Audit logs | 2 years | Immutable append-only |
| Security events | 1 year | Indexed, searchable |
| Access logs | 90 days | Rotated |

## Multi-Tenancy Readiness

### Isolation Model (v2+)

- **Tenant ID**: Every CDM object carries a `tenant_id` field
- **Data isolation**: Row-level security in PostgreSQL, namespace isolation in graph
- **API isolation**: Tenant context extracted from JWT claims
- **Plugin isolation**: Each tenant can have independent plugin configurations
- **Network isolation**: Per-tenant network policies in Kubernetes

### v1 (Single-Tenant)

v1 operates as a single-tenant system. Multi-tenancy hooks are present in the data model but not enforced at the API layer.

## Plugin Security

### Plugin Sandbox

Plugins execute within the platform process (v1) but are subject to:
- **No filesystem access** beyond their config directory
- **No network access** except to their declared endpoint
- **Rate limiting** per plugin (configurable RPM)
- **Error isolation** — plugin failures don't crash the core

### Plugin Manifest Verification

Each plugin declares in its manifest:
- Required secrets (validated at load time)
- Minimum platform version (compatibility check)
- Declared capabilities (enforced at runtime)

## Network Security

```
┌─────────────────────────────────────────────┐
│                DMZ / Edge                     │
│  ┌─────────┐                                │
│  │ API GW  │ ← TLS termination, rate limit  │
│  └────┬────┘                                │
│       │                                      │
│ ──────┼─── Trust Boundary ──────────────────│
│       │                                      │
│  ┌────┴────────────────────────┐            │
│  │      AIOps Platform Core    │            │
│  │  (RBAC enforced at handler) │            │
│  └────┬────────────────────────┘            │
│       │                                      │
│ ──────┼─── Plugin Boundary ─────────────────│
│       │                                      │
│  ┌────┴─────────────────────┐               │
│  │  Connector Plugins       │ → External    │
│  │  (isolated credentials)  │   Systems     │
│  └──────────────────────────┘               │
└─────────────────────────────────────────────┘
```

## Compliance Considerations

- **GDPR**: PII minimization in topology data; data subject access/deletion via API
- **SOC 2**: Audit logging, access controls, encryption meet Type II requirements
- **ISO 27001**: Security controls mapped to Annex A controls

## Security Checklist for v1

- [x] API key authentication for all endpoints
- [x] RBAC with 4 roles
- [x] Audit logging for security events
- [x] Plugin credential isolation
- [x] TLS for API communication
- [x] Rate limiting per plugin
- [ ] JWT authentication (v1.1)
- [ ] OIDC/SAML integration (v2)
- [ ] mTLS for internal communication (v2)
- [ ] Multi-tenant data isolation (v2)
- [ ] Vault integration for secrets (v2)
