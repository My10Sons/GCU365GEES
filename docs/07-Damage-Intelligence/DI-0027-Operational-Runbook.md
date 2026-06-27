---
id: "DI-0027"
title: "Damage Intelligence Operational Runbook"
version: "1.0.0"
document_type: "Product Specification"
document_class: "Operational Runbook"
status: "Draft"
classification: "Internal"
owner: "Riyadah Technology"
reviewers: "Chief Enterprise Architect, Product Owner, Operations Lead, DevOps Lead, Security Lead, QA Lead, Damage Intelligence Lead, CROMS Lead, Maintenance Lead, AI Engineering Lead"
approvers: ""
created: "2026-06-27"
updated: "2026-06-27"
authoritative: true
ai_consumable: true
related: "DI-0001, DI-0002, DI-0004, DI-0005, DI-0006, DI-0011, DI-0012, DI-0013, DI-0014, DI-0015, DI-0016, DI-0017, DI-0018, DI-0019, DI-0020, DI-0021, DI-0022, DI-0023, DI-0024, DI-0026, GEES-0007, GEES-0009, PLATFORM-0005"
---

# Damage Intelligence Operational Runbook

## Executive Summary

This document defines the operational runbook for Damage Intelligence.

The runbook provides operational guidance for monitoring, incident response, escalation, recovery, troubleshooting, support handling, routine checks, and service continuity.

Damage Intelligence supports inspection workflows, image capture, evidence storage, AI damage detection, damage comparison, human review, damage cases, CROMS integration, Maintenance integration, reporting, audit, retention, localization, configuration, monitoring, and release operations.

This runbook SHALL help operations, support, DevOps, security, QA, AI engineering, CROMS, and Maintenance teams respond consistently to operational issues.

---

# Purpose

The purpose of this document is to define operational procedures for Damage Intelligence.

This specification SHALL guide:

- Daily operational checks.
- Incident triage.
- Incident severity classification.
- Escalation.
- Troubleshooting.
- Recovery.
- Evidence protection.
- Integration failure handling.
- AI failure handling.
- Security incident response.
- Audit failure handling.
- Post-incident review.
- Operational readiness.

---

# Scope

## In Scope

This runbook covers:

- Operational roles.
- Daily checks.
- Monitoring review.
- Alert response.
- Incident classification.
- Incident triage.
- Inspection workflow issues.
- Image upload issues.
- Image quality processing issues.
- AI processing issues.
- Damage comparison issues.
- Review queue issues.
- Damage case issues.
- CROMS integration issues.
- Maintenance integration issues.
- Report generation issues.
- Evidence access issues.
- Security issues.
- Audit issues.
- Retention job issues.
- Configuration issues.
- Deployment-related issues.
- Escalation.
- Recovery.
- Communication.
- Post-incident review.

## Out of Scope

This runbook does not define:

- Final on-call schedule.
- Final monitoring tool setup.
- Final ticketing system workflow.
- Final cloud infrastructure scripts.
- Final disaster recovery plan.
- Final production SLA contract.
- Final legal incident notification policy.
- Final security breach notification procedure.

---

# Operational Principles

Damage Intelligence operations SHALL follow these principles:

1. Protect Evidence First
2. Protect Tenant Isolation
3. Protect Customer-Impacting Workflows
4. Preserve Auditability
5. Escalate Security Issues Immediately
6. Make Incidents Traceable
7. Restore Service Safely
8. Avoid Manual Data Changes Without Approval
9. Communicate Clearly
10. Record Lessons Learned

---

# Operational Roles

| Role | Responsibility |
|-----|----------------|
| Operations Lead | Owns workflow health and business continuity |
| DevOps Lead | Owns infrastructure, deployment, monitoring, and recovery |
| Security Lead | Owns security incidents, access issues, and suspicious activity |
| Damage Intelligence Lead | Owns product-specific operational decisions |
| AI Engineering Lead | Owns AI service, model, confidence, and processing issues |
| CROMS Lead | Owns rental workflow integration issues |
| Maintenance Lead | Owns work order and repair workflow integration issues |
| QA Lead | Owns validation of fixes and regression checks |
| Product Owner | Owns business priority and release/mitigation decisions |

---

# Severity Classification

Incidents SHALL be classified by severity.

