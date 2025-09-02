from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ...database import async_session_factory
from ...db.seed.words import load_words
from ...db.seed.groups import load_groups
from ...db.seed.sentences import load_sentences

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/reset/all")
async def reset_database():
    """Reset entire database and reseed with fresh data"""
    try:
        # Clear all tables in reverse dependency order
        async with async_session_factory() as db:
            tables_to_clear = [
                "word_group_map",  # Association table first
                "sample_sentences",
                "activity_logs",
                "word_stats",
                "wrong_inputs",
                "word_review_items",
                "words",
                "word_groups",
                "study_sessions",
            ]

            for table in tables_to_clear:
                try:
                    await db.execute(text(f"DELETE FROM {table}"))
                except Exception:
                    pass  # Table might not exist

            # Reset auto-increment counters
            tables_with_auto_increment = [
                "words",
                "word_groups",
                "sample_sentences",
                "activity_logs",
                "word_stats",
                "wrong_inputs",
                "word_review_items",
                "study_sessions",
            ]

            for table in tables_with_auto_increment:
                try:
                    await db.execute(
                        text(
                            f"DELETE FROM sqlite_sequence WHERE name='{table}'"
                        )
                    )
                except Exception:
                    pass  # Sequence might not exist

            await db.commit()

        # Reseed with fresh data
        async with async_session_factory() as db:
            await load_words(db)

        async with async_session_factory() as db:
            await load_groups(db)

        async with async_session_factory() as db:
            await load_sentences(db)

        return {
            "status": "success",
            "message": "Database fully reset and reseeded with fresh Korean learning data",
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Database reset failed: {str(e)}"
        )


@router.post("/reset/session/{session_id}")
async def reset_study_session(session_id: int):
    """Reset specific study session data"""
    try:
        reset_session(session_id)
        return {
            "status": "success",
            "message": f"Session {session_id} reset successful",
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
