# Platform Governance Framework

## 1. RFC Process

### When Required
- Any change to the Canonical Data Model (new types, field changes, enum additions)
- New service boundary or service split
- New connector that introduces a new entity type
- Changes to identity resolution rules
- Security model changes
- Breaking API changes

### Workflow
1. **Author** creates RFC using [rfc-template.md](rfc-template.md)
2. **Review period**: 5 business days minimum
3. **CDM Review Board** reviews and votes (majority approval required)
4. **Implementation** tracked in Jira with RFC reference
5. **Retrospective** after rollout

## 2. CDM Review Board

- **Charter**: Ensure CDM consistency, backward compatibility, and cross-team alignment
- **Membership**: Platform architect (chair), 1 rep per team (Ingestion, Core, Analytics, Integration), Security lead
- **Cadence**: Bi-weekly review meeting; async review for urgent RFCs
- **Quorum**: Chair + 3 members
- **Decisions**: Documented in RFC status field; rationale captured in meeting notes

## 3. Release Train

- **Cadence**: Monthly releases (v1.x.y) on the first Monday
- **Versioning**: Semantic Versioning — MAJOR.MINOR.PATCH
- **Changelog**: Auto-generated from conventional commits + manual highlights
- **Release branches**: `release/v1.x` cut from `main` 1 week before release
- **Hotfix**: Cherry-pick to release branch, release as PATCH

## 4. Deprecation Policy

- **Notice period**: 2 release cycles (2 months) minimum
- **Migration support**: Deprecated features emit warnings in logs + API responses
- **Documentation**: Deprecation notice in changelog + migration guide in docs/
- **Removal**: Only in MAJOR version bumps; announced 1 quarter ahead

## 5. Schema Evolution Rules

### Backward Compatibility Requirements
- **MINOR versions**: Only additive changes (new optional fields, new enum values)
- **No removal** of fields or enum values in MINOR versions
- **No type changes** in MINOR versions
- **Default values** required for all new fields (so old producers don't break)

### Migration Playbook Template
1. Define target schema version
2. Write migration script (schema + data)
3. Test on staging with production data copy
4. Deploy with dual-write (old + new) during transition
5. Validate all consumers process new schema
6. Remove old schema support (next MAJOR)

## 6. KPI Review

- **Monthly**: Review platform KPIs (see kpis-slos.md) in ops review meeting
- **Quarterly**: Review against roadmap milestones, adjust targets
- **Annual**: Strategic review, update v-next roadmap
