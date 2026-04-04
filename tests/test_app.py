"""
test_app.py - ACEest Fitness & Gym Unit Tests
Run with: pytest tests/test_app.py -v
"""

import pytest
import json
import os
import sys

# Ensure the project root is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app, init_db, DB_NAME


# ---------- FIXTURES ----------
@pytest.fixture
def client(tmp_path, monkeypatch):
    """Provide a test Flask client with an isolated temp database."""
    import app as app_module

    test_db = str(tmp_path / "test_aceest.db")
    monkeypatch.setattr(app_module, "DB_NAME", test_db)

    # Patch get_db to use temp DB
    import sqlite3

    def mock_get_db():
        conn = sqlite3.connect(test_db)
        conn.row_factory = sqlite3.Row
        return conn

    monkeypatch.setattr(app_module, "get_db", mock_get_db)

    app_module.init_db()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def post_json(client, url, data):
    return client.post(url, data=json.dumps(data), content_type="application/json")


# ---------- HEALTH & ROOT ----------
class TestHealthEndpoints:
    def test_health_returns_200(self, client):
        r = client.get("/health")
        assert r.status_code == 200

    def test_health_body(self, client):
        r = client.get("/health")
        assert r.get_json()["status"] == "healthy"

    def test_root_returns_200(self, client):
        r = client.get("/")
        assert r.status_code == 200

    def test_root_contains_app_name(self, client):
        r = client.get("/")
        assert "ACEest" in r.get_json()["app"]


# ---------- CLIENT CRUD ----------
class TestClientCreation:
    def test_create_client_success(self, client):
        r = post_json(client, "/clients", {"name": "Alice"})
        assert r.status_code == 201

    def test_create_client_response_message(self, client):
        r = post_json(client, "/clients", {"name": "Bob"})
        assert "Bob" in r.get_json()["message"]

    def test_create_client_missing_name(self, client):
        r = post_json(client, "/clients", {})
        assert r.status_code == 400

    def test_create_client_empty_name(self, client):
        r = post_json(client, "/clients", {"name": "  "})
        assert r.status_code == 400

    def test_create_duplicate_client(self, client):
        post_json(client, "/clients", {"name": "Charlie"})
        r = post_json(client, "/clients", {"name": "Charlie"})
        assert r.status_code == 409

    def test_create_client_with_all_fields(self, client):
        payload = {
            "name": "Dana",
            "age": 30,
            "weight": 75.5,
            "height": 170.0,
            "calories": 2000,
            "membership_status": "Active",
        }
        r = post_json(client, "/clients", payload)
        assert r.status_code == 201


class TestClientRetrieval:
    def test_list_clients_empty(self, client):
        r = client.get("/clients")
        assert r.status_code == 200
        assert r.get_json() == []

    def test_list_clients_returns_created(self, client):
        post_json(client, "/clients", {"name": "Eve"})
        r = client.get("/clients")
        names = [c["name"] for c in r.get_json()]
        assert "Eve" in names

    def test_get_client_by_name(self, client):
        post_json(client, "/clients", {"name": "Frank"})
        r = client.get("/clients/Frank")
        assert r.status_code == 200
        assert r.get_json()["name"] == "Frank"

    def test_get_nonexistent_client(self, client):
        r = client.get("/clients/Ghost")
        assert r.status_code == 404

    def test_get_client_default_membership(self, client):
        post_json(client, "/clients", {"name": "Grace"})
        r = client.get("/clients/Grace")
        assert r.get_json()["membership_status"] == "Active"


class TestClientDeletion:
    def test_delete_client(self, client):
        post_json(client, "/clients", {"name": "Henry"})
        r = client.delete("/clients/Henry")
        assert r.status_code == 200

    def test_delete_removes_client(self, client):
        post_json(client, "/clients", {"name": "Iris"})
        client.delete("/clients/Iris")
        r = client.get("/clients/Iris")
        assert r.status_code == 404

    def test_delete_nonexistent_client(self, client):
        r = client.delete("/clients/Nobody")
        assert r.status_code == 404


