from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .game_session import GameSession


class GameResult(SQLModel, table=True):
    __tablename__ = "game_results"

    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="game_sessions.id", nullable=False)
    total: int = Field(nullable=False)
    correct: int = Field(nullable=False)
    accuracy: float = Field(nullable=False)  # percentage 0-100
    wpm: Optional[float] = None  # words per minute
    score: int = Field(nullable=False)
    ended_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    session: "GameSession" = Relationship(back_populates="game_result")
