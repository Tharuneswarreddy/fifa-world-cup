"""Import all models so SQLAlchemy metadata (and Alembic) can see them."""
from app.db.base import Base
from app.models.competition import (
    Competition,
    CompetitionEdition,
    GroupStanding,
    TournamentGroup,
    TournamentStage,
)
from app.models.ingestion import ImportError, ImportJob
from app.models.match import Match, MatchGoal, PenaltyShootout
from app.models.player import Player
from app.models.reference import Confederation, DataSource
from app.models.team import Team, TeamAlias

__all__ = [
    "Base",
    "Competition",
    "CompetitionEdition",
    "TournamentStage",
    "TournamentGroup",
    "GroupStanding",
    "Team",
    "TeamAlias",
    "Player",
    "Match",
    "MatchGoal",
    "PenaltyShootout",
    "Confederation",
    "DataSource",
    "ImportJob",
    "ImportError",
]
