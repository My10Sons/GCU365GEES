---
id: "DI-0031"
title: "Damage Intelligence Existing System Integration Scope"
version: "1.0.0"
document_type: "Product Specification"
document_class: "Integration Scope Clarification"
status: "Draft"
classification: "Internal"
owner: "Riyadah Technology"
reviewers: "Chief Enterprise Architect, Product Owner, Damage Intelligence Lead, CROMS Lead, Maintenance Lead, QA Lead, Security Lead, Operations Lead"
approvers: ""
created: "2026-06-27"
updated: "2026-06-27"
authoritative: true
ai_consumable: true
related: "DI-0001, DI-0002, DI-0004, DI-0005, DI-0006, DI-0011, DI-0012, DI-0013, DI-0014, DI-0015, DI-0017, DI-0018, DI-0019, DI-0020, DI-0023, DI-0024, DI-0026, DI-0027, DI-0029, DI-0030, PLATFORM-0005, GEES-0007, GEES-0009"
---

# Damage Intelligence Existing System Integration Scope

## Executive Summary

This document clarifies the scope of Damage Intelligence in relation to existing GCU365 CROMS and GCU365Maintenance systems.

Damage Intelligence is not a replacement for GCU365 CROMS.

Damage Intelligence is not a replacement for GCU365Maintenance.

Damage Intelligence is not a Fleet Management system.

Damage Intelligence is an image analysis, inspection evidence processing, AI-assisted damage detection, damage comparison, damage case context, and reporting capability that integrates with existing GCU365 CROMS and GCU365Maintenance systems.

GCU365 CROMS and GCU365Maintenance are existing systems that are already developed and used. Damage Intelligence SHALL serve those systems by providing damage-related intelligence and evidence context, while preserving their existing business ownership.

---

# Purpose

The purpose of this document is to prevent scope drift.

This specification SHALL ensure that product, engineering, QA, architecture, operations, and AI development agents understand that Damage Intelligence is an add-on intelligence module for existing systems, not a new product replacing CROMS, Maintenance, or Fleet.

This document SHALL guide:

- Product planning.
- Architecture decisions.
- API design.
- Integration design.
- Domain model boundaries.
- Backlog creation.
- QA test planning.
- AI implementation prompts.
- Documentation updates.
- Scope control.

---

# Scope Statement

Damage Intelligence SHALL provide:

- Vehicle inspection image analysis.
- Vehicle inspection evidence processing.
- AI-assisted damage detection.
- Image quality validation.
- Damage classification.
- Damage severity suggestion.
- Damage comparison between inspection points.
- New damage candidate identification.
- Pre-existing damage recognition.
- Human review support.
- Damage case context.
- Damage-related reporting.
- Evidence package support.
- Integration APIs for existing CROMS.
- Integration APIs for existing GCU365Maintenance.
- Audit and traceability for damage-related actions.

Damage Intelligence SHALL NOT provide:

- A new CROMS product.
- A new Maintenance product.
- A new Fleet Management product.
- A new vehicle asset master.
- A new rental agreement system.
- A new work order execution system.
- A new finance or billing system.
- A new accounting system.
- A new customer rental lifecycle system.
- A new repair execution workflow.

---

# Existing Systems

## GCU365 CROMS

GCU365 CROMS is an existing system already developed and used.

CROMS remains responsible for:

- Rental operations.
- Rental agreements.
- Customer rental workflow.
- Reservation and booking workflow where applicable.
- Vehicle rental assignment.
- Check-out and check-in rental workflow.
- Rental status.
- Rental closure.
- Rental customer charges.
- Rental invoices or rental financial references where applicable.
- Rental reporting.

Damage Intelligence SHALL integrate with CROMS to provide damage-related evidence and analysis.

Damage Intelligence SHALL NOT replace CROMS or duplicate its rental lifecycle ownership.

---

## GCU365Maintenance

GCU365Maintenance is an existing system already developed and used.

GCU365Maintenance remains responsible for:

- Maintenance workflow.
- Work orders.
- Repair execution.
- Technician workflow.
- Workshop workflow.
- Parts usage.
- Labor tracking.
- Repair status.
- Maintenance approval workflow.
- Actual repair cost.
- Repair completion.
- Maintenance reporting.

Damage Intelligence SHALL integrate with GCU365Maintenance to provide damage evidence, damage context, advisory estimates, and post-repair inspection support.

Damage Intelligence SHALL NOT replace GCU365Maintenance or duplicate its maintenance execution ownership.

---

# Damage Intelligence Ownership

