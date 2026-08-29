# Checkpoint do Projeto

- Atualizado em: **2026-08-29**
- Versão documental: **2.8**
- Código-fonte: **CODEX 02E concluído; fundações anteriores preservadas**

## Consolidação de produto em 2026-08-19

Foram incorporados à documentação, sem liberar código nem remover gates existentes: mapa/lista de instrutores, demanda declarada por alunos, agregados geográficos de demanda, matching determinístico, captação de instrutores autorizados, funil de candidatos, registro de verificação oficial por fonte documentada/manual e Academia do Instrutor como hub orientativo. Novas decisões `ADR-021–026`, questões `OPEN-015–019` e riscos `R-026–030` foram registrados.

A fase continua **M0**, com `GOV-001/OPEN-001` concluído. Esta consolidação não autoriza scraping de portais públicos, IA no caminho crítico, publicação sem elegibilidade nem implementação antes dos gates.

## Fase atual

**INSTRUTORPRO DEMO 01 concluída.** O frontend contém experiência visual navegável e mobile-first apenas com fixtures sintéticas. CODEX 01, 02A e 02B permanecem preservados; CODEX 02C está suspenso e não deve ser retomado sem autorização explícita. Capacidades reguladas, usuários reais, perfis e publicação continuam condicionados aos respectivos gates.

## Últimas atividades concluídas

Revisão documental controlada de `GOV-002` registrada em 29/08/2026 para RS, SC, SP,
RJ e ES. A autorização humana permitiu registrar somente decisões suficientemente
sustentadas, mas não aprovou nominalmente nenhuma linha nem selecionou opções da análise
anterior. Resultado conservador: 0 linhas `APPROVED`, 16 permanecem
`HUMAN_REVIEW_REQUIRED` e 4 permanecem `RESEARCH_REQUIRED`. `OPEN-002` continua aberto;
nenhuma elegibilidade, publicação, pessoa real, integração ou funcionalidade foi liberada.

Deploy da demo no Ubuntu preparado em 24/08/2026: Compose isolado do ambiente local,
frontend Angular estático em Nginx, Django/Gunicorn, redes privadas para PostGIS/Redis,
volumes persistentes, configuração não versionada, backup pré-deploy, atualização
fast-forward e smoke/readiness. O ambiente continua exclusivamente sintético; domínio,
TLS e instalação no servidor dependem dos dados/acesso do operador.

CODEX 02E executado em 24/08/2026 com dados exclusivamente sintéticos: serviços
transacionais para submissão, revisão, verificação, publicação, suspensão/despublicação e
autorização/revogação da localização; proteção contra alteração direta; ações do Admin
ligadas aos serviços; onboarding Angular mobile-first em cinco etapas e timeline pós-envio.
O perfil termina enviado e não publicado. CODEX 02C permanece suspenso.

Interface e Admin padronizados para português do Brasil em 24/08/2026. PrimeNG/PrimeUI, que não era usado por componentes da demo e exibia aviso de licença sem chave, foi removido legitimamente; Angular, PrimeIcons, Leaflet e estilos próprios permanecem. Admin recebeu identidade InstrutorPro, nomes e colunas em português e booleanos Sim/Não. Migration `discovery/0003` altera somente metadados de apresentação.

CODEX 02D executado em 24/08/2026 com dados exclusivamente sintéticos: perfil, área pública, autorização, verificação SYNTHETIC, publicação auditada, policy central, Admin protegido e mapa elegível. CODEX 02C permanece suspenso.

MAPA ONLINE 01 executado em 24/08/2026: módulo `discovery`, migration nova, 11 pontos públicos sintéticos nas cinco UFs, geocoder local, busca espacial PostGIS e mapa Leaflet/OpenStreetMap sincronizado com lista e perfil demo. Nenhuma localização automática, pessoa real, elegibilidade, publicação ou CODEX 02C foi implementado.

