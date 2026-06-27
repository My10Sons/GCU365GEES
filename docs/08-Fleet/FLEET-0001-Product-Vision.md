---
id: "FLEET-0001"
title: "Fleet Product Vision"
version: "1.0.0"
document_type: "Product Specification"
document_class: "Product Vision"
status: "Draft"
classification: "Internal"
owner: "Riyadah Technology"
reviewers: "Chief Enterprise Architect, Product Owner, Fleet Lead, CROMS Lead, Maintenance Lead, IoT Lead, Operations Lead, QA Lead, Security Lead"
approvers: ""
created: "2026-06-27"
updated: "2026-06-27"
authoritative: true
ai_consumable: true
related: "FLEET-0002, FLEET-0003, FLEET-0004, FLEET-0005, FLEET-0006, FLEET-0007, FLEET-0008, FLEET-0009, FLEET-0010, DI-0001, DI-0017, DI-0018, PLATFORM-0005, GEES-0007, GEES-0009"
---

# Fleet Product Vision

## Executive Summary

Fleet is the GCU365 capability responsible for managing vehicles as operational, financial, contractual, maintenance, rental, telematics, inspection, and compliance assets across the enterprise.

Fleet SHALL provide the trusted vehicle master, lifecycle status, operational availability, assignment context, utilization visibility, maintenance readiness, damage visibility, IoT connectivity, compliance status, and integration foundation required by CROMS, Maintenance, Damage Intelligence, Finance, HR, Operations, Reporting, and future mobility platforms.

Fleet is not only a vehicle list. It is the operational backbone that connects every vehicle to its condition, availability, location, ownership, documents, cost profile, rental readiness, maintenance readiness, damage history, and business utilization.

---

# Product Vision

The vision of Fleet is to become the authoritative enterprise vehicle intelligence layer for Riyadah and GCU365 products.

Fleet SHALL enable the organization to answer critical operational questions such as:

- What vehicles do we own, operate, manage, lease, rent, or track?
- Where is each vehicle?
- What is each vehicle’s operational status?
- Is the vehicle available for rental?
- Is the vehicle blocked because of damage, maintenance, documents, compliance, or operational rule?
- What is the vehicle’s maintenance history?
- What is the vehicle’s damage history?
- What is the vehicle’s utilization?
- What is the vehicle’s cost profile?
- Which system currently owns the active workflow for the vehicle?
- What actions are required before the vehicle can return to service?

Fleet SHALL act as the central source of truth for vehicle identity and operational readiness, while preserving ownership boundaries with connected systems.

---

# Strategic Goals

Fleet SHALL support the following strategic goals:

1. Establish a single trusted vehicle master.
2. Improve fleet visibility and operational control.
3. Increase vehicle utilization.
4. Reduce downtime.
5. Improve maintenance coordination.
6. Improve rental readiness.
7. Improve damage and inspection traceability.
8. Enable IoT and telematics-driven operations.
9. Support financial visibility of vehicle costs.
10. Support scalable fleet operations across branches, tenants, and business lines.

---

# Business Outcomes

Fleet SHOULD deliver measurable business outcomes.

| Outcome | Description |
|--------|-------------|
| Higher Utilization | Better visibility of available, blocked, assigned, and under-maintenance vehicles |
| Lower Downtime | Faster detection of maintenance, compliance, and operational blockers |
| Better Asset Control | Single trusted record for vehicle identity, ownership, status, and history |
| Better Rental Readiness | Clear readiness status before CROMS rental workflow uses a vehicle |
| Better Maintenance Planning | Clear linkage between vehicles, faults, work orders, and repair history |
| Better Damage Control | Integrated vehicle damage history from Damage Intelligence |
| Better Financial Visibility | Better cost, depreciation, ownership, and expense visibility |
| Better Compliance | Document, registration, insurance, inspection, and operational compliance tracking |
| Better Reporting | Fleet KPIs, utilization, downtime, cost, and operational dashboards |
| Better Scalability | Support multi-tenant, multi-branch, multi-product fleet operations |

---

# Product Positioning

