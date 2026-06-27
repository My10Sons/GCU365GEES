---
id: DI-0007
title: Damage Intelligence Vehicle Capture Standards
version: 1.0.0
document_type: Product Specification
document_class: Capture Standard
status: Draft
classification: Internal
owner: Riyadah Technology
reviewers:
  - Chief Enterprise Architect
  - Product Owner
  - UX Lead
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
  - DI-0002
  - DI-0003
  - DI-0004
  - DI-0005
  - DI-0006
  - RA-0001
  - RA-0002
  - GEES-0005
  - PLATFORM-0005
---

# Damage Intelligence Vehicle Capture Standards

## Executive Summary

This document defines the vehicle image capture standards for Damage Intelligence.

Vehicle capture quality directly affects inspection reliability, AI damage detection accuracy, damage comparison accuracy, customer dispute evidence, maintenance routing, and auditability.

Damage Intelligence SHALL use standardized capture positions, image quality rules, metadata requirements, device guidance, and exception handling to ensure that vehicle condition evidence is consistent, comparable, and trustworthy across check-out, check-in, maintenance intake, and quality inspection workflows.

---

# Purpose

The purpose of this document is to define how vehicle condition evidence SHALL be captured.

This standard SHALL guide:

- Mobile capture workflow
- Web-assisted upload workflow
- AI damage detection
- Historical damage comparison
- Image quality validation
- Inspection templates
- User training
- Test cases
- Acceptance criteria
- Evidence audit requirements

---

# Scope

## In Scope

This standard covers:

- Required exterior capture positions
- Required interior capture positions
- Odometer and fuel or battery capture
- Close-up damage capture
- Image quality requirements
- Device orientation
- Lighting guidance
- Distance guidance
- Angle guidance
- Capture metadata
- Offline capture considerations
- Recapture rules
- Exception handling
- Audit requirements

## Out of Scope

This standard does not define:

- AI damage detection algorithms
- Damage taxonomy
- Final damage severity rules
- Database schema
- API contracts
- Full mobile UI design
- Legal evidence admissibility rules
- Camera hardware procurement

---

# Capture Principles

Vehicle capture SHALL follow these principles:

1. Standardization
2. Repeatability
3. Comparability
4. Evidence Integrity
5. AI Readiness
6. Human Review Support
7. Operational Simplicity
8. Auditability
9. Security
10. Offline Tolerance Where Required

---

# Capture Objectives

Vehicle capture SHALL support the following objectives:

- Establish baseline vehicle condition.
- Capture return vehicle condition.
- Enable before/after comparison.
- Enable AI damage detection.
- Support human review.
- Support dispute evidence.
- Support maintenance routing.
- Preserve inspection history.
- Reduce missed visible damage.
- Reduce inconsistent branch inspection practices.

---

# Capture Contexts

Damage Intelligence SHALL support capture in the following contexts:

| Context | Description |
|---------|-------------|
| Check-Out | Baseline condition before rental starts |
| Check-In | Return condition after rental ends |
| Maintenance Intake | Vehicle condition before repair begins |
| Maintenance Quality | Vehicle condition after repair completion |
| Ad Hoc | Manual inspection outside normal workflow |

Version 1 SHALL prioritize Check-Out and Check-In capture.

---

# Required Exterior Capture Positions

The system SHOULD support the following standard exterior capture positions.

| Capture ID | Capture Position | Required for Check-Out | Required for Check-In | Purpose |
|------------|------------------|------------------------|-----------------------|---------|
| CAPTURE-FRONT | Front View | Yes | Yes | Front bumper, hood, headlights, windshield |
| CAPTURE-REAR | Rear View | Yes | Yes | Rear bumper, trunk, tail lights |
| CAPTURE-LEFT | Left Side View | Yes | Yes | Left doors, fenders, side panels |
| CAPTURE-RIGHT | Right Side View | Yes | Yes | Right doors, fenders, side panels |
| CAPTURE-FL-CORNER | Front Left Corner | Yes | Yes | Front-left bumper, fender, wheel, light |
| CAPTURE-FR-CORNER | Front Right Corner | Yes | Yes | Front-right bumper, fender, wheel, light |
| CAPTURE-RL-CORNER | Rear Left Corner | Yes | Yes | Rear-left bumper, quarter panel, wheel |
| CAPTURE-RR-CORNER | Rear Right Corner | Yes | Yes | Rear-right bumper, quarter panel, wheel |
| CAPTURE-ROOF | Roof | Optional | Optional | Roof damage where required |
| CAPTURE-WHEELS | Wheels | Template-Based | Template-Based | Wheel rash, tire damage |

Capture templates MAY vary by vehicle type, operational policy, branch policy, inspection type, and risk category.

