"""
Repository Traceability:
- Source Document: DI-SPRINT-00 (Identity and Authorization Setup — Recommended initial roles).
- Purpose: Stable role codes for Damage Intelligence.
"""


class Role:
    DI_ADMIN = "DI_Admin"
    DI_INSPECTOR = "DI_Inspector"
    DI_REVIEWER = "DI_Reviewer"
    DI_OPERATIONS = "DI_Operations"
    DI_AUDITOR = "DI_Auditor"
    DI_INTEGRATION_SERVICE = "DI_IntegrationService"


ALL_ROLES = [
    Role.DI_ADMIN,
    Role.DI_INSPECTOR,
    Role.DI_REVIEWER,
    Role.DI_OPERATIONS,
    Role.DI_AUDITOR,
    Role.DI_INTEGRATION_SERVICE,
]