| Severity | Description | Example |
|---------|-------------|---------|
| Critical | Immediate risk to evidence, tenant isolation, security, active rental workflow, or major outage | Cross-tenant data exposure, evidence access breach, system-wide inspection failure |
| High | Major workflow or integration failure with business impact | CROMS check-in integration down, image upload unavailable |
| Medium | Degraded service with workaround | AI queue delay, report generation delay |
| Low | Minor operational issue or non-urgent defect | Dashboard refresh delay, non-critical notification failure |

---

# Incident Response Flow

```text
Alert or User Report
  ↓
Triage
  ↓
Severity Classification
  ↓
Initial Containment
  ↓
Owner Assignment
  ↓
Investigation
  ↓
Mitigation or Recovery
  ↓
Validation
  ↓
Communication
  ↓
Closure
  ↓
Post-Incident Review
```

---

# Daily Operational Checks

Operations SHOULD perform daily checks.

| Check | Owner | Frequency |
|------|-------|-----------|
| API health | DevOps Lead | Daily |
| Database health | DevOps Lead | Daily |
| Storage health | DevOps Lead | Daily |
| AI queue health | AI Engineering Lead | Daily |
| Failed AI jobs | AI Engineering Lead | Daily |
| Image upload failures | DevOps Lead | Daily |
| Inspection backlog | Operations Lead | Daily |
| Review queue backlog | Operations Lead | Daily |
| Damage case backlog | Operations Lead | Daily |
| CROMS integration failures | CROMS Lead | Daily |
| Maintenance integration failures | Maintenance Lead | Daily |
| Report generation failures | Operations Lead | Daily |
| Security alerts | Security Lead | Daily |
| Audit logging health | Security Lead | Daily |
| Retention job status | DevOps Lead | Daily |

---

# Weekly Operational Checks

Weekly checks SHOULD include:

- Review open incidents.
- Review recurring alerts.
- Review AI failure trends.
- Review image quality failure trends.
- Review missing baseline rates.
- Review integration reliability.
- Review review queue SLA.
- Review evidence access anomalies.
- Review audit failures.
- Review retention job failures.
- Review configuration changes.
- Review release-related incidents.
- Review unresolved support tickets.

---

# Incident Triage Checklist

When an incident is reported, the responder SHOULD capture:

- Incident ID.
- Reporter.
- Tenant ID.
- Environment.
- Affected module.
- Affected workflow.
- Affected users.
- Affected vehicle ID where applicable.
- Affected inspection session ID where applicable.
- Affected damage case ID where applicable.
- Correlation ID.
- Time started.
- Current status.
- Error message.
- Severity.
- Initial owner.
- Immediate workaround.

Do not record secrets, tokens, raw images, or unrestricted evidence URLs in incident notes.

---

# General Troubleshooting Steps

Initial troubleshooting SHOULD include:

1. Confirm affected environment.
2. Confirm tenant and user scope.
3. Check service health.
4. Check recent deployments.
5. Check recent configuration changes.
6. Check logs by correlation ID.
7. Check event processing status.
8. Check background job status.
9. Check integration status.
10. Check audit records.
11. Confirm whether evidence integrity is affected.
12. Confirm whether tenant isolation is affected.
13. Escalate if security, privacy, or evidence risk exists.

---

# Inspection Workflow Incident Runbook

## Symptoms

- User cannot create inspection.
- Inspection cannot be started.
- Inspection cannot be submitted.
- Inspection stuck in Draft, Capturing, Submitted, Analyzing, or ReviewRequired.
- Required capture checklist not loading.
- Invalid state transition error.

## Checks

- Check API health.
- Check tenant configuration.
- Check capture template status.
- Check user permissions.
- Check workflow state.
- Check required image status.
- Check AI/comparison queue status.
- Check recent configuration changes.
- Check logs by inspectionSessionId and correlationId.

## Mitigation

- Retry failed background job where safe.
- Requeue inspection processing where approved.
- Request recapture where evidence is missing.
- Apply authorized workflow correction only through approved admin function.
- Escalate invalid state corruption to engineering.

## Escalation

Escalate to Damage Intelligence Lead and DevOps Lead if multiple inspections are affected.

Escalate to Security Lead if cross-tenant access or unauthorized workflow state change is suspected.

---

# Image Upload Incident Runbook

## Symptoms

- Image upload fails.
- Upload URL cannot be generated.
- Image registration fails.
- Uploaded image not visible.
- Image appears under wrong inspection.
- Evidence access denied unexpectedly.

