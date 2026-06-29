"""
Repository Traceability:
- Source Document: DI-0014 (Security and Privacy — password hashing).
- Purpose: bcrypt password hashing helpers. Never log raw passwords.
  bcrypt is CPU-bound; the async wrappers offload it to a thread pool so it does not
  block the asyncio event loop under concurrent login load.
"""
import asyncio

import bcrypt


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


async def hash_password_async(password: str) -> str:
    return await asyncio.to_thread(hash_password, password)


async def verify_password_async(plain: str, hashed: str) -> bool:
    return await asyncio.to_thread(verify_password, plain, hashed)
