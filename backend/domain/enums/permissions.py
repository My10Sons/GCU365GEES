"""
Repository Traceability:
- Source Document: DI-0034 (Authentication and Authorization — Recommended permissions table, 23 permissions).
- Purpose: Stable permission codes for Damage Intelligence authorization.
"""


class Permission:
    INSPECTIONS_CREATE = "di.inspections.create"
    INSPECTIONS_READ = "di.inspections.read"
    INSPECTIONS_SUBMIT = "di.inspections.submit"
    INSPECTIONS_CANCEL = "di.inspections.cancel"
    IMAGES_UPLOAD = "di.images.upload"
    IMAGES_READ = "di.images.read"
    EVIDENCE_ACCESS = "di.evidence.access"
    AI_REQUEST = "di.ai.request"
    AI_READ = "di.ai.read"
    COMPARISON_REQUEST = "di.comparison.request"
    COMPARISON_READ = "di.comparison.read"
    REVIEW_READ = "di.review.read"
    REVIEW_DECIDE = "di.review.decide"
    DAMAGECASES_CREATE = "di.damagecases.create"
    DAMAGECASES_READ = "di.damagecases.read"
    DAMAGECASES_UPDATE = "di.damagecases.update"
    INTEGRATIONS_CROMS = "di.integrations.croms"
    INTEGRATIONS_MAINTENANCE = "di.integrations.maintenance"
    REPORTS_GENERATE = "di.reports.generate"
    REPORTS_READ = "di.reports.read"
    REPORTS_ACCESS = "di.reports.access"
    AUDIT_READ = "di.audit.read"
    CONFIGURATION_MANAGE = "di.configuration.manage"


ALL_PERMISSIONS = [
    Permission.INSPECTIONS_CREATE, Permission.INSPECTIONS_READ,
    Permission.INSPECTIONS_SUBMIT, Permission.INSPECTIONS_CANCEL,
    Permission.IMAGES_UPLOAD, Permission.IMAGES_READ, Permission.EVIDENCE_ACCESS,
    Permission.AI_REQUEST, Permission.AI_READ,
    Permission.COMPARISON_REQUEST, Permission.COMPARISON_READ,
    Permission.REVIEW_READ, Permission.REVIEW_DECIDE,
    Permission.DAMAGECASES_CREATE, Permission.DAMAGECASES_READ, Permission.DAMAGECASES_UPDATE,
    Permission.INTEGRATIONS_CROMS, Permission.INTEGRATIONS_MAINTENANCE,
    Permission.REPORTS_GENERATE, Permission.REPORTS_READ, Permission.REPORTS_ACCESS,
    Permission.AUDIT_READ, Permission.CONFIGURATION_MANAGE,
]