# ---------- PROGRAM GENERATOR ----------
class TestProgramGeneration:
    def test_generate_program_valid_client(self, client):
        post_json(client, "/clients", {"name": "Jack"})
        r = post_json(client, "/clients/Jack/program", {})
        assert r.status_code == 200

    def test_generate_program_returns_data(self, client):
        post_json(client, "/clients", {"name": "Kate"})
        r = post_json(client, "/clients/Kate/program", {})
        data = r.get_json()
        assert "program" in data
        assert "program_type" in data

    def test_generate_program_updates_client(self, client):
        post_json(client, "/clients", {"name": "Leo"})
        post_json(client, "/clients/Leo/program", {})
        r = client.get("/clients/Leo")
        assert r.get_json()["program"] is not None

    def test_generate_program_invalid_client(self, client):
        r = post_json(client, "/clients/NoOne/program", {})
        assert r.status_code == 404


# ---------- WORKOUTS ----------
class TestWorkouts:
    def test_add_workout_success(self, client):
        post_json(client, "/clients", {"name": "Mia"})
        r = post_json(client, "/clients/Mia/workouts", {
            "workout_type": "Strength", "duration_min": 60
        })
        assert r.status_code == 201

    def test_add_workout_missing_type(self, client):
        post_json(client, "/clients", {"name": "Ned"})
        r = post_json(client, "/clients/Ned/workouts", {"duration_min": 45})
        assert r.status_code == 400

    def test_list_workouts_empty(self, client):
        post_json(client, "/clients", {"name": "Olivia"})
        r = client.get("/clients/Olivia/workouts")
        assert r.status_code == 200
        assert r.get_json() == []

    def test_list_workouts_after_add(self, client):
        post_json(client, "/clients", {"name": "Paul"})
        post_json(client, "/clients/Paul/workouts", {
            "workout_type": "Cardio", "duration_min": 30
        })
        r = client.get("/clients/Paul/workouts")
        assert len(r.get_json()) == 1

    def test_workout_invalid_client(self, client):
        r = client.get("/clients/Ghost/workouts")
        assert r.status_code == 404

    def test_workout_stores_type(self, client):
        post_json(client, "/clients", {"name": "Quinn"})
        post_json(client, "/clients/Quinn/workouts", {
            "workout_type": "Mobility", "duration_min": 20
        })
        r = client.get("/clients/Quinn/workouts")
        assert r.get_json()[0]["workout_type"] == "Mobility"


# ---------- PROGRESS ----------
class TestProgress:
    def test_add_progress_success(self, client):
        post_json(client, "/clients", {"name": "Rita"})
        r = post_json(client, "/clients/Rita/progress", {
            "week": "2025-W01", "adherence": 80
        })
        assert r.status_code == 201

    def test_add_progress_missing_week(self, client):
        post_json(client, "/clients", {"name": "Sam"})
        r = post_json(client, "/clients/Sam/progress", {"adherence": 70})
        assert r.status_code == 400

    def test_add_progress_invalid_adherence_high(self, client):
        post_json(client, "/clients", {"name": "Tina"})
        r = post_json(client, "/clients/Tina/progress", {
            "week": "2025-W02", "adherence": 150
        })
        assert r.status_code == 400

    def test_list_progress_empty(self, client):
        post_json(client, "/clients", {"name": "Uma"})
        r = client.get("/clients/Uma/progress")
        assert r.status_code == 200
        assert r.get_json() == []

    def test_list_progress_after_add(self, client):
        post_json(client, "/clients", {"name": "Vera"})
        post_json(client, "/clients/Vera/progress", {
            "week": "2025-W03", "adherence": 90
        })
        r = client.get("/clients/Vera/progress")
        assert len(r.get_json()) == 1

    def test_progress_invalid_client(self, client):
        r = client.get("/clients/Ghost/progress")
        assert r.status_code == 404

    def test_progress_adherence_boundary_zero(self, client):
        post_json(client, "/clients", {"name": "Walt"})
        r = post_json(client, "/clients/Walt/progress", {
            "week": "2025-W04", "adherence": 0
        })
        assert r.status_code == 201

    def test_progress_adherence_boundary_hundred(self, client):
        post_json(client, "/clients", {"name": "Xena"})
        r = post_json(client, "/clients/Xena/progress", {
            "week": "2025-W05", "adherence": 100
        })
        assert r.status_code == 201
