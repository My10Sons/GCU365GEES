---
id: DI-0009
title: Damage Intelligence Severity Assessment
version: 1.0.0
document_type: Product Specification
document_class: Severity Assessment Specification
status: Draft
classification: Internal
owner: Riyadah Technology
reviewers:
  - Chief Enterprise Architect
  - Product Owner
  - AI Engineering Lead
  - Maintenance Lead
  - Operations Lead
  - QA Lead
approvers: []
created: 2026-06-27
updated: 2026-06-27
authoritative: true
ai_consumable: true
related:
  - DI-0001
  - DI-0002
  - DI-0005
  - DI-0006
  - DI-0007
  - DI-0008
  - RA-0001
  - RA-0002
  - GEES-0005
  - GEES-0007
  - PLATFORM-0005
---

# Damage Intelligence Severity Assessment

## Executive Summary

This document defines the severity assessment framework used by Damage Intelligence.

Severity Assessment classifies detected or reported vehicle damage according to operational impact, visible extent, safety relevance, repair urgency, customer impact, and maintenance relevance.

Severity is used to support:

- Human review prioritization.
- Damage case workflow.
- Maintenance routing.
- Repair estimation.
- Customer dispute evidence.
- Reporting and analytics.
- AI model evaluation.
- Operational decision-making.

Severity assessment SHALL support AI-assisted recommendations but SHALL remain reviewable and adjustable by authorized users.

AI-generated severity is advisory until confirmed by an authorized reviewer where operational, financial, legal, or customer-impacting decisions are involved.

---

# Purpose

The purpose of this document is to define a governed severity model for vehicle damage findings.

This specification SHALL guide:

- AI severity suggestions.
- Human review decisions.
- Damage case prioritization.
- Maintenance routing.
- Repair estimate support.
- Reporting.
- API schemas.
- Database schemas.
- UI labels.
- Test cases.
- Acceptance criteria.

---

# Scope

## In Scope

This specification covers:

- Severity levels.
- Severity assessment dimensions.
- AI severity suggestion rules.
- Human severity confirmation.
- Severity override.
- Maintenance routing implications.
- Review priority implications.
- Safety relevance.
- Repair relevance.
- Reporting and analytics implications.
- Audit requirements.
- Severity-related business rules.

## Out of Scope

This specification does not define:

- Final repair cost.
- Final customer liability.
- Final customer charge amount.
- Insurance claim value.
- Manufacturer-specific repair procedure.
- Workshop labor codes.
- Full repair estimation model.
- Mechanical diagnostic severity unrelated to visible inspection evidence.

Repair cost estimation SHALL be defined separately in:

```text
DI-0010-Repair-Cost-Estimation.md
```

---

# Severity Assessment Principles

Severity Assessment SHALL follow these principles:

1. Evidence-Based Assessment
2. Human Accountability
3. Safety Awareness
4. Operational Relevance
5. Repair Relevance
6. Explainability
7. Auditability
8. Consistency
9. Configurability
10. Traceability

Severity SHALL NOT be treated as a final financial decision.

---

# Severity Levels

Damage Intelligence SHALL support the following standard severity levels.

| Code | Severity | Description |
|------|----------|-------------|
| MINOR | Minor | Cosmetic or low-impact damage with limited operational effect |
| MODERATE | Moderate | Noticeable damage that may require repair or review |
| MAJOR | Major | Significant damage likely requiring repair before release or further use |
| CRITICAL | Critical | Safety-impacting or severe damage requiring immediate escalation |
| UNKNOWN | Unknown | Severity cannot be reliably determined |

---

# Severity Level Definitions

## MINOR

Minor damage is visible but generally low impact.

Examples MAY include:

- Small scratch.
- Small paint chip.
- Light scuff.
- Minor wheel rash.
- Small cosmetic mark.
- Minor interior stain.

Typical handling:

- Record evidence.
- Human review MAY be required depending on policy.
- Maintenance routing MAY not be required.
- Monitoring MAY be sufficient.

---

## MODERATE

Moderate damage is visible and may require repair, review, or customer dispute handling.

Examples MAY include:

- Noticeable scratch.
- Medium dent.
- Cracked trim.
- Noticeable bumper scuff.
- Medium wheel rash.
- Interior tear or burn mark.

Typical handling:

- Human review SHOULD be required.
- Damage case SHOULD be created.
- Maintenance review MAY be required.
- Customer dispute evidence SHOULD be preserved.

---

## MAJOR

Major damage is significant and likely requires repair before vehicle release depending on operational policy.

Examples MAY include:

- Large dent.
- Broken bumper.
- Broken light.
- Significant glass crack.
- Multi-panel damage.
- Severe wheel damage.
- Major interior damage.

Typical handling:

- Human review SHALL be required.
- Damage case SHALL be created.
- Maintenance routing SHOULD be required.
- Vehicle availability MAY be affected.
- Supervisor review MAY be required.

---

## CRITICAL

Critical damage is severe, safety-impacting, or operationally urgent.

Examples MAY include:

- Broken windshield affecting visibility.
- Tire bulge or severe tire damage.
- Broken light affecting roadworthiness.
- Fluid leak.
- Severe structural deformation.
- Damage that may make the vehicle unsafe.
- Missing critical component.

Typical handling:

- Immediate escalation SHALL be required.
- Maintenance routing SHALL be required.
- Vehicle SHOULD be prevented from release until reviewed.
- Supervisor or safety review SHOULD be required.
- Customer handover SHOULD be blocked where policy requires.

---

## UNKNOWN

Unknown severity means the system cannot determine severity reliably.

Reasons MAY include:

- Poor image quality.
- Incomplete evidence.
- Obstruction.
- Low AI confidence.
- Unclear vehicle area.
- Damage type uncertain.
- Conflicting evidence.

Typical handling:

- Human review SHALL be required.
- Additional evidence MAY be requested.
- Severity SHALL NOT be finalized automatically.

---

# Severity Assessment Dimensions

Severity assessment SHOULD consider multiple dimensions.

## Visible Extent

Visible extent refers to the size, spread, and visual scope of the damage.

Factors:

- Damage size.
- Damage length.
- Damage spread.
- Number of affected panels.
- Visibility.

---

## Damage Type

Some damage types are inherently more serious than others.

Examples:

- Tire bulge may be critical.
- Broken light may be major or critical.
- Light scratch may be minor.
- Fluid leak may be critical.
- Glass crack may be moderate, major, or critical depending on location and extent.

---

## Vehicle Area

Vehicle area influences severity.

Examples:

- Windshield damage may be more severe than similar-sized cosmetic body damage.
- Tire damage may be more severe than wheel cosmetic rash.
- Headlight or tail light damage may affect roadworthiness.
- Bumper scuff may be cosmetic unless structural or severe.

---

## Safety Relevance

Safety relevance considers whether damage could affect safe vehicle use.

Safety-relevant areas MAY include:

- Tires
- Wheels
- Lights
- Windshield
- Mirrors
- Braking-related visible evidence
- Fluid leaks
- Structural or severe body deformation

---

## Repair Urgency

Repair urgency considers whether the vehicle can remain operational before repair.

Possible urgency levels:

| Code | Meaning |
|------|---------|
| NO_REPAIR_REQUIRED | No repair required |
| MONITOR | Monitor condition |
| NEXT_SERVICE | Repair at next service opportunity |
| REPAIR_BEFORE_RELEASE | Repair before vehicle is released |
| IMMEDIATE_REVIEW | Immediate safety or supervisor review required |

---

## Customer Impact

Customer impact considers whether damage may create disputes, claims, complaints, or customer charges.

Damage with potential customer impact SHOULD require human review.

---

## Operational Impact

Operational impact considers whether the damage affects:

- Vehicle availability.
- Rental readiness.
- Workshop routing.
- Customer handover.
- Branch operations.
- Maintenance backlog.

---

## Evidence Quality

Severity confidence depends on evidence quality.

Poor evidence SHOULD reduce severity confidence and trigger human review.

---

# Severity Assessment Matrix

The following matrix provides initial guidance.