Fleet SHALL be positioned as the vehicle asset and operational readiness layer within the GCU365 ecosystem.

Fleet SHALL integrate with:

- CROMS for rental availability, rental assignment, rental lifecycle references, and vehicle operational readiness.
- Maintenance for work orders, faults, repair status, maintenance plans, and vehicle serviceability.
- Damage Intelligence for inspections, damage cases, evidence, and vehicle condition history.
- IoT and telematics services for location, odometer, status, driving events, and device connectivity.
- Finance for asset cost, depreciation, expenses, invoices, revenue allocation, and financial reporting.
- Reporting and dashboards for operational and executive visibility.
- Identity and access services for secure role-based operations.

Fleet SHALL not replace CROMS, Maintenance, Finance, or Damage Intelligence. Fleet SHALL provide shared vehicle context and status intelligence to those systems.

---

# Ownership Boundaries

Fleet SHALL preserve clear ownership boundaries.

| Area | System of Record |
|------|------------------|
| Vehicle master record | Fleet |
| Vehicle identity and attributes | Fleet |
| Vehicle operational status | Fleet |
| Vehicle availability status | Fleet with inputs from CROMS, Maintenance, Damage Intelligence, and Operations |
| Rental agreement | CROMS |
| Rental lifecycle | CROMS |
| Rental closure | CROMS |
| Customer billing for rental | CROMS or Finance |
| Maintenance work order | Maintenance |
| Repair execution | Maintenance |
| Actual repair cost | Maintenance or Finance |
| Damage evidence | Damage Intelligence |
| Damage case | Damage Intelligence |
| IoT device registry | IoT or Fleet depending on final architecture |
| Financial asset accounting | Finance |
| Employee assignment | HR or Operations depending on workflow |

---

# Core Product Capabilities

Fleet SHALL provide the following core capabilities.

## Vehicle Master

Fleet SHALL manage the authoritative vehicle master record.

Vehicle master SHOULD include:

- Vehicle ID.
- VIN.
- Plate number.
- Make.
- Model.
- Year.
- Color.
- Body type.
- Fuel or energy type.
- Transmission.
- Odometer.
- Ownership type.
- Branch.
- Tenant.
- Operational status.
- Availability status.
- Compliance status.
- Maintenance status.
- Damage status.
- IoT status.
- Financial asset reference.

---

## Vehicle Lifecycle

Fleet SHALL support vehicle lifecycle tracking.

Lifecycle stages MAY include:

- Planned.
- Ordered.
- Received.
- Onboarding.
- Active.
- Available.
- Assigned.
- Rented.
- Under Inspection.
- Under Maintenance.
- Blocked.
- Retired.
- Sold.
- Decommissioned.

Lifecycle changes SHALL be auditable.

---

## Vehicle Availability

Fleet SHALL provide vehicle availability status.

Availability SHOULD consider:

- Rental status.
- Maintenance status.
- Damage status.
- Inspection status.
- Compliance status.
- Document status.
- Branch assignment.
- Operational holds.
- Manual blocks.
- IoT immobilization or device condition where applicable.

Fleet SHALL provide availability context to CROMS but SHALL NOT own rental agreement decisions.

---

## Vehicle Operational Status

Fleet SHALL track operational status.

Operational statuses MAY include:

- Available.
- Reserved.
- Rented.
- In Inspection.
- In Maintenance.
- Awaiting Parts.
- Awaiting Approval.
- Damaged.
- Blocked.
- In Transit.
- Retired.

Status calculation SHOULD be rule-driven and auditable.

---

## Vehicle Documents

Fleet SHOULD manage vehicle document status.

Documents MAY include:

- Registration.
- Insurance.
- Periodic inspection.
- Authorization documents.
- Ownership documents.
- Lease documents.
- Permit documents.
- Compliance attachments.

Document expiry SHOULD affect vehicle readiness where configured.

---

## Vehicle Assignment

Fleet SHOULD support assignment context.

Assignment MAY include:

- Branch assignment.
- Department assignment.
- Driver assignment.
- Employee assignment.
- Vendor assignment.
- Rental fleet pool.
- Maintenance pool.
- Replacement vehicle pool.

Assignment history SHOULD be auditable.

---

## IoT and Telematics

Fleet SHOULD support IoT and telematics integration.

IoT data MAY include:

- Device ID.
- Device status.
- Last known location.
- Odometer.
- Ignition status.
- Battery status.
- Fuel level.
- Speed events.
- Geofence events.
- Immobilization status where applicable.
- Last communication timestamp.

Fleet SHALL treat IoT data as operational signal and SHALL preserve source traceability.

---

## Maintenance Visibility

Fleet SHALL integrate with Maintenance.

Fleet SHOULD show:

- Open work orders.
- Maintenance status.
- Preventive maintenance due.
- Corrective maintenance status.
- Repair completion status.
- Vehicle serviceability.
- Maintenance downtime.
- Actual cost reference where available.
- Maintenance blocker reason.

Fleet SHALL NOT own work order execution.

---

## Damage Visibility

Fleet SHALL integrate with Damage Intelligence.

Fleet SHOULD show:

- Latest inspection status.
- Latest damage status.
- Open damage cases.
- Damage severity.
- Damage history.
- Evidence references.
- Repair relevance.
- Damage-related blocks.
- Post-repair inspection status.

Fleet SHALL NOT own damage evidence or damage case decisions.

---

## Compliance Visibility

Fleet SHOULD provide compliance visibility.

Compliance MAY include:

- Registration status.
- Insurance status.
- Inspection validity.
- Operating authorization.
- Fleet policy compliance.
- Branch compliance.
- Document expiry.
- Missing document flags.

Compliance status SHOULD affect readiness where configured.

---

## Fleet Reporting

Fleet SHOULD provide operational and executive reporting.

Reports MAY include:

- Fleet inventory.
- Fleet availability.
- Fleet utilization.
- Fleet downtime.
- Fleet age.
- Fleet cost.
- Fleet compliance.
- Maintenance status.
- Damage status.
- Branch distribution.
- Vehicle lifecycle status.
- IoT connectivity.
- Document expiry.

---

# Target Users

Fleet SHALL support multiple user groups.

| User | Need |
|------|------|
| Fleet Manager | Full visibility and control of vehicles |
| Operations Manager | Vehicle readiness, availability, and utilization |
| Branch Manager | Branch-level fleet status and blockers |
| Rental Operations User | Vehicle availability for rental |
| Maintenance Manager | Vehicles requiring service or repair |
| Damage Review User | Vehicle condition and damage history context |
| Finance User | Asset, cost, and financial references |
| Compliance User | Document and compliance status |
| Executive User | Fleet KPIs, utilization, downtime, and performance |
| Support User | Troubleshooting vehicle status and workflow issues |

---

# Core Product Rules

Fleet SHALL follow these rules:

- Fleet owns the vehicle master.
- CROMS owns rental agreements and rental lifecycle.
- Maintenance owns work orders and repair execution.
- Damage Intelligence owns inspection evidence and damage cases.
- Finance owns accounting, invoices, depreciation, and actual financial postings.
- Fleet availability may be influenced by external systems.
- Fleet status changes must be auditable.
- Vehicle readiness must be explainable.
- Tenant isolation is mandatory.
- Vehicle records must not be silently overwritten.
- External system references must be preserved.

---

# Fleet Readiness Concept

Fleet readiness is the system’s answer to whether a vehicle is operationally ready for use.

Readiness SHOULD consider:

- Vehicle active status.
- Rental availability.
- Maintenance blocker.
- Damage blocker.
- Document blocker.
- Compliance blocker.
- Branch assignment.
- Operational hold.
- IoT or device blocker where applicable.

Readiness SHOULD produce:

- Ready or Not Ready result.
- Reason codes.
- Source systems.
- Timestamp.
- Actor or system source.
- Override status where allowed.

---

# Fleet Readiness Example