## Checks

- Check object storage health.
- Check API upload endpoint.
- Check signed URL generation.
- Check file size and content type.
- Check tenant storage path.
- Check image registration record.
- Check user permission.
- Check evidence access audit.
- Check storage policy changes.
- Check recent deployment or configuration change.

## Mitigation

- Ask user to retry upload where safe.
- Reissue upload URL where appropriate.
- Re-register uploaded object only if storage object and tenant path are verified.
- Never manually move evidence between tenants.
- Never expose public image URLs as workaround.

## Escalation

Escalate immediately to Security Lead if evidence appears visible to the wrong tenant or unauthorized user.

---

# Image Quality Incident Runbook

## Symptoms

- Excessive recapture requests.
- Valid images rejected.
- Poor images accepted.
- Quality check not running.
- Quality check queue delayed.
- Quality failure reasons missing.

## Checks

- Check image quality service health.
- Check queue depth.
- Check quality configuration.
- Check capture template version.
- Check threshold changes.
- Check failure rate by branch/user/capture position.
- Check recent AI or image quality release.
- Check audit for configuration changes.

## Mitigation

- Roll back recent threshold change where approved.
- Disable strict quality rule by feature flag only if approved.
- Allow authorized override where policy permits.
- Route affected inspections for review if evidence quality is uncertain.

## Escalation

Escalate to AI Engineering Lead or Damage Intelligence Lead when quality logic affects customer-impacting evidence.

---

# AI Processing Incident Runbook

## Symptoms

- AI analysis not starting.
- AI jobs stuck.
- AI failures increasing.
- AI timeout spike.
- AI output missing.
- Low-confidence outputs increasing.
- AI provider unavailable.

## Checks

- Check AI service health.
- Check AI queue depth.
- Check provider status.
- Check AI timeout and retry metrics.
- Check model or engine version.
- Check recent AI configuration changes.
- Check input image availability.
- Check privacy filter behavior.
- Check logs by aiAnalysisId and inspectionSessionId.

## Mitigation

- Retry failed AI job where safe.
- Requeue analysis where approved.
- Fall back to manual review if AI unavailable.
- Disable AI feature flag only if approved.
- Roll back AI model/provider change where practical.
- Notify Operations if manual review backlog will increase.

## Escalation

Escalate to AI Engineering Lead for AI service or model issues.

Escalate to Product Owner if AI unavailability affects business workflow.

---

# Damage Comparison Incident Runbook

## Symptoms

- Comparison not running.
- Missing baseline spike.
- NotComparable spike.
- New damage not identified.
- Pre-existing damage incorrectly marked.
- Comparison failures increasing.

## Checks

- Check comparison worker health.
- Check baseline selection rules.
- Check previous inspection availability.
- Check image evidence availability.
- Check tenant configuration.
- Check taxonomy and capture template versions.
- Check logs by comparisonId, vehicleId, and inspectionSessionId.

## Mitigation

- Requeue comparison where safe.
- Route affected results to human review.
- Apply configuration rollback where faulty rule is identified.
- Do not automatically confirm new damage when baseline is missing.

## Escalation

Escalate to Damage Intelligence Lead if comparison outcomes affect customer disputes or billing workflows.

---

# Review Queue Incident Runbook

## Symptoms

- Review queue not loading.
- Review assignments missing.
- Review backlog increasing.
- Review decision cannot be saved.
- Unauthorized users see review items.
- Review override reason not recorded.

## Checks

- Check review API health.
- Check user permissions.
- Check tenant and branch scope.
- Check review routing rules.
- Check queue filters.
- Check database status.
- Check audit records for review actions.
- Check recent configuration changes.

## Mitigation

- Rebuild review queue read model where supported.
- Correct permissions through approved admin process.
- Route high-priority cases manually through approved workflow.
- Do not bypass review for customer-impacting cases unless governance approves.

## Escalation

Escalate to Operations Lead if review backlog affects service levels.

Escalate to Security Lead if unauthorized review access is suspected.

---

# Damage Case Incident Runbook

## Symptoms

- Damage case not created.
- Duplicate damage case created.
- Damage case stuck.
- Case cannot be confirmed or rejected.
- Case cannot be routed to Maintenance.
- Case closure fails.

## Checks