INSTRUTORPRO DEMO 01 executada em 24/08/2026: landing InstrutorPro, jornada do aluno, descoberta de serviços, mapa/lista e perfil de instrutores fictícios, solicitação visual, matching mock, demanda fictícia, clínicas/exames, entrada profissional, dashboard do instrutor e mapa agregado de demanda. Dados ficam isolados em providers `Demo*`; não houve alteração de backend, migration, login, API, dado real ou integração. Build Angular aprovado, 7 testes frontend aprovados em Chrome Headless e 50 testes backend preservados.

CODEX 02B executado em 24/08/2026: `Account` recebeu estados `ACTIVE/BLOCKED/DEACTIVATED`, coerência com `is_active`, última mudança e versão; serviços internos autorizados implementam ativação, bloqueio e desativação sem exclusão; lock/versão/constraint resolvem concorrência e desativação é terminal nesta fatia. Migration `accounts/0003_alter_account_options_account_lifecycle_changed_at_and_more.py` aplicada. Foram aprovados 50 testes, sem endpoint público ou dados reais.

CODEX 02A executado em 24/08/2026: `RoleAssignment` passou a preservar ciclos de concessão/revogação com atores e motivos; policy exige `people.manage_role_assignments`; comandos transacionais usam lock da pessoa e constraint parcial; auditoria registra grant/revoke e repetições idempotentes. Migration `people/0002_role_assignment_history_and_authorization.py` aplicada. Foram aprovados 31 testes, incluindo concorrência PostgreSQL, sem endpoint público ou dados reais.

Fechamento documental dos gates pré-CODEX 02 em 24/08/2026: `GOV-002` recebeu schema normalizado e 20 linhas conservadoras para RS/SC/SP/RJ/ES, sem nenhuma aprovação operacional; `FIRST_LICENSE/CATEGORY_B` foi confirmada como primeira oferta; papéis funcionais e SLAs de `GOV-003` foram aprovados; tabletop formal foi preparado e permanece não executado; `GOV-004` foi classificado por gates com todos os dados reais desconhecidos em `PENDING_HUMAN_INPUT`. Nenhum código, migration, usuário ou dado real foi alterado.

Autorização humana limitada `PRE-CODEX-02 FOUNDATION` executada em 24/08/2026: migrations novas criaram `Person`, `RoleAssignment`, `Clinic`, `ClinicMembership`, `commercial_status` e `RegulatoryReadiness`; nenhum endpoint público, perfil profissional, usuário real ou aprovação regulatória foi criado. O seed preserva 27 UFs e ativa somente RS/SC/SP/RJ/ES. Testes backend passaram com dados exclusivamente sintéticos.

Rodada documental de preparação do CODEX 02 concluída em 24/08/2026: `OPEN-001` fechado por decisão humana; política multi-papel aprovada; separação futura `commercial_status`/`regulatory_status` definida; estrutura nacional de `GOV-002` aprovada sem aprovar linhas/gaps; owners funcionais, SLA proposto e checklist não executado registrados no `GOV-003`; inventário pendente do `GOV-004`; providers de desenvolvimento/produção separados; política conservadora de menores e dívidas de segurança/frontend documentadas. Nenhum código funcional ou migration foi alterado.

Matriz regulatória inicial `GOV-002` ampliada em 24/08/2026 com **Rondônia, Amazonas, Acre e Roraima**, usando fontes oficiais e estados internos conservadores. A autorização PRE-CODEX-02 posterior manteve a primeira onda somente em RS/SC/SP/RJ/ES; RO/AM/AC/RR continuam sem ativação automática.

Matriz `GOV-002` revalidada e política `GOV-003` criada com estados, segregação, motivos, concorrência, falhas, expiração e contestação. A estrutura nacional de `GOV-002` foi posteriormente aprovada, sem aprovar linhas/gaps; `GOV-003` permanece proposta até tabletop e aceite funcional dos owners.

