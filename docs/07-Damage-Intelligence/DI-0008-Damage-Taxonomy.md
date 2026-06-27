---
id: DI-0008
title: Damage Intelligence Damage Taxonomy
version: 1.0.0
document_type: Product Specification
document_class: Taxonomy Specification
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
  - DI-0004
  - DI-0005
  - DI-0006
  - DI-0007
  - RA-0001
  - RA-0002
  - GEES-0005
---

# Damage Intelligence Damage Taxonomy

## Executive Summary

This document defines the standardized damage taxonomy used by Damage Intelligence.

The taxonomy provides a controlled vocabulary for classifying visible vehicle damage, affected vehicle areas, damage attributes, severity indicators, review status, comparison outcomes, evidence types, and repair relevance.

A consistent taxonomy is essential for:

- AI damage detection.
- Human review.
- Damage comparison.
- Damage case management.
- Reporting.
- Maintenance routing.
- Customer dispute evidence.
- Repair estimation.
- Model evaluation.
- Analytics.

All Damage Intelligence specifications, APIs, databases, UI screens, AI prompts, reports, and tests SHALL use the taxonomy defined in this document unless superseded by an approved later version.

---

# Purpose

The purpose of this document is to define a governed vocabulary for vehicle damage classification.

This taxonomy SHALL guide:

- AI output schemas.
- Damage finding data models.
- Damage case records.
- Review workflows.
- Reporting categories.
- Maintenance handoff.
- Search filters.
- Analytics dashboards.
- Test data.
- AI model evaluation.

---

# Scope

## In Scope

This taxonomy covers:

- Damage categories.
- Damage types.
- Vehicle exterior areas.
- Vehicle interior areas.
- Mechanical/visible condition categories.
- Damage attributes.
- Evidence types.
- Comparison outcomes.
- Review classifications.
- Repair relevance.
- AI uncertainty categories.
- Reporting labels.

## Out of Scope

This taxonomy does not define:

- Final repair cost.
- Final repair method.
- Legal liability.
- Customer charge rules.
- Insurance claim rules.
- Workshop labor codes.
- Manufacturer-specific repair procedures.
- Full mechanical diagnostic taxonomy.
- Telematics fault taxonomy.

Those SHALL be defined in later specifications where required.

---

# Taxonomy Principles

The Damage Taxonomy SHALL be:

1. Standardized
2. Human-readable
3. AI-consumable
4. Stable across workflows
5. Extensible
6. Traceable
7. Suitable for reporting
8. Suitable for maintenance routing
9. Suitable for comparison
10. Suitable for audit and dispute evidence

---

# Taxonomy Governance

The taxonomy SHALL be governed as an authoritative product artifact.

Changes to taxonomy values SHALL consider:

- Backward compatibility.
- Existing damage records.
- AI model outputs.
- Reports and dashboards.
- API consumers.
- Database constraints.
- User training.
- Maintenance integration.

Taxonomy values SHALL NOT be renamed or deleted without migration planning.

Deprecated values SHALL remain reserved.

---

# Taxonomy Structure

The Damage Taxonomy consists of the following layers:

```text
Damage Domain
    ↓
Damage Category
    ↓
Damage Type
    ↓
Vehicle Area
    ↓
Damage Attributes
    ↓
Severity
    ↓
Comparison Outcome
    ↓
Review Outcome
    ↓
Repair Relevance
```

---

# Damage Category

Damage Category is the highest-level grouping of visible condition issues.

| Code | Category | Description |
|------|----------|-------------|
| BODY | Body Damage | Damage to exterior panels, bumpers, bodywork, or trim |
| GLASS | Glass Damage | Damage to windshield, windows, mirrors, or glass surfaces |
| LIGHTING | Lighting Damage | Damage to headlights, tail lights, indicators, reflectors |
| WHEEL_TIRE | Wheel and Tire Damage | Damage to wheels, rims, tires, hubcaps |
| PAINT_SURFACE | Paint and Surface Damage | Paint scratches, transfer, peeling, discoloration |
| INTERIOR | Interior Damage | Seats, dashboard, trim, upholstery, interior panels |
| UNDERBODY | Underbody or Low Area Damage | Lower bumper, undertray, visible low components |
| FLUID | Fluid Evidence | Visible leak or fluid residue |
| MISSING_PART | Missing Part | Missing trim, badge, cover, cap, mirror part |
| UNKNOWN | Unknown or Unclassified | Visible abnormality requiring review |

---

# Damage Types

