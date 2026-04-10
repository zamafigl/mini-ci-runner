# Mini CI Runner

> A lightweight self-hosted CI/CD backend that executes stage-based pipelines asynchronously with FastAPI, Redis, RQ, and PostgreSQL.

---

## Overview

**Mini CI Runner** is a small backend system inspired by real CI/CD platforms like GitHub Actions and GitLab CI.

It lets you:

- define pipelines with ordered stages
- trigger pipeline runs via API
- execute jobs asynchronously in a background worker
- store run history and stage results
- retry failed runs
- inspect execution output and statuses

This project is focused on **backend orchestration**, **queue-based execution**, and **pipeline lifecycle management**.

---

## Why this project is worth attention

This is not another CRUD demo.

It shows practical backend and DevOps-oriented concepts:

- background job execution
- queue-based architecture
- API + worker separation
- stage-by-stage pipeline processing
- retry logic
- timeout handling
- persistent execution history
- subprocess-based command execution

---

## Tech Stack

- **FastAPI** — API layer
- **PostgreSQL** — persistence
- **SQLAlchemy** — ORM
- **Redis** — queue backend
- **RQ** — background job processing
- **Pytest** — tests
- **Docker / Docker Compose** — local infrastructure

---

## Architecture

```text
Client
  │
  ▼
FastAPI API
  │
  ▼
Redis Queue
  │
  ▼
RQ Worker
  │
  ▼
Pipeline Stage Execution
  │
  ▼
PostgreSQL
```
**Execution flow**\
A user creates a pipeline.\
A user triggers a run for that pipeline.\
The API places a job into Redis.\
The worker picks up the job.\
Stages are executed sequentially.\
Logs, statuses, and exit codes are stored in the database.\
Failed runs can be retried.\
**Features**\
Pipeline creation with multiple ordered stages\
Asynchronous execution through Redis + RQ\
Run history storage\
Stage-level status tracking\
Command output logging\
Exit code tracking\
Retry endpoint for failed runs\
Health-check endpoints\
Stage timeout support\
## Project Structure
```
mini-ci-runner/
├── app/
│   ├── __init__.py
│   ├── db.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── core/
│   │   └── config.py
│   ├── routes/
│   │   ├── pipelines.py
│   │   └── runs.py
│   └── workers/
│       ├── jobs.py
│       └── queue.py
├── tests/
│   ├── test_pipelines.py
│   └── test_runs.py
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```
## API Endpoints
Pipelines\
```
Method	Endpoint	Description
POST	/pipelines	Create a pipeline
GET	/pipelines	List all pipelines
GET	/pipelines/{pipeline_id}	Get pipeline by ID
Runs
Method	Endpoint	Description
POST	/runs/pipelines/{pipeline_id}	Trigger a pipeline run
POST	/runs/{run_id}/retry	Retry an existing run
GET	/runs	List all runs
GET	/runs/{run_id}	Get run by ID
Health
Method	Endpoint	Description
GET	/health	Basic service health
GET	/db-health	Database connectivity check
```

**Example Pipeline Payload**\
```
{
  "name": "demo-pipeline",
  "description": "Simple CI pipeline",
  "max_retries": 1,
  "stages": [
    {
      "name": "lint",
      "command": "echo lint",
      "order": 1,
      "timeout_seconds": 10
    },
    {
      "name": "test",
      "command": "echo test",
      "order": 2,
      "timeout_seconds": 10
    }
  ]
}
```
**Quick Start**
1. Clone the repository
git clone https://github.com/zamafigl/mini-ci-runner.git
cd mini-ci-runner
2. Create and fill .env
cp .env.example .env

Example:
```
APP_NAME=Mini CI Runner
DEBUG=true

POSTGRES_DB=mini_ci
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5434

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
QUEUE_NAME=mini-ci
```
3. Start infrastructure
docker compose up -d

This starts:

PostgreSQL
Redis\
4. Create a virtual environment
python3 -m venv venv
source venv/bin/activate\
5. Install dependencies
pip install -r requirements.txt\
6. Run the API
uvicorn app.main:app --reload

API will be available at:

http://127.0.0.1:8000

Docs:
http://127.0.0.1:8000/docs \
7. Run the worker

In a second terminal:
```
source venv/bin/activate
PYTHONPATH=. rq worker mini-ci
Example Usage
Create pipeline
curl -X POST "http://127.0.0.1:8000/pipelines" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "demo-pipeline",
    "description": "Simple CI pipeline",
    "max_retries": 1,
    "stages": [
      {
        "name": "build",
        "command": "echo building",
        "order": 1,
        "timeout_seconds": 5
      },
      {
        "name": "test",
        "command": "echo testing",
        "order": 2,
        "timeout_seconds": 5
      }
    ]
  }'
```
**Trigger run**
```
curl -X POST "http://127.0.0.1:8000/runs/pipelines/1"
```
**List runs**
```
curl "http://127.0.0.1:8000/runs"
```
**Retry run**
```
curl -X POST "http://127.0.0.1:8000/runs/1/retry"
```
**Running Tests**
```
pytest -v
```
**Current Limitations**\
Commands are executed with subprocess, without container isolation
No authentication or authorization
No Git webhook triggers yet
No frontend/UI
No parallel stage execution
Logs are stored in DB, but there is no live streaming yet
Roadmap
 Docker-isolated job execution
 GitHub/GitLab webhook triggers
 Live log streaming
 Parallel stage execution
 Authentication
 Better observability and metrics
 Per-project runner configuration
What this project demonstrates

This repository is useful as a portfolio project for roles related to:

Junior Python Backend
Junior DevOps
Infrastructure / Platform Engineer trainee roles
Automation-focused backend roles

It demonstrates that the author can work with:

API design
async task execution patterns
Redis-based queues
PostgreSQL integration
worker architecture
Dockerized local infrastructure
pipeline-oriented backend logic
Author

**Alexander**\
**GitHub: zamafigl**

## License

**This project is for educational and portfolio purposes.**