#!/usr/bin/env python3
"""
Database reset and reseed script for the Korean learning app.
This script completely clears the database and reseeds it with fresh data.
"""

import asyncio
import sys
from pathlib import Path

# Add the backend src directory to the Python path
backend_root = Path(__file__).parent.parent
sys.path.insert(0, str(backend_root))

from sqlalchemy import text
from src.database import async_session_factory, engine
from src.db.seed.words import load_words
from src.db.seed.groups import load_groups
from src.db.seed.sentences import load_sentences


async def clear_all_tables():
    """Clear all data from all tables in the correct order to avoid foreign key constraints."""
    print("🗑️  Clearing all database tables...")

    async with async_session_factory() as db:
        try:
            # Clear tables in reverse dependency order to avoid foreign key constraints
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
                    print(f"   ✅ Cleared {table}")
                except Exception as e:
                    print(f"   ⚠️  Warning: Could not clear {table}: {e}")

            await db.commit()
            print("✅ All tables cleared successfully")

        except Exception as e:
            print(f"❌ Error clearing tables: {e}")
            await db.rollback()
            raise


async def reset_auto_increment():
    """Reset auto-increment counters for all tables."""
    print("🔄 Resetting auto-increment counters...")

    async with async_session_factory() as db:
        try:
            # Reset SQLite sequences
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
                    print(f"   ✅ Reset auto-increment for {table}")
                except Exception as e:
                    print(
                        f"   ⚠️  Warning: Could not reset auto-increment for {table}: {e}"
                    )

            await db.commit()
            print("✅ Auto-increment counters reset successfully")

        except Exception as e:
            print(f"❌ Error resetting auto-increment: {e}")
            await db.rollback()
            raise


async def seed_all_data():
    """Seed the database with all initial data."""
    print("🌱 Seeding database with fresh data...")

    try:
        # Seed words first (base data)
        print("\n📚 Seeding words...")
        async with async_session_factory() as db:
            await load_words(db)

        # Seed word groups (depends on words)
        print("\n🏷️  Seeding word groups...")
        async with async_session_factory() as db:
            await load_groups(db)

        # Seed sample sentences (depends on words)
        print("\n💬 Seeding sample sentences...")
        async with async_session_factory() as db:
            await load_sentences(db)

        print("\n✅ All data seeded successfully!")

    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        raise


async def verify_data():
    """Verify that data was seeded correctly."""
    print("\n🔍 Verifying seeded data...")

    async with async_session_factory() as db:
        try:
            # Check word count
            result = await db.execute(text("SELECT COUNT(*) FROM words"))
            word_count = result.scalar()
            print(f"   📚 Words: {word_count}")

            # Check group count
            result = await db.execute(text("SELECT COUNT(*) FROM word_groups"))
            group_count = result.scalar()
            print(f"   🏷️  Groups: {group_count}")

            # Check sentence count
            result = await db.execute(
                text("SELECT COUNT(*) FROM sample_sentences")
            )
            sentence_count = result.scalar()
            print(f"   💬 Sentences: {sentence_count}")

            # Check word-group associations
            result = await db.execute(
                text("SELECT COUNT(*) FROM word_group_map")
            )
            association_count = result.scalar()
            print(f"   🔗 Word-Group associations: {association_count}")

            # Sample Korean text verification
            result = await db.execute(text("SELECT korean FROM words LIMIT 5"))
            sample_words = result.fetchall()
            print(
                f"   🇰🇷 Sample Korean words: {[row[0] for row in sample_words]}"
            )

            print("✅ Data verification completed successfully!")

        except Exception as e:
            print(f"❌ Error during verification: {e}")
            raise


async def main():
    """Main function to reset and reseed the database."""
    print("🚀 Starting database reset and reseed process...")
    print("=" * 60)

    try:
        # Step 1: Clear all existing data
        await clear_all_tables()

        # Step 2: Reset auto-increment counters
        await reset_auto_increment()

        # Step 3: Seed fresh data
        await seed_all_data()

        # Step 4: Verify the results
        await verify_data()

        print("\n" + "=" * 60)
        print("🎉 Database reset and reseed completed successfully!")
        print("   The database now contains fresh Korean learning data.")
        print("   All Korean text is properly encoded in UTF-8.")

    except Exception as e:
        print(f"\n❌ Database reset failed: {e}")
        print("   Please check the error messages above and try again.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