---

# Required Interior Capture Positions

Interior capture MAY be required depending on rental policy.

| Capture ID | Capture Position | Required | Purpose |
|------------|------------------|----------|---------|
| CAPTURE-INTERIOR-FRONT | Front Interior | Optional | Dashboard, seats, console |
| CAPTURE-INTERIOR-REAR | Rear Interior | Optional | Rear seats, floor, trim |
| CAPTURE-DASHBOARD | Dashboard | Optional | Dashboard condition and warning lights |
| CAPTURE-TRUNK | Trunk/Cargo Area | Optional | Cargo area damage or missing items |

---

# Required Instrument Capture

The system SHALL support capture of operational evidence.

| Capture ID | Capture Position | Required | Purpose |
|------------|------------------|----------|---------|
| CAPTURE-ODOMETER | Odometer | Yes | Mileage evidence |
| CAPTURE-FUEL-BATTERY | Fuel/Battery Indicator | Yes | Fuel or EV battery level |
| CAPTURE-VIN | VIN Plate | Optional | Vehicle identity validation |
| CAPTURE-LICENSE-PLATE | License Plate | Optional | Vehicle identity validation |

Odometer and fuel/battery capture MAY be supported by OCR in future versions.

---

# Close-Up Damage Capture

When visible damage is detected or manually reported, users SHOULD capture one or more close-up images.

Close-up damage images SHOULD include:

- The damage area.
- Surrounding panel context.
- A stable, focused view.
- Sufficient lighting.
- Optional reference scale where operationally practical.

Close-up images SHALL be linked to the related inspection session and damage finding.

---

# Capture Angle Standards

Exterior images SHOULD be captured so that the relevant vehicle side or area is clearly visible.

Guidance:

- Front and rear images SHOULD show the full vehicle width.
- Side images SHOULD show the full vehicle side where practical.
- Corner images SHOULD show two vehicle faces and the nearest wheel.
- Close-up images SHOULD show both the damage and enough surrounding context to identify location.
- Odometer and fuel/battery images SHOULD be captured straight-on where practical.

---

# Capture Distance Standards

Recommended capture distance MAY vary by vehicle size.

General guidance:

| Capture Type | Recommended Distance |
|--------------|----------------------|
| Full exterior view | 2–5 meters |
| Corner view | 1.5–3 meters |
| Wheel view | 0.5–1.5 meters |
| Close-up damage | 0.3–1 meter |
| Odometer/fuel | Close enough for readability |

The system MAY provide user guidance through overlays, examples, or instructions.

---

# Orientation Standards

Images SHOULD be captured in the orientation required by the capture template.

The system MAY enforce or recommend:

- Landscape orientation for exterior full-view images.
- Portrait or landscape orientation for close-ups depending on damage location.
- Straight-on framing for instrument cluster images.

The capture workflow SHOULD discourage rotated, cropped, or partial images when full-view capture is required.

---

# Lighting Standards

Images SHOULD be captured with sufficient lighting for human review and AI analysis.

The system SHOULD detect or warn about:

- Underexposure
- Overexposure
- Strong glare
- Heavy shadow
- Night capture without flash or illumination
- Reflection that obscures damage
- Rain or water obstruction

Where lighting is poor, the system SHOULD request recapture or additional close-up images.

---

# Image Quality Standards

The system SHOULD validate image quality using automated checks where practical.

Quality checks SHOULD include:

- Blur detection
- Brightness
- Overexposure
- Resolution
- Vehicle presence
- Capture position match
- Duplicate image detection
- Obstruction detection
- Crop completeness
- Focus quality
- File corruption

Images failing critical quality checks SHOULD be recaptured unless operational policy allows submission with a reason.

---

# Minimum Image Metadata

Every captured image SHALL include or be associated with metadata.

Required metadata SHOULD include:

- Image ID
- Inspection Session ID
- Vehicle ID
- Capture Position ID
- Inspection Type
- Capture Timestamp
- Capture User ID
- Tenant ID
- Branch ID where available
- Rental Agreement ID where applicable
- Device Identifier where available
- GPS Location where permitted
- Image Quality Result
- Sync Status
- Storage Reference

---

# Image File Standards

The system SHOULD support common mobile image formats.

Preferred formats:

- JPEG
- PNG where required
- HEIC support MAY be considered where devices require it

Images SHOULD be compressed for upload efficiency while preserving sufficient quality for review and AI analysis.

Original or high-quality evidence versions SHOULD be preserved according to evidence retention policy.

---

# Evidence Integrity

Captured images SHALL be protected from unauthorized alteration.

The system SHOULD preserve:

- Original upload timestamp.
- Capture metadata.
- Storage reference.
- User identity.
- Audit history.
- Image hash where practical.

