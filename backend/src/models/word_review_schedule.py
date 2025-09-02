from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .word import Word


class WordReviewSchedule(SQLModel, table=True):
    __tablename__ = "word_review_schedules"

    id: Optional[int] = Field(default=None, primary_key=True)
    word_id: int = Field(foreign_key="words.id", nullable=False, unique=True)
    next_review: datetime = Field(nullable=False)
    interval_days: int = Field(nullable=False)
    ease_factor: float = Field(nullable=False, default=2.5)
    repetitions: int = Field(nullable=False, default=0)
    last_reviewed: datetime = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    word: "Word" = Relationship()
