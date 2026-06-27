---
id: DI-0003
title: Damage Intelligence User Personas
version: 1.0.0
document_type: Product Specification
document_class: User Personas
status: Draft
classification: Internal
owner: Riyadah Technology
reviewers:
  - Chief Enterprise Architect
  - Product Owner
  - UX Lead
  - Operations Lead
  - AI Engineering Lead
approvers: []
created: 2026-06-27
updated: 2026-06-27
authoritative: true
ai_consumable: true
related:
  - DI-0001
  - DI-0002
  - RA-0001
  - RA-0002
  - GEES-0012
  - GEES-0015
  - GEES-0016
---

# Damage Intelligence User Personas

## Executive Summary

This document defines the primary and secondary user personas for the Damage Intelligence capability.

Damage Intelligence is used by multiple operational roles across rental operations, maintenance operations, fleet supervision, customer service, and management.

Each persona has different goals, responsibilities, permissions, devices, pain points, and success criteria.

Future workflows, UI specifications, API authorization rules, notifications, reports, and AI behavior SHALL consider these personas.

---

# Purpose

The purpose of this document is to define the human users, operational roles, and external stakeholders who interact with Damage Intelligence.

This document SHALL guide:

- User experience design
- Mobile inspection design
- Web portal design
- Permission model
- Workflow design
- Notification rules
- Reporting requirements
- AI review workflows
- Acceptance criteria
- Test scenarios

---

# Scope

This document covers personas related to:

- Vehicle check-out inspection
- Vehicle check-in inspection
- Damage review
- Damage approval
- Customer dispute evidence
- Maintenance routing
- Repair review
- Operational reporting
- System administration

This document does not define detailed UI screens, APIs, database schemas, or workflows. Those SHALL be defined in later specifications.

---

# Persona Groups

Damage Intelligence users are grouped into the following categories:

1. Frontline Rental Users
2. Customer-Facing Users
3. Maintenance Users
4. Review and Approval Users
5. Management Users
6. Administrative Users
7. External Stakeholders
8. AI-Assisted Roles

---

# Primary Personas

## Persona DI-PER-0001 — Rental Agent

### Description

The Rental Agent performs vehicle handover and return activities at a rental branch.

The Rental Agent is usually responsible for starting check-out and check-in inspections and ensuring required photos are captured.

### Primary Goals

- Complete inspection quickly.
- Capture required vehicle condition evidence.
- Avoid missing visible damage.
- Reduce customer disputes.
- Complete the rental handover or return without delay.

### Responsibilities

- Start vehicle inspection.
- Capture required photos.
- Confirm inspection completion.
- Record visible damage notes.
- Submit inspection for AI analysis.
- Review obvious findings when permitted.
- Provide inspection evidence to the customer when needed.

### Pain Points

- Time pressure during busy branch hours.
- Customers waiting during inspection.
- Poor lighting or outdoor conditions.
- Difficulty capturing consistent angles.
- Fear of being blamed for missed damage.
- Manual typing of damage notes.

### Device Context

- Mobile device
- Tablet
- Branch workstation

### Required Capabilities

- Guided capture
- Checklist progress
- Simple damage marking
- Offline capture where required
- Quick submission
- Clear success confirmation

### AI Assistance

AI SHOULD help by:

- Validating photo quality.
- Detecting visible damage.
- Suggesting damage notes.
- Highlighting missing capture angles.
- Warning when photos are unclear.

### Success Criteria

The Rental Agent is successful when:

- Required inspection evidence is captured.
- Inspection is completed without unnecessary delay.
- AI quality checks pass.
- Damage evidence is linked to the correct rental and vehicle.
- The customer handover or return process continues smoothly.

---

## Persona DI-PER-0002 — Customer

### Description

The Customer receives or returns a rented vehicle and may later review vehicle condition evidence.

The customer may not directly use the Damage Intelligence system in Version 1, but customer transparency is a key business outcome.

### Primary Goals

- Receive a fair and transparent inspection process.
- Understand vehicle condition at check-out.
- Avoid being charged for pre-existing damage.
- See clear evidence if new damage is claimed.

### Responsibilities

