---
id: GBP-0001
title: GEES Build Manifest
version: 1.0.0
document_type: Build Package
document_class: Build Manifest
status: Draft
classification: Internal
owner: Riyadah Technology
reviewers:
  - Chief Enterprise Architect
  - Chief Technology Officer
approvers: []
created: 2026-06-27
updated: 2026-06-27
authoritative: true
ai_consumable: true
---

# GEES Build Manifest

## Purpose

This document defines the authoritative implementation scope for the GEES Platform.

It identifies the approved architecture, standards, technologies, and implementation constraints that AI-assisted development tools SHALL follow.

---

# Scope

The Build Manifest applies to:

- Source code generation
- Repository creation
- API implementation
- Database implementation
- UI implementation
- Test generation
- CI/CD configuration
- Infrastructure automation

---

# Authoritative Inputs

The implementation SHALL follow these documents in order of precedence:

1. Engineering Constitution
2. Repository Architecture
3. Universal Engineering Registry Standard
4. Engineering Metamodel
5. Platform System Architecture
6. Knowledge Graph Specification
7. Enterprise Architecture documents
8. Approved Catalogs
9. Approved Requirements

No implementation SHALL contradict an approved authoritative document.

---

# Approved Technology Stack

| Layer | Standard |
|--------|----------|
| Backend | ASP.NET Core (.NET) |
| Frontend | Blazor Web App |
| AI Services | Python |
| Database | PostgreSQL |
| Knowledge Graph | Neo4j |
| Search | OpenSearch |
| Cache | Redis |
| Messaging | RabbitMQ |
| Storage | Azure Blob Storage |
| Authentication | Microsoft Entra ID / Keycloak |
| CI/CD | GitHub Actions |
| Containers | Docker |
| Orchestration | Kubernetes (when required) |

---

# Architectural Constraints

The implementation SHALL:

- Follow Domain-Driven Design.
- Use API-first principles.
- Keep bounded contexts independent.
- Use event-driven integration where appropriate.
- Preserve traceability.
- Preserve audit history.
- Support AI-assisted workflows.

---

# Deliverables

The implementation SHALL include:

- Source code
- Automated tests
- API documentation
- Database migrations
- Deployment scripts
- Infrastructure definitions
- Configuration files

---

# Quality Gates

No feature SHALL be considered complete unless it:

- Passes automated tests.
- Passes validation rules.
- Preserves traceability.
- Includes documentation updates.
- Meets security requirements.

---

# References

- PLATFORM-0003
- PLATFORM-0004
- META-0010
- META-0011

---

# Revision History

| Version | Date | Description |
|----------|------|-------------|
| 1.0.0 | 2026-06-27 | Initial Build Manifest |