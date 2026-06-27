---
id: "DI-0030"
title: "Damage Intelligence Glossary and Terminology"
version: "1.0.0"
document_type: "Product Specification"
document_class: "Glossary and Terminology"
status: "Draft"
classification: "Internal"
owner: "Riyadah Technology"
reviewers: "Chief Enterprise Architect, Product Owner, Damage Intelligence Lead, CROMS Lead, Maintenance Lead, AI Engineering Lead, QA Lead, Security Lead, Arabic Localization Lead"
approvers: ""
created: "2026-06-27"
updated: "2026-06-27"
authoritative: true
ai_consumable: true
related: "DI-0001, DI-0002, DI-0003, DI-0004, DI-0005, DI-0006, DI-0007, DI-0008, DI-0009, DI-0010, DI-0011, DI-0012, DI-0013, DI-0014, DI-0015, DI-0016, DI-0017, DI-0018, DI-0019, DI-0020, DI-0021, DI-0022, DI-0023, DI-0024, DI-0025, DI-0026, DI-0027, DI-0028, DI-0029, GEES-0007, GEES-0009, PLATFORM-0005"
---

# Damage Intelligence Glossary and Terminology

## Executive Summary

This document defines the glossary, terminology, stable codes, and approved meaning of key terms used across Damage Intelligence.

The glossary SHALL ensure consistent understanding across product, engineering, QA, AI engineering, security, operations, CROMS, Maintenance, reporting, audit, localization, and executive stakeholders.

This document SHALL be used by human teams and AI development agents to avoid ambiguity in requirements, user stories, APIs, events, reports, dashboards, test cases, and implementation artifacts.

Stable technical codes SHALL remain language-neutral. Display labels MAY be localized.

---

# Purpose

The purpose of this document is to define a shared vocabulary for Damage Intelligence.

This specification SHALL guide:

- Product requirements.
- User stories.
- API naming.
- Event naming.
- Domain model naming.
- UI labels.
- Report labels.
- Dashboard labels.
- QA test cases.
- AI prompts and implementation plans.
- Arabic localization.
- Training material.
- Support documentation.

---

# Scope

## In Scope

This glossary covers:

- Product terms.
- Inspection terms.
- Vehicle capture terms.
- Evidence terms.
- AI terms.
- Damage taxonomy terms.
- Severity terms.
- Comparison terms.
- Damage case terms.
- Human review terms.
- Repair estimate terms.
- CROMS integration terms.
- Maintenance integration terms.
- Security terms.
- Privacy terms.
- Audit terms.
- Reporting terms.
- Retention terms.
- Operational terms.
- Localization terms.
- Stable codes.

## Out of Scope

This document does not define:

- Final UI copy.
- Final Arabic translation approval.
- Final database schema.
- Final OpenAPI schema.
- Final event payload schema.
- Final report template wording.
- Final legal terminology.
- Final insurance terminology.

---

# Glossary Principles

Damage Intelligence terminology SHALL follow these principles:

1. Use one approved term for each concept.
2. Preserve stable codes.
3. Separate internal codes from display labels.
4. Avoid ambiguous business meaning.
5. Avoid using AI output as final liability language.
6. Preserve ownership boundaries.
7. Support Arabic localization without changing codes.
8. Keep terms traceable to requirements.
9. Use domain language consistently.
10. Review terminology changes before implementation.

---

# Stable Codes and Labels

Stable codes SHALL be used in:

- Domain objects.
- APIs.
- Events.
- Audit records.
- Reports where technical traceability is required.
- Test cases.
- Configuration.
- Data storage.

Localized labels MAY be used in:

- User interfaces.
- Reports.
- Dashboards.
- Notifications.
- Mobile capture screens.
- Customer-facing content.

Stable codes SHALL NOT be translated.

---

# Core Product Terms

