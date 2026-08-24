# Backlog Priorizado

## CODEX 02E — concluído em 24/08/2026

- [x] serviços auditados para perfil, verificação, publicação e localização;
- [x] campos críticos somente leitura no Admin e ações conectadas aos serviços;
- [x] onboarding Angular DEMO em cinco etapas integrado a `SUBMITTED`;
- [x] fluxo sintético até publicação, suspensão e remoção das buscas;
- [ ] profissionais reais continuam bloqueados por regulação, LGPD e operação.

## CODEX 02D — concluído em 24/08/2026

- [x] perfil, área, autorização, verificação, publicação e policy central sintéticos;
- [x] mapa, Admin protegido, histórico, auditoria e testes;
- [ ] `OPEN-007` e dados/verificação reais continuam bloqueados.

## MAPA ONLINE 01 — concluído em 24/08/2026

- [x] localização pública sintética separada da privada;
- [x] geocoding local e busca PostGIS por raio/filtros;
- [x] Leaflet/OpenStreetMap por provider e mapa/lista sincronizados;
- [x] 11 instrutores demo em RS/SC/SP/RJ/ES;
- [ ] provider e profissionais reais permanecem bloqueados por `OPEN-007`, elegibilidade e LGPD.

## INSTRUTORPRO DEMO 01 — concluída em 24/08/2026

- [x] landing InstrutorPro e entradas de aluno/profissional;
- [x] jornada, serviços, instrutores, solicitação, matching e demanda sintéticos;
- [x] clínicas/exames sem dados clínicos;
- [x] dashboard do instrutor e demanda agregada RS/SC/SP/RJ/ES;
- [x] providers demo isolados, responsividade, build e testes;
- [x] regressão das fundações CODEX 01/02A/02B;
- [ ] evolução da demo ou retomada de CODEX 02C exige autorização humana.

Não libera marketplace, login público, persistência, matching definitivo,
publicação regulatória, pagamentos ou integrações oficiais.

Fonte oficial das unidades implementáveis. Prioridade: `P0` bloqueia a sequência; `P1` compõe o caminho crítico; `P2` entra após o gate indicado. Cada tarefa termina em estado executável e commit próprio/coerente conforme `AGENTS.md`.

## M0 — Governança e decisões

### GOV-001 — Fixar jurisdição e categoria (`P0`)

- **Estado em 24/08/2026: CONCLUÍDO POR DECISÃO HUMANA.** Arquitetura nacional; primeira onda técnica RS/SC/SP/RJ/ES conforme autorização PRE-CODEX-02; demais UFs sem ativação automática; nenhuma cidade estrutural; primeira oferta priorizada primeira habilitação/categoria B.

- **Objetivo/contexto:** escolher cidade/UF e categoria inicial; sem isso requisitos e piloto seriam genéricos.
- **Dependências:** owners de Product, Operations e Compliance.
- **Arquivos/módulos:** `SCOPE`, `PILOT`, `DECISIONS`, `CHECKPOINT`.
- **Aceite:** decisão, fontes, data, responsável e consequência registradas; `OPEN-001` fechada.
- **Testes necessários:** revisão cruzada de escopo, regra local e capacidade operacional.
- **Concluído quando:** documentos afetados estão consistentes, revisados e commitados.

### GOV-002 — Aprovar matriz documental local (`P0`)

- **Estado em 24/08/2026:** estrutura e schema normalizado aprovados; 20 linhas da primeira onda classificadas como `HUMAN_REVIEW_REQUIRED`/`RESEARCH_REQUIRED`; nenhuma linha operacionalmente aprovada. Não bloqueia fundação sintética, mas bloqueia elegibilidade/publicação regulada.

- **Objetivo/contexto:** listar evidências, validade, substituição e fonte oficial para publicação; a plataforma não cria credenciamento.
- **Dependências:** `GOV-001`.
- **Arquivos/módulos:** `DOMAIN`, `LGPD`, `REFERENCES`, futura configuração `compliance`.
- **Aceite:** cada requisito tem jurisdição/categoria/vigência/obrigatoriedade/fonte e dado mínimo; `OPEN-002` parcialmente fechada.
- **Testes necessários:** revisão de completude, expiração, conflito de vigência e minimização.
- **Concluído quando:** Compliance/Legal aprovam a matriz versionada e impacto de mudança.

### GOV-003 — Aprovar política de revisão e aplicação ativa (`P0`)

- **Estado em 24/08/2026:** papéis funcionais e SLAs iniciais aprovados; tabletop formal preparado e não executado. Operação real de revisão/publicação continua bloqueada até execução e aprovação final.

- **Objetivo/contexto:** definir evidência, segregação, motivos, SLA e conceito de aplicação ativa sem inventar fluxo no código.
- **Dependências:** `GOV-002`.
- **Arquivos/módulos:** `DOMAIN`, `AUTHORIZATION`, `TEST_STRATEGY`, futura app `instructors`.
- **Aceite:** transições/autoridades, self-review, pendência, suspensão, expiração e recurso/reativação estão definidos.
- **Testes necessários:** tabletop de casos feliz, documento inválido, expiração, conflito e abuso interno.
- **Concluído quando:** `OPEN-002` fechada e decisão registrada.

### GOV-004 — Identificar organização e responsáveis (`P0`)

- **Estado em 24/08/2026:** estrutura e gates aprovados; campos reais permanecem `PENDING_HUMAN_INPUT`. GOV-004 não bloqueia desenvolvimento exclusivamente sintético, mas bloqueia homologação aplicável/produção conforme a tabela do documento.

- **Objetivo/contexto:** impedir termos, finanças e privacidade ligados a entidade fictícia.
- **Dependências:** nenhuma técnica.
- **Arquivos/módulos:** `BUSINESS_MODEL`, `LGPD`, `RISKS`, futura app `compliance`.
- **Aceite:** organização operadora e owners Legal/Privacy/Security/Finance/Operations formalmente identificados ou bloqueio explícito mantido.
- **Testes necessários:** revisão de segregação e contatos de escalonamento.
- **Concluído quando:** owner de cada gate crítico consta nos registros.