## Body Damage Types

| Code | Damage Type | Description |
|------|-------------|-------------|
| SCRATCH | Scratch | Linear surface damage or paint mark |
| DENT | Dent | Depressed or deformed body panel |
| CRACK | Crack | Crack in body panel, bumper, trim, or plastic component |
| DEFORMATION | Deformation | Bent or distorted part shape |
| BROKEN_PART | Broken Part | Component visibly broken or fragmented |
| MISALIGNMENT | Misalignment | Panel gap, bumper displacement, or part misalignment |
| HOLE | Hole | Visible puncture or missing material |
| SCUFF | Scuff | Surface abrasion usually on bumper or trim |

---

## Paint and Surface Damage Types

| Code | Damage Type | Description |
|------|-------------|-------------|
| PAINT_TRANSFER | Paint Transfer | Foreign paint or material transferred onto vehicle |
| PAINT_PEEL | Paint Peel | Paint peeling or flaking |
| PAINT_CHIP | Paint Chip | Small localized missing paint |
| DISCOLORATION | Discoloration | Unusual visible color change |
| SURFACE_STAIN | Surface Stain | Persistent visible stain or mark |
| RUST | Rust | Visible corrosion or oxidation |
| CLEAR_COAT_DAMAGE | Clear Coat Damage | Surface layer damage without obvious dent |

---

## Glass Damage Types

| Code | Damage Type | Description |
|------|-------------|-------------|
| GLASS_CRACK | Glass Crack | Crack in windshield, window, or glass |
| GLASS_CHIP | Glass Chip | Small chip or impact mark in glass |
| GLASS_SHATTERED | Shattered Glass | Broken or shattered glass |
| GLASS_SCRATCH | Glass Scratch | Scratch on glass surface |
| MIRROR_GLASS_DAMAGE | Mirror Glass Damage | Damaged mirror glass |

---

## Lighting Damage Types

| Code | Damage Type | Description |
|------|-------------|-------------|
| LIGHT_CRACK | Light Crack | Crack in light lens |
| LIGHT_BROKEN | Broken Light | Broken or missing light lens or assembly |
| LIGHT_SCRATCH | Light Scratch | Scratch on light lens |
| LIGHT_MISSING | Missing Light | Light or reflector missing |
| LIGHT_MISALIGNED | Misaligned Light | Light unit appears displaced |

---

## Wheel and Tire Damage Types

| Code | Damage Type | Description |
|------|-------------|-------------|
| WHEEL_RASH | Wheel Rash | Scrape or curb rash on wheel rim |
| WHEEL_DENT | Wheel Dent | Bent or dented wheel rim |
| WHEEL_CRACK | Wheel Crack | Crack on wheel rim |
| HUBCAP_DAMAGE | Hubcap Damage | Damaged hubcap or wheel cover |
| TIRE_CUT | Tire Cut | Visible cut in tire |
| TIRE_BULGE | Tire Bulge | Visible sidewall bulge |
| TIRE_TEAR | Tire Tear | Torn tire surface |
| TIRE_LOW_TREAD | Low Tire Tread | Visibly low tread condition |
| TIRE_FLAT | Flat Tire | Tire appears deflated |

---

## Interior Damage Types

| Code | Damage Type | Description |
|------|-------------|-------------|
| SEAT_TEAR | Seat Tear | Tear in seat material |
| SEAT_STAIN | Seat Stain | Visible stain on seat |
| BURN_MARK | Burn Mark | Burn mark on interior surface |
| INTERIOR_SCRATCH | Interior Scratch | Scratch on interior trim or panel |
| TRIM_BROKEN | Broken Interior Trim | Broken interior plastic or trim |
| MISSING_INTERIOR_PART | Missing Interior Part | Missing interior component |
| DASHBOARD_DAMAGE | Dashboard Damage | Damage to dashboard |
| FLOOR_DAMAGE | Floor Damage | Damage to floor mat or carpet |

---

## Missing Part Types

| Code | Damage Type | Description |
|------|-------------|-------------|
| MISSING_TRIM | Missing Trim | Exterior or interior trim missing |
| MISSING_BADGE | Missing Badge | Vehicle badge/emblem missing |
| MISSING_MIRROR_COVER | Missing Mirror Cover | Side mirror cover missing |
| MISSING_CAP | Missing Cap | Fuel cap, wheel cap, or cover missing |
| MISSING_SENSOR_COVER | Missing Sensor Cover | Sensor cover or cap missing |
| MISSING_LICENSE_PLATE | Missing License Plate | License plate missing or detached |

