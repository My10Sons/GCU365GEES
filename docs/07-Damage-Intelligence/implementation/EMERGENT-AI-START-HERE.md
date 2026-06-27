---
id: "DI-EMERGENT-AI-START-HERE"
title: "Damage Intelligence Emergent AI Start Here"
version: "1.0.0"
document_type: "AI Agent Start Guide"
document_class: "Execution Entry Point"
status: "Draft"
classification: "Internal"
owner: "Riyadah Technology"
reviewers: "Chief Enterprise Architect, Product Owner, Damage Intelligence Lead, Backend Lead, AI Engineering Lead, Frontend Lead, Mobile Lead, QA Lead, Security Lead, DevOps Lead, CROMS Lead, Maintenance Lead"
approvers: ""
created: "2026-06-27"
updated: "2026-06-27"
authoritative: true
ai_consumable: true
related: "DI-EMERGENT-AI-EXECUTION-PROMPT, DI-EMERGENT-AI-TASK-SEQUENCE, DI-0031, DI-0032, DI-0033, DI-0034, DI-0035, DI-SPRINT-00, DI-SPRINT-01, DI-SPRINT-02, DI-SPRINT-03, DI-SPRINT-04, DI-SPRINT-05"
---

# Damage Intelligence Emergent AI Start Here

## Executive Summary

This is the first file Emergent AI SHALL read before implementing the production-ready Damage Intelligence application.

Emergent AI SHALL use this repository as the source of truth for every line of code.

Emergent AI SHALL NOT write code until it has read the required repository documents, confirmed the product scope, confirmed the ownership boundaries, and completed TASK-00 from the task sequence.

Damage Intelligence is a production-ready image analysis and damage detection application for existing GCU365 CROMS and existing GCU365Maintenance systems.

Damage Intelligence is not an MVP.

Damage Intelligence SHALL NOT replace CROMS, GCU365Maintenance, Fleet, Finance, rental lifecycle ownership, maintenance work order execution, actual repair cost ownership, or vehicle asset management.

---

# Start Instruction for Emergent AI

Emergent AI, start here.

Before writing any code, you MUST read this file completely.

Then read the required files listed below in the exact order.

You MUST use the repository as the source of truth for every implementation decision.

You MUST make every line of code traceable to repository documentation.

You MUST NOT invent undocumented behavior.

You MUST NOT create undocumented APIs, database tables, workflows, permissions, integrations, reports, tests, or business rules.

If the repository does not define something, stop and record a blocker.

---

# Required Reading Order

Emergent AI SHALL read the following documents in this order.

## Step 1 — Read the AI Execution Control Files

```text
docs/07-Damage-Intelligence/implementation/EMERGENT-AI-START-HERE.md
docs/07-Damage-Intelligence/implementation/EMERGENT-AI-EXECUTION-PROMPT.md
docs/07-Damage-Intelligence/implementation/EMERGENT-AI-TASK-SEQUENCE.md
```

## Step 2 — Read the Damage Intelligence Index

```text
docs/07-Damage-Intelligence/README.md
```

## Step 3 — Read the Core Scope and Implementation Files

```text
docs/07-Damage-Intelligence/DI-0031-Existing-System-Integration-Scope.md
docs/07-Damage-Intelligence/DI-0032-Implementation-Plan.md
docs/07-Damage-Intelligence/DI-0033-User-Stories-and-Backlog.md
docs/07-Damage-Intelligence/DI-0034-OpenAPI-Contract.md
docs/07-Damage-Intelligence/DI-0035-QA-Test-Case-Pack.md
```

## Step 4 — Read the Sprint Execution Plans

```text
docs/07-Damage-Intelligence/implementation/SPRINT-00-Engineering-Setup.md
docs/07-Damage-Intelligence/implementation/SPRINT-01-Production-Inspection-and-Evidence-Foundation.md
docs/07-Damage-Intelligence/implementation/SPRINT-02-Production-Image-Quality-and-AI-Detection.md
docs/07-Damage-Intelligence/implementation/SPRINT-03-Production-Review-Comparison-and-Damage-Cases.md
docs/07-Damage-Intelligence/implementation/SPRINT-04-Production-CROMS-and-Maintenance-Integration.md
docs/07-Damage-Intelligence/implementation/SPRINT-05-Production-Reports-Monitoring-Security-and-Release.md
```