| Term | Definition |
|------|------------|
| Damage Intelligence | The product capability that captures inspection evidence, detects damage, compares damage, manages damage cases, supports review, integrates with CROMS and Maintenance, and produces reports. |
| Inspection | A structured process for capturing vehicle condition evidence. |
| Evidence | Images, metadata, reports, findings, review decisions, and audit records used to support vehicle condition assessment. |
| Damage Finding | A structured record describing observed or suspected damage on a vehicle. |
| Damage Case | A managed business case created around confirmed, suspected, disputed, or repair-relevant damage. |
| Damage Comparison | The process of comparing current vehicle evidence against baseline or historical evidence. |
| AI Analysis | Automated or AI-assisted processing of inspection evidence to identify possible damage or quality issues. |
| Human Review | Review performed by an authorized person to confirm, reject, edit, or escalate AI or comparison outputs. |
| Advisory Output | A result that supports decision-making but is not final liability, billing, or repair cost determination. |
| Maintenance Handoff | Controlled transfer of damage evidence and context to Maintenance for repair review or work order workflow. |

---

# Inspection Terms

| Term | Definition |
|------|------------|
| Inspection Session | A lifecycle object representing one vehicle inspection process. |
| Check-Out Inspection | Inspection performed before a vehicle is handed to a renter, driver, or customer. |
| Check-In Inspection | Inspection performed when a vehicle is returned. |
| Maintenance Intake Inspection | Inspection performed when a vehicle enters Maintenance workflow. |
| Maintenance Quality Inspection | Inspection performed after repair to verify condition or repair completion. |
| Ad Hoc Inspection | Inspection performed outside a standard rental or maintenance workflow. |
| Capture Checklist | Required and optional capture positions for an inspection. |
| Capture Position | A defined vehicle angle, area, or required photo position. |
| Inspection Status | The current lifecycle state of an inspection session. |
| Required Capture | A mandatory image or evidence item required by the capture template. |
| Optional Capture | A non-mandatory image or evidence item. |
| Recapture | Re-taking an image because the original image failed quality or completeness checks. |
| Inspection Submission | The action of submitting captured evidence for processing, review, comparison, or reporting. |

---

# Vehicle Capture Terms

| Term | Definition |
|------|------------|
| Capture Template | A configured set of required and optional capture positions for an inspection type. |
| Front Capture | Image showing the front side of the vehicle. |
| Rear Capture | Image showing the rear side of the vehicle. |
| Left Side Capture | Image showing the left side of the vehicle. |
| Right Side Capture | Image showing the right side of the vehicle. |
| Odometer Capture | Image showing the vehicle odometer reading. |
| Fuel or Battery Capture | Image showing fuel level, battery level, or energy level. |
| Close-Up Capture | Detailed image focused on a specific damage area. |
| Capture Metadata | Metadata describing image capture context such as timestamp, user, position, and inspection session. |
| Image Quality Result | Result of quality validation applied to an image. |
| Quality Failure Reason | Reason an image failed quality validation, such as blur, low light, obstruction, or incorrect angle. |

---

# Evidence Terms

| Term | Definition |
|------|------------|
| Inspection Image | Image captured or uploaded as part of an inspection session. |
| Evidence Package | Controlled set of evidence records shared with reviewers, CROMS, Maintenance, or reports. |
| Evidence Reference | Secure reference to evidence, not a public URL. |
| Evidence Integrity | Protection against silent modification, overwrite, loss, or unauthorized deletion of evidence. |
| Evidence Access | Authorized viewing, retrieval, or export of evidence. |
| Evidence Supersession | Relationship showing that one evidence item replaced or superseded another while preserving history. |
| Baseline Evidence | Previous inspection evidence used for comparison. |
| Current Evidence | Evidence captured in the current inspection. |
| Historical Evidence | Evidence captured in prior inspections. |
| Evidence Chain of Custody | Traceability of evidence capture, access, review, use, and retention. |

---

# AI Terms