### GOV-005 — Mapear pareceres e documentos jurídicos (`P0`)

- **Objetivo/contexto:** separar o que permite desenvolvimento sintético do que bloqueia usuários/dinheiro reais.
- **Dependências:** `GOV-004`.
- **Arquivos/módulos:** `BUSINESS_MODEL`, `LGPD`, `SECURITY`, `DECISIONS`.
- **Aceite:** lista de pareceres/termos, responsáveis, gate e evidência de aprovação; aceite separado de consentimento; público/idade e incidência do ECA Digital decididos; nenhum disclaimer tratado como parecer.
- **Testes necessários:** revisão de cobertura consumerista, civil, trabalhista, fiscal, pagamentos, LGPD, Marco Civil e ECA Digital aplicável.
- **Concluído quando:** `OPEN-004/008/014` têm plano e gate verificável.

### GOV-006 — Definir abstrações e fornecedores estruturais (`P0`)

- **Estado em 24/08/2026:** adapters/simuladores liberados para desenvolvimento; nenhum provider comercial escolhido. Seleção, contratos, regiões e suboperadores continuam gate de provider real/produção.

- **Objetivo/contexto:** permitir ambiente local sem acoplar produção prematuramente.
- **Dependências:** `GOV-004`; necessidades de `GOV-002`.
- **Arquivos/módulos:** `ARCHITECTURE`, `INTEGRATIONS`, `DEVOPS`, futura `integrations`.
- **Aceite:** fakes locais e critérios de seleção para storage/scan/mensagem/observabilidade definidos; segredos/regiões separados.
- **Testes necessários:** contract-test plan e falhas esperadas.
- **Concluído quando:** A1 pode iniciar sem fornecedor implícito e `OPEN-006` tem caminho aprovado.

## M1 — Fundação, identidade e confiança

### FND-001 — Criar scaffold backend (`P1`)

- **Objetivo/contexto:** iniciar Django/DRF com custom user antes da primeira migration.
- **Dependências:** `GOV-001–006` liberadas no checkpoint.
- **Arquivos/módulos:** `backend/config`, `backend/apps/accounts`, lockfiles, `.env.example`.
- **Aceite:** configurações por ambiente, custom user vazio funcional, `/api/v1` e comando de check.
- **Testes necessários:** startup, config ausente, migration check e segredo fora do repo.
- **Concluído quando:** ambiente sobe reproduzivelmente e documentação/comandos estão registrados.

### FND-002 — Provisionar dependências locais (`P1`)

- **Objetivo/contexto:** banco real de integração, geografia e assíncrono desde a fundação.
- **Dependências:** `FND-001`.
- **Arquivos/módulos:** `compose.yaml`, Dockerfiles, config PostgreSQL/PostGIS/Redis/Celery.
- **Aceite:** web, banco, worker e scheduler ficam healthy; Redis não guarda estado irrecuperável.
- **Testes necessários:** conexão, PostGIS, task smoke, reinício e persistência do banco.
- **Concluído quando:** setup novo funciona por comandos documentados.

### FND-003 — Implantar baseline de qualidade e API (`P1`)

- **Objetivo/contexto:** falhar cedo em erro, contrato e insegurança básica.
- **Dependências:** `FND-001/002`.
- **Arquivos/módulos:** CI, formatter/lint/type config, pytest, OpenAPI, health/readiness, middleware request ID.
- **Aceite:** pipeline verifica formato, lint, testes, migration, secrets, build e schema; erro segue `API.md`.
- **Testes necessários:** health/readiness degradados, request ID válido/inválido e schema snapshot.
- **Concluído quando:** CI local/remota aplicável está verde.

### FND-004 — Criar shell Angular/PWA (`P1`)

- **Objetivo/contexto:** estabelecer cliente seguro/acessível sem antecipar regras.
- **Dependências:** contrato básico de `FND-003`.
- **Arquivos/módulos:** `frontend/src/app/{core,shared,auth}`, config e testes.
- **Aceite:** rotas, CSRF, tratamento de erro/request ID, loading/empty states e acessibilidade base.
- **Testes necessários:** unit/component, build, navegação por teclado e sessão expirada.
- **Concluído quando:** build reproduzível integrado à CI.

### AUD-001 — Implementar auditoria base (`P1`)

- **Objetivo/contexto:** permitir que toda ação sensível posterior já nasça rastreável.
- **Dependências:** `FND-003`.
- **Arquivos/módulos:** `apps/audit/{models,services,selectors,policies,api,tests}`.
- **Aceite:** `AuditEvent` append-only, ator sistema/humano, request ID, ação/alvo/motivo e redação.
- **Testes necessários:** append, imutabilidade lógica, autorização, ausência de segredos e correlação.
- **Concluído quando:** API/admin mínimo seguro e migration/testes/OpenAPI estão verdes.

### IAM-001 — Implementar conta e sessão (`P1`)

- **Estado parcial CODEX 02B em 24/08/2026:** lifecycle interno de Account concluído com estados, deny-by-default, permissionamento explícito, idempotência, concorrência, constraint e auditoria. Cadastro/login/logout público, sessão, CSRF, antienumeração e rate limit permanecem fora desta fatia.

- **Objetivo/contexto:** autenticação local segura sem papel enviado pelo cliente.
- **Dependências:** `AUD-001`.
- **Arquivos/módulos:** `accounts` models/services/policies/api/tests; telas auth.
- **Aceite:** cadastro, login/logout, estados, cookie/CSRF, antienumeração e rate limit.
- **Testes necessários:** sucesso, credencial inválida, bloqueio, CSRF, fixation/rotação e mass assignment.
- **Concluído quando:** sessão segura e contrato OpenAPI passam na CI.

### IAM-002 — Verificar contatos e recuperar acesso (`P1`)

