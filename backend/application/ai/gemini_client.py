"""
Repository Traceability:
- Source Documents: DI-SPRINT-02 (Gemini multimodal vision integration), DI-0014
  (security — never log raw images), DI-0034 (modelVersion traceability).
- Purpose: Thin wrapper around emergentintegrations LlmChat to perform
  image-in / structured-JSON-text-out calls. Returns (parsed_json, model_label, latency_ms).
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import time
import uuid
from pathlib import Path
from typing import Any

from emergentintegrations.llm.chat import (  # type: ignore
    FileContentWithMimeType,
    LlmChat,
    UserMessage,
)

from infrastructure.observability.logging import get_logger, log_event

logger = get_logger("di.ai.gemini")


def _emergent_key() -> str:
    return os.environ["EMERGENT_LLM_KEY"]


def _timeout_seconds() -> float:
    return float(os.environ.get("DI_AI_TIMEOUT_SECONDS", "60"))


def _max_retries() -> int:
    return int(os.environ.get("DI_AI_MAX_RETRIES", "1"))


def _extract_json_block(text: str) -> dict | None:
    if not text:
        return None
    text = text.strip()
    # Fast path: pure JSON
    try:
        return json.loads(text)
    except Exception:
        pass
    # Strip ```json ... ``` fenced block if present
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    # Heuristic last-resort: largest balanced { ... }
    m = re.search(r"\{[\s\S]*\}", text)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            pass
    return None


async def call_vision_model(
    *,
    provider: str,
    model_name: str,
    system_message: str,
    user_prompt: str,
    image_path: str,
    mime_type: str,
    correlation_id: str,
) -> tuple[dict | None, str, int, str | None]:
    """
    Returns (parsed_json_or_None, model_label, latency_ms, error_message_or_None).
    Never logs image bytes. Logs only sizes and timing.
    """
    if not Path(image_path).exists():
        return None, f"{provider}:{model_name}", 0, "image_missing"

    last_error: str | None = None
    started = time.perf_counter()
    retries = _max_retries()
    for attempt in range(retries + 1):
        chat = LlmChat(
            api_key=_emergent_key(),
            session_id=f"di-{uuid.uuid4().hex}",
            system_message=system_message,
        ).with_model(provider, model_name)
        msg = UserMessage(
            text=user_prompt,
            file_contents=[
                FileContentWithMimeType(file_path=image_path, mime_type=mime_type)
            ],
        )
        try:
            text = await asyncio.wait_for(chat.send_message(msg), timeout=_timeout_seconds())
            latency_ms = int((time.perf_counter() - started) * 1000)
            parsed = _extract_json_block(text or "")
            log_event(
                logger,
                20,
                "AI call done",
                provider=provider,
                model=model_name,
                latencyMs=latency_ms,
                parsedOk=parsed is not None,
                attempt=attempt,
                correlationId=correlation_id,
            )
            if parsed is None:
                last_error = "non_json_output"
                if attempt < retries:
                    continue
                return None, f"{provider}:{model_name}", latency_ms, last_error
            return parsed, f"{provider}:{model_name}", latency_ms, None
        except asyncio.TimeoutError:
            last_error = "timeout"
            log_event(logger, 30, "AI call timeout", provider=provider, model=model_name, attempt=attempt, correlationId=correlation_id)
            if attempt < retries:
                await asyncio.sleep(1.5 * (attempt + 1))
                continue
            latency_ms = int((time.perf_counter() - started) * 1000)
            return None, f"{provider}:{model_name}", latency_ms, last_error
        except Exception as exc:  # noqa: BLE001
            last_error = type(exc).__name__
            log_event(
                logger, 40, "AI call failed",
                provider=provider, model=model_name, error=last_error, attempt=attempt, correlationId=correlation_id,
            )
            if attempt < retries:
                await asyncio.sleep(1.5 * (attempt + 1))
                continue
            latency_ms = int((time.perf_counter() - started) * 1000)
            return None, f"{provider}:{model_name}", latency_ms, last_error

    latency_ms = int((time.perf_counter() - started) * 1000)
    return None, f"{provider}:{model_name}", latency_ms, last_error


async def call_vision_model_multi(
    *,
    provider: str,
    model_name: str,
    system_message: str,
    user_prompt: str,
    images: list[dict],
    correlation_id: str,
) -> tuple[dict | None, str, int, str | None]:
    """
    Multi-image variant used by the Sprint 03 comparison engine.
    `images` is a list of {"path": str, "mime": str}. Order is significant — the
    prompt should reference image positions (e.g. baseline first, current second).
    Never logs image bytes. Returns (parsed_json_or_None, model_label, latency_ms, error).
    """
    file_contents = []
    for img in images:
        path = img.get("path")
        if not path or not Path(path).exists():
            return None, f"{provider}:{model_name}", 0, "image_missing"
        file_contents.append(
            FileContentWithMimeType(file_path=path, mime_type=img.get("mime") or "image/jpeg")
        )

    last_error: str | None = None
    started = time.perf_counter()
    retries = _max_retries()
    for attempt in range(retries + 1):
        chat = LlmChat(
            api_key=_emergent_key(),
            session_id=f"di-cmp-{uuid.uuid4().hex}",
            system_message=system_message,
        ).with_model(provider, model_name)
        msg = UserMessage(text=user_prompt, file_contents=file_contents)
        try:
            text = await asyncio.wait_for(chat.send_message(msg), timeout=_timeout_seconds())
            latency_ms = int((time.perf_counter() - started) * 1000)
            parsed = _extract_json_block(text or "")
            log_event(
                logger, 20, "AI compare call done",
                provider=provider, model=model_name, latencyMs=latency_ms,
                parsedOk=parsed is not None, images=len(file_contents),
                attempt=attempt, correlationId=correlation_id,
            )
            if parsed is None:
                last_error = "non_json_output"
                if attempt < retries:
                    continue
                return None, f"{provider}:{model_name}", latency_ms, last_error
            return parsed, f"{provider}:{model_name}", latency_ms, None
        except asyncio.TimeoutError:
            last_error = "timeout"
            log_event(logger, 30, "AI compare timeout", provider=provider, model=model_name, attempt=attempt, correlationId=correlation_id)
            if attempt < retries:
                await asyncio.sleep(1.5 * (attempt + 1))
                continue
            latency_ms = int((time.perf_counter() - started) * 1000)
            return None, f"{provider}:{model_name}", latency_ms, last_error
        except Exception as exc:  # noqa: BLE001
            last_error = type(exc).__name__
            log_event(logger, 40, "AI compare failed", provider=provider, model=model_name, error=last_error, attempt=attempt, correlationId=correlation_id)
            if attempt < retries:
                await asyncio.sleep(1.5 * (attempt + 1))
                continue
            latency_ms = int((time.perf_counter() - started) * 1000)
            return None, f"{provider}:{model_name}", latency_ms, last_error

    latency_ms = int((time.perf_counter() - started) * 1000)
    return None, f"{provider}:{model_name}", latency_ms, last_error