- Review inspection evidence when presented.
- Confirm vehicle condition where business workflow requires it.
- Raise dispute if evidence is unclear.

### Pain Points

- Disagreement over whether damage is new.
- Poor or unclear photos.
- Lack of trust in manual inspection notes.
- Unexpected charges after return.

### Device Context

- Customer-facing branch screen
- Email report
- PDF report
- Customer portal in future versions

### Required Capabilities

- Clear evidence report
- Before/after comparison summary
- Human-readable damage explanation
- Timestamped inspection record

### AI Assistance

AI MAY support customer transparency by:

- Generating plain-language summaries.
- Highlighting evidence used for damage comparison.
- Distinguishing AI findings from human-approved findings.

### Success Criteria

The customer experience is successful when:

- Inspection evidence is understandable.
- Claims are supported by clear evidence.
- Pre-existing damage is not incorrectly assigned to the customer.
- Disputes can be reviewed fairly.

---

## Persona DI-PER-0003 — Damage Review Specialist

### Description

The Damage Review Specialist reviews AI-generated findings and determines whether damage should be confirmed, rejected, escalated, or routed to Maintenance.

This persona may be a branch supervisor, operations reviewer, or centralized review team member.

### Primary Goals

- Review AI findings efficiently.
- Confirm valid new damage.
- Reject false positives.
- Escalate uncertain cases.
- Maintain consistent decisions.
- Reduce incorrect customer charges.

### Responsibilities

- Review inspection photos.
- Review AI findings.
- Compare current and historical inspection evidence.
- Confirm damage classification.
- Adjust severity.
- Approve or reject findings.
- Route confirmed damage to Maintenance.
- Add reviewer comments.

### Pain Points

- Too many false positives.
- Inconsistent photo angles.
- Unclear historical evidence.
- Pressure from customers or branch teams.
- Lack of standardized review criteria.

### Device Context

- Web portal
- Tablet
- Review dashboard

### Required Capabilities

- Side-by-side comparison
- AI confidence display
- Damage timeline
- Reviewer notes
- Approval/rejection controls
- Escalation workflow
- Audit history

### AI Assistance

AI SHOULD help by:

- Comparing current and prior images.
- Suggesting damage status.
- Explaining evidence.
- Flagging uncertainty.
- Summarizing likely new damage.
- Recommending review priority.

### Success Criteria

The Damage Review Specialist is successful when:

- Valid damage is confirmed.
- False positives are rejected.
- Uncertain findings are escalated.
- Decisions are auditable.
- Review time is reduced.
- Decision consistency improves.

---

## Persona DI-PER-0004 — Fleet Supervisor

### Description

The Fleet Supervisor monitors vehicle condition across multiple vehicles, branches, or fleet groups.

### Primary Goals

- Understand fleet damage trends.
- Identify high-risk vehicles.
- Monitor open damage cases.
- Improve vehicle availability.
- Reduce downtime.

### Responsibilities

- Review fleet-level damage dashboards.
- Monitor unresolved damage cases.
- Track vehicle damage history.
- Coordinate with rental and maintenance teams.
- Identify recurring damage patterns.

### Pain Points

- Lack of fleet-wide visibility.
- Damage cases hidden in branch-level processes.
- Vehicles unavailable due to delayed repair decisions.
- Difficulty identifying branches with poor inspection quality.

### Device Context

- Web dashboard
- Management reporting portal

### Required Capabilities

- Fleet damage dashboard
- Vehicle damage history
- Open damage case list
- Branch trend reports
- Maintenance routing status

### AI Assistance

AI MAY help by:

- Identifying damage trends.
- Highlighting recurring vehicle damage.
- Ranking high-risk vehicles.
- Suggesting process improvements.

### Success Criteria

The Fleet Supervisor is successful when:

- Open damage cases are visible.
- Vehicle availability impact is understood.
- Damage trends are measurable.
- Maintenance routing is faster.
- Fleet condition history is reliable.

---

## Persona DI-PER-0005 — Maintenance Advisor

### Description

The Maintenance Advisor determines whether confirmed damage requires repair and whether a work order should be created.

### Primary Goals

- Understand confirmed damage.
- Assess repair need.
- Route damage correctly.
- Avoid unnecessary work orders.
- Prioritize urgent repairs.