- **Objetivo/contexto:** provar posse de canal sem persistir OTP claro.
- **Dependências:** `IAM-001`, fake/porta de mensagens.
- **Arquivos/módulos:** `ContactVerificationChallenge`, notifications/integrations, telas.
- **Aceite:** finalidade única, hash, expiração, tentativas, consumo, resend e resposta antienumeração.
- **Testes necessários:** replay, concorrência, expiração, limite, provider failure e log redaction.
- **Concluído quando:** e-mail/telefone/reset funcionam com fake e auditoria.

### IAM-003 — Inventariar e revogar sessões (`P1`)

- **Objetivo/contexto:** interromper acesso após risco/bloqueio.
- **Dependências:** `IAM-001`.
- **Arquivos/módulos:** sessão/selector/API `/me/sessions`; frontend.
- **Aceite:** lista mascarada, revogação própria, global em eventos definidos e objeto alheio oculto.
- **Testes necessários:** revogação concorrente, sessão atual/outra, bloqueio e autorização.
- **Concluído quando:** sessão revogada não autentica e evento é auditado.

### IAM-004 — Implementar MFA privilegiada (`P1`)

- **Objetivo/contexto:** proteger revisão/admin/financeiro antes de ativar funções internas.
- **Dependências:** `IAM-002/003`; política de recuperação aprovada.
- **Arquivos/módulos:** accounts/security, API MFA, interface administrativa.
- **Aceite:** enrollment, desafio, recuperação, reautenticação e sessão privilegiada conforme policy.
- **Testes necessários:** replay, brute force, recovery, clock/expiração, revogação e bypass negado.
- **Concluído quando:** ação marcada não executa sem MFA recente.

### IAM-005 — Preparar identidade externa inativa (`P1`)

- **Objetivo/contexto:** evitar migration insegura futura sem oferecer login Google agora.
- **Dependências:** `IAM-001`.
- **Arquivos/módulos:** `ExternalIdentity` model/domain/tests.
- **Aceite:** provider/subject único, dono único, metadado mínimo e nenhum token/rota/UI.
- **Testes necessários:** constraints, concorrência e varredura de endpoints/segredos ausentes.
- **Concluído quando:** estrutura migra e permanece inacessível ao usuário.

### IAM-006 — Organização, termos, aceites e consentimentos (`P1`)

- **Objetivo/contexto:** vincular aceite à organização/texto/versionamento reais.
- **Dependências:** `GOV-004/005`, `AUD-001`.
- **Arquivos/módulos:** `compliance` models/services/API e frontend legal.
- **Aceite:** uma organização ativa configurada; documento vigente/hash; `LegalAcceptanceRecord` obrigatório separado de `ConsentRecord` opcional, granular e retirável.
- **Testes necessários:** vigência concorrente, versão antiga, público errado, aceite não criando consentimento, retirada equivalente, finalidade distinta e auditoria.
- **Concluído quando:** aceite/consentimento apontam à versão exata e nenhum é usado como prova do outro.

### IDN-001 — Implementar pessoa protegida (`P1`)

- **Objetivo/contexto:** separar identidade civil de autenticação.
- **Dependências:** `IAM-001/006`; decisão de proteção de CPF.
- **Arquivos/módulos:** `people` model/service/policy/API; formulário.
- **Aceite:** propriedade 1:1, normalização/proteção, resposta mascarada e edição permitida.
- **Testes necessários:** unicidade aprovada, autorização, logs, validação e concorrência.
- **Concluído quando:** dado completo não vaza e migration/testes passam.

### IDN-002 — Implementar papéis pessoais compatíveis (`P1`)

- **Estado CODEX 02A concluído em 24/08/2026:** grant/revoke internos, deny-by-default, histórico, idempotência, lock/constraint, auditoria e testes concorrentes concluídos. Endpoint público e UI não foram criados; integração com perfis continua em cards posteriores.

- **Objetivo/contexto:** impedir conta aluno+instrutor inclusive por corrida.
- **Dependências:** `IDN-001`, `AUD-001`.
- **Arquivos/módulos:** `RoleAssignment`, people domain/API/policies; seleção UI.
- **Aceite:** concessão idempotente de `STUDENT`/`INSTRUCTOR`/`DOCTOR`/`PSYCHOLOGIST`, coexistência compatível, combinação proibida negada atomicamente, ausência de autorização transitiva, constraint/lock e papéis internos separados; `ClinicMembership` não vira papel pessoal.
- **Testes necessários:** requests concorrentes, API direta, revogação indevida e auditoria.
- **Concluído quando:** nenhuma rota/admin cria combinação proibida.

### IDN-003 — Implementar perfil de aluno (`P1`)

- **Objetivo/contexto:** concluir ramo de aluno sem dar capacidade de instrutor.
- **Dependências:** `RoleAssignment(STUDENT)` vigente.
- **Arquivos/módulos:** people/student model/service/API; onboarding.
- **Aceite:** criação/edição própria, campos mínimos e inexistência para instructor.
- **Testes necessários:** propriedade, papel errado, mass assignment e concorrência com perfil oposto.
- **Concluído quando:** contrato e interface acessível passam.

### IDN-004 — Implementar perfil de instrutor (`P1`)

- **Objetivo/contexto:** dados profissionais em rascunho sem publicação/preço de oferta.
- **Dependências:** `RoleAssignment(INSTRUCTOR)` vigente.
- **Arquivos/módulos:** instructors profile service/API; onboarding.
- **Aceite:** próprio instrutor edita allowlist; perfil começa não publicável.
- **Testes necessários:** papel/propriedade, perfil oposto, campos de status/preço forjados.
- **Concluído quando:** invariantes e UI de rascunho passam.

## M2 — Credenciamento e elegibilidade

### CRD-001 — Implementar aplicação e transições (`P1`)

- **Objetivo/contexto:** formalizar submissão/revisão sem edição direta de status.
- **Dependências:** `IDN-004`, `GOV-003`.
- **Arquivos/módulos:** InstructorApplication domain/service/API/tests; wizard.
- **Aceite:** uma ativa, transições/versão/motivos e correção de pendência.
- **Testes necessários:** estado inválido, concorrência, propriedade, idempotência e auditoria.
- **Concluído quando:** ciclo draft→submitted→pending funciona sem banco manual.

