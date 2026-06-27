---
id: DI-0006
title: Damage Intelligence Damage Comparison
version: 1.0.0
document_type: Product Specification
document_class: AI Comparison Specification
status: Draft
classification: Internal
owner: Riyadah Technology
reviewers:
  - Chief Enterprise Architect
  - Product Owner
  - AI Engineering Lead
  - Operations Lead
  - Maintenance Lead
  - Security Lead
approvers: []
created: 2026-06-27
updated: 2026-06-27
authoritative: true
ai_consumable: true
related:
  - DI-0001
  - DI-0002
  - DI-0003
  - DI-0004
  - DI-0005
  - RA-0001
  - RA-0002
  - GEES-0005
  - GEES-0007
  - PLATFORM-0005
---

# Damage Intelligence Damage Comparison

## Executive Summary

This document defines the Damage Comparison capability within Damage Intelligence.

Damage Comparison is responsible for comparing current vehicle inspection evidence against historical vehicle condition evidence to determine whether visible damage is likely new, pre-existing, changed, repaired, or uncertain.

Damage Comparison is one of the most important capabilities in Damage Intelligence because it supports vehicle rental check-in/check-out decisions, customer dispute handling, maintenance routing, and vehicle damage history.

Damage Comparison SHALL be evidence-based, auditable, explainable where practical, and subject to human review before operationally significant, financial, customer-impacting, or legal decisions are finalized.

---

# Purpose

The purpose of this document is to define the required business and technical behavior for comparing vehicle damage evidence across inspections.

This specification SHALL guide:

- Damage comparison logic
- Historical inspection lookup
- AI comparison behavior
- Damage delta classification
- Damage case creation
- Human review workflow
- CROMS integration
- Maintenance integration
- API specification
- Data model specification
- Test scenarios
- Acceptance criteria
- Audit design

---

# Scope

## In Scope

Damage Comparison includes:

- Comparing current inspection evidence against prior inspection evidence.
- Matching current and previous vehicle capture positions.
- Matching detected damage findings across inspections.
- Identifying likely new damage.
- Identifying likely pre-existing damage.
- Identifying changed or worsened damage.
- Identifying repaired damage.
- Identifying uncertain comparison outcomes.
- Producing structured comparison results.
- Supporting human review.
- Supporting damage case decisions.
- Supporting customer dispute evidence.
- Supporting maintenance routing.
- Preserving comparison audit history.

## Out of Scope

The following are out of scope for this specification:

- Final customer liability decision.
- Final legal responsibility decision.
- Final billing or charge decision.
- Full repair work order lifecycle.
- Full insurance claim automation.
- Full AI model training lifecycle.
- 3D reconstruction.
- Telematics accident detection.
- Automated fraud accusation.
- Autonomous customer dispute resolution.

---

# Comparison Principles

Damage Comparison SHALL follow these principles:

1. Evidence-Based Comparison
2. Historical Context Awareness
3. Human Accountability
4. Explainability Where Practical
5. Uncertainty Disclosure
6. Complete Auditability
7. Preservation of Original Evidence
8. Traceability
9. Privacy by Design
10. Security by Design

Damage Comparison SHALL NOT silently convert uncertain evidence into a final conclusion.

---

# Business Objective

The primary business objective of Damage Comparison is to answer the following question:

> Is the damage observed in the current inspection new, pre-existing, changed, repaired, or uncertain when compared against available historical evidence?

This answer SHALL support, but SHALL NOT independently finalize:

- Rental return decisions
- Customer dispute review
- Maintenance routing
- Repair planning
- Operational reporting
- Damage history management

---

# Comparison Contexts

Damage Comparison SHALL support the following comparison contexts.

| Context | Description |
|---------|-------------|
| Check-In vs Check-Out | Compare return inspection to rental start baseline |
| Current Inspection vs Last Inspection | Compare current evidence to most recent prior inspection |
| Current Inspection vs Damage History | Compare current evidence to approved damage records |
| Post-Repair vs Pre-Repair | Compare post-repair evidence to pre-repair damage evidence |
| Ad Hoc Comparison | Compare two selected inspections manually |

