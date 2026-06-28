"""
Repository Traceability:
- Source Documents: DI-SPRINT-01 (Inspection types implied), DI-0004 (Inspection Workflow),
  DI-0011 (Inspection types).
- Purpose: Stable inspection-type and source-system codes.
"""


class InspectionType:
    CHECK_OUT = "CHECK_OUT"            # CROMS rental check-out inspection
    CHECK_IN = "CHECK_IN"              # CROMS rental check-in inspection
    MAINTENANCE_INTAKE = "MAINTENANCE_INTAKE"  # GCU365Maintenance work-order intake
    MAINTENANCE_HANDBACK = "MAINTENANCE_HANDBACK"  # GCU365Maintenance work-order handback
    SPOT_CHECK = "SPOT_CHECK"          # Ad-hoc fleet spot check


ALL_INSPECTION_TYPES = [
    InspectionType.CHECK_OUT,
    InspectionType.CHECK_IN,
    InspectionType.MAINTENANCE_INTAKE,
    InspectionType.MAINTENANCE_HANDBACK,
    InspectionType.SPOT_CHECK,
]


class SourceSystem:
    CROMS = "GCU365-CROMS"
    MAINTENANCE = "GCU365Maintenance"
    DI_WEB = "DI-Web"
    DI_MOBILE = "DI-Mobile"


ALL_SOURCE_SYSTEMS = [
    SourceSystem.CROMS,
    SourceSystem.MAINTENANCE,
    SourceSystem.DI_WEB,
    SourceSystem.DI_MOBILE,
]


class InspectionImageStatus:
    PENDING = "PENDING"            # upload requested, not yet registered
    REGISTERED = "REGISTERED"      # registered as evidence
    REJECTED = "REJECTED"          # registration rejected (validation, future quality fail)