### CRD-002 — Implementar requisitos versionados (`P1`)

- **Objetivo/contexto:** materializar `GOV-002` sem constantes em views.
- **Dependências:** `CRD-001`, matriz aprovada.
- **Arquivos/módulos:** DocumentRequirement model/selectors/admin/tests.
- **Aceite:** jurisdição/categoria/vigência/prioridade e conflito de versões bloqueado.
- **Testes necessários:** datas-limite, obrigatório/opcional, troca de versão e autorização admin.
- **Concluído quando:** aplicação resolve exatamente a matriz aplicável.

### CRD-003 — Implementar pipeline privado de documentos (`P1`)

- **Objetivo/contexto:** receber evidência sem exposição/malware.
- **Dependências:** `CRD-002`, storage/scan aprovados, `AUD-001`.
- **Arquivos/módulos:** InstructorDocument, outbox, integrations, tasks/API/UI.
- **Aceite:** quarentena→validação→scan→promoção, hash, substituição e acesso temporário.
- **Testes necessários:** MIME falso, tamanho, malware, scanner/storage failure, URL expirada, IDOR e órfão.
- **Concluído quando:** nenhum arquivo é público e falha fecha o fluxo.

### CRD-004 — Implementar veículo (`P1`)

- **Objetivo/contexto:** evidenciar veículo elegível com dados protegidos.
- **Dependências:** `IDN-004`, requisitos aplicáveis.
- **Arquivos/módulos:** Vehicle model/domain/API/tests; formulário.
- **Aceite:** estados, propriedade, placa/Renavam protegidos, transmissão/adaptação e validade.
- **Testes necessários:** autorização, mascaramento, duplicidade, estado inválido e expiração.
- **Concluído quando:** veículo válido é consultável pela policy sem expor identificadores.

### CRD-005 — Implementar backoffice de revisão (`P1`)

- **Objetivo/contexto:** decidir documentos/aplicação com segregação e motivo.
- **Dependências:** `CRD-001–004`, `IAM-004`, `AUD-001`.
- **Arquivos/módulos:** policies/selectors/admin API; frontend admin.
- **Aceite:** fila, detalhe minimizado, acesso temporário, aprovar/rejeitar/pedir informação/suspender.
- **Testes necessários:** self-review, papel errado, objeto fora do escopo, stale version, MFA e auditoria.
- **Concluído quando:** revisão completa ocorre sem admin genérico/banco manual.

### CRD-006 — Implementar elegibilidade/publicação (`P1`)

- **Objetivo/contexto:** publicar somente quem satisfaz requisitos atuais.
- **Dependências:** `CRD-001–005`, contatos verificados.
- **Arquivos/módulos:** eligibility domain/policy/tasks/API; checklist UI.
- **Aceite:** motivos estruturados, can_publish calculado, suspensão/expiração retiram publicação e recebedor não bloqueia publicação.
- **Testes necessários:** cada motivo, combinação, corrida, relógio, task perdida/reconciliação e auditoria.
- **Concluído quando:** selector público futuro só pode consumir policy verdadeira.

### CRD-007 — Consolidar primeiro ciclo (`P1`)

- **Objetivo/contexto:** provar o Gate M2 antes do marketplace.
- **Dependências:** `CRD-006` e frontend associado.
- **Arquivos/módulos:** E2E, OpenAPI, docs, métricas e checkpoint.
- **Aceite:** cadastro→pendência→correção→aprovação→publicação e perda de elegibilidade demonstrados.
- **Testes necessários:** E2E, autorização, acessibilidade, concorrência, expiração, backup/rollback da fatia.
- **Concluído quando:** M2 é formalmente aceito e checkpoint libera B1 ou Google.

### GGL-001 — Ativar Google OIDC (`P2`)

- **Objetivo/contexto:** método adicional somente após M2.
- **Dependências:** `CRD-007`, `OPEN-011` decidida.
- **Arquivos/módulos:** accounts/integrations/API/UI/config.
- **Aceite:** state/nonce/issuer/audience/sub, link/unlink por reauth, sessão Django e sem tokens desnecessários.
- **Testes necessários:** CSRF/login injection, e-mail coincidente, replay, conta bloqueada, último método e provider failure.
- **Concluído quando:** não duplica conta/papel/elegibilidade e rollout pode ser desligado.

## M3 — Marketplace e reserva

### MKT-001 — Implementar área geográfica (`P1`)

- **Objetivo/contexto:** delimitar serviço sem expor residência.
- **Dependências:** `CRD-007`, `OPEN-007`.
- **Arquivos/módulos:** marketplace ServiceArea/PostGIS/API/UI.
- **Aceite:** raio/cidade e precisão mínima validados; somente dono edita.
- **Testes necessários:** geometria/raio inválido, autorização, query geográfica e falha do mapa.
- **Concluído quando:** consulta espacial é indexada e privacidade revisada.

### MKT-002 — Implementar oferta de serviço (`P1`)

- **Objetivo/contexto:** separar preço/duração publicável do perfil.
- **Dependências:** `MKT-001`, `CRD-006`.
- **Arquivos/módulos:** ServiceOffering domain/API/UI.
- **Aceite:** draft/active/paused, BRL, duração/veículo/área e ativação condicionada.
- **Testes necessários:** status forjado, dependência inválida, perda de elegibilidade e propriedade.
- **Concluído quando:** snapshot completo pode alimentar proposta.

### MKT-003 — Implementar disponibilidade e exceções (`P1`)

- **Objetivo/contexto:** gerar slots confiáveis em timezone explícito.
- **Dependências:** `MKT-002`, valores de duração/buffer aprovados.
- **Arquivos/módulos:** scheduling rules/exceptions/selectors/API/UI.
- **Aceite:** recorrência, exceção prioritária, horário passado/DST e paginação de slots.
- **Testes necessários:** timezone/DST, overlap de regra, exceção, limite e autorização.
- **Concluído quando:** slots determinísticos são consultáveis, sem promessa de reserva.

