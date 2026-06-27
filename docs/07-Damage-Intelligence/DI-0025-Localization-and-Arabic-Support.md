---
id: "DI-0025"
title: "Damage Intelligence Localization and Arabic Support"
version: "1.0.0"
document_type: "Product Specification"
document_class: "Localization and Arabic Support Specification"
status: "Draft"
classification: "Internal"
owner: "Riyadah Technology"
reviewers: "Chief Enterprise Architect, Product Owner, UX Lead, Arabic Localization Lead, Damage Intelligence Lead, CROMS Lead, Maintenance Lead, QA Lead, Security Lead"
approvers: ""
created: "2026-06-27"
updated: "2026-06-27"
authoritative: true
ai_consumable: true
related: "DI-0001, DI-0002, DI-0003, DI-0004, DI-0007, DI-0008, DI-0009, DI-0010, DI-0011, DI-0014, DI-0016, DI-0019, DI-0020, DI-0024, GEES-0007, GEES-0009, PLATFORM-0005"
---

# Damage Intelligence Localization and Arabic Support
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Damage Intelligence Localization and Arabic Support

## Executive Summary

This document defines localization and Arabic language support requirements for Damage Intelligence.

Damage Intelligence SHALL support English and Arabic user experiences where required by tenant, user, branch, report, or customer-facing workflow.

Arabic support SHALL include right-to-left layout, Arabic labels, Arabic report output, localized taxonomy display, localized severity labels, localized validation messages, localized dashboard labels, localized notification templates, and proper handling of mixed Arabic and English technical identifiers.

Stable internal codes SHALL remain language-neutral. Display labels MAY be localized.

Localization SHALL be implemented without compromising security, auditability, evidence integrity, tenant isolation, or traceability.

---

# Purpose

The purpose of this document is to define how Damage Intelligence SHALL support localization, Arabic language, and right-to-left user interfaces.

This specification SHALL guide:

* Web application localization.
* Mobile capture localization.
* Arabic report generation.
* Dashboard localization.
* Damage taxonomy localization.
* Severity label localization.
* Error message localization.
* Notification localization.
* API localization behavior.
* Test case generation.
* QA validation.
* Accessibility and usability review.

---

# Scope

## In Scope

This specification covers:

* Language support.
* Arabic support.
* English support.
* Right-to-left layout.
* Localized labels.
* Localized taxonomy.
* Localized severity values.
* Localized UI messages.
* Localized validation messages.
* Localized reports.
* Localized dashboards.
* Localized notifications.
* Mixed language handling.
* Date, time, number, and currency formatting.
* API localization headers.
* Localization testing.
* Translation governance.

## Out of Scope

This specification does not define:

* Final Arabic copywriting.
* Final translation vendor process.
* Final UI wireframes.
* Final report templates.
* Full accessibility standard.
* Final localization database schema.
* Full multilingual customer support process.
* Final notification template wording.

---

# Localization Principles

Damage Intelligence localization SHALL follow these principles:

1. Stable Codes, Localized Labels
2. Arabic and English Support
3. Right-to-Left Layout Support
4. Tenant-Aware Localization
5. User Preference Support
6. Consistent Terminology
7. No Translation of Stable Identifiers
8. Secure Localized Output
9. Auditable Configuration
10. Testable Localization Behavior

---

# Supported Languages

Damage Intelligence SHOULD support at minimum:

| Language | Locale Code | Direction     |
| -------- | ----------- | ------------- |
| English  | en          | Left-to-right |
| Arabic   | ar          | Right-to-left |

Additional locale variants MAY be supported later, such as:

| Language             | Locale Code | Direction     |
| -------------------- | ----------- | ------------- |
| English Saudi Arabia | en-SA       | Left-to-right |
| Arabic Saudi Arabia  | ar-SA       | Right-to-left |

---

# Language Selection

Damage Intelligence SHOULD support language selection by:

* User preference.
* Tenant default.
* Branch default where applicable.
* Browser or device preference.
* Report request parameter.
* Customer-facing report setting.
* API localization header where applicable.

If no language is selected, the system SHOULD use the tenant default language.

---

# Language Fallback

The system SHALL support safe fallback behavior.

Fallback order SHOULD be:

```text
User Selected Language
  ↓
Tenant Default Language
  ↓
System Default Language
  ↓
Stable Internal Code
```