---

## Fluid and Leak Evidence Types

| Code | Damage Type | Description |
|------|-------------|-------------|
| FLUID_LEAK | Fluid Leak | Visible fluid leak under or near vehicle |
| OIL_RESIDUE | Oil Residue | Visible oil-like residue |
| COOLANT_RESIDUE | Coolant Residue | Visible coolant-like residue |
| UNKNOWN_FLUID | Unknown Fluid | Unknown visible fluid evidence |

---

## Unknown Damage Types

| Code | Damage Type | Description |
|------|-------------|-------------|
| UNKNOWN_DAMAGE | Unknown Damage | Visible abnormality not classified |
| POSSIBLE_DAMAGE | Possible Damage | Suspected damage requiring review |
| IMAGE_ARTIFACT | Image Artifact | Visual issue likely caused by image quality |
| REVIEW_REQUIRED | Review Required | Cannot classify automatically |

---

# Vehicle Area Taxonomy

## Exterior Areas

| Code | Vehicle Area | Description |
|------|--------------|-------------|
| FRONT_BUMPER | Front Bumper | Front bumper area |
| REAR_BUMPER | Rear Bumper | Rear bumper area |
| HOOD | Hood | Engine hood/bonnet |
| TRUNK | Trunk | Trunk lid or tailgate |
| ROOF | Roof | Roof panel |
| WINDSHIELD | Windshield | Front glass |
| REAR_GLASS | Rear Glass | Rear window glass |
| LEFT_FRONT_FENDER | Left Front Fender | Left front fender |
| RIGHT_FRONT_FENDER | Right Front Fender | Right front fender |
| LEFT_REAR_QUARTER | Left Rear Quarter Panel | Left rear quarter panel |
| RIGHT_REAR_QUARTER | Right Rear Quarter Panel | Right rear quarter panel |
| LEFT_FRONT_DOOR | Left Front Door | Driver-side/front-left door based on vehicle orientation |
| RIGHT_FRONT_DOOR | Right Front Door | Front-right door |
| LEFT_REAR_DOOR | Left Rear Door | Rear-left door |
| RIGHT_REAR_DOOR | Right Rear Door | Rear-right door |
| LEFT_MIRROR | Left Mirror | Left side mirror |
| RIGHT_MIRROR | Right Mirror | Right side mirror |
| FRONT_LEFT_WHEEL | Front Left Wheel | Front-left wheel/rim/tire area |
| FRONT_RIGHT_WHEEL | Front Right Wheel | Front-right wheel/rim/tire area |
| REAR_LEFT_WHEEL | Rear Left Wheel | Rear-left wheel/rim/tire area |
| REAR_RIGHT_WHEEL | Rear Right Wheel | Rear-right wheel/rim/tire area |
| LEFT_HEADLIGHT | Left Headlight | Left front light |
| RIGHT_HEADLIGHT | Right Headlight | Right front light |
| LEFT_TAIL_LIGHT | Left Tail Light | Left rear light |
| RIGHT_TAIL_LIGHT | Right Tail Light | Right rear light |
| FRONT_LICENSE_PLATE | Front License Plate | Front plate area |
| REAR_LICENSE_PLATE | Rear License Plate | Rear plate area |
| UNDERBODY_VISIBLE | Visible Underbody | Visible lower/underbody area |

---

## Interior Areas

| Code | Vehicle Area | Description |
|------|--------------|-------------|
| DRIVER_SEAT | Driver Seat | Driver seat area |
| PASSENGER_SEAT | Passenger Seat | Front passenger seat |
| REAR_SEATS | Rear Seats | Rear seating area |
| DASHBOARD | Dashboard | Dashboard area |
| CENTER_CONSOLE | Center Console | Console area |
| STEERING_WHEEL | Steering Wheel | Steering wheel area |
| DOOR_TRIM | Door Trim | Interior door trim |
| FLOOR_CARPET | Floor/Carpet | Interior flooring |
| TRUNK_INTERIOR | Trunk Interior | Cargo/trunk interior |
| INTERIOR_ROOF | Interior Roof | Headliner/interior roof |

---

## Generic Area Values

The system MAY use generic area values where exact panel identification is not possible.

| Code | Area | Description |
|------|------|-------------|
| FRONT | Front | General front area |
| REAR | Rear | General rear area |
| LEFT_SIDE | Left Side | General left side |
| RIGHT_SIDE | Right Side | General right side |
| INTERIOR_GENERAL | Interior General | General interior |
| UNKNOWN_AREA | Unknown Area | Area cannot be determined |

