# Checkpoint do Projeto

- Atualizado em: **2026-08-30**
- Versão documental: **3.3**
- Código-fonte: **CODEX 02E e configuração administrativa GOV-004 concluídos; fundações anteriores preservadas**

## Consolidação de produto em 2026-08-19

Foram incorporados à documentação, sem liberar código nem remover gates existentes: mapa/lista de instrutores, demanda declarada por alunos, agregados geográficos de demanda, matching determinístico, captação de instrutores autorizados, funil de candidatos, registro de verificação oficial por fonte documentada/manual e Academia do Instrutor como hub orientativo. Novas decisões `ADR-021–026`, questões `OPEN-015–019` e riscos `R-026–030` foram registrados.

A fase continua **M0**, com `GOV-001/OPEN-001` concluído. Esta consolidação não autoriza scraping de portais públicos, IA no caminho crítico, publicação sem elegibilidade nem implementação antes dos gates.

## Fase atual

**INSTRUTORPRO DEMO 01 concluída.** O frontend contém experiência visual navegável e mobile-first apenas com fixtures sintéticas. CODEX 01, 02A e 02B permanecem preservados; CODEX 02C está suspenso e não deve ser retomado sem autorização explícita. Capacidades reguladas, usuários reais, perfis e publicação continuam condicionados aos respectivos gates.

## Últimas atividades concluídas

`BCR-06/CERTIFICADO` resolvido em 30/08/2026: o certificado ECDSA da Let's Encrypt para
`179.199.136.4`, válido de 29/08/2026 a 04/09/2026, teve cadeia externa validada e renovação
simulada aprovada pelo Certbot às 06:30:47 UTC. O serviço `certbot-renew` já avalia renovação
a cada 12 horas, com webroot compartilhado, e o gateway Nginx recarrega a cada 6 horas.
HTTP→HTTPS, frontend, API, health, readiness, Admin, cookie CSRF `Secure` e headers de
segurança foram comprovados. Nenhum certificado foi forçado ou reinstalado; os demais
bloqueadores de produção permanecem independentes.

Verificação de deploy corrigida em 30/08/2026: o readiness interno executado pelo container frontend
passa a declarar `X-Forwarded-Proto: https`, evitando que o redirecionamento seguro `301` seja tratado
como indisponibilidade. A exigência de HTTPS permanece ativa e não foi afrouxada.

Mapa agregado nacional refinado em 30/08/2026: a ilustração conceitual foi substituída pela malha
local das 27 UFs obtida do IBGE, com seleção estadual e detalhamento por cidade. Somente RS, SC, SP,
RJ e ES recebem marcadores e contagens sintéticas; as demais UFs ficam neutras, sem sugerir ativação
operacional. A seleção de uma UF ativa encaminha à busca local de instrutores com a capital demo já
informada; o mapa de destino consulta somente publicações sintéticas. Nenhuma demanda ou localização
individual real foi adicionada.

Experiência visual da busca de instrutores refinada em 30/08/2026: entrada por cidade/bairro/CEP,
mapa Leaflet amplo, marcadores identificáveis, filtros, painel de resultados e alternância móvel
mapa/lista. A interface preserva identidade InstrutorPro, minimização sem GPS automático e dados
exclusivamente sintéticos; não altera elegibilidade, provider de produção, publicação real ou os
gates de `OPEN-007`.

Exceção temporária do painel autorizada em 29/08/2026 para avaliação por sócios e colaboradores:
MFA pode ser desativado somente no servidor de demonstração com dados sintéticos por flag segura por
padrão. Senha, staff, permissões explícitas, Axes, sessão curta e auditoria permanecem. Enquanto a
flag estiver desativada, `ADMIN-PROD-01` continua `NOT READY` e nenhum dado/profissional/publicação
real é permitido; reativar MFA é condição anterior a produção.

Configuração administrativa GOV-004 implementada em 29/08/2026 no app `organizations`:
`PlatformOrganization` singleton, CNPJ validado/normalizado, estados
`INCOMPLETE/PENDING_VALIDATION/VALIDATED`, edição e validação com permissões separadas,
lock/versão, auditoria redigida e Django Admin reutilizado. Migration
`organizations/0002_platformorganization.py` aplicada somente no banco local. Nenhum
dado real foi semeado, nenhum endpoint público, upload, deploy ou liberação de BCR-02 foi
criado. Foram aprovados 11 testes direcionados e 83 testes backend completos.

