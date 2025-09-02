from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class WordBase(BaseModel):
    korean: str
    english: str
    part_of_speech: Optional[str] = None
    romanization: Optional[str] = None
    topik_level: Optional[int] = Field(None, ge=1, le=6)
    source_type: Optional[str] = None
    source_details: Optional[str] = None
    added_by_agent: Optional[str] = None


class WordCreate(WordBase):
    pass


class WordResponse(WordBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class WordUpdate(WordBase):
    korean: Optional[str] = None
    english: Optional[str] = None
    part_of_speech: Optional[str] = None
    romanization: Optional[str] = None
    topik_level: Optional[int] = Field(None, ge=1, le=6)
    source_type: Optional[str] = None
    source_details: Optional[str] = None
    added_by_agent: Optional[str] = None


class PracticeRequest(BaseModel):
    practice_type: Optional[str] = Field(
        default="definition",
        description="Type of practice content to generate",
    )

    class Config:
        schema_extra = {"example": {"practice_type": "definition"}}


class PracticeResponse(BaseModel):
    content: str = Field(description="AI-generated practice content")
    type: str = Field(description="Type of practice content")
    word_id: int = Field(description="ID of the word this practice is for")

    class Config:
        schema_extra = {
            "example": {
                "content": "The Korean word '안녕하세요' is a formal greeting meaning 'hello' or 'how are you?'",
                "type": "definition",
                "word_id": 1,
            }
        }