Damage Intelligence owns the following scope:

| Area | Ownership |
|------|-----------|
| Inspection evidence | Damage Intelligence |
| Image upload and evidence registration | Damage Intelligence |
| Image quality validation | Damage Intelligence |
| AI-assisted damage detection | Damage Intelligence |
| Damage finding records | Damage Intelligence |
| Damage comparison results | Damage Intelligence |
| Damage case context | Damage Intelligence |
| Human review of damage findings | Damage Intelligence |
| Damage-related reports | Damage Intelligence |
| Evidence package generation | Damage Intelligence |
| Damage audit trail | Damage Intelligence |
| Damage-related API responses | Damage Intelligence |

---

# Non-Ownership Boundaries

Damage Intelligence SHALL NOT own the following:

| Area | Owner |
|------|-------|
| Rental lifecycle | GCU365 CROMS |
| Rental agreement | GCU365 CROMS |
| Rental closure | GCU365 CROMS |
| Final rental customer charge | GCU365 CROMS or Finance |
| Vehicle master as full asset system | Existing CROMS or existing enterprise vehicle source |
| Maintenance work order | GCU365Maintenance |
| Repair execution | GCU365Maintenance |
| Technician assignment | GCU365Maintenance |
| Workshop operation | GCU365Maintenance |
| Actual repair cost | GCU365Maintenance or Finance |
| Financial posting | Finance |
| Accounting | Finance |

---

# Integration Model

Damage Intelligence SHALL operate as an integration service around image analysis and damage detection.

Recommended conceptual flow:

```text
GCU365 CROMS
  ↓
Requests inspection or damage analysis context
  ↓
Damage Intelligence
  ↓
Processes images, detects damage, compares evidence, creates damage context
  ↓
Returns damage summary, evidence package, report, or status to CROMS
```

Recommended maintenance flow:

```text
GCU365Maintenance
  ↓
Receives damage context or evidence package
  ↓
Uses damage information for maintenance review and work order workflow
  ↓
Returns repair status or actual cost reference where needed
  ↓
Damage Intelligence updates damage context and post-repair evidence
```

---

# CROMS Integration Scope

Damage Intelligence MAY provide the following to CROMS:

- Create inspection session for rental check-out.
- Create inspection session for rental check-in.
- Receive rental agreement reference.
- Receive vehicle reference.
- Receive branch reference.
- Receive customer or driver reference where allowed.
- Receive check-out/check-in context.
- Return inspection status.
- Return damage summary.
- Return damage comparison result.
- Return damage case status.
- Return evidence package reference.
- Return report reference.
- Support dispute evidence package.
- Support rental damage summary.

Damage Intelligence SHALL NOT close rentals, decide final rental charges, or own rental agreement state.

---

# Maintenance Integration Scope

Damage Intelligence MAY provide the following to GCU365Maintenance:

- Damage case context.
- Damage finding details.
- Damage severity suggestion.
- Evidence package reference.
- Inspection report reference.
- Advisory repair estimate.
- Repair relevance indicator.
- Post-repair inspection request.
- Damage case status update.
- Repair completion evidence context.

GCU365Maintenance MAY provide back to Damage Intelligence:

- Work order reference.
- Maintenance request reference.
- Repair status.
- Actual repair cost reference.
- Repair completion confirmation.
- Maintenance rejection reason.
- Additional evidence request.

Damage Intelligence SHALL NOT execute repairs, assign technicians, manage workshop operations, or own actual repair cost.

---

# Image Analysis Scope

Damage Intelligence SHALL focus on image analysis capabilities.

Image analysis MAY include:

- Image quality validation.
- Vehicle angle validation.
- Required capture completeness.
- Damage candidate detection.
- Damage type suggestion.
- Vehicle area suggestion.
- Severity suggestion.
- Confidence score.
- Uncertainty reason.
- Duplicate damage grouping.
- Comparison against previous evidence.
- New damage identification.
- Pre-existing damage matching.
- Repaired damage detection.

Image analysis outputs SHALL be advisory unless confirmed through approved workflow.

---

# AI Scope

AI in Damage Intelligence SHALL be used to support damage detection and analysis.

AI MAY assist with:

- Detecting visible damage.
- Classifying damage type.
- Suggesting affected vehicle area.
- Suggesting severity.
- Comparing current and baseline images.
- Identifying uncertain cases.
- Routing low-confidence findings to human review.
- Supporting report generation context.

AI SHALL NOT independently:

- Decide final customer liability.
- Decide final customer charge.
- Decide final actual repair cost.
- Close rental agreements.
- Create final Maintenance work orders without approved integration workflow.
- Replace human review where policy requires review.

---

# Evidence Scope

Damage Intelligence SHALL manage damage-related evidence.

Evidence MAY include:

- Inspection images.
- Image metadata.
- Capture position.
- Image quality result.
- Damage finding references.
- Comparison references.
- Review decisions.
- Damage case references.
- Reports.
- Audit records.

Evidence SHALL be:

- Secure.
- Tenant-isolated.
- Traceable.
- Access-controlled.
- Auditable.
- Protected from silent overwrite.
- Linked to CROMS or Maintenance references where applicable.

---

# Reporting Scope

Damage Intelligence MAY produce reports for existing systems.

Reports MAY include:

- Inspection Summary Report.
- Damage Detection Report.
- Damage Comparison Report.
- Damage Case Report.
- Rental Damage Summary Report.
- Maintenance Handoff Report.
- Post-Repair Inspection Report.
- Evidence Package Report.

Reports SHALL not replace CROMS rental reports or GCU365Maintenance work order reports unless explicitly designed as integrated supporting reports.

---

# Domain Boundary Rules

Damage Intelligence SHALL preserve the following domain boundaries:

1. CROMS owns rental domain.
2. Maintenance owns repair domain.
3. Damage Intelligence owns damage evidence and analysis domain.
4. Finance owns accounting and financial posting domain.
5. Existing enterprise systems remain the source of their current operational data.
6. Damage Intelligence consumes references from existing systems.
7. Damage Intelligence returns analysis and evidence context to existing systems.
8. Damage Intelligence SHALL NOT redefine existing CROMS or Maintenance workflows without explicit approved scope.

---

# API Boundary Rules

Damage Intelligence APIs SHALL be designed as integration APIs, not replacement system APIs.

APIs SHOULD support:

- Receiving existing system references.
- Creating inspection sessions.
- Uploading or referencing images.
- Running damage analysis.
- Returning damage summaries.
- Returning reports.
- Returning evidence references.
- Returning status.
- Receiving repair status updates.
- Receiving actual cost references where needed.

APIs SHALL NOT expose endpoints that imply Damage Intelligence owns:

- Rental creation.
- Rental closure.
- Customer billing.
- Maintenance work order execution.
- Financial posting.
- Full vehicle asset lifecycle.

---

# Data Boundary Rules

Damage Intelligence SHALL store only data required for damage analysis, evidence processing, audit, reporting, and integration.

Damage Intelligence SHOULD store references to existing systems rather than duplicating full ownership records.

Examples:

| Data | Storage Approach |
|------|------------------|
| Rental Agreement | Store reference from CROMS |
| Vehicle | Store reference and minimal required context |
| Customer | Store reference or minimized context only where needed |
| Work Order | Store reference from GCU365Maintenance |
| Actual Repair Cost | Store reference or returned value where needed, not ownership |
| Inspection Image | Store and own as evidence |
| Damage Finding | Store and own |
| Damage Case | Store and own |
| Damage Report | Store and own |

---

# Configuration Boundary Rules

Damage Intelligence configuration SHALL control only Damage Intelligence behavior.

Configuration MAY include:

- Capture templates.
- Image quality thresholds.
- AI thresholds.
- Damage taxonomy.
- Severity rules.
- Review routing rules.
- Report templates.
- Integration settings.
- Retention settings.
- Monitoring thresholds.

Damage Intelligence configuration SHALL NOT modify CROMS rental rules or GCU365Maintenance work order rules unless explicitly provided through approved integration configuration.

---

# Operational Boundary Rules

Operations teams SHALL treat Damage Intelligence incidents according to its scope.

Damage Intelligence incidents include:

- Image upload failure.
- AI analysis failure.
- Damage comparison failure.
- Evidence access failure.
- Damage report failure.
- Damage case processing failure.
- Integration callback failure.
- Security or audit issue related to damage evidence.

CROMS incidents remain CROMS incidents.

GCU365Maintenance incidents remain Maintenance incidents.

Cross-system incidents SHALL be coordinated, but ownership SHALL remain clear.

---

# Scope Drift Controls

The following scope drift risks SHALL be controlled.

| Risk | Control |
|------|---------|
| Building a new CROMS | Treat CROMS as existing system and integrate only |
| Building a new Maintenance system | Treat GCU365Maintenance as existing system and integrate only |
| Building a new Fleet asset system | Use existing vehicle references; do not create full asset lifecycle scope |
| AI becoming final authority | Preserve advisory AI and human review rules |
| Damage Intelligence owning repair cost | Use Maintenance or Finance actual cost reference |
| Damage Intelligence owning rental closure | CROMS remains owner of rental closure |
| Duplicating existing workflows | Use APIs/events to connect with existing systems |