| Damage Type | Typical Severity Range |
|-------------|------------------------|
| Small scratch | Minor |
| Large scratch | Moderate |
| Small dent | Minor to Moderate |
| Large dent | Moderate to Major |
| Broken light | Major to Critical |
| Glass chip | Minor to Moderate |
| Glass crack | Moderate to Critical |
| Tire cut | Moderate to Critical |
| Tire bulge | Critical |
| Wheel rash | Minor to Moderate |
| Fluid leak | Critical |
| Missing trim | Minor to Moderate |
| Missing mirror cover | Moderate |
| Broken mirror | Major |
| Bumper scuff | Minor to Moderate |
| Broken bumper | Major |
| Interior stain | Minor to Moderate |
| Seat tear | Moderate |
| Burn mark | Moderate |
| Unknown visible issue | Unknown |

This matrix is guidance only. Final severity MAY depend on context and human review.

---

# Severity and Damage Taxonomy

Severity SHALL be applied to damage findings classified using the Damage Taxonomy defined in:

```text
DI-0008-Damage-Taxonomy.md
```

Damage Type and Vehicle Area SHALL be used as inputs to severity assessment.

---

# AI Severity Suggestion

AI MAY suggest severity based on:

- Damage type.
- Vehicle area.
- Visible extent.
- Image quality.
- Confidence score.
- Historical comparison.
- Prior human-reviewed examples.
- Configured severity rules.

AI severity SHALL be advisory.

AI SHALL NOT finalize severity for customer-impacting, financial, legal, safety, or operationally significant decisions without human review.

---

# AI Severity Output

AI severity output SHOULD include:

- Suggested severity.
- Confidence score.
- Evidence reference.
- Explanation.
- Uncertainty reason where applicable.
- Review recommendation.
- Damage type.
- Vehicle area.
- Image quality status.
- AI engine/model identifier.

Example:

~~~json
{
  "findingId": "AIF-DI-000188",
  "damageType": "GLASS_CRACK",
  "vehicleArea": "WINDSHIELD",
  "suggestedSeverity": "MAJOR",
  "confidenceScore": 0.82,
  "reviewRecommendation": "HumanReviewRequired",
  "explanation": "A visible crack appears on the windshield. Windshield damage may affect roadworthiness and requires review.",
  "evidenceReferences": ["IMG-DI-01012"],
  "uncertaintyReasons": [],
  "aiEngine": {
    "engineType": "HybridVision",
    "modelVersion": "TBD"
  }
}
~~~

---

# Severity Review Workflow

Severity review SHALL support the following workflow:

```text
AI or User Damage Finding
        ↓
Severity Suggested
        ↓
Review Trigger Evaluated
        ↓
Human Review Required?
        ↓
Reviewer Confirms / Edits / Escalates / Rejects
        ↓
Severity Finalized
        ↓
Damage Case Updated
        ↓
Maintenance Routing Evaluated
```

---

# Human Severity Review

Authorized reviewers SHALL be able to:

- Confirm suggested severity.
- Increase severity.
- Decrease severity.
- Mark severity as unknown.
- Request additional evidence.
- Escalate severity review.
- Add review notes.

Every change SHALL be audited.

---

# Severity Override

Severity override SHALL require:

- Authorized user.
- Reason or note where required.
- Audit record.
- Previous value.
- New value.
- Timestamp.

Severity override MAY trigger workflow changes.

Examples:

- Changing Moderate to Major may trigger maintenance routing.
- Changing Unknown to Minor may close review.
- Changing Minor to Critical may block vehicle release.

---

# Severity and Review Triggers

Human review SHALL be required when:

- Severity is Moderate, Major, or Critical.
- Severity is Unknown.
- Damage may be customer-impacting.
- Damage may require maintenance.
- Damage is safety-relevant.
- AI confidence is below configured threshold.
- Image quality is poor.
- Business policy requires review.

Minor damage MAY still require review depending on policy.

---

# Severity and Maintenance Routing

Severity SHOULD influence Maintenance routing.

| Severity | Maintenance Action |
|----------|-------------------|
| Minor | No routing or monitor, depending on policy |
| Moderate | Maintenance review may be required |
| Major | Maintenance routing should be required |
| Critical | Immediate maintenance/safety review required |
| Unknown | Human review required before routing decision |

Maintenance owns repair execution.

Damage Intelligence owns severity evidence and review status.