| Term | Definition |
|------|------------|
| AI Damage Detection | AI-assisted identification of possible vehicle damage from inspection images. |
| AI Finding | Structured finding generated by AI analysis. |
| Confidence Score | Numeric or categorical value indicating AI confidence in an output. |
| Low Confidence | AI output below configured threshold requiring human review or caution. |
| Uncertainty Reason | Explanation or category indicating why AI confidence is limited. |
| AI Model Version | Version or identifier of the AI model, engine, or provider used. |
| AI Provider | External or internal AI service used to process evidence. |
| AI Failure | Failure of AI request, processing, timeout, provider, or output generation. |
| AI Review Routing | Routing AI output to human review based on confidence, severity, policy, or risk. |
| AI Quality Metric | Measurement of AI performance such as confirmation rate, rejection rate, edit rate, false positives, or false negatives. |
| Advisory AI | AI output used to assist decisions but not to make final customer liability, billing, or actual repair cost decisions. |

---

# Damage Taxonomy Terms

| Term | Definition |
|------|------------|
| Damage Type | Classification of damage such as scratch, dent, crack, broken light, or missing part. |
| Vehicle Area | Standardized vehicle location where damage appears. |
| Damage Category | Higher-level grouping of damage types. |
| Scratch | Surface-level mark or abrasion. |
| Dent | Deformation or indentation in vehicle body. |
| Crack | Break, split, or fracture in material. |
| Broken Light | Damaged, broken, or non-functional light component. |
| Missing Part | Vehicle part that is absent or detached. |
| Paint Damage | Damage affecting vehicle paint surface. |
| Glass Damage | Damage affecting windshield, window, mirror, or glass component. |
| Tire or Wheel Damage | Damage affecting tire, rim, wheel cover, or related area. |
| Interior Damage | Damage inside the vehicle cabin. |
| Unknown Damage | Damage that cannot be confidently classified. |

---

# Severity Terms

| Term | Definition |
|------|------------|
| Severity | Assessment of damage seriousness or operational impact. |
| Minor | Low-impact damage, usually cosmetic or low risk. |
| Moderate | Damage requiring attention but not necessarily safety-critical. |
| Major | Significant damage that may require repair, escalation, or operational restriction. |
| Critical | Severe or safety-relevant damage requiring urgent review or action. |
| Unknown Severity | Severity cannot be determined from available evidence. |
| Safety-Relevant Damage | Damage that may affect safe vehicle operation. |
| Severity Override | Human change to an AI-suggested or system-assigned severity. |

---

# Damage Comparison Terms

| Term | Definition |
|------|------------|
| Baseline Selection | Process of selecting prior evidence for comparison. |
| Comparison Outcome | Result of comparing current evidence against baseline or historical evidence. |
| New Damage | Damage that appears in current evidence and was not present in baseline evidence. |
| Pre-Existing Damage | Damage that existed in prior baseline evidence. |
| Changed Damage | Existing damage that has increased, worsened, moved, or changed in appearance. |
| Repaired Damage | Previously recorded damage that appears repaired or no longer visible. |
| Uncertain | Comparison cannot confidently determine outcome. |
| Not Comparable | Comparison cannot be performed due to missing, poor, incompatible, or insufficient evidence. |
| Missing Baseline | No valid prior evidence exists for comparison. |
| Comparison Review | Human review of comparison outputs. |

---

# Damage Case Terms

| Term | Definition |
|------|------------|
| Damage Case | Managed record for damage requiring review, tracking, reporting, dispute support, or maintenance routing. |
| Case Status | Current lifecycle state of a damage case. |
| Case Creation | Creation of a damage case from a finding, comparison, review, or business rule. |
| Case Confirmation | Human or authorized workflow confirmation that a damage case is valid. |
| Case Rejection | Decision that a damage case should not proceed as confirmed damage. |
| Case Escalation | Moving a case to higher review level due to severity, dispute, uncertainty, or policy. |
| Case Closure | Final closing of a case with outcome and reason. |
| Case Reopen | Reopening a previously closed case due to new evidence, dispute, or correction. |
| Duplicate Case | Multiple cases created for the same damage context where one case should exist. |
| Case Evidence | Evidence linked to a damage case. |

---

# Human Review Terms

| Term | Definition |
|------|------------|
| Reviewer | Authorized user who reviews findings, comparisons, cases, estimates, or reports. |
| Review Queue | Worklist containing items requiring human review. |
| Review Decision | Decision made by a reviewer, such as confirm, reject, edit, escalate, or request evidence. |
| Confirmed | Accepted as valid by reviewer or approved workflow. |
| Rejected | Not accepted as valid by reviewer or approved workflow. |
| Edited | Modified by reviewer from previous AI, comparison, or system output. |
| Escalated | Sent to higher authority or specialized review. |
| Additional Evidence Required | Status indicating that current evidence is insufficient. |
| Review Reason | Explanation provided by reviewer for decision or override. |
| Override | Human decision changing AI, system, or previous value. |

---

# Repair Estimate Terms

| Term | Definition |
|------|------------|
| Repair Estimate | Advisory estimate of possible repair cost or range. |
| Advisory Estimate | Estimate used for guidance, not final actual repair cost. |
| Estimate Range | Low and high estimated cost values. |
| Estimate Confidence | Confidence level of estimate quality. |
| Actual Repair Cost | Final or recorded repair cost owned by Maintenance or Finance, not Damage Intelligence. |
| Estimate Supersession | Actual cost or later estimate replacing earlier advisory estimate context. |
| Repair Relevance | Indicator that damage may require repair review. |
| Estimate Review | Human review of advisory estimate. |
| Estimate Disclaimer | Statement explaining that estimate is advisory. |

---

# CROMS Integration Terms

| Term | Definition |
|------|------------|
| CROMS | Car Rental Operations Management System. |
| Rental Agreement | Rental contract or rental workflow record owned by CROMS. |
| Rental Damage Summary | Damage Intelligence summary provided to CROMS for a rental agreement. |
| Check-Out Request | CROMS request to create or retrieve check-out inspection. |
| Check-In Request | CROMS request to create or retrieve check-in inspection. |
| Rental Closure | CROMS-owned rental closure workflow. |
| Customer Charge | Final customer charge decision owned outside Damage Intelligence. |
| Rental Dispute Evidence | Evidence used to support rental dispute review. |
| CROMS Callback | CROMS or Damage Intelligence callback used to exchange status updates. |
| CROMS Ownership Boundary | Rule that CROMS owns rental lifecycle and final rental decisions. |

---

# Maintenance Integration Terms

| Term | Definition |
|------|------------|
| Maintenance | GCU365 Maintenance system or workflow for repair review and work orders. |
| Maintenance Request | Request created or managed by Maintenance for repair review. |
| Work Order | Maintenance-owned record for repair execution. |
| Repair Status | Current status of repair workflow. |
| Maintenance Routing | Routing a damage case to Maintenance for repair review. |
| Evidence Handoff | Controlled sharing of evidence package with Maintenance. |
| Post-Repair Inspection | Inspection performed after repair completion. |
| Maintenance Rejection | Maintenance decision not to accept routed damage for repair workflow. |
| Work Order Reference | Identifier linking Damage Intelligence case to Maintenance work order. |
| Maintenance Ownership Boundary | Rule that Maintenance owns repair execution, work orders, and actual repair cost. |

---

# Security Terms

| Term | Definition |
|------|------------|
| Authentication | Verification of user or service identity. |
| Authorization | Permission check for action or object access. |
| Tenant Isolation | Separation of data and access between tenants. |
| Object-Level Authorization | Access control applied to a specific record or object. |
| Secure Evidence Access | Access to evidence only through authenticated, authorized, controlled methods. |
| Signed URL | Time-limited controlled access URL, not a permanent public URL. |
| Secret | Password, token, API key, storage key, credential, or private configuration value. |
| Privileged Action | High-risk action requiring elevated permission. |
| Security Event | Event related to security-relevant activity. |
| Cross-Tenant Access Attempt | Attempt to access data belonging to another tenant. |

---

# Privacy Terms

| Term | Definition |
|------|------------|
| Personal Data | Data related to an identifiable person. |
| Customer-Linked Data | Data associated with a customer, renter, driver, or individual. |
| Data Minimization | Processing only data required for the intended purpose. |
| Privacy by Design | Designing privacy controls into workflows from the start. |
| Customer-Facing Report | Report intended to be shared with a customer or external party. |
| Redaction | Removal or masking of sensitive information. |
| Sensitive Data Exposure | Unauthorized or unnecessary exposure of sensitive data. |
| Privacy Review | Review of data handling, minimization, and sharing controls. |

---

# Audit and Traceability Terms

| Term | Definition |
|------|------------|
| Audit Record | Record of a significant action, actor, object, tenant, timestamp, and context. |
| Traceability | Ability to follow a chain from requirement, workflow, evidence, decision, report, and audit. |
| Correlation ID | Identifier used to connect logs, events, API calls, jobs, reports, and audits. |
| Event ID | Unique identifier of a domain or integration event. |
| Actor | User, service, system, or process performing an action. |
| Audit Immutability | Protection against unauthorized alteration of audit records. |
| Tamper-Evident | Designed so unauthorized alteration can be detected. |
| Audit Access | Viewing or exporting audit records. |
| Requirement Traceability | Link between requirement IDs and implementation or testing artifacts. |

---

# Reporting Terms

| Term | Definition |
|------|------------|
| Damage Report | Report summarizing damage findings, evidence, review, and case status. |
| Inspection Summary Report | Report summarizing inspection evidence and status. |
| Vehicle Damage History Report | Report showing historical damage records for a vehicle. |
| Rental Damage Summary Report | Report or summary provided to CROMS for rental workflow. |
| Maintenance Handoff Report | Report or evidence package shared with Maintenance. |
| Dashboard | Visual operational or analytical view of KPIs and status. |
| KPI | Key performance indicator. |
| Report Export | Downloadable or generated report file. |
| Report Version | Version of report template or report output. |
| Report Expiration | Expiration or revocation of report access. |

---

# Retention Terms

| Term | Definition |
|------|------------|
| Retention Policy | Rule defining how long data is kept. |
| Archive | Moving data to controlled long-term storage. |
| Deletion Eligibility | Condition where data may be deleted under approved policy. |
| Legal Hold | Protection that blocks deletion due to legal or compliance need. |
| Dispute Hold | Protection that blocks deletion due to active dispute. |
| Soft Delete | Marking data as deleted while retaining recoverability. |
| Physical Delete | Permanent removal of data from active storage. |
| Archive Retrieval | Controlled process of retrieving archived data. |
| Retention Job | Scheduled or triggered process that evaluates archival or deletion. |

---

# Operational Terms

| Term | Definition |
|------|------------|
| Monitoring | Observing system health, workflow health, security, integrations, and performance. |
| Alert | Notification of a condition requiring attention. |
| Incident | Operational issue requiring triage, mitigation, or recovery. |
| Runbook | Operational guide for responding to incidents. |
| Disaster Recovery | Process for recovering systems after major failure. |
| Business Continuity | Process for continuing critical operations during disruption. |
| RTO | Recovery Time Objective. |
| RPO | Recovery Point Objective. |
| Degraded Mode | Limited operating state used when part of system is unavailable. |
| Manual Continuity | Approved manual process used during outage. |

---

# Localization Terms

| Term | Definition |
|------|------------|
| Localization | Adapting labels, formats, messages, reports, and UI for language or locale. |
| Locale | Language and regional setting such as en, ar, en-SA, or ar-SA. |
| Right-to-Left | Layout direction used for Arabic. |
| Stable Code | Language-neutral technical code. |
| Localized Label | Display label translated for a locale. |
| Translation Fallback | Safe fallback when translation is missing. |
| Arabic Support | Support for Arabic text, RTL layout, Arabic labels, and Arabic reports. |
| Mixed Direction Text | Text containing both Arabic RTL and English LTR content. |

---

# Stable Damage Type Codes

| Code | English Label | Arabic Label |
|------|---------------|--------------|
| SCRATCH | Scratch | خدش |
| DENT | Dent | انبعاج |
| CRACK | Crack | كسر أو تشقق |
| BROKEN_LIGHT | Broken light | مصباح مكسور |
| MISSING_PART | Missing part | قطعة مفقودة |
| PAINT_DAMAGE | Paint damage | تلف في الطلاء |
| GLASS_DAMAGE | Glass damage | تلف في الزجاج |
| TIRE_DAMAGE | Tire damage | تلف في الإطار |
| WHEEL_DAMAGE | Wheel damage | تلف في العجلة |
| INTERIOR_DAMAGE | Interior damage | تلف داخلي |
| UNKNOWN_DAMAGE | Unknown damage | تلف غير معروف |

---

# Stable Severity Codes

| Code | English Label | Arabic Label |
|------|---------------|--------------|
| MINOR | Minor | بسيط |
| MODERATE | Moderate | متوسط |
| MAJOR | Major | كبير |
| CRITICAL | Critical | حرج |
| UNKNOWN | Unknown | غير معروف |

---

# Stable Comparison Outcome Codes

| Code | English Label | Arabic Label |
|------|---------------|--------------|
| NEW | New | جديد |
| PRE_EXISTING | Pre-existing | موجود سابقا |
| CHANGED | Changed | تغير |
| REPAIRED | Repaired | تم إصلاحه |
| UNCERTAIN | Uncertain | غير مؤكد |
| NOT_COMPARABLE | Not comparable | غير قابل للمقارنة |

---

# Stable Review Decision Codes

| Code | English Label | Arabic Label |
|------|---------------|--------------|
| CONFIRMED | Confirmed | مؤكد |
| REJECTED | Rejected | مرفوض |
| EDITED | Edited | تم تعديله |
| ESCALATED | Escalated | تم التصعيد |
| ADDITIONAL_EVIDENCE_REQUIRED | Additional evidence required | مطلوب دليل إضافي |

---

# Stable Inspection Type Codes

| Code | English Label | Arabic Label |
|------|---------------|--------------|
| CHECK_OUT | Check-out inspection | فحص التسليم |
| CHECK_IN | Check-in inspection | فحص الاستلام |
| MAINTENANCE_INTAKE | Maintenance intake inspection | فحص دخول الصيانة |
| MAINTENANCE_QUALITY | Maintenance quality inspection | فحص جودة الصيانة |
| AD_HOC | Ad hoc inspection | فحص مخصص |

---

# Stable Capture Position Codes

| Code | English Label | Arabic Label |
|------|---------------|--------------|
| CAPTURE_FRONT | Front | الأمام |
| CAPTURE_REAR | Rear | الخلف |
| CAPTURE_LEFT | Left side | الجانب الأيسر |
| CAPTURE_RIGHT | Right side | الجانب الأيمن |
| CAPTURE_ODOMETER | Odometer | عداد المسافة |
| CAPTURE_FUEL_BATTERY | Fuel or battery | الوقود أو البطارية |
| CAPTURE_VIN | VIN | رقم الهيكل |
| CAPTURE_LICENSE_PLATE | License plate | لوحة المركبة |
| CAPTURE_INTERIOR | Interior | الداخل |
| CAPTURE_DAMAGE_CLOSEUP | Damage close-up | صورة قريبة للتلف |

---

# Terms That Must Not Be Used Incorrectly

The following terms SHALL be used carefully.

| Term | Rule |
|------|------|
| Final Liability | SHALL NOT be assigned by AI alone. |
| Final Customer Charge | SHALL NOT be determined by Damage Intelligence alone. |
| Actual Repair Cost | SHALL be owned by Maintenance or Finance, not Damage Intelligence. |
| Rental Closure | SHALL be owned by CROMS, not Damage Intelligence. |
| Work Order Execution | SHALL be owned by Maintenance, not Damage Intelligence. |
| Public Evidence URL | SHALL NOT be used as an approved evidence sharing method. |
| Confirmed Damage | SHOULD require approved workflow or human review where customer-impacting. |
| Advisory Estimate | SHALL NOT be presented as final actual repair cost. |

---

# Acceptance Criteria

## AC-DI-3000 — Glossary Exists

Given Damage Intelligence documentation is reviewed, then approved glossary and terminology SHALL exist.

## AC-DI-3001 — Stable Codes Preserved

Given localized labels are displayed, then stable internal codes SHALL remain unchanged in APIs, events, audit records, and storage.

## AC-DI-3002 — Ownership Terms Clear

Given integration terminology is used, then ownership boundaries for CROMS, Maintenance, and Damage Intelligence SHALL remain clear.

## AC-DI-3003 — Advisory Terms Clear

Given AI or repair estimate terminology is used, then advisory outputs SHALL not be described as final liability, final customer charge, or actual repair cost.

## AC-DI-3004 — Arabic Labels Supported

Given glossary terms have user-facing labels, then Arabic labels SHOULD be provided where required.

## AC-DI-3005 — Terminology Consistency

Given requirements, tests, reports, dashboards, APIs, and events are created, then terminology SHOULD align with this glossary.

---

# Normative Requirements

## Requirement

ID: REQ-DI-2900

Title:
Glossary and Terminology

Statement:
Damage Intelligence SHALL define a glossary and terminology reference covering product, inspection, evidence, AI, damage, comparison, case, review, estimate, integration, security, privacy, audit, reporting, retention, operations, localization, and stable codes.

Priority:
High

Verification:
Documentation Review

---

## Requirement

ID: REQ-DI-2901

Title:
Stable Code Terminology

Statement:
Damage Intelligence SHALL preserve stable internal codes independent of localized labels.

Priority:
Critical

Verification:
Data Integrity Review

---

## Requirement

ID: REQ-DI-2902

Title:
Localized Term Labels

Statement:
Damage Intelligence SHOULD define English and Arabic labels for user-facing stable terms where required.

Priority:
High

Verification:
Localization Review

---

## Requirement

ID: REQ-DI-2903

Title:
Ownership Boundary Terminology

Statement:
Damage Intelligence terminology SHALL clearly distinguish Damage Intelligence ownership from CROMS rental ownership and Maintenance repair ownership.

Priority:
Critical

Verification:
Architecture Review

---

## Requirement

ID: REQ-DI-2904

Title:
Advisory Output Terminology

Statement:
Damage Intelligence terminology SHALL clearly identify AI outputs and repair estimates as advisory where final business decision ownership belongs elsewhere.

Priority:
Critical

Verification:
Product Review

---

## Requirement

ID: REQ-DI-2905

Title:
Taxonomy Terminology

Statement:
Damage Intelligence SHALL define standard damage type, severity, comparison outcome, review decision, inspection type, and capture position terminology.

Priority:
High

Verification:
Taxonomy Review

---

## Requirement

ID: REQ-DI-2906

Title:
Security and Privacy Terminology

Statement:
Damage Intelligence SHALL define security and privacy terms used in requirements, reports, audit, monitoring, and operations.

Priority:
High

Verification:
Security Review

---

## Requirement

ID: REQ-DI-2907

Title:
Audit and Traceability Terminology

Statement:
Damage Intelligence SHALL define audit and traceability terms used across workflows, APIs, events, and reports.

