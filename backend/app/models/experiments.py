from datetime import datetime

from sqlalchemy import String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Experiment(Base):
    __tablename__ = "experiments"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id"), nullable=True)
    variable: Mapped[str] = mapped_column(String(64))  # hook_type, caption_style, posting_time, etc.
    hypothesis: Mapped[str] = mapped_column(Text)
    expected_metric_improvement: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default="planned")  # planned, running, complete
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    results: Mapped[list["ExperimentResult"]] = relationship(back_populates="experiment")


class ExperimentResult(Base):
    __tablename__ = "experiment_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    experiment_id: Mapped[int] = mapped_column(ForeignKey("experiments.id"))
    actual_results: Mapped[str] = mapped_column(Text)
    winner_or_loser: Mapped[str] = mapped_column(String(16))  # winner, loser, inconclusive
    lesson_learned: Mapped[str] = mapped_column(Text)
    next_recommended_test: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    experiment: Mapped["Experiment"] = relationship(back_populates="results")


class CompetitorNote(Base):
    __tablename__ = "competitor_notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id"), nullable=True)
    competitor_name: Mapped[str] = mapped_column(String(128))
    profile_reference: Mapped[str | None] = mapped_column(String(256), nullable=True)  # plain text, not scraped
    content_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    hook: Mapped[str | None] = mapped_column(Text, nullable=True)
    topic: Mapped[str | None] = mapped_column(String(128), nullable=True)
    offer: Mapped[str | None] = mapped_column(Text, nullable=True)
    visual_style: Mapped[str | None] = mapped_column(Text, nullable=True)
    estimated_engagement: Mapped[str | None] = mapped_column(String(64), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    screenshot_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    why_it_worked: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id"), nullable=True)
    raw_text: Mapped[str] = mapped_column(Text)
    classification: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    reply_drafts: Mapped[list["ReplyDraft"]] = relationship(
        "ReplyDraft", back_populates="comment", foreign_keys="ReplyDraft.comment_id"
    )


class DMMessage(Base):
    __tablename__ = "dm_messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id"), nullable=True)
    raw_text: Mapped[str] = mapped_column(Text)
    classification: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ReplyDraft(Base):
    """
    Draft-only replies. Never auto-sent. Sending, if ever implemented via an
    approved official API, requires explicit per-message human confirmation.
    """
    __tablename__ = "reply_drafts"

    id: Mapped[int] = mapped_column(primary_key=True)
    comment_id: Mapped[int | None] = mapped_column(ForeignKey("comments.id"), nullable=True)
    dm_id: Mapped[int | None] = mapped_column(ForeignKey("dm_messages.id"), nullable=True)
    tone: Mapped[str] = mapped_column(String(32))
    draft_text: Mapped[str] = mapped_column(Text)
    approved: Mapped[bool] = mapped_column(default=False)
    sent: Mapped[bool] = mapped_column(default=False)  # always False; no send path exists yet
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    comment: Mapped["Comment"] = relationship("Comment", back_populates="reply_drafts", foreign_keys=[comment_id])
