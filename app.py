"""
ACEest Fitness & Gym - Flask Web Application
DevOps Assignment 1 - CSIZG514/SEZG514
"""

from flask import Flask, jsonify, request, abort
import sqlite3
import os
import random
from datetime import date

app = Flask(__name__)

DB_NAME = os.environ.get("DB_PATH", "aceest_fitness.db")

PROGRAM_TEMPLATES = {
    "Fat Loss": ["Full Body HIIT", "Circuit Training", "Cardio + Weights"],
    "Muscle Gain": ["Push/Pull/Legs", "Upper/Lower Split", "Full Body Strength"],
    "Beginner": ["Full Body 3x/week", "Light Strength + Mobility"],
}

# ---------- DATABASE ----------
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            age INTEGER,
            height REAL,
            weight REAL,
            program TEXT,
            calories INTEGER,
            target_weight REAL,
            membership_status TEXT DEFAULT 'Active',
            membership_end TEXT
        );

        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            date TEXT NOT NULL,
            workout_type TEXT,
            duration_min INTEGER,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            week TEXT NOT NULL,
            adherence INTEGER
        );
    """)
    conn.commit()
    conn.close()


# ---------- ROOT ----------
@app.route("/")
def index():
    return jsonify({
        "app": "ACEest Fitness & Gym API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": [
            "GET  /health",
            "GET  /clients",
            "POST /clients",
            "GET  /clients/<name>",
            "DELETE /clients/<name>",
            "POST /clients/<name>/program",
            "GET  /clients/<name>/workouts",
            "POST /clients/<name>/workouts",
            "GET  /clients/<name>/progress",
            "POST /clients/<name>/progress",
        ]
    })


@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200


# ---------- CLIENTS ----------
@app.route("/clients", methods=["GET"])
def list_clients():
    conn = get_db()
    rows = conn.execute("SELECT * FROM clients ORDER BY name").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows]), 200


@app.route("/clients", methods=["POST"])
def create_client():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "name is required"}), 400

    conn = get_db()
    try:
        conn.execute(
            """INSERT INTO clients (name, age, height, weight, calories,
               target_weight, membership_status, membership_end)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                name,
                data.get("age"),
                data.get("height"),
                data.get("weight"),
                data.get("calories"),
                data.get("target_weight"),
                data.get("membership_status", "Active"),
                data.get("membership_end"),
            ),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": f"Client '{name}' already exists"}), 409
    conn.close()
    return jsonify({"message": f"Client '{name}' created"}), 201


@app.route("/clients/<name>", methods=["GET"])
def get_client(name):
    conn = get_db()
    row = conn.execute("SELECT * FROM clients WHERE name=?", (name,)).fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "Client not found"}), 404
    return jsonify(dict(row)), 200


@app.route("/clients/<name>", methods=["DELETE"])
def delete_client(name):
    conn = get_db()
    result = conn.execute("DELETE FROM clients WHERE name=?", (name,))
    conn.commit()
    conn.close()
    if result.rowcount == 0:
        return jsonify({"error": "Client not found"}), 404
    return jsonify({"message": f"Client '{name}' deleted"}), 200


# ---------- PROGRAM GENERATOR ----------
@app.route("/clients/<name>/program", methods=["POST"])
def generate_program(name):
    conn = get_db()
    row = conn.execute("SELECT id FROM clients WHERE name=?", (name,)).fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Client not found"}), 404

    program_type = random.choice(list(PROGRAM_TEMPLATES.keys()))
    program_detail = random.choice(PROGRAM_TEMPLATES[program_type])

    conn.execute(
        "UPDATE clients SET program=? WHERE name=?", (program_detail, name)
    )
    conn.commit()
    conn.close()
    return jsonify({"client": name, "program_type": program_type, "program": program_detail}), 200


# ---------- WORKOUTS ----------
@app.route("/clients/<name>/workouts", methods=["GET"])
def list_workouts(name):
    conn = get_db()
    if not conn.execute("SELECT id FROM clients WHERE name=?", (name,)).fetchone():
        conn.close()
        return jsonify({"error": "Client not found"}), 404
    rows = conn.execute(
        "SELECT * FROM workouts WHERE client_name=? ORDER BY date DESC", (name,)
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows]), 200


@app.route("/clients/<name>/workouts", methods=["POST"])
def add_workout(name):
    conn = get_db()
    if not conn.execute("SELECT id FROM clients WHERE name=?", (name,)).fetchone():
        conn.close()
        return jsonify({"error": "Client not found"}), 404

    data = request.get_json(silent=True) or {}
    workout_date = data.get("date", date.today().isoformat())
    workout_type = data.get("workout_type", "")
    duration_min = data.get("duration_min")
    notes = data.get("notes", "")

    if not workout_type:
        conn.close()
        return jsonify({"error": "workout_type is required"}), 400

    conn.execute(
        "INSERT INTO workouts (client_name, date, workout_type, duration_min, notes) VALUES (?,?,?,?,?)",
        (name, workout_date, workout_type, duration_min, notes),
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Workout added"}), 201


# ---------- PROGRESS ----------
@app.route("/clients/<name>/progress", methods=["GET"])
def list_progress(name):
    conn = get_db()
    if not conn.execute("SELECT id FROM clients WHERE name=?", (name,)).fetchone():
        conn.close()
        return jsonify({"error": "Client not found"}), 404
    rows = conn.execute(
        "SELECT week, adherence FROM progress WHERE client_name=? ORDER BY id", (name,)
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows]), 200


@app.route("/clients/<name>/progress", methods=["POST"])
def add_progress(name):
    conn = get_db()
    if not conn.execute("SELECT id FROM clients WHERE name=?", (name,)).fetchone():
        conn.close()
        return jsonify({"error": "Client not found"}), 404

    data = request.get_json(silent=True) or {}
    week = data.get("week", "")
    adherence = data.get("adherence")

    if not week:
        conn.close()
        return jsonify({"error": "week is required"}), 400
    if adherence is None or not (0 <= int(adherence) <= 100):
        conn.close()
        return jsonify({"error": "adherence must be 0-100"}), 400

    conn.execute(
        "INSERT INTO progress (client_name, week, adherence) VALUES (?,?,?)",
        (name, week, adherence),
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Progress recorded"}), 201


# ---------- ENTRY POINT ----------
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=False)
