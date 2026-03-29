# ADR-004: In-Process Event Bus, Evolve to Message Broker

## Status
Accepted

## Context
Bounded contexts precisam se comunicar (ex: TreatmentPlanApproved -> Billing gera Invoice). Opcoes: chamada direta, EventBus in-process, message broker (RabbitMQ/Redis Streams).

## Decision
Comecar com **EventBus in-process** (mesmo pattern do StockPulse). Evoluir para Redis Streams ou RabbitMQ quando necessario (Fase 2+).

## Rationale
- Monolito com um processo: in-process pub/sub e simples, rapido, zero infra extra
- Interface do EventBus (subscribe/publish) e a mesma independente do transporte
- Trocar implementacao e uma unica mudanca em infrastructure

## Trade-offs
- Eventos perdidos se processo crashar mid-handling
- Aceitavel para Fase 1 (scheduling + clinical records)
- Fase 2 (billing + insurance): adicionar outbox pattern com eventos persistentes

## Consequences
- shared/event_bus.py com EventBus class
- Handlers registrados no lifespan da app
- Futura evolucao: Redis Streams subscriber substitui in-process handlers
