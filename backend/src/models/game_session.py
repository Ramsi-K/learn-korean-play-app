from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .game_result import GameResult
    from .game_item import GameItem


class GameSession(SQLModel, table=True):
    __tablename__ = "game_sessions"

    id: Optional[int] = Field(default=None, primary_key=True)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    mode: str = Field(nullable=False)  # "flashcards", "quiz", etc.
    duration_sec: int = Field(nullable=False)

    # Relationships
    game_result: Optional["GameResult"] = Relationship(
        back_populates="session",
        sa_relationship_kwargs={
            "uselist": False,
            "cascade": "all, delete-orphan",
        },
    )
    game_items: List["GameItem"] = Relationship(
        back_populates="session",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