---

# Severity and Vehicle Availability

Severity MAY affect vehicle availability.

Suggested behavior:

| Severity | Vehicle Availability Impact |
|----------|-----------------------------|
| Minor | Usually no immediate block |
| Moderate | May require review before next rental |
| Major | May block release pending maintenance review |
| Critical | Should block release pending safety/maintenance review |
| Unknown | May require review before release depending on policy |

Final vehicle availability decisions SHALL be governed by CROMS and Maintenance policies.

---

# Severity and Customer Disputes

Severity SHALL support dispute evidence but SHALL NOT independently determine liability.

Customer-impacting reports SHOULD distinguish:

- AI suggested severity.
- Human confirmed severity.
- Evidence used.
- Review decision.
- Decision timestamp.

---

# Severity and Repair Cost Estimation

Severity MAY be used as an input to repair cost estimation.

However:

- Severity is not a cost.
- Severity does not equal repair price.
- Severity does not determine customer charge.
- Repair cost estimation SHALL be defined separately.

---

# Severity Confidence

Severity confidence SHOULD be tracked independently of damage detection confidence where practical.

Example:

- AI may be confident there is a scratch.
- AI may be less confident whether the scratch is Minor or Moderate.

Severity confidence SHOULD be lowered when:

- Image quality is poor.
- Vehicle area is uncertain.
- Damage extent is unclear.
- Close-up evidence is missing.
- Damage type is uncertain.

---

# Severity Configuration

Severity rules SHOULD be configurable by policy where needed.

Configuration MAY include:

- Review thresholds.
- Maintenance routing thresholds.
- Vehicle release thresholds.
- Damage type severity defaults.
- Vehicle area severity modifiers.
- Tenant or branch policy.
- Rental category policy.

Configuration changes SHALL be audited.

---

# Severity KPIs

Damage Intelligence SHOULD track:

- Severity distribution.
- Severity override rate.
- AI severity acceptance rate.
- Severity escalation rate.
- Unknown severity rate.
- Severity by damage type.
- Severity by vehicle area.
- Severity by branch.
- Severity to maintenance routing rate.
- Severity to repair completion rate.

---

# Severity Audit Requirements

The system SHALL audit:

- Severity suggested.
- Severity confidence.
- Severity changed.
- Severity confirmed.
- Severity escalated.
- Severity marked unknown.
- Severity review completed.
- Maintenance routing triggered by severity.
- Vehicle availability impact triggered by severity.

Audit record SHOULD include:

- User or system actor.
- Timestamp.
- Finding reference.
- Previous severity where applicable.
- New severity.
- Reason.
- Evidence references.

---

# Safety Escalation

Damage Intelligence SHALL support safety escalation for potentially unsafe damage.

Safety escalation MAY be triggered by:

- Tire bulge.
- Major tire cut.
- Broken windshield in driver visibility area.
- Broken or missing critical light.
- Fluid leak.
- Severe deformation.
- Mirror damage affecting safe driving.
- Unknown damage with possible safety impact.

Safety escalation SHALL require human review.

---

# Edge Cases

## Cosmetic Damage with High Visibility

Some cosmetic damage may be Minor physically but significant for customer dispute or resale visibility.

System SHOULD allow reviewer adjustment.

## Small Damage on Critical Component

Small damage on a critical area, such as windshield or tire, may be more severe than size alone suggests.

## Poor Evidence

When evidence is poor, severity SHOULD be Unknown or routed for review.

## Existing Damage Worsened

If comparison shows damage worsened, severity SHOULD reflect current condition and changed status.

## Repaired Damage

If damage appears repaired, severity may become not applicable or resolved depending on workflow.

---

# Normative Requirements

## Requirement

ID: REQ-DI-0800

Title:
Standard Severity Levels

Statement:
Damage Intelligence SHALL use standardized severity levels for damage findings.

Priority:
Critical

Verification:
Data Review

---

## Requirement

ID: REQ-DI-0801

Title:
Severity Assessment

Statement:
Damage Intelligence SHALL support severity assessment for detected or reported damage findings.

Priority:
Critical

Verification:
Functional Test

---

## Requirement

ID: REQ-DI-0802

