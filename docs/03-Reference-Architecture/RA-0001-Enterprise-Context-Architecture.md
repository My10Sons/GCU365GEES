---
id: RA-0001
title: Enterprise Context Architecture
version: 1.0.0
document_type: Architecture Standard
document_class: Reference Architecture
status: Draft
classification: Internal
owner: Riyadah Technology
reviewers:
  - Chief Enterprise Architect
  - CTO
approvers: []
created: 2026-06-27
updated: 2026-06-27
effective_date: TBD
next_review: 2027-06-27
authoritative: true
ai_consumable: true

related:
  - GEES-0006
  - GEES-0007
  - GEES-0009
---

# Enterprise Context Architecture

---

# Executive Summary

This document defines the highest level architecture of the GCU365 Platform.

It establishes:

• System boundaries

• Business domains

• Shared enterprise services

• External integrations

• Product ownership

• Data ownership

• Context relationships

Every future architecture document SHALL conform to this enterprise context.

---

# Purpose

The purpose of this document is to establish a single architectural view of the entire GCU365 ecosystem before defining detailed product specifications.

This architecture SHALL govern:

- GCU365 CROMS
- GCU365 Maintenance
- Damage Intelligence Platform

---

# Scope

Included

✓ CROMS

✓ Maintenance

✓ Damage Intelligence

✓ Shared Services

✓ AI Platform

✓ External Integrations

Excluded

✗ Internal implementation details

✗ Database schema

✗ API definitions

✗ UI specifications

These are documented separately.

---

# Architectural Vision

GCU365 SHALL operate as a unified enterprise platform composed of multiple business domains sharing common enterprise services.

Business domains SHALL remain logically independent while operating within a single enterprise architecture.

---

# Enterprise Context

```
                            GCU365 Platform

        ┌──────────────────────────────────────────────────┐
        │                                                  │
        │               Shared Enterprise Platform          │
        │                                                  │
        │ Authentication                                   │
        │ Authorization                                    │
        │ Notification                                     │
        │ Audit                                             │
        │ Document Management                               │
        │ AI Gateway                                        │
        │ Reporting                                         │
        │ Workflow                                          │
        │ Configuration                                     │
        └──────────────────────────────────────────────────┘

                       ▲
                       │

        ┌──────────────┼──────────────┐
        │                             │

   GCU365 CROMS              GCU365 Maintenance

        │                             │

        └──────────────┬──────────────┘
                       │

            Damage Intelligence Platform

                       │

              Computer Vision Engine

                       │

                AI Decision Services
```

---

# External Actors

The platform interacts with:

Rental Company

Workshop

Maintenance Technician

Customer

Driver

Insurance Company

Saudi TGA

Yaqeen

Payment Gateway

SMS Provider

Email Provider

Cloud Storage

Maps Provider

---

# Primary Products

## GCU365 CROMS

Responsible for

Rental Operations

Reservations

Rental Contracts

Vehicle Availability

Customers

Branches

Fleet Assignment

Driver Management

Invoices

Payments

Vehicle Check-in

Vehicle Check-out

Vehicle Status

---

## GCU365 Maintenance

Responsible for

Maintenance Operations

Work Orders

Inspection Management

Workshop Management

Inventory

Parts

Technicians

Labour

Vendor Repairs

Warranty

Maintenance Scheduling

Quality Control

---

## Damage Intelligence Platform

Responsible for

Image Processing

Computer Vision

Damage Detection

Damage Classification

Damage Comparison

Historical Damage Matching

Repair Cost Estimation

Fraud Detection

AI Recommendations

Damage Reports

---

# Shared Enterprise Services

The following services SHALL be shared.

Authentication

Authorization

Notification Service

Audit Service

Document Service

Image Service

Workflow Engine

Reporting Engine

Search Engine

Configuration Service

AI Gateway

Logging

Monitoring

---

# Business Domains

Vehicle Domain

Customer Domain

Rental Domain

Maintenance Domain

Workshop Domain

Damage Domain

Inventory Domain

Financial Domain

Identity Domain

Reporting Domain

Notification Domain

AI Domain

---

# System Ownership