### Responsibilities

- Review confirmed damage cases.
- Review AI severity and repair suggestions.
- Decide whether repair is required.
- Request work order creation.
- Coordinate with workshop teams.
- Review repair estimate support.

### Pain Points

- Incomplete damage evidence.
- Lack of severity information.
- Unclear repair priority.
- Re-entering information into Maintenance system.
- Missing link between rental damage and repair action.

### Device Context

- Maintenance web portal
- Tablet
- Workshop workstation

### Required Capabilities

- Damage case view
- Damage severity
- Repair recommendation
- Evidence package
- Maintenance routing
- Work order handoff

### AI Assistance

AI SHOULD help by:

- Suggesting repair category.
- Estimating severity.
- Suggesting repair urgency.
- Summarizing evidence for technician review.

### Success Criteria

The Maintenance Advisor is successful when:

- Damage requiring repair is routed quickly.
- Evidence is sufficient for repair planning.
- Work orders contain accurate damage context.
- Repair priority is clear.
- Duplicate manual data entry is reduced.

---

## Persona DI-PER-0006 — Technician

### Description

The Technician performs physical repair or inspection work after damage is routed to Maintenance.

### Primary Goals

- Understand the reported damage.
- View supporting images.
- Confirm repair scope.
- Complete repair efficiently.
- Support quality control.

### Responsibilities

- Review damage evidence.
- Inspect vehicle physically.
- Confirm repair work.
- Add repair notes.
- Capture post-repair photos where required.
- Support quality inspection.

### Pain Points

- Poor damage descriptions.
- Missing images.
- Unclear location of damage.
- Damage case not linked to work order.
- Lack of before/after repair evidence.

### Device Context

- Mobile technician app
- Tablet
- Workshop workstation

### Required Capabilities

- Damage image viewer
- Annotated damage location
- Damage severity
- Work order link
- Post-repair image capture
- Technician notes

### AI Assistance

AI MAY help by:

- Summarizing damage.
- Highlighting affected area.
- Suggesting inspection points.
- Comparing post-repair photos against pre-repair evidence.

### Success Criteria

The Technician is successful when:

- Damage scope is clear.
- Repair evidence is accessible.
- Repair notes are recorded.
- Post-repair condition is documented.
- Quality inspection is supported.

---

## Persona DI-PER-0007 — Operations Manager

### Description

The Operations Manager oversees branch operations, customer disputes, process performance, and financial impact related to vehicle damage.

### Primary Goals

- Reduce disputes.
- Improve inspection compliance.
- Monitor staff performance.
- Reduce damage-related losses.
- Improve process consistency.

### Responsibilities

- Review operational reports.
- Monitor branch inspection quality.
- Review dispute trends.
- Approve policy changes.
- Track AI effectiveness.
- Ensure compliance with business process.

### Pain Points

- Lack of visibility into inspection quality.
- Inconsistent branch behavior.
- Unclear damage liability.
- Weak reporting.
- High dispute resolution time.

### Device Context

- Management dashboard
- Web portal
- Reports

### Required Capabilities

- Executive dashboard
- Branch comparison
- Damage trends
- Dispute evidence reports
- AI performance reports
- Review SLA tracking

### AI Assistance

AI MAY help by:

- Identifying branches with poor inspection compliance.
- Detecting unusual damage patterns.
- Summarizing disputes.
- Suggesting process improvements.

### Success Criteria

The Operations Manager is successful when:

- Damage disputes decrease.
- Inspection compliance improves.
- Branch trends are visible.
- AI performance is measurable.
- Operational decisions are evidence-based.

---

## Persona DI-PER-0008 — System Administrator

### Description

The System Administrator configures users, roles, permissions, inspection templates, capture requirements, and system settings.

### Primary Goals

- Configure Damage Intelligence safely.
- Manage access permissions.
- Maintain inspection templates.
- Monitor system health.
- Support operational rollout.

### Responsibilities

- Manage users and roles.
- Configure inspection capture rules.
- Configure damage categories.
- Configure review workflows.
- Manage integration settings.
- Monitor audit and access logs.

### Pain Points

