from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .game_session import GameSession
    from .word import Word


class GameItem(SQLModel, table=True):
    __tablename__ = "game_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="game_sessions.id", nullable=False)
    word_id: int = Field(foreign_key="words.id", nullable=False)
    correct: bool = Field(nullable=False)
    time_ms: int = Field(nullable=False)  # time taken in milliseconds

    # Relationships
    session: "GameSession" = Relationship(back_populates="game_items")
    word: "Word" = Relationship()
