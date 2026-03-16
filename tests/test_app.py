from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_activities_returns_initial_data():
    # Arrange
    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert "Chess Club" in body
    assert body["Chess Club"]["max_participants"] == 12


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]

    # Verify the new participant is in activity
    response2 = client.get("/activities")
    assert email in response2.json()[activity_name]["participants"]


def test_signup_duplicate_participant_returns_400():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()


def test_signup_capacity_limit_returns_400():
    # Arrange
    activity_name = "Mathletes"
    activity_data = client.get("/activities").json()[activity_name]
    existing = len(activity_data["participants"])
    max_participants = activity_data["max_participants"]

    for i in range(max_participants - existing):
        client.post(f"/activities/{activity_name}/signup", params={"email": f"student{i}@mergington.edu"})

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": "overflow@mergington.edu"})

    # Assert
    assert response.status_code == 400
    assert "maximum capacity" in response.json()["detail"].lower()


def test_remove_participant_success():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 200
    assert "Removed" in response.json()["message"]

    response2 = client.get("/activities")
    assert email not in response2.json()[activity_name]["participants"]


def test_remove_nonexistent_participant_returns_404():
    # Arrange
    activity_name = "Chess Club"
    email = "nobody@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 404