Approved evidence SHALL NOT be overwritten.

Corrections SHALL create new versions or audit records.

---

# Offline Capture Standards

Where offline capture is supported:

- Required inspection context SHOULD be cached before capture.
- Captured images SHALL be stored securely on the device.
- Local inspection metadata SHALL be preserved.
- Sync status SHALL be visible to users.
- Upload SHALL occur when connectivity is restored.
- Server-side validation SHALL occur after upload.
- Conflicts SHALL be resolved through defined rules.

Offline capture SHALL NOT bypass auditability.

---

# Capture Template Configuration

Damage Intelligence SHOULD support configurable capture templates.

Templates MAY vary by:

- Vehicle type
- Rental type
- Branch
- Tenant
- Inspection type
- Risk category
- Maintenance workflow
- Damage review policy

Each template SHOULD define:

- Required capture positions
- Optional capture positions
- Minimum image quality rules
- Recapture rules
- Close-up requirements
- Review triggers

---

# Guided Capture User Experience

The guided capture experience SHOULD provide:

- Capture checklist
- Progress indicator
- Required/optional marker
- Example reference image
- Angle guidance
- Quality feedback
- Retake option
- Save draft
- Resume inspection
- Submit inspection
- Offline status where applicable

The workflow SHOULD minimize typing for frontline users.

---

# AI Capture Support

AI MAY assist capture by:

- Detecting wrong angle.
- Detecting missing vehicle.
- Detecting blurry images.
- Detecting poor lighting.
- Suggesting retake.
- Identifying possible damage during capture.
- Recommending close-up images.
- Confirming capture completeness.

AI capture support SHALL be advisory unless enforced by inspection policy.

---

# Recapture Rules

The system SHOULD request recapture when:

- Required image is missing.
- Image is too blurry.
- Image is too dark.
- Image is overexposed.
- Vehicle is not visible.
- Wrong capture position is detected.
- Image is duplicate.
- Required area is cropped.

Users MAY be allowed to override recapture with a reason if business policy permits.

Overrides SHALL be audited.

---

# Exception Handling

## Vehicle Cannot Be Fully Captured

If space constraints prevent full capture:

- User SHALL capture best available evidence.
- User SHALL provide reason where required.
- System SHOULD request additional close-ups.

## Weather Prevents Standard Capture

If weather affects capture:

- User SHOULD record condition.
- System MAY request indoor or sheltered capture where possible.
- Image quality limitations SHALL be recorded.

## Customer Refuses Waiting

If operational time pressure prevents complete capture:

- User SHALL follow branch policy.
- Missing required evidence SHALL be flagged.
- Supervisor review MAY be required.

## Device Failure

If device capture fails:

- User MAY resume on another device.
- Partial inspection state SHOULD be preserved where possible.

## Sync Failure

If upload fails:

- Images SHALL remain queued.
- User SHALL see sync status.
- System SHALL retry according to policy.

---

# Capture Security

The system SHALL enforce:

- Authenticated capture user
- Tenant isolation
- Secure local storage where offline
- Secure upload
- Secure cloud storage
- Controlled access to image URLs
- Audit logging
- Image access authorization

Temporary public image links SHALL expire.

---

# Capture Audit Requirements

The system SHALL audit:

- Inspection started
- Image captured
- Image retaken
- Image rejected
- Image quality failed
- Image submitted
- Capture override
- Offline capture
- Sync completed
- Sync failed
- Image accessed
- Image deleted attempt

Audit entries SHALL include user, timestamp, object reference, and reason where applicable.

---

# Capture KPIs

Damage Intelligence SHOULD measure:

- Average capture completion time
- Required photo completion rate
- Image quality failure rate
- Recapture rate
- Offline capture rate
- Sync failure rate
- Missing evidence rate
- Close-up capture rate
- AI capture guidance acceptance rate
- Branch capture compliance rate

---

# Normative Requirements

## Requirement

ID: REQ-DI-0600

Title:
Standard Vehicle Capture

Statement:
Damage Intelligence SHALL define standardized vehicle capture positions for inspection workflows.

Priority:
Critical

Verification:
Inspection Template Review

---

## Requirement

ID: REQ-DI-0601

Title:
Required Capture Checklist

Statement:
Damage Intelligence SHALL support required capture checklists for inspection templates.

Priority:
Critical

Verification:
Functional Test

---

## Requirement

ID: REQ-DI-0602

Title:
Exterior Capture Positions

Statement:
Damage Intelligence SHALL support standard exterior capture positions including front, rear, left side, right side, and corner views.

Priority:
Critical

Verification:
Workflow Test

---

## Requirement

