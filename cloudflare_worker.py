"""Cloudflare Python Worker entrypoint for Asfandyar AI Studio."""
from workers import asgi

from cloudflare_app import app

# Official Python Workers ASGI adapter for FastAPI.
Default = asgi.entrypoint(app)
