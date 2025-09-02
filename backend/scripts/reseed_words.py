import asyncio
import sys
from pathlib import Path

# Add the backend src directory to the Python path
backend_root = Path(__file__).parent.parent
sys.path.insert(0, str(backend_root))

from src.db.seed.words import load_words
from src.database import async_session_factory


async def run():
    async with async_session_factory() as db:
        await load_words(db)


if __name__ == "__main__":
    asyncio.run(run())