Title:
AI Severity Suggestion

Statement:
Damage Intelligence MAY provide AI-generated severity suggestions.

Priority:
High

Verification:
AI Review

---

## Requirement

ID: REQ-DI-0803

Title:
Human Severity Review

Statement:
Authorized users SHALL be able to review and adjust AI-generated severity suggestions.

Priority:
Critical

Verification:
Workflow Test

---

## Requirement

ID: REQ-DI-0804

Title:
Severity Audit Trail

Statement:
Severity suggestions, confirmations, overrides, and escalations SHALL be auditable.

Priority:
Critical

Verification:
Audit Review

---

## Requirement

ID: REQ-DI-0805

Title:
Unknown Severity

Statement:
Damage Intelligence SHALL support Unknown severity where severity cannot be reliably determined.

Priority:
Critical

Verification:
AI Governance Review

---

## Requirement

ID: REQ-DI-0806

Title:
Severity Review Triggers

Statement:
Damage Intelligence SHALL route Moderate, Major, Critical, Unknown, safety-relevant, or policy-required severity findings for human review.

Priority:
Critical

Verification:
Workflow Test

---

## Requirement

ID: REQ-DI-0807

Title:
Maintenance Routing Influence

Statement:
Damage severity SHOULD influence maintenance routing recommendations.

Priority:
High

Verification:
Maintenance Review

---

## Requirement

ID: REQ-DI-0808

Title:
Safety Escalation

Statement:
Damage Intelligence SHALL support escalation for potentially safety-impacting damage.

Priority:
Critical

Verification:
Safety Review

---

## Requirement

ID: REQ-DI-0809

Title:
Severity Is Not Liability

Statement:
Damage severity SHALL NOT independently determine customer liability, legal responsibility, or financial charge.

Priority:
Critical

Verification:
Governance Review

---

## Requirement

ID: REQ-DI-0810

Title:
Severity Configuration

Statement:
Damage Intelligence SHOULD support configurable severity thresholds and routing rules.

Priority:
Medium

Verification:
Configuration Review

---

## Requirement

ID: REQ-DI-0811

Title:
Severity KPIs

Statement:
Damage Intelligence SHOULD track severity-related operational and AI quality metrics.

Priority:
Medium

Verification:
Report Review

---

# Business Rules

## BR-DI-0400 — Severity Must Be Standardized

Damage severity SHALL use approved severity labels.

---

## BR-DI-0401 — Unknown Is Acceptable

When severity cannot be reliably determined, the system SHALL use Unknown rather than guessing.

---

## BR-DI-0402 — Human Review Required for Significant Severity

Moderate, Major, Critical, and Unknown severity findings SHALL require review where operationally significant.

---

## BR-DI-0403 — Safety-Relevant Damage Requires Escalation

Potentially safety-impacting damage SHALL be escalated for review.

---

## BR-DI-0404 — AI Severity Is Advisory

AI-generated severity SHALL remain advisory until reviewed where human review is required.

---

## BR-DI-0405 — Severity Does Not Equal Charge

Severity SHALL NOT be treated as a customer charge amount or liability decision.

---

# AI Implementation Contract

AI development agents SHALL:

- Treat this document as the authoritative severity assessment specification.
- Preserve all severity codes.
- Preserve all requirement IDs.
- Not treat severity as final liability or financial charge.
- Generate future APIs, data schemas, UI labels, reports, tests, and AI prompts consistent with this document.
- Preserve human review requirements.
- Preserve safety escalation requirements.
- Preserve audit requirements.
- Use UNKNOWN when severity cannot be reliably determined.
- Raise ambiguity where severity criteria are insufficient.

---

# References

- DI-0005 – AI Damage Detection
- DI-0006 – Damage Comparison
- DI-0008 – Damage Taxonomy
- DI-0010 – Repair Cost Estimation
- GEES-0005 – AI Engineering Standard
- GEES-0007 – Enterprise Security Standard
- GEES-0013 – Business Rule Engineering Standard

---

# Revision History

| Version | Date | Description |
|----------|------|-------------|
| 1.0.0 | 2026-06-27 | Initial Damage Intelligence Severity Assessment Specification |