Dados organizacionais adicionais declarados pelo responsável humano em 29/08/2026:
razão social `FOCUS INFORMATICA E CELULAR LTDA`, endereço parcial
`RUA MATO GROSSO 1660`, representante parcial `Gilmar Cesar` e contato operacional
`64996765431`. O registro é documental e mantém pendentes comprovação, endereço completo,
nome civil/qualidade de representação e homologação do canal; nenhum dado foi gravado no
banco ou exposto pelo painel administrativo.

Cotação controlada para Encarregado/DPO externo enviada em 29/08/2026 a Seusdados,
Omnisblue e Global Data Solutions, com mensagem uniforme e matriz de avaliação. Os três
envios foram confirmados; as propostas continuam pendentes. Nenhum fornecedor foi
escolhido, nenhum contrato/custo foi aceito e nenhum dado de instrutor foi compartilhado.

Modelo de Encarregado/DPO externo independente aprovado em 29/08/2026, sem seleção de
fornecedor, contrato ou cobrança. A identidade e o ato formal continuam pendentes antes
de dados reais.

Exigência de Encarregado/DPO formal antes de dados reais aprovada em 29/08/2026. O canal
`focusgtba@gmail.com` permanece válido para contato inicial, mas não é nomeação. Pessoa ou
serviço, ato formal, substituição, recursos e avaliação de conflito continuam pendentes;
nenhum DPO foi inventado ou considerado designado.

Procedimento `GOV002-RS-INSTRUCTOR` aprovado por decisão humana em 29/08/2026 somente
para M1 Porto Alegre/categoria B: consulta manual voluntária sem upload, revalidação a
cada 24 horas e tolerância de 72 horas para indisponibilidade. A linha passou a
`APPROVED`; as outras 19 permanecem inalteradas. O tabletop GOV-003 foi repetido e obteve
`PASS` no mesmo recorte, com self-review/conflito ainda exigindo pessoa distinta. Isso não
libera dados reais ou implementação.

Operador/controlador do M1 registrado em 29/08/2026 como pessoa jurídica, CNPJ
`10.280.826/0001-05`, e canal inicial de privacidade `focusgtba@gmail.com`. A decisão não
comprova as declarações posteriores de razão social, representação e endereço parcial,
nem designa DPO. O caminho mínimo RS foi
reduzido: consulta manual oficial pode dispensar upload/storage/scanner no primeiro
instrutor se o procedimento proposto for aprovado; segundo revisor só é bloqueante para
self-review, relação ou conflito. Nenhum dado real ou código foi ativado.

Prontidão pré-produção M1 inicialmente avaliada em 29/08/2026 com resultado **`NOT READY`**. A análise
focada em Porto Alegre/RS consolidou seis bloqueadores reais: regra/operação RS,
operador/LGPD/jurídico, segregação, cadastro/documentos reais, MapTiler contratual e
plataforma segura de produção. A fonte oficial do DetranRS confirma categoria B e lista
de IA autorizados; naquela avaliação `GOV002-RS-INSTRUCTOR` ainda não tinha aprovação
nominal. A decisão posterior registrada acima substitui esse bloqueio, sem ativar dado
real, código, migration, deploy ou integração.

Tabletop obrigatório `GOV-003` do piloto M1 executado documentalmente em 29/08/2026,
com Gilmar Cesar Alves atuando separadamente nas cinco funções provisórias e Codex apenas
como facilitador/relator. O cenário e suas variantes usaram somente evidência sintética.
Resultado: **`FAIL`**. Permanecem abertos F-001 a F-006: linha `RS/INSTRUCTOR` não
aprovada, falta de revisor independente, validação jurídica externa, storage/scanner real,
tolerância da fonte e comprovação organizacional/DPO. Nenhuma elegibilidade, revisão ou publicação
real foi liberada.

Decisões territoriais e de provider do M1 registradas em 29/08/2026: Porto Alegre/RS é
o primeiro território operacional controlado, sem limitar a arquitetura nacional;
MapTiler Cloud Flex é o provider preferencial condicionado, com PostGIS como fonte de
verdade, geocoding no backend, Leaflet, sem GPS e fallback de busca/lista por Porto Alegre.
`OPEN-007` não é mais uma escolha genérica, mas produção permanece bloqueada até aceite
do plano/DPA, subprocessadores, países/transferência, retenção da consulta, endpoint
europeu, chaves/limites e testes. Nenhuma integração ou dado real foi ativado.

Gate LGPD mínimo da busca de instrutores documentado em 29/08/2026. Foram aprovados
somente a busca com dados sintéticos e o desenho minimizado: pesquisa sem login por
cidade/bairro/CEP explícito, sem GPS automático, histórico individual, saúde ou residência
pública; localização de serviço do instrutor permanece separada, granular, auditada e
revogável. O ROPA mínimo foi registrado. Busca e profissional reais continuam bloqueados
por LIA/RIPD, organização/canal, retenção, provider, segurança, elegibilidade e gates
regulatórios/operacionais; `OPEN-007` não foi fechado.

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

