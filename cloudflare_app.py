"""Minimal Cloudflare-only FastAPI app.

Do not import main.py here: its existing managers initialize local SQLite and
some in-memory stores at import time. This shell is intentionally isolated
until each manager has been migrated to a durable repository.
"""
from fastapi import FastAPI, HTTPException, Request

from cloudflare_d1 import D1Store

app = FastAPI(
    title="Asfandyar AI Studio - Cloudflare",
    version="0.1.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)


@app.get("/")
async def root():
    return {
        "project": "Asfandyar AI Studio",
        "runtime": "cloudflare-python-worker",
        "status": "worker-shell",
        "note": "Full dashboard migration is still in progress.",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/health/storage")
async def storage_health(request: Request):
    """Check D1 connectivity without returning table names or stored data."""
    try:
        store = D1Store.from_request(request)
        result = await store.one("SELECT 1 AS ok")
        if not result or int(result.get("ok", 0)) != 1:
            raise RuntimeError("D1 health query returned an unexpected result.")
        return {"status": "healthy", "storage": "connected"}
    except Exception:
        # Do not leak binding names, SQL, credentials, or internal errors.
        raise HTTPException(status_code=503, detail="Durable storage is unavailable.")