Version 1 SHALL prioritize Check-In vs Check-Out comparison.

---

# Comparison Inputs

Damage Comparison SHALL consume the following inputs where available.

## Current Inspection Inputs

- Current Inspection Session ID
- Current Inspection Type
- Current Inspection Photos
- Current AI Damage Findings
- Current Image Quality Results
- Current Capture Position Metadata
- Current Inspection Timestamp
- Current Vehicle Context
- Current Rental Context where applicable

## Historical Inputs

- Prior Inspection Session ID
- Prior Inspection Photos
- Prior AI Damage Findings
- Prior Human-Approved Damage Findings
- Prior Damage Cases
- Prior Damage History
- Prior Capture Position Metadata
- Prior Inspection Timestamp
- Prior Repair History where available

## Context Inputs

- Vehicle ID
- Rental Agreement ID where applicable
- Branch or location context
- Vehicle damage history
- Maintenance history where available
- Repair completion status where available
- User permissions

---

# Comparison Outputs

Damage Comparison SHALL produce structured comparison outputs.

Each comparison result SHOULD include:

- Comparison ID
- Current Inspection Session ID
- Baseline Inspection Session ID where available
- Current Finding ID
- Historical Finding ID where matched
- Damage Type
- Vehicle Area
- Comparison Outcome
- Confidence Score
- Evidence References
- Explanation
- Review Recommendation
- Created Timestamp
- AI Engine or Comparison Engine Identifier
- Human Review Status

---

# Comparison Outcome Types

Damage Comparison SHALL classify outcomes using the following standard values.

| Outcome | Meaning |
|---------|---------|
| New | Damage appears in current evidence and is not supported by prior evidence |
| PreExisting | Damage appears to match damage previously recorded |
| Changed | Previously recorded damage appears worsened, expanded, or materially changed |
| Repaired | Previously recorded damage appears no longer visible or repaired |
| Uncertain | Evidence is insufficient or inconclusive |
| NotComparable | Comparison cannot be performed due to missing or incompatible evidence |

---

# Standard Comparison Output Example

Comparison output SHOULD be representable in structured form similar to:

~~~json
{
  "comparisonId": "CMP-DI-000001",
  "currentInspectionSessionId": "INS-DI-000045",
  "baselineInspectionSessionId": "INS-DI-000022",
  "currentFindingId": "AIF-DI-000188",
  "historicalFindingId": null,
  "damageType": "Dent",
  "vehicleArea": "Left Rear Door",
  "comparisonOutcome": "New",
  "confidenceScore": 0.84,
  "reviewRecommendation": "HumanReviewRequired",
  "evidence": {
    "currentImages": ["IMG-DI-01012"],
    "historicalImages": ["IMG-DI-00431"],
    "notes": "No matching dent is visible in the baseline left-side image."
  },
  "explanation": "A dent is visible on the left rear door in the current inspection. The comparable baseline image does not show the same damage.",
  "createdAt": "2026-06-27T00:00:00Z"
}
~~~

This example is illustrative. Final schema SHALL be defined in later API and data specifications.

---

# Comparison Workflow

Damage Comparison SHOULD follow this workflow.

```text
Current Inspection Submitted
        ↓
Current AI Findings Loaded
        ↓
Historical Evidence Retrieved
        ↓
Capture Positions Matched
        ↓
Damage Findings Compared
        ↓
Outcome Classified
        ↓
Confidence Calculated
        ↓
Review Recommendation Generated
        ↓
Comparison Result Stored
        ↓
Human Review Queue Updated
```

---

# Historical Evidence Selection

Damage Comparison SHALL select historical evidence using a governed selection strategy.

## Preferred Historical Evidence

The preferred comparison baseline for rental return SHALL be:

1. The check-out inspection for the same rental agreement.
2. If unavailable, the most recent approved inspection before rental start.
3. If unavailable, approved vehicle damage history.
4. If unavailable, no baseline is available.

## Rules

- The selected baseline SHALL be recorded.
- The reason for selecting the baseline SHALL be recorded.
- The absence of baseline evidence SHALL be explicitly recorded.
- The system SHALL NOT classify damage as confirmed new solely because no historical evidence exists.

---

# Capture Position Matching

Comparison accuracy depends on comparable views.

Damage Comparison SHOULD match current and historical images using:

- Capture Position ID
- Vehicle side or area
- Camera angle
- Timestamp
- Vehicle area detection
- Image metadata
- AI-assisted similarity where available

If capture positions cannot be reliably matched, comparison outcome SHOULD be set to `Uncertain` or `NotComparable`.

---

# Damage Finding Matching

Damage Comparison SHOULD match damage findings using:

- Damage type
- Vehicle area
- Region or bounding box
- Segmentation mask where available
- Visual similarity
- Historical approved damage record
- Human reviewer decision
- Severity
- Damage dimensions where available

The matching algorithm MAY evolve over time.

---

# Damage Delta Classification

Damage Comparison SHALL classify the delta between current and historical evidence.

## New Damage

Damage SHOULD be classified as `New` when:

- Current evidence shows visible damage.
- Comparable historical evidence does not show the same damage.
- Image quality is sufficient.
- Capture positions are sufficiently comparable.
- Confidence meets configured threshold or human review confirms it.

## Pre-Existing Damage

Damage SHOULD be classified as `PreExisting` when:

- Current damage visually matches previously recorded damage.
- Vehicle area and damage type are consistent.
- Historical evidence supports the match.

## Changed Damage

Damage SHOULD be classified as `Changed` when:

- Existing damage appears larger.
- Existing damage appears more severe.
- Existing damage appears in the same area but materially different.
- Prior damage has expanded or worsened.

## Repaired Damage

Damage SHOULD be classified as `Repaired` when:

- Historical damage is recorded.
- Current comparable evidence no longer shows the same damage.
- Repair completion context exists where available.

## Uncertain

Damage SHOULD be classified as `Uncertain` when:

- Current image quality is poor.
- Historical evidence is missing.
- Capture angles are not comparable.
- Damage visibility is unclear.
- AI confidence is low.
- Findings conflict.
- Human review is required.

## Not Comparable

Damage SHOULD be classified as `NotComparable` when:

- No comparable historical image exists.
- Required vehicle area is missing.
- Current or historical evidence is unavailable.
- Images are technically unusable.

---

# Confidence Scoring

Damage Comparison SHOULD assign confidence scores to comparison results.

Confidence scoring SHOULD consider:

- Current image quality
- Historical image quality
- Capture position match quality
- Damage type certainty
- Vehicle area certainty
- Visual similarity
- Historical finding quality
- Human-approved prior damage records
- AI detection confidence
- Time gap between inspections

Confidence thresholds SHALL be configurable.

---

# Confidence Levels

The system MAY use the following confidence categories.

| Level | Suggested Range | Meaning |
|-------|-----------------|---------|
| High | 0.80–1.00 | Comparison is likely reliable |
| Medium | 0.50–0.79 | Review recommended |
| Low | 0.00–0.49 | Comparison is uncertain |

Operational thresholds SHALL be defined through configuration and validation.

---

# Review Recommendation

Damage Comparison SHALL produce a review recommendation.

Possible recommendations:

| Recommendation | Meaning |
|----------------|---------|
| NoReviewRequired | Low-risk finding that may not require manual review |
| HumanReviewRequired | Human review is required |
| EscalationRequired | Higher-level review is required |
| AdditionalEvidenceRequired | More evidence is needed |
| MaintenanceReviewRequired | Maintenance should review damage |

