"""
Repository Traceability:
- Source Documents: DI-SPRINT-00 (Object Storage Setup — local development storage,
  tenant-isolated path convention, no public unrestricted access),
  DECISION-001 (local-disk abstraction; production object store deferred to Sprint 05).
- Purpose: Local-disk storage provider with signed (HMAC) tokens for time-limited access.
"""
from __future__ import annotations

import hmac
import hashlib
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

from infrastructure.storage.storage_provider import StorageProvider, UploadInstruction


def _root() -> Path:
    root = Path(os.environ.get("DI_LOCAL_STORAGE_ROOT", "/var/lib/damage-intelligence/storage"))
    root.mkdir(parents=True, exist_ok=True)
    return root


def _sign(object_path: str, expires_at_epoch: int) -> str:
    secret = os.environ["JWT_SECRET"].encode("utf-8")
    msg = f"{object_path}|{expires_at_epoch}".encode("utf-8")
    return hmac.new(secret, msg, hashlib.sha256).hexdigest()


class LocalStorageProvider(StorageProvider):
    def evidence_path(self, tenant_id: str, inspection_session_id: str, image_id: str) -> str:
        return f"tenants/{tenant_id}/damage-intelligence/inspections/{inspection_session_id}/images/{image_id}"

    async def make_upload_instruction(self, object_path: str, expires_in_seconds: int) -> UploadInstruction:
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in_seconds)
        epoch = int(expires_at.timestamp())
        token = _sign(object_path, epoch)
        return UploadInstruction(
            upload_url=f"/api/v1/damage-intelligence/internal/storage/upload?path={object_path}&exp={epoch}&sig={token}",
            method="PUT",
            expires_at_iso=expires_at.isoformat(),
        )

    async def make_access_link(self, object_path: str, expires_in_seconds: int) -> tuple[str, str]:
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in_seconds)
        epoch = int(expires_at.timestamp())
        token = _sign(object_path, epoch)
        url = f"/api/v1/damage-intelligence/internal/storage/access?path={object_path}&exp={epoch}&sig={token}"
        return url, expires_at.isoformat()

    async def object_exists(self, object_path: str) -> bool:
        return (_root() / object_path).exists()


_provider: StorageProvider | None = None


def get_storage_provider() -> StorageProvider:
    global _provider
    if _provider is None:
        _provider = LocalStorageProvider()
    return _provider