## Step 5 — Read Supporting Product Specifications as Needed

Before implementing any feature, Emergent AI SHALL read the related product specification files.

Examples:

```text
docs/07-Damage-Intelligence/DI-0011-API-Specification.md
docs/07-Damage-Intelligence/DI-0012-Domain-Model.md
docs/07-Damage-Intelligence/DI-0014-Security-and-Privacy.md
docs/07-Damage-Intelligence/DI-0015-Audit-and-Traceability.md
docs/07-Damage-Intelligence/DI-0019-Acceptance-Criteria.md
docs/07-Damage-Intelligence/DI-0020-Test-Strategy.md
```

---

# First Task

After reading the required files, Emergent AI SHALL start with:

```text
TASK-00 — Repository Understanding and Scope Lock
```

TASK-00 is defined in:

```text
docs/07-Damage-Intelligence/implementation/EMERGENT-AI-TASK-SEQUENCE.md
```

Emergent AI SHALL NOT start coding before TASK-00 is complete.

---

# TASK-00 Required Output

Before coding, Emergent AI SHALL produce this output:

```text
Repository Understanding Summary:
Documents Read:
Product Scope Confirmation:
Production-Ready Confirmation:
Ownership Boundary Confirmation:
Forbidden Scope Confirmation:
Implementation Order Confirmation:
Assumptions:
Blockers:
Decision Needed:
Ready to Start Sprint 00:
```

If any blocker exists, Emergent AI SHALL stop.

---

# Repository-as-Reference Rule

Emergent AI SHALL always use the repository as the reference for every line of code.

This means:

- Every code file must map to a repository document.
- Every class must map to a repository document.
- Every method must map to a repository document.
- Every API endpoint must map to a repository document.
- Every database table must map to a repository document.
- Every database field must map to a repository document.
- Every status code must map to a repository document.
- Every permission must map to a repository document.
- Every audit event must map to a repository document.
- Every test must map to a repository document.
- Every integration must map to a repository document.
- Every report must map to a repository document.
- Every UI screen must map to a repository document.
- Every configuration setting must map to a repository document.

If a line of code cannot be traced to the repository, do not write it.

---

# Mandatory Traceability Questions

Before writing code, Emergent AI SHALL answer:

```text
Which repository document requires this code?
Which requirement does this code satisfy?
Which acceptance criterion does this code satisfy?
Which QA test validates this code?
Which security rule applies to this code?
Which audit rule applies to this code?
Which ownership boundary does this code preserve?
```

If any answer is missing, Emergent AI SHALL stop and create a blocker.

---

# Production-Ready Rule

This project is production-ready from the start.

Emergent AI SHALL NOT build a prototype.

Emergent AI SHALL NOT use MVP shortcuts.

Emergent AI SHALL NOT create temporary business workflows unless they are explicitly allowed in Sprint 00.

Production-ready means:

- Secure by default.
- Tenant-isolated.
- Auditable.
- Testable.
- Observable.
- Configurable.
- Idempotent where needed.
- Safe error handling.
- Controlled evidence access.
- Controlled report access.
- Traceable implementation.
- Clear ownership boundaries.
- Release-ready acceptance gates.

---

# Product Scope Confirmation

Damage Intelligence SHALL provide:

- Vehicle inspection evidence handling.
- Secure image upload.
- Inspection image registration.
- Image quality validation.
- AI-assisted damage detection.
- Advisory AI findings.
- Damage comparison.
- Review queue.
- Review decisions.
- Damage case context.
- Evidence packages.
- Damage reports.
- CROMS integration.
- GCU365Maintenance integration.
- Monitoring and audit.

Damage Intelligence SHALL integrate with existing GCU365 CROMS and existing GCU365Maintenance.

---

# Ownership Boundary Confirmation

## Damage Intelligence Owns

Damage Intelligence owns:

- Inspection evidence.
- Inspection images.
- Image quality results.
- AI damage findings.
- Damage comparison results.
- Review decisions.
- Damage case context.
- Evidence packages.
- Damage reports.
- Controlled evidence access.
- Controlled report access.
- Damage Intelligence audit records.
- Damage Intelligence monitoring.
- Integration references.

## CROMS Owns

GCU365 CROMS owns:

- Rental agreement.
- Rental lifecycle.
- Check-out rental operation.
- Check-in rental operation.
- Rental closure.
- Final rental customer charge.
- Rental invoice reference where applicable.
- Customer rental account actions.