### MKT-004 — Publicar busca e perfil minimizados (`P1`)

- **Objetivo/contexto:** permitir descoberta somente de oferta elegível.
- **Dependências:** `MKT-001–003`.
- **Arquivos/módulos:** marketplace selectors/API/Angular páginas/métricas.
- **Aceite:** filtros allowlist, cursor estável, perfil sem dado protegido e remoção de inelegível.
- **Testes necessários:** vazamento, enumeração, filtro/ordenação, paginação concorrente, acessibilidade e desempenho.
- **Concluído quando:** busca atende Gate M3 de leitura.

### BKG-001 — Implementar política e proposta versionadas (`P1`)

- **Objetivo/contexto:** congelar acordo sem sobrescrever contraproposta.
- **Dependências:** `OPEN-003`, `MKT-002/003`.
- **Arquivos/módulos:** commercial_policies, LessonRequest/Proposal, API/UI.
- **Aceite:** versões imutáveis, autor/destinatário, cálculo server-side, expiração e policy referenciada.
- **Testes necessários:** preço forjado, versão velha, papel errado, expiração e autorização por objeto.
- **Concluído quando:** request/counter/decline funcionam com histórico exato.

### BKG-002 — Criar hold atômico no aceite (`P1`)

- **Objetivo/contexto:** impedir booking avulso e dupla reserva.
- **Dependências:** `BKG-001`.
- **Arquivos/módulos:** Booking domain/service/constraints/API/UI.
- **Aceite:** aceite idempotente cria um HELD, converte request e guarda snapshots numa transação.
- **Testes necessários:** aceite simultâneo, sobreposição, chave repetida/payload distinto, inelegibilidade durante corrida e rollback.
- **Concluído quando:** apenas um concorrente obtém slot e nenhum estado parcial resta.

### BKG-003 — Expirar/cancelar hold e booking (`P1`)

- **Objetivo/contexto:** liberar agenda e aplicar política comercial sem copiar estado financeiro.
- **Dependências:** `BKG-002`, policy aprovada.
- **Arquivos/módulos:** bookings tasks/services/API/UI/outbox.
- **Aceite:** expiração reconciliável, cancelamento por ator/motivo e efeito financeiro solicitado separadamente.
- **Testes necessários:** relógio, task duplicada/perdida, cancelamento concorrente e autorização.
- **Concluído quando:** slot é liberado uma vez e histórico fica auditado.

### NTF-001 — Entregar notificações transacionais (`P1`)

- **Objetivo/contexto:** informar eventos sem tornar provedor fonte de estado.
- **Dependências:** outbox e fluxos `BKG-001–003`.
- **Arquivos/módulos:** notifications model/templates/tasks/adapters/UI feedback.
- **Aceite:** template versionado, retry, status, opt-out aplicável e conteúdo mínimo.
- **Testes necessários:** duplicação, provider failure, bounce, PII em log e evento atrasado.
- **Concluído quando:** mensagem é rastreável e falha gera retry/alerta.

## M4 — Financeiro

### FIN-001 — Aprovar gateway e política contábil (`P0 no M4`)

- **Objetivo/contexto:** fechar `OPEN-005` antes de modelar lançamentos definitivos.
- **Dependências:** `OPEN-003/004`, RFP/sandbox.
- **Arquivos/módulos:** `BUSINESS_MODEL`, `INTEGRATIONS`, `DECISIONS`, plano de contas.
- **Aceite:** gateway, KYC/split, taxas, reconhecimento, repasse, reembolso/chargeback e reconciliação aprovados.
- **Testes necessários:** prova sandbox dos eventos/relatórios e tabletop jurídico-contábil.
- **Concluído quando:** contrato e mapeamento de fatos→lançamentos estão versionados.

### FIN-002 — Implementar núcleo do ledger (`P1`)

- **Objetivo/contexto:** registrar efeitos sem custódia/saldo editável.
- **Dependências:** `FIN-001`.
- **Arquivos/módulos:** ledger models/domain/services/selectors/tests.
- **Aceite:** parties/accounts/transactions/entries, balanceamento, BRL, confirmação, reversão e saldo derivado.
- **Testes necessários:** débito=crédito, valor/moeda, imutabilidade, concorrência, idempotência e segregação.
- **Concluído quando:** property tests e migration provam invariantes.

### FIN-003 — Integrar recebedor/KYC (`P1`)

- **Objetivo/contexto:** habilitar instrutor sem guardar dado de cartão.
- **Dependências:** `FIN-002`, gateway sandbox, `IAM-004`.
- **Arquivos/módulos:** payments recipient/adapters/API/UI.
- **Aceite:** estados internos, criação/alteração idempotente, MFA e eligibility financeira calculada.
- **Testes necessários:** timeout/consulta, duplicação, provider rejection, papel errado e mudança sensível.
- **Concluído quando:** recebedor sandbox e contas internas correlacionam.

### FIN-004 — Criar pagamento/checkout (`P1`)

- **Objetivo/contexto:** cobrar hold válido sem confiar no browser.
- **Dependências:** `FIN-003`, `BKG-002`.
- **Arquivos/módulos:** Payment service/adapter/API/checkout UI.
- **Aceite:** amount/split server-side, idempotência, estado consultável e tokenização no gateway.
- **Testes necessários:** hold expirado, preço forjado, timeout desconhecido, repetição e provider failure.
- **Concluído quando:** sandbox cria cobrança sem armazenar cartão.

### FIN-005 — Processar webhook e lançar comissão (`P1`)

- **Objetivo/contexto:** confirmar pagamento uma vez e registrar ledger balanceado.
- **Dependências:** `FIN-002/004`.
- **Arquivos/módulos:** WebhookReceipt/IdempotencyRecord/tasks/ledger mappings.
- **Aceite:** assinatura, corpo bruto, resposta rápida, ordem/duplicação, Payment e Booking correlacionados.
- **Testes necessários:** assinatura inválida/rotacionada, replay, evento antigo, task crash, ledger duplicado e concorrência.
- **Concluído quando:** webhook pago confirma booking e comissão/líquido exatamente uma vez.

### FIN-006 — Implementar transferência e conciliação (`P1`)

- **Objetivo/contexto:** explicar liquidação e detectar divergência.
- **Dependências:** `FIN-005`.
- **Arquivos/módulos:** Transfer/ReconciliationRecord/tasks/admin/API/UI.
- **Aceite:** importação paginada, match, divergência/owner/resolução e extratos segregados.
- **Testes necessários:** arquivo/evento faltante, duplicado, valor divergente, timezone, reprocessamento e autorização.
- **Concluído quando:** relatório sandbox fecha gateway=payment=transfer=ledger ou aponta diferença.

### FIN-007 — Implementar reembolso/chargeback (`P1`)

- **Objetivo/contexto:** tratar reversões sem editar lançamento original.
- **Dependências:** `FIN-005/006`, policy/limites aprovados.
- **Arquivos/módulos:** payment operations/ledger/admin/API/UI.
- **Aceite:** parcial/total, aprovação/MFA, idempotência, reversão/compensação e booking separado.
- **Testes necessários:** concorrência, limite excedido, repetição, chargeback fora de ordem e reconciliação.
- **Concluído quando:** todos os extratos explicam o efeito e trilha identifica decisão.

### FIN-008 — Consolidar financeiro (`P1`)

- **Objetivo/contexto:** atingir Gate M4 antes de execução/piloto.
- **Dependências:** `FIN-002–007`.
- **Arquivos/módulos:** E2E, dashboards/alerts/runbooks/OpenAPI/docs.
- **Aceite:** cenários pago, falho, refund e chargeback reconciliam; fila/divergência alertam.
- **Testes necessários:** E2E sandbox/fake, carga de webhook, rotação, outage e restore.
- **Concluído quando:** Finance/Security/Engineering aprovam evidência.

## M5 — Execução e reputação

### EXE-001 — Implementar conclusão e no-show (`P1`)

- **Objetivo/contexto:** encerrar aula comercial sem alegar homologação.
- **Dependências:** `OPEN-003`, booking confirmado.
- **Arquivos/módulos:** bookings domain/API/UI/notifications.
- **Aceite:** check-in, solicitação/confirmação, timeout/escalonamento e no_show_party conforme policy.
- **Testes necessários:** ator/janela errados, concorrência, linguagem, auditoria e efeito financeiro solicitado.
- **Concluído quando:** todos os caminhos têm estado comercial válido.

### DSP-001 — Implementar disputa/evidências (`P1`)

- **Objetivo/contexto:** resolver contestação com privacidade e efeito explícito.
- **Dependências:** `EXE-001`, `FIN-007`.
- **Arquivos/módulos:** disputes models/services/policies/API/admin/UI/storage.
- **Aceite:** janela, evidência privada, responsável, decisão/motivo e comando financeiro separado.
- **Testes necessários:** IDOR, arquivo malicioso, prazo, papel/segregação, decisão concorrente e auditoria.
- **Concluído quando:** disputa resolvida é rastreável e ledger não é editado diretamente.

### SUP-001 — Implementar suporte e denúncias (`P1`)

- **Objetivo/contexto:** separar atendimento/conduta/segurança/privacidade de disputa financeira.
- **Dependências:** `IAM-004`, política/SLA aprovados.
- **Arquivos/módulos:** support models/services/policies/API/admin/UI.
- **Aceite:** triagem, atribuição, notas privadas, suspensão preventiva autorizada e acesso minimizado.
- **Testes necessários:** escopo, dados de terceiros, SLA, abuso interno, concorrência e auditoria.
- **Concluído quando:** caso percorre abertura→resolução sem privilégio genérico.

### REV-001 — Implementar avaliação/moderação (`P1`)

- **Objetivo/contexto:** reputação vinculada à participação elegível.
- **Dependências:** `EXE-001`, `SUP-001`.
- **Arquivos/módulos:** reviews domain/API/admin/UI/aggregates.
- **Aceite:** uma avaliação por participação concluída, publicação moderável e denúncia correlacionada.
- **Testes necessários:** booking não concluído/alheio, duplicação, conteúdo removido, média concorrente e privacidade.
- **Concluído quando:** nota pública é reconstruível e denúncia auditada.

### MVP-001 — Executar E2E funcional (`P1`)

- **Objetivo/contexto:** provar todo o escopo antes de hardening.
- **Dependências:** M1–M5 concluídos.
- **Arquivos/módulos:** suites E2E, fixtures sintéticas, OpenAPI/docs/checkpoint.
- **Aceite:** fluxo principal e cancelamento/no-show/disputa/denúncia/chargeback/perda de elegibilidade passam.
- **Testes necessários:** E2E multiusuário, autorização, concorrência, idempotência, acessibilidade e falha externa.
- **Concluído quando:** critérios do MVP em `SCOPE.md` têm evidência rastreável.

## M6 — Hardening e homologação

### REL-001 — Criar dados demo sintéticos (`P1`)

- **Objetivo/contexto:** permitir demonstração/UAT sem PII real.
- **Dependências:** `MVP-001`.
- **Arquivos/módulos:** factories/management command/guards/docs.
- **Aceite:** cenários determinísticos, marcados, idempotentes e bloqueados em produção.
- **Testes necessários:** execução repetida, isolamento, detecção de produção e ausência de dados reais.
- **Concluído quando:** ambiente limpo reproduz roteiro de demo.

### REL-002 — Fechar segurança e privacidade (`P0 pré-piloto`)

- **Objetivo/contexto:** fechar `OPEN-004/006/008/014` e riscos críticos de privacidade.
- **Dependências:** `MVP-001`, pareceres/fornecedores.
- **Arquivos/módulos:** threat model, ROPA, retenção/direitos, contracts, scans/pentest fixes.
- **Aceite:** ROPA/bases/agentes/idade, LIA/RIPD, transferências, retenção, direitos, cookies, controles/gaps/owners, termos e contratos aprovados; crítica/alta tratada ou exceção temporária formal.
- **Testes necessários:** autorização, aceite ≠ consentimento, cookies opt-in, export/delete/propagação, retenção/restore, decisão automatizada, incident tabletop/pentest e redaction.
- **Concluído quando:** Legal/Privacy/Security assinam o gate.

