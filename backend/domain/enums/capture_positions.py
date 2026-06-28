"""
Repository Traceability:
- Source Document: DI-SPRINT-01 (Capture Positions).
- Purpose: Stable, language-neutral capture-position codes seeded into di_capture_positions.
"""

CAPTURE_POSITIONS: list[dict] = [
    {"code": "CAPTURE_FRONT", "label": "Front vehicle view", "group": "EXTERIOR", "order": 10, "required": True},
    {"code": "CAPTURE_REAR", "label": "Rear vehicle view", "group": "EXTERIOR", "order": 20, "required": True},
    {"code": "CAPTURE_LEFT", "label": "Left vehicle side", "group": "EXTERIOR", "order": 30, "required": True},
    {"code": "CAPTURE_RIGHT", "label": "Right vehicle side", "group": "EXTERIOR", "order": 40, "required": True},
    {"code": "CAPTURE_FRONT_LEFT", "label": "Front-left angle", "group": "EXTERIOR", "order": 50, "required": False},
    {"code": "CAPTURE_FRONT_RIGHT", "label": "Front-right angle", "group": "EXTERIOR", "order": 60, "required": False},
    {"code": "CAPTURE_REAR_LEFT", "label": "Rear-left angle", "group": "EXTERIOR", "order": 70, "required": False},
    {"code": "CAPTURE_REAR_RIGHT", "label": "Rear-right angle", "group": "EXTERIOR", "order": 80, "required": False},
    {"code": "CAPTURE_INTERIOR_FRONT", "label": "Interior front area", "group": "INTERIOR", "order": 110, "required": False},
    {"code": "CAPTURE_INTERIOR_REAR", "label": "Interior rear area", "group": "INTERIOR", "order": 120, "required": False},
    {"code": "CAPTURE_ODOMETER", "label": "Odometer", "group": "INDICATOR", "order": 210, "required": True},
    {"code": "CAPTURE_FUEL_OR_CHARGE", "label": "Fuel or charge indicator", "group": "INDICATOR", "order": 220, "required": True},
]

CAPTURE_POSITION_CODES = {p["code"] for p in CAPTURE_POSITIONS}
