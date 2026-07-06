from datetime import date
from pydantic import BaseModel, Field


class ContentScoreRequest(BaseModel):
    niche: str | None = None
    target_audience: str | None = None
    business_goal: str | None = None
    content_idea: str
    hook: str | None = None
    caption: str | None = None
    cta: str | None = None
    thumbnail_description: str | None = None
    content_type: str = Field(default="reel")
    account_id: int | None = None


class ContentScoreResponse(BaseModel):
    overall_score: float
    hook_score: float
    clarity_score: float
    novelty_score: float
    audience_fit_score: float
    emotional_pull_score: float
    usefulness_score: float
    shareability_score: float
    saveability_score: float
    trust_score: float
    cta_score: float
    retention_risk: str
    improvement_suggestions: list[str]
    method: str


class HookGenerateRequest(BaseModel):
    niche: str
    topic: str
    audience: str | None = None
    styles: list[str] | None = None  # if omitted, generate all supported styles
    account_id: int | None = None


class HookResult(BaseModel):
    style: str
    text: str
    expected_strength: float
    rationale: str
    visual_opening: str
    matching_caption: str
    matching_cta: str


class CaptionGenerateRequest(BaseModel):
    topic: str
    niche: str | None = None
    brand_voice: str | None = None
    styles: list[str] | None = None
    account_id: int | None = None


class CaptionResult(BaseModel):
    style: str
    text: str


class CTAGenerateRequest(BaseModel):
    topic: str
    content_type: str = "reel"
    funnel_stage: str | None = None
    audience_intent: str | None = None
    account_id: int | None = None


class CTAResult(BaseModel):
    text: str
    funnel_stage: str
    content_type: str
    audience_intent: str | None = None


class CalendarGenerateRequest(BaseModel):
    niche: str
    audience: str
    business_goal: str
    product: str | None = None
    brand_voice: str | None = None
    posting_frequency_per_week: int = 5
    days: int = 30
    important_dates: list[str] | None = None
    campaigns: list[str] | None = None
    account_id: int | None = None
    start_date: date | None = None


class CalendarItemOut(BaseModel):
    date: date
    content_type: str
    topic: str
    hook: str
    caption_outline: str
    cta: str
    asset_needed: str
    production_difficulty: str
    expected_outcome: str
    experiment_tag: str | None = None
    status: str

    class Config:
        from_attributes = True
