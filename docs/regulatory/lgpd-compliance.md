# LGPD Compliance — OdontoFlow

## Dados de Saude (Art. 11)
Dados de pacientes odontologicos sao **dados pessoais sensiveis**. Tratamento exige:
- Consentimento explicito OU base legal de protecao a saude (por profissional de saude)
- Proibido compartilhamento para vantagem economica

## Medidas Implementadas

### Isolamento de Dados
- Schema-per-tenant: dados de cada clinica fisicamente separados no PostgreSQL
- Impossivel acesso cruzado entre tenants

### Criptografia
- Dados em transito: HTTPS/TLS obrigatorio
- Dados em repouso: PostgreSQL com encryption at rest
- CPF e dados sensiveis: criptografia a nivel de coluna (planejado Fase 2)

### Controle de Acesso (RBAC)
- Roles: OWNER, ADMIN, DENTIST, RECEPTIONIST, ASSISTANT, PATIENT
- Permissoes granulares por funcionalidade
- JWT com expiracao curta (15 min)

### Audit Trail
- `public.audit_log`: registro imutavel de TODA operacao de escrita
- Campos: tenant_id, user_id, action, entity_type, entity_id, changes (JSON diff), ip_address, timestamp
- Retencao: 20 anos (requisito CFO)

### Consentimento
- Campo `lgpd_consent` em pacientes (timestamp, tipo, IP)
- Tela de consentimento no cadastro do paciente
- Registro de consentimento para comunicacao (WhatsApp, SMS, email)

### Direito ao Esquecimento vs Retencao CFO
- Prontuario clinico: retencao obrigatoria de 20 anos (CFO 91/2009)
- Dados pessoais: anonimizacao via `scripts/anonymize_patient.py`
  - Substitui nome, CPF, telefone, email por dados anonimizados
  - Preserva prontuario clinico com referencia anonima
- Portabilidade: `GET /api/v1/patients/{id}/data-export` retorna todos os dados em JSON

### Resposta a Incidentes
- Notificacao a ANPD em 72h (processo documentado)
- Log de incidentes com impacto e medidas tomadas
