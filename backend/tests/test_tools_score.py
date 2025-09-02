#!/usr/bin/env python3
"""
Tests for the scoring tool including edge cases and timing calculations.
"""
import pytest
from tools.score import score_round, score_round_from_dict, GameItem, ScoreResult


class TestScoreRound:
    """Test the score_round function with various scenarios."""

    def test_empty_round(self):
        """Test scoring an empty round."""
        result = score_round([])
        
        assert result.correct == 0
        assert result.total == 0
        assert result.accuracy == 0.0
        assert result.wpm == 0.0
        assert result.score == 0

    def test_perfect_round(self):
        """Test scoring a perfect round (10/10)."""
        items = [
            GameItem(word_id=i, correct=True, time_ms=2000)
            for i in range(1, 11)
        ]
        
        result = score_round(items, duration_sec=60)
        
        assert result.correct == 10
        assert result.total == 10
        assert result.accuracy == 100.0
        assert result.wpm == 10.0  # 10 words in 1 minute
        assert result.score > 1000  # Base score + accuracy bonus + speed bonus

    def test_all_wrong_round(self):
        """Test scoring when all answers are wrong (0/10)."""
        items = [
            GameItem(word_id=i, correct=False, time_ms=5000)
            for i in range(1, 11)
        ]
        
        result = score_round(items, duration_sec=60)
        
        assert result.correct == 0
        assert result.total == 10
        assert result.accuracy == 0.0
        assert result.wpm == 10.0  # 10 words in 1 minute
        assert result.score == 0  # No points for incorrect answers

    def test_mixed_performance(self):
        """Test scoring with mixed correct/incorrect answers."""
        items = [
            GameItem(word_id=1, correct=True, time_ms=2000),   # Fast correct
            GameItem(word_id=2, correct=True, time_ms=4000),   # Medium correct
            GameItem(word_id=3, correct=False, time_ms=6000),  # Slow incorrect
            GameItem(word_id=4, correct=True, time_ms=1500),   # Very fast correct
            GameItem(word_id=5, correct=False, time_ms=8000),  # Very slow incorrect
        ]
        
        result = score_round(items, duration_sec=60)
        
        assert result.correct == 3
        assert result.total == 5
        assert result.accuracy == 60.0
        assert result.wpm == 5.0  # 5 words in 1 minute
        
        # Check score components
        base_score = 3 * 100  # 300 points for 3 correct
        assert result.score >= base_score  # Should have some bonuses

    def test_speed_bonus_calculation(self):
        """Test that speed bonuses are calculated correctly."""
        items = [
            GameItem(word_id=1, correct=True, time_ms=1000),   # Under 3s: +25 bonus
            GameItem(word_id=2, correct=True, time_ms=4000),   # Under 5s: +10 bonus
            GameItem(word_id=3, correct=True, time_ms=6000),   # Over 5s: no bonus
            GameItem(word_id=4, correct=False, time_ms=1000),  # Fast but wrong: no bonus
        ]
        
        result = score_round(items, duration_sec=60)
        
        assert result.correct == 3
        base_score = 3 * 100  # 300 base points
        accuracy_bonus = int(base_score * 0.75 * 0.5)  # 75% accuracy bonus
        speed_bonus = 25 + 10  # Fast bonuses for first two items
        
        expected_score = base_score + accuracy_bonus + speed_bonus
        assert result.score == expected_score

    def test_wpm_calculation_no_duration(self):
        """Test WPM calculation when no duration is provided."""
        items = [
            GameItem(word_id=1, correct=True, time_ms=30000),   # 30 seconds
            GameItem(word_id=2, correct=True, time_ms=30000),   # 30 seconds
        ]
        
        result = score_round(items)  # No duration_sec provided
        
        assert result.wpm == 2.0  # 2 words in 1 minute (60000ms total)

    def test_wpm_with_zero_time(self):
        """Test WPM calculation edge case with zero time."""
        items = [
            GameItem(word_id=1, correct=True, time_ms=0),
            GameItem(word_id=2, correct=True, time_ms=0),
        ]
        
        result = score_round(items, duration_sec=0)
        
        # Should handle division by zero gracefully
        assert result.wpm == 0.0

    def test_accuracy_calculation_edge_cases(self):
        """Test accuracy calculation with edge cases."""
        # Single item correct
        single_correct = [GameItem(word_id=1, correct=True, time_ms=3000)]
        result = score_round(single_correct)
        assert result.accuracy == 100.0
        
        # Single item incorrect
        single_incorrect = [GameItem(word_id=1, correct=False, time_ms=3000)]
        result = score_round(single_incorrect)
        assert result.accuracy == 0.0