Identidade visual fornecida pelo responsável do projeto aplicada em 2026-08-24 ao cabeçalho do frontend e registrada em `docs/img/logo.jpg`; o asset substitui o marcador visual provisório sem alterar escopo funcional ou liberar CODEX 02.

Marca operacional e identificadores técnicos renomeados para **InstrutorPro** em 2026-08-23, incluindo interface, API/OpenAPI, Celery, frontend, documentação, CI e banco local. A pesquisa e proteção jurídica de marca/domínio permanecem abertas em `OPEN-012`.

Fundação técnica executável criada em 2026-08-23: Django/DRF com conta customizada e `ExternalIdentity` inativa; `AuditEvent` append-only com ator nulo; catálogo territorial idempotente; PostgreSQL/PostGIS, Redis e Celery; API `/api/v1`, health/readiness, request ID, erros estáveis e OpenAPI; shell Angular/PrimeNG responsivo e acessível; Docker Compose e CI. Foram comprovados migrations sem drift, 27 UFs/5 `FIRST_WAVE`, PostGIS 3.5, worker Celery, 6 testes backend, lint/formatação, schema, build frontend e audit npm sem vulnerabilidades conhecidas.

Auditoria de todos os artefatos do `docs/MANIFEST.json`: hierarquia e responsabilidades definidas; contradições registradas/resolvidas; domínio/API/arquitetura/autorização consolidados; roadmap até operação; plano A–H; backlog implementável; gates de segurança, LGPD, DevOps e piloto.

Revisão jurídico-técnica de privacidade em fontes oficiais vigentes em 22/07/2026: inventário e bases refinados; aceite separado de consentimento; encarregado/LIA/RIPD, cookies, direitos, transferência internacional, Marco Civil, ECA Digital, incidente e decisão automatizada convertidos em controles; `ADR-017–020` e `OPEN-014` registrados. Nenhum parecer ou gate de Legal/Privacy foi presumido como aprovado.

## Atividade em execução

Nenhuma implementação em execução. CODEX 02E terminou; não iniciar outra fatia sem autorização humana e não retomar CODEX 02C. `OPEN-007`, elegibilidade e LGPD bloqueiam localizações/profissionais reais.

## Próxima atividade

Receber autorização explícita para qualquer próximo passo. O próximo gate documental
previsto é executar o tabletop obrigatório de `GOV-003`, em etapa separada; ele não foi
executado nesta revisão. Não retomar automaticamente inventário/revogação interna de
sessões (`IAM-003`/CODEX 02C). Antes de elegibilidade/publicação, ainda é necessário
aprovar nominalmente as linhas aplicáveis de `GOV-002` e executar/aprovar o tabletop de
`GOV-003`.

## Decisões abertas

| ID       | Classe         | Resumo                                                          | Gate                 |
| -------- | -------------- | --------------------------------------------------------------- | -------------------- |
| OPEN-002 | bloqueante     | requisitos locais e política de revisão                         | A14/M2               |
| OPEN-003 | bloqueante     | comissão, hold, cancelamento, no-show, conclusão e disputa      | B5/B6/M3             |
| OPEN-004 | bloqueante     | responsabilidade, consumo, vínculo, seguro, termos e bases LGPD | usuários reais/M6    |
| OPEN-005 | bloqueante     | gateway, split/KYC, tributação e política contábil              | C1/M4                |
| OPEN-006 | parcial        | provider real, contratos, regiões e suboperadores; simuladores liberados para desenvolvimento | provider real/A14/M6 |
| OPEN-007 | bloqueante     | mapa, precisão e retenção de geolocalização                     | B1/M3                |
| OPEN-008 | bloqueante     | retenção, direitos e papéis de tratamento                       | produção/M6          |
| OPEN-009 | bloqueante     | SLO, RPO/RTO, suporte, orçamento e limites                      | piloto/M6            |
| OPEN-010 | bloqueante     | metas, duração, coortes e go/no-go do piloto                    | M7                   |
| OPEN-011 | não bloqueante | biblioteca/política OIDC Google                                 | Gate M2.1            |
| OPEN-012 | não bloqueante | nome, marca e domínio                                           | produção pública/VOI |
| OPEN-013 | não bloqueante | modelo SaaS do instrutor                                        | pós-piloto/M9        |
| OPEN-014 | diferido       | menores bloqueados no MVP; mecanismo/política para expansão futura | expansão com menores |