- Misconfigured permissions.
- Inconsistent inspection templates.
- Difficulty managing multi-branch settings.
- Lack of configuration audit trail.

### Device Context

- Admin portal
- Web dashboard

### Required Capabilities

- Role management
- Permission management
- Inspection template configuration
- Workflow configuration
- Integration configuration
- Audit logs

### AI Assistance

AI MAY help by:

- Detecting configuration inconsistencies.
- Suggesting missing permissions.
- Explaining configuration impact.
- Flagging risky settings.

### Success Criteria

The System Administrator is successful when:

- Users have correct permissions.
- Inspection templates are consistent.
- Configuration changes are auditable.
- Integrations remain healthy.
- System settings support operational needs.

---

# Secondary Personas

## Persona DI-PER-0009 — Insurance Reviewer

### Description

An Insurance Reviewer may review damage evidence when insurance claim support is required.

### Primary Goals

- Review damage evidence.
- Understand inspection timeline.
- Assess claim evidence.

### Access Level

Usually external or limited-access.

### Required Capabilities

- Read-only damage report
- Evidence package
- Timeline
- Human-approved findings

---

## Persona DI-PER-0010 — Compliance Auditor

### Description

A Compliance Auditor reviews whether inspection evidence, user decisions, and system actions were properly recorded.

### Primary Goals

- Verify auditability.
- Confirm evidence integrity.
- Review user actions.
- Confirm policy compliance.

### Required Capabilities

- Audit log access
- Evidence history
- Decision timeline
- Report export

---

## Persona DI-PER-0011 — AI Quality Reviewer

### Description

The AI Quality Reviewer monitors AI output quality, false positives, false negatives, human override rates, and model performance.

### Primary Goals

- Evaluate AI accuracy.
- Identify recurring AI errors.
- Improve prompt/model quality.
- Support governance review.

### Required Capabilities

- AI finding review
- Human override reports
- Accuracy metrics
- False positive/negative tagging
- AI feedback loop

---

# Persona Permission Overview

| Persona | Capture | Review AI | Approve Damage | Route to Maintenance | Configure | Reports |
|---------|---------|-----------|----------------|----------------------|-----------|---------|
| Rental Agent | Yes | Limited | No | No | No | Limited |
| Customer | No | No | No | No | No | Limited/External |
| Damage Review Specialist | Yes | Yes | Yes | Yes | No | Yes |
| Fleet Supervisor | No | Yes | Limited | Yes | No | Yes |
| Maintenance Advisor | No | Yes | Limited | Yes | No | Yes |
| Technician | Limited | Limited | No | No | No | Limited |
| Operations Manager | No | Yes | Yes | Yes | No | Yes |
| System Administrator | No | No | No | No | Yes | Yes |
| Insurance Reviewer | No | No | No | No | No | Limited |
| Compliance Auditor | No | No | No | No | No | Audit |
| AI Quality Reviewer | No | Yes | No | No | No | AI Quality |

Detailed permission rules SHALL be defined in a later permissions specification.

---

# Device and Environment Considerations

Damage Intelligence SHALL support users operating in different physical environments:

## Branch Environment

- Fast customer handover.
- Outdoor lighting variations.
- Customer waiting.
- Time-sensitive inspection.

## Parking Lot Environment

- Weak connectivity.
- Sun glare.
- Night conditions.
- Space constraints.

## Workshop Environment

- Dirty vehicles.
- Vehicle parts removed.
- Technician gloves.
- Tablet or rugged device usage.

## Management Environment

- Dashboard review.
- Reports.
- Branch comparison.
- Historical analysis.

---

# UX Implications

Damage Intelligence user interfaces SHALL be:

- Fast for frontline users.
- Evidence-rich for reviewers.
- Dashboard-oriented for managers.
- Permission-aware.
- Mobile-friendly.
- Clear about AI confidence and uncertainty.
- Explicit when human review is required.

Where required, the interface SHOULD support Arabic and English.

---

# AI Interaction by Persona

