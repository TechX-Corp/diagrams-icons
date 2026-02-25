# Operational Readiness

## 1. Team Ownership Model

| Service | Owning Team | On-Call | Escalation |
|---|---|---|---|
| Connector framework | Team Ingestion | 24x7 primary+secondary | Platform Lead |
| Normalization & entity resolution | Team Ingestion | Shared with connector | Platform Lead |
| Topology graph | Team Core | 24x7 primary+secondary | Platform Lead |
| Event hub | Team Core | 24x7 primary+secondary | Platform Lead → Infra |
| Correlation engine | Team Analytics | Business hours; Core after-hours | Analytics Lead |
| RCA engine | Team Analytics | Same as correlation | Analytics Lead |
| ITSM integration | Team Integration | Business hours; Core after-hours | Platform Lead |
| API gateway & UI | Team Platform | 24x7 primary+secondary | Platform Lead |
| Infrastructure | Team Infra | 24x7 primary+secondary | Infra Lead → VP Eng |

## 2. On-Call Readiness Checklist

- [ ] Runbook exists for every alert that pages on-call
- [ ] On-call has production access (read + restart)
- [ ] VPN/bastion access verified
- [ ] Monitoring dashboards accessible (Grafana)
- [ ] PagerDuty account configured
- [ ] Completed shadow shift (≥1 week)
- [ ] Passed incident simulation (game day)
- [ ] Knows: rolling restart, connector disable/enable, log level change

### Escalation Path
```
L1: On-call (15 min) → L2: Secondary/team lead (30 min) → L3: Platform Lead (1 hr) → L4: Vendor support
```

## 3. Incident Response (Platform Itself)

| Severity | Definition | Response | Update Cadence |
|---|---|---|---|
| SEV-1 | Platform down / data loss | 15 min | Every 30 min |
| SEV-2 | Degraded processing | 30 min | Every 1 hr |
| SEV-3 | Non-critical failure | 4 hr | Next business day |
| SEV-4 | Minor / improvement | Next sprint | N/A |

**Lifecycle**: Detection → Triage → Mitigation → Resolution → Post-Incident Review (within 5 days for SEV-1/2)

## 4. Capacity Planning

| Milestone | Event Rate | Entity Count | Graph Memory |
|---|---|---|---|
| v1.0 | 500 events/s | 10,000 | 8 GB |
| v2.0 | 2,000 events/s | 50,000 | 32 GB |
| v3.0 | 5,000 events/s | 200,000 | 64 GB |

**Review cadence**: Monthly growth trends, quarterly load tests at 2x peak, pre-milestone validation.

## 5. Disaster Recovery

| Scenario | RPO | RTO | Procedure |
|---|---|---|---|
| Single pod failure | 0 | <1 min | K8s auto-restart |
| Node failure | 0 | <5 min | K8s reschedules |
| AZ failure | ≤5 min | ≤15 min | Traffic shift, replica promote |
| Region failure | ≤1 hr | ≤4 hr | Restore from S3, DNS failover |

**DR drills**: Quarterly single-store restore, semi-annual full failover simulation.

## 6. Change Management

| Category | Approval | Lead Time |
|---|---|---|
| Standard (config toggle, dep bump) | Auto-approved | ≥1 hr |
| Normal (feature, migration, new connector) | Peer review + team lead | ≥1 business day |
| Emergency (hotfix for SEV-1/2) | On-call lead + post-approval | Immediate |

**Deploy**: Code review → CI green → Staging → Canary 10% (15 min) → Full rollout. Rollback if error rate >1%.

## 7. Go-Live Criteria

### v1.0
- [ ] All acceptance criteria met in staging
- [ ] Load test: 500 events/s, 1hr, no data loss
- [ ] No open SEV-1/2 bugs
- [ ] Runbooks written for all alerts
- [ ] On-call staffed (≥2 trained engineers)
- [ ] Monitoring dashboards deployed
- [ ] Rollback procedure tested
- [ ] Stakeholder sign-off