Detalhes, recomendação, alternativas, impactos e owner estão em `DECISIONS.md`.

## Bloqueios

- conteúdo regulatório por linha ainda precisa de aprovação humana antes de elegibilidade/publicação (`OPEN-002`);
- tabletop de `GOV-003` não foi executado; os SLAs já estão aprovados, mas a operação real continua bloqueada;
- dados da organização operadora permanecem `PENDING_HUMAN_INPUT`; não bloqueiam desenvolvimento sintético, apenas homologação/produção conforme o gate;
- provider real continua bloqueado até decisão contratual, mas adapters/simuladores estão liberados para desenvolvimento (`OPEN-006`);
- menores permanecem bloqueados no MVP; `OPEN-014` não bloqueia desenvolvimento sintético para adultos, mas bloqueia qualquer expansão/cadastro operacional de menores.

Os demais bloqueios são diferidos até seus gates; não impedem pesquisa/decisões M0, mas impedem a fase dependente.

## Riscos ativos

Prioridade imediata: `R-001` publicação irregular, `R-003` responsabilidade jurídica, `R-005` LGPD sem base/agente/retenção/transferência, `R-012` risco de custódia, `R-015` recuperação não provada, `R-016/017` densidade/economia, `R-019` suporte, `R-021` mudança regulatória, `R-024` métricas retroativas e `R-025` menor sem proteção/aferição adequada. Registro completo em `RISKS.md`.

## Documentos que precisam ser atualizados

- Após `GOV-001`: `SCOPE.md`, `PILOT.md`, `DECISIONS.md`, `RISKS.md`, `REFERENCES.md` e este checkpoint.
- Após `GOV-002/003`: `DOMAIN.md`, `AUTHORIZATION.md`, `TEST_STRATEGY.md`, `BACKLOG.md` e este checkpoint.
- Após `GOV-004/005`: `LGPD.md`, `DOMAIN.md`, `API.md`, `DECISIONS.md`, `RISKS.md`, termos/avisos e este checkpoint; fechar ou manter explicitamente `OPEN-004/008/014`.
- Após cada decisão/implementação: somente fontes afetadas, OpenAPI/README técnico quando houver código, e este checkpoint.

Não há documento conhecido pendente desta auditoria; as atualizações acima dependem de decisões ainda não disponíveis.

## Critério do primeiro ciclo

Pessoa cria conta, verifica contatos, aceita termos e recebe `INSTRUCTOR` conforme policy de compatibilidade, sem herdar permissões de outros papéis; preenche perfil/aplicação próprios, envia documentos/veículo, submete, recebe pendência, corrige, é aprovada, fica elegível/publicável nesse papel e perde a publicação quando requisito deixa de valer — sem edição manual de banco, com autorização, privacidade, auditoria, testes e operação observável.

## Gate seguinte

Marketplace (M3) somente após M2 aceito. Google é gate opcional M2.1. Pagamento só após `OPEN-005`; piloto só após M6 e checklist de `PILOT.md`.

## Regra de retomada

1. Ler `README.md`, `DECISIONS.md`, `IMPLEMENTATION_PLAN.md`, `BACKLOG.md` e este arquivo.
2. Executar somente o próximo gate documental liberado (`GOV-002/003/004`) ou, após autorização humana explícita, a primeira fatia delimitada do CODEX 02.
3. Scaffold/fundação pode seguir somente conforme `CODEX_01_FOUNDATION.md`; não liberar capacidades reguladas, usuários reais ou publicação antes dos respectivos gates.
4. Ao concluir uma tarefa: validar, atualizar fontes/checkpoint, revisar diff e criar commit convencional.