Business policy MAY require review even when AI confidence is high.

---

# Human Review Requirements

Human review SHALL be required when:

- Damage is potentially new.
- Damage may be chargeable.
- Damage may require maintenance.
- Comparison confidence is below configured threshold.
- Historical evidence is incomplete.
- Damage severity is Moderate or higher.
- Customer dispute is possible.
- Business policy requires review.

Human reviewers SHALL be able to:

- Confirm outcome.
- Change outcome.
- Reject finding.
- Request additional evidence.
- Escalate case.
- Add review notes.

---

# Missing Historical Evidence

When historical evidence is missing:

- The system SHALL continue current inspection processing.
- The system SHALL mark comparison as `NotComparable` or `Uncertain`.
- The system SHALL explain that historical comparison could not be completed.
- The system SHALL NOT treat damage as confirmed new solely due to missing historical evidence.
- Human review MAY be required.

---

# Poor Evidence Handling

When current or historical evidence quality is poor:

- The system SHOULD reduce confidence.
- The system SHOULD request recapture if operationally possible.
- The system SHOULD route findings to human review.
- The system SHALL record image quality limitations.

---

# Damage Comparison and Damage Case Creation

Damage Comparison MAY create or update a Damage Case when:

- Damage is classified as New.
- Damage is classified as Changed.
- Damage is classified as Uncertain and requires review.
- Damage may require maintenance.
- Damage may be customer-impacting.
- Business policy requires case creation.

Damage Case SHALL preserve the comparison result and evidence references.

---

# Damage Comparison and CROMS

Damage Comparison SHALL support CROMS by providing:

- Check-in comparison summary.
- New damage candidate list.
- Existing damage list.
- Uncertain damage list.
- Evidence report reference.
- Review status.
- Damage case status.
- Maintenance routing status where applicable.

CROMS SHALL NOT directly decide damage classification without Damage Intelligence results when Damage Intelligence is enabled.

---

# Damage Comparison and Maintenance

Damage Comparison SHALL support Maintenance by providing:

- Confirmed damage details.
- Damage severity.
- Affected vehicle area.
- Evidence package.
- Repair recommendation where available.
- Historical comparison summary.
- Review decision.

Maintenance SHALL own repair execution after damage is routed.

---

# Damage Comparison and Customer Disputes

Damage Comparison SHALL support dispute handling by preserving:

- Current evidence.
- Historical evidence.
- Comparison outcome.
- Reviewer decision.
- AI confidence where available.
- Explanation.
- Audit history.

Customer-facing reports SHALL distinguish between:

- AI-generated finding.
- Human-reviewed decision.
- Approved final operational conclusion.

---

# Audit Requirements

Damage Comparison SHALL audit:

- Comparison request.
- Baseline selection.
- Historical evidence retrieval.
- Current evidence used.
- AI comparison result.
- Confidence score.
- Comparison outcome.
- Review recommendation.
- Human review decision.
- Outcome change.
- Damage case creation.
- Maintenance routing.
- Report generation.

Audit records SHALL include:

- Timestamp
- User or system actor
- Action
- Object reference
- Previous state where applicable
- New state where applicable
- Reason or explanation where applicable

---

# Security and Privacy

Damage Comparison SHALL comply with GEES security and privacy standards.

The system SHALL:

- Respect tenant boundaries.
- Enforce authorization.
- Protect image access.
- Protect customer-related evidence.
- Avoid exposing unauthorized historical records.
- Audit access to comparison evidence.
- Use secure storage and secure transmission.

---

# Performance Expectations

Damage Comparison SHOULD complete within operationally acceptable time.

Performance thresholds SHALL be defined in later non-functional requirements.

The system SHOULD support asynchronous processing for AI-heavy comparison tasks.

---

# Operational KPIs

Damage Comparison SHOULD track:

- Number of comparisons performed.
- Percentage of comparisons classified as New.
- Percentage classified as PreExisting.
- Percentage classified as Changed.
- Percentage classified as Repaired.
- Percentage classified as Uncertain.
- Percentage classified as NotComparable.
- Average comparison processing time.
- Human override rate.
- Dispute rate after comparison.
- Maintenance routing rate.
- False positive rate.
- False negative rate.

---

# Comparison Quality Feedback

The system SHOULD support feedback from reviewers.

Feedback MAY include:

- Correct outcome
- Incorrect outcome
- Missed damage
- False match
- Poor evidence
- Wrong vehicle area
- Wrong damage type
- Wrong severity

Feedback SHALL be usable for AI quality improvement.

---

# Exceptions

## No Prior Inspection

Outcome SHALL be `NotComparable` or `Uncertain`.

## Prior Inspection Exists but Required View Missing

Outcome SHOULD be `NotComparable`.

## Current Image Failed Quality

Outcome SHOULD be `Uncertain` and recapture SHOULD be requested.

## AI Service Failure

Manual review SHALL remain possible.

## Conflicting Evidence

Outcome SHOULD be `Uncertain` and escalated.

## Vehicle Mismatch

Comparison SHALL stop and generate an exception event.

---

# Normative Requirements

## Requirement

ID: REQ-DI-0500

Title:
Damage Comparison

Statement:
Damage Intelligence SHALL compare current inspection evidence against historical inspection evidence where available.

Priority:
Critical

Verification:
Comparison Test

---

## Requirement

ID: REQ-DI-0501

Title:
Baseline Selection

Statement:
Damage Comparison SHALL record which historical inspection or evidence set was selected as the comparison baseline.

Priority:
Critical

Verification:
Audit Review

---

## Requirement

ID: REQ-DI-0502

Title:
Comparison Outcome Classification

Statement:
Damage Comparison SHALL classify comparison results using standard outcome values.

Priority:
Critical

Verification:
Functional Test

---

## Requirement

ID: REQ-DI-0503

Title:
New Damage Candidate Identification

Statement:
Damage Comparison SHALL identify candidate new damage where current evidence differs from comparable historical evidence.

Priority:
Critical

Verification:
Comparison Test

---

## Requirement

ID: REQ-DI-0504

Title:
Pre-Existing Damage Matching

Statement:
Damage Comparison SHALL identify likely pre-existing damage where current evidence matches prior recorded damage.

Priority:
Critical

Verification:
Comparison Test

---

## Requirement

ID: REQ-DI-0505

Title:
Changed Damage Identification

Statement:
Damage Comparison SHOULD identify existing damage that appears materially changed or worsened.

Priority:
High

Verification:
Comparison Review

---

## Requirement

ID: REQ-DI-0506

Title:
Repaired Damage Identification

Statement:
Damage Comparison SHOULD identify previously recorded damage that appears repaired where evidence supports it.

Priority:
Medium

Verification:
Comparison Review

---

## Requirement

ID: REQ-DI-0507

Title:
Uncertainty Disclosure

Statement:
Damage Comparison SHALL explicitly classify inconclusive results as Uncertain or NotComparable.

Priority:
Critical

Verification:
AI Governance Review

---

## Requirement

ID: REQ-DI-0508

Title:
No New Damage Without Evidence

Statement:
Damage Comparison SHALL NOT classify damage as confirmed new solely because historical evidence is unavailable.

Priority:
Critical

Verification:
Governance Review

---

## Requirement

ID: REQ-DI-0509

Title:
Comparison Confidence

Statement:
Damage Comparison SHOULD provide confidence scores for comparison outcomes.

Priority:
High

Verification:
AI Review

---

## Requirement

ID: REQ-DI-0510

Title:
Human Review Routing

Statement:
Damage Comparison SHALL route significant, chargeable, uncertain, or policy-required findings for human review.

Priority:
Critical

Verification:
Workflow Test

---

## Requirement

ID: REQ-DI-0511

Title:
Comparison Audit Trail

Statement:
Damage Comparison SHALL preserve an audit trail of baseline selection, evidence used, comparison outcome, confidence, and human decisions.

Priority:
Critical

Verification:
Audit Review

---

## Requirement

ID: REQ-DI-0512

Title:
Comparison Evidence References

Statement:
Damage Comparison SHALL reference the current and historical evidence used to support each comparison result.

Priority:
Critical

Verification:
Data Review

---

## Requirement

ID: REQ-DI-0513

Title:
CROMS Comparison Summary

Statement:
Damage Comparison SHALL provide CROMS with comparison summaries for check-in workflows where applicable.

Priority:
High

Verification:
Integration Test

---

## Requirement

ID: REQ-DI-0514

Title:
Maintenance Comparison Context

Statement:
Damage Comparison SHALL provide Maintenance with comparison context when confirmed damage is routed for repair review.

Priority:
High

Verification:
Integration Test

---

## Requirement

ID: REQ-DI-0515

Title:
Reviewer Override

Statement:
Authorized reviewers SHALL be able to override or correct comparison outcomes.

Priority:
Critical

Verification:
Review Workflow Test

---

## Requirement

ID: REQ-DI-0516

Title:
Comparison Feedback Loop

Statement:
Damage Comparison SHOULD capture reviewer feedback to improve future comparison quality.

Priority:
Medium

Verification:
AI Quality Review

---

## Requirement

ID: REQ-DI-0517

Title:
Tenant Isolation

Statement:
Damage Comparison SHALL enforce tenant isolation when retrieving historical evidence.

Priority:
Critical

Verification:
Security Review

---

## Requirement

ID: REQ-DI-0518

Title:
Secure Evidence Access

Statement:
Damage Comparison SHALL access current and historical evidence only through authorized mechanisms.

Priority:
Critical

Verification:
Security Test

---

# Business Rules

## BR-DI-0100 — Evidence Required for Comparison

Damage Comparison SHALL use identifiable current and historical evidence when generating comparison outcomes.

---

## BR-DI-0101 — Missing History Does Not Prove New Damage

If historical evidence is missing, the system SHALL NOT automatically conclude that current damage is new.

---

## BR-DI-0102 — Chargeable Damage Requires Human Review

Damage that may result in customer charging SHALL require human review.

---

## BR-DI-0103 — Comparison Outcome Must Be Auditable

Every comparison outcome SHALL preserve evidence references and audit history.

---

## BR-DI-0104 — Reviewer Decision Supersedes AI Suggestion

A human reviewer decision SHALL supersede advisory AI comparison output where the reviewer is authorized.

---

# AI Implementation Contract

AI development agents SHALL:

- Treat this document as the authoritative specification for Damage Comparison.
- Preserve all requirement IDs.
- Preserve all comparison outcome types.
- Preserve the rule that missing historical evidence does not prove new damage.
- Preserve human review requirements.
- Preserve auditability and evidence references.
- Not convert AI comparison output into final liability or financial decisions.
- Generate future APIs, schemas, workflows, tests, and prompts consistent with this specification.
- Raise ambiguity when comparison baseline, evidence quality, or ownership is unclear.

---

# References

- DI-0001 – Damage Intelligence Product Vision
- DI-0002 – Damage Intelligence Business Requirements
- DI-0004 – Damage Intelligence Inspection Workflow
- DI-0005 – AI Damage Detection
- DI-0008 – Damage Taxonomy
- DI-0009 – Severity Assessment
- RA-0001 – Enterprise Context Architecture
- RA-0002 – Domain-Driven Design Architecture
- GEES-0005 – AI Engineering Standard
- GEES-0007 – Enterprise Security Standard
- PLATFORM-0005 – GEES Core and Application Architecture

---

# Revision History

| Version | Date | Description |
|----------|------|-------------|
| 1.0.0 | 2026-06-27 | Initial Damage Intelligence Damage Comparison Specification |
