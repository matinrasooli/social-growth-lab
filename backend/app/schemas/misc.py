from datetime import date
from pydantic import BaseModel


class InsightRecord(BaseModel):
    post_date: date | None = None
    content_type: str | None = None
    topic: str | None = None
    caption: str | None = None
    hook: str | None = None
    reach: int | None = None
    impressions: int | None = None
    likes: int | None = None
    comments: int | None = None
    shares: int | None = None
    saves: int | None = None
    profile_visits: int | None = None
    follows: int | None = None
    unfollows: int | None = None
    watch_time_seconds: float | None = None
    average_watch_duration: float | None = None
    completion_rate: float | None = None
    retention_3s: float | None = None
    retention_50pct: float | None = None
    retention_95pct: float | None = None
    story_exits: int | None = None
    story_taps_forward: int | None = None
    story_taps_back: int | None = None
    story_replies: int | None = None
    link_clicks: int | None = None
    campaign: str | None = None
    cta_type: str | None = None
    hook_style: str | None = None


class InsightsImportManual(BaseModel):
    account_id: int | None = None
    records: list[InsightRecord]


class AnalyticsFilter(BaseModel):
    date_from: date | None = None
    date_to: date | None = None
    content_type: str | None = None
    topic: str | None = None
    campaign: str | None = None
    hook_style: str | None = None
    cta_type: str | None = None
    account_id: int | None = None


class ExperimentCreate(BaseModel):
    account_id: int | None = None
    variable: str
    hypothesis: str
    expected_metric_improvement: str


class ExperimentResultCreate(BaseModel):
    experiment_id: int
    actual_results: str
    winner_or_loser: str
    lesson_learned: str
    next_recommended_test: str


class CommentClassifyRequest(BaseModel):
    account_id: int | None = None
    texts: list[str]


class ReplyDraftRequest(BaseModel):
    comment_text: str
    classification: str | None = None
    tones: list[str] | None = None
    account_id: int | None = None


class CompetitorNoteCreate(BaseModel):
    account_id: int | None = None
    competitor_name: str
    profile_reference: str | None = None
    content_type: str | None = None
    hook: str | None = None
    topic: str | None = None
    offer: str | None = None
    visual_style: str | None = None
    estimated_engagement: str | None = None
    notes: str | None = None
    why_it_worked: str | None = None


class SimulationRunRequest(BaseModel):
    name: str
    account_id: int | None = None
    network_structure: str = "small_world"  # random, small_world, influencer_hub, niche_cluster,
    # dense_local_community, sparse_network, multi_community
    num_users: int = 300
    num_ticks: int = 48
    hook_strength: float = 0.6
    visual_quality: float = 0.6
    emotional_intensity: float = 0.5
    usefulness: float = 0.5
    novelty: float = 0.5
    controversy: float = 0.2
    clarity: float = 0.6
    cta_strength: float = 0.5
    creator_trust: float = 0.6
    posting_hour: int = 18
    topic: str = "general"
    experiment_type: str | None = None  # compare_hooks, compare_posting_times, etc.


class ComplianceCheckRequest(BaseModel):
    text: str