- Check damage case API health.
- Check case creation rules.
- Check comparison result.
- Check damage finding status.
- Check evidence links.
- Check review decision status.
- Check idempotency logs.
- Check Maintenance integration status.
- Check audit records.

## Mitigation

- Requeue case creation where safe.
- Merge or mark duplicates only through approved workflow.
- Route case to review where status is uncertain.
- Avoid manual database edits.

## Escalation

Escalate to Damage Intelligence Lead for lifecycle corruption or customer-impacting cases.

---

# CROMS Integration Incident Runbook

## Symptoms

- CROMS cannot request check-out inspection.
- CROMS cannot request check-in inspection.
- Rental damage summary unavailable.
- Damage status not reaching CROMS.
- Duplicate inspection sessions from CROMS retry.
- CROMS callback failure.

## Checks

- Check CROMS integration endpoint health.
- Check authentication and authorization.
- Check tenant mapping.
- Check rentalAgreementId.
- Check vehicleId.
- Check idempotency key.
- Check event or callback logs.
- Check retry and dead-letter status.
- Check recent CROMS release or configuration change.

## Mitigation

- Retry failed callback where safe.
- Replay event where approved.
- Return existing inspection where duplicate request detected.
- Temporarily queue requests if CROMS is unavailable.
- Notify CROMS Lead and Operations Lead.

## Escalation

Escalate as High or Critical if active rental check-in/check-out is blocked.

---

# Maintenance Integration Incident Runbook

## Symptoms

- Damage case not routed to Maintenance.
- Maintenance does not receive evidence package.
- Work order reference not received.
- Repair status update not processed.
- Duplicate Maintenance request created.
- Post-repair inspection not triggered.

## Checks

- Check Maintenance integration endpoint health.
- Check damageCaseId.
- Check maintenanceRequestId.
- Check workOrderId.
- Check tenant mapping.
- Check evidence package access.
- Check routing rules.
- Check retry and dead-letter status.
- Check recent Maintenance release or configuration change.

## Mitigation

- Retry routing where idempotency is available.
- Replay event where approved.
- Provide controlled evidence package reference where authorized.
- Trigger post-repair inspection manually only through approved workflow.
- Do not expose public evidence URLs.

## Escalation

Escalate to Maintenance Lead when repair-required damage is blocked.

Escalate to Security Lead if evidence package access is unauthorized.

---

# Report Generation Incident Runbook

## Symptoms

- Report generation fails.
- Report export fails.
- Report download access denied.
- Customer-facing report unavailable.
- Report contains incorrect language.
- Report contains missing evidence.
- Report access expiration not working.

## Checks

- Check reporting service health.
- Check report template version.
- Check source inspection/case data.
- Check evidence references.
- Check user permissions.
- Check tenant and object scope.
- Check localization settings.
- Check report storage.
- Check audit records.

## Mitigation

- Regenerate report where safe.
- Rebuild report read model where supported.
- Revoke report access if privacy issue is suspected.
- Reissue report after validation.
- Never manually attach evidence outside authorized report process.

## Escalation

Escalate to Security Lead if report exposes unauthorized data.

Escalate to Product Owner if report failure affects customer dispute.

---

# Evidence Access Incident Runbook

## Symptoms

- Unauthorized evidence access.
- Evidence visible to wrong user.
- Evidence visible to wrong tenant.
- Signed URLs not expiring.
- Evidence download spike.
- Evidence not accessible to authorized user.

## Checks

- Check access logs.
- Check audit records.
- Check user role and tenant.
- Check object-level authorization.
- Check signed URL expiry.
- Check storage policy.
- Check report sharing policy.
- Check recent permission/configuration changes.

## Mitigation

- Revoke exposed links immediately.
- Disable affected evidence access path where required.
- Rotate affected credentials where needed.
- Notify Security Lead.
- Preserve evidence and audit logs.
- Do not delete evidence unless approved.

## Escalation

Treat suspected cross-tenant evidence exposure as Critical.

---

# Security Incident Runbook

## Symptoms

- Cross-tenant access attempt.
- Unauthorized evidence access.
- Excessive failed authorization.
- Suspicious export activity.
- Privileged role misuse.
- Secrets exposed in logs or alerts.
- API abuse pattern.

## Checks

- Check security alerts.
- Check audit records.
- Check user session activity.
- Check permission changes.
- Check API logs.
- Check evidence access logs.
- Check report access logs.
- Check recent deployments/configuration changes.

