# CLAUDE.md — OdontoFlow

## Overview

OdontoFlow is an integrated dental clinic management SaaS (site + system + operations). Built with DDD, SOLID, Clean Architecture. Modular monolith with 12 bounded contexts and schema-per-tenant PostgreSQL multi-tenancy.

## Architecture

- **Pattern**: Modular Monolith with DDD bounded contexts
- **Multi-tenancy**: Schema-per-tenant PostgreSQL (LGPD compliance)
- **CQRS**: Only for Clinical Records (patient timeline read model)
- **Events**: In-process EventBus (shared kernel)

## Tech Stack

- **Backend**: Python 3.12 + FastAPI + SQLAlchemy 2.0 (async) + asyncpg + Alembic + Pydantic v2
- **Frontend**: Next.js 15 + React 19 + TypeScript + Tailwind CSS 4
- **Database**: PostgreSQL 16 + Redis 7
- **Storage**: MinIO (S3-compatible) for documents/images
- **Auth**: JWT (access + refresh tokens)
- **CI**: GitHub Actions (Ruff lint + pytest + Next.js build)

## Project Structure

```
odontologia/
├── backend/           # Python FastAPI backend
│   ├── src/odontoflow/
│   │   ├── shared/    # Shared kernel (events, value objects, base classes)
│   │   ├── clinical/  # BC: Clinical Records (prontuario, odontograma)
│   │   ├── scheduling/# BC: Scheduling (agenda, appointments)
│   │   ├── patient/   # BC: Patient Management
│   │   ├── billing/   # BC: Billing & Finance
│   │   ├── iam/       # BC: Identity & Access Management
│   │   └── api/       # FastAPI routers, schemas, middleware
│   ├── tests/
│   ├── alembic/
│   └── scripts/
├── frontend/          # Next.js frontend
│   └── src/
│       ├── app/       # App Router (auth + dashboard groups)
│       ├── components/ # UI components per domain
│       ├── hooks/     # Custom hooks
│       └── lib/       # API clients, types, utils
└── docs/              # Architecture docs, ADRs, regulatory
```

## Commands

### Backend
```bash
cd backend
pip install -e ".[dev]"          # Install with dev deps
uvicorn odontoflow.api.main:app --reload  # Dev server (port 8000)
pytest tests/ -x -v              # Run tests
ruff check src/ tests/           # Lint
alembic upgrade head             # Run migrations
python scripts/create_tenant.py <slug>    # Provision new tenant
```

### Frontend
```bash
cd frontend
npm install                      # Install deps
npm run dev                      # Dev server (port 3000)
npm run build                    # Production build
```

### Docker
```bash
docker compose up -d             # Start all services (pg, redis, minio, backend, frontend)
docker compose down              # Stop
```

## Bounded Contexts & Layers

Each BC follows Clean Architecture:
```
context/
├── domain/         # Models (aggregates, entities, VOs), repository protocols, domain services
├── application/    # Use cases (commands + queries for CQRS contexts)
└── infrastructure/ # PostgreSQL repos, external API gateways
```

**Dependency rule**: domain/ imports NOTHING from application/ or infrastructure/. Arrows always point inward.

## Conventions

- Domain models: `@dataclass(frozen=True)` for VOs, mutable `@dataclass` for entities/aggregates
- Repository interfaces: Python `Protocol` classes in `domain/repositories.py`
- Value objects: Self-validating (CPF, Email, Phone, Money, ToothNumber)
- Events: Published via shared EventBus, contexts never call each other directly
- API schemas: Pydantic v2 models in `api/schemas/`
- Naming: Portuguese for user-facing labels, English for code identifiers

## Regulatory

- **LGPD**: Health data = sensitive. Encryption, audit logs, consent tracking, 20-year retention
- **CFO 91/2009**: Digital dental records. ICP-Brasil for paperless
- **TISS/ANS**: XML standard for insurance billing (GTO)

## Language

Developer (Cleber) communicates in Brazilian Portuguese. Respond in Portuguese unless asked otherwise.
