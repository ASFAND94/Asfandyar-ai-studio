from datetime import datetime
from typing import Literal, Optional
import os

from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

from analytics_manager import AnalyticsManager
from auth_manager import AuthManager, SESSION_COOKIE
from content_manager import ContentManager
from keyword_manager import KeywordManager
from seo_manager import SEOManager
from traffic_manager import TrafficManager
from social_account_manager import (
    SocialAccountManager,
    SUPPORTED_PLATFORMS,
    MAX_ACCOUNTS_PER_PLATFORM,
)

app = FastAPI(
    title="Asfandyar AI Studio",
    description="Private, single-owner AI Digital Marketing Manager",
    version="1.4.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

auth = AuthManager()
content_manager = ContentManager()
analytics_manager = AnalyticsManager()
keyword_manager = KeywordManager()
seo_manager = SEOManager()
traffic_manager = TrafficManager()
social_accounts = SocialAccountManager()

app.mount("/app", StaticFiles(directory=str(Path(__file__).resolve().parent / "static"), html=True), name="dashboard")


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


class AccountPreferencesRequest(BaseModel):
    niche: Optional[str] = Field(default=None, max_length=160)
    content_formats: Optional[list[Literal["post", "video", "reel", "story", "short", "article"]]] = None
    publishing_enabled: Optional[bool] = None
    require_approval: Optional[bool] = None


class OwnerControlsRequest(BaseModel):
    global_publishing_enabled: Optional[bool] = None
    require_approval: Optional[bool] = None


class ContentDraftRequest(BaseModel):
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


class SocialAccountRequest(BaseModel):
    platform: str = Field(min_length=1, max_length=30)
    account_name: str = Field(min_length=1, max_length=120)
    account_handle: str = Field(min_length=1, max_length=160)


@app.middleware("http")
async def security_and_auth_middleware(request: Request, call_next):
    path = request.url.path
    public_paths = {"/health", "/auth/status", "/auth/setup", "/auth/login"}
    is_public_asset = path == "/app" or path.startswith("/app/")
    if path not in public_paths and not is_public_asset:
        raw_session = request.cookies.get(SESSION_COOKIE)
        session = auth.validate_session(raw_session)
        if not session:
            response = JSONResponse(status_code=401, content={"detail": "Login required."})
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["Referrer-Policy"] = "no-referrer"
            response.headers["Cache-Control"] = "no-store"
            return response
        if request.method not in {"GET", "HEAD", "OPTIONS"}:
            csrf = request.headers.get("X-CSRF-Token", "")
            if not auth.validate_csrf(session, csrf):
                response = JSONResponse(status_code=403, content={"detail": "CSRF validation failed."})
                response.headers["X-Content-Type-Options"] = "nosniff"
                response.headers["X-Frame-Options"] = "DENY"
                response.headers["Referrer-Policy"] = "no-referrer"
                response.headers["Cache-Control"] = "no-store"
                response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none'; object-src 'none'"
                return response

    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'"
    if request.url.scheme == "https":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


@app.get("/auth/status")
def auth_status():
    return {"setup_required": not auth.is_configured(), "login_required": True}


@app.post("/auth/setup", status_code=201)
def setup_admin(request: SetupRequest):
    try:
        auth.setup(request.setup_key, request.username, request.password)
        return {"success": True, "message": "Admin created. Remove ADMIN_SETUP_KEY from the server environment now, then log in."}
    except FileExistsError as error:
        raise HTTPException(status_code=409, detail=str(error))
    except PermissionError:
        raise HTTPException(status_code=403, detail="Invalid setup key.")
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.post("/auth/login")
def login(request: LoginRequest, http_request: Request, response: Response):
    client_key = http_request.client.host if http_request.client else "unknown"
    try:
        result = auth.login(request.username, request.password, client_key)
    except TimeoutError as error:
        raise HTTPException(status_code=429, detail=str(error))
    if not result:
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    response.set_cookie(
        key=SESSION_COOKIE,
        value=result["session"],
        httponly=True,
        secure=os.getenv("COOKIE_SECURE", "true").lower() == "true",
        samesite="strict",
        max_age=8 * 60 * 60,
        path="/",
    )
    return {"success": True, "username": result["username"], "csrf_token": result["csrf"], "expires_in_seconds": 28800}


@app.get("/auth/me")
def who_am_i(request: Request):
    session = auth.validate_session(request.cookies.get(SESSION_COOKIE))
    return {"authenticated": bool(session), "role": "owner"}


@app.post("/auth/logout")
def logout(request: Request, response: Response):
    auth.logout(request.cookies.get(SESSION_COOKIE))
    response.delete_cookie(SESSION_COOKIE, path="/", httponly=True, samesite="strict")
    return {"success": True, "message": "Logged out."}


@app.post("/auth/change-password")
def change_password(request: ChangePasswordRequest, http_request: Request, response: Response):
    try:
        auth.change_password(
            http_request.cookies.get(SESSION_COOKIE),
            request.current_password, request.new_password
        )
    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error))
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    response.delete_cookie(SESSION_COOKIE, path="/", httponly=True, samesite="strict")
    return {"success": True, "message": "Password changed. All sessions were revoked; log in again."}


@app.get("/")
def home():
    return {
        "project": "Asfandyar AI Studio",
        "status": "running",
        "version": app.version,
        "message": "Private owner dashboard API",
    }


@app.get("/health")
def health():
    return {"status": "healthy", "time": datetime.now().astimezone().isoformat()}


@app.get("/features")
def features():
    return {
        "features": [
            "Private single-owner login with secure sessions",
            "Separate Facebook profile and Facebook Page registries; up to 10 account slots per platform",
            "AI-assisted content planning",
            "Content draft management",
            "SEO and keyword analysis",
            "Blogger integration (credentials and official API required)",
            "Social publishing (official OAuth/API approval required)",
            "Traffic campaign planning",
            "Analytics reporting",
            "Adsterra and Monetag reporting (official integration required)",
        ]
    }


@app.get("/social/platforms")
def social_platforms():
    return {
        "max_accounts_per_platform": MAX_ACCOUNTS_PER_PLATFORM,
        "facebook_account_types": {"facebook_profile": "Personal Facebook profiles", "facebook_page": "Facebook Pages"},
        "platforms": sorted(SUPPORTED_PLATFORMS),
        "limits": social_accounts.account_limits(),
        "note": "Registered account slots are not authenticated platform connections. Official OAuth is required.",
    }


@app.get("/social/accounts")
def list_social_accounts(platform: Optional[str] = Query(default=None)):
    try:
        return {"accounts": social_accounts.list_accounts(platform), "limits": social_accounts.account_limits()}
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.post("/social/accounts", status_code=201)
def add_social_account(request: SocialAccountRequest):
    try:
        account = social_accounts.add_account(request.platform, request.account_name, request.account_handle)
        return {"account": account, "message": "Account slot created. Complete official OAuth before publishing."}
    except OverflowError as error:
        raise HTTPException(status_code=409, detail=str(error))
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.get("/social/accounts/{account_id}/preferences")
def get_social_account_preferences(account_id: int):
    preferences = social_accounts.get_preferences(account_id)
    if preferences is None:
        raise HTTPException(status_code=404, detail="Social account not found.")
    return preferences


@app.put("/social/accounts/{account_id}/preferences")
def update_social_account_preferences(account_id: int, request: AccountPreferencesRequest):
    try:
        preferences = social_accounts.update_preferences(
            account_id, request.model_dump(exclude_unset=True)
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    if preferences is None:
        raise HTTPException(status_code=404, detail="Social account not found.")
    return {
        "preferences": preferences,
        "message": "Saved. The selected niche is owner-defined; publishing remains subject to the global safety switch and platform authorization.",
    }


@app.get("/control/settings")
def get_owner_control_settings():
    return social_accounts.get_owner_controls()


@app.put("/control/settings")
def update_owner_control_settings(request: OwnerControlsRequest):
    settings = social_accounts.update_owner_controls(
        global_publishing_enabled=request.global_publishing_enabled,
        require_approval=request.require_approval,
    )
    return {"settings": settings, "message": "Owner controls updated."}


@app.delete("/social/accounts/{account_id}")
def delete_social_account(account_id: int):
    if not social_accounts.remove_account(account_id):
        raise HTTPException(status_code=404, detail="Social account not found.")
    return {"success": True, "message": "Account slot removed."}


@app.post("/content", status_code=201)
def create_content_draft(request: ContentDraftRequest):
    draft = content_manager.create_content(request.title.strip(), request.body.strip(), request.platform)
    if draft is None:
        raise HTTPException(status_code=400, detail="A title and body are required.")
    return draft


@app.get("/content")
def list_content():
    return content_manager.get_all_content()


@app.post("/content/{content_id}/ready")
def mark_content_ready(content_id: int):
    content = content_manager.publish_content(content_id)
    if content is None:
        raise HTTPException(status_code=404, detail="Content draft not found.")
    return {**content, "message": "Marked ready. This endpoint does not publish externally."}


@app.post("/seo/analyze")
def analyze_seo(request: SEORequest):
    return seo_manager.analyze_content(request.title, request.content, request.keyword)


@app.post("/keywords/analyze")
def analyze_keywords(request: KeywordRequest):
    return keyword_manager.create_keyword_report(request.text, request.main_keyword)


@app.post("/campaigns", status_code=201)
def create_campaign(request: CampaignRequest):
    return traffic_manager.create_campaign(request.name, request.platform, request.website_url)


@app.get("/campaigns")
def list_campaigns():
    return traffic_manager.get_campaigns()


@app.post("/analytics/record", status_code=201)
def add_analytics_record(request: AnalyticsRequest):
    record = analytics_manager.add_daily_record(**request.model_dump())
    return analytics_manager.calculate_metrics(record)


@app.get("/analytics/summary")
def analytics_summary():
    records = analytics_manager.get_report()
    return {"record_count": len(records), "total_earnings": analytics_manager.total_earnings(), "records": records}