### REL-003 — Implantar pipeline staging→produção (`P1`)

- **Objetivo/contexto:** promover artefato imutável com migração segura.
- **Dependências:** `REL-002`, infraestrutura escolhida.
- **Arquivos/módulos:** IaC/config/CI-CD/secrets/release docs.
- **Aceite:** ambientes isolados, approval, migration, smoke, rollback/roll-forward e release notes.
- **Testes necessários:** deploy staging, falha de migration, rollback e segredo ausente/rotacionado.
- **Concluído quando:** mesmo artefato aprovado é promovível sem build manual.

### REL-004 — Validar observabilidade e continuidade (`P0 pré-piloto`)

- **Objetivo/contexto:** fechar `OPEN-009` com evidência, não promessa.
- **Dependências:** `REL-003`.
- **Arquivos/módulos:** dashboards/alerts/backups/runbooks/DR evidence.
- **Aceite:** SLI/SLO, on-call, RPO/RTO, backup criptografado, restore cronometrado e alertas acionáveis.
- **Testes necessários:** restore, worker/gateway/storage/banco outage, fila presa, divergência e alert delivery.
- **Concluído quando:** Operations/Engineering aceitam resultados e gaps.

### REL-005 — Executar testes não funcionais (`P1`)

- **Objetivo/contexto:** validar capacidade, acessibilidade, compatibilidade e contratos.
- **Dependências:** `REL-003/004`.
- **Arquivos/módulos:** load/a11y/contract/security test suites e relatórios.
- **Aceite:** budgets/metas aprovados, gargalos tratados e browsers/dispositivos documentados.
- **Testes necessários:** carga/soak crítica, a11y, browser, provider sandbox e degradação.
- **Concluído quando:** relatório não contém bloqueio sem owner/aceitação.

### REL-006 — Homologar release candidate (`P0 pré-piloto`)

- **Objetivo/contexto:** obter aceite interdisciplinar antes de produção limitada.
- **Dependências:** `REL-001–005`.
- **Arquivos/módulos:** roteiros/evidências UAT, treinamento, release checklist, checkpoint.
- **Aceite:** aluno/instrutor/revisor/finance/support, jurídico/conteúdo, smoke/rollback e stop conditions aprovados.
- **Testes necessários:** UAT completo e ensaio operacional em staging.
- **Concluído quando:** release candidate é assinado ou rejeitado com bloqueios.

## M7 — Piloto

### PIL-001 — Congelar desenho do piloto (`P0`)

- **Objetivo/contexto:** impedir meta retroativa.
- **Dependências:** `REL-006`, `OPEN-010`.
- **Arquivos/módulos:** `PILOT`, dashboards/coortes, runbooks e termos.
- **Aceite:** cidade, duração, orçamento, limites, coortes, métricas, thresholds, owners e stop conditions.
- **Testes necessários:** tabletop de go/no-go, incidente, fraude e capacidade de suporte.
- **Concluído quando:** checklist de entrada está assinado.

### PIL-002 — Lançar por ondas (`P1`)

- **Objetivo/contexto:** limitar blast radius com usuários/dinheiro reais.
- **Dependências:** `PIL-001`.
- **Arquivos/módulos:** config/feature flags, operação, release evidence.
- **Aceite:** lote inicial, smoke, conciliação e monitoramento; expansão só após janela aprovada.
- **Testes necessários:** produção controlada, rollback/pausa e suporte de primeiro caso.
- **Concluído quando:** onda encerra sem stop condition ou é pausada corretamente.

### PIL-003 — Operar e revisar semanalmente (`P1`)

- **Objetivo/contexto:** coletar evidência econômica/operacional confiável.
- **Dependências:** `PIL-002`.
- **Arquivos/módulos:** dashboards, registros de intervenção/incidente/custo e atas.
- **Aceite:** conciliação diária, suporte auditado, coortes/funil/margem e riscos atualizados.
- **Testes necessários:** qualidade de eventos, reconciliação amostral e alert/runbook drill.
- **Concluído quando:** cada semana tem dados completos e decisões registradas.

### PIL-004 — Encerrar e decidir (`P1`)

- **Objetivo/contexto:** converter o piloto em go/iterate/no-go objetivo.
- **Dependências:** janela/stop de `PIL-003`.
- **Arquivos/módulos:** relatório, `DECISIONS`, `RISKS`, `ROADMAP`, backlog/checkpoint.
- **Aceite:** métricas contra baseline, custos, incidentes, entrevistas, risco residual e destino dos dados.
- **Testes necessários:** revisão independente de cálculos/coortes e completude.
- **Concluído quando:** decisão/owner/próxima fase estão commitados e comunicáveis.

## M8–M11 — Operação e evolução

### VOI-001 — Corrigir achados e estabilizar operação (`P1 após go`)

- **Objetivo/contexto:** transformar evidência do piloto em operação sustentável.
- **Dependências:** `PIL-004=go/iterate`.
- **Arquivos/módulos:** conforme achados; SLO/runbooks/backlog/docs.
- **Aceite:** riscos/defeitos prioritários fechados, intervenção frequente automatizada e gates afetados repetidos.
- **Testes necessários:** regressão, carga/DR/segurança conforme mudança.
- **Concluído quando:** owners aceitam SLO, custo, suporte e risco residual.

### VOI-002 — Instituir cadência operacional (`P1`)

- **Objetivo/contexto:** manter produção segura além do lançamento.
- **Dependências:** `VOI-001`.
- **Arquivos/módulos:** calendário de release/patch/access review/restore/DR/reconciliação.
- **Aceite:** owners, frequência, evidência e escalonamento definidos e exercitados.
- **Testes necessários:** primeiro ciclo completo de cada rotina e auditoria amostral.
- **Concluído quando:** checkpoint registra operação contínua mensurável.

