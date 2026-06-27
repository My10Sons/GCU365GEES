---
id: DI-0002
title: Damage Intelligence Business Requirements
version: 1.0.0
document_type: Product Specification
document_class: Business Requirements
status: Draft
classification: Internal
owner: Riyadah Technology
reviewers:
  - Chief Enterprise Architect
  - Product Owner
  - AI Engineering Lead
  - Operations Lead
  - Maintenance Lead
approvers: []
created: 2026-06-27
updated: 2026-06-27
authoritative: true
ai_consumable: true
related:
  - DI-0001
  - RA-0001
  - RA-0002
  - GEES-0005
  - GEES-0011
  - GEES-0013
  - GEES-0014
  - PLATFORM-0005
---

# Damage Intelligence Business Requirements

## Executive Summary

This document defines the business requirements for the Damage Intelligence capability.

Damage Intelligence is the shared AI-assisted vehicle inspection, evidence management, damage detection, damage comparison, and damage case management capability used by GCU365 CROMS and GCU365 Maintenance.

The business requirements in this document define what the capability must achieve from an operational, business, compliance, and customer-dispute perspective.

Technical implementation details, database schemas, API contracts, UI screens, and AI prompt contracts SHALL be defined in later specifications.

---

# Purpose

The purpose of this document is to define the business requirements that govern Damage Intelligence.

These requirements SHALL guide:

- Product design
- Workflow design
- AI behavior
- API design
- Data model design
- Mobile capture design
- CROMS integration
- Maintenance integration
- Reporting
- Testing
- Acceptance criteria

---

# Scope

## In Scope

The following business capabilities are in scope:

- Vehicle check-out inspection support.
- Vehicle check-in inspection support.
- Standardized vehicle photo capture.
- Inspection evidence management.
- Image quality assessment.
- AI-assisted damage detection.
- Damage classification.
- Damage severity assessment.
- Historical damage comparison.
- New versus pre-existing damage determination.
- Human review of AI findings.
- Damage case management.
- Damage reports.
- CROMS integration.
- Maintenance integration.
- Audit trail.
- Dispute evidence support.

## Out of Scope

The following capabilities are out of scope for this document:

- Full CROMS rental agreement management.
- Full Maintenance work order management.
- Full insurance claim processing.
- Customer payment processing.
- Automatic liability assignment without human approval.
- Full ML training pipeline.
- Telematics accident detection.
- Legal claim management.
- Fully autonomous repair approval.

---

# Business Context

Vehicle rental and fleet operations require reliable evidence of vehicle condition at the beginning and end of each rental lifecycle.

Without standardized inspection and comparison, organizations face:

- Customer disputes.
- Missed vehicle damage.
- Inconsistent staff inspection quality.
- Poor evidence capture.
- Delayed repair decisions.
- Unreliable damage history.
- Weak operational accountability.
- Difficulty proving whether damage is new or pre-existing.

Damage Intelligence addresses these challenges by creating a structured, auditable, AI-assisted vehicle condition intelligence layer.

---

# Business Goals

Damage Intelligence SHALL support the following business goals:

1. Reduce customer disputes related to vehicle damage.
2. Improve inspection consistency.
3. Improve photo evidence quality.
4. Identify likely new damage.
5. Preserve complete vehicle condition history.
6. Support maintenance routing.
7. Reduce manual damage documentation.
8. Improve operational transparency.
9. Support audit and compliance.
10. Improve confidence in rental check-in and check-out decisions.

---

# Stakeholders

## Business Stakeholders

- Rental Operations Manager
- Fleet Operations Manager
- Maintenance Manager
- Workshop Manager
- Customer Service Manager
- Finance Manager
- Compliance Officer
- Branch Manager

## Operational Users

- Rental Agent
- Vehicle Inspector
- Maintenance Advisor
- Technician
- Fleet Supervisor
- Quality Inspector

## External Stakeholders

- Customer
- Insurance Company
- Repair Vendor
- Regulatory Auditor

---

# Assumptions

The following assumptions apply:

1. Vehicles are registered in GCU365 CROMS before inspection.
2. Rental agreements are managed by GCU365 CROMS.
3. Work orders are managed by GCU365 Maintenance.
4. Damage Intelligence owns inspection evidence and damage assessment records.
5. AI assists but does not make final liability or financial decisions.
6. Human review is required for operationally significant damage decisions.
7. Images may be captured from mobile devices.
8. Internet connectivity may not always be available during capture.
9. Historical inspection evidence may not exist for every vehicle at launch.
10. Different lighting, weather, reflections, dirt, and camera angles may affect image quality.

---

# Dependencies

Damage Intelligence depends on:

- Vehicle master data from CROMS.
- Rental agreement context from CROMS.
- User identity and permissions from shared platform services.
- Image storage service.
- AI services.
- Audit logging.
- Maintenance integration for repair routing.
- Notification services.
- Reporting services.

---

# Requirement Categories

Business requirements are grouped into the following categories:

1. Inspection Workflow
2. Image Capture
3. Evidence Management
4. AI Damage Detection
5. Historical Comparison
6. Damage Case Management
7. Human Review
8. CROMS Integration
9. Maintenance Integration
10. Audit and Compliance
11. Reporting
12. Non-Functional Business Requirements

---

# Business Requirements

## REQ-DI-0100 — Standardized Inspection Workflow

### Title

Standardized Inspection Workflow

### Statement

Damage Intelligence SHALL provide standardized inspection workflows for vehicle check-out and vehicle check-in.

### Rationale

Standardized workflows reduce inspection inconsistency and improve evidence quality.

### Priority

Critical

### Verification

Workflow Review, Functional Test

---

## REQ-DI-0101 — Check-Out Baseline Inspection

### Title

Check-Out Baseline Inspection

### Statement

Damage Intelligence SHALL support a baseline vehicle inspection before a rental starts.

### Rationale

The baseline inspection establishes the vehicle condition before customer possession.

### Priority

Critical

### Verification

Functional Test

---

## REQ-DI-0102 — Check-In Return Inspection

### Title

Check-In Return Inspection

### Statement

Damage Intelligence SHALL support a return inspection when a vehicle is returned after rental.

### Rationale

The return inspection establishes the vehicle condition after customer possession.

### Priority

Critical

### Verification

Functional Test

---

## REQ-DI-0103 — Guided Photo Capture

### Title

Guided Photo Capture

### Statement

Damage Intelligence SHALL guide users to capture required vehicle photos using standardized capture positions.

### Rationale

Guided capture improves consistency and makes historical comparison more reliable.

### Priority

Critical

### Verification

Mobile Workflow Test

---

## REQ-DI-0104 — Mandatory Capture Set

### Title

Mandatory Capture Set

### Statement

Damage Intelligence SHALL define a mandatory minimum photo capture set for each inspection type.

### Rationale

A minimum capture set ensures adequate evidence coverage.

### Priority

Critical

### Verification

Inspection Configuration Review

---

## REQ-DI-0105 — Image Quality Validation

### Title

Image Quality Validation

### Statement

Damage Intelligence SHALL validate image quality before accepting inspection photos where practical.

### Rationale

Poor-quality images reduce AI accuracy and weaken dispute evidence.

### Priority

High

### Verification

Image Quality Test

---

## REQ-DI-0106 — Inspection Evidence Preservation

### Title

Inspection Evidence Preservation

### Statement

Damage Intelligence SHALL preserve inspection photos, metadata, timestamps, capture user, inspection type, and related vehicle context.

### Rationale

Inspection evidence must be auditable and usable in operational review or dispute resolution.

### Priority

Critical

### Verification

Audit Review, Data Review

---

## REQ-DI-0107 — AI-Assisted Damage Detection

### Title

AI-Assisted Damage Detection

### Statement

Damage Intelligence SHALL support AI-assisted detection of visible vehicle damage from inspection images.

### Rationale

AI assistance reduces manual inspection effort and improves detection consistency.

### Priority

Critical

### Verification

AI Functional Test

---

## REQ-DI-0108 — Damage Classification

### Title

Damage Classification

### Statement

Damage Intelligence SHALL classify detected damage by damage type, vehicle area, and severity where possible.

### Rationale

Structured classification enables reporting, review, repair routing, and cost estimation.

### Priority

Critical

### Verification

Functional Test, AI Review

---

## REQ-DI-0109 — Supported Damage Types

### Title

Supported Damage Types

### Statement

Damage Intelligence SHALL support classification of common visible vehicle damage types.

Supported types SHOULD include:

- Scratch
- Dent
- Crack
- Broken light
- Broken glass
- Missing trim
- Wheel rash
- Tire damage
- Paint transfer
- Rust
- Bumper damage
- Mirror damage
- Fluid leak

### Rationale

Damage categories must be standardized for operational consistency.

### Priority

High

### Verification

Taxonomy Review

---

## REQ-DI-0110 — Historical Damage Comparison

### Title

Historical Damage Comparison

### Statement

Damage Intelligence SHALL compare current inspection evidence against previous inspection evidence where available.

### Rationale

Historical comparison is required to determine whether damage is new, pre-existing, changed, repaired, or uncertain.

### Priority

Critical

### Verification

Comparison Test

---

## REQ-DI-0111 — Damage Delta Classification

### Title

Damage Delta Classification

### Statement

Damage Intelligence SHALL classify compared damage findings as one of:

- New
- Pre-existing
- Changed
- Repaired
- Uncertain

### Rationale

Operational decisions depend on distinguishing new damage from existing damage.

### Priority

Critical

### Verification

Functional Test

---

## REQ-DI-0112 — Confidence Scoring

### Title

Confidence Scoring

### Statement

Damage Intelligence SHOULD provide confidence scores for AI-generated damage findings and comparison results.

### Rationale

Confidence scores help users decide when human review is required.

### Priority

High

### Verification

AI Review

---

## REQ-DI-0113 — Human Review Requirement

### Title

Human Review Requirement

### Statement

Damage Intelligence SHALL allow authorized users to review AI-generated damage findings before final operational or financial decisions.

### Rationale

AI must support human decision-making but not replace accountability.

### Priority

Critical

### Verification

Workflow Test

---

## REQ-DI-0114 — Human Override

### Title

Human Override

### Statement

Damage Intelligence SHALL allow authorized users to confirm, edit, reject, or override AI-generated findings.

### Rationale

Human judgment is required where AI results are incomplete, uncertain, or operationally significant.

### Priority

Critical

### Verification

Functional Test

---

## REQ-DI-0115 — Damage Case Creation

### Title

Damage Case Creation

### Statement

Damage Intelligence SHALL create a structured damage case when damage requires review, approval, repair routing, or dispute support.

### Rationale

Damage cases provide the operational object for managing damage decisions.

### Priority

Critical

### Verification

Functional Test

---

## REQ-DI-0116 — Damage Case Lifecycle

### Title

Damage Case Lifecycle

### Statement

Damage Intelligence SHALL support a damage case lifecycle.

The lifecycle SHOULD include:

- Draft
- Detected
- In Review
- Confirmed
- Rejected
- Routed to Maintenance
- Closed
- Archived

### Rationale

A defined lifecycle enables consistent operational handling.

### Priority

High

### Verification

Workflow Review

---

## REQ-DI-0117 — Maintenance Routing

### Title

Maintenance Routing

### Statement

Damage Intelligence SHALL support routing confirmed repair-required damage to GCU365 Maintenance.

### Rationale

Confirmed damage may require repair planning, technician assignment, parts, and work order execution.

### Priority

Critical

### Verification

Integration Test

---

## REQ-DI-0118 — CROMS Rental Context

### Title

CROMS Rental Context

### Statement

Damage Intelligence SHALL consume rental context from GCU365 CROMS when inspections are performed during vehicle check-out or check-in.

### Rationale

Inspection evidence must be linked to the correct rental lifecycle.

### Priority

Critical

### Verification

Integration Test

---

## REQ-DI-0119 — Vehicle Context

### Title

Vehicle Context

### Statement

Damage Intelligence SHALL consume vehicle master context from the authoritative vehicle source.

### Rationale

Damage records must be linked to the correct vehicle and vehicle history.

### Priority

Critical

### Verification

Integration Test

---

## REQ-DI-0120 — Customer Dispute Evidence

### Title

Customer Dispute Evidence

### Statement

Damage Intelligence SHALL preserve inspection and review evidence in a form suitable for customer dispute review.

### Rationale

Rental operators require trustworthy evidence for dispute resolution.

### Priority

High

### Verification

Report Review, Audit Review

---

## REQ-DI-0121 — Damage Report Generation

### Title

Damage Report Generation

### Statement

Damage Intelligence SHALL generate structured damage reports containing inspection evidence, AI findings, human review decisions, and timestamps.

### Rationale

Reports are required for operational review, maintenance routing, customer communication, and audit.

### Priority

High

### Verification

Report Test

---

## REQ-DI-0122 — Audit Trail

### Title

Audit Trail

### Statement

Damage Intelligence SHALL record an audit trail for inspection capture, AI analysis, human review, damage decisions, and integration events.

### Rationale

Auditability supports accountability, compliance, and dispute handling.

### Priority

Critical

### Verification

Audit Review

---

## REQ-DI-0123 — Role-Based Access

### Title

Role-Based Access

### Statement

Damage Intelligence SHALL enforce role-based access for inspection, review, approval, reporting, and administrative operations.

### Rationale

Different users require different permissions based on operational responsibility.

### Priority

Critical

### Verification

Security Test

---

## REQ-DI-0124 — Privacy Protection

### Title

Privacy Protection

### Statement

Damage Intelligence SHALL protect personal data, vehicle images, location metadata, and customer-related inspection evidence according to applicable privacy requirements.

### Rationale

Inspection evidence may contain sensitive or personally identifiable information.

### Priority

Critical

### Verification

Security Review

---

## REQ-DI-0125 — Secure Image Storage

### Title

Secure Image Storage

### Statement

Damage Intelligence SHALL store inspection images securely with controlled access.

### Rationale

Vehicle images are operational evidence and must be protected from unauthorized access.

### Priority

Critical

### Verification

Security Test

---

## REQ-DI-0126 — Offline Capture Support

### Title

Offline Capture Support

### Statement

Damage Intelligence SHOULD support offline or intermittent-connectivity capture workflows where operationally required.

### Rationale

Vehicle inspections may occur in parking lots, branches, workshops, or locations with weak connectivity.

### Priority

Medium

### Verification

Mobile Workflow Test

---

## REQ-DI-0127 — Evidence Integrity

### Title

Evidence Integrity

### Statement

Damage Intelligence SHALL protect inspection evidence from unauthorized alteration.

### Rationale

Evidence integrity is essential for trust, audit, and dispute resolution.

### Priority

Critical

### Verification

Audit Review, Security Review

---

## REQ-DI-0128 — AI Explainability

### Title

AI Explainability

### Statement

Damage Intelligence SHOULD provide explanations for AI findings where practical, including damage type, location, confidence, and evidence reference.

### Rationale

Explainable AI improves user trust and review quality.

### Priority

High

### Verification

AI Review

---

## REQ-DI-0129 — AI Uncertainty Handling

### Title

AI Uncertainty Handling

### Statement

Damage Intelligence SHALL identify uncertain AI findings and route them for human review.

### Rationale

Uncertain AI output must not silently drive operational decisions.

### Priority

Critical

### Verification

AI Workflow Test

---

## REQ-DI-0130 — Repair Estimate Support

### Title

Repair Estimate Support

### Statement

Damage Intelligence MAY provide repair cost or repair effort estimates based on damage type, severity, and affected area.

### Rationale

Repair estimation supports maintenance planning and operational decision-making.

### Priority

Medium

### Verification

Functional Review

---

## REQ-DI-0131 — Damage History

### Title

Damage History

### Statement

Damage Intelligence SHALL maintain damage history for each vehicle.

### Rationale

Vehicle-level damage history is required for comparison, maintenance, resale, dispute resolution, and reporting.

### Priority

Critical

### Verification

Data Review

---

## REQ-DI-0132 — Reporting and Analytics

### Title

Reporting and Analytics

### Statement

Damage Intelligence SHALL support operational reporting on inspections, damage cases, review outcomes, and damage trends.

### Rationale

Management requires visibility into damage patterns, branch performance, and operational quality.

### Priority

High

### Verification

Report Review

---

## REQ-DI-0133 — Multi-Tenant Isolation

### Title

Multi-Tenant Isolation

### Statement

Damage Intelligence SHALL preserve tenant isolation for inspection evidence, damage records, users, and reports.

### Rationale

The platform may serve multiple organizations and must prevent cross-tenant data exposure.

### Priority

Critical

### Verification

Security Review

---

## REQ-DI-0134 — API-First Integration

### Title

API-First Integration

### Statement

Damage Intelligence SHALL expose integration capabilities through approved APIs and events.

### Rationale

CROMS, Maintenance, and future systems require governed access to Damage Intelligence capabilities.

### Priority

High

### Verification

API Review

---

## REQ-DI-0135 — No Final AI Liability Decision

### Title

No Final AI Liability Decision

### Statement

Damage Intelligence SHALL NOT make final customer liability, legal, or financial charge decisions without human approval.

### Rationale

AI supports operational decisions but accountability remains with authorized human users.

### Priority

Critical

### Verification

Governance Review

---

# Business Rules

The following business rules are introduced by this document.

## BR-DI-0001 — Inspection Evidence Required

A vehicle return damage decision SHALL NOT be finalized without inspection evidence.

---

## BR-DI-0002 — Human Review Required for Chargeable Damage

Potentially chargeable damage SHALL require human review before financial action.

---

## BR-DI-0003 — AI Findings Are Advisory

AI-generated damage findings SHALL be treated as advisory until confirmed by an authorized reviewer.

---

## BR-DI-0004 — Historical Comparison Preferred

Where previous inspection evidence exists, the system SHALL compare current evidence against historical evidence before classifying damage as new.

---

## BR-DI-0005 — Evidence Must Be Immutable After Approval

Approved inspection evidence SHALL NOT be modified without creating a new version or audit record.

---

# Non-Functional Business Requirements

## Availability

Damage Intelligence SHOULD be available during branch operating hours and workshop operating hours.

## Performance

AI analysis SHOULD return results within an operationally acceptable timeframe.

Specific thresholds SHALL be defined in later performance specifications.

## Usability

The inspection workflow SHALL be simple enough for rental agents and inspectors to complete with minimal training.

## Accessibility

User interfaces SHOULD follow applicable accessibility guidance.

## Localization

Damage Intelligence SHOULD support Arabic and English user-facing content where required by GCU365 products.

## Auditability

All operationally significant actions SHALL be auditable.

---

# Reporting Requirements

Damage Intelligence SHOULD support the following reports:

- Inspection Completion Report
- Damage Case Report
- New Damage Report
- Damage Review Report
- Branch Damage Trend Report
- Vehicle Damage History Report
- AI Detection Quality Report
- Human Override Report
- Maintenance Routing Report
- Dispute Evidence Report

Detailed report specifications SHALL be defined separately.

---

# Integration Requirements

## CROMS Integration Requirements

Damage Intelligence SHALL integrate with CROMS for:

- Vehicle context
- Rental context
- Check-out inspection initiation
- Check-in inspection initiation
- Damage result return
- Dispute evidence retrieval
- Vehicle availability impact

## Maintenance Integration Requirements

Damage Intelligence SHALL integrate with Maintenance for:

- Repair recommendation
- Work order creation request
- Damage evidence transfer
- Repair status feedback
- Quality inspection comparison
- Damage repair closure

---

# Data Requirements

Damage Intelligence SHALL manage or reference the following information objects:

- Inspection Session
- Inspection Photo
- Damage Finding
- Damage Case
- Damage Comparison
- AI Assessment
- Human Review Decision
- Damage Report
- Vehicle Damage History
- Damage Evidence Audit Record

Detailed data model SHALL be defined in:

```text
DI-0012-Domain-Model.md
DI-0014-Database-Model.md
