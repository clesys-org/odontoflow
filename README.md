# OdontoFlow

Sistema integrado de gestao odontologica — site, sistema e operacao.

## Quick Start (Docker — recomendado)

Unico pre-requisito: [Docker Desktop](https://www.docker.com/products/docker-desktop/)

```bash
git clone https://github.com/clesys-org/odontoflow.git
cd odontoflow
make up
```

Pronto! Acesse:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **MinIO Console**: http://localhost:9001

### Comandos uteis

```bash
make up          # Sobe tudo (pg, redis, minio, backend, frontend)
make down        # Para tudo
make logs        # Ver logs em tempo real
make test        # Rodar testes no Docker
make lint        # Rodar linter
make shell-db    # Abrir psql no PostgreSQL
make status      # Ver status dos containers
make help        # Ver todos os comandos
```

### Sem Docker (dev local)

```bash
# Sobe apenas a infra no Docker
make up-infra

# Backend (requer Python 3.9+)
cd backend
python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"
.venv/bin/uvicorn odontoflow.api.main:app --reload

# Frontend (requer Node 20+)
cd frontend
npm install && npm run dev
```

## Stack

- **Backend**: Python + FastAPI + SQLAlchemy 2.0 + PostgreSQL 16
- **Frontend**: Next.js 15 + React 19 + TypeScript + Tailwind CSS 4
- **Infra**: Docker Compose + Redis 7 + MinIO (S3)
- **Arquitetura**: DDD + Clean Architecture + CQRS (clinical records)

## Numeros

| Metrica | Valor |
|---------|-------|
| Testes unitarios | 294 |
| Endpoints API | 81 |
| Paginas frontend | 20 |
| Bounded contexts | 12/12 |

## Arquitetura

Modular Monolith com DDD, 12 bounded contexts, schema-per-tenant PostgreSQL.

```
IAM → Patient → Scheduling → Clinical → Treatment → Billing
                                          ↓
                              Insurance ← ↑
                              Inventory · Staff · Analytics
                              Communication · Website
```

Veja [docs/architecture/](docs/architecture/) para ADRs e detalhes.

## Status

- [x] Fase 0: Skeleton (estrutura, shared kernel, IAM, Docker)
- [x] Fase 1A: Patient Management
- [x] Fase 1B: Scheduling
- [x] Fase 1C: Clinical Records (odontograma SVG)
- [x] Fase 2: Treatment Plans + Billing & Finance
- [x] Fase 3: Insurance (TISS) + Inventory + Staff + Analytics
- [x] Fase 4: Communication + Website Builder
- [ ] Deploy (Railway + Vercel)
- [ ] PostgreSQL real (migrar de in-memory repos)
- [ ] Testes de integracao API