| Persona | AI Role |
|---------|---------|
| Rental Agent | Photo quality, damage suggestions, capture guidance |
| Customer | Plain-language explanation of approved findings |
| Damage Review Specialist | Comparison, confidence, evidence summary |
| Fleet Supervisor | Trends, prioritization, anomaly detection |
| Maintenance Advisor | Severity, repair recommendation |
| Technician | Damage summary, affected area guidance |
| Operations Manager | Analytics, dispute trend summaries |
| System Administrator | Configuration risk warnings |
| AI Quality Reviewer | Model quality monitoring |

---

# Persona-Based Risks

| Persona | Risk | Mitigation |
|---------|------|------------|
| Rental Agent | Skips required photos | Guided checklist and mandatory capture |
| Customer | Distrusts AI output | Human-approved report and evidence |
| Damage Review Specialist | Review overload | Confidence scoring and prioritization |
| Fleet Supervisor | Misses fleet-wide trends | Dashboards and reports |
| Maintenance Advisor | Receives incomplete evidence | Required evidence package |
| Technician | Misunderstands damage scope | Annotated images and notes |
| Operations Manager | Inconsistent branch performance | Branch-level KPIs |
| System Administrator | Misconfigures permissions | RBAC validation and audit |
| AI Quality Reviewer | Cannot measure AI quality | AI quality metrics and feedback loop |

---

# Normative Requirements

## Requirement

ID: REQ-DI-0200

Title:
Persona-Aware Design

Statement:
Damage Intelligence SHALL support workflows appropriate to the responsibilities of each primary persona.

Priority:
Critical

Verification:
UX Review

---

## Requirement

ID: REQ-DI-0201

Title:
Role-Based Capabilities

Statement:
Damage Intelligence SHALL enforce persona-aligned role-based capabilities for capture, review, approval, reporting, and administration.

Priority:
Critical

Verification:
Security Review

---

## Requirement

ID: REQ-DI-0202

Title:
Customer Transparency

Statement:
Damage Intelligence SHALL support customer-facing evidence transparency where required by business workflow.

Priority:
High

Verification:
Business Review

---

## Requirement

ID: REQ-DI-0203

Title:
Reviewer Workflow Support

Statement:
Damage Intelligence SHALL provide review tools for authorized users to evaluate AI findings and historical comparisons.

Priority:
Critical

Verification:
Workflow Test

---

## Requirement

ID: REQ-DI-0204

Title:
Maintenance Persona Support

Statement:
Damage Intelligence SHALL provide damage evidence and severity context suitable for Maintenance Advisor and Technician use.

Priority:
High

Verification:
Maintenance Review

---

## Requirement

ID: REQ-DI-0205

Title:
Management Reporting Personas

Statement:
Damage Intelligence SHALL support management personas with reports and dashboards for damage trends, review outcomes, and operational performance.

Priority:
High

Verification:
Report Review

---

## Requirement

ID: REQ-DI-0206

Title:
AI Quality Review Persona

Statement:
Damage Intelligence SHOULD support an AI Quality Reviewer persona for monitoring AI output quality and human override patterns.

Priority:
Medium

Verification:
AI Governance Review

---

## Requirement

ID: REQ-DI-0207

Title:
Persona-Based Permission Design

Statement:
Damage Intelligence SHALL define permissions based on operational responsibility and least privilege.

Priority:
Critical

Verification:
Security Review

---

# AI Implementation Contract

AI development agents SHALL:

- Preserve all persona IDs.
- Preserve the role separation defined in this document.
- Generate future workflows and screens according to persona responsibilities.
- Not grant approval or administrative authority to personas unless explicitly specified.
- Preserve the distinction between AI suggestions and human-approved decisions.
- Use personas to generate user stories, acceptance criteria, permissions, and test cases.
- Raise ambiguity if a workflow lacks a responsible persona.

---

# References

- DI-0001 – Damage Intelligence Product Vision
- DI-0002 – Damage Intelligence Business Requirements
- GEES-0012 – User Story Engineering Standard
- GEES-0015 – Use Case Engineering Standard
- GEES-0016 – Business Process Engineering Standard
- GEES-0007 – Enterprise Security Standard

---

# Revision History

| Version | Date | Description |
|----------|------|-------------|
| 1.0.0 | 2026-06-27 | Initial Damage Intelligence User Personas |
