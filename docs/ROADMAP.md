# Roadmap por Capacidades e Gates

Fonte oficial das fases macro. Datas só entram após capacidade/owners; o plano técnico está em `IMPLEMENTATION_PLAN.md` e tarefas em `BACKLOG.md`.

## M0 — Decisões de entrada

**Capacidade:** explicar onde, para quem, sob quais evidências, termos, políticas e responsabilidades o produto opera.

**Entregáveis:** cidade/UF, categoria, público/idade, organização operadora, requisitos locais, política de revisão, jornadas, comercial/cancelamento/no-show/disputa, pareceres, fornecedores a selecionar, métricas e orçamento.

**Gate:** `OPEN-001` está fechado; conteúdo aplicável de `OPEN-002` precisa ser aprovado para iniciar modelos regulados dependentes. Demais decisões têm gates explícitos e owners.

## M1 — Fundação técnica, identidade e confiança

**Capacidade:** executar e auditar o primeiro ciclo cadastral com ambiente reproduzível.

**Entregáveis:** Docker, Django/DRF, Angular, PostgreSQL/PostGIS, Redis/Celery, CI, configuração, health, logs, OpenAPI, auditoria, conta, contatos, sessões, MFA, pessoa, papéis compatíveis com autorização independente, termos/aceites/consentimentos separados e organização.

**Gate:** aplicação reproduzível, CI verde, autorização deny-by-default e ações sensíveis auditáveis.

## M2 — Credenciamento e elegibilidade

**Capacidade:** revisar aplicação/documentos/veículo e publicar somente instrutor internamente elegível.

**Entregáveis:** perfis, aplicação, requisitos versionados, storage/quarentena/scan, veículo, backoffice, suspensão, expiração, política calculada, E2E e acessibilidade.

**Gate do primeiro ciclo:** onboarding e revisão sem edição de banco; perda de requisito retira publicação; documento privado; concorrência/autorização/auditoria testadas.

## Gate M2.1 — Google OIDC opcional

Somente após M2. `ExternalIdentity` já existe inativa. Implementar Google como método adicional, terminar em sessão Django e não substituir verificações/elegibilidade. Nenhum outro provedor.

## M3 — Descoberta, agenda e negociação

**Capacidade:** aluno encontra oferta elegível, propõe condições e obtém hold sem dupla reserva.

**Entregáveis:** área/PostGIS, oferta, disponibilidade/exceções, perfil público, busca/filtros, política comercial versionada, solicitação/proposta, aceite atômico, hold, notificações e cancelamento comercial.

**Gate:** `OPEN-003/007` fechadas; busca nunca vaza inelegível/endereço; concorrência prova reserva única.

## M4 — Pagamento, ledger e receita

**Capacidade:** cobrar via gateway e explicar comissão/líquido/repasse sem custódia.

**Entregáveis:** núcleo de partidas dobradas, recebedor/KYC, checkout, webhook, idempotência, comissão, transferência, reembolso, chargeback, extratos e conciliação.

**Gate:** `OPEN-005` fechada; sandbox/contratos; eventos duplicados/fora de ordem seguros; ledger balanceado; reconciliação e operação de falha aprovadas.

## M5 — Execução, disputa, suporte e reputação

**Capacidade:** encerrar a aula comercial ou o conflito de forma consistente e auditável.

**Entregáveis:** check-in não oficial, conclusão bilateral, no-show, disputa/evidência, denúncia/suporte, efeitos financeiros explícitos, avaliação/moderação e suspensão.

**Gate do MVP funcional:** E2E completo, estados independentes, política aplicada e nenhum fluxo crítico dependente de edição de banco.

## M6 — Hardening e homologação

**Capacidade:** provar que o MVP está apto a receber dados e dinheiro reais sob limites.

**Entregáveis:** dados demo sintéticos, testes de contrato/carga/acessibilidade/segurança, pentest/revisão, ROPA/retenção/direitos, staging, migração, restore/rollback, incident drill, runbooks, treinamento, UAT e release candidate.

**Gate:** `OPEN-004/006/008/009/014` fechadas; zero falha crítica/alta não aceita; restauração e rollback demonstrados; jurídico/privacidade/segurança/finanças/operação aprovam.

## M7 — Piloto controlado

**Capacidade:** validar oferta, demanda, conversão, repetição, margem, segurança e custo operacional numa região.