---

# Correct Product Definition

The correct product definition is:

```text
Damage Intelligence is an AI-assisted image analysis and damage detection service that integrates with existing GCU365 CROMS and GCU365Maintenance systems to process inspection evidence, detect damage, compare vehicle condition, support damage review, and provide damage reports.
```

The incorrect product definition is:

```text
Damage Intelligence is a new CROMS, Fleet, or Maintenance system.
```

The incorrect definition SHALL NOT be used.

---

# Acceptance Criteria

## AC-DI-3100 — Existing System Scope

Given Damage Intelligence documentation is reviewed, then it SHALL clearly state that CROMS and GCU365Maintenance are existing systems already developed and used.

## AC-DI-3101 — No Replacement Scope

Given Damage Intelligence scope is reviewed, then it SHALL NOT be positioned as a replacement for CROMS, GCU365Maintenance, Fleet, Finance, or enterprise asset management.

## AC-DI-3102 — CROMS Boundary

Given CROMS integration is designed, then CROMS SHALL remain the owner of rental operations, rental agreements, rental lifecycle, rental closure, and final rental customer charge.

## AC-DI-3103 — Maintenance Boundary

Given Maintenance integration is designed, then GCU365Maintenance SHALL remain the owner of maintenance workflow, work orders, repair execution, repair status, and actual repair cost.

## AC-DI-3104 — Damage Intelligence Boundary

Given Damage Intelligence is implemented, then it SHALL own inspection evidence, image analysis, damage findings, comparison results, damage case context, review context, and damage-related reports.

## AC-DI-3105 — AI Advisory Boundary

Given AI analysis is used, then AI SHALL remain advisory and SHALL NOT independently decide final liability, final customer charge, actual repair cost, rental closure, or work order execution.

## AC-DI-3106 — Integration API Boundary

Given APIs are designed, then APIs SHALL exchange references, evidence, analysis, status, reports, and callbacks without duplicating CROMS or Maintenance ownership.

---

# Normative Requirements

## Requirement

ID: REQ-DI-3000

Title:
Existing System Integration Scope

Statement:
Damage Intelligence SHALL define its scope as an image analysis and damage detection service for existing GCU365 CROMS and GCU365Maintenance systems.

Priority:
Critical

Verification:
Product Review

---

## Requirement

ID: REQ-DI-3001

Title:
No CROMS Replacement

Statement:
Damage Intelligence SHALL NOT be positioned or implemented as a replacement for GCU365 CROMS.

Priority:
Critical

Verification:
Scope Review

---

## Requirement

ID: REQ-DI-3002

Title:
No Maintenance Replacement

Statement:
Damage Intelligence SHALL NOT be positioned or implemented as a replacement for GCU365Maintenance.

Priority:
Critical

Verification:
Scope Review

---

## Requirement

ID: REQ-DI-3003

Title:
No Fleet Asset System Scope

Statement:
Damage Intelligence SHALL NOT be positioned or implemented as a full Fleet Management or vehicle asset lifecycle system.

Priority:
Critical

Verification:
Scope Review

---

## Requirement

ID: REQ-DI-3004

Title:
CROMS Ownership Boundary

Statement:
GCU365 CROMS SHALL remain the system of record for rental operations, rental agreements, rental lifecycle, rental closure, and final rental customer charge.

Priority:
Critical

Verification:
Architecture Review

---

## Requirement

ID: REQ-DI-3005

Title:
Maintenance Ownership Boundary

Statement:
GCU365Maintenance SHALL remain the system of record for maintenance workflows, work orders, repair execution, repair status, and actual repair cost.

Priority:
Critical

Verification:
Architecture Review

---

## Requirement

ID: REQ-DI-3006

Title:
Damage Intelligence Ownership Boundary

Statement:
Damage Intelligence SHALL own inspection evidence, image analysis, damage findings, comparison results, damage case context, review context, evidence packages, and damage-related reports.

Priority:
Critical

Verification:
Architecture Review

---

## Requirement

ID: REQ-DI-3007

Title:
Advisory AI Boundary

Statement:
Damage Intelligence AI outputs SHALL remain advisory and SHALL NOT independently decide final liability, final customer charge, rental closure, actual repair cost, or work order execution.

Priority:
Critical

Verification:
AI Governance Review

---

## Requirement

ID: REQ-DI-3008

Title:
Integration Reference Model

Statement:
Damage Intelligence SHALL integrate with existing systems primarily through references, status exchange, evidence packages, damage reports, callbacks, and controlled APIs.

Priority:
High

Verification:
Integration Review

---

## Requirement

ID: REQ-DI-3009

Title:
Scope Drift Control

Statement:
Damage Intelligence documentation and implementation SHALL prevent scope drift into CROMS, Maintenance, Fleet, Finance, or vehicle asset lifecycle ownership.

Priority:
Critical

Verification:
Scope Review

---

## Requirement

ID: REQ-DI-3010

Title:
Existing System Preservation

Statement:
Damage Intelligence SHALL preserve existing GCU365 CROMS and GCU365Maintenance business workflows and SHALL integrate without redefining ownership unless explicitly approved.

Priority:
Critical

Verification:
Product Review

---

# Business Rules

## BR-DI-2600 — CROMS Is Existing and Remains Owner

GCU365 CROMS is an existing system and SHALL remain the owner of rental operations, rental agreements, rental lifecycle, rental closure, and final rental customer charge.

---

## BR-DI-2601 — Maintenance Is Existing and Remains Owner

GCU365Maintenance is an existing system and SHALL remain the owner of maintenance workflows, work orders, repair execution, repair status, and actual repair cost.

---

## BR-DI-2602 — Damage Intelligence Is Image Analysis and Damage Detection

Damage Intelligence SHALL be scoped as image analysis, evidence processing, AI-assisted damage detection, comparison, review support, damage case context, and reporting.

---

## BR-DI-2603 — No Fleet Management Scope

Damage Intelligence SHALL NOT become a full Fleet Management or vehicle asset lifecycle system.

---

## BR-DI-2604 — Use References Instead of Ownership Duplication

Damage Intelligence SHOULD reference rental, vehicle, customer, work order, and actual cost records from existing systems instead of duplicating ownership.

---

## BR-DI-2605 — AI Cannot Own Final Business Decisions

AI SHALL NOT independently own final liability, customer charge, actual repair cost, rental closure, or work order execution decisions.

---

## BR-DI-2606 — Integration Must Preserve Existing Workflows

Damage Intelligence integration SHALL preserve existing CROMS and GCU365Maintenance workflows unless an explicit approved change is documented.

---

# AI Implementation Contract

AI development agents SHALL:

- Treat this document as the authoritative scope boundary for Damage Intelligence integration with existing systems.
- Preserve all requirement IDs, acceptance criterion IDs, and business rule IDs.
- Treat GCU365 CROMS and GCU365Maintenance as existing systems already developed and used.
- Never generate requirements that turn Damage Intelligence into a replacement CROMS, Maintenance system, Fleet system, Finance system, or vehicle asset master system.
- Preserve CROMS ownership of rental lifecycle, rental closure, and final rental customer charge.
- Preserve GCU365Maintenance ownership of maintenance workflow, work orders, repair execution, repair status, and actual repair cost.
- Preserve Damage Intelligence ownership of inspection evidence, image analysis, damage findings, comparison results, damage case context, review context, evidence packages, and damage-related reports.
- Use references, APIs, callbacks, events, and reports to integrate with existing systems.
- Raise ambiguity where a requirement appears to duplicate or replace an existing CROMS or Maintenance capability.

---

# References

- DI-0001 – Product Vision
- DI-0002 – Business Requirements
- DI-0004 – Inspection Workflow
- DI-0005 – AI Damage Detection
- DI-0006 – Damage Comparison
- DI-0011 – API Specification
- DI-0012 – Domain Model
- DI-0013 – Events
- DI-0014 – Security and Privacy
- DI-0015 – Audit and Traceability
- DI-0017 – Integration with CROMS
- DI-0018 – Integration with Maintenance
- DI-0019 – Acceptance Criteria
- DI-0020 – Test Strategy
- DI-0023 – Operational Monitoring and Alerts
- DI-0024 – Configuration and Administration
- DI-0026 – Deployment and Release Strategy
- DI-0027 – Operational Runbook
- DI-0029 – Product Roadmap
- DI-0030 – Glossary and Terminology
- PLATFORM-0005 – GEES Core and Application Architecture
- GEES-0007 – Enterprise Security Standard
- GEES-0009 – Traceability Standard

---

# Revision History

| Version | Date | Description |
|----------|------|-------------|
| 1.0.0 | 2026-06-27 | Initial Existing System Integration Scope clarification |
