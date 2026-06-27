# GEES Repository Index

**Project:** GCU365 Enterprise Engineering Specification (GEES)

**Purpose:** Repository Navigation Guide

**Version:** 1.0.0

---

# Purpose

This document provides a single navigation entry point to the entire GEES repository.

It is intended for:

* Software Engineers
* Solution Architects
* Enterprise Architects
* AI Development Platforms
* Reviewers
* Product Owners

It identifies where authoritative information is located and the recommended reading order.

---

# Repository Overview

```text
Repository Root
│
├── Damage Intelligence
├── Onboarding
├── Governance
├── Enterprise Architecture
├── Platform Architecture
├── Business Specifications
├── Build Package
├── Knowledge Graph
├── Traceability
├── Reference Material
├── Machine-Readable Specifications (planned)
└── Source Code (planned)
```

---
## Damage Intelligence

- Folder: [docs/07-Damage-Intelligence/](docs/07-Damage-Intelligence/)
- Index: [docs/07-Damage-Intelligence/README.md](docs/07-Damage-Intelligence/README.md)
- Scope: Vehicle inspection evidence, AI-assisted damage detection, damage comparison, damage cases, CROMS integration, Maintenance integration, reporting, audit, retention, monitoring, localization, [...]
---
# Root-Level Documents

## START_HERE.md

Primary entry point for all developers and AI assistants.

Purpose:

* Repository bootstrap
* Mandatory reading order
* AI implementation rules

---

## WHAT_THIS_REPOSITORY_IS.md

Explains:

* What GEES is
* What GEES is not
* Repository intent
* Relationship between GEES and GCU365 products

---

## IMPLEMENTATION_STATUS.md

Current implementation maturity.

Includes:

* Current phase
* Completion status
* Planned milestones

---

## ROADMAP_TO_IMPLEMENTATION.md

Implementation roadmap.

Explains:

* Engineering lifecycle
* Development phases
* GEES Core implementation sequence
* Business application implementation sequence

---

## README.md

General repository overview.

---

# Documentation Structure

## 00-Constitution

Defines the engineering constitution and governing principles.

Examples:

* GEES Master Blueprint
* Executive Vision
* Enterprise Philosophy

---

## 01-Normative

Enterprise engineering standards.

Examples:

* Security
* Architecture
* Development
* Documentation
* Testing
* UX

---

## 02-Enterprise-Foundation

Enterprise vision and foundational concepts.

---

## 03-Reference-Architecture

Authoritative enterprise architecture.

Includes:

* Enterprise Context
* Domain-Driven Design
* Business Architecture
* Information Architecture
* Application Architecture
* Technology Architecture

---

## 04-Platform

Platform-level specifications.

Includes:

* Platform Architecture
* Logical Domain Model
* GEES Core Architecture
* Knowledge Graph

---

## 05–20 Domain Specifications

Business product specifications.

Current priorities:

* CROMS
* Damage Intelligence
* Maintenance

Future areas include:

* Fleet
* Mobile
* Web
* AI
* APIs
* Database
* Security
* DevOps
* QA
* UX
* ADRs
* Templates
* Glossary

---

## 21–24 Platform & Build

Platform implementation guidance.

Includes:

* Platform Services
* Catalogs
* GEES Language
* Build Package

---

## 95-Roadmaps

Strategic engineering roadmaps.

---

## 96-Reference

External references and standards.

---

## 97-Meta

Repository governance.

Includes:

* Universal Engineering Registry
* Engineering Metamodel
* Lifecycle
* Naming Standards
* Metadata Standards

---

## 98-Knowledge-Graph

Knowledge Graph architecture and specifications.

---

## 99-Appendices

Supporting material, requirement registries, and reference appendices.

---

# Authoritative Documents

The following documents define the engineering authority of the repository:

1. GEES-0000 – Master Blueprint
2. Repository Architecture
3. Universal Engineering Registry
4. Engineering Metamodel
5. Enterprise Architecture
6. Platform Specifications
7. Build Package
8. Approved Requirements

Generated code SHALL conform to these documents.

---

# Recommended Reading Order

## For New Engineers

1. START_HERE.md
2. WHAT_THIS_REPOSITORY_IS.md
3. IMPLEMENTATION_STATUS.md
4. ROADMAP_TO_IMPLEMENTATION.md
5. GEES-0000 – Master Blueprint
6. Enterprise Architecture
7. Platform Specifications
8. Build Package

---

## For AI Development Platforms

1. START_HERE.md
2. WHAT_THIS_REPOSITORY_IS.md
3. AI Developer Onboarding Guide
4. Master Blueprint
5. Universal Engineering Registry
6. Engineering Metamodel
7. Platform Specifications
8. Applicable Requirements
9. Build Package

---

## For Product Owners

1. Executive Vision
2. Enterprise Philosophy
3. Domain Specifications
4. Roadmaps

---

# Planned Repository Areas

The following areas are planned for future implementation:

## specs/

Machine-readable assets:

* JSON Schemas
* OpenAPI Specifications
* Validation Rules
* Graph Schemas

---

## src/

Production implementation of GEES Core and governed applications.

---

## tests/

Automated testing assets.

---

## tools/

Engineering automation tools.

---

# Repository Status

Current Phase:

**Architecture Baseline**

Next Phase:

**Business Specifications**

Implementation Status:

**Pre-Implementation**

---

# Repository Principles

This repository follows these principles:

* Specification First
* Architecture First
* AI Native
* Documentation as Code
* Domain-Driven Design
* API First
* Traceability by Design
* Security by Design
* Governance by Default

---

# Final Note

This repository is the authoritative engineering source of truth for the GEES Framework.

Every implementation SHALL trace back to approved specifications contained within this repository.

No implementation SHALL supersede the approved engineering architecture or governance.
