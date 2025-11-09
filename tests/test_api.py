import copy
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


def backup_activities():
    return copy.deepcopy(activities)


def restore_activities(backup):
    activities.clear()
    activities.update(backup)


def test_get_activities():
    backup = backup_activities()
    try:
        resp = client.get("/activities")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, dict)
        # Check a known activity exists
        assert "Chess Club" in data
    finally:
        restore_activities(backup)


def test_signup_and_duplicate_blocked():
    backup = backup_activities()
    try:
        activity = "Chess Club"
        email = "testuser@example.com"

        # Ensure not present initially
        assert email not in activities[activity]["participants"]

        # Signup should succeed
        resp = client.post(f"/activities/{activity}/signup?email={email}")
        assert resp.status_code == 200
        assert "Signed up" in resp.json().get("message", "")
        assert email in activities[activity]["participants"]

        # Duplicate signup should be rejected
        resp2 = client.post(f"/activities/{activity}/signup?email={email}")
        assert resp2.status_code == 400
        assert "already" in resp2.json().get("detail", "").lower()
    finally:
        restore_activities(backup)


def test_unregister_participant():
    backup = backup_activities()
    try:
        activity = "Programming Class"
        email = "temp-remove@example.com"

        # Add a participant to remove
        activities[activity]["participants"].append(email)
        assert email in activities[activity]["participants"]

        # Remove via DELETE
        resp = client.delete(f"/activities/{activity}/signup?email={email}")
        assert resp.status_code == 200
        assert "Unregistered" in resp.json().get("message", "")
        assert email not in activities[activity]["participants"]

        # Removing non-existent participant returns 404
        resp2 = client.delete(f"/activities/{activity}/signup?email={email}")
        assert resp2.status_code == 404
    finally:
        restore_activities(backup)
