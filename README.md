# ACEest Fitness & Gym — DevOps CI/CD Project

> **Course:** Introduction to DevOps — CSIZG514 / SEZG514 / SEUSZG514 (S2-25)  
> **Assignment:** 1 — Implementing Automated CI/CD Pipelines

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Repository Structure](#repository-structure)
3. [Local Setup & Execution](#local-setup--execution)
4. [Running Tests Manually](#running-tests-manually)
5. [Docker Usage](#docker-usage)
6. [GitHub Actions — CI/CD Pipeline](#github-actions--cicd-pipeline)
7. [Jenkins BUILD Integration](#jenkins-build-integration)
8. [API Reference](#api-reference)

---

## Project Overview

ACEest Fitness & Gym is a **RESTful Flask web API** for managing gym clients, workout sessions, and weekly adherence progress. This repository demonstrates a complete DevOps lifecycle:

- **Version Control** — Git branching strategy with descriptive commits  
- **Unit Testing** — Pytest suite with isolated test databases  
- **Containerisation** — Multi-stage Dockerfile for a lean, secure image  
- **CI/CD** — GitHub Actions pipeline (lint → test → Docker build/health-check)  
- **Build Server** — Jenkins project for secondary build validation

---

## Repository Structure

```
aceest-fitness/
├── app.py                        # Flask application & SQLite logic
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Multi-stage Docker build
├── Jenkinsfile                   # Jenkins pipeline definition
├── tests/
│   └── test_app.py               # Pytest unit-test suite
├── .github/
│   └── workflows/
│       └── main.yml              # GitHub Actions CI/CD pipeline
└── README.md
```

---

## Local Setup & Execution

### Prerequisites

- Python 3.11+
- pip

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/aceest-fitness.git
cd aceest-fitness

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialise the database and start the server
python -c "from app import init_db; init_db()"
python app.py
```

The API will be available at **http://localhost:5000**.

---

## Running Tests Manually

```bash
# Run all tests with verbose output
pytest tests/test_app.py -v

# Run with coverage report
pytest tests/test_app.py -v --cov=app --cov-report=term-missing

# Run a specific test class
pytest tests/test_app.py::TestClientCreation -v
```

The test suite uses temporary SQLite databases via `pytest` fixtures — no cleanup required.

---

## Docker Usage

### Build the image

```bash
docker build -t aceest-fitness:latest .
```

### Run the container

```bash
docker run -d \
  --name aceest \
  -p 5000:5000 \
  aceest-fitness:latest
```

### Verify it is running

```bash
curl http://localhost:5000/health
# Expected: {"status": "healthy"}
```

### Stop and remove

```bash
docker rm -f aceest
```

---

## GitHub Actions — CI/CD Pipeline

The pipeline is defined in `.github/workflows/main.yml` and triggers on every **push** or **pull_request** to any branch.

### Pipeline Stages

| Job | Stage | Description |
|-----|-------|-------------|
| 1 | **Build & Lint** | Installs dependencies; runs `flake8` for syntax errors and style violations. |
| 2 | **Automated Testing** | Executes the full Pytest suite with coverage reporting. Requires Job 1 to pass. |
| 3 | **Docker Image Assembly** | Builds the Docker image, starts a container, performs a live `/health` HTTP check, then tears it down. Requires Job 2 to pass. |

### Key Design Decisions

- **Sequential `needs:` dependencies** — each job only starts if the previous one passes, acting as a quality gate.  
- **`--no-cache-dir`** in the Dockerfile — keeps the image lean; caching is handled by the GitHub Actions layer cache instead.  
- **Non-root container user** — the `appuser` account is created inside the image to follow container security best practices.

---

## Jenkins BUILD Integration

Jenkins acts as a secondary **build validation layer**, pulling the latest code from GitHub and verifying the build succeeds in a controlled environment.

### Setup Steps

1. **Install Jenkins** (locally or on a VM) and ensure the **Git** and **Pipeline** plugins are installed.

2. **Create a new Pipeline job** in Jenkins and point **SCM** to your GitHub repository URL.

3. **Add a `Jenkinsfile`** to the repository root:

```groovy
pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/<your-username>/aceest-fitness.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }

        stage('Lint') {
            steps {
                sh 'flake8 app.py --select=E9,F63,F7,F82'
            }
        }

        stage('Unit Tests') {
            steps {
                sh 'pytest tests/test_app.py -v'
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build -t aceest-fitness:jenkins .'
            }
        }
    }

    post {
        success { echo 'BUILD PASSED — all stages completed successfully.' }
        failure { echo 'BUILD FAILED — check stage logs above.' }
    }
}
```

4. **Configure a GitHub Webhook** (`Settings → Webhooks`) pointing to `http://<jenkins-host>:8080/github-webhook/` so Jenkins triggers automatically on every push.

### Integration Flow

```
Developer Push
      │
      ▼
GitHub (source of truth)
      │
      ├──► GitHub Actions (immediate: lint → test → docker)
      │
      └──► Jenkins Webhook → Pipeline (build validation in clean agent)
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API overview & endpoint list |
| GET | `/health` | Health check |
| GET | `/clients` | List all clients |
| POST | `/clients` | Create a new client |
| GET | `/clients/<name>` | Get a single client |
| DELETE | `/clients/<name>` | Delete a client |
| POST | `/clients/<name>/program` | Auto-generate a training program |
| GET | `/clients/<name>/workouts` | List workouts for a client |
| POST | `/clients/<name>/workouts` | Log a new workout |
| GET | `/clients/<name>/progress` | List weekly progress |
| POST | `/clients/<name>/progress` | Record weekly adherence |

### Example Requests

```bash
# Create a client
curl -X POST http://localhost:5000/clients \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "age": 28, "weight": 65, "height": 165}'

# Generate a training program
curl -X POST http://localhost:5000/clients/Alice/program

# Log a workout
curl -X POST http://localhost:5000/clients/Alice/workouts \
  -H "Content-Type: application/json" \
  -d '{"workout_type": "Strength", "duration_min": 60, "notes": "PB on bench"}'

# Record weekly adherence
curl -X POST http://localhost:5000/clients/Alice/progress \
  -H "Content-Type: application/json" \
  -d '{"week": "2025-W01", "adherence": 85}'
```