If a translation is missing, the system SHOULD display the configured fallback label and record localization quality issue where appropriate.

Missing translations SHALL NOT break workflows.

---

# Stable Codes and Localized Labels

Damage Intelligence SHALL preserve stable internal codes.

Examples of stable codes:

* SCRATCH
* DENT
* CRACK
* BROKEN_LIGHT
* FRONT_BUMPER
* REAR_BUMPER
* MINOR
* MODERATE
* MAJOR
* CRITICAL
* NEW
* PRE_EXISTING
* CHANGED
* REPAIRED
* UNCERTAIN

Stable codes SHALL NOT be translated in storage, APIs, audit records, events, or domain objects.

Localized labels MAY be displayed to users.

---

# Localized Taxonomy Example

| Code             | English Label    | Arabic Label         |
| ---------------- | ---------------- | -------------------- |
| SCRATCH          | Scratch          | خدش                  |
| DENT             | Dent             | انبعاج               |
| CRACK            | Crack            | كسر أو تشقق          |
| BROKEN_LIGHT     | Broken light     | مصباح مكسور          |
| MISSING_PART     | Missing part     | قطعة مفقودة          |
| FRONT_BUMPER     | Front bumper     | الصدام الأمامي       |
| REAR_BUMPER      | Rear bumper      | الصدام الخلفي        |
| LEFT_FRONT_DOOR  | Left front door  | الباب الأمامي الأيسر |
| RIGHT_FRONT_DOOR | Right front door | الباب الأمامي الأيمن |

---

# Localized Severity Labels

Severity labels SHOULD support localization.

| Code     | English Label | Arabic Label |
| -------- | ------------- | ------------ |
| MINOR    | Minor         | بسيط         |
| MODERATE | Moderate      | متوسط        |
| MAJOR    | Major         | كبير         |
| CRITICAL | Critical      | حرج          |
| UNKNOWN  | Unknown       | غير معروف    |

Severity codes SHALL remain stable.

---

# Localized Comparison Outcomes

Comparison outcome labels SHOULD support localization.

| Code           | English Label  | Arabic Label      |
| -------------- | -------------- | ----------------- |
| NEW            | New            | جديد              |
| PRE_EXISTING   | Pre-existing   | موجود سابقا       |
| CHANGED        | Changed        | تغير              |
| REPAIRED       | Repaired       | تم إصلاحه         |
| UNCERTAIN      | Uncertain      | غير مؤكد          |
| NOT_COMPARABLE | Not comparable | غير قابل للمقارنة |

---

# Right-to-Left Layout

Arabic user interfaces SHALL support right-to-left layout.

RTL support SHALL apply to:

* Mobile capture screens.
* Web portal screens.
* Review queue.
* Damage case views.
* Evidence viewer metadata.
* Dashboards.
* Reports.
* Notifications.
* Admin configuration screens where localized.

RTL layout SHALL NOT corrupt stable identifiers, codes, IDs, URLs, numbers, or timestamps.

---

# Mixed Language Handling

Damage Intelligence SHALL support mixed Arabic and English content.

Examples of mixed content:

* Vehicle ID in English inside Arabic sentence.
* Damage code displayed with Arabic label.
* Report ID inside Arabic report.
* English technical reference inside Arabic dashboard.
* Arabic reviewer notes with English identifiers.

The system SHALL preserve readability of mixed left-to-right and right-to-left content.

---

# UI Localization

UI localization SHALL apply to:

* Page titles.
* Section headings.
* Buttons.
* Form labels.
* Field hints.
* Validation messages.
* Status labels.
* Error messages.
* Empty states.
* Tooltips.
* Confirmation dialogs.
* Review decision labels.
* Action menus.
* Dashboard labels.

UI localization SHALL be consistent across web and mobile where practical.

---

# Mobile Capture Localization

Mobile capture screens SHOULD support Arabic and English.

Localized mobile capture SHOULD include:

* Inspection type labels.
* Required capture checklist.
* Capture position instructions.
* Image quality messages.
* Recapture guidance.
* Offline status messages.
* Upload status messages.
* Submission messages.
* Error messages.
* Confirmation messages.

Mobile Arabic UI SHALL support RTL layout.

---

# Capture Instruction Localization

Capture instructions SHOULD be localized.

Examples:

| Capture Position     | English Instruction                   | Arabic Instruction                   |
| -------------------- | ------------------------------------- | ------------------------------------ |
| CAPTURE-FRONT        | Capture the front side of the vehicle | التقط صورة للجهة الأمامية من المركبة |
| CAPTURE-REAR         | Capture the rear side of the vehicle  | التقط صورة للجهة الخلفية من المركبة  |
| CAPTURE-LEFT         | Capture the left side of the vehicle  | التقط صورة للجهة اليسرى من المركبة   |
| CAPTURE-RIGHT        | Capture the right side of the vehicle | التقط صورة للجهة اليمنى من المركبة   |
| CAPTURE-ODOMETER     | Capture the odometer clearly          | التقط صورة واضحة لعداد المسافة       |
| CAPTURE-FUEL-BATTERY | Capture the fuel or battery level     | التقط صورة لمستوى الوقود أو البطارية |

---

# Validation Message Localization

Validation messages SHALL be localized.

Examples:

| Scenario               | English Message                                | Arabic Message                          |
| ---------------------- | ---------------------------------------------- | --------------------------------------- |
| Missing required image | Required image is missing.                     | الصورة المطلوبة غير مرفقة.              |
| Image blurry           | Image is blurry. Please retake it.             | الصورة غير واضحة. يرجى إعادة التصوير.   |
| Low light              | Lighting is too low. Please retake the image.  | الإضاءة منخفضة. يرجى إعادة التصوير.     |
| Unauthorized action    | You are not authorized to perform this action. | غير مصرح لك بتنفيذ هذا الإجراء.         |
| Upload failed          | Image upload failed. Please try again.         | فشل رفع الصورة. يرجى المحاولة مرة أخرى. |

---

# Error Message Localization

Error messages SHOULD be localized without exposing sensitive technical details.

Localized errors SHALL NOT expose:

* Secrets.
* Tokens.
* Stack traces.
* Storage paths.
* Internal system errors.
* Sensitive customer data.
* Unrestricted image URLs.

Technical error details MAY be logged securely for authorized support teams.

---

# Report Localization

Damage Intelligence reports SHOULD support English and Arabic.

Localized reports MAY include:

* Inspection Summary Report.
* Damage Case Report.
* Vehicle Damage History Report.
* Rental Damage Summary Report.
* Maintenance Handoff Report.
* AI Quality Report.
* Evidence Access Report.
* Repair Estimate Report.

Arabic reports SHALL support right-to-left layout.

---

# Report Localization Rules

Reports SHALL preserve:

* Stable IDs.
* Stable codes where required.
* Evidence references.
* Timestamps.
* Currency.
* Audit references.
* Legal disclaimers.
* Advisory AI disclaimers.
* Advisory estimate disclaimers.

Reports SHOULD localize:

* Titles.
* Section headings.
* Status labels.
* Damage labels.
* Severity labels.
* Comparison labels.
* Instructions.
* Disclaimers.
* User-facing notes where appropriate.

---

# Arabic Report Considerations

Arabic reports SHOULD support:

* Right-to-left layout.
* Arabic headings.
* Arabic labels.
* Proper alignment of tables.
* Mixed Arabic and English identifiers.
* Arabic date formatting where configured.
* SAR currency formatting.
* Localized disclaimers.
* Clear distinction between AI suggestion and human-reviewed decision.

---

# Dashboard Localization

Dashboards SHOULD support localized labels.

Dashboard localization SHOULD include:

* Dashboard titles.
* KPI names.
* Filter labels.
* Chart labels.
* Table headers.
* Status labels.
* Severity labels.
* Tooltip text.
* Empty state messages.
* Export labels.

Stable KPI identifiers SHALL remain language-neutral internally.

---

# Notification Localization

Notifications SHOULD support localization.

Notification localization MAY include:

* Inspection assigned.
* Recapture required.
* AI analysis completed.
* Damage case created.
* Review required.
* Additional evidence requested.
* Damage routed to Maintenance.
* Report generated.
* Integration failure.
* Security alert where appropriate.

Notifications SHALL avoid sensitive data unless explicitly authorized.

---

# Admin Configuration Localization

Administrative configuration SHOULD support localized display labels.

Admin localization MAY include:

* Configuration category names.
* Capture template names.
* Taxonomy labels.
* Severity labels.
* Review rule labels.
* Report template labels.
* Retention rule labels.
* Monitoring threshold labels.

