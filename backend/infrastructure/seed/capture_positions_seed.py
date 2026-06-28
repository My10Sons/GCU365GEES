"""
Repository Traceability:
- Source Document: DI-SPRINT-01 (Capture Positions — seed stable codes).
- Purpose: Idempotent seed of the di_capture_positions reference collection.
"""
from datetime import datetime, timezone

from domain.enums.capture_positions import CAPTURE_POSITIONS
from infrastructure.db.mongo import get_db


async def seed_capture_positions() -> None:
    db = get_db()
    now = datetime.now(timezone.utc)
    for pos in CAPTURE_POSITIONS:
        await db.di_capture_positions.update_one(
            {"code": pos["code"]},
            {"$set": {**pos, "updatedAt": now}, "$setOnInsert": {"createdAt": now}},
            upsert=True,
        )
