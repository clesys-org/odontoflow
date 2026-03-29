# ADR-003: CQRS Only for Clinical Records

## Status
Accepted

## Context
A timeline do paciente e a query mais complexa do sistema — agrega dados de notas clinicas, consultas, prescricoes, tratamentos e pagamentos. Outros contextos tem queries simples.

## Decision
CQRS (Command Query Responsibility Segregation) **apenas** para o bounded context Clinical Records. Outros contextos usam repository pattern padrao.

## Rationale
- `patient_timeline_view` e uma tabela denormalizada atualizada por event handlers
- Renderizacao instantanea da timeline (sem JOINs complexos)
- Outros contextos (scheduling, patient, billing) nao justificam a complexidade adicional do CQRS

## Trade-offs
- Timeline read model pode ser temporariamente inconsistente (eventual consistency)
- Aceitavel: entry e visualizacao sao sequenciais (mesmo usuario)
- Event handlers rodam in-process (sub-millisecond lag)

## Consequences
- Clinical context tem `application/commands/` e `application/queries/` separados
- Event handlers populam `patient_timeline_view` quando eventos ocorrem
- Outros contextos mantem estrutura simples (application/use_cases/)
