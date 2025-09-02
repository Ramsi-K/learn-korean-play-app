from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, desc, func
from contextlib import asynccontextmanager
from typing import List, Optional
from datetime import datetime
import logging

from ...database import get_db
from ...models.game_session import GameSession
from ...models.game_result import GameResult
from ...models.game_item import GameItem
from ...models.word import Word
from ...models.word_review_schedule import WordReviewSchedule
from tools.score import score_round_from_dict
from tools.srs import schedule_review_from_dict
from tools.agent_quiz import AgentQuizGenerator
from ...services.groq_service import groq_service
from ...schemas.game import (
    GameSessionCreate,
    GameSessionResponse,
    GameSubmitRequest,
    GameSubmitResponse,
    GameRoundResponse,
    GameRoundItem,
    GameStatsResponse,
    GameStatsItem,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/game", tags=["game"])


async def update_word_srs_schedule(db, word_id: int, correct: bool):
    """Update SRS schedule for a word based on performance."""
    # Get existing schedule
    schedule_query = select(WordReviewSchedule).where(
        WordReviewSchedule.word_id == word_id
    )
    schedule_result = await db.execute(schedule_query)
    existing_schedule = schedule_result.scalar_one_or_none()

    # Convert to dict format for SRS tool
    current_schedule_dict = None
    if existing_schedule:
        current_schedule_dict = {
            "word_id": existing_schedule.word_id,
            "next_review": existing_schedule.next_review.isoformat(),
            "interval_days": existing_schedule.interval_days,
            "ease_factor": existing_schedule.ease_factor,
            "repetitions": existing_schedule.repetitions,
            "last_reviewed": existing_schedule.last_reviewed.isoformat(),
        }

    # Calculate new schedule using SRS tool
    new_schedule_dict = schedule_review_from_dict(
        word_id, correct, current_schedule_dict
    )

    # Update or create schedule in database
    if existing_schedule:
        existing_schedule.next_review = datetime.fromisoformat(
            new_schedule_dict["next_review"]
        )
        existing_schedule.interval_days = new_schedule_dict["interval_days"]
        existing_schedule.ease_factor = new_schedule_dict["ease_factor"]
        existing_schedule.repetitions = new_schedule_dict["repetitions"]
        existing_schedule.last_reviewed = datetime.fromisoformat(
            new_schedule_dict["last_reviewed"]
        )
        existing_schedule.updated_at = datetime.utcnow()
    else:
        new_schedule = WordReviewSchedule(
            word_id=new_schedule_dict["word_id"],
            next_review=datetime.fromisoformat(
                new_schedule_dict["next_review"]
            ),
            interval_days=new_schedule_dict["interval_days"],
            ease_factor=new_schedule_dict["ease_factor"],
            repetitions=new_schedule_dict["repetitions"],
            last_reviewed=datetime.fromisoformat(
                new_schedule_dict["last_reviewed"]
            ),
        )
        db.add(new_schedule)


@router.post("/sessions", response_model=GameSessionResponse)
async def create_game_session(
    session_data: GameSessionCreate,
    db_cm: asynccontextmanager = Depends(get_db),
):
    """Create a new game session."""
    async with db_cm as db:
        try:
            # Create new game session
            game_session = GameSession(
                mode=session_data.mode, duration_sec=session_data.duration_sec
            )

            db.add(game_session)
            await db.commit()
            await db.refresh(game_session)

            return GameSessionResponse(
                session_id=game_session.id,
                started_at=game_session.started_at,
                mode=game_session.mode,
                duration_sec=game_session.duration_sec,
            )
        except Exception as e:
            logger.error(f"Error creating game session: {e}")
            await db.rollback()
            raise HTTPException(
                status_code=500, detail="Failed to create game session"
            )


@router.get("/round", response_model=GameRoundResponse)
async def get_game_round(
    count: int = Query(default=10, ge=1, le=50),
    level: Optional[str] = Query(default=None),
    enhance: bool = Query(
        default=False, description="Use AI to generate hints and distractors"
    ),
    db_cm: asynccontextmanager = Depends(get_db),
):
    """Get words for a game round."""
    async with db_cm as db:
        try:
            # Build query for words
            query = select(Word)

            # Filter by TOPIK level if specified
            if level:
                if level.upper() == "TOPIK1":
                    query = query.where(Word.topik_level.in_([1, 2]))
                elif level.upper() == "TOPIK2":
                    query = query.where(Word.topik_level.in_([3, 4, 5, 6]))
                else:
                    # Try to parse as integer
                    try:
                        level_int = int(level)
                        query = query.where(Word.topik_level == level_int)
                    except ValueError:
                        pass  # Ignore invalid level, use all words

            # Order randomly and limit
            query = query.order_by(func.random()).limit(count)

            result = await db.execute(query)
            words = result.scalars().all()

            if not words:
                raise HTTPException(
                    status_code=404,
                    detail="No words found for the specified criteria",
                )

            # Convert to game round items
            if enhance:
                # Use AI to generate hints and distractors
                try:
                    agent_generator = AgentQuizGenerator(groq_service)
                    words_data = [
                        {
                            "id": word.id,
                            "korean": word.korean,
                            "english": word.english,
                        }
                        for word in words
                    ]

                    quiz_items = await agent_generator.generate_quiz_items(
                        words_data, level or "TOPIK1"
                    )

                    items = [
                        GameRoundItem(
                            word_id=item.word_id,
                            korean=item.korean,
                            english=item.answer_en,
                            hint=item.hint,
                            distractors=item.distractors,
                        )
                        for item in quiz_items
                    ]
                except Exception as e:
                    logger.error(
                        f"AI enhancement failed, falling back to basic items: {e}"
                    )
                    # Fallback to basic items
                    items = [
                        GameRoundItem(
                            word_id=word.id,
                            korean=word.korean,
                            english=word.english,
                            hint=None,
                            distractors=None,
                        )
                        for word in words
                    ]
            else:
                # Basic items without AI enhancement
                items = [
                    GameRoundItem(
                        word_id=word.id,
                        korean=word.korean,
                        english=word.english,
                        hint=None,
                        distractors=None,
                    )
                    for word in words
                ]

            return GameRoundResponse(
                items=items, count=len(items), level=level
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting game round: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to get game round"
            )


@router.post("/submit", response_model=GameSubmitResponse)
async def submit_game_results(
    submit_data: GameSubmitRequest,
    db_cm: asynccontextmanager = Depends(get_db),
):
    """Submit game results and save to database."""
    async with db_cm as db:
        try:
            # Verify session exists
            session_query = select(GameSession).where(
                GameSession.id == submit_data.session_id
            )
            session_result = await db.execute(session_query)
            session = session_result.scalar_one_or_none()

            if not session:
                raise HTTPException(
                    status_code=404, detail="Game session not found"
                )

            # Use scoring tool to calculate results
            items_for_scoring = [
                {
                    "word_id": item.word_id,
                    "correct": item.correct,
                    "time_ms": item.time_ms,
                }
                for item in submit_data.items
            ]

            scoring_result = score_round_from_dict(
                items_for_scoring, session.duration_sec
            )

            # Create game result using tool-calculated values
            game_result = GameResult(
                session_id=submit_data.session_id,
                total=scoring_result["total"],
                correct=scoring_result["correct"],
                accuracy=scoring_result["accuracy"],
                wpm=scoring_result["wpm"],
                score=scoring_result["score"],
            )

            db.add(game_result)
            await db.flush()  # Get the ID

            # Create game items and update SRS schedules
            for item_data in submit_data.items:
                # Create game item
                game_item = GameItem(
                    session_id=submit_data.session_id,
                    word_id=item_data.word_id,
                    correct=item_data.correct,
                    time_ms=item_data.time_ms,
                )
                db.add(game_item)

                # Update SRS schedule for this word
                await update_word_srs_schedule(
                    db, item_data.word_id, item_data.correct
                )

            await db.commit()

            return GameSubmitResponse(success=True, result_id=game_result.id)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error submitting game results: {e}")
            await db.rollback()
            raise HTTPException(
                status_code=500, detail="Failed to submit game results"
            )


@router.get("/stats", response_model=GameStatsResponse)
async def get_game_stats(
    limit: int = Query(default=10, ge=1, le=100),
    db_cm: asynccontextmanager = Depends(get_db),
):
    """Get recent game session statistics."""
    async with db_cm as db:
        try:
            # Query recent game results with session info
            query = (
                select(GameResult, GameSession)
                .join(GameSession, GameResult.session_id == GameSession.id)
                .order_by(desc(GameResult.ended_at))
                .limit(limit)
            )

            result = await db.execute(query)
            results = result.all()

            # Convert to response format
            sessions = [
                GameStatsItem(
                    session_id=game_result.session_id,
                    mode=game_session.mode,
                    score=game_result.score,
                    accuracy=game_result.accuracy,
                    wpm=game_result.wpm,
                    ended_at=game_result.ended_at,
                )
                for game_result, game_session in results
            ]

            # Get total session count
            count_query = select(func.count(GameResult.id))
            count_result = await db.execute(count_query)
            total_sessions = count_result.scalar() or 0

            return GameStatsResponse(
                sessions=sessions, total_sessions=total_sessions
            )
        except Exception as e:
            logger.error(f"Error getting game stats: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to get game stats"
            )
