from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def test_root_redirects_to_static_index():
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_activity_details():
    response = client.get("/activities")

    assert response.status_code == 200
    activities = response.json()
    assert "Chess Club" in activities
    assert activities["Chess Club"]["max_participants"] == 12
    assert "michael@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_adds_student_to_activity():
    response = client.post(
        "/activities/Soccer Club/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Signed up student@mergington.edu for Soccer Club"
    }
    activities = client.get("/activities").json()
    assert "student@mergington.edu" in activities["Soccer Club"]["participants"]


def test_signup_rejects_duplicate_participant():
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "michael@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_signup_rejects_unknown_activity():
    response = client.post(
        "/activities/Unknown Club/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_participant_removes_email_from_activity():
    response = client.delete(
        "/activities/Chess Club/participants/michael%40mergington.edu"
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Unregistered michael@mergington.edu from Chess Club"

    activities = client.get("/activities").json()
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


def test_unregister_participant_fails_when_not_signed_up():
    response = client.delete(
        "/activities/Chess Club/participants/ghost%40mergington.edu"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in activity"


def test_unregister_rejects_unknown_activity():
    response = client.delete(
        "/activities/Unknown Club/participants/student%40mergington.edu"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"