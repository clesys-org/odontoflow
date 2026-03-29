# ADR-002: Schema-per-Tenant PostgreSQL Multi-tenancy

## Status
Accepted

## Context
OdontoFlow e SaaS multi-clinica. Dados de saude sao sensiveis (LGPD Art. 11). Precisamos de isolamento forte entre tenants.

## Decision
Cada clinica (tenant) recebe um **schema PostgreSQL proprio** (ex: `tenant_clinica_sorriso`). Tabelas globais (users, tenants, audit_log) ficam no schema `public`.

## Rationale
1. **LGPD**: dados de cada clinica fisicamente separados
2. **Exclusao**: `DROP SCHEMA CASCADE` para churned tenant
3. **Backup**: backup/restore por tenant
4. **Seguranca**: impossivel vazar dados entre tenants por WHERE clause ausente
5. **PostgreSQL**: suporta centenas de schemas eficientemente

## Trade-offs
- Migrations precisam iterar sobre todos schemas (Alembic customizado)
- Queries cross-tenant (admin SaaS) precisam qualificar schema
- Provisionar novo tenant e mais lento (roda todas migrations)

## Consequences
- `alembic/env.py` customizado com iteracao de schemas
- `scripts/create_tenant.py` para provisionar
- Middleware extrai tenant_id do JWT e seta search_path