Marketplace Core M1 autorizado em execução somente com dados sintéticos. A primeira fatia criou
`StudentProfile`, `StudentDemand`, `InstructorVehicle`, aceite de pré-requisitos e `LessonRequest`,
com sessão de aluno DEMO, agregação de demanda por limiar configurável, transições auditadas e tela
funcional em `/aluno/demanda`. As flags de cadastro/publicação/demanda real permanecem `false` por
padrão. `OPEN-015` não foi resolvido: o valor `3` existe apenas nos exemplos/testes sintéticos.

Correção funcional executada em 30/08/2026: landing e header agora expõem encontrar instrutor,
entrar, criar conta, aluno e profissional; cadastro de aluno persiste `Account`, `Person`, papel
`STUDENT` e `StudentProfile`; login por e-mail cria sessão e direciona à área do papel. O onboarding
do instrutor possui pré-requisito e seis etapas, cria conta acessível, veículo e aceite sintéticos,
área de atendimento, perfil `SUBMITTED/UNPUBLISHED` e exibe status `EM ANÁLISE`. O registro permanece
visível no Django Admin protegido por MFA. Fluxos foram verificados no navegador local e no banco;
nenhuma flag real foi ativada e nenhum deploy Ubuntu foi realizado.

O certificado Let's Encrypt do endpoint `179.199.136.4` teve renovação simulada com sucesso em
30/08/2026; o mecanismo Docker `certbot-renew` verifica a cada 12 horas e o gateway recarrega a cada
6 horas. Essa evidência não equivale a domínio registrado nem amplia o gate de produção.

## Próxima atividade

Completar a fatia autorizada do Marketplace Core M1 com integração do onboarding/veículo, painel de
solicitações do instrutor, clusters nacionais de instrutores, agregados hierárquicos de demanda e
testes frontend/E2E proporcionais. Depois, apresentar evidências e plano de implantação e parar para
autorização humana. Não fazer deploy, não ativar flags reais e não retomar `IAM-003`/CODEX 02C.

## Decisões abertas

| ID       | Classe         | Resumo                                                          | Gate                 |
| -------- | -------------- | --------------------------------------------------------------- | -------------------- |
| OPEN-002 | resolvido M1 / bloqueante demais escopos | RS/Porto Alegre/B aprovado; demais linhas pendentes | A14/M2 |
| OPEN-003 | bloqueante     | comissão, hold, cancelamento, no-show, conclusão e disputa      | B5/B6/M3             |
| OPEN-004 | bloqueante     | responsabilidade, consumo, vínculo, seguro, termos e bases LGPD | usuários reais/M6    |
| OPEN-005 | bloqueante     | gateway, split/KYC, tributação e política contábil              | C1/M4                |
| OPEN-006 | parcial        | provider real, contratos, regiões e suboperadores; simuladores liberados para desenvolvimento | provider real/A14/M6 |
| OPEN-007 | condicional/bloqueante produção | MapTiler escolhido; faltam contrato/DPA, subprocessadores, países, retenção, endpoint e testes | B1/M3 |
| OPEN-008 | bloqueante     | retenção, direitos e papéis de tratamento                       | produção/M6          |
| OPEN-009 | bloqueante     | SLO, RPO/RTO, suporte, orçamento e limites                      | piloto/M6            |
| OPEN-010 | bloqueante     | metas, duração, coortes e go/no-go do piloto                    | M7                   |
| OPEN-011 | não bloqueante | biblioteca/política OIDC Google                                 | Gate M2.1            |
| OPEN-012 | não bloqueante | nome, marca e domínio                                           | produção pública/VOI |
| OPEN-013 | não bloqueante | modelo SaaS do instrutor                                        | pós-piloto/M9        |
| OPEN-014 | diferido       | menores bloqueados no MVP; mecanismo/política para expansão futura | expansão com menores |

Detalhes, recomendação, alternativas, impactos e owner estão em `DECISIONS.md`.

## Bloqueios

- `GOV002-RS-INSTRUCTOR` e o tabletop passaram no recorte M1; qualquer outra linha/escopo continua bloqueada por `OPEN-002`;
- operador PJ/CNPJ, razão social declarada e canais iniciais estão definidos; comprovação, endereço completo, representação, DPO e documentos aplicáveis permanecem pendentes para homologação/produção;
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
