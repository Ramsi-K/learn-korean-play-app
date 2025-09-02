from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class GameSessionCreate(BaseModel):
    mode: str  # "flashcards", "quiz", etc.
    duration_sec: int


class GameSessionResponse(BaseModel):
    session_id: int
    started_at: datetime
    mode: str
    duration_sec: int


class GameItemSubmit(BaseModel):
    word_id: int
    correct: bool
    time_ms: int


class GameSubmitRequest(BaseModel):
    session_id: int
    items: List[GameItemSubmit]
    score: int
    accuracy: float


class GameSubmitResponse(BaseModel):
    success: bool
    result_id: int


class GameRoundItem(BaseModel):
    word_id: int
    korean: str
    english: str
    hint: Optional[str] = None
    distractors: Optional[List[str]] = None


class GameRoundResponse(BaseModel):
    items: List[GameRoundItem]
    count: int
    level: Optional[str] = None


class GameStatsItem(BaseModel):
    session_id: int
    mode: str
    score: int
    accuracy: float
    wpm: Optional[float]
    ended_at: datetime


class GameStatsResponse(BaseModel):
    sessions: List[GameStatsItem]
    total_sessions: int
