# CFO Resolution 91/2009 — Requisitos para Prontuario Digital

## Obrigatorio no Prontuario
1. Identificacao do paciente (nome, CPF, data nascimento)
2. Anamnese (queixa principal, historico medico, historico dental)
3. Exame clinico (odontograma com notacao FDI)
4. Plano de tratamento
5. Evolucoes clinicas (notas de cada atendimento)
6. Prescricoes
7. Atestados
8. Termos de consentimento
9. Radiografias e exames complementares

## Certificacao Digital (NGS2)
- Para eliminar papel: exige certificacao SBIS + certificado digital ICP-Brasil
- Assinatura digital em prontuarios garante autenticidade e integridade
- OdontoFlow: campo `digital_signature` (JSON) em anamnesis, clinical_notes
- Planejado: integracao com Lacuna PKI para ICP-Brasil (Fase 3)

## Retencao
- Minimo 20 anos apos ultimo atendimento
- Prontuarios digitais devem ter backup e protecao contra alteracao
- Registros assinados sao imutaveis (append-only)

## Implementacao no OdontoFlow
- Tabela `patient_records` como aggregate root (um por paciente)
- Tabelas separadas: anamnesis, odontogram_teeth, clinical_notes, prescriptions, consent_forms
- Campo `digital_signature` JSONB para assinatura ICP-Brasil
- Campo `signed_at` torna registro imutavel
- Audit log registra todas alteracoes