class TestScoreRoundFromDict:
    """Test the dictionary interface for scoring."""

    def test_score_from_dict_basic(self):
        """Test scoring from dictionary data."""
        items_data = [
            {"word_id": 1, "correct": True, "time_ms": 2000},
            {"word_id": 2, "correct": False, "time_ms": 5000},
            {"word_id": 3, "correct": True, "time_ms": 3000},
        ]
        
        result = score_round_from_dict(items_data, duration_sec=60)
        
        assert isinstance(result, dict)
        assert result["correct"] == 2
        assert result["total"] == 3
        assert result["accuracy"] == pytest.approx(66.67, abs=0.1)
        assert result["wpm"] == 3.0
        assert result["score"] > 0

    def test_score_from_dict_empty(self):
        """Test scoring empty data."""
        result = score_round_from_dict([])
        
        assert result["correct"] == 0
        assert result["total"] == 0
        assert result["accuracy"] == 0.0
        assert result["wpm"] == 0.0
        assert result["score"] == 0

    def test_score_from_dict_invalid_data(self):
        """Test scoring with missing required fields."""
        with pytest.raises(KeyError):
            # Missing 'correct' field
            items_data = [
                {"word_id": 1, "time_ms": 2000},
            ]
            score_round_from_dict(items_data)

    def test_score_from_dict_performance_metrics(self):
        """Test that performance metrics are calculated correctly."""
        items_data = [
            {"word_id": 1, "correct": True, "time_ms": 1500},   # Very fast
            {"word_id": 2, "correct": True, "time_ms": 2500},   # Fast
            {"word_id": 3, "correct": True, "time_ms": 4500},   # Medium
            {"word_id": 4, "correct": True, "time_ms": 7000},   # Slow
        ]
        
        result = score_round_from_dict(items_data, duration_sec=30)
        
        assert result["correct"] == 4
        assert result["total"] == 4
        assert result["accuracy"] == 100.0
        assert result["wpm"] == 8.0  # 4 words in 0.5 minutes
        
        # Should have speed bonuses for fast answers
        base_score = 4 * 100  # 400 base points
        assert result["score"] > base_score


class TestScoringEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_very_large_round(self):
        """Test scoring a very large round."""
        items = [
            GameItem(word_id=i, correct=i % 2 == 0, time_ms=3000)
            for i in range(1, 101)  # 100 items
        ]
        
        result = score_round(items, duration_sec=300)  # 5 minutes
        
        assert result.total == 100
        assert result.correct == 50  # Every other item correct
        assert result.accuracy == 50.0
        assert result.wpm == 20.0  # 100 words in 5 minutes

    def test_negative_time_handling(self):
        """Test handling of invalid negative times."""
        items = [
            GameItem(word_id=1, correct=True, time_ms=-1000),  # Invalid negative time
            GameItem(word_id=2, correct=True, time_ms=2000),
        ]
        
        # Should not crash with negative times
        result = score_round(items, duration_sec=60)
        assert result.total == 2
        assert result.correct == 2

    def test_very_fast_answers(self):
        """Test bonus calculation for extremely fast answers."""
        items = [
            GameItem(word_id=1, correct=True, time_ms=500),    # 0.5 seconds
            GameItem(word_id=2, correct=True, time_ms=1000),   # 1 second
            GameItem(word_id=3, correct=True, time_ms=2999),   # Just under 3 seconds
        ]
        
        result = score_round(items, duration_sec=60)
        
        # All should get the fast answer bonus
        base_score = 3 * 100
        speed_bonus = 3 * 25  # All under 3 seconds
        accuracy_bonus = int(base_score * 0.5)  # 100% accuracy
        
        expected_score = base_score + accuracy_bonus + speed_bonus
        assert result.score == expected_score

    def test_long_duration_wpm(self):
        """Test WPM calculation with very long durations."""
        items = [GameItem(word_id=1, correct=True, time_ms=1000)]
        
        result = score_round(items, duration_sec=3600)  # 1 hour
        
        assert result.wpm == pytest.approx(0.0167, abs=0.001)  # 1 word in 60 minutes = 0.0167 WPM


if __name__ == "__main__":
    pytest.main([__file__, "-v"])