ID: REQ-DI-0603

Title:
Instrument Capture

Statement:
Damage Intelligence SHALL support odometer and fuel or battery indicator capture where required by inspection workflow.

Priority:
Critical

Verification:
Functional Test

---

## Requirement

ID: REQ-DI-0604

Title:
Close-Up Damage Capture

Statement:
Damage Intelligence SHOULD support close-up image capture for visible damage.

Priority:
High

Verification:
Functional Test

---

## Requirement

ID: REQ-DI-0605

Title:
Image Quality Validation

Statement:
Damage Intelligence SHOULD validate captured image quality before inspection submission.

Priority:
High

Verification:
Image Quality Test

---

## Requirement

ID: REQ-DI-0606

Title:
Image Metadata

Statement:
Every captured inspection image SHALL be associated with required metadata.

Priority:
Critical

Verification:
Data Review

---

## Requirement

ID: REQ-DI-0607

Title:
Evidence Integrity

Statement:
Captured inspection evidence SHALL be protected from unauthorized alteration.

Priority:
Critical

Verification:
Security Review

---

## Requirement

ID: REQ-DI-0608

Title:
Offline Capture

Statement:
Damage Intelligence SHOULD support secure offline capture and later synchronization where operationally required.

Priority:
Medium

Verification:
Offline Workflow Test

---

## Requirement

ID: REQ-DI-0609

Title:
Capture Template Configuration

Statement:
Damage Intelligence SHOULD support configurable capture templates by inspection type, tenant, branch, or vehicle type.

Priority:
High

Verification:
Configuration Review

---

## Requirement

ID: REQ-DI-0610

Title:
Guided Capture Experience

Statement:
Damage Intelligence SHALL provide guided capture instructions for required inspection images.

Priority:
Critical

Verification:
UX Review

---

## Requirement

ID: REQ-DI-0611

Title:
Recapture Request

Statement:
Damage Intelligence SHOULD request recapture when required images fail critical quality checks.

Priority:
High

Verification:
Workflow Test

---

## Requirement

ID: REQ-DI-0612

Title:
Capture Override Audit

Statement:
Any user override of capture or quality requirements SHALL be audited.

Priority:
Critical

Verification:
Audit Review

---

## Requirement

ID: REQ-DI-0613

Title:
Secure Image Upload

Statement:
Inspection images SHALL be uploaded using secure transmission and stored using access-controlled storage.

Priority:
Critical

Verification:
Security Test

---

## Requirement

ID: REQ-DI-0614

Title:
Capture Audit Trail

Statement:
Damage Intelligence SHALL audit significant capture actions.

Priority:
Critical

Verification:
Audit Review

---

## Requirement

ID: REQ-DI-0615

Title:
Capture Compliance Metrics

Statement:
Damage Intelligence SHOULD track capture compliance metrics.

Priority:
Medium

Verification:
Report Review

---

# Business Rules

## BR-DI-0200 — Required Evidence Must Be Captured

Required inspection images SHALL be captured before inspection submission unless an authorized override is recorded.

---

## BR-DI-0201 — Poor Image Quality Requires Action

Images failing critical quality checks SHOULD require recapture or an override reason.

---

## BR-DI-0202 — Approved Evidence Must Not Be Overwritten

Approved inspection evidence SHALL NOT be overwritten.

---

## BR-DI-0203 — Close-Up Required for Visible Damage

When visible damage is manually reported during capture, close-up evidence SHOULD be captured.

---

## BR-DI-0204 — Offline Evidence Must Sync Before AI Analysis

Offline-captured evidence SHALL be synchronized before server-side AI analysis begins.

---

# AI Implementation Contract

AI development agents SHALL:

- Treat this document as the authoritative standard for vehicle image capture.
- Preserve all capture position IDs.
- Preserve all requirement IDs.
- Generate future mobile, API, database, and test specifications consistent with this capture standard.
- Not weaken evidence integrity requirements.
- Not bypass required capture checklist behavior unless an approved business rule allows override.
- Preserve offline capture and audit requirements.
- Raise ambiguity if capture template behavior or required images are unclear.

---

# References

- DI-0001 – Damage Intelligence Product Vision
- DI-0002 – Damage Intelligence Business Requirements
- DI-0004 – Damage Intelligence Inspection Workflow
- DI-0005 – AI Damage Detection
- DI-0006 – Damage Comparison
- GEES-0005 – AI Engineering Standard
- GEES-0007 – Enterprise Security Standard
- PLATFORM-0005 – GEES Core and Application Architecture

---

# Revision History

| Version | Date | Description |
|----------|------|-------------|
| 1.0.0 | 2026-06-27 | Initial Damage Intelligence Vehicle Capture Standards |
