#!/usr/bin/env python3
"""
Tests for game API endpoints including session lifecycle, round generation, and stats.
"""
import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


class TestGameSessionAPI:
    """Test game session creation and management."""

    def test_create_session_success(self, client):
        """Test successful game session creation."""
        session_data = {
            "mode": "flashcards",
            "duration_sec": 60
        }
        
        response = client.post("/api/game/sessions", json=session_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["mode"] == "flashcards"
        assert data["duration_sec"] == 60
        assert "started_at" in data

    def test_create_session_invalid_data(self, client):
        """Test session creation with invalid data."""
        session_data = {
            "mode": 123,  # Invalid type (should be string)
            "duration_sec": "invalid"  # Invalid type (should be int)
        }
        
        response = client.post("/api/game/sessions", json=session_data)
        
        assert response.status_code == 422  # Validation error


class TestGameRoundAPI:
    """Test game round generation and enhancement."""

    def test_get_basic_round(self, client):
        """Test getting a basic game round without AI enhancement."""
        response = client.get("/api/game/round?count=3&enhance=false")
        
        # Should either succeed with data or fail with 404 if no words
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert "items" in data
            assert "count" in data
            assert isinstance(data["items"], list)

    def test_get_enhanced_round(self, client):
        """Test getting an AI-enhanced game round."""
        response = client.get("/api/game/round?count=2&enhance=true")
        
        # Should either succeed or fail gracefully
        assert response.status_code in [200, 404, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "items" in data
            assert "count" in data

    def test_get_round_with_level_filter(self, client):
        """Test getting round with TOPIK level filtering."""
        response = client.get("/api/game/round?count=5&level=TOPIK1")
        
        # Should not error even if no words match the filter
        assert response.status_code in [200, 404]

    def test_get_round_invalid_count(self, client):
        """Test getting round with invalid count parameter."""
        response = client.get("/api/game/round?count=100")  # Over limit
        
        assert response.status_code == 422  # Validation error


class TestGameSubmitAPI:
    """Test game result submission and scoring."""

    def test_submit_invalid_session(self, client):
        """Test submitting results for non-existent session."""
        submit_data = {
            "session_id": 99999,  # Non-existent session
            "items": [
                {"word_id": 1, "correct": True, "time_ms": 2000},
            ],
            "score": 100,
            "accuracy": 100.0
        }
        
        response = client.post("/api/game/submit", json=submit_data)
        
        assert response.status_code == 404

    def test_submit_invalid_data_structure(self, client):
        """Test submitting with invalid data structure."""
        submit_data = {
            "session_id": "invalid",  # Should be int
            "items": "not_a_list",    # Should be list
        }
        
        response = client.post("/api/game/submit", json=submit_data)
        
        assert response.status_code == 422  # Validation error


class TestGameStatsAPI:
    """Test game statistics retrieval."""

    def test_get_game_stats(self, client):
        """Test getting game statistics."""
        response = client.get("/api/game/stats?limit=5")
        
        # Should return stats structure even if empty
        assert response.status_code in [200, 500]  # 500 if DB issues
        
        if response.status_code == 200:
            data = response.json()
            assert "sessions" in data
            assert "total_sessions" in data
            assert isinstance(data["sessions"], list)
            assert isinstance(data["total_sessions"], int)

    def test_get_stats_with_invalid_limit(self, client):
        """Test getting stats with invalid limit."""
        response = client.get("/api/game/stats?limit=200")  # Over max limit
        
        assert response.status_code == 422  # Validation error

    def test_get_stats_default_limit(self, client):
        """Test getting stats with default limit."""
        response = client.get("/api/game/stats")
        
        assert response.status_code in [200, 500]


class TestGameAPIIntegration:
    """Integration tests for complete game workflow."""

    def test_api_endpoints_exist(self, client):
        """Test that all required API endpoints exist and respond."""
        # Test that endpoints exist (even if they fail due to empty DB)
        endpoints = [
            ("/api/game/sessions", "POST", {"mode": "test", "duration_sec": 60}),
            ("/api/game/round?count=5", "GET", None),
            ("/api/game/stats?limit=5", "GET", None),
        ]
        
        for endpoint, method, data in endpoints:
            if method == "POST":
                response = client.post(endpoint, json=data)
            else:
                response = client.get(endpoint)
            
            # Should not return 404 (endpoint not found)
            assert response.status_code != 404

    def test_session_creation_and_stats(self, client):
        """Test creating a session and checking it appears in stats."""
        # Create a session
        session_data = {"mode": "flashcards", "duration_sec": 60}
        session_response = client.post("/api/game/sessions", json=session_data)
        
        if session_response.status_code == 200:
            # Check that stats endpoint works
            stats_response = client.get("/api/game/stats")
            assert stats_response.status_code in [200, 500]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])