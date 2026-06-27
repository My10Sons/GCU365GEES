# WHAT THIS REPOSITORY IS

# Read This Before Doing Anything

If you are an AI coding assistant (Emergent, ChatGPT, Claude, Cursor, Windsurf, GitHub Copilot, etc.), **read this document before analyzing the repository or generating code**.

---

# This Repository Is NOT an Application

This repository does **not** contain the implementation of GCU365.

It is **not** intended to be:

* A starter application
* A code template
* A software framework
* A runnable product
* An MVP

The absence of application code is **intentional**.

---

# What This Repository Is

This repository contains the **GCU365 Enterprise Engineering Specification (GEES)**.

GEES is the authoritative engineering framework used to design, govern, validate, and implement enterprise software.

Think of GEES as an **Engineering Operating System**, not an application.

---

# Purpose

GEES defines:

* Enterprise engineering standards
* Engineering governance
* Enterprise architecture
* Platform architecture
* Domain-driven design
* Engineering metadata
* Traceability
* Knowledge graph model
* AI engineering rules
* Build rules
* Implementation sequence

Applications are built **from GEES**.

They are **not** the repository itself.

---

# Products Governed by GEES

GEES governs the implementation of products including:

* GCU365 CROMS
* GCU365 Maintenance
* GCU365 Damage Intelligence
* Future GCU365 platforms

GEES is the engineering authority for these systems.

---

# Source of Truth

Implementation SHALL follow the approved GEES documentation.

Source code SHALL conform to GEES.

GEES SHALL NOT be modified to match generated source code.

Engineering specifications always take precedence.

---

# Repository Maturity

This repository is currently in the **Architecture Baseline** stage.

The architecture has been designed.

The implementation has intentionally **not** been created yet.

This repository is preparing for AI-assisted implementation.

Do not interpret the absence of source code as missing work.

It is a deliberate phase of the project.

---

# Your Role

If you are an AI assistant:

Your responsibility is **implementation**, not architecture.

You SHALL:

* Read the architecture.
* Read the platform specifications.
* Read the Build Package.
* Read the implementation playbook.
* Implement the approved design.

You SHALL NOT:

* Replace the architecture.
* Introduce a different technology stack.
* Invent requirements.
* Invent APIs.
* Invent workflows.
* Invent entities.
* Remove traceability.

If required information is missing, report the gap instead of making assumptions.

---

# Technology Stack

Unless an approved Architecture Decision Record (ADR) states otherwise, implementation SHALL use:

* ASP.NET Core (.NET)
* Blazor Web App
* Python (AI services only)
* PostgreSQL
* Neo4j
* OpenSearch
* Redis
* RabbitMQ
* Azure Blob Storage
* GitHub Actions
* Docker
* Kubernetes (when required)

Alternative technologies SHALL NOT be introduced without architectural approval.

---

# Implementation Order

Implementation SHALL proceed in this sequence:

1. GEES Core
2. Universal Engineering Registry
3. Artifact Repository
4. Metadata Engine
5. Workflow Engine
6. Validation Engine
7. Knowledge Graph
8. Traceability Engine
9. Search Engine
10. AI Orchestrator
11. Engineering Portal
12. Product Modules

Products such as CROMS and Maintenance SHALL be implemented only after the GEES Core platform is established.

---

# Required Reading

Before implementation, read these documents in order:

1. START_HERE.md
2. docs/00-Constitution/GEES-0000-Master-Blueprint.md
3. docs/24-Build-Package/GBP-0015-AI-Developer-Onboarding-Guide.md
4. Universal Engineering Registry Standard
5. Engineering Metamodel
6. Enterprise Architecture
7. Platform Specifications
8. Approved Requirements

Do not begin implementation until these documents have been reviewed.

---

# Final Statement

GEES is an AI-native enterprise engineering platform specification.

It exists to enable consistent, governed, traceable, and production-quality implementation.

Your task is to faithfully implement the approved GEES architecture—not to redesign it.