| Capability | Owner |
|------------|-------|
| Vehicle Master | CROMS |
| Customer Master | CROMS |
| Rental Agreement | CROMS |
| Vehicle Availability | CROMS |
| Maintenance History | Maintenance |
| Work Orders | Maintenance |
| Parts Inventory | Maintenance |
| Workshop Operations | Maintenance |
| Damage Detection | Damage Intelligence |
| Damage Assessment | Damage Intelligence |
| Repair Estimate | Damage Intelligence |
| AI Recommendations | Damage Intelligence |

---

# Enterprise Data Ownership

Every business entity SHALL have one authoritative owner.

Examples

Vehicle

Owner:

CROMS

Maintenance SHALL consume Vehicle information.

It SHALL NOT own Vehicle records.

Likewise

Work Order

Owner:

Maintenance

CROMS SHALL reference Work Orders.

It SHALL NOT own them.

---

# Integration Model

Communication between domains SHALL occur through approved APIs or enterprise events.

Direct database access between domains SHALL NOT be permitted.

---

# Primary Business Events

Rental Started

Rental Extended

Rental Closed

Vehicle Checked Out

Vehicle Returned

Vehicle Inspection Started

Vehicle Inspection Completed

Damage Detected

Damage Approved

Damage Rejected

Repair Approved

Repair Started

Repair Completed

Vehicle Released

---

# Enterprise Workflow

```
Customer

↓

Reservation

↓

Rental Agreement

↓

Vehicle Check-Out

↓

Rental

↓

Vehicle Return

↓

AI Damage Inspection

↓

Maintenance Decision

↓

Work Order

↓

Repair

↓

Quality Inspection

↓

Vehicle Available
```

---

# External Integrations

Saudi Transport General Authority

Yaqeen

Payment Gateway

SMS Gateway

Email Gateway

Azure AI

OpenAI

Maps API

Storage

---

# Security Boundary

Every external request SHALL pass through:

Authentication

↓

Authorization

↓

Validation

↓

Business Logic

↓

Audit

↓

Persistence

---

# AI Context

Artificial Intelligence SHALL assist:

Vehicle Inspection

Damage Detection

Damage Comparison

Repair Estimation

Maintenance Planning

Image Analysis

Document OCR

Operational Analytics

---

# Architecture Constraints

The platform SHALL:

Support Multi-tenancy

Support Horizontal Scaling

Support Offline Mobile

Support Cloud Deployment

Support High Availability

Support Full Auditability

Support Complete Traceability

Support Regulatory Compliance

---

# Technology Baseline

Backend

ASP.NET Core

Language

C#

AI

Python

Database

PostgreSQL

Cache

Redis

Message Broker

RabbitMQ

Storage

Azure Blob Storage

Authentication

OAuth2/OpenID Connect

Mobile

Flutter

Web

Blazor

Monitoring

OpenTelemetry

Hosting

Microsoft Azure

---

# Normative Requirements

### Requirement

ID: REQ-ARCH-1000

Title

Unified Enterprise Context

Statement

Every GCU365 product SHALL conform to the Enterprise Context Architecture.

Priority

Critical

Verification

Architecture Review

---

### Requirement

ID: REQ-ARCH-1001

Title

Single Capability Ownership

Statement

Every enterprise capability SHALL have exactly one business owner.

Priority

Critical

Verification

Architecture Review

---

### Requirement

ID: REQ-ARCH-1002

Title

Domain Independence

Statement

Business domains SHALL communicate only through approved integration mechanisms.

Priority

Critical

Verification

Architecture Review

---

### Requirement

ID: REQ-ARCH-1003

Title

Shared Enterprise Services

Statement

Enterprise services SHALL be reused before introducing duplicate implementations.

Priority

High

Verification

Architecture Review

---

### Requirement

ID: REQ-ARCH-1004

Title

AI Integration

Statement

Damage Intelligence SHALL operate as a shared enterprise capability accessible by both CROMS and Maintenance.

Priority

Critical

Verification

Architecture Review

---

# AI Implementation Contract

AI development agents SHALL:

Read this architecture before implementing any product.

Respect business ownership.

Respect data ownership.

Never bypass shared enterprise services.

Never introduce duplicate business capabilities.

Generate implementations that conform to this architecture.

Raise architectural conflicts instead of making assumptions.

---

# References

GEES-0006 Enterprise Architecture Standard

GEES-0007 Enterprise Security Standard

GEES-0009 Traceability Standard

---

# Revision History

| Version | Date | Description |
|----------|------------|--------------------------------|
|1.0.0|2026-06-27|Initial Enterprise Context Architecture|