**Entregáveis:** 20–50 instrutores elegíveis como meta de oferta, aquisição limitada, suporte registrado, conciliação diária, métricas/coortes, revisão semanal e relatório final.

**Gate:** critérios congelados de `PILOT.md`; go, iterate ou no-go registrado. O piloto pode ser interrompido por segurança, fraude, divergência financeira ou operação insustentável.

## M8 — Versão operacional inicial

**Capacidade:** operar continuamente o produto validado.

**Entregáveis:** correções do piloto, SLO/on-call, capacidade/custo, suporte e release sustentáveis, automação de intervenções frequentes, DR periódico e expansão controlada dentro do escopo aprovado.

**Gate:** métricas de confiabilidade e negócio permanecem dentro dos limites por janela aprovada; owners aceitam o risco residual.

## M9 — SaaS do instrutor

Alunos próprios, agenda/link, pacotes, lembretes, calendário, financeiro e assinatura. Exige descoberta própria, novo contrato/preço e evidência de uso semanal além de leads.

## M10 — Integrações oficiais

Consulta Online Senatran, Datavalid, Gov.br ou Detran somente após análise jurídica, finalidade, contrato, documentação, homologação e política de dados. Sem scraping autenticado, credencial do cidadão ou endpoint inventado.

## M11 — Expansão

Novas cidades/UFs/categorias, configuração local, antifraude, suporte/capacidade e eventual app nativo. Cada expansão repete análise regulatória, privacidade, oferta e operação.

## Funcionalidades futuras, não compromissos

Chat em tempo real, biometria, tracking, seguros próprios, IA, precificação dinâmica, microserviços e cobertura nacional. Só entram por nova decisão de escopo, caso validado e análise de risco.

## Critérios de aceite por fase

| Fase   | Evidência de aceite                                                          |
| ------ | ---------------------------------------------------------------------------- |
| M0     | jurisdição, público/idade, decisões/gates/owners e fontes verificadas         |
| M1     | build/test/CI, sessão/CSRF/MFA, aceite ≠ consentimento, papel e auditoria     |
| M2     | E2E de aplicação até elegibilidade, storage privado e expiração/suspensão    |
| M3     | busca minimizada e aceite concorrente cria um hold com snapshot correto      |
| M4     | cobrança sandbox/E2E, webhook seguro, ledger/reembolso/repasse reconciliados |
| M5     | conclusão/no-show/disputa/denúncia/avaliação respeitam policy e autorização  |
| M6     | UAT, segurança/LGPD, restore/rollback, observabilidade e runbooks aprovados  |
| M7     | relatório e decisão por métricas congeladas, sem incidente intolerável       |
| M8     | SLO/custo/suporte sustentáveis e DR/release periódicos                       |
| M9–M11 | caso próprio, ADR/escopo, riscos e gates antes da implementação              |

## Ordem proibida

Não antecipar marketplace antes de M2, pagamento antes das decisões de M4, piloto antes de M6, nem microserviços/app/IA/biometria/múltiplos Detrans/expansão antes de evidência e nova aprovação.

## Capacidades consolidadas em 2026-08-19

- **M2:** preparar entrada de candidato e evidência oficial sem automatizar autoridade pública.
- **M3:** incluir `StudentDemand`, mapa/lista de oferta, agregados de demanda e matching determinístico antes da negociação.
- **M7:** medir densidade local, razão demanda/oferta e conversão de matches no piloto.
- **M9:** evoluir Academia do Instrutor, SaaS e possíveis parcerias educacionais somente após validação.
- **M10:** ativar integrações oficiais documentadas/contratadas, mantendo fallback manual auditável.
- **M11:** usar dados agregados para expansão geográfica controlada.

IA de ranking/matching permanece posterior ao MVP e depende de dados, avaliação de privacidade, explicabilidade, testes de viés/qualidade e feature flag.

## Repriorização 19/08/2026

- Produto nasce nacional; primeira onda técnica/comercial: RS, SC, SP, RJ e ES. AM, RO, AC e RR permanecem na matriz regulatória sem ativação automática.
- Antes do marketplace público: consolidar matriz federal + primeira onda para instrutores, clínicas, médicos e psicólogos.
- Incorporar perfis de clínica/profissionais e Jornada CNH sem armazenar resultados clínicos no MVP.
- “Quero me tornar instrutor” e Academia do Instrutor saem do MVP e retornam somente após decisão de roadmap.
- Ativação de novas UFs é configuração + gate regulatório/operacional, não projeto de reescrita.