---

# Damage Attributes

Damage findings MAY include attributes to improve classification, review, reporting, and repair estimation.

## Size Attribute

| Code | Meaning |
|------|---------|
| VERY_SMALL | Very small visible damage |
| SMALL | Small damage |
| MEDIUM | Medium damage |
| LARGE | Large damage |
| EXTENSIVE | Extensive damage |
| UNKNOWN_SIZE | Size cannot be determined |

---

## Depth Attribute

| Code | Meaning |
|------|---------|
| SURFACE | Surface level |
| SHALLOW | Shallow visible damage |
| DEEP | Deep visible damage |
| PENETRATING | Penetrates surface or component |
| UNKNOWN_DEPTH | Depth cannot be determined |

---

## Length Attribute

| Code | Meaning |
|------|---------|
| SHORT | Short visible mark |
| MEDIUM_LENGTH | Medium length |
| LONG | Long visible mark |
| UNKNOWN_LENGTH | Length cannot be determined |

---

## Spread Attribute

| Code | Meaning |
|------|---------|
| LOCALIZED | Localized to small area |
| PANEL_LEVEL | Covers significant panel area |
| MULTI_PANEL | Extends across multiple panels |
| UNKNOWN_SPREAD | Spread cannot be determined |

---

## Visibility Attribute

| Code | Meaning |
|------|---------|
| CLEARLY_VISIBLE | Easily visible |
| PARTIALLY_VISIBLE | Partially visible |
| LOW_VISIBILITY | Difficult to see |
| OBSTRUCTED | Obstructed |
| UNKNOWN_VISIBILITY | Visibility cannot be determined |

---

# Severity Levels

Damage severity is formally defined in:

```text
DI-0009-Severity-Assessment.md
```

This taxonomy recognizes the following severity labels for consistency:

| Code | Severity |
|------|----------|
| MINOR | Minor |
| MODERATE | Moderate |
| MAJOR | Major |
| CRITICAL | Critical |
| UNKNOWN | Unknown |

Severity SHALL NOT be treated as final until the Severity Assessment specification is applied.

---

# Comparison Outcome Taxonomy

Damage comparison outcomes are formally defined in:

```text
DI-0006-Damage-Comparison.md
```

The standard outcome labels are:

| Code | Outcome |
|------|---------|
| NEW | New |
| PRE_EXISTING | Pre-existing |
| CHANGED | Changed |
| REPAIRED | Repaired |
| UNCERTAIN | Uncertain |
| NOT_COMPARABLE | Not Comparable |

---

# Review Outcome Taxonomy

Human review outcomes SHALL use standardized values.

| Code | Review Outcome | Description |
|------|----------------|-------------|
| CONFIRMED | Confirmed | Finding accepted |
| EDITED | Edited | Finding accepted with modifications |
| REJECTED | Rejected | Finding rejected |
| ESCALATED | Escalated | Requires higher review |
| ADDITIONAL_EVIDENCE_REQUIRED | Additional Evidence Required | More evidence required |
| DEFERRED | Deferred | Review postponed |
| CLOSED | Closed | Review completed |

---

# Repair Relevance Taxonomy

Damage findings MAY include repair relevance.

| Code | Repair Relevance | Description |
|------|------------------|-------------|
| NO_REPAIR_REQUIRED | No Repair Required | No immediate repair required |
| MONITOR | Monitor | Monitor condition |
| REPAIR_RECOMMENDED | Repair Recommended | Repair should be considered |
| REPAIR_REQUIRED | Repair Required | Repair required before release or according to policy |
| SAFETY_REVIEW_REQUIRED | Safety Review Required | Safety-related review required |
| UNKNOWN | Unknown | Repair relevance unknown |

---

# Evidence Type Taxonomy

Damage evidence SHALL be categorized.

| Code | Evidence Type | Description |
|------|---------------|-------------|
| FULL_VIEW_IMAGE | Full View Image | Standard full vehicle angle |
| CLOSE_UP_IMAGE | Close-Up Image | Close-up damage evidence |
| INTERIOR_IMAGE | Interior Image | Interior condition evidence |
| ODOMETER_IMAGE | Odometer Image | Mileage evidence |
| FUEL_BATTERY_IMAGE | Fuel/Battery Image | Fuel or battery level evidence |
| AI_FINDING | AI Finding | AI-generated damage finding |
| HUMAN_REVIEW_NOTE | Human Review Note | Reviewer note |
| COMPARISON_RESULT | Comparison Result | Historical comparison result |
| REPAIR_PHOTO | Repair Photo | Repair-related evidence |
| REPORT | Report | Generated report |

