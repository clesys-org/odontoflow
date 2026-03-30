# ══════════════════════════════════════════════════
# OdontoFlow — Comandos Docker
# ══════════════════════════════════════════════════

.PHONY: up down restart logs backend frontend test lint clean help

# ── Subir tudo ────────────────────────────────────

up: ## Sobe todos os servicos (pg, redis, minio, backend, frontend)
	docker compose up -d --build
	@echo ""
	@echo "✅ OdontoFlow rodando!"
	@echo "   Frontend:  http://localhost:3000"
	@echo "   Backend:   http://localhost:8000"
	@echo "   API Docs:  http://localhost:8000/docs"
	@echo "   MinIO:     http://localhost:9001"
	@echo ""

up-infra: ## Sobe apenas infra (pg, redis, minio) — para dev local sem Docker
	docker compose up -d postgres redis minio

# ── Parar ─────────────────────────────────────────

down: ## Para todos os servicos
	docker compose down

down-clean: ## Para tudo e remove volumes (APAGA DADOS)
	docker compose down -v

# ── Logs ──────────────────────────────────────────

logs: ## Mostra logs de todos os servicos
	docker compose logs -f

logs-backend: ## Logs apenas do backend
	docker compose logs -f backend

logs-frontend: ## Logs apenas do frontend
	docker compose logs -f frontend

# ── Rebuild ───────────────────────────────────────

restart: ## Restart backend + frontend (rebuild)
	docker compose up -d --build backend frontend

rebuild: ## Rebuild completo (limpa cache)
	docker compose build --no-cache backend frontend
	docker compose up -d

# ── Testes e Lint ─────────────────────────────────

test: ## Roda testes unitarios no Docker
	docker compose run --rm test

lint: ## Roda linter (ruff) no Docker
	docker compose run --rm --profile tools lint

# ── Utilitarios ───────────────────────────────────

shell-backend: ## Abre shell no container backend
	docker compose exec backend bash

shell-db: ## Abre psql no PostgreSQL
	docker compose exec postgres psql -U odontoflow -d odontoflow

migrate: ## Roda migrations do Alembic
	docker compose exec backend alembic upgrade head

seed: ## Cria tenant demo
	docker compose exec backend python scripts/create_tenant.py demo "Clinica Demo"

# ── Status ────────────────────────────────────────

status: ## Mostra status dos containers
	docker compose ps

health: ## Verifica health do backend
	@curl -s http://localhost:8000/health | python3 -m json.tool 2>/dev/null || echo "Backend nao esta rodando"

# ── Help ──────────────────────────────────────────

help: ## Mostra esta ajuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
