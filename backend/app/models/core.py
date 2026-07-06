from datetime import datetime

from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(256))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    accounts: Mapped[list["Account"]] = relationship(back_populates="owner")


class Account(Base):
    """A business/creator Instagram account being managed (metadata only, no credentials)."""
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    display_name: Mapped[str] = mapped_column(String(128))
    niche: Mapped[str | None] = mapped_column(String(128), nullable=True)
    audience: Mapped[str | None] = mapped_column(Text, nullable=True)
    brand_voice: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    owner: Mapped["User"] = relationship(back_populates="accounts")


class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id"), nullable=True)
    filename: Mapped[str] = mapped_column(String(256))
    stored_path: Mapped[str] = mapped_column(String(512))
    content_type: Mapped[str] = mapped_column(String(64))
    purpose: Mapped[str] = mapped_column(String(64))  # insights_csv, insights_json, media, screenshot, other
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ComplianceLog(Base):
    __tablename__ = "compliance_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    endpoint: Mapped[str] = mapped_column(String(128))
    input_excerpt: Mapped[str] = mapped_column(Text)
    allowed: Mapped[bool] = mapped_column(Boolean)
    category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    explanation: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class LLMCall(Base):
    __tablename__ = "llm_calls"

    id: Mapped[int] = mapped_column(primary_key=True)
    provider: Mapped[str] = mapped_column(String(32))
    model: Mapped[str] = mapped_column(String(128))
    purpose: Mapped[str] = mapped_column(String(64))
    prompt_excerpt: Mapped[str] = mapped_column(Text)
    response_excerpt: Mapped[str] = mapped_column(Text)
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