---

# AI Confidence Labels

AI confidence MAY be represented using labels.

| Code | Meaning |
|------|---------|
| HIGH | High confidence |
| MEDIUM | Medium confidence |
| LOW | Low confidence |
| UNKNOWN | Confidence unavailable |

Numeric confidence scores SHOULD also be stored where available.

---

# AI Uncertainty Reasons

AI systems SHOULD classify uncertainty reasons where possible.

| Code | Reason |
|------|--------|
| POOR_LIGHTING | Poor lighting |
| BLUR | Image blur |
| GLARE | Glare or reflection |
| OBSTRUCTION | Obstruction |
| LOW_RESOLUTION | Low resolution |
| WRONG_ANGLE | Wrong capture angle |
| DIRTY_SURFACE | Dirty vehicle surface |
| WATER_OR_RAIN | Water or rain affects visibility |
| PARTIAL_VIEW | Partial vehicle view |
| MISSING_HISTORY | Missing historical evidence |
| CONFLICTING_EVIDENCE | Conflicting evidence |
| MODEL_UNCERTAIN | Model uncertainty |
| UNKNOWN_REASON | Unknown reason |

---

# Damage Finding Record Minimum Classification

Every damage finding SHOULD include:

- Damage Type
- Damage Category
- Vehicle Area
- Severity Suggestion
- Confidence
- Evidence Reference
- Review Status
- Comparison Outcome where applicable
- Repair Relevance where applicable
- Source

Source MAY be:

| Code | Source |
|------|--------|
| AI | AI-generated |
| HUMAN | Human-created |
| IMPORTED | Imported from external system |
| SYSTEM | System-generated |
| HYBRID | AI-generated and human-reviewed |

---

# Taxonomy Usage Rules

## Rule 1 — Use Standard Codes

Systems SHALL store taxonomy codes, not only display labels.

## Rule 2 — Preserve Labels

Systems SHOULD preserve display labels for reporting and UI.

## Rule 3 — Avoid Free Text for Taxonomy Values

Free text SHALL NOT replace governed taxonomy values.

## Rule 4 — Unknown Is Better Than Guessing

If the system cannot determine a value, it SHALL use an appropriate unknown or uncertain value.

## Rule 5 — Deprecated Codes Remain Reserved

Deprecated taxonomy codes SHALL NOT be reused.

---

# Localization

Taxonomy labels SHOULD support localization.

Initial supported languages SHOULD include:

- English
- Arabic

Taxonomy codes SHALL remain language-neutral.

Example:

| Code | English | Arabic |
|------|---------|--------|
| SCRATCH | Scratch | خدش |
| DENT | Dent | انبعاج |
| CRACK | Crack | كسر / شرخ |

Arabic labels SHALL be reviewed by qualified domain and language reviewers before production use.

---

# Reporting Implications

Reports SHALL use taxonomy codes consistently.

Reports MAY group damage by:

- Damage Category
- Damage Type
- Vehicle Area
- Severity
- Branch
- Vehicle
- Rental Agreement
- Review Outcome
- Comparison Outcome
- Repair Relevance

---

# AI Model Implications

AI models and AI prompts SHALL map outputs to approved taxonomy values.

AI systems SHALL NOT introduce unapproved damage categories without governance review.

If AI detects a damage type outside the taxonomy, it SHOULD classify it as:

```text
UNKNOWN_DAMAGE
```

or

```text
POSSIBLE_DAMAGE
```

and route it for review.

---

# API Implications

APIs SHOULD expose taxonomy codes using stable enum-like values.

APIs SHOULD include display labels where needed.

APIs SHOULD support retrieval of active taxonomy values.

APIs SHOULD support taxonomy versioning.

---

# Database Implications

Database design SHOULD store:

- Taxonomy code
- Taxonomy version
- Display label where necessary
- Deprecated status where applicable

Historical records SHALL preserve the taxonomy value used at the time of decision.

---

# Governance and Change Control

Taxonomy changes SHALL follow governance review.

Changes requiring review include:

- New damage type
- Renamed label
- Deprecated code
- New vehicle area
- New severity label
- New comparison outcome
- New review outcome
- New repair relevance value

