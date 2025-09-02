#!/usr/bin/env python3
"""
Pure Python scoring tool for game rounds.
Provides deterministic scoring without external dependencies.
"""
from typing import List, Dict, Any
from dataclasses import dataclass
import time


@dataclass
class GameItem:
    """Represents a single game item result"""

    word_id: int
    correct: bool
    time_ms: int


@dataclass
class ScoreResult:
    """Result of scoring a game round"""

    correct: int
    total: int
    accuracy: float  # percentage 0-100
    wpm: float  # words per minute
    score: int  # calculated score


def score_round(
    items: List[GameItem], duration_sec: int = None
) -> ScoreResult:
    """
    Score a game round based on correctness and timing.

    Args:
        items: List of GameItem objects with results
        duration_sec: Optional total duration for WPM calculation

    Returns:
        ScoreResult with calculated metrics
    """
    if not items:
        return ScoreResult(correct=0, total=0, accuracy=0.0, wpm=0.0, score=0)

    # Basic counts
    total = len(items)
    correct = sum(1 for item in items if item.correct)
    accuracy = (correct / total) * 100.0 if total > 0 else 0.0

    # Calculate WPM
    wpm = 0.0
    if duration_sec and duration_sec > 0:
        minutes = duration_sec / 60.0
        wpm = total / minutes
    else:
        # Fallback: use total time from individual items
        total_time_ms = sum(item.time_ms for item in items)
        if total_time_ms > 0:
            minutes = total_time_ms / (1000.0 * 60.0)
            wpm = total / minutes

    # Calculate score
    # Base score: 100 points per correct answer
    base_score = correct * 100

    # Accuracy bonus: up to 50% bonus for high accuracy
    accuracy_bonus = int(base_score * (accuracy / 100.0) * 0.5)

    # Speed bonus: bonus for fast answers (under 3 seconds)
    speed_bonus = 0
    for item in items:
        if item.correct and item.time_ms < 3000:  # Under 3 seconds
            speed_bonus += 25
        elif item.correct and item.time_ms < 5000:  # Under 5 seconds
            speed_bonus += 10

    total_score = base_score + accuracy_bonus + speed_bonus

    return ScoreResult(
        correct=correct,
        total=total,
        accuracy=accuracy,
        wpm=wpm,
        score=total_score,
    )


def score_round_from_dict(
    items_data: List[Dict[str, Any]], duration_sec: int = None
) -> Dict[str, Any]:
    """
    Score a round from dictionary data (for API usage).

    Args:
        items_data: List of dicts with keys: word_id, correct, time_ms
        duration_sec: Optional total duration for WPM calculation

    Returns:
        Dictionary with scoring results
    """
    items = [
        GameItem(
            word_id=item["word_id"],
            correct=item["correct"],
            time_ms=item["time_ms"],
        )
        for item in items_data
    ]

    result = score_round(items, duration_sec)

    return {
        "correct": result.correct,
        "total": result.total,
        "accuracy": result.accuracy,
        "wpm": result.wpm,
        "score": result.score,
    }


# Example usage and testing
if __name__ == "__main__":
    # Test cases
    test_items = [
        GameItem(word_id=1, correct=True, time_ms=2000),  # Fast correct
        GameItem(word_id=2, correct=True, time_ms=4000),  # Medium correct
        GameItem(word_id=3, correct=False, time_ms=6000),  # Slow incorrect
        GameItem(word_id=4, correct=True, time_ms=1500),  # Very fast correct
        GameItem(word_id=5, correct=True, time_ms=8000),  # Slow correct
    ]

    result = score_round(test_items, duration_sec=60)

    print("Scoring Test Results:")
    print(f"Correct: {result.correct}/{result.total}")
    print(f"Accuracy: {result.accuracy:.1f}%")
    print(f"WPM: {result.wpm:.1f}")
    print(f"Score: {result.score}")

    # Test edge cases
    print("\nEdge Case Tests:")

    # Empty round
    empty_result = score_round([])
    print(f"Empty round: {empty_result}")

    # Perfect round
    perfect_items = [
        GameItem(word_id=i, correct=True, time_ms=2000) for i in range(1, 11)
    ]
    perfect_result = score_round(perfect_items, duration_sec=60)
    print(
        f"Perfect round (10/10): Score={perfect_result.score}, Accuracy={perfect_result.accuracy}%"
    )

    # All wrong
    wrong_items = [
        GameItem(word_id=i, correct=False, time_ms=5000) for i in range(1, 11)
    ]
    wrong_result = score_round(wrong_items, duration_sec=60)
    print(
        f"All wrong (0/10): Score={wrong_result.score}, Accuracy={wrong_result.accuracy}%"
    )
