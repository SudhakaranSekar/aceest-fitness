# ACEest Fitness & Gym API

A Flask-based REST API for managing gym clients, workout programs, progress tracking, and membership at ACEest Fitness & Gym.

## Features

- Client management (create, read, delete)
- AI-style workout program generator
- Workout logging with type and duration
- Weekly adherence progress tracking
- SQLite database for persistent storage
- Health check endpoint for monitoring

## Tech Stack

- **Backend:** Python, Flask
- **Database:** SQLite
- **Testing:** Pytest
- **Containerization:** Docker
- **CI/CD:** GitHub Actions, Jenkins

## Local Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/SudhakaranSekar/aceest-fitness.git
   cd aceest-fitness
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python app.py
   ```
   The API starts at `http://localhost:5000`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | App info |
| GET | `/health` | Health check |
| GET | `/clients` | List all clients |
| POST | `/clients` | Create a new client |
| GET | `/clients/<name>` | Get client by name |
| DELETE | `/clients/<name>` | Delete a client |
| POST | `/clients/<name>/program` | Generate a fitness program |
| GET | `/clients/<name>/workouts` | List client workouts |
| POST | `/clients/<name>/workouts` | Add a workout |
| GET | `/clients/<name>/progress` | List weekly progress |
| POST | `/clients/<name>/progress` | Log weekly adherence |

## Running Tests

```bash
python -m pytest tests/test_app.py -v
```

This runs 36 unit tests covering all API endpoints including health checks, client CRUD operations, program generation, workout logging, and progress tracking.

## Docker

Build and run with Docker:
```bash
docker build -t aceest-fitness .
docker run -p 5000:5000 aceest-fitness
```

## CI/CD Pipeline

### GitHub Actions

The workflow file `.github/workflows/main.yml` triggers on every push and pull request to the `main` branch. It runs the following stages:

1. **Checkout** - pulls the latest code
2. **Setup Python** - installs Python 3.11
3. **Install dependencies** - installs Flask and Pytest
4. **Lint** - checks app.py for syntax errors
5. **Run tests** - executes the full Pytest suite
6. **Docker build** - builds the Docker image to verify containerization

### Jenkins

The `Jenkinsfile` defines a pipeline with stages for cloning, setup, linting, testing, and Docker image building. It connects to the GitHub repository and validates every build in a controlled environment.

## Project Structure

```
aceest-fitness/
├── app.py                  # Flask application
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker configuration
├── Jenkinsfile             # Jenkins pipeline
├── README.md               # Documentation
├── .gitignore              # Git ignore rules
├── .github/
│   └── workflows/
│       └── main.yml        # GitHub Actions CI/CD
└── tests/
    └── test_app.py         # Unit tests (36 tests)
```

## Author

Sudhakaran Sekar
# ACEest Fitness 
