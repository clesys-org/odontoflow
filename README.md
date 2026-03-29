# OdontoFlow

Sistema integrado de gestao odontologica — site, sistema e operacao.

## Stack

- **Backend**: Python 3.12 + FastAPI + SQLAlchemy 2.0 + PostgreSQL 16
- **Frontend**: Next.js 15 + React 19 + TypeScript + Tailwind CSS 4
- **Infra**: Docker Compose + Redis + MinIO (S3)

## Quick Start

```bash
# Subir infra local
docker compose up -d

# Backend
cd backend
pip install -e ".[dev]"
alembic upgrade head
python scripts/create_tenant.py demo
uvicorn odontoflow.api.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

Acesse: http://localhost:3000

## Arquitetura

Modular Monolith com DDD, 12 bounded contexts, schema-per-tenant PostgreSQL.

Veja [docs/architecture/](docs/architecture/) para detalhes.

## Status

- [x] Fase 0: Skeleton (estrutura, shared kernel, IAM, Docker)
- [ ] Fase 1A: Patient Management
- [ ] Fase 1B: Scheduling
- [ ] Fase 1C: Clinical Records
- [ ] Fase 2: Financial & Treatment
- [ ] Fase 3: Insurance & Advanced
- [ ] Fase 4: Differentiators (AI, Teleodonto)
