"""
Repository Traceability:
- Source Documents: DI-0034 (Permissions table), DI-SPRINT-00 (Recommended initial roles).
- Purpose: Role -> permission set mapping used by the authorization layer.
"""
from typing import FrozenSet

from domain.enums.permissions import Permission as P
from domain.enums.roles import Role


ROLE_PERMISSIONS: dict[str, FrozenSet[str]] = {
    Role.DI_ADMIN: frozenset(
        [
            P.INSPECTIONS_CREATE, P.INSPECTIONS_READ, P.INSPECTIONS_SUBMIT, P.INSPECTIONS_CANCEL,
            P.IMAGES_UPLOAD, P.IMAGES_READ, P.EVIDENCE_ACCESS,
            P.AI_REQUEST, P.AI_READ,
            P.COMPARISON_REQUEST, P.COMPARISON_READ,
            P.REVIEW_READ, P.REVIEW_DECIDE,
            P.DAMAGECASES_CREATE, P.DAMAGECASES_READ, P.DAMAGECASES_UPDATE,
            P.REPORTS_GENERATE, P.REPORTS_READ, P.REPORTS_ACCESS,
            P.AUDIT_READ, P.CONFIGURATION_MANAGE,
        ]
    ),
    Role.DI_INSPECTOR: frozenset(
        [
            P.INSPECTIONS_CREATE, P.INSPECTIONS_READ, P.INSPECTIONS_SUBMIT,
            P.IMAGES_UPLOAD, P.IMAGES_READ, P.EVIDENCE_ACCESS,
            P.AI_REQUEST, P.AI_READ,
            P.COMPARISON_READ,
        ]
    ),
    Role.DI_REVIEWER: frozenset(
        [
            P.INSPECTIONS_READ, P.IMAGES_READ, P.EVIDENCE_ACCESS,
            P.AI_READ, P.COMPARISON_REQUEST, P.COMPARISON_READ,
            P.REVIEW_READ, P.REVIEW_DECIDE,
            P.DAMAGECASES_CREATE, P.DAMAGECASES_READ, P.DAMAGECASES_UPDATE,
            P.REPORTS_GENERATE, P.REPORTS_READ, P.REPORTS_ACCESS,
        ]
    ),
    Role.DI_OPERATIONS: frozenset(
        [
            P.INSPECTIONS_READ, P.IMAGES_READ, P.EVIDENCE_ACCESS,
            P.AI_READ, P.COMPARISON_READ, P.REVIEW_READ,
            P.DAMAGECASES_READ, P.REPORTS_READ, P.AUDIT_READ,
        ]
    ),
    Role.DI_AUDITOR: frozenset([P.AUDIT_READ, P.REPORTS_READ, P.DAMAGECASES_READ, P.INSPECTIONS_READ]),
    Role.DI_INTEGRATION_SERVICE: frozenset(
        [P.INTEGRATIONS_CROMS, P.INTEGRATIONS_MAINTENANCE, P.INSPECTIONS_CREATE, P.INSPECTIONS_READ]
    ),
}


def permissions_for_roles(roles: list[str]) -> set[str]:
    result: set[str] = set()
    for role in roles or []:
        result |= ROLE_PERMISSIONS.get(role, frozenset())
    return result
