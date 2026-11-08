"""Team (national side) models."""
from __future__ import annotations

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Team(Base, TimestampMixin):
    __tablename__ = "team"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(140), unique=True, index=True)
    team_type: Mapped[str] = mapped_column(String(20), default="national")

    confederation_id: Mapped[int | None] = mapped_column(ForeignKey("confederation.id"))
    fifa_code: Mapped[str | None] = mapped_column(String(3))
    iso2: Mapped[str | None] = mapped_column(String(10))  # flag CDN code (e.g. gb-eng); null for defunct nations
    is_defunct: Mapped[bool] = mapped_column(default=False)

    source_key: Mapped[str | None] = mapped_column(String(64))

    confederation = relationship("Confederation", lazy="joined")
    aliases = relationship(
        "TeamAlias", back_populates="team", cascade="all, delete-orphan"
    )


class TeamAlias(Base):
    __tablename__ = "team_alias"

    id: Mapped[int] = mapped_column(primary_key=True)
    team_id: Mapped[int] = mapped_column(
        ForeignKey("team.id", ondelete="CASCADE"), index=True
    )
    alias: Mapped[str] = mapped_column(String(120), index=True)

    team = relationship("Team", back_populates="aliases")

    __table_args__ = (UniqueConstraint("team_id", "alias", name="uq_team_alias"),)