## Mitigation

- Disable affected account where approved.
- Revoke tokens where applicable.
- Rotate secrets where needed.
- Block affected access path.
- Preserve logs and audit records.
- Notify Security Lead immediately.

## Escalation

Security incidents involving tenant isolation, evidence exposure, secrets, or customer data SHALL be escalated as Critical.

---

# Audit Failure Runbook

## Symptoms

- Audit record creation failed.
- Audit records missing for critical action.
- Audit storage unavailable.
- Audit access not logged.
- Audit export failed.

## Checks

- Check audit service health.
- Check database/storage health.
- Check event pipeline.
- Check application logs.
- Check affected workflow.
- Check recent deployment.
- Check retention or archival job.

## Mitigation

- Stop or restrict critical workflow if audit cannot be preserved.
- Retry audit write where safe.
- Queue audit records where supported.
- Record manual incident note without sensitive details.
- Escalate to Security Lead.

## Escalation

Audit failure for critical actions SHALL be High or Critical depending on business impact.

---

# Retention Job Incident Runbook

## Symptoms

- Retention job failed.
- Archive job failed.
- Deletion job failed.
- Legal hold not applied.
- Dispute hold not applied.
- Data deleted despite hold.
- Records blocked incorrectly.

## Checks

- Check retention job logs.
- Check retention policy.
- Check legal hold status.
- Check dispute hold status.
- Check active workflow dependencies.
- Check audit records.
- Check recent retention configuration changes.

## Mitigation

- Pause deletion jobs if risk is unclear.
- Restore from backup where approved and feasible.
- Reapply legal or dispute hold.
- Re-run archival job where safe.
- Do not manually delete records.

## Escalation

Any deletion of held or active evidence SHALL be treated as Critical.

---

# Configuration Incident Runbook

## Symptoms

- Incorrect capture template active.
- AI threshold changed unexpectedly.
- Review routing changed unexpectedly.
- Report template incorrect.
- Retention policy incorrect.
- Integration settings changed.
- Unauthorized configuration change.

## Checks

- Check configuration audit.
- Check active configuration version.
- Check approver.
- Check tenant scope.
- Check activation timestamp.
- Check recent release.
- Check affected workflow.

## Mitigation

- Roll back configuration where practical.
- Disable affected feature flag where approved.
- Notify affected workflow owners.
- Re-test affected workflow.
- Preserve audit trail.

## Escalation

Escalate high-risk configuration incidents to Security Lead and Product Owner.

---

# Deployment Incident Runbook

## Symptoms

- Failure after release.
- Increased error rate.
- Migration failure.
- API incompatibility.
- Event consumer failure.
- Mobile app incompatibility.
- Feature flag issue.
- Monitoring missing after deployment.

## Checks

- Check release record.
- Check deployed version.
- Check commit SHA.
- Check migration status.
- Check smoke test result.
- Check error rate.
- Check integration status.
- Check feature flags.
- Check rollback plan.

## Mitigation

- Roll back application where practical.
- Disable feature flag where available.
- Apply hotfix where rollback is not safe.
- Pause affected background worker where required.
- Notify release owner.

## Escalation

Escalate to DevOps Lead and Product Owner for release decision.

---

# Communication Guidelines

Incident communication SHOULD include:

- Incident ID.
- Severity.
- Affected environment.
- Affected tenant where appropriate.
- Affected workflow.
- Current impact.
- Current mitigation.
- Owner.
- Next update time.
- Resolution status.

Communication SHALL NOT include secrets, raw evidence, unrestricted image URLs, or unnecessary customer data.

---

# Customer and Tenant Communication

Customer or tenant communication SHOULD be approved by Product Owner and Operations Lead.

Security, privacy, or legal incident communication SHALL involve Security Lead and legal/compliance owners where required.

---

# Recovery Validation

After mitigation or recovery, the team SHALL validate:

- Service health.
- Workflow behavior.
- Evidence access.
- Tenant isolation.
- Audit records.
- Integration status.
- Background jobs.
- Monitoring and alerts.
- User-facing behavior.
- No duplicate business objects.
- No data corruption.

---

# Post-Incident Review

Post-incident review SHOULD be completed for Critical and High incidents.

Review SHOULD include:

- Timeline.
- Root cause.
- Detection method.
- Impact.
- Resolution.
- Recovery actions.
- Evidence integrity assessment.
- Tenant isolation assessment.
- Customer impact assessment.
- Preventive actions.
- Owner.
- Due date.