Administrative stable codes SHALL remain unchanged.

---

# API Localization Behavior

APIs SHOULD support localization for display fields where appropriate.

API behavior SHOULD distinguish between:

* Stable code fields.
* Localized display labels.

Example:

```json
{
  "damageTypeCode": "SCRATCH",
  "damageTypeLabel": "خدش",
  "severityCode": "MINOR",
  "severityLabel": "بسيط"
}
```

API consumers SHOULD NOT rely on localized labels as stable business identifiers.

---

# Localization Headers

APIs MAY use standard localization headers or parameters.

Examples:

```http
Accept-Language: ar-SA
```

or:

```http
GET /api/v1/damage-intelligence/taxonomy?locale=ar-SA
```

If no locale is provided, tenant or user default SHOULD be used.

---

# Search and Filtering Localization

Search and filtering SHOULD support localized display values where practical.

Search behavior SHOULD allow:

* Search by stable code.
* Search by English label.
* Search by Arabic label.
* Filter by stable code.
* Display localized result label.

Filtering logic SHOULD use stable codes internally.

---

# Sorting Localization

Localized sorting SHOULD consider language-specific behavior where practical.

Arabic display lists SHOULD sort in a predictable order.

Where localized sorting is not available, stable configured order MAY be used.

---

# Date and Time Localization

Date and time display SHOULD support localization.

The system SHOULD consider:

* Tenant time zone.
* User time zone.
* Gregorian calendar display.
* Arabic display where configured.
* 24-hour or 12-hour format based on tenant/user settings.
* Server timestamps remain standardized internally.

Stored timestamps SHALL remain in standard machine-readable format.

---

# Currency Localization

Repair estimates and cost-related reports SHOULD support currency localization.

Default currency for Saudi implementation SHOULD be SAR unless tenant configuration specifies otherwise.

Currency display SHOULD support:

* SAR
* Arabic labels where configured
* Decimal precision
* English and Arabic report display

Cost values SHALL remain numeric internally.

---

# Number Formatting

Numbers SHOULD be localized where appropriate.

Examples:

* Image count.
* Damage count.
* Confidence score.
* Estimate amount.
* Dashboard KPI value.
* Percentage.

Internal numeric values SHALL remain language-neutral.

---

# Arabic Content Storage

Arabic text SHALL be stored using Unicode-compatible encoding.

The system SHALL support Arabic in:

* User notes.
* Review reasons.
* Report labels.
* Notification templates.
* Taxonomy labels.
* Configuration labels.
* Capture instructions.

Arabic text SHALL not be corrupted during storage, retrieval, reporting, export, or search.

---

# Export Localization

Exports SHOULD support localization where applicable.

Export formats MAY include:

* PDF.
* CSV.
* Excel.
* JSON.

PDF reports SHOULD support Arabic RTL layout.

CSV and Excel exports SHOULD preserve Arabic text encoding.

JSON exports SHOULD preserve stable codes and MAY include localized labels.

---

# Localization Security

Localization SHALL not weaken security.

Localized content SHALL be protected against:

* Injection attacks.
* Script injection.
* Unsafe HTML rendering.
* Broken access control.
* Sensitive data exposure.
* Translation string abuse.

User-entered Arabic text SHALL be safely encoded and rendered.

---

# Localization Privacy

Localized reports, notifications, dashboards, and exports SHALL follow privacy rules.

Localization SHALL NOT cause:

* Extra customer data exposure.
* Exposure of internal notes in customer-facing Arabic reports.
* Exposure of unrestricted evidence links.
* Exposure of AI prompts.
* Exposure of hidden reviewer notes.
* Exposure of security audit details.

---

# Translation Governance

Translation governance SHOULD define:

* Translation owner.
* Review process.
* Approval process.
* Terminology glossary.
* Versioning.
* Change audit.
* Release process.
* Fallback handling.
* Quality review.

Arabic terminology SHOULD be reviewed by Arabic-speaking business and operations stakeholders.

---

# Terminology Consistency

Damage Intelligence SHOULD maintain a localization glossary.

Glossary entries SHOULD include:

* Stable code.
* English label.
* Arabic label.
* Description.
* Usage context.
* Approved status.
* Version.
* Effective date.

Glossary changes SHOULD be audited.

---

# Localization Testing

