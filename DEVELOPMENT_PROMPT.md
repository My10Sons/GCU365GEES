# GEES Enterprise Development Prompt

**Last Updated:** 2026-06-27  
**Project:** GCU365 GEES (Global Enterprise Engineering System)  
**Version:** 1.0.0

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Development Principles](#development-principles)
3. [Architecture & System Design](#architecture--system-design)
4. [Coding Standards](#coding-standards)
5. [Workflow & Git Practices](#workflow--git-practices)
6. [Quality Assurance](#quality-assurance)
7. [Documentation Requirements](#documentation-requirements)
8. [AI/LLM Consumption Rules](#aillm-consumption-rules)
9. [Security & Compliance](#security--compliance)
10. [Collaboration Guidelines](#collaboration-guidelines)

---

## Project Overview

### Vision
The GEES Enterprise Starter is a foundational platform providing:
- **Governance Framework:** Enterprise-grade policies, procedures, and compliance mechanisms
- **Architecture Foundation:** Reference architecture for distributed, scalable systems
- **Platform Services:** Modular, reusable enterprise components
- **Knowledge Management:** Comprehensive domain knowledge and ontology
- **DevOps Infrastructure:** Automated build, test, deploy pipelines

### Key Domains
- **Platform (GEES-0001):** Executive vision and strategic direction
- **Architecture:** Reference models, design patterns, system integration
- **AI & Machine Learning:** ML services, model governance, data pipeline
- **API Management:** RESTful services, integration points, API versioning
- **Database:** Data models, schema design, performance optimization
- **Security:** Authentication, authorization, encryption, compliance
- **DevOps:** CI/CD, infrastructure, monitoring, disaster recovery
- **QA & Testing:** Test strategy, automation, performance testing
- **UX & Frontend:** User experience design, accessibility, responsive design
- **Mobile:** Cross-platform mobile applications
- **Web:** Web applications and portals

---

## Development Principles

### 1. Enterprise-First Mindset
- Design for scalability, reliability, and maintainability
- Consider regulatory compliance from the start
- Plan for geographic distribution and disaster recovery
- Document all critical decisions

### 2. Framework Adherence
- Follow the GEES Constitution (GEES-0000) for all structural decisions
- Reference the Normative documents for domain-specific guidelines
- Use standardized naming conventions and identification schemes
- Maintain bidirectional traceability between requirements and implementations

### 3. Quality Over Speed
- Code reviews are mandatory for all changes
- Test coverage must exceed 80% for critical paths
- Performance benchmarks must be established and monitored
- Security reviews required for all authentication/authorization changes

### 4. Documentation-Driven Development
- Write documentation before or concurrent with code
- Keep architecture diagrams synchronized with implementation
- Maintain ADR (Architecture Decision Records) for significant choices
- Update glossary as new terms are introduced

### 5. Collaborative Excellence
- Communicate early and often about design decisions
- Share knowledge through internal wikis and knowledge graphs
- Participate in architecture reviews and design discussions
- Support cross-functional teams in integrating your components

---

## Architecture & System Design

### Reference Architecture Layers

```
┌─────────────────────────────────────────────┐
│         User Experience (UI/UX)             │
├─────────────────────────────────────────────┤
│   Presentation Layer (Web, Mobile, API)     │
├─────────────────────────────────────────────┤
│      Business Logic & Service Layer         │
├─────────────────────────────────────────────┤
│    Data Access & Integration Layer          │
├─────────────────────────────────────────────┤
│   Infrastructure & Platform Services        │
├─────────────────────────────────────────────┤
│    DevOps, Security, Monitoring, Compliance │
└─────────────────────────────────────────────┘
```

### Design Principles
- **Microservices:** Services should be independently deployable and testable
- **API-First:** Expose functionality through well-defined APIs
- **Stateless:** Minimize state management at service level
- **Eventual Consistency:** Plan for distributed transaction handling
- **Resilience:** Implement circuit breakers, timeouts, and retry logic
- **Observability:** Comprehensive logging, metrics, and tracing

### Technology Guidance
- **Languages:** TypeScript (preferred), Python, Go, Java based on domain needs
- **Frameworks:** React (Web), React Native (Mobile), Express/FastAPI (APIs)
- **Databases:** PostgreSQL (relational), MongoDB (document), Redis (cache)
- **Message Queues:** RabbitMQ or Kafka for async communication
- **Container Orchestration:** Kubernetes or Docker Compose for development
- **Service Mesh:** Consider Istio for advanced traffic management

---

## Coding Standards

### General Guidelines

#### Naming Conventions
- **Variables & Functions:** `camelCase`
- **Classes & Types:** `PascalCase`
- **Constants:** `UPPER_SNAKE_CASE`
- **Files & Folders:** `kebab-case` (except TypeScript/JavaScript which use `PascalCase` for exported classes)
- **Database Tables:** `snake_case`
- **Database Columns:** `snake_case`

#### Code Organization
- Max line length: 100 characters (120 for exceptional cases)
- Files should be focused (single responsibility principle)
- Organize imports: external → internal modules → relative imports
- Use meaningful variable names; avoid single-letter variables except in loops

#### Comments & Documentation
- Every public function/class must have JSDoc/docstring comments
- Complex logic requires inline comments explaining the "why"
- TODO comments must include ticket/issue reference
- Update comments when changing code behavior

### Language-Specific Standards

#### TypeScript
```typescript
// Strict mode required: strict: true in tsconfig.json
// No any types unless absolutely necessary with explanation

// Good practices
interface User {
  id: string;
  email: string;
  createdAt: Date;
}

async function getUser(id: string): Promise<User> {
  // Implementation
}

// Avoid
function getUser(id): any {
  // Implementation
}
```

#### Python
```python
# PEP 8 compliance
# Type hints for all function signatures
# Docstring format: Google style

from typing import Optional, List

def process_data(items: List[str]) -> Optional[str]:
    """Process a list of items.
    
    Args:
        items: List of item strings to process.
    
    Returns:
        Processed result or None if empty.
    """
    pass
```

---

## Workflow & Git Practices

### Branch Strategy (Git Flow)
```
main              (production-ready releases, tagged)
  ├─ develop      (integration branch for features)
  ├─ feature/*    (feature branches from develop)
  ├─ bugfix/*     (bug fixes from develop)
  ├─ hotfix/*     (critical production fixes from main)
  └─ release/*    (release preparation from develop)
```

### Commit Message Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style (formatting, missing semicolons, etc.)
- `refactor:` Code refactoring without behavior change
- `perf:` Performance improvements
- `test:` Test additions/modifications
- `chore:` Build process, dependencies, tooling

**Example:**
```
feat(auth): implement OAuth2 integration for SSO

- Add OAuth2 provider configuration
- Implement token refresh mechanism
- Add unit and integration tests

Closes #1234
```

### Pull Request Process
1. Create feature branch from `develop`
2. Implement changes with tests
3. Ensure CI passes (linting, tests, coverage)
4. Request code review (minimum 2 approvals for main components)
5. Address review feedback
6. Squash commits if needed before merge
7. Delete feature branch after merge

### Commit Frequency
- Commit frequently (every logical unit of work)
- Keep commits atomic and self-contained
- Never commit broken code or failing tests
- Include related tests with feature commits

---

## Quality Assurance

### Testing Requirements

#### Test Coverage Goals
- **Unit Tests:** 80%+ coverage for business logic
- **Integration Tests:** 60%+ coverage for API layers
- **End-to-End Tests:** Critical user workflows
- **Performance Tests:** Load testing for APIs and databases

#### Test Structure
```
src/
  ├─ features/
  │  ├─ user/
  │  │  ├─ user.service.ts
  │  │  ├─ user.controller.ts
  │  │  ├─ __tests__/
  │  │  │  ├─ user.service.test.ts
  │  │  │  ├─ user.controller.test.ts
  │  │  │  └─ user.integration.test.ts
```

#### Writing Tests
```typescript
describe('UserService', () => {
  let service: UserService;
  
  beforeEach(() => {
    service = new UserService();
  });
  
  describe('getUser', () => {
    it('should return user when found', async () => {
      // Arrange
      const userId = '123';
      
      // Act
      const result = await service.getUser(userId);
      
      // Assert
      expect(result).toBeDefined();
      expect(result.id).toBe(userId);
    });
    
    it('should throw NotFoundException when user not found', async () => {
      // Arrange, Act, Assert
      await expect(service.getUser('nonexistent'))
        .rejects
        .toThrow(NotFoundException);
    });
  });
});
```

### Code Review Checklist
- [ ] Code follows naming conventions and style guidelines
- [ ] Tests cover new functionality (>80% coverage)
- [ ] All tests pass locally and in CI
- [ ] No hardcoded secrets or credentials
- [ ] Documentation updated or added
- [ ] No unnecessary dependencies added
- [ ] Performance impact considered
- [ ] Security implications reviewed
- [ ] Breaking changes documented

### Performance Standards
- API response time: <200ms (p95) for standard queries
- Database query time: <100ms for indexed operations
- Webpage load time: <3s (fully interactive)
- Mobile app startup: <2s
- Memory usage within defined limits per service

---

## Documentation Requirements

### Mandatory Documentation

#### For Every Feature/Component
1. **README:** Purpose, usage examples, configuration
2. **Architecture Diagram:** System context and interactions
3. **API Documentation:** Endpoints, parameters, responses, error codes
4. **Database Schema:** Tables, relationships, constraints (if applicable)
5. **Deployment Guide:** Prerequisites, installation, configuration
6. **Troubleshooting Guide:** Common issues and solutions

#### Documentation Standards
- Use clear, active voice
- Include code examples for complex features
- Maintain a glossary for domain-specific terms
- Version documentation alongside code changes
- Update README when changing public APIs

### File Naming Convention
```
docs/
  └─ 01-Normative/
      ├─ Architecture/
      │  └─ GEES-XXXX-Component-Name.md
      ├─ API/
      │  └─ GEES-XXXX-API-Specification.md
      ├─ Database/
      │  └─ GEES-XXXX-Data-Model.md
      └─ Development/
         └─ GEES-XXXX-Development-Guidelines.md
```

---

## AI/LLM Consumption Rules

### Guidance for AI Systems (including GitHub Copilot)

#### Allowed Uses
- ✅ Code completion for boilerplate and repetitive patterns
- ✅ Test generation from existing code
- ✅ Documentation generation from code
- ✅ Refactoring suggestions for code simplification
- ✅ Security and performance improvement suggestions
- ✅ Bug detection and fix recommendations

#### Restricted Uses
- ❌ Security-critical authentication/encryption code (review carefully)
- ❌ Financial calculations (must be human-reviewed)
- ❌ Data deletion/destruction operations (must be human-reviewed)
- ❌ Configuration that affects production systems
- ❌ Generation of regulatory compliance code without legal review

#### AI-Generated Code Review Process
1. Run through existing test suite
2. Perform manual code review focusing on:
   - Correct business logic
   - Edge case handling
   - Security implications
   - Performance impact
3. Add/modify tests to cover AI-generated code
4. Get peer review approval before merge

#### Disclosing AI Usage
- Document if AI tools were used to generate significant portions
- Use commit message prefix: `ai:` or `ai-assisted:` for transparency
- Note in PR description which AI tools were used

---

## Security & Compliance

### Security Requirements

#### Authentication & Authorization
- All APIs must authenticate requests (OAuth2, JWT, API keys)
- Role-based access control (RBAC) for all resources
- Multi-factor authentication (MFA) for administrative access
- Session timeouts: 30 minutes for web, 24 hours for mobile

#### Data Protection
- Encrypt sensitive data at rest (AES-256)
- Encrypt data in transit (TLS 1.2+)
- Never log passwords, tokens, or PII
- Implement data retention and purging policies
- GDPR compliance: Right to be forgotten, data portability

#### Code Security
- No hardcoded secrets; use environment variables
- Dependency scanning: check for known vulnerabilities
- SAST (Static Application Security Testing) in CI pipeline
- Regular security audits of critical components
- SQL injection prevention: use parameterized queries
- XSS prevention: input validation and output encoding

#### Compliance
- Log all security-relevant events (authentication, authorization, data access)
- Maintain audit trails for sensitive operations
- Regular security training for development team
- Incident response plan documented and tested

---

## Collaboration Guidelines

### Communication Standards
- **Asynchronous First:** Document decisions in tickets/wikis
- **Synchronous Meetings:** For design decisions, urgent issues only
- **Code Review:** 24-hour response time for PRs
- **Issue Reporting:** Clear title, detailed description, reproduction steps

### Knowledge Sharing
- Participate in architecture review sessions
- Document lessons learned after significant work
- Share library/utility code across teams
- Mentor junior developers on project standards

### Definition of Done (DoD)
A feature is complete when:
- [ ] Code written and self-reviewed
- [ ] Unit tests passing (80%+ coverage)
- [ ] Integration tests passing
- [ ] Code review approved (2 reviewers)
- [ ] Documentation updated
- [ ] No new security vulnerabilities
- [ ] Performance impact assessed
- [ ] Merged to develop branch

---

## Tooling & Environment Setup

### Required Tools
- **Version Control:** Git 2.30+
- **Language Runtime:** Node.js 18+, Python 3.9+
- **Package Managers:** npm, pip, Maven (as needed)
- **Container:** Docker 20.10+
- **IDE:** VS Code with recommended extensions
- **Linting:** ESLint, Prettier, Black
- **Testing:** Jest, Pytest, Postman
- **CI/CD:** GitHub Actions or Jenkins

### Development Environment
```bash
# Clone repository
git clone https://github.com/gcu365/GEES_Enterprise_Starter_v2.git
cd GEES_Enterprise_Starter_v2

# Install dependencies
npm install
# or
pip install -r requirements.txt

# Setup git hooks
npm run setup:hooks

# Run tests
npm run test

# Start development server
npm run dev
```

### IDE Configuration
- EditorConfig settings included in repository
- Prettier configuration enforced
- ESLint/Pylint configuration included
- VS Code extensions recommended in `.vscode/extensions.json`

---

## Escalation & Support

### Issue Resolution Path
1. **Local Debugging:** Reproduce locally, check logs
2. **Team Discussion:** Discuss in Slack/Teams channel
3. **Architecture Review:** For design-level issues
4. **Leadership Escalation:** For blocking production issues

### Getting Help
- **Questions:** Ask in team Slack channel with context
- **Blocked:** Create blocker issue with details
- **Urgent:** Page on-call engineer for production issues

---

## References

- [GEES Constitution](docs/00-Constitution/GEES-0000-Constitution.md)
- [Executive Vision](docs/02-Enterprise-Foundation/GEES-0001-Executive-Vision.md)
- [Architecture Reference](docs/03-Reference-Architecture/)
- [Security Guidelines](docs/14-Security/)
- [API Standards](docs/12-API/)
- [Database Standards](docs/13-Database/)

---

**Next Steps:**
1. Review this document thoroughly
2. Bookmark relevant sections for your domain
3. Provide feedback on development prompt clarity
4. Reference this in code review comments
5. Update as project evolves

---

*This development prompt is a living document. Feedback and updates are welcome through the standard PR process.*