## GCU365Maintenance Owns

GCU365Maintenance owns:

- Maintenance request.
- Work order.
- Repair execution.
- Technician workflow.
- Workshop workflow.
- Repair status.
- Actual repair cost.
- Maintenance completion.
- Parts usage.
- Labor tracking.

---

# Forbidden Scope

Emergent AI SHALL NOT build or implement:

- A new CROMS.
- A new GCU365Maintenance system.
- Fleet Management.
- Finance or Accounting.
- Customer billing.
- Rental closure logic.
- Final customer charge logic.
- Final liability decision logic.
- Maintenance work order execution.
- Technician assignment.
- Actual repair cost ownership.
- Vehicle asset master.
- Insurance claim approval.
- Undocumented APIs.
- Undocumented database tables.
- Undocumented roles.
- Undocumented permissions.
- Undocumented workflows.
- Undocumented reports.
- Undocumented integrations.

---

# AI Advisory Rule

AI is advisory only.

AI outputs SHALL:

- Be marked advisory.
- Include confidence score where applicable.
- Include uncertainty reason where applicable.
- Include model or provider version.
- Be linked to image, inspection, tenant, and analysis record.
- Be reviewable.
- Be auditable.

AI outputs SHALL NOT:

- Decide final customer liability.
- Decide final customer charge.
- Decide rental closure.
- Decide actual repair cost.
- Execute work orders.
- Post to Finance.
- Override human review where required.

---

# Security Rule

Emergent AI SHALL implement security from the beginning.

Security is not optional.

Emergent AI SHALL enforce:

- Authentication.
- Authorization.
- Tenant isolation.
- Object-level authorization.
- Service-to-service authentication.
- Safe error responses.
- Secret protection.
- Evidence access control.
- Report access control.
- Secure upload.
- Secure download.
- No public unrestricted evidence URLs.
- No public unrestricted report URLs.
- No raw images in logs.
- No secrets in logs.
- No cross-tenant access.

Any security ambiguity SHALL become a blocker.

---

# Audit Rule

Emergent AI SHALL create audit records for critical actions.

Audit records SHALL include:

```text
tenantId
actorId
actorType
action
objectType
objectId
timestamp
correlationId
safeMetadata
```

Audit records SHALL NOT include:

- Secrets.
- Tokens.
- Raw images.
- Permanent evidence URLs.
- Permanent report URLs.
- Sensitive storage keys.
- Unnecessary personal data.

---

# Evidence and Report Access Rule

Evidence and report access SHALL be controlled.

Emergent AI SHALL ensure:

- Access requires authorization.
- Access is tenant-scoped.
- Access uses time-limited links.
- Access is auditable.
- Public unrestricted URLs are not used.
- Permanent public links are not used.
- Retention rules are respected.
- Access purpose is respected where required.

---

# Required Implementation Order

Emergent AI SHALL implement in this order:

```text
TASK-00 — Repository Understanding and Scope Lock
TASK-01 — Sprint 00 Engineering Setup
TASK-02 — Sprint 01 Production Inspection and Evidence Foundation
TASK-03 — Sprint 02 Production Image Quality and AI Detection
TASK-04 — Sprint 03 Production Review Comparison and Damage Cases
TASK-05 — Sprint 04 Production CROMS and Maintenance Integration
TASK-06 — Sprint 05 Production Reports Monitoring Security and Release
TASK-07 — Full Regression and Production Readiness Validation
TASK-08 — Final Handover Report
```

Emergent AI SHALL NOT skip ahead unless a formal blocker, exception, or approved dependency change is documented.

---

# Required Task Summary Format

For every completed task, Emergent AI SHALL produce this summary:

```text
Task ID:
Task Name:
Sprint:
Repository Documents Read:
Requirements Implemented:
Acceptance Criteria Implemented:
QA Test Cases Implemented:
Files Created:
Files Modified:
Database Changes:
API Changes:
Security Controls Added:
Audit Controls Added:
Observability Added:
Configuration Changes:
Assumptions:
Blockers:
Validation Performed:
Tests Passed:
Tests Failed:
Known Limitations:
Next Recommended Task:
```

---

# Blocker Handling

If Emergent AI cannot continue safely, it SHALL stop and report a blocker.

Blocker format:

```text
Blocker ID:
Task ID:
Task Name:
Repository Documents Checked:
Issue:
Why This Blocks Implementation:
Risk If Ignored:
Recommended Clarification:
Proposed Safe Default:
Files Affected:
```

---

# Assumption Handling

Emergent AI MAY make only safe assumptions.

Unsafe assumptions SHALL become blockers.

Assumption format:

```text
Assumption ID:
Task ID:
Task Name:
Repository Reference:
Assumption:
Reason:
Risk:
Validation Needed:
```

Assumptions are not allowed for:

- Security.
- Tenant isolation.
- Audit.
- Evidence access.
- Report access.
- Final customer charge.
- Rental closure.
- Actual repair cost.
- Work order execution.
- CROMS ownership.
- Maintenance ownership.
- Finance posting.
- Scope expansion.

---

# Validation Before Every Commit

Before committing any change, Emergent AI SHALL validate:

```text
Build passes.
Relevant tests pass.
No secrets are committed.
No raw images are logged.
No unrestricted evidence URLs exist.
No unrestricted report URLs exist.
Tenant isolation is preserved.
Authorization is enforced.
Audit records exist where required.
Safe errors are used.
Correlation IDs are used.
Scope boundaries are preserved.
Code is traceable to repository documents.
```

---

# Commit Message Format

Emergent AI SHOULD use this commit message pattern:

```text
DI-TASK-XX: Description
```

Examples:

```text
DI-TASK-00: Confirm repository scope and execution order
DI-TASK-01: Add Sprint 00 engineering foundation
DI-TASK-02: Implement inspection and evidence foundation
DI-TASK-03: Implement image quality and AI detection
DI-TASK-04: Implement comparison review and damage cases
DI-TASK-05: Implement CROMS and Maintenance integrations
DI-TASK-06: Implement reports monitoring security and release readiness
DI-TASK-07: Complete production readiness validation
DI-TASK-08: Add final handover report
```

---

# Do Not Start Coding Until

Emergent AI SHALL NOT start coding until:

- This file has been read.
- `EMERGENT-AI-EXECUTION-PROMPT.md` has been read.
- `EMERGENT-AI-TASK-SEQUENCE.md` has been read.
- `README.md` has been read.
- DI-0031 has been read.
- DI-0032 has been read.
- DI-0033 has been read.
- DI-0034 has been read.
- DI-0035 has been read.
- TASK-00 scope lock is completed.
- No critical blocker exists.

---

# Ready-to-Start Confirmation

Before starting Sprint 00, Emergent AI SHALL output:

```text
I have read the required repository documents.
I confirm Damage Intelligence is production-ready, not MVP.
I confirm Damage Intelligence is an image analysis and damage detection application for existing GCU365 CROMS and GCU365Maintenance.
I confirm Damage Intelligence does not replace CROMS.
I confirm Damage Intelligence does not replace GCU365Maintenance.
I confirm Damage Intelligence does not build Fleet.
I confirm Damage Intelligence does not build Finance.
I confirm AI outputs are advisory.
I confirm tenant isolation is mandatory.
I confirm audit is mandatory.
I confirm controlled evidence and report access are mandatory.
I confirm every line of code must be traceable to repository documentation.
I am ready to begin TASK-01 only after TASK-00 is complete.
```

---

# Final Non-Negotiable Rules

Emergent AI SHALL obey these rules:

1. Use the repository as the source of truth.
2. Reference repository documents before writing code.
3. Make every line of code traceable to repository documentation.
4. Build production-ready, not MVP.
5. Do not invent undocumented behavior.
6. Do not rebuild CROMS.
7. Do not rebuild GCU365Maintenance.
8. Do not build Fleet.
9. Do not build Finance.
10. Do not own final customer charge.
11. Do not own rental closure.
12. Do not own work order execution.
13. Do not own actual repair cost.
14. Keep AI advisory.
15. Enforce tenant isolation.
16. Enforce authorization.
17. Audit critical actions.
18. Protect evidence access.
19. Protect report access.
20. Never expose public unrestricted URLs.
21. Never log secrets.
22. Never log raw images.
23. Validate with DI-0035 test cases.
24. Stop and report blockers when documentation is unclear.
25. Do not commit work that cannot be traced to the repository.

---

# Revision History

| Version | Date | Description |
|----------|------|-------------|
| 1.0.0 | 2026-06-27 | Initial Emergent AI start guide for production-ready Damage Intelligence |
