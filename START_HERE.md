# 🚀 START HERE — GEES AI Bootstrap

**Repository:** GCU365 Enterprise Engineering Specification (GEES)

**Version:** 1.0.0

---

# STOP

Before generating **ANY** code, documentation, architecture, database schema, API, UI, workflow, AI model, or engineering artifact, you MUST read this file completely.

Failure to follow these instructions will result in an invalid implementation.

---

# What is GEES?

GEES is **NOT** an application.

GEES is an **AI-native Enterprise Engineering Framework**.

Its purpose is to govern the design, implementation, validation, deployment, and lifecycle management of enterprise software.

Applications such as:

* GCU365 CROMS
* GCU365 Maintenance
* Future GCU365 products

are implemented **using GEES**.

GEES itself is the engineering operating system.

---

# Your Role

You are **NOT** the software architect.

The architecture has already been approved.

Your responsibility is to implement the approved engineering specifications.

You SHALL:

* Preserve architecture.
* Preserve identifiers.
* Preserve traceability.
* Preserve metadata.
* Preserve governance.

You SHALL NOT invent architecture.

---

# Read These Documents In Order

Before writing code, read the following documents in sequence.

## 1

```
docs/00-Constitution/GEES-0000-Master-Blueprint.md
```

This defines the entire framework.

---

## 2

```
docs/24-Build-Package/GBP-0015-AI-Developer-Onboarding-Guide.md
```

This defines your responsibilities.

---

## 3

```
docs/97-Meta/META-0010-Universal-Engineering-Registry-Standard.md
```

Everything inherits from this.

---

## 4

```
docs/97-Meta/META-0011-Engineering-Metamodel.md
```

This defines every engineering object.

---

## 5

Read the Enterprise Architecture.

* Business Architecture
* Capability Architecture
* Information Architecture
* Application Architecture
* Technology Architecture

---

## 6

Read the Platform Specifications.

Especially:

* Platform Architecture
* Knowledge Graph
* Build Package

---

## 7

Read the applicable Requirements.

---

## 8

Only after all previous documents have been consumed MAY implementation begin.

---

# Authoritative Precedence

If two documents conflict, the following precedence SHALL apply.

1. START_HERE.md
2. GEES Master Blueprint
3. Engineering Constitution
4. Meta Standards
5. Universal Engineering Registry
6. Engineering Metamodel
7. Enterprise Architecture
8. Platform Specifications
9. Approved Requirements
10. Build Package
11. Source Code

Source Code SHALL NEVER override an approved specification.

---

# Mandatory Technology Stack

Unless an approved ADR states otherwise, implementation SHALL use:

| Layer           | Standard                      |
| --------------- | ----------------------------- |
| Backend         | ASP.NET Core (.NET)           |
| Frontend        | Blazor Web App                |
| AI              | Python                        |
| Database        | PostgreSQL                    |
| Knowledge Graph | Neo4j                         |
| Search          | OpenSearch                    |
| Cache           | Redis                         |
| Messaging       | RabbitMQ                      |
| Authentication  | Microsoft Entra ID / Keycloak |
| Containers      | Docker                        |
| CI/CD           | GitHub Actions                |

Do not substitute technologies.

---

# Mandatory Build Sequence

Implement in this order:

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
13. Administration
14. Product Modules

---

# Before Writing Code

Confirm:

* Requirements reviewed.
* Architecture reviewed.
* Platform documents reviewed.
* Applicable standards reviewed.
* Dependencies identified.

If any required information is missing:

STOP.

Request clarification.

Never guess.

---

# Deliverables

Every implementation SHALL include:

* Production-ready source code.
* Unit tests.
* Integration tests.
* API documentation.
* Traceability updates.
* Security controls.
* Logging.
* Health checks.

---

# Definition of Success

A successful implementation is one that:

* Implements the approved requirements.
* Preserves the approved architecture.
* Passes all quality gates.
* Maintains complete traceability.
* Produces maintainable enterprise-grade software.

The goal is not simply to generate code.

The goal is to faithfully implement the GEES Platform.

---

# Final Instruction

If you have not read the required documents listed above, you are **not authorized** to begin implementation.

