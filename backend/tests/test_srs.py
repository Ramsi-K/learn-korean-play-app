#!/usr/bin/env python3
"""
Tests for SRS (Spaced Repetition System) scheduling logic.
Tests that schedules move forward on correct answers and reset on wrong answers.
"""
import pytest
from datetime import datetime, timedelta
from tools.srs import SRSScheduler, ReviewSchedule, schedule_review_from_dict


class TestSRSScheduler:
    """Test the SRS scheduler functionality."""

    def setUp(self):
        self.scheduler = SRSScheduler()

    def test_new_word_schedule(self):
        """Test scheduling for a brand new word."""
        scheduler = SRSScheduler()
        word_id = 1
        
        schedule = scheduler.schedule_review(word_id, True)
        
        assert schedule.word_id == word_id
        assert schedule.interval_days == 1  # First interval
        assert schedule.ease_factor == scheduler.DEFAULT_EASE_FACTOR
        assert schedule.repetitions == 0
        assert isinstance(schedule.next_review, datetime)
        assert isinstance(schedule.last_reviewed, datetime)

    def test_correct_answer_progression(self):
        """Test that correct answers increase intervals properly."""
        scheduler = SRSScheduler()
        word_id = 1
        
        # First review (new word)
        schedule1 = scheduler.schedule_review(word_id, True)
        assert schedule1.interval_days == 1
        assert schedule1.repetitions == 0
        
        # Second review (correct)
        schedule2 = scheduler.schedule_review(word_id, True, schedule1)
        assert schedule2.interval_days == 1  # Still first interval
        assert schedule2.repetitions == 1
        
        # Third review (correct)
        schedule3 = scheduler.schedule_review(word_id, True, schedule2)
        assert schedule3.interval_days == 6  # Second fixed interval
        assert schedule3.repetitions == 2
        
        # Fourth review (correct) - now using SM-2 formula
        schedule4 = scheduler.schedule_review(word_id, True, schedule3)
        expected_interval = int(6 * schedule3.ease_factor)
        assert schedule4.interval_days == expected_interval
        assert schedule4.repetitions == 3
        assert schedule4.ease_factor > schedule3.ease_factor  # Should increase

    def test_incorrect_answer_reset(self):
        """Test that incorrect answers reset the schedule."""
        scheduler = SRSScheduler()
        word_id = 1
        
        # Build up some progress
        schedule1 = scheduler.schedule_review(word_id, True)
        schedule2 = scheduler.schedule_review(word_id, True, schedule1)
        schedule3 = scheduler.schedule_review(word_id, True, schedule2)
        
        # Now get one wrong
        schedule4 = scheduler.schedule_review(word_id, False, schedule3)
        
        assert schedule4.interval_days == 1  # Reset to first interval
        assert schedule4.repetitions == 0  # Reset repetitions
        assert schedule4.ease_factor < schedule3.ease_factor  # Should decrease

    def test_ease_factor_bounds(self):
        """Test that ease factor stays within bounds."""
        scheduler = SRSScheduler()
        word_id = 1
        
        # Start with minimum ease factor
        schedule = ReviewSchedule(
            word_id=word_id,
            next_review=datetime.utcnow(),
            interval_days=1,
            ease_factor=scheduler.MIN_EASE_FACTOR,
            repetitions=5,
            last_reviewed=datetime.utcnow(),
        )
        
        # Multiple wrong answers shouldn't go below minimum
        for _ in range(5):
            schedule = scheduler.schedule_review(word_id, False, schedule)
        
        assert schedule.ease_factor >= scheduler.MIN_EASE_FACTOR
        
        # Start with maximum ease factor
        schedule = ReviewSchedule(
            word_id=word_id,
            next_review=datetime.utcnow(),
            interval_days=30,
            ease_factor=scheduler.MAX_EASE_FACTOR,
            repetitions=10,
            last_reviewed=datetime.utcnow(),
        )
        
        # Multiple correct answers shouldn't go above maximum
        for _ in range(5):
            schedule = scheduler.schedule_review(word_id, True, schedule)
        
        assert schedule.ease_factor <= scheduler.MAX_EASE_FACTOR

    def test_get_due_words(self):
        """Test getting words that are due for review."""
        scheduler = SRSScheduler()
        now = datetime.utcnow()
        
        schedules = [
            # Due yesterday (overdue)
            ReviewSchedule(
                word_id=1, next_review=now - timedelta(days=1),
                interval_days=1, ease_factor=2.5, repetitions=1,
                last_reviewed=now - timedelta(days=2)
            ),
            # Due now
            ReviewSchedule(
                word_id=2, next_review=now,
                interval_days=1, ease_factor=2.5, repetitions=1,
                last_reviewed=now - timedelta(days=1)
            ),
            # Due tomorrow (not due yet)
            ReviewSchedule(
                word_id=3, next_review=now + timedelta(days=1),
                interval_days=2, ease_factor=2.5, repetitions=2,
                last_reviewed=now
            ),
        ]
        
        due_words = scheduler.get_due_words(schedules)
        
        assert len(due_words) == 2  # Only first two are due
        assert due_words[0].word_id == 1  # Most overdue first
        assert due_words[1].word_id == 2

    def test_get_due_words_with_limit(self):
        """Test getting due words with a limit."""
        scheduler = SRSScheduler()
        now = datetime.utcnow()
        
        schedules = [
            ReviewSchedule(
                word_id=i, next_review=now - timedelta(hours=i),
                interval_days=1, ease_factor=2.5, repetitions=1,
                last_reviewed=now - timedelta(days=1)
            )
            for i in range(1, 6)  # 5 overdue words
        ]
        
        due_words = scheduler.get_due_words(schedules, limit=3)
        
        assert len(due_words) == 3
        # Should be ordered by most overdue (highest i value first)
        assert due_words[0].word_id == 5
        assert due_words[1].word_id == 4
        assert due_words[2].word_id == 3

    def test_calculate_retention_rate(self):
        """Test retention rate calculation based on ease factors."""
        scheduler = SRSScheduler()
        
        # High ease factors (good retention)
        good_schedules = [
            ReviewSchedule(
                word_id=i, next_review=datetime.utcnow(),
                interval_days=10, ease_factor=3.5, repetitions=5,
                last_reviewed=datetime.utcnow()
            )
            for i in range(1, 6)
        ]
        
        good_retention = scheduler.calculate_retention_rate(good_schedules)
        assert good_retention > 0.8  # Should be high
        
        # Low ease factors (poor retention)
        poor_schedules = [
            ReviewSchedule(
                word_id=i, next_review=datetime.utcnow(),
                interval_days=1, ease_factor=1.3, repetitions=0,
                last_reviewed=datetime.utcnow()
            )
            for i in range(1, 6)
        ]
        
        poor_retention = scheduler.calculate_retention_rate(poor_schedules)
        assert poor_retention < 0.7  # Should be low
        
        # Empty schedules
        empty_retention = scheduler.calculate_retention_rate([])
        assert empty_retention == 0.0