Localization testing SHALL validate:

* Arabic text rendering.
* RTL layout.
* Mixed Arabic-English content.
* Mobile Arabic screens.
* Web Arabic screens.
* Arabic reports.
* Arabic dashboard labels.
* Arabic notifications.
* Arabic validation messages.
* Date, time, number, and currency formatting.
* Search and filtering with Arabic labels.
* Export encoding.
* No truncation or layout breakage.
* No broken stable codes.

---

# Arabic Accessibility Considerations

Arabic UI SHOULD consider:

* Readable font size.
* Clear labels.
* Clear capture instructions.
* Clear error messages.
* Proper RTL alignment.
* Avoidance of ambiguous translation.
* Consistent terminology.
* Screen reader compatibility where required.

---

# Acceptance Criteria

## AC-DI-2500 — Arabic UI Support

Given a user selects Arabic, when the user opens supported Damage Intelligence screens, then labels, messages, and layout SHOULD display in Arabic and RTL where supported.

## AC-DI-2501 — Stable Code Preservation

Given a localized label is displayed, when data is stored or exchanged by API/event, then stable internal codes SHALL remain unchanged.

## AC-DI-2502 — Arabic Capture Instructions

Given a mobile capture user selects Arabic, when capture positions are displayed, then capture instructions SHOULD appear in Arabic.

## AC-DI-2503 — Arabic Reports

Given an Arabic report is requested, when report generation completes, then report headings, labels, and user-facing terms SHOULD be Arabic and RTL where supported.

## AC-DI-2504 — Localization Fallback

Given a translation is missing, when localized display is requested, then the system SHALL use a safe fallback without breaking the workflow.

## AC-DI-2505 — Arabic Export Encoding

Given Arabic content is exported, when the file is opened, then Arabic text SHOULD remain readable and not corrupted.

## AC-DI-2506 — Localization Security

Given localized text is rendered, when the content contains unsafe input, then the system SHALL safely encode or reject unsafe content.

---

# Normative Requirements

## Requirement

ID: REQ-DI-2400

Title:
Localization and Arabic Support

Statement:
Damage Intelligence SHALL define localization and Arabic support requirements for user interfaces, reports, dashboards, notifications, taxonomy labels, validation messages, and exports.

Priority:
High

Verification:
Localization Review

---

## Requirement

ID: REQ-DI-2401

Title:
Arabic Language Support

Statement:
Damage Intelligence SHOULD support Arabic language display for supported screens, reports, dashboards, notifications, and user-facing messages.

Priority:
High

Verification:
Localization Test

---

## Requirement

ID: REQ-DI-2402

Title:
Right-to-Left Layout

Statement:
Damage Intelligence SHOULD support right-to-left layout for Arabic user interfaces and reports.

Priority:
High

Verification:
RTL UI Test

---

## Requirement

ID: REQ-DI-2403

Title:
Stable Code Preservation

Statement:
Damage Intelligence SHALL preserve stable internal codes independent of localized display labels.

Priority:
Critical

Verification:
Data Integrity Test

---

## Requirement

ID: REQ-DI-2404

Title:
Localized Taxonomy Labels

Statement:
Damage Intelligence SHOULD support localized labels for damage types, vehicle areas, severity levels, comparison outcomes, and review outcomes.

Priority:
High

Verification:
Taxonomy Localization Test

---

## Requirement

ID: REQ-DI-2405

Title:
Localized Capture Instructions

Statement:
Damage Intelligence SHOULD support localized capture instructions for vehicle inspection workflows.

Priority:
High

Verification:
Mobile Localization Test

---

## Requirement

ID: REQ-DI-2406

Title:
Localized Validation Messages

Statement:
Damage Intelligence SHOULD support localized validation and error messages.

Priority:
Medium

Verification:
Localization Test

---

## Requirement

ID: REQ-DI-2407

Title:
Localized Reports

Statement:
Damage Intelligence SHOULD support Arabic and English report output where required.

Priority:
High

Verification:
Report Localization Test

---

## Requirement

ID: REQ-DI-2408

Title:
Localized Dashboards

Statement:
Damage Intelligence SHOULD support localized dashboard labels, KPI names, filters, and table headings.

Priority:
Medium

Verification:
Dashboard Localization Test

---

## Requirement

ID: REQ-DI-2409

Title:
Localized Notifications

