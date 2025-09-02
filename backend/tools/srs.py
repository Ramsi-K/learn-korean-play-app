#!/usr/bin/env python3
"""
Spaced Repetition System (SRS) tool for scheduling word reviews.
Implements a simplified SM-2 algorithm with Leitner box fallback.
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import math


@dataclass
class ReviewSchedule:
    """Represents a word's review schedule"""

    word_id: int
    next_review: datetime
    interval_days: int
    ease_factor: float
    repetitions: int
    last_reviewed: datetime


class SRSScheduler:
    """
    Simplified SRS scheduler based on SM-2 algorithm.
    """

    # Default parameters
    DEFAULT_EASE_FACTOR = 2.5
    MIN_EASE_FACTOR = 1.3
    MAX_EASE_FACTOR = 4.0

    # Initial intervals (in days)
    INITIAL_INTERVALS = [1, 6]  # First two intervals are fixed

    def __init__(self):
        pass

    def schedule_review(
        self,
        word_id: int,
        correct: bool,
        current_schedule: Optional[ReviewSchedule] = None,
    ) -> ReviewSchedule:
        """
        Schedule the next review for a word based on performance.

        Args:
            word_id: ID of the word
            correct: Whether the answer was correct
            current_schedule: Existing schedule (None for new words)

        Returns:
            Updated ReviewSchedule
        """
        now = datetime.utcnow()

        if current_schedule is None:
            # New word - start with first interval
            return ReviewSchedule(
                word_id=word_id,
                next_review=now + timedelta(days=self.INITIAL_INTERVALS[0]),
                interval_days=self.INITIAL_INTERVALS[0],
                ease_factor=self.DEFAULT_EASE_FACTOR,
                repetitions=0,
                last_reviewed=now,
            )

        # Update existing schedule
        new_repetitions = current_schedule.repetitions + 1
        new_ease_factor = current_schedule.ease_factor
        new_interval = current_schedule.interval_days

        if correct:
            # Correct answer - increase interval
            if new_repetitions == 1:
                new_interval = self.INITIAL_INTERVALS[0]
            elif new_repetitions == 2:
                new_interval = self.INITIAL_INTERVALS[1]
            else:
                # Use SM-2 formula: new_interval = old_interval * ease_factor
                new_interval = max(
                    1, int(current_schedule.interval_days * new_ease_factor)
                )

            # Adjust ease factor slightly upward for correct answers
            new_ease_factor = min(self.MAX_EASE_FACTOR, new_ease_factor + 0.1)
        else:
            # Incorrect answer - reset to beginning but keep some progress
            new_repetitions = 0
            new_interval = self.INITIAL_INTERVALS[0]

            # Decrease ease factor for incorrect answers
            new_ease_factor = max(self.MIN_EASE_FACTOR, new_ease_factor - 0.2)

        return ReviewSchedule(
            word_id=word_id,
            next_review=now + timedelta(days=new_interval),
            interval_days=new_interval,
            ease_factor=new_ease_factor,
            repetitions=new_repetitions,
            last_reviewed=now,
        )

    def get_due_words(
        self, schedules: list[ReviewSchedule], limit: int = 20
    ) -> list[ReviewSchedule]:
        """
        Get words that are due for review.

        Args:
            schedules: List of all word schedules
            limit: Maximum number of words to return

        Returns:
            List of schedules that are due for review
        """
        now = datetime.utcnow()

        due_schedules = [
            schedule for schedule in schedules if schedule.next_review <= now
        ]

        # Sort by next_review time (most overdue first)
        due_schedules.sort(key=lambda s: s.next_review)

        return due_schedules[:limit]

    def calculate_retention_rate(
        self, schedules: list[ReviewSchedule]
    ) -> float:
        """
        Calculate overall retention rate based on ease factors.

        Args:
            schedules: List of word schedules

        Returns:
            Estimated retention rate (0.0 to 1.0)
        """
        if not schedules:
            return 0.0

        # Higher ease factor indicates better retention
        avg_ease = sum(s.ease_factor for s in schedules) / len(schedules)

        # Convert ease factor to retention rate (rough approximation)
        # Ease factor 1.3 -> ~60% retention
        # Ease factor 2.5 -> ~85% retention
        # Ease factor 4.0 -> ~95% retention
        retention = min(
            0.95, max(0.6, (avg_ease - 1.3) / (4.0 - 1.3) * 0.35 + 0.6)
        )

        return retention


def schedule_review_from_dict(
    word_id: int,
    correct: bool,
    current_schedule_dict: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Schedule review from dictionary data (for API usage).

    Args:
        word_id: ID of the word
        correct: Whether the answer was correct
        current_schedule_dict: Existing schedule as dict (None for new words)

    Returns:
        Dictionary with updated schedule
    """
    scheduler = SRSScheduler()

    current_schedule = None
    if current_schedule_dict:
        current_schedule = ReviewSchedule(
            word_id=current_schedule_dict["word_id"],
            next_review=datetime.fromisoformat(
                current_schedule_dict["next_review"]
            ),
            interval_days=current_schedule_dict["interval_days"],
            ease_factor=current_schedule_dict["ease_factor"],
            repetitions=current_schedule_dict["repetitions"],
            last_reviewed=datetime.fromisoformat(
                current_schedule_dict["last_reviewed"]
            ),
        )

    new_schedule = scheduler.schedule_review(
        word_id, correct, current_schedule
    )

    return {
        "word_id": new_schedule.word_id,
        "next_review": new_schedule.next_review.isoformat(),
        "interval_days": new_schedule.interval_days,
        "ease_factor": new_schedule.ease_factor,
        "repetitions": new_schedule.repetitions,
        "last_reviewed": new_schedule.last_reviewed.isoformat(),
    }


# Example usage and testing
if __name__ == "__main__":
    scheduler = SRSScheduler()

    print("SRS Scheduler Test:")
    print("=" * 40)

    # Test new word
    word_id = 123
    schedule1 = scheduler.schedule_review(word_id, True)
    print(f"New word {word_id}:")
    print(f"  Next review: {schedule1.next_review}")
    print(f"  Interval: {schedule1.interval_days} days")
    print(f"  Ease factor: {schedule1.ease_factor}")

    # Test correct answer progression
    schedule2 = scheduler.schedule_review(word_id, True, schedule1)
    print(f"\nAfter correct answer:")
    print(f"  Next review: {schedule2.next_review}")
    print(f"  Interval: {schedule2.interval_days} days")
    print(f"  Ease factor: {schedule2.ease_factor}")

    schedule3 = scheduler.schedule_review(word_id, True, schedule2)
    print(f"\nAfter another correct answer:")
    print(f"  Next review: {schedule3.next_review}")
    print(f"  Interval: {schedule3.interval_days} days")
    print(f"  Ease factor: {schedule3.ease_factor}")

    # Test incorrect answer
    schedule4 = scheduler.schedule_review(word_id, False, schedule3)
    print(f"\nAfter incorrect answer:")
    print(f"  Next review: {schedule4.next_review}")
    print(f"  Interval: {schedule4.interval_days} days")
    print(f"  Ease factor: {schedule4.ease_factor}")
    print(f"  Repetitions reset to: {schedule4.repetitions}")

    # Test due words
    print(f"\nTesting due words:")
    test_schedules = [schedule1, schedule2, schedule3, schedule4]
    due_words = scheduler.get_due_words(test_schedules)
    print(f"Due words: {len(due_words)}")

    # Test retention rate
    retention = scheduler.calculate_retention_rate(test_schedules)
    print(f"Estimated retention rate: {retention:.1%}")