Taxonomy updates SHALL include migration impact assessment.

---

# Normative Requirements

## Requirement

ID: REQ-DI-0700

Title:
Standard Damage Taxonomy

Statement:
Damage Intelligence SHALL use a governed taxonomy for damage categories, damage types, vehicle areas, review outcomes, and comparison outcomes.

Priority:
Critical

Verification:
Data Review

---

## Requirement

ID: REQ-DI-0701

Title:
Standard Damage Type Codes

Statement:
Damage Intelligence SHALL use stable damage type codes for structured damage findings.

Priority:
Critical

Verification:
API/Data Review

---

## Requirement

ID: REQ-DI-0702

Title:
Vehicle Area Taxonomy

Statement:
Damage Intelligence SHALL use standardized vehicle area codes where damage location is recorded.

Priority:
Critical

Verification:
Data Review

---

## Requirement

ID: REQ-DI-0703

Title:
Unknown Classification

Statement:
Damage Intelligence SHALL support unknown or uncertain taxonomy values when accurate classification is not possible.

Priority:
High

Verification:
AI Governance Review

---

## Requirement

ID: REQ-DI-0704

Title:
Taxonomy Versioning

Statement:
Damage Intelligence SHOULD support taxonomy versioning for damage records.

Priority:
High

Verification:
Architecture Review

---

## Requirement

ID: REQ-DI-0705

Title:
Taxonomy Localization

Statement:
Damage Intelligence SHOULD support localized display labels for taxonomy values where required.

Priority:
Medium

Verification:
UX Review

---

## Requirement

ID: REQ-DI-0706

Title:
AI Taxonomy Compliance

Statement:
AI-generated damage findings SHALL map to approved taxonomy values.

Priority:
Critical

Verification:
AI Review

---

## Requirement

ID: REQ-DI-0707

Title:
No Unapproved Taxonomy Expansion

Statement:
Systems and AI agents SHALL NOT introduce new taxonomy values without governance approval.

Priority:
Critical

Verification:
Governance Review

---

## Requirement

ID: REQ-DI-0708

Title:
Historical Taxonomy Preservation

Statement:
Historical damage records SHALL preserve the taxonomy values used at the time of recording.

Priority:
High

Verification:
Data Review

---

## Requirement

ID: REQ-DI-0709

Title:
Review Outcome Taxonomy

Statement:
Human review outcomes SHALL use standardized review outcome values.

Priority:
High

Verification:
Workflow Review

---

## Requirement

ID: REQ-DI-0710

Title:
Repair Relevance Taxonomy

Statement:
Damage Intelligence SHOULD classify repair relevance using standardized values.

Priority:
Medium

Verification:
Maintenance Review

---

# Business Rules

## BR-DI-0300 — Standard Codes Required

Damage findings SHALL use approved taxonomy codes.

---

## BR-DI-0301 — Unknown Is Allowed

When classification cannot be determined reliably, the system SHALL use an unknown or uncertain taxonomy value rather than guessing.

---

## BR-DI-0302 — AI Must Map to Taxonomy

AI outputs SHALL be mapped to approved taxonomy values before storage.

---

## BR-DI-0303 — Taxonomy Codes Are Stable

Taxonomy codes SHALL NOT be reused after deprecation.

---

## BR-DI-0304 — Human Review Can Correct Classification

Authorized reviewers MAY correct AI-generated taxonomy classification.

---

# AI Implementation Contract

AI development agents SHALL:

- Treat this document as the authoritative damage taxonomy.
- Preserve all taxonomy codes.
- Preserve all requirement IDs.
- Generate future AI prompts, schemas, APIs, tests, UI filters, and reports using these taxonomy values.
- Not invent unapproved damage types or vehicle areas.
- Use UNKNOWN_DAMAGE, POSSIBLE_DAMAGE, UNKNOWN_AREA, or UNKNOWN_REASON where classification is uncertain.
- Preserve taxonomy versioning requirements.
- Preserve localization and reporting implications.
- Raise ambiguity when taxonomy values are insufficient.

---

# References

- DI-0005 – AI Damage Detection
- DI-0006 – Damage Comparison
- DI-0007 – Vehicle Capture Standards
- DI-0009 – Severity Assessment
- GEES-0005 – AI Engineering Standard
- GEES-0013 – Business Rule Engineering Standard

---

# Revision History

| Version | Date | Description |
|----------|------|-------------|
| 1.0.0 | 2026-06-27 | Initial Damage Intelligence Damage Taxonomy |
