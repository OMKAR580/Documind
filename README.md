# DocuMind AI

AI-powered multimodal document intelligence platform for extracting insights, answering questions with exact citations, and reasoning across complex documents (PDFs, DOCX, images).

---

## Architecture Overview

DocuMind is architected as a **modular monolith** with clean boundaries across services, background processing, and UI:

```
Documind/
├── .github/workflows/       # GitHub Actions CI quality gates
├── apps/
│   └── web/                 # Next.js 16 (Turbopack, React 19, Tailwind CSS v4, shadcn UI)
├── services/
│   ├── api/                 # FastAPI REST API (Pydantic Settings, SQLAlchemy 2, Alembic)
│   └── worker/              # Background processing worker (OCR, chunking, embeddings)
├── ai/                      # AI modules (agents, computer vision, NLP, RAG)
├── packages/
│   └── shared/              # Shared schemas and utilities
├── infra/
│   └── docker/              # Production & development Dockerfiles
├── .env.example             # Safe environment variable configuration template
├── docker-compose.yml       # Containerized orchestration (PostgreSQL, Redis, API, Worker, Web)
└── README.md
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Next.js 16 (App Router), TypeScript, Tailwind CSS v4, shadcn UI |
| **API Backend** | Python 3.12+, FastAPI, Pydantic v2 Settings |
| **Database & ORM** | PostgreSQL 16, SQLAlchemy 2.0, Alembic migrations |
| **Worker & Queue** | Python worker, Redis 7 (Celery/ARQ queue integration in Sprint 2+) |
| **AI / ML Pipeline** | Document parsers, embeddings, RAG, agent workflows (Phased) |
| **Infrastructure** | Docker, Docker Compose, GitHub Actions CI/CD |

---

## Getting Started

### Prerequisites

- **Node.js**: `v20.x` or higher
- **Python**: `3.12.x` or higher
- **Git**
- **Docker & Docker Compose** *(Optional for local containerized development)*

---

### Method A: Native Local Development (Windows / Linux / macOS)

#### 1. Clone & Configure Environment

```bash
git clone https://github.com/OMKAR580/Documind.git
cd Documind
copy .env.example .env     # Windows PowerShell / CMD
# or: cp .env.example .env  # Linux / macOS
```

#### 2. Start Backend API (`services/api`)

```bash
cd services/api

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate       # Windows PowerShell
# source venv/bin/activate     # Linux / macOS

# Install dependencies
pip install -r requirements.txt

# Inspect static migration SQL (offline, no database required)
alembic upgrade head --sql

# Run migrations against active PostgreSQL database
alembic upgrade head

# Start API dev server (runs on http://localhost:8000)
uvicorn app.main:app --reload --port 8000
```

- **Interactive API Docs**: `http://localhost:8000/api/docs`
- **Alternative ReDoc**: `http://localhost:8000/api/redoc`
- **Process Liveness Probe**: `http://localhost:8000/api/v1/health`
- **Dependency Readiness Probe**: `http://localhost:8000/api/v1/health/ready`

#### 3. Start Frontend (`apps/web`)

```bash
cd apps/web

# Install dependencies
npm install

# Start Next.js development server (runs on http://localhost:3000)
npm run dev
```

#### 4. Run Background Worker (`services/worker`)

```bash
cd services/worker

# Activate the shared or dedicated Python environment
python -m app.worker
```

---

### Method B: Containerized Development (Docker Compose)

Ensure Docker Desktop is running, then execute from the repository root:

```bash
# Start all services (PostgreSQL, Redis, API, Worker, Web)
docker compose up --build

# Run in detached mode
docker compose up -d

# Check service logs
docker compose logs -f api

# Tear down services and retain volume data
docker compose down
```

---

## Backend Architecture & Conventions (Phase 1)

### 1. Centralized Configuration & Security
- Managed via `app.core.config.Settings` (Pydantic Settings v2).
- Validates environment mode (`development`, `testing`, `staging`, `production`).
- **Production Safety:** Startup fails fast if default credentials (`postgres:postgres`) or insecure `SECRET_KEY` are used in production mode.
- Passwords and connection credentials in database URLs are automatically sanitized in logs.

### 2. Database & SQLAlchemy 2.0
- SQLAlchemy 2.0 with connection pooling (`pool_size`, `max_overflow`, `pool_pre_ping`).
- Asynchronous-safe design: Blocking database connection checks in endpoints are offloaded via `run_in_threadpool` to prevent event loop starvation.
- Modern `DeclarativeBase` (`app.models.base.Base`) with `TimestampMixin` and `UUIDPrimaryKeyMixin`.
- Lightweight `BaseRepository` pattern for clean, testable data access (`app.repositories.base.BaseRepository`).
- Core infrastructure model: `SystemMetadata` (`system_metadata`) for tracking platform state and schema metadata without premature business-domain tables.

### 3. Alembic Database Migrations
- Migration files located in `services/api/alembic/versions/`.
- Initial revision: `0001_initial_core_schema.py` creating `system_metadata`.
- Autogeneration targets `Base.metadata` via `app.models`.
- Generate offline SQL: `alembic upgrade head --sql`
- Apply migrations: `alembic upgrade head`
- Revert migrations: `alembic downgrade base`

### 4. Consistent Error Handling Envelopes
All API endpoints return predictable, standardized JSON error responses:
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Resource not found",
    "details": null
  }
}
```
Global exception handlers automatically catch:
- `AppException` (application-specific domain errors)
- `StarletteHTTPException` / `HTTPException` (standard HTTP errors)
- `RequestValidationError` (422 validation errors with sanitized field details)
- `Exception` (unhandled 500 server errors, logging full tracebacks internally without exposing stack traces to clients)

---

## Quality Checks & Automated Testing

### Backend Quality Suite (`services/api`)

```bash
cd services/api

# Run full unit and integration test suite (23 tests)
pytest -v

# Run Ruff linter
ruff check .

# Check code formatting with Ruff
ruff format --check .

# Validate offline Alembic migration DDL generation
alembic upgrade head --sql
```

### Frontend Quality Suite (`apps/web`)

```bash
cd apps/web

# Run ESLint
npm run lint

# Run TypeScript type check
npx tsc --noEmit

# Run production build
npm run build
```

---

## Branching Strategy & Git Workflow

This project adheres to a strict two-branch release flow:

- **`develop`**: Primary integration branch for active development and validated feature work.
- **`main`**: Production-ready branch containing only fully tested and validated phase releases.
- **Rule**: Direct pushes to `main` are restricted. All features and fixes integrate into `develop` first. Phase releases from `develop` to `main` occur only after complete regression testing.
