# Weekly Project Feedback Tool

Chat-first internal weekly feedback tool for project teams. The current codebase is an empty Django project scaffold for the selected Django stack in `_docs/plan.md`.

## Setup

Install dependencies with uv:

```powershell
uv sync
```

Use the placeholder environment file as a reference for local values:

```powershell
Get-Content .env.example
```

The project reads Django and PostgreSQL settings from environment variables. The `.env.example` file contains placeholders only; do not commit real credentials.

For example, in PowerShell:

```powershell
$env:POSTGRES_DB = "weekly_feedback"
$env:POSTGRES_USER = "weekly_feedback"
$env:POSTGRES_PASSWORD = "weekly_feedback"
$env:POSTGRES_HOST = "localhost"
$env:POSTGRES_PORT = "5432"
$env:POSTGRES_TEST_DB = "test_weekly_feedback"
```

## PostgreSQL

Create local development and test databases that match your environment variables:

```powershell
createdb weekly_feedback
createdb test_weekly_feedback
```

The default local connection uses:

```text
POSTGRES_DB=weekly_feedback
POSTGRES_USER=weekly_feedback
POSTGRES_PASSWORD=weekly_feedback
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_TEST_DB=test_weekly_feedback
```

Application model migrations begin in the custom user task. This setup task intentionally does not add application migrations before the custom user model exists.

## Run The Development Server

```powershell
uv run python manage.py runserver
```

## Run Tests

```powershell
uv run pytest
```

The smoke tests verify that Django settings load and that database settings are built from environment variables.
