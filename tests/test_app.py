"""FastAPI backend tests for the Mergington High School API.

These tests use the Arrange-Act-Assert pattern and FastAPI's TestClient
for exercising the API endpoints.

Each test resets the in-memory activity state so they can run in isolation.
"""

import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

# Keep a stable baseline so tests can reset state between runs
_ORIGINAL_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities_state():
    """Reset the in-memory activities dictionary before each test."""
    activities.clear()
    activities.update(copy.deepcopy(_ORIGINAL_ACTIVITIES))
    yield


@pytest.fixture
def client():
    """Provide a fresh TestClient instance for each test."""
    return TestClient(app)


class TestGetActivities:
    def test_get_activities_returns_initial_activities(self, client):
        # Arrange

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert data["Chess Club"]["participants"] == [
            "michael@mergington.edu",
            "daniel@mergington.edu",
        ]


class TestPostSignup:
    def test_post_signup_adds_participant(self, client):
        # Arrange
        activity_name = "Chess Club"
        new_email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email},
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {new_email} for {activity_name}"
        assert new_email in activities[activity_name]["participants"]

    def test_post_signup_twice_returns_400(self, client):
        # Arrange
        activity_name = "Chess Club"
        new_email = "double@mergington.edu"
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email},
        )

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email},
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]


class TestDeleteParticipant:
    def test_delete_participant_removes_participant(self, client):
        # Arrange
        activity_name = "Chess Club"
        new_email = "remove@mergington.edu"
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email},
        )
        assert new_email in activities[activity_name]["participants"]

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": new_email},
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Removed {new_email} from {activity_name}"
        assert new_email not in activities[activity_name]["participants"]

    def test_delete_nonexistent_participant_returns_404(self, client):
        # Arrange
        activity_name = "Programming Class"
        missing_email = "missing@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": missing_email},
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
