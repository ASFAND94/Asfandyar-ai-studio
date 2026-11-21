"""Cloudflare-native FastAPI backend for Asfandyar AI Studio.

All user data is stored in D1. This module intentionally does not import the
local SQLite-backed main.py. Provider publishing and OAuth are not enabled.
"""
import hashlib
import hmac
import json
import re
import secrets
from datetime import datetime, timedelta, timezone
from typing import Literal, Optional

from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from cloudflare_d1 import D1Store
from cloudflare_social_repository import D1SocialAccountRepository
from cloudflare_marketing_repository import (
    D1AnalyticsRepository, D1CampaignRepository, D1ContentRepository,
)
from keyword_manager import KeywordManager
from seo_manager import SEOManager

SESSION_COOKIE = "asfandyar_admin_session"
SESSION_HOURS = 8
PBKDF2_ITERATIONS = 310_000
MAX_LOGIN_FAILURES = 5
LOCKOUT_MINUTES = 15
SUPPORTED_PLATFORMS = {
    "facebook_profile", "facebook_page", "instagram", "x", "youtube",
    "linkedin", "tiktok", "pinterest",
}

app = FastAPI(
    title="Asfandyar AI Studio",
    description="Private owner-controlled digital marketing workspace",
    version="2.0.0",
    docs_url=None, redoc_url=None, openapi_url=None,
)
seo = SEOManager()
keywords = KeywordManager()


def utc_now():
    return datetime.now(timezone.utc)


def utc_text(value):
    return value.isoformat()


def token_digest(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def make_password_hash(password):
    salt = secrets.token_bytes(16)
    derived = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS
    )
    return salt.hex() + "$" + derived.hex()


def verify_password(password, stored_hash):
    try:
        salt_hex, expected_hex = stored_hash.split("$", 1)
        actual = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), bytes.fromhex(salt_hex),
            PBKDF2_ITERATIONS,
        ).hex()
        return hmac.compare_digest(actual, expected_hex)
    except (ValueError, TypeError):
        return False


def store(request):
    return D1Store.from_request(request)


def repos(request):
    db = store(request)
    return (
        D1SocialAccountRepository(db),
        D1ContentRepository(db),
        D1CampaignRepository(db),
        D1AnalyticsRepository(db),
    )


async def get_session(request):
    raw = request.cookies.get(SESSION_COOKIE)
    if not raw:
        return None
    row = await store(request).one(
        "SELECT token_hash, csrf_hash, expires_at FROM admin_sessions WHERE token_hash = ?",
        token_digest(raw),
    )
    if not row:
        return None
    try:
        if datetime.fromisoformat(row["expires_at"]) <= utc_now():
            await store(request).execute(
                "DELETE FROM admin_sessions WHERE token_hash = ?", row["token_hash"]
            )
            return None
    except (ValueError, TypeError, KeyError):
        return None
    return row


@app.middleware("http")
async def owner_security(request: Request, call_next):
    path = request.url.path
    public = {
        "/health", "/health/storage", "/auth/status",
        "/auth/setup", "/auth/login",
    }
    public_asset = path == "/app" or path.startswith("/app/")
    if path not in public and not public_asset:
        try:
            session = await get_session(request)
        except Exception:
            return JSONResponse(status_code=503, content={"detail": "Secure storage is unavailable."})
        if not session:
            return JSONResponse(status_code=401, content={"detail": "Login required."})
        request.state.owner_session = session
        if request.method not in {"GET", "HEAD", "OPTIONS"}:
            csrf = request.headers.get("X-CSRF-Token", "")
            if not csrf or not hmac.compare_digest(
                session["csrf_hash"], token_digest(csrf)
            ):
                return JSONResponse(status_code=403, content={"detail": "CSRF validation failed."})
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; style-src 'self'; "
        "img-src 'self' data:; connect-src 'self'; object-src 'none'; "
        "base-uri 'self'; frame-ancestors 'none'"
    )
    if request.url.scheme == "https":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


class SetupRequest(BaseModel):
    setup_key: str = Field(min_length=20, max_length=256)
    username: str = Field(min_length=3, max_length=80)
    password: str = Field(min_length=12, max_length=256)


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    password: str = Field(min_length=1, max_length=256)


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=256)
    new_password: str = Field(min_length=12, max_length=256)


class SocialAccountRequest(BaseModel):
    platform: str = Field(min_length=1, max_length=30)
    account_name: str = Field(min_length=1, max_length=120)
    account_handle: str = Field(min_length=1, max_length=160)


class PreferencesRequest(BaseModel):
    niche: Optional[str] = Field(default=None, max_length=160)
    content_formats: Optional[list[Literal["post", "video", "reel", "story", "short", "article"]]] = None
    publishing_enabled: Optional[bool] = None
    require_approval: Optional[bool] = None


class ControlsRequest(BaseModel):
    global_publishing_enabled: Optional[bool] = None
    require_approval: Optional[bool] = None


class ContentRequest(BaseModel):
    title: str = Field(min_length=3, max_length=180)
    body: str = Field(min_length=10, max_length=50000)
    platform: Literal["blogger", "facebook", "x", "pinterest"] = "blogger"


class SEORequest(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    content: str = Field(min_length=1, max_length=50000)
    keyword: str = Field(min_length=1, max_length=120)


class KeywordRequest(BaseModel):
    text: str = Field(min_length=1, max_length=50000)
    main_keyword: str = Field(min_length=1, max_length=120)


class CampaignRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    platform: Literal["facebook", "x", "blogger", "pinterest"]
    website_url: str = Field(min_length=8, max_length=2048)


class AnalyticsRequest(BaseModel):
    platform: str = Field(min_length=1, max_length=40)
    visitors: int = Field(default=0, ge=0)
    pageviews: int = Field(default=0, ge=0)
    impressions: int = Field(default=0, ge=0)
    clicks: int = Field(default=0, ge=0)
    earnings: float = Field(default=0.0, ge=0)


@app.get("/")
async def root():
    return {"project": "Asfandyar AI Studio", "status": "running", "version": app.version,
            "dashboard": "/app/"}


@app.get("/health")
async def health():
    return {"status": "healthy", "time": utc_text(utc_now())}


@app.get("/health/storage")
async def storage_health(request: Request):
    try:
        row = await store(request).one("SELECT 1 AS ok")
        if not row or int(row.get("ok", 0)) != 1:
            raise RuntimeError("D1 health query failed")
        return {"status": "healthy", "storage": "connected"}
    except Exception:
        raise HTTPException(status_code=503, detail="Durable storage is unavailable.")


@app.get("/features")
async def features():
    return {"features": [
        "Private single-owner login, PBKDF2 password hashing, hashed sessions and CSRF checks",
        "Ten account slots per supported social platform",
        "Persistent content drafts, campaign plans and manual analytics in D1",
        "SEO and keyword analysis",
        "Owner publishing switch OFF by default and approval required",
        "Blogger, Adsterra and Monetag link settings are planned; live APIs are not connected",
        "Social OAuth and external publishing are not enabled",
    ]}


@app.get("/auth/status")
async def auth_status(request: Request):
    row = await store(request).one("SELECT 1 AS configured FROM admin_user WHERE id = 1")
    return {"setup_required": not bool(row), "login_required": True}


@app.post("/auth/setup", status_code=201)
async def setup_admin(data: SetupRequest, request: Request):
    env = request.scope.get("env")
    expected = getattr(env, "ADMIN_SETUP_KEY", None) if env else None
    if not expected or not hmac.compare_digest(str(expected), data.setup_key):
        raise HTTPException(status_code=403, detail="Invalid one-time setup key.")
    if not re.fullmatch(r"[A-Za-z0-9_.-]{3,80}", data.username.strip()):
        raise HTTPException(status_code=400, detail="Username must use letters, numbers, dot, underscore or hyphen.")
    db = store(request)
    if await db.one("SELECT 1 AS configured FROM admin_user WHERE id = 1"):
        raise HTTPException(status_code=409, detail="Admin account is already configured.")
    now = utc_text(utc_now())
    try:
        await db.execute(
            """INSERT INTO admin_user (id, username, password_hash, created_at, updated_at)
               VALUES (1, ?, ?, ?, ?)""",
            data.username.strip(), make_password_hash(data.password), now, now,
        )
    except Exception:
        raise HTTPException(status_code=409, detail="Owner setup could not be completed.")
    return {"success": True, "message": "Owner created. Remove the setup secret after setup."}


@app.post("/auth/login")
async def login(data: LoginRequest, request: Request, response: Response):
    db = store(request)
    client_key = request.headers.get("CF-Connecting-IP", "unknown")[:80]
    attempt = await db.one(
        "SELECT failures, locked_until FROM login_attempts WHERE client_key = ?",
        client_key,
    )
    if attempt and attempt.get("locked_until"):
        try:
            if datetime.fromisoformat(attempt["locked_until"]) > utc_now():
                raise HTTPException(status_code=429, detail="Too many failed attempts. Try again later.")
        except ValueError:
            pass
    user = await db.one("SELECT username, password_hash FROM admin_user WHERE id = 1")
    valid = bool(user and hmac.compare_digest(
        user["username"].encode(), data.username.encode()
    ) and verify_password(data.password, user["password_hash"]))
    if not valid:
        failures = int(attempt["failures"] if attempt else 0) + 1
        locked = utc_text(utc_now() + timedelta(minutes=LOCKOUT_MINUTES)) if failures >= MAX_LOGIN_FAILURES else None
        await db.execute(
            """INSERT INTO login_attempts (client_key, failures, locked_until)
               VALUES (?, ?, ?)
               ON CONFLICT(client_key) DO UPDATE SET
                 failures=excluded.failures, locked_until=excluded.locked_until""",
            client_key, failures, locked,
        )
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    await db.execute("DELETE FROM login_attempts WHERE client_key = ?", client_key)
    raw_session = secrets.token_urlsafe(48)
    raw_csrf = secrets.token_urlsafe(32)
    now = utc_now()
    await db.execute(
        """INSERT INTO admin_sessions (token_hash, csrf_hash, created_at, expires_at)
           VALUES (?, ?, ?, ?)""",
        token_digest(raw_session), token_digest(raw_csrf),
        utc_text(now), utc_text(now + timedelta(hours=SESSION_HOURS)),
    )
    response.set_cookie(
        key=SESSION_COOKIE, value=raw_session, httponly=True, secure=True,
        samesite="strict", max_age=SESSION_HOURS * 3600, path="/",
    )
    return {"success": True, "username": user["username"],
            "csrf_token": raw_csrf, "expires_in_seconds": SESSION_HOURS * 3600}


@app.get("/auth/me")
async def who_am_i(request: Request):
    return {"authenticated": True, "role": "owner"}


@app.post("/auth/logout")
async def logout(request: Request, response: Response):
    raw = request.cookies.get(SESSION_COOKIE)
    if raw:
        await store(request).execute(
            "DELETE FROM admin_sessions WHERE token_hash = ?", token_digest(raw)
        )
    response.delete_cookie(SESSION_COOKIE, path="/", httponly=True, samesite="strict", secure=True)
    return {"success": True, "message": "Logged out."}


@app.post("/auth/change-password")
async def change_password(data: ChangePasswordRequest, request: Request, response: Response):
    db = store(request)
    user = await db.one("SELECT password_hash FROM admin_user WHERE id = 1")
    if not user or not verify_password(data.current_password, user["password_hash"]):
        raise HTTPException(status_code=403, detail="Current password is incorrect.")
    await db.execute(
        "UPDATE admin_user SET password_hash = ?, updated_at = ? WHERE id = 1",
        make_password_hash(data.new_password), utc_text(utc_now()),
    )
    await db.execute("DELETE FROM admin_sessions")
    response.delete_cookie(SESSION_COOKIE, path="/", httponly=True, samesite="strict", secure=True)
    return {"success": True, "message": "Password changed. Sign in again."}


@app.get("/social/platforms")
async def social_platforms(request: Request):
    social, _, _, _ = repos(request)
    return {"max_accounts_per_platform": 10,
            "facebook_account_types": {"facebook_profile": "Personal profiles", "facebook_page": "Pages"},
            "platforms": sorted(SUPPORTED_PLATFORMS),
            "limits": await social.account_limits(),
            "note": "Slots are not OAuth connections. Live posting is disabled."}


@app.get("/social/accounts")
async def list_social_accounts(request: Request, platform: Optional[str] = Query(default=None)):
    social, _, _, _ = repos(request)
    return {"accounts": await social.list_accounts(platform),
            "limits": await social.account_limits()}


@app.post("/social/accounts", status_code=201)
async def add_social_account(data: SocialAccountRequest, request: Request):
    social, _, _, _ = repos(request)
    try:
        account = await social.add_account(data.platform, data.account_name, data.account_handle)
    except OverflowError as error:
        raise HTTPException(status_code=409, detail=str(error))
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return {"account": account, "message": "Slot saved. Official OAuth is not yet connected."}


@app.get("/social/accounts/{account_id}/preferences")
async def get_preferences(account_id: int, request: Request):
    social, _, _, _ = repos(request)
    result = await social.get_preferences(account_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Social account not found.")
    return result


@app.put("/social/accounts/{account_id}/preferences")
async def update_preferences(account_id: int, data: PreferencesRequest, request: Request):
    social, _, _, _ = repos(request)
    try:
        result = await social.update_preferences(account_id, data.model_dump(exclude_unset=True))
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    if result is None:
        raise HTTPException(status_code=404, detail="Social account not found.")
    return {"preferences": result, "message": "Preferences saved."}


@app.delete("/social/accounts/{account_id}")
async def delete_social_account(account_id: int, request: Request):
    social, _, _, _ = repos(request)
    if not await social.remove_account(account_id):
        raise HTTPException(status_code=404, detail="Social account not found.")
    return {"success": True}


@app.get("/control/settings")
async def get_controls(request: Request):
    social, _, _, _ = repos(request)
    return await social.get_owner_controls()


@app.put("/control/settings")
async def update_controls(data: ControlsRequest, request: Request):
    social, _, _, _ = repos(request)
    result = await social.update_owner_controls(
        data.global_publishing_enabled, data.require_approval
    )
    return {"settings": result, "message": "Owner controls updated."}


@app.post("/content", status_code=201)
async def create_content(data: ContentRequest, request: Request):
    _, content, _, _ = repos(request)
    result = await content.create_content(data.title.strip(), data.body.strip(), data.platform)
    return result


@app.get("/content")
async def list_content(request: Request):
    _, content, _, _ = repos(request)
    return await content.get_all_content()


@app.post("/content/{content_id}/ready")
async def mark_content_ready(content_id: int, request: Request):
    _, content, _, _ = repos(request)
    result = await content.mark_ready(content_id)
    if not result:
        raise HTTPException(status_code=404, detail="Content draft not found.")
    return {**result, "message": "Marked ready only; not published externally."}


@app.post("/seo/analyze")
async def analyze_seo(data: SEORequest):
    return seo.analyze_content(data.title, data.content, data.keyword)


@app.post("/keywords/analyze")
async def analyze_keywords(data: KeywordRequest):
    return keywords.create_keyword_report(data.text, data.main_keyword)


@app.post("/campaigns", status_code=201)
async def create_campaign(data: CampaignRequest, request: Request):
    _, _, campaigns, _ = repos(request)
    return await campaigns.create_campaign(data.name, data.platform, data.website_url)


@app.get("/campaigns")
async def list_campaigns(request: Request):
    _, _, campaigns, _ = repos(request)
    return await campaigns.get_campaigns()


@app.post("/analytics/record", status_code=201)
async def add_analytics(data: AnalyticsRequest, request: Request):
    _, _, _, analytics = repos(request)
    return await analytics.add_daily_record(**data.model_dump())


@app.get("/analytics/summary")
async def analytics_summary(request: Request):
    _, _, _, analytics = repos(request)
    records = await analytics.get_report()
    return {"record_count": len(records),
            "total_earnings": await analytics.total_earnings(),
            "records": records}


async def serve_dashboard(path: str, request: Request):
    env = request.scope.get("env")
    assets = getattr(env, "ASSETS", None) if env else None
    if assets is None:
        raise HTTPException(status_code=503, detail="Dashboard assets are not configured.")
    asset_path = "/index.html" if not path else "/" + path
    try:
        asset_response = await assets.fetch("https://assets.local" + asset_path)
        body = await asset_response.bytes()
        content_type = asset_response.headers.get("content-type", "application/octet-stream")
        return Response(content=body, status_code=asset_response.status,
                        headers={"Content-Type": content_type})
    except Exception:
        raise HTTPException(status_code=404, detail="Dashboard asset not found.")


@app.get("/app")
async def dashboard_root(request: Request):
    return await serve_dashboard("", request)


@app.get("/app/{path:path}")
async def dashboard_asset(path: str, request: Request):
    return await serve_dashboard(path, request)
