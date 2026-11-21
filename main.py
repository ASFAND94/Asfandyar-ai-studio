from datetime import datetime
from typing import Literal, Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from analytics_manager import AnalyticsManager
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
    description="Free AI Digital Marketing Manager",
    version="1.2.0",
)

content_manager = ContentManager()
analytics_manager = AnalyticsManager()
keyword_manager = KeywordManager()
seo_manager = SEOManager()
traffic_manager = TrafficManager()
social_accounts = SocialAccountManager()


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


@app.get("/")
def home():
    return {
        "project": "Asfandyar AI Studio",
        "status": "running",
        "version": app.version,
        "message": "Welcome to Asfandyar AI Studio",
    }


@app.get("/health")
def health():
    return {"status": "healthy", "time": datetime.now().astimezone().isoformat()}


@app.get("/features")
def features():
    return {
        "features": [
            "AI-assisted content planning",
            "Content draft management",
            "SEO analysis",
            "Keyword analysis",
            "Per-platform multi-account registry (5 account slots each)",
            "Blogger integration (credentials required)",
            "Social publishing adapters (official API/OAuth required)",
            "Traffic campaign planning",
            "Analytics reporting",
            "Adsterra and Monetag tracking (manual/API data only until verified)",
        ]
    }


@app.get("/social/platforms")
def social_platforms():
    return {
        "max_accounts_per_platform": MAX_ACCOUNTS_PER_PLATFORM,
        "platforms": sorted(SUPPORTED_PLATFORMS),
        "limits": social_accounts.account_limits(),
        "note": "Account slots are not the same as authenticated connections. "
                "Official OAuth setup is required to mark accounts connected.",
    }


@app.get("/social/accounts")
def list_social_accounts(platform: Optional[str] = Query(default=None)):
    try:
        return {
            "accounts": social_accounts.list_accounts(platform),
            "limits": social_accounts.account_limits(),
        }
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.post("/social/accounts", status_code=201)
def add_social_account(request: SocialAccountRequest):
    try:
        account = social_accounts.add_account(
            request.platform, request.account_name, request.account_handle
        )
        return {
            "account": account,
            "message": "Account slot created. Complete the platform's official "
                       "OAuth authorization before publishing.",
        }
    except OverflowError as error:
        raise HTTPException(status_code=409, detail=str(error))
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.delete("/social/accounts/{account_id}")
def delete_social_account(account_id: int):
    if not social_accounts.remove_account(account_id):
        raise HTTPException(status_code=404, detail="Social account not found.")
    return {"success": True, "message": "Account slot removed."}


@app.post("/content", status_code=201)
def create_content_draft(request: ContentDraftRequest):
    draft = content_manager.create_content(
        request.title.strip(), request.body.strip(), request.platform
    )
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
    return {
        **content,
        "message": "Marked ready. This endpoint does not publish externally.",
    }


@app.post("/seo/analyze")
def analyze_seo(request: SEORequest):
    return seo_manager.analyze_content(
        request.title, request.content, request.keyword
    )


@app.post("/keywords/analyze")
def analyze_keywords(request: KeywordRequest):
    return keyword_manager.create_keyword_report(
        request.text, request.main_keyword
    )


@app.post("/campaigns", status_code=201)
def create_campaign(request: CampaignRequest):
    return traffic_manager.create_campaign(
        request.name, request.platform, request.website_url
    )


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
    return {
        "record_count": len(records),
        "total_earnings": analytics_manager.total_earnings(),
        "records": records,
    }
