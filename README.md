# Weekly Project Feedback Tool

Chat-first internal weekly feedback tool for project teams. The current codebase is an empty Django project scaffold for the selected Django stack in `_docs/plan.md`.

## Setup

Install dependencies with uv:

```powershell
uv sync
```

## Run The Development Server

```powershell
uv run python manage.py runserver
```

## Run Tests

```powershell
uv run pytest
```

The initial smoke test verifies that Django settings load without requiring PostgreSQL, Slack credentials, or any other external service.