class TestScheduleReviewFromDict:
    """Test the dictionary interface for SRS scheduling."""

    def test_new_word_from_dict(self):
        """Test scheduling a new word using dictionary interface."""
        word_id = 1
        
        result = schedule_review_from_dict(word_id, True)
        
        assert isinstance(result, dict)
        assert result["word_id"] == word_id
        assert result["interval_days"] == 1
        assert result["ease_factor"] == 2.5
        assert result["repetitions"] == 0
        assert "next_review" in result
        assert "last_reviewed" in result

    def test_existing_word_from_dict(self):
        """Test updating an existing word schedule using dictionary interface."""
        word_id = 1
        
        # Create initial schedule
        current_schedule = {
            "word_id": word_id,
            "next_review": datetime.utcnow().isoformat(),
            "interval_days": 1,
            "ease_factor": 2.5,
            "repetitions": 0,
            "last_reviewed": datetime.utcnow().isoformat(),
        }
        
        # Update with correct answer
        result = schedule_review_from_dict(word_id, True, current_schedule)
        
        assert result["word_id"] == word_id
        assert result["repetitions"] == 1  # Should increment
        assert result["ease_factor"] >= current_schedule["ease_factor"]  # Should increase

    def test_wrong_answer_reset_from_dict(self):
        """Test that wrong answers reset schedule via dictionary interface."""
        word_id = 1
        
        # Advanced schedule
        advanced_schedule = {
            "word_id": word_id,
            "next_review": datetime.utcnow().isoformat(),
            "interval_days": 15,
            "ease_factor": 3.0,
            "repetitions": 5,
            "last_reviewed": datetime.utcnow().isoformat(),
        }
        
        # Wrong answer should reset
        result = schedule_review_from_dict(word_id, False, advanced_schedule)
        
        assert result["interval_days"] == 1  # Reset to first interval
        assert result["repetitions"] == 0  # Reset repetitions
        assert result["ease_factor"] < advanced_schedule["ease_factor"]  # Decreased

    def test_datetime_serialization(self):
        """Test that datetime fields are properly serialized."""
        word_id = 1
        
        result = schedule_review_from_dict(word_id, True)
        
        # Should be able to parse the datetime strings
        next_review = datetime.fromisoformat(result["next_review"])
        last_reviewed = datetime.fromisoformat(result["last_reviewed"])
        
        assert isinstance(next_review, datetime)
        assert isinstance(last_reviewed, datetime)
        assert next_review > last_reviewed  # Next review should be in the future

    def test_schedule_consistency(self):
        """Test that multiple updates maintain consistency."""
        word_id = 1
        schedule_dict = None
        
        # Simulate 10 correct answers in a row
        for i in range(10):
            schedule_dict = schedule_review_from_dict(word_id, True, schedule_dict)
            
            # Verify consistency
            assert schedule_dict["word_id"] == word_id
            assert schedule_dict["repetitions"] == i
            assert schedule_dict["interval_days"] >= 1
            assert schedule_dict["ease_factor"] >= SRSScheduler.MIN_EASE_FACTOR
            assert schedule_dict["ease_factor"] <= SRSScheduler.MAX_EASE_FACTOR

    def test_alternating_performance(self):
        """Test schedule behavior with alternating correct/incorrect answers."""
        word_id = 1
        schedule_dict = None
        
        results = [True, False, True, False, True, True]
        
        for i, correct in enumerate(results):
            schedule_dict = schedule_review_from_dict(word_id, correct, schedule_dict)
            
            if correct:
                # Correct answers should maintain or increase ease factor
                assert schedule_dict["ease_factor"] >= SRSScheduler.MIN_EASE_FACTOR
            else:
                # Wrong answers should reset repetitions
                assert schedule_dict["repetitions"] == 0
                assert schedule_dict["interval_days"] == 1


class TestSRSIntegration:
    """Integration tests for SRS system."""

    def test_realistic_learning_progression(self):
        """Test a realistic learning progression for a word."""
        scheduler = SRSScheduler()
        word_id = 123
        
        # Learning progression: mostly correct with occasional mistakes
        performance = [True, True, False, True, True, True, False, True, True, True]
        
        schedule = None
        
        for i, correct in enumerate(performance):
            schedule = scheduler.schedule_review(word_id, correct, schedule)
            
            # Log progression for manual verification
            print(f"Review {i+1}: {'✓' if correct else '✗'} -> "
                  f"Interval: {schedule.interval_days}d, "
                  f"Ease: {schedule.ease_factor:.2f}, "
                  f"Reps: {schedule.repetitions}")
        
        # After this progression, word should have reasonable parameters
        assert schedule.interval_days >= 1
        assert schedule.ease_factor >= scheduler.MIN_EASE_FACTOR
        assert schedule.ease_factor <= scheduler.MAX_EASE_FACTOR

    def test_difficult_word_scenario(self):
        """Test a word that's consistently difficult (many wrong answers)."""
        scheduler = SRSScheduler()
        word_id = 456
        
        # Difficult word: mostly wrong answers
        performance = [False, False, True, False, False, True, False, True, False]
        
        schedule = None
        
        for correct in performance:
            schedule = scheduler.schedule_review(word_id, correct, schedule)
        
        # Difficult word should have low ease factor and short intervals
        assert schedule.ease_factor <= scheduler.DEFAULT_EASE_FACTOR
        assert schedule.interval_days <= 6  # Shouldn't progress too far

    def test_easy_word_scenario(self):
        """Test a word that's consistently easy (all correct answers)."""
        scheduler = SRSScheduler()
        word_id = 789
        
        # Easy word: all correct answers
        performance = [True] * 8
        
        schedule = None
        
        for correct in performance:
            schedule = scheduler.schedule_review(word_id, correct, schedule)
        
        # Easy word should have high ease factor and long intervals
        assert schedule.ease_factor >= scheduler.DEFAULT_EASE_FACTOR
        assert schedule.repetitions == 7  # Should have progressed
        assert schedule.interval_days > 6  # Should have long intervals

    def test_schedule_dates_are_future(self):
        """Test that next review dates are always in the future."""
        scheduler = SRSScheduler()
        now = datetime.utcnow()
        
        # Test new word
        schedule = scheduler.schedule_review(1, True)
        assert schedule.next_review > now
        
        # Test existing word
        existing_schedule = ReviewSchedule(
            word_id=1,
            next_review=now - timedelta(days=1),  # Overdue
            interval_days=1,
            ease_factor=2.5,
            repetitions=1,
            last_reviewed=now - timedelta(days=2),
        )
        
        new_schedule = scheduler.schedule_review(1, True, existing_schedule)
        assert new_schedule.next_review > now

    def test_interval_progression_formula(self):
        """Test that interval progression follows expected SM-2 formula."""
        scheduler = SRSScheduler()
        
        # Create a schedule at the point where SM-2 formula kicks in
        schedule = ReviewSchedule(
            word_id=1,
            next_review=datetime.utcnow(),
            interval_days=6,  # Second fixed interval
            ease_factor=2.5,
            repetitions=2,
            last_reviewed=datetime.utcnow(),
        )
        
        # Next correct answer should use formula
        new_schedule = scheduler.schedule_review(1, True, schedule)
        
        expected_interval = int(6 * 2.5)  # 15 days
        assert new_schedule.interval_days == expected_interval
        assert new_schedule.repetitions == 3

    def test_multiple_words_due_ordering(self):
        """Test that due words are returned in correct order."""
        scheduler = SRSScheduler()
        now = datetime.utcnow()
        
        schedules = [
            # Word 1: due 2 hours ago (most overdue)
            ReviewSchedule(
                word_id=1, next_review=now - timedelta(hours=2),
                interval_days=1, ease_factor=2.5, repetitions=1,
                last_reviewed=now - timedelta(days=1)
            ),
            # Word 2: due 1 hour ago
            ReviewSchedule(
                word_id=2, next_review=now - timedelta(hours=1),
                interval_days=1, ease_factor=2.5, repetitions=1,
                last_reviewed=now - timedelta(days=1)
            ),
            # Word 3: due 30 minutes ago
            ReviewSchedule(
                word_id=3, next_review=now - timedelta(minutes=30),
                interval_days=1, ease_factor=2.5, repetitions=1,
                last_reviewed=now - timedelta(days=1)
            ),
        ]
        
        due_words = scheduler.get_due_words(schedules)
        
        # Should be ordered by most overdue first
        assert len(due_words) == 3
        assert due_words[0].word_id == 1  # 2 hours overdue
        assert due_words[1].word_id == 2  # 1 hour overdue
        assert due_words[2].word_id == 3  # 30 minutes overdue