Statement:
Damage Intelligence MAY support localized notification templates for inspection, review, damage case, maintenance routing, report, and integration events.

Priority:
Medium

Verification:
Notification Review

---

## Requirement

ID: REQ-DI-2410

Title:
API Localization Support

Statement:
Damage Intelligence APIs SHOULD support localized display labels while preserving stable code fields.

Priority:
Medium

Verification:
API Test

---

## Requirement

ID: REQ-DI-2411

Title:
Localization Fallback

Statement:
Damage Intelligence SHALL support fallback behavior when localized labels or messages are missing.

Priority:
High

Verification:
Localization Test

---

## Requirement

ID: REQ-DI-2412

Title:
Arabic Text Storage

Statement:
Damage Intelligence SHALL support Unicode-compatible storage, retrieval, search, reporting, and export of Arabic text.

Priority:
Critical

Verification:
Data Test

---

## Requirement

ID: REQ-DI-2413

Title:
Localized Export Encoding

Statement:
Damage Intelligence exports SHOULD preserve Arabic text readability and encoding.

Priority:
High

Verification:
Export Test

---

## Requirement

ID: REQ-DI-2414

Title:
Localization Security

Statement:
Localized content SHALL be safely rendered and SHALL NOT introduce injection, script, or sensitive data exposure risks.

Priority:
Critical

Verification:
Security Test

---

## Requirement

ID: REQ-DI-2415

Title:
Localization Privacy

Statement:
Localized reports, notifications, dashboards, and exports SHALL follow Damage Intelligence privacy and data minimization requirements.

Priority:
Critical

Verification:
Privacy Review

---

## Requirement

ID: REQ-DI-2416

Title:
Translation Governance

Statement:
Damage Intelligence SHOULD define governance for approved translations, terminology, review, versioning, and fallback.

Priority:
Medium

Verification:
Localization Governance Review

---

# Business Rules

## BR-DI-2000 — Codes Are Not Translated

Stable internal codes SHALL NOT be translated in storage, APIs, events, audit records, or domain objects.

---

## BR-DI-2001 — Labels May Be Localized

Display labels MAY be localized based on user, tenant, branch, report, or API locale.

---

## BR-DI-2002 — Arabic Requires RTL Support

Arabic screens and Arabic reports SHOULD support right-to-left layout.

---

## BR-DI-2003 — Missing Translation Must Not Break Workflow

Missing localization values SHALL fall back safely and SHALL NOT block critical operational workflows.

---

## BR-DI-2004 — Customer-Facing Arabic Reports Must Be Controlled

Arabic customer-facing reports SHALL follow the same security, privacy, access, and evidence controls as English reports.

---

## BR-DI-2005 — Localized Content Must Be Secure

Localized content SHALL be encoded, validated, and rendered safely.

---

# AI Implementation Contract

AI development agents SHALL:

* Treat this document as the authoritative localization and Arabic support specification for Damage Intelligence.
* Preserve all requirement IDs, acceptance criterion IDs, and business rule IDs.
* Preserve stable-code and localized-label separation.
* Preserve Arabic RTL requirements.
* Generate future UI, mobile, API, report, dashboard, notification, export, and test implementations consistent with this document.
* Never translate stable internal codes in storage, APIs, events, audit records, or domain objects.
* Preserve localization security and privacy requirements.
* Raise ambiguity where translation ownership, glossary terminology, locale fallback, report localization, or RTL behavior is unclear.

---

# References

* DI-0003 – User Personas
* DI-0004 – Inspection Workflow
* DI-0007 – Vehicle Capture Standards
* DI-0008 – Damage Taxonomy
* DI-0009 – Severity Assessment
* DI-0010 – Repair Cost Estimation
* DI-0011 – API Specification
* DI-0014 – Security and Privacy
* DI-0016 – Reporting and Dashboards
* DI-0019 – Acceptance Criteria
* DI-0020 – Test Strategy
* DI-0024 – Configuration and Administration
* GEES-0007 – Enterprise Security Standard
* GEES-0009 – Traceability Standard
* PLATFORM-0005 – GEES Core and Application Architecture

---

# Revision History

| Version | Date       | Description                                                               |
| ------- | ---------- | ------------------------------------------------------------------------- |
| 1.0.0   | 2026-06-27 | Initial Damage Intelligence Localization and Arabic Support Specification |

