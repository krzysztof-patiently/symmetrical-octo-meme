# rekrutacja

FastAPI service.

## Setup

```bash
uv sync
```

## Run

```bash
uv run fastapi dev app/main.py
```

API docs at http://127.0.0.1:8000/docs

## Test

```bash
uv run pytest
```

## Docker

```bash
docker compose up --build
```

## Jobs API

Jobs are stored in SQLite (`DATABASE_URL`, default `sqlite:///./data/jobs.db`).

A job has a `description` (text), a `status` (`TODO` or `DONE`, default `TODO`) and a `location`
(`{"latitude": -90..90, "longitude": -180..180}`).

| Method | Path | Body / params |
| --- | --- | --- |
| `POST` | `/jobs` | JSON: `description`, `location`, optional `status` |
| `GET` | `/jobs` | |
| `GET` | `/jobs/{id}` | |
| `PATCH` | `/jobs/{id}` | JSON: `status` (the only field that can change) |
| `DELETE` | `/jobs/{id}` | |

```bash
curl -H 'Content-Type: application/json' \
  -d '{"description": "Fix the fence", "location": {"latitude": 52.2297, "longitude": 21.0122}}' \
  localhost:8000/jobs
```
