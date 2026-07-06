from datetime import datetime, date

from sqlalchemy import String, Integer, Float, DateTime, Date, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class InstagramInsight(Base):
    """Normalized schema for manually-uploaded Instagram Insights data."""
    __tablename__ = "instagram_insights"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id"), nullable=True)

    post_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    content_type: Mapped[str | None] = mapped_column(String(32), nullable=True)  # reel, story, carousel, static
    topic: Mapped[str | None] = mapped_column(String(128), nullable=True)
    caption: Mapped[str | None] = mapped_column(Text, nullable=True)
    hook: Mapped[str | None] = mapped_column(Text, nullable=True)

    reach: Mapped[int | None] = mapped_column(Integer, nullable=True)
    impressions: Mapped[int | None] = mapped_column(Integer, nullable=True)
    likes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    comments: Mapped[int | None] = mapped_column(Integer, nullable=True)
    shares: Mapped[int | None] = mapped_column(Integer, nullable=True)
    saves: Mapped[int | None] = mapped_column(Integer, nullable=True)
    profile_visits: Mapped[int | None] = mapped_column(Integer, nullable=True)
    follows: Mapped[int | None] = mapped_column(Integer, nullable=True)
    unfollows: Mapped[int | None] = mapped_column(Integer, nullable=True)

    watch_time_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    average_watch_duration: Mapped[float | None] = mapped_column(Float, nullable=True)
    completion_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    retention_3s: Mapped[float | None] = mapped_column(Float, nullable=True)
    retention_50pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    retention_95pct: Mapped[float | None] = mapped_column(Float, nullable=True)

    story_exits: Mapped[int | None] = mapped_column(Integer, nullable=True)
    story_taps_forward: Mapped[int | None] = mapped_column(Integer, nullable=True)
    story_taps_back: Mapped[int | None] = mapped_column(Integer, nullable=True)
    story_replies: Mapped[int | None] = mapped_column(Integer, nullable=True)
    link_clicks: Mapped[int | None] = mapped_column(Integer, nullable=True)

    campaign: Mapped[str | None] = mapped_column(String(128), nullable=True)
    cta_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    hook_style: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source_file: Mapped[str | None] = mapped_column(String(256), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ContentItem(Base):
    """A content idea / draft that can be scored, scheduled, and tracked."""
    __tablename__ = "content_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id"), nullable=True)
    content_type: Mapped[str] = mapped_column(String(32))
    topic: Mapped[str | None] = mapped_column(String(128), nullable=True)
    idea: Mapped[str | None] = mapped_column(Text, nullable=True)
    hook: Mapped[str | None] = mapped_column(Text, nullable=True)
    caption: Mapped[str | None] = mapped_column(Text, nullable=True)
    cta: Mapped[str | None] = mapped_column(Text, nullable=True)
    thumbnail_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    media_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="idea")  # kanban stage
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    scores: Mapped[list["ContentScore"]] = relationship(back_populates="content_item")


class ContentScore(Base):
    __tablename__ = "content_scores"

    id: Mapped[int] = mapped_column(primary_key=True)
    content_item_id: Mapped[int] = mapped_column(ForeignKey("content_items.id"))

    overall_score: Mapped[float] = mapped_column(Float)
    hook_score: Mapped[float] = mapped_column(Float)
    clarity_score: Mapped[float] = mapped_column(Float)
    novelty_score: Mapped[float] = mapped_column(Float)
    audience_fit_score: Mapped[float] = mapped_column(Float)
    emotional_pull_score: Mapped[float] = mapped_column(Float)
    usefulness_score: Mapped[float] = mapped_column(Float)
    shareability_score: Mapped[float] = mapped_column(Float)
    saveability_score: Mapped[float] = mapped_column(Float)
    trust_score: Mapped[float] = mapped_column(Float)
    cta_score: Mapped[float] = mapped_column(Float)
    retention_risk: Mapped[str] = mapped_column(String(16))  # low, medium, high
    suggestions: Mapped[str] = mapped_column(Text)  # JSON-encoded list
    method: Mapped[str] = mapped_column(String(32))  # rules, llm, blended
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    content_item: Mapped["ContentItem"] = relationship(back_populates="scores")


class HookAsset(Base):
    __tablename__ = "hooks"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id"), nullable=True)
    style: Mapped[str] = mapped_column(String(64))
    text: Mapped[str] = mapped_column(Text)
    expected_strength: Mapped[float] = mapped_column(Float)
    rationale: Mapped[str] = mapped_column(Text)
    visual_opening: Mapped[str] = mapped_column(Text)
    matching_caption: Mapped[str] = mapped_column(Text)
    matching_cta: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CaptionAsset(Base):
    __tablename__ = "captions"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id"), nullable=True)
    style: Mapped[str] = mapped_column(String(64))
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CTAAsset(Base):
    __tablename__ = "ctas"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id"), nullable=True)
    text: Mapped[str] = mapped_column(Text)
    funnel_stage: Mapped[str] = mapped_column(String(32))  # awareness, consideration, conversion, retention
    content_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    audience_intent: Mapped[str | None] = mapped_column(String(128), nullable=True)
    topic: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ContentCalendarItem(Base):
    __tablename__ = "content_calendar_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id"), nullable=True)
    date: Mapped[date] = mapped_column(Date)
    content_type: Mapped[str] = mapped_column(String(32))
    topic: Mapped[str] = mapped_column(String(128))
    hook: Mapped[str] = mapped_column(Text)
    caption_outline: Mapped[str] = mapped_column(Text)
    cta: Mapped[str] = mapped_column(Text)
    asset_needed: Mapped[str] = mapped_column(Text)
    production_difficulty: Mapped[str] = mapped_column(String(16))  # low, medium, high
    expected_outcome: Mapped[str] = mapped_column(Text)
    experiment_tag: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="idea")  # kanban stage
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
