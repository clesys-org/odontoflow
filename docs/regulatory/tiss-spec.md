# TISS/ANS — Integracao com Convenios

## O que e TISS
Troca de Informacao em Saude Suplementar — padrao XML obrigatorio da ANS para comunicacao entre prestadores e operadoras de planos de saude.

## Componentes TISS
1. **Organizacional**: regras de negocio, prazos, fluxos
2. **Conteudo/Estrutura**: schemas XML, campos obrigatorios
3. **Terminologia (TUSS)**: codigos padrao de procedimentos
4. **Seguranca**: assinatura digital, hash de lotes
5. **Comunicacao**: web services para envio/retorno

## Guia Odontologico (GTO)
- Guia especifico para odontologia
- Fluxo: Solicitacao → Autorizacao → Execucao → Cobranca
- Campos: dados do beneficiario, procedimentos (TUSS), dentes, faces

## Codigos TUSS Odontologicos (exemplos)
- 81000030: Consulta odontologica inicial
- 81000065: Urgencia/emergencia
- 82000034: Restauracao em resina (1 face)
- 82000042: Restauracao em resina (2 faces)
- 83000031: Exodontia simples
- 84000038: Tratamento endodontico (1 canal)
- 85000035: Raspagem sub-gengival
- 87000028: Protese total

## Planejamento no OdontoFlow (Fase 3)
- Bounded context `insurance/` dedicado
- Geracao de XML TISS a partir de treatment_items
- Workflow de autorizacao previa
- Faturamento em lote
- Gestao de glosas (rejeicoes)
- Tabela `procedure_catalog` ja inclui tuss_code
