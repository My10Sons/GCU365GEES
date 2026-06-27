---
id: RA-0002
title: Domain-Driven Design Architecture
version: 1.0.0
document_type: Reference Architecture
document_class: Domain Architecture
status: Draft
classification: Internal
owner: Riyadah Technology
reviewers:
  - Chief Enterprise Architect
  - CTO
created: 2026-06-27
updated: 2026-06-27
ai_consumable: true
authoritative: true
related:
  - RA-0001
  - GEES-0006
---

# Domain-Driven Design Architecture

## Executive Summary

This document defines the Domain-Driven Design (DDD) architecture for the GCU365 platform.

It establishes business boundaries, ownership rules, aggregates, entities, value objects, repositories, domain services, and domain events.

This architecture SHALL govern all software developed for:

- GCU365 CROMS
- GCU365 Maintenance
- Damage Intelligence Platform

---

# Purpose

To ensure that business logic is organized according to business capabilities rather than technical layers.

---

# Architecture Philosophy

Business domains SHALL own business rules.

Infrastructure SHALL NOT own business rules.

User interfaces SHALL NOT contain business logic.

Databases SHALL persist domain state but SHALL NOT implement business behavior.

---

# Enterprise Domains

The platform SHALL consist of the following bounded contexts.

## Identity

Responsible for:

- Users
- Roles
- Permissions
- Authentication
- Authorization

---

## Customer

Responsible for:

- Customers
- Corporate Customers
- Drivers
- Contacts

---

## Vehicle

Responsible for:

- Vehicle Master
- Vehicle Status
- Vehicle Specifications
- VIN
- Registration

---

## Rental (CROMS)

Responsible for:

- Reservations
- Rental Agreements
- Check-Out
- Check-In
- Rental Billing
- Vehicle Availability

---

## Maintenance

Responsible for:

- Work Orders
- Repairs
- Technicians
- Workshops
- Labour
- Parts
- Preventive Maintenance

---

## Damage Intelligence

Responsible for:

- Image Analysis
- Damage Detection
- Damage Classification
- Damage Comparison
- Severity Assessment
- AI Recommendations
- Repair Cost Estimation

---

## Inventory

Responsible for:

- Spare Parts
- Suppliers
- Stock Levels
- Warehouses

---

## Financial

Responsible for:

- Charges
- Payments
- Invoices
- Cost Allocation

---

## Reporting

Responsible for:

- KPIs
- Dashboards
- Analytics

---

# Bounded Context Relationships

```text
Customer
      │
      ▼
Vehicle
      │
      ▼
Rental
      │
      ▼
Damage Intelligence
      │
      ▼
Maintenance
      │
      ▼
Financial
```

---

# Aggregate Roots

## Vehicle

Aggregate Root

Contains

Vehicle

Vehicle Status

Registration

Insurance

Inspection History

---

## Rental Agreement

Aggregate Root

Contains

Rental Contract

Rental Driver

Rental Charges

Rental Extensions

Rental Return

---

## Work Order

Aggregate Root

Contains

Repair Lines

Labour

Parts

Technicians

Approvals

---

## Damage Case

Aggregate Root

Contains

Captured Images

AI Findings

Manual Review

Approval

Repair Estimate

History

---

# Value Objects

Examples

Vehicle VIN

License Plate

Money

Mileage

GPS Coordinates

Phone Number

Email Address

Engine Number

Color

Damage Severity

These SHALL be immutable.

---

# Domain Services

Examples

Rental Pricing Service

Vehicle Availability Service

Damage Comparison Service

Maintenance Scheduling Service

Repair Cost Estimation Service

Vehicle Assignment Service

Invoice Calculation Service

---

# Domain Events

Examples

Reservation Created

Rental Started

Rental Extended

Vehicle Checked Out

Vehicle Returned

Vehicle Inspected

Damage Detected

Damage Approved

Work Order Created

Repair Started

Repair Completed

Vehicle Released

Invoice Generated

Payment Received

---

# Repository Interfaces

Each Aggregate Root SHALL expose one Repository.

Examples

Vehicle Repository

Rental Repository

WorkOrder Repository

Damage Repository

Customer Repository

Repositories SHALL hide persistence implementation.

---

# Application Services

Application Services SHALL orchestrate use cases.

Examples

Create Reservation

Return Vehicle

Generate Work Order

Approve Damage

Close Work Order

Generate Invoice

Application Services SHALL NOT contain core business rules.

---

# Domain Rules

Business rules SHALL remain inside the domain model.

Business rules SHALL NOT exist inside:

Controllers

Views

SQL

Mobile Apps

External APIs

---

# Integration Rules

Domains SHALL communicate through:

Application Services

Domain Events

Approved APIs

Direct database communication SHALL NOT occur.

---

# AI Integration

Damage Intelligence SHALL behave as an independent domain.

Other domains SHALL consume AI results through contracts rather than directly invoking AI models.

---

# Folder Structure Recommendation

```text
src/

Domain/
    Customer/
    Vehicle/
    Rental/
    Maintenance/
    Damage/
    Inventory/
    Financial/

Application/

Infrastructure/

Presentation/
```

---

# Normative Requirements

### Requirement

ID: REQ-DDD-0001

Title

Bounded Contexts

Statement

Business capabilities SHALL be implemented within approved bounded contexts.

Priority

Critical

Verification

Architecture Review

---

### Requirement

ID: REQ-DDD-0002

Title

Aggregate Ownership

Statement

Each Aggregate Root SHALL own its entities and invariants.

Priority

Critical

Verification

Code Review

---

### Requirement

ID: REQ-DDD-0003

Title

Business Logic

Statement

Business rules SHALL reside within the domain layer.

Priority

Critical

Verification

Architecture Review

---

### Requirement

ID: REQ-DDD-0004

Title

Repository Pattern

Statement

Aggregate Roots SHALL expose repositories independent of persistence technology.

Priority

High

Verification

Code Review

---

### Requirement

ID: REQ-DDD-0005

Title

Domain Events

Statement

Cross-domain communication SHALL occur using domain events or approved APIs.

Priority

Critical

Verification

Architecture Review

---

# AI Implementation Contract

AI development agents SHALL:

- Respect bounded contexts.
- Never duplicate business rules.
- Generate aggregate roots correctly.
- Preserve domain ownership.
- Use repositories instead of direct persistence.
- Keep business logic inside the domain layer.
- Raise architectural conflicts instead of making assumptions.

---

# References

RA-0001 Enterprise Context Architecture

GEES-0006 Enterprise Architecture Standard

GEES-0009 Traceability Standard

---

# Revision History

| Version | Date | Description |
|----------|------------|------------------------------|
|1.0.0|2026-06-27|Initial DDD Architecture|