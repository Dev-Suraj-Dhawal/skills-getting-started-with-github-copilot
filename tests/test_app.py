from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def client():
    return TestClient(app_module.app)


@pytest.fixture
def activities():
    original_activities = deepcopy(app_module.activities)
    yield app_module.activities
    app_module.activities.clear()
    app_module.activities.update(original_activities)


def test_get_activities_returns_activity_details(client, activities):
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert expected_activity in response.json()
    assert response.json()[expected_activity]["participants"] == activities[expected_activity]["participants"]


def test_signup_adds_participant(client, activities):
    # Arrange
    activity = "Art Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity}"}
    assert email in activities[activity]["participants"]


def test_signup_returns_not_found_for_unknown_activity(client):
    # Arrange
    activity = "Unknown Activity"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_rejects_duplicate_participant(client, activities):
    # Arrange
    activity = "Chess Club"
    email = activities[activity]["participants"][0]

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}


def test_unregister_removes_participant(client, activities):
    # Arrange
    activity = "Art Club"
    email = "student@mergington.edu"
    activities[activity]["participants"].append(email)

    # Act
    response = client.delete(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity}"}
    assert email not in activities[activity]["participants"]


def test_unregister_returns_not_found_for_unknown_activity(client):
    # Arrange
    activity = "Unknown Activity"
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_returns_not_found_for_unsigned_participant(client):
    # Arrange
    activity = "Art Club"
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Student is not signed up for this activity"}
