from datetime import datetime

from sqlalchemy import String, Float, Integer, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class SimulationRun(Base):
    """
    A single closed-network virality simulation. Entirely local and synthetic —
    never reads from or writes to any real social platform.
    """
    __tablename__ = "simulation_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(128))
    network_structure: Mapped[str] = mapped_column(String(32))
    num_users: Mapped[int] = mapped_column(Integer)
    config_json: Mapped[str] = mapped_column(Text)   # full input config, JSON-encoded
    results_json: Mapped[str] = mapped_column(Text)  # full output summary, JSON-encoded
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SimulatedUser(Base):
    __tablename__ = "simulated_users"

    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("simulation_runs.id"))
    external_index: Mapped[int] = mapped_column(Integer)
    interest_category: Mapped[str] = mapped_column(String(64))
    activity_hour: Mapped[int] = mapped_column(Integer)
    like_prob: Mapped[float] = mapped_column(Float)
    comment_prob: Mapped[float] = mapped_column(Float)
    save_prob: Mapped[float] = mapped_column(Float)
    share_prob: Mapped[float] = mapped_column(Float)
    watch_prob: Mapped[float] = mapped_column(Float)
    trust_sensitivity: Mapped[float] = mapped_column(Float)
    novelty_sensitivity: Mapped[float] = mapped_column(Float)
    community_cluster: Mapped[int] = mapped_column(Integer)
    fatigue_level: Mapped[float] = mapped_column(Float)


class SimulatedPost(Base):
    __tablename__ = "simulated_posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("simulation_runs.id"))
    topic: Mapped[str] = mapped_column(String(64))
    hook_strength: Mapped[float] = mapped_column(Float)
    visual_quality: Mapped[float] = mapped_column(Float)
    emotional_intensity: Mapped[float] = mapped_column(Float)
    usefulness: Mapped[float] = mapped_column(Float)
    novelty: Mapped[float] = mapped_column(Float)
    controversy: Mapped[float] = mapped_column(Float)
    clarity: Mapped[float] = mapped_column(Float)
    cta_strength: Mapped[float] = mapped_column(Float)
    creator_trust: Mapped[float] = mapped_column(Float)
    posting_hour: Mapped[int] = mapped_column(Integer)


class SimulatedEngagementEvent(Base):
    __tablename__ = "simulated_engagement_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("simulation_runs.id"))
    post_id: Mapped[int] = mapped_column(ForeignKey("simulated_posts.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("simulated_users.id"))
    tick: Mapped[int] = mapped_column(Integer)
    event_type: Mapped[str] = mapped_column(String(16))  # view, like, comment, save, share, negative