```json
{
  "vehicleId": "VEH-000001",
  "readinessStatus": "NOT_READY",
  "reasonCodes": [
    "OPEN_CRITICAL_DAMAGE_CASE",
    "REGISTRATION_EXPIRED"
  ],
  "sourceSystems": [
    "DamageIntelligence",
    "Fleet"
  ],
  "evaluatedAt": "2026-06-27T10:00:00Z"
}
```

---

# Integration Vision

Fleet SHALL become the shared vehicle context layer across GCU365.

Integration vision:

```text
Fleet
  ↓
CROMS rental workflows
  ↓
Damage Intelligence inspection and damage workflows
  ↓
Maintenance repair workflows
  ↓
Finance asset and cost workflows
  ↓
IoT operational telemetry
  ↓
Reporting and executive dashboards
```

Fleet SHALL expose controlled APIs and events to keep connected systems aligned.

---

# Data Vision

Fleet data SHALL be structured, traceable, tenant-aware, and integration-ready.

Fleet data SHOULD support:

- Vehicle master data.
- Lifecycle history.
- Availability status.
- Assignment history.
- Document history.
- Maintenance references.
- Damage references.
- IoT references.
- Financial references.
- Operational holds.
- Compliance status.
- Audit records.

---

# AI and Intelligence Vision

Fleet MAY support AI-assisted intelligence in future phases.

Candidate capabilities MAY include:

- Predictive downtime.
- Preventive maintenance risk.
- Utilization optimization.
- Vehicle replacement recommendation.
- Damage risk analysis.
- Branch fleet balancing.
- Idle vehicle detection.
- Cost anomaly detection.
- Compliance risk detection.
- Fuel or energy consumption insights.

AI outputs SHALL be advisory unless approved governance defines otherwise.

---

# Security Vision

Fleet SHALL be secure by design.

Security vision includes:

- Authentication.
- Authorization.
- Tenant isolation.
- Branch-level access where required.
- Object-level authorization.
- Secure integration.
- Audit logging.
- Role-based administration.
- Secure document access.
- Secure IoT data access.
- No secrets in logs or reports.

---

# Privacy Vision

Fleet SHALL follow privacy-by-design.

Fleet SHOULD avoid unnecessary exposure of:

- Driver personal data.
- Customer personal data.
- Employee personal data.
- Precise location data unless authorized.
- Sensitive operational notes.
- Financial details unless authorized.

Fleet data access SHALL follow role and business need.

---

# Audit Vision

Fleet SHALL be auditable.

Audit SHOULD cover:

- Vehicle creation.
- Vehicle update.
- Status change.
- Availability override.
- Assignment change.
- Document upload.
- Document expiry override.
- Operational hold.
- Integration update.
- IoT device link or unlink.
- Configuration change.
- Access to sensitive vehicle records.

---

# Reporting Vision

Fleet reporting SHALL support operational and strategic decisions.

Reporting SHOULD answer:

- How many vehicles are active?
- How many vehicles are available?
- How many vehicles are rented?
- How many vehicles are under maintenance?
- How many vehicles are blocked by damage?
- How many vehicles are blocked by documents?
- How many vehicles are idle?
- Which branches have shortage or oversupply?
- Which vehicles have high downtime?
- Which vehicles have high cost?
- Which vehicles have recurring damage?
- Which vehicles are due for replacement?

---

# MVP Vision

The Fleet MVP SHOULD focus on the minimum capabilities required to establish trusted vehicle master and readiness visibility.

MVP SHOULD include:

- Vehicle master record.
- Vehicle list and detail.
- Vehicle status.
- Branch assignment.
- Basic availability.
- Basic document status.
- Basic Maintenance reference.
- Basic Damage Intelligence reference.
- Basic CROMS readiness reference.
- Audit logging.
- Role-based access.
- Tenant isolation.
- Basic fleet report.

MVP SHOULD NOT attempt to deliver full predictive intelligence, advanced IoT analytics, or automated financial accounting.

---

# Success Metrics

Fleet success SHOULD be measured using:

- Vehicle master completeness.
- Vehicle availability accuracy.
- Vehicle readiness accuracy.
- Reduction in unknown vehicle status.
- Reduction in downtime.
- Improvement in utilization.
- Reduction in duplicate vehicle records.
- Reduction in expired document incidents.
- Maintenance blocker visibility.
- Damage blocker visibility.
- Integration reliability.
- User adoption.
- Report usage.

---

# Risks and Constraints

Fleet roadmap SHALL consider the following risks:

| Risk | Description |
|------|-------------|
| Duplicate Vehicle Records | Poor master data can create operational confusion |
| Ownership Confusion | CROMS, Maintenance, Damage Intelligence, and Finance boundaries must remain clear |
| Status Conflict | Multiple systems may influence vehicle status |
| Data Quality | VIN, plate, branch, and ownership data must be accurate |
| Integration Failure | CROMS, Maintenance, IoT, or Damage Intelligence failures may affect readiness |
| Privacy Risk | Driver, customer, employee, and location data must be controlled |
| Security Risk | Vehicle and operational data must be protected |
| Over-Automation | AI recommendations must remain advisory without governance |
| Reporting Inaccuracy | Wrong readiness logic can mislead operations |
| Manual Overrides | Overrides require control and audit |

---

# Product Roadmap Direction

Fleet SHOULD be delivered through staged phases.

Recommended roadmap direction:

1. Vehicle master and basic status.
2. Branch assignment and document tracking.
3. CROMS readiness integration.
4. Maintenance status integration.
5. Damage Intelligence integration.
6. IoT and telematics integration.
7. Fleet dashboards.
8. Advanced utilization and downtime analytics.
9. Predictive maintenance and AI intelligence.
10. Optimization and executive decision support.

---

# Acceptance Criteria

## AC-FLEET-0001 — Vehicle Master Vision

Given the Fleet vision is reviewed, then Fleet SHALL be recognized as the vehicle master and operational readiness layer.

## AC-FLEET-0002 — Ownership Boundaries

Given Fleet integrates with CROMS, Maintenance, Damage Intelligence, Finance, and IoT, then system ownership boundaries SHALL remain clear.

## AC-FLEET-0003 — Readiness Concept

Given a vehicle is evaluated, then Fleet SHOULD provide readiness status and reason codes based on configured rules and external system inputs.

## AC-FLEET-0004 — MVP Direction

Given Fleet MVP is planned, then MVP SHOULD focus on vehicle master, status, branch assignment, basic availability, document status, audit, and tenant isolation.

## AC-FLEET-0005 — Security and Privacy Direction

Given Fleet is implemented, then tenant isolation, role-based access, auditability, and privacy-by-design SHALL be preserved.

---

# Normative Requirements

## Requirement

ID: REQ-FLEET-0001

Title:
Fleet Product Vision

Statement:
Fleet SHALL define the product vision for vehicle master, operational readiness, lifecycle visibility, integration, reporting, security, privacy, auditability, and future intelligence.

Priority:
Critical

Verification:
Product Review

---

## Requirement

ID: REQ-FLEET-0002

Title:
Vehicle Master Ownership

Statement:
Fleet SHALL be the system of record for vehicle master records, vehicle identity, vehicle attributes, and vehicle operational context.

Priority:
Critical

Verification:
Architecture Review

---

## Requirement

ID: REQ-FLEET-0003

Title:
Ownership Boundary Preservation

Statement:
Fleet SHALL preserve ownership boundaries with CROMS, Maintenance, Damage Intelligence, Finance, IoT, and other connected systems.

Priority:
Critical

Verification:
Architecture Review

---

## Requirement

ID: REQ-FLEET-0004

Title:
Vehicle Readiness Vision

Statement:
Fleet SHOULD provide vehicle readiness status and reason codes based on vehicle status, rental status, maintenance status, damage status, document status, compliance status, and operational holds.

Priority:
High

Verification:
Product Review

---

## Requirement

ID: REQ-FLEET-0005

Title:
Fleet Integration Vision

Statement:
Fleet SHALL define integration vision with CROMS, Maintenance, Damage Intelligence, IoT, Finance, Reporting, and enterprise platform services.

Priority:
High

Verification:
Integration Review

---

## Requirement

ID: REQ-FLEET-0006

Title:
Fleet Security Vision

Statement:
Fleet SHALL define security vision including authentication, authorization, tenant isolation, object-level access, secure integrations, and audit logging.

Priority:
Critical

Verification:
Security Review

---

## Requirement

ID: REQ-FLEET-0007

Title:
Fleet Privacy Vision

Statement:
Fleet SHALL define privacy vision for vehicle, driver, customer, employee, location, document, and operational data.

Priority:
High

Verification:
Privacy Review

---

## Requirement

ID: REQ-FLEET-0008

Title:
Fleet Audit Vision

Statement:
Fleet SHALL define audit vision for vehicle creation, updates, status changes, assignments, documents, integrations, overrides, and sensitive access.

Priority:
High

Verification:
Audit Review

---

## Requirement

ID: REQ-FLEET-0009

Title:
Fleet MVP Vision

Statement:
Fleet SHOULD define MVP direction covering vehicle master, status, branch assignment, availability, document status, references to Maintenance and Damage Intelligence, audit, RBAC, and tenant isolation.

Priority:
High

Verification:
Product Review

---

## Requirement

ID: REQ-FLEET-0010

Title:
Fleet Future Intelligence

Statement:
Fleet MAY support future AI-assisted intelligence for downtime prediction, utilization optimization, replacement recommendation, compliance risk, and cost anomaly detection.

Priority:
Medium

Verification:
Roadmap Review

---

# Business Rules

## BR-FLEET-0001 — Fleet Owns Vehicle Master

Fleet SHALL own the authoritative vehicle master record.

---

## BR-FLEET-0002 — CROMS Owns Rental Lifecycle

Fleet SHALL NOT own rental agreements, rental closure, or final rental decisions.

---

## BR-FLEET-0003 — Maintenance Owns Work Orders

Fleet SHALL NOT own Maintenance work order execution or final repair workflow.

---

## BR-FLEET-0004 — Damage Intelligence Owns Damage Evidence

Fleet SHALL NOT own inspection evidence or damage case decision records.

---

## BR-FLEET-0005 — Finance Owns Financial Postings

Fleet SHALL NOT own final accounting, invoices, depreciation, or financial postings.

---

## BR-FLEET-0006 — Vehicle Readiness Must Be Explainable

Vehicle readiness SHALL include reason codes and source systems where practical.

---

## BR-FLEET-0007 — Status Overrides Must Be Audited

Manual overrides of vehicle status, availability, readiness, or blocker state SHALL be audited.

---

## BR-FLEET-0008 — Tenant Isolation Is Mandatory

Vehicle records SHALL be tenant-isolated.

---

# AI Implementation Contract

AI development agents SHALL:

- Treat this document as the authoritative product vision for Fleet.
- Preserve all requirement IDs, acceptance criterion IDs, and business rule IDs.
- Generate future Fleet requirements, user stories, APIs, domain models, events, tests, dashboards, and implementation plans consistent with this document.
- Preserve vehicle master ownership by Fleet.
- Preserve ownership boundaries with CROMS, Maintenance, Damage Intelligence, Finance, IoT, and Reporting.
- Preserve tenant isolation, security, privacy, and auditability requirements.
- Never assign rental lifecycle ownership, work order execution ownership, damage evidence ownership, or financial posting ownership to Fleet.
- Treat AI outputs as advisory unless approved governance defines otherwise.
- Raise ambiguity where ownership, readiness logic, integration source of truth, or override authority is unclear.

---

# References

- DI-0001 – Damage Intelligence Product Vision
- DI-0017 – Integration with CROMS
- DI-0018 – Integration with Maintenance
- PLATFORM-0005 – GEES Core and Application Architecture
- GEES-0007 – Enterprise Security Standard
- GEES-0009 – Traceability Standard

---

# Revision History

| Version | Date | Description |
|----------|------|-------------|
| 1.0.0 | 2026-06-27 | Initial Fleet Product Vision |
