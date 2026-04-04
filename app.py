"""
app.py - ACEest Fitness & Gym Flask API
A REST API for managing gym clients, workouts, programs, and progress tracking.
"""

from flask import Flask, request, jsonify
import sqlite3
import random

app = Flask(__name__)
DB_NAME = "aceest_fitness.db"

# ---------- PROGRAM TEMPLATES ----------
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

    cur.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            age INTEGER,
            height REAL,
            weight REAL,
            program TEXT,
            calories INTEGER,
            membership_status TEXT DEFAULT 'Active'
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT,
            workout_type TEXT,
            duration_min INTEGER,
            notes TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT,
            week TEXT,
            adherence INTEGER
        )
    """)

    conn.commit()
    conn.close()


# ---------- HELPER ----------
def client_exists(name):
    conn = get_db()
    row = conn.execute("SELECT id FROM clients WHERE name=?", (name,)).fetchone()
    conn.close()
    return row is not None


# ---------- ROUTES ----------
@app.route("/")
def index():
    return jsonify({"app": "ACEest Fitness & Gym API", "version": "3.2.4"}), 200


@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200


# --- Clients ---
@app.route("/clients", methods=["GET"])
def list_clients():
    conn = get_db()
    rows = conn.execute("SELECT * FROM clients ORDER BY name").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows]), 200


@app.route("/clients/<name>", methods=["GET"])
def get_client(name):
    conn = get_db()
    row = conn.execute("SELECT * FROM clients WHERE name=?", (name,)).fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "Client not found"}), 404
    return jsonify(dict(row)), 200


@app.route("/clients", methods=["POST"])
def create_client():
    data = request.get_json(force=True)
    name = data.get("name", "").strip()

    if not name:
        return jsonify({"error": "Name is required"}), 400

    age = data.get("age")
    weight = data.get("weight")
    height = data.get("height")
    calories = data.get("calories")
    membership_status = data.get("membership_status", "Active")

    conn = get_db()
    try:
        conn.execute(
            """INSERT INTO clients (name, age, height, weight, calories, membership_status)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (name, age, height, weight, calories, membership_status),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "Client already exists"}), 409
    conn.close()
    return jsonify({"message": f"Client {name} created successfully"}), 201


@app.route("/clients/<name>", methods=["DELETE"])
def delete_client(name):
    conn = get_db()
    cur = conn.execute("DELETE FROM clients WHERE name=?", (name,))
    conn.commit()
    if cur.rowcount == 0:
        conn.close()
        return jsonify({"error": "Client not found"}), 404
    conn.close()
    return jsonify({"message": f"Client {name} deleted"}), 200


# --- Program Generator ---
@app.route("/clients/<name>/program", methods=["POST"])
def generate_program(name):
    if not client_exists(name):
        return jsonify({"error": "Client not found"}), 404

    program_type = random.choice(list(PROGRAM_TEMPLATES.keys()))
    program = random.choice(PROGRAM_TEMPLATES[program_type])

    conn = get_db()
    conn.execute("UPDATE clients SET program=? WHERE name=?", (program, name))
    conn.commit()
    conn.close()

    return jsonify({"program": program, "program_type": program_type}), 200


# --- Workouts ---
@app.route("/clients/<name>/workouts", methods=["GET"])
def list_workouts(name):
    if not client_exists(name):
        return jsonify({"error": "Client not found"}), 404

    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM workouts WHERE client_name=?", (name,)
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows]), 200


@app.route("/clients/<name>/workouts", methods=["POST"])
def add_workout(name):
    if not client_exists(name):
        return jsonify({"error": "Client not found"}), 404

    data = request.get_json(force=True)
    workout_type = data.get("workout_type")
    duration_min = data.get("duration_min")
    notes = data.get("notes", "")

    if not workout_type:
        return jsonify({"error": "workout_type is required"}), 400

    conn = get_db()
    conn.execute(
        "INSERT INTO workouts (client_name, workout_type, duration_min, notes) VALUES (?, ?, ?, ?)",
        (name, workout_type, duration_min, notes),
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Workout added"}), 201


# --- Progress ---
@app.route("/clients/<name>/progress", methods=["GET"])
def list_progress(name):
    if not client_exists(name):
        return jsonify({"error": "Client not found"}), 404

    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM progress WHERE client_name=?", (name,)
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows]), 200


@app.route("/clients/<name>/progress", methods=["POST"])
def add_progress(name):
    if not client_exists(name):
        return jsonify({"error": "Client not found"}), 404

    data = request.get_json(force=True)
    week = data.get("week")
    adherence = data.get("adherence")

    if not week:
        return jsonify({"error": "week is required"}), 400
    if adherence is None or not (0 <= adherence <= 100):
        return jsonify({"error": "adherence must be between 0 and 100"}), 400

    conn = get_db()
    conn.execute(
        "INSERT INTO progress (client_name, week, adherence) VALUES (?, ?, ?)",
        (name, week, adherence),
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Progress recorded"}), 201


# ---------- RUN ----------
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
