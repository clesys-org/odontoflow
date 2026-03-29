# ADR-001: Modular Monolith over Microservices

## Status
Accepted

## Context
OdontoFlow precisa de uma arquitetura que suporte 12 bounded contexts com isolamento claro, mas e desenvolvido por um time pequeno (1 dev).

## Decision
**Monolito modular** com bounded contexts separados em pacotes Python. Cada contexto tem domain/, application/ e infrastructure/. Comunicacao entre contextos via EventBus in-process.

## Rationale
- Microservices adicionam complexidade operacional (service discovery, distributed transactions, debugging) sem beneficio nesta escala
- A estrutura modular permite extrair qualquer contexto para servico separado no futuro — basta trocar EventBus in-process por message broker
- O boundary ja esta definido; apenas o transporte muda

## Trade-offs
- Bug em um contexto pode derrubar todos (mitigado por error handling no EventBus)
- Compartilha um processo (OK para clinicas com ate ~100 usuarios simultaneos)

## Consequences
- Cada contexto e um pacote Python independente
- Comunicacao APENAS via domain events (nunca import direto entre contextos)
- deps.py como composition root para DI
