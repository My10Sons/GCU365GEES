---

id: GBP-0015
title: AI Developer Onboarding Guide
version: 1.0.0
document_type: Build Package
document_class: AI Implementation Guide
status: Approved
classification: Internal
owner: Riyadah Technology
reviewers:

* Chief Enterprise Architect
* Chief Technology Officer
  approvers: []
  created: 2026-06-27
  updated: 2026-06-27
  authoritative: true
  ai_consumable: true

---

# AI Developer Onboarding Guide

## Executive Summary

This document is the mandatory onboarding guide for all AI-assisted software development tools implementing the GCU365 Enterprise Engineering Specification (GEES).

Before generating code, modifying architecture, or creating engineering artifacts, every AI development assistant SHALL consume this guide.

Failure to follow this guide may result in architecture drift, broken traceability, inconsistent implementations, or violations of the GEES Framework.

---

# 1. What GEES Is

GEES (GCU365 Enterprise Engineering Specification) is **not an application**.

GEES is an AI-native enterprise engineering framework that governs how enterprise software is designed, implemented, validated, documented, and maintained.

GEES is the authoritative engineering source of truth.

Applications such as GCU365 CROMS, GCU365 Maintenance, and future GCU365 products SHALL be implemented in accordance with GEES.

---

# 2. What GEES Is Not

GEES is NOT:

* A sample application.
* A starter template.
* A generic software framework.
* A collection of coding guidelines.
* A code-generation experiment.

AI SHALL NOT attempt to replace GEES with alternative architectures or technology choices.

---

# 3. Source of Truth

When multiple artifacts exist, the following order of precedence SHALL apply:

1. GEES Master Blueprint
2. Engineering Constitution
3. Repository Architecture
4. Universal Engineering Registry
5. Engineering Metamodel
6. Enterprise Architecture
7. Platform Specifications
8. Approved Requirements
9. Build Package
10. Machine-readable Schemas
11. Source Code

Source code SHALL NEVER override an approved engineering specification.

---

# 4. Architecture Principles

Implementation SHALL preserve the approved architecture.

Core principles include:

* Domain-Driven Design (DDD)
* API-First
* AI-First
* Documentation as Code
* Event-Driven Integration where appropriate
* Modular Architecture
* Complete Traceability
* Security by Design
* Observability by Design

AI SHALL NOT introduce architectural patterns that conflict with approved GEES documents.

---

# 5. Approved Technology Stack

The approved technology stack is:

| Layer               | Standard                       |
| ------------------- | ------------------------------ |
| Backend             | ASP.NET Core (.NET)            |
| Frontend            | Blazor Web App                 |
| AI Services         | Python                         |
| Relational Database | PostgreSQL                     |
| Knowledge Graph     | Neo4j                          |
| Search              | OpenSearch                     |
| Cache               | Redis                          |
| Messaging           | RabbitMQ                       |
| Object Storage      | Azure Blob Storage             |
| Authentication      | Microsoft Entra ID or Keycloak |
| CI/CD               | GitHub Actions                 |
| Containers          | Docker                         |
| Orchestration       | Kubernetes (when required)     |

AI SHALL NOT substitute technologies unless explicitly authorized by an approved Architecture Decision Record (ADR).

---

# 6. Universal Engineering Registry

Every engineering object SHALL be represented as a governed object with:

* Unique Identifier
* Name
* Version
* Status
* Owner
* Metadata
* Relationships
* Traceability
* Lifecycle
* Audit History

AI SHALL preserve these attributes in every generated implementation.

---

# 7. Engineering Metamodel

Every engineering artifact inherits from the EngineeringObject metamodel.

Examples include:

* Requirement
* Capability
* Service
* API
* Event
* Workflow
* Entity
* AI Agent
* Business Rule
* Test Case
* Architecture Document

Generated code SHALL reflect this model where applicable.

---

# 8. Knowledge Graph

The GEES Knowledge Graph is a foundational platform capability.

Every governed engineering object SHALL become a graph node.

Every governed relationship SHALL become a graph edge.

AI SHALL:

* Preserve graph relationships.
* Update traceability.
* Never create orphaned engineering objects.

---

# 9. Build Sequence

Implementation SHALL follow this order:

1. Shared Kernel
2. Universal Engineering Registry
3. Artifact Repository
4. Metadata Engine
5. Workflow Engine
6. Validation Engine
7. Knowledge Graph
8. Traceability Engine
9. Search Engine
10. Metrics Engine
11. AI Orchestrator
12. Engineering Portal
13. Reporting
14. Administration
15. Product-Specific Modules (e.g., CROMS, Maintenance)

AI SHALL NOT implement downstream modules before their prerequisites.

---

# 10. AI Responsibilities

Before generating code, AI SHALL:

* Read the relevant requirements.
* Read the applicable architecture documents.
* Read the service specification.
* Read the API specification.
* Read the validation rules.
* Read the Build Package.

If required information is missing, AI SHALL request clarification instead of inventing requirements.

---

# 11. AI Prohibitions

AI SHALL NOT:

* Invent requirements.
* Invent business rules.
* Invent APIs.
* Invent workflows.
* Invent entities.
* Replace the approved technology stack.
* Ignore traceability.
* Modify approved architecture without authorization.

---

# 12. Required Deliverables

Every implementation SHALL include:

* Production-ready source code.
* Automated tests.
* API documentation.
* Updated traceability.
* Updated metadata.
* Security controls.
* Logging.
* Health checks.

---

# 13. Quality Gates

Every implementation SHALL satisfy:

* Architecture compliance.
* Coding standards.
* Static analysis.
* Unit tests.
* Integration tests.
* Security review.
* Documentation updates.
* Traceability validation.

No implementation SHALL be considered complete until all quality gates are passed.

---

# 14. When in Doubt

If ambiguity exists, AI SHALL:

1. Stop implementation.
2. Report the ambiguity.
3. Identify the missing authoritative artifact.
4. Request clarification.

AI SHALL NEVER guess.

---

# 15. Success Criteria

A successful implementation:

* Conforms to GEES.
* Preserves architecture.
* Preserves governance.
* Preserves traceability.
* Produces maintainable, production-quality software.

The objective is not simply to generate code, but to implement the GEES Platform faithfully and provide a stable foundation for all GCU365 products.

---

# References

* GEES-0000 – Master Blueprint
* META-0010 – Universal Engineering Registry Standard
* META-0011 – Engineering Metamodel
* PLATFORM-0003 – GEES Platform System Architecture
* PLATFORM-0004 – GEES Knowledge Graph Specification
* GBP-0001 – Build Manifest
* GBP-0013 – Implementation Playbook
* GBP-0014 – Architecture Readiness Review

---

# Revision History

| Version | Date       | Description                           |
| ------- | ---------- | ------------------------------------- |
| 1.0.0   | 2026-06-27 | Initial AI Developer Onboarding Guide |