---

# Operational Acceptance Criteria

## AC-DI-2700 — Incident Classification

Given an operational incident is reported, when triage is performed, then the incident SHALL be assigned a severity and owner.

## AC-DI-2701 — Evidence Protection

Given an incident affects evidence, when mitigation is performed, then evidence integrity and access control SHALL be preserved.

## AC-DI-2702 — Tenant Isolation Escalation

Given cross-tenant access is suspected, when triage is performed, then the incident SHALL be treated as Critical and escalated to Security Lead.

## AC-DI-2703 — Integration Recovery

Given CROMS or Maintenance integration fails, when recovery is performed, then retry, replay, queue, or manual approved recovery SHALL be used without creating duplicate business objects.

## AC-DI-2704 — Audit Failure Handling

Given required audit logging fails, when detected, then the incident SHALL be escalated and critical workflows SHOULD be restricted where auditability cannot be preserved.

## AC-DI-2705 — Post-Incident Review

Given a Critical or High incident is resolved, then a post-incident review SHOULD be completed.

---

# Normative Requirements

## Requirement

ID: REQ-DI-2600

Title:
Operational Runbook

Statement:
Damage Intelligence SHALL define an operational runbook covering monitoring, incident triage, severity classification, escalation, troubleshooting, recovery, communication, and post-incident review.

Priority:
Critical

Verification:
Operational Review

---

## Requirement

ID: REQ-DI-2601

Title:
Incident Severity Classification

Statement:
Damage Intelligence incidents SHALL be classified by severity including Critical, High, Medium, and Low.

Priority:
Critical

Verification:
Operational Review

---

## Requirement

ID: REQ-DI-2602

Title:
Daily Operational Checks

Statement:
Damage Intelligence SHOULD define daily operational checks for health, workflows, AI, integrations, reports, audit, security, and retention jobs.

Priority:
High

Verification:
Operational Review

---

## Requirement

ID: REQ-DI-2603

Title:
Inspection Incident Handling

Statement:
Damage Intelligence SHALL define troubleshooting and mitigation guidance for inspection workflow incidents.

Priority:
High

Verification:
Runbook Review

---

## Requirement

ID: REQ-DI-2604

Title:
Evidence Incident Handling

Statement:
Damage Intelligence SHALL define troubleshooting and escalation guidance for image upload, evidence access, evidence integrity, and evidence security incidents.

Priority:
Critical

Verification:
Security Review

---

## Requirement

ID: REQ-DI-2605

Title:
AI Incident Handling

Statement:
Damage Intelligence SHALL define troubleshooting and mitigation guidance for AI processing, AI queue, AI provider, and AI output incidents.

Priority:
High

Verification:
AI Operational Review

---

## Requirement

ID: REQ-DI-2606

Title:
Comparison Incident Handling

Statement:
Damage Intelligence SHOULD define troubleshooting and mitigation guidance for damage comparison incidents.

Priority:
Medium

Verification:
Runbook Review

---

## Requirement

ID: REQ-DI-2607

Title:
Review and Case Incident Handling

Statement:
Damage Intelligence SHALL define troubleshooting and mitigation guidance for review queue and damage case incidents.

Priority:
High

Verification:
Runbook Review

---

## Requirement

ID: REQ-DI-2608

Title:
CROMS Integration Incident Handling

Statement:
Damage Intelligence SHALL define troubleshooting, retry, replay, and escalation guidance for CROMS integration incidents.

Priority:
Critical

Verification:
Integration Review

---

## Requirement

ID: REQ-DI-2609

Title:
Maintenance Integration Incident Handling

Statement:
Damage Intelligence SHALL define troubleshooting, retry, replay, and escalation guidance for Maintenance integration incidents.

Priority:
Critical

Verification:
Integration Review

---

## Requirement

ID: REQ-DI-2610

Title:
Report Incident Handling

Statement:
Damage Intelligence SHOULD define troubleshooting and mitigation guidance for report generation, export, access, and localization incidents.

Priority:
High

Verification:
Reporting Review

---

## Requirement

ID: REQ-DI-2611

Title:
Security Incident Escalation

Statement:
Damage Intelligence incidents involving tenant isolation, evidence exposure, unauthorized access, secrets, or suspicious activity SHALL be escalated to Security Lead.

Priority:
Critical

Verification:
Security Review

---

## Requirement

ID: REQ-DI-2612

Title:
Audit Failure Handling

Statement:
Damage Intelligence SHALL define escalation and mitigation guidance for audit record creation, storage, access, and auditability failures.

Priority:
Critical

Verification:
Audit Review

---

## Requirement

ID: REQ-DI-2613

Title:
Retention Incident Handling

Statement:
Damage Intelligence SHOULD define troubleshooting and mitigation guidance for retention, archive, deletion, legal hold, and dispute hold incidents.

Priority:
High

Verification:
Compliance Review

---

## Requirement

ID: REQ-DI-2614

Title:
Configuration Incident Handling

Statement:
Damage Intelligence SHOULD define troubleshooting, rollback, and escalation guidance for configuration incidents.

Priority:
High

Verification:
Configuration Review

---

## Requirement

ID: REQ-DI-2615

Title:
Deployment Incident Handling

Statement:
Damage Intelligence SHALL define troubleshooting, rollback, hotfix, and mitigation guidance for deployment-related incidents.

Priority:
High

Verification:
Release Review

---

## Requirement

ID: REQ-DI-2616

Title:
Incident Communication

Statement:
Damage Intelligence incident communication SHALL avoid secrets, raw evidence, unrestricted image URLs, and unnecessary customer data.

Priority:
Critical

Verification:
Privacy Review

---

## Requirement

ID: REQ-DI-2617

Title:
Post-Incident Review

Statement:
Critical and High Damage Intelligence incidents SHOULD result in post-incident review with root cause, impact, recovery, and preventive actions.

Priority:
High

Verification:
Operational Review

---

# Business Rules

## BR-DI-2200 — Evidence Must Be Protected During Incidents

Incident response SHALL preserve evidence integrity, access control, tenant isolation, and auditability.

---

## BR-DI-2201 — Cross-Tenant Risk Is Critical

Suspected cross-tenant access or exposure SHALL be treated as Critical until proven otherwise.

---

## BR-DI-2202 — Public Evidence Links Are Not a Workaround

Operations SHALL NOT use public or unrestricted image URLs as an incident workaround.

---

## BR-DI-2203 — Critical Audit Failure Requires Escalation

Failure to create required audit records for critical actions SHALL be escalated.

---

## BR-DI-2204 — Retry Must Be Idempotent

Operational retry or replay SHALL avoid duplicate inspections, damage cases, reports, Maintenance requests, work orders, or customer-impacting records.

---

## BR-DI-2205 — Manual Data Changes Require Approval

Manual correction of production data SHALL require approval, audit, and validation.

---

## BR-DI-2206 — Incident Notes Must Avoid Sensitive Data

Incident notes SHALL NOT include secrets, tokens, raw images, unrestricted evidence URLs, or unnecessary customer data.

---

# AI Implementation Contract

AI development agents SHALL:

- Treat this document as the authoritative operational runbook for Damage Intelligence.
- Preserve all requirement IDs, acceptance criterion IDs, and business rule IDs.
- Generate future runbooks, incident templates, alert response guides, recovery scripts, troubleshooting flows, and support procedures consistent with this document.
- Preserve evidence protection, tenant isolation, security escalation, auditability, idempotent retry, and privacy requirements.
- Preserve CROMS and Maintenance integration incident handling boundaries.
- Never recommend public evidence URLs, unsafe manual database edits, or unaudited production changes.
- Raise ambiguity where incident owner, severity, escalation path, recovery method, or customer communication policy is unclear.

---

# References

- DI-0011 – API Specification
- DI-0013 – Events
- DI-0014 – Security and Privacy
- DI-0015 – Audit and Traceability
- DI-0017 – Integration with CROMS
- DI-0018 – Integration with Maintenance
- DI-0020 – Test Strategy
- DI-0022 – Data Retention and Archival
- DI-0023 – Operational Monitoring and Alerts
- DI-0024 – Configuration and Administration
- DI-0026 – Deployment and Release Strategy
- GEES-0007 – Enterprise Security Standard
- GEES-0009 – Traceability Standard
- PLATFORM-0005 – GEES Core and Application Architecture

---

# Revision History

| Version | Date | Description |
|----------|------|-------------|
| 1.0.0 | 2026-06-27 | Initial Damage Intelligence Operational Runbook |
