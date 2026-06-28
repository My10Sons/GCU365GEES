"""
Repository Traceability:
- Source Documents: DI-SPRINT-00 (Object Storage Setup — path convention, no public
  unrestricted access, time-limited links).
- Purpose: Storage provider interface (production object store wired in Sprint-05
  hardening per DECISION-001).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class UploadInstruction:
    upload_url: str
    method: str
    expires_at_iso: str


class StorageProvider(ABC):
    @abstractmethod
    def evidence_path(self, tenant_id: str, inspection_session_id: str, image_id: str) -> str:
        ...

    @abstractmethod
    async def make_upload_instruction(self, object_path: str, expires_in_seconds: int) -> UploadInstruction:
        ...

    @abstractmethod
    async def make_access_link(self, object_path: str, expires_in_seconds: int) -> tuple[str, str]:
        """Returns (url, expires_at_iso)."""
        ...

    @abstractmethod
    async def object_exists(self, object_path: str) -> bool:
        ...