### EVO-001 — Abrir iniciativa posterior (`P2`)

- **Objetivo/contexto:** impedir que SaaS, integração oficial, nova região, app ou IA entre por inércia.
- **Dependências:** gate/resultado de M8 e evidência específica.
- **Arquivos/módulos:** `VISION/SCOPE/BUSINESS_MODEL/DECISIONS/RISKS/ROADMAP` e discovery próprio.
- **Aceite:** problema/evidência, alternativas, jurídico/privacidade/segurança, arquitetura, métricas e rollout aprovados.
- **Testes necessários:** protótipo/experimento e plano de gates proporcional.
- **Concluído quando:** nova fatia tem escopo e backlog próprios; caso contrário é rejeitada/adiada.

## Definition of Ready global

Objetivo, contexto, decisão, dependências, owner, dados, autorização, auditoria, falhas, observabilidade, rollback, aceite e testes estão claros; questão bloqueante fechada.

## Definition of Done global

Código/config/documento da fatia, migration quando aplicável, testes, segurança/privacidade, OpenAPI, logs/métricas, documentação/checkpoint, CI verde, diff revisado, sem segredo/dado real e commit convencional coerente.

## Extensão consolidada — demanda, matching e formação de oferta

### CRD-008 — Implementar candidato e jornada orientativa (`P1 após CRD-002`)

**Dependências:** requisitos locais versionados, política de idade e privacidade.  
**Aceite:** candidato separado de instrutor publicável; checklist versionado; nenhuma mensagem de “apto” oficial; auditoria e testes de autorização.

### CRD-009 — Registrar verificação oficial manual (`P1 após CRD-002`)

**Dependências:** matriz de evidências e política de revisão.  
**Aceite:** fonte, data, método, validade/resultado normalizado e evidência protegida; falha/ausência não rejeita definitivamente sem regra.

### MKT-005 — Implementar demanda do aluno (`P1 após MKT-001`)

**Dependências:** perfil do aluno, PostGIS, `OPEN-007`.  
**Aceite:** criar/publicar/cancelar/expirar demanda; localização minimizada; filtros versionados; auditoria; testes de privacidade.

### MKT-006 — Implementar agregados/mapa de demanda (`P1 após MKT-005`)

**Dependências:** política de limiar de agregação.  
**Aceite:** clusters por cidade/região sem reidentificação prática; filtros permitidos; cache invalidável; teste de células pequenas.

### MCH-001 — Implementar matching determinístico (`P1 após MKT-002, MKT-003, MKT-005`)

**Aceite:** somente instrutor elegível; regra versionada; fatores explicáveis; distância aproximada; idempotência; testes de borda e performance.

### MCH-002 — Converter match em negociação (`P1 após MCH-001, BKG-001`)

**Aceite:** origem preservada, autorização de ambas as partes, proposta versionada e métricas de funil.

### REG-001 — Avaliar integração oficial por jurisdição (`P2 / Gate M10`)

**Aceite:** fonte e termos documentados, capacidades suportadas, DPIA/LIA quando aplicável, teste de falha e fallback manual; nenhuma automação de endpoint não documentado.

### ACA-001 — Evoluir Academia do Instrutor (`P2 pós-piloto`)

**Aceite:** iniciativa separada com conteúdo, responsabilidades, parceiros/monetização e compliance aprovados; não certificar nem prometer credenciamento.

## Backlog adicional — decisão nacional 19/08/2026

- **GOV-002A** — matriz federal CONTRAN/SENATRAN/RENACH e fontes oficiais aplicáveis.
- **GOV-002B** — matriz detalhada RS/SC/SP/RJ/ES/RO/AM/AC/RR para instrutor, clínica, médico e psicólogo.
- **GOV-002C** — template das demais 18 UFs e processo de ativação progressiva.
- **PRIV-001** — atualizar ROPA com jornada CNH, mapa, demanda, clínicas e profissionais.
- **PRIV-002** — definir matriz de agentes e compartilhamento aluno→clínica/profissional.
- **PRIV-003** — política de geolocalização/clusters e teste de reidentificação.
- **PRIV-004** — decisão/RIPD sobre qualquer dado de saúde/acessibilidade antes de coletá-lo.
- **DOM-HEALTH-001** — modelar ClinicProfile, HealthProfessionalProfile e vínculos.
- **DOM-JUR-001** — modelar jurisdição, ativação territorial, regras e fontes versionadas.
- **UX-JOURNEY-001** — adaptar experiência à referência visual da landing InstrutorPro: Sou aluno / Sou profissional.
- **DEFER-001** — manter Academia do Instrutor/candidato a instrutor fora do MVP.

## Backlog v1.6 — fundação do modelo nacional

- [ ] DM-001 Implementar `CountrySubdivision` com seed das 27 UFs.
- [ ] DM-002 Implementar `Municipality` com estratégia de importação/versionamento.
- [ ] DM-003 Implementar `RegulatoryRule` e `VerificationSource`.
- [x] DM-004 Implementar fundação estrutural de `Clinic` e `ClinicMembership` (onboarding/policies operacionais permanecem pendentes).
- [ ] DM-005 Implementar `DoctorProfile` e `PsychologistProfile`.
- [ ] DM-006 Implementar `Credential`, `CredentialEvidence` e `OfficialVerification`.
- [ ] DM-007 Implementar `PublicationDecision` separado da verificação estatal.
- [ ] DM-008 Implementar `OfficialFlowPolicy` por UF/serviço.
- [ ] DM-009 Implementar `StudentDemand` com localização privada.
- [ ] DM-010 Implementar matching determinístico/versionado e `DemandMatch`.
- [ ] DM-011 Implementar `DemandAggregate` com limiar de privacidade.
- [ ] DM-012 Implementar `Referral` para fluxo designado/encaminhado.
- [ ] DM-013 Implementar Jornada CNH informativa sem dados clínicos sensíveis.
- [ ] DM-014 Criar serializers públicos separados dos serializers internos.
- [ ] DM-015 Criar testes de autorização, geoprivacidade, expiração e auditoria.