class TestScheduleReviewFromDict:
    """Test the dictionary interface for SRS scheduling."""

    def test_dict_interface_new_word(self):
        """Test dictionary interface for new word."""
        result = schedule_review_from_dict(1, True)
        
        assert isinstance(result, dict)
        required_keys = ["word_id", "next_review", "interval_days", 
                        "ease_factor", "repetitions", "last_reviewed"]
        for key in required_keys:
            assert key in result

    def test_dict_interface_existing_word(self):
        """Test dictionary interface for existing word."""
        existing_dict = {
            "word_id": 1,
            "next_review": datetime.utcnow().isoformat(),
            "interval_days": 6,
            "ease_factor": 2.5,
            "repetitions": 2,
            "last_reviewed": datetime.utcnow().isoformat(),
        }
        
        result = schedule_review_from_dict(1, True, existing_dict)
        
        assert result["word_id"] == 1
        assert result["repetitions"] == 3  # Should increment
        assert result["interval_days"] > 6  # Should increase

    def test_dict_datetime_handling(self):
        """Test that datetime strings are handled correctly."""
        # Test with current datetime
        now_str = datetime.utcnow().isoformat()
        
        existing_dict = {
            "word_id": 1,
            "next_review": now_str,
            "interval_days": 1,
            "ease_factor": 2.5,
            "repetitions": 0,
            "last_reviewed": now_str,
        }
        
        result = schedule_review_from_dict(1, True, existing_dict)
        
        # Should be able to parse and update the datetime
        new_review_time = datetime.fromisoformat(result["next_review"])
        last_reviewed_time = datetime.fromisoformat(result["last_reviewed"])
        
        assert isinstance(new_review_time, datetime)
        assert isinstance(last_reviewed_time, datetime)
        assert new_review_time > last_reviewed_time


class TestSRSEdgeCases:
    """Test edge cases and error handling."""

    def test_none_schedule_handling(self):
        """Test handling of None schedule (new word)."""
        result = schedule_review_from_dict(1, True, None)
        
        assert result["word_id"] == 1
        assert result["repetitions"] == 0
        assert result["interval_days"] == 1

    def test_empty_schedules_list(self):
        """Test handling of empty schedules list."""
        scheduler = SRSScheduler()
        
        due_words = scheduler.get_due_words([])
        assert due_words == []
        
        retention = scheduler.calculate_retention_rate([])
        assert retention == 0.0

    def test_invalid_datetime_strings(self):
        """Test handling of invalid datetime strings."""
        invalid_dict = {
            "word_id": 1,
            "next_review": "invalid-datetime",
            "interval_days": 1,
            "ease_factor": 2.5,
            "repetitions": 0,
            "last_reviewed": "also-invalid",
        }
        
        # Should raise ValueError for invalid datetime
        with pytest.raises(ValueError):
            schedule_review_from_dict(1, True, invalid_dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])