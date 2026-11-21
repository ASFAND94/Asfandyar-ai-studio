"""Cloudflare Python Worker entrypoint for the isolated FastAPI shell.

Cloudflare's documented ASGI adapter attaches Worker bindings to the request
scope. The local Windows application continues to use main.py + Uvicorn.
"""
from workers import WorkerEntrypoint
import asgi

from cloudflare_app import app


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        return await asgi.fetch(app, request, self.env)
