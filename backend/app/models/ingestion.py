"""Ingestion bookkeeping models (import jobs and their errors)."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ImportJob(Base):
    __tablename__ = "import_job"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_key: Mapped[str] = mapped_column(String(64), index=True)
    command: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(20), default="running")  # running/success/failed
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    records_created: Mapped[int] = mapped_column(Integer, default=0)
    records_updated: Mapped[int] = mapped_column(Integer, default=0)
    records_skipped: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[str | None] = mapped_column(Text)

    errors = relationship(
        "ImportError", back_populates="job", cascade="all, delete-orphan"
    )


class ImportError(Base):
    __tablename__ = "import_error"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(
        ForeignKey("import_job.id", ondelete="CASCADE"), index=True
    )
    stage: Mapped[str] = mapped_column(String(80))
    message: Mapped[str] = mapped_column(Text)
    payload: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    job = relationship("ImportJob", back_populates="errors")
