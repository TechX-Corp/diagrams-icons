# AIOps Platform — Threat Model & Security Architecture

## 1. RBAC Model

### Roles & Permissions

| Resource | Action | admin | operator | viewer | connector-service |
|----------|--------|:-----:|:--------:|:------:|:-----------------:|
| Incidents | list/read | Y | Y | Y | - |
| Incidents | update status | Y | Y | - | - |
| Topology | read/query | Y | Y | Y | - |
| Events | read | Y | Y | Y | - |
| Events | inject | Y | Y | - | Y |
| Connectors | create/update | Y | - | - | - |
| Rules | create/update/delete | Y | - | - | - |
| Config | read/update | Y | - | - | - |
| RBAC | manage | Y | - | - | - |
| Audit Log | read | Y | - | Y | - |
| Health | read | Y | Y | Y | Y |
| Entities | write (upsert) | - | - | - | Y |

## 2. Authentication

| Mode | Use Case | v1 | v2 |
|------|----------|:--:|:--:|
| API Key | Service-to-service, CLI | Y | Y |
| JWT (self-issued) | Internal service tokens (15min TTL) | Y | Y |
| OIDC | User SSO via corporate IdP | - | Y |

- API keys hashed with Argon2id at rest, passed via `Authorization: Bearer` header
- Key rotation: create new → update clients → revoke old

## 3. Audit Logging

### Audited Events
- Authentication: login_success, login_failure, token_issued, key_created, key_revoked
- Authorization: access_denied
- Incidents: created, acknowledged, resolved, suppressed
- Configuration: connector/rule CRUD, config changes
- RBAC: role_assigned, role_revoked
- Integration: ticket_created, notification_sent

### Format
```json
{
  "id": "audit-20260225-001234",
  "timestamp": "2026-02-25T10:15:00.123Z",
  "event": "incident_acknowledged",
  "actor": {"type": "user", "id": "admin-01", "role": "admin", "ip": "10.0.1.50"},
  "resource": {"type": "incident", "id": "inc-20260225-0042"},
  "details": {"previous_status": "open", "new_status": "acknowledged"},
  "outcome": "success"
}
```

- Retention: 90 days (configurable), append-only, exportable to SIEM

## 4. Secrets Management

| Secret | v1 Storage | v2 Storage |
|--------|-----------|-----------|
| Connector API tokens | Environment variables / Docker secrets | HashiCorp Vault |
| API key hashes | JSON file (mounted secret) | Vault / K8s Secret |
| JWT signing key | Environment variable | Vault |
| Database credentials | Environment variable | Vault |

Rules: Never in config/images/logs, `_FILE` suffix convention, .env gitignored, 90-day rotation

## 5. Network Security

| Control | v1 | v2 |
|---------|:--:|:--:|
| TLS for external API calls | Y | Y |
| TLS for inbound API (HTTPS) | Y (reverse proxy) | Y (ingress) |
| Service-to-service mTLS | - (single process) | Y (Istio/Linkerd) |
| Network policies (K8s) | - | Y (deny-all default) |
| API rate limiting | Y (600 req/min/key) | Y |
| Webhook signature verification | Y (HMAC-SHA256) | Y |

## 6. Data Classification

| Data Type | Classification | Controls |
|-----------|---------------|----------|
| Topology data | Internal/Confidential | Auth required, not public |
| Event data | Internal/Confidential | May contain stack traces |
| Credentials | Secret | Encrypted at rest, never logged |
| Audit logs | Internal/Compliance | Append-only, retained per policy |

## 7. Top 5 Threats (STRIDE)

### T1: Credential Theft from Connector Configuration
- **Category**: Information Disclosure | **Impact**: Critical
- **Mitigations**: Docker secrets/Vault, encrypt at rest, 90-day rotation, audit access, least-privilege connectors

### T2: Unauthorized Incident Manipulation
- **Category**: Tampering, Elevation of Privilege | **Impact**: High
- **Mitigations**: RBAC enforcement, immutable audit log, suppression requires admin, anomaly alerting

### T3: Topology Data Exfiltration
- **Category**: Information Disclosure | **Impact**: High
- **Mitigations**: Auth + permissions, rate limiting, network isolation, audit logging, data masking for viewers

### T4: Event Injection via Webhook Spoofing
- **Category**: Spoofing, Tampering | **Impact**: High
- **Mitigations**: HMAC-SHA256 verification, IP allowlist, secret rotation, anomaly detection, connector-service role auth

### T5: Denial of Service via Event Flooding
- **Category**: Denial of Service | **Impact**: High
- **Mitigations**: Per-connector rate limiting, buffer cap with drop policy, circuit breakers, API rate limiting, resource limits

## 8. Security Checklist (v1)

- [ ] All external API calls use TLS with cert verification
- [ ] No secrets in source code, config files, or container images
- [ ] API keys hashed with Argon2id at rest
- [ ] RBAC enforced on every API endpoint
- [ ] Audit logging for all state-changing operations
- [ ] Input validation (Pydantic) on all API inputs
- [ ] Webhook signature verification enabled
- [ ] Rate limiting on all public endpoints
- [ ] Dependency scanning (pip-audit) in CI
- [ ] Container image scanning (Trivy) in CI
- [ ] Non-root container user