Priority:
High

Verification:
Audit Review

---

## Requirement

ID: REQ-DI-2908

Title:
Terminology Consistency

Statement:
Damage Intelligence requirements, APIs, events, reports, dashboards, tests, and AI-generated implementation artifacts SHOULD use terminology consistent with this glossary.

Priority:
High

Verification:
QA Review

---

# Business Rules

## BR-DI-2500 — Stable Codes Are Not Translated

Stable internal codes SHALL NOT be translated in storage, APIs, events, audit records, configuration, or domain objects.

---

## BR-DI-2501 — Localized Labels Are Display Values

Localized labels SHALL be treated as display values, not stable business identifiers.

---

## BR-DI-2502 — Ownership Boundaries Must Remain Clear

Terminology SHALL preserve CROMS ownership of rental lifecycle, Maintenance ownership of repair execution, and Damage Intelligence ownership of evidence and damage context.

---

## BR-DI-2503 — Advisory Outputs Must Be Labeled Correctly

AI outputs and repair estimates SHALL be described as advisory where final decision ownership belongs to human, CROMS, Maintenance, Finance, or approved business workflow.

---

## BR-DI-2504 — Customer-Impacting Terms Require Care

Terms that imply customer liability, customer charge, dispute outcome, or repair cost SHALL be used only according to approved business ownership rules.

---

## BR-DI-2505 — Glossary Changes Must Be Reviewed

Changes to stable codes, taxonomy terms, severity labels, comparison outcomes, or integration ownership terms SHOULD be reviewed before implementation.

---

# AI Implementation Contract

AI development agents SHALL:

- Treat this document as the authoritative glossary and terminology reference for Damage Intelligence.
- Preserve all requirement IDs, acceptance criterion IDs, and business rule IDs.
- Use the approved terms consistently in future requirements, user stories, APIs, events, tests, reports, dashboards, and implementation plans.
- Preserve stable-code and localized-label separation.
- Preserve CROMS, Maintenance, and Damage Intelligence ownership boundaries.
- Never describe AI output as final liability, final billing, final customer charge, or actual repair cost.
- Never translate stable internal codes in storage, APIs, events, audit records, configuration, or domain objects.
- Raise ambiguity where terminology conflicts with existing requirements, ownership boundaries, localization, or business rules.

---

# References

- DI-0001 – Product Vision
- DI-0002 – Business Requirements
- DI-0003 – User Personas
- DI-0004 – Inspection Workflow
- DI-0005 – AI Damage Detection
- DI-0006 – Damage Comparison
- DI-0007 – Vehicle Capture Standards
- DI-0008 – Damage Taxonomy
- DI-0009 – Severity Assessment
- DI-0010 – Repair Cost Estimation
- DI-0011 – API Specification
- DI-0012 – Domain Model
- DI-0013 – Events
- DI-0014 – Security and Privacy
- DI-0015 – Audit and Traceability
- DI-0016 – Reporting and Dashboards
- DI-0017 – Integration with CROMS
- DI-0018 – Integration with Maintenance
- DI-0019 – Acceptance Criteria
- DI-0020 – Test Strategy
- DI-0021 – Implementation Readiness Checklist
- DI-0022 – Data Retention and Archival
- DI-0023 – Operational Monitoring and Alerts
- DI-0024 – Configuration and Administration
- DI-0025 – Localization and Arabic Support
- DI-0026 – Deployment and Release Strategy
- DI-0027 – Operational Runbook
- DI-0028 – Disaster Recovery and Business Continuity
- DI-0029 – Product Roadmap
- GEES-0007 – Enterprise Security Standard
- GEES-0009 – Traceability Standard
- PLATFORM-0005 – GEES Core and Application Architecture

---

# Revision History

| Version | Date | Description |
|----------|------|-------------|
| 1.0.0 | 2026-06-27 | Initial Damage Intelligence Glossary and Terminology |
