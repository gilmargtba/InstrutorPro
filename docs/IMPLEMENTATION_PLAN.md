# Plano de Implementação por Dependências

Este documento é a fonte oficial da ordem técnica. Fases A–H refinam os marcos M0–M11 de `ROADMAP.md`; unidades de commit menores estão em `BACKLOG.md`. O agente executa somente a próxima tarefa liberada no `CHECKPOINT.md`.

## Objetivo

Converter o roadmap em fatias verticais pequenas, executáveis e verificáveis. Cada etapa entrega modelo ou grupo inseparável, regras de negócio, serviço, política, API, testes e documentação. O frontend associado começa somente após o contrato e as regras do backend da etapa estarem estáveis.

## Regras de decomposição

- um modelo é individual quando possui utilidade e invariantes verificáveis após suas dependências;
- modelos são agrupados quando a implementação isolada permitiria estado inválido ou não entregaria caso de uso;
- regra crítica permanece no domínio/serviço, nunca apenas no frontend;
- cada etapa termina executável, atualiza o checkpoint e gera commit próprio conforme `AGENTS.md`;
- migrations já aplicadas não são editadas;
- Google permanece inativo até o gate cadastral completo;
- papéis pessoais podem coexistir somente conforme policy explícita; cada papel mantém perfil, requisitos, verificação, publicação e autorização independentes;
- estado cadastral, comercial, financeiro e oficial permanece separado;
- nenhum valor ou política aberta em `DECISIONS.md` é inventado para destravar código;
- backend e contrato estabilizam antes da interface da mesma capacidade;
- tarefas de segurança, privacidade, observabilidade, documentação e rollback fazem parte da fatia, não são fase final opcional.

## Mapa de implementabilidade

| Modelo ou grupo                                    | Forma                      | Dependências principais                                               |
| -------------------------------------------------- | -------------------------- | --------------------------------------------------------------------- |
| `AuditEvent`                                       | Individual                 | Fundação técnica; ator pode ser sistema/anônimo                       |
| `Account`                                          | Individual                 | Custom user na primeira migration                                     |
| `ContactVerificationChallenge`                     | Individual                 | `Account` e provedor de mensagens                                     |
| `ExternalIdentity`                                 | Individual e inativo       | `Account`; sem endpoints Google no primeiro ciclo                     |
| `Person`                                           | Individual                 | `Account`                                                             |
| `RoleAssignment`                                   | Individual                 | `Account`; policy explícita de compatibilidade e ausência de autorização transitiva |
| `PlatformOrganization`                             | Individual                 | Fundação e decisões jurídicas mínimas                                 |
| `LegalDocument` + `LegalAcceptanceRecord` + `ConsentRecord` | Grupo              | Texto versionado; aceite obrigatório e consentimento opcional separados |
| `StudentProfile`                                   | Individual                 | `Person` + papel `STUDENT`                                            |
| `InstructorProfile`                                | Individual                 | `Person` + papel `INSTRUCTOR`                                         |
| `InstructorApplication`                            | Individual                 | `InstructorProfile`                                                   |
| `DocumentRequirement` + `InstructorDocument`       | Grupo                      | Aplicação, storage privado, scan e política local                     |
| `Vehicle`                                          | Individual                 | `InstructorProfile` e requisitos definidos                            |
| Elegibilidade/publicação                           | Serviço/política           | Conta, contatos, aplicação, documentos e veículo                      |
| `ServiceArea`                                      | Individual                 | `InstructorProfile` + PostGIS                                         |
| `AvailabilityRule`                                 | Individual                 | Instrutor operacional                                                 |
| `AvailabilityException`                            | Individual                 | Agenda/regras do instrutor                                            |
| `ServiceOffering`                                  | Individual                 | Instrutor elegível, área e política de preço permitida                |
| `CommercialPolicy`                                 | Individual/versionado      | Decisão comercial/jurídica aprovada                                   |
| `LessonRequest` + `LessonProposal`                 | Grupo                      | Aluno, instrutor, oferta e termos versionados                         |
| `Booking`                                          | Individual                 | Proposta aceita, agenda e política de cancelamento                    |
| Núcleo do ledger                                   | Grupo                      | `FinancialParty`, `LedgerAccount`, `LedgerTransaction`, `LedgerEntry` |
| `PaymentRecipient`                                 | Individual                 | Instrutor, ledger e gateway escolhido                                 |
| `Payment` + `WebhookReceipt` + `IdempotencyRecord` | Grupo                      | Booking, gateway e núcleo do ledger                                   |
| `Transfer` + `ReconciliationRecord`                | Grupo                      | Payment, recebedor, ledger e gateway                                  |
| `Dispute` + `DisputeEvidence`                      | Grupo                      | Booking, política e efeitos financeiros                               |
| `Review`                                           | Individual                 | Booking concluída                                                     |
| `SupportCase`                                      | Individual                 | Conta, autorização e política de atendimento/denúncia                 |
| `NotificationDelivery`                             | Infraestrutura transversal | Templates, outbox e provedor de mensagens                             |
| `OutboxEvent`                                      | Infraestrutura transversal | Introduzir antes do primeiro evento assíncrono crítico                |

## Fase A — Decisões, fundação cadastral e credenciamento (M0–M2)

### A0 — Decisões mínimas do piloto

Backend/domínio: cidade/UF, categoria inicial, requisitos documentais, política de revisão, termos e definição de aplicação ativa.

Frontend: somente fluxos e wireframes documentais das jornadas de aluno, instrutor e backoffice; nenhuma implementação Angular nesta etapa.

Saída: `OPEN-001` fechado; conteúdo de `OPEN-002` aprovado para a capacidade implementada; responsáveis/evidências registrados e regras suficientes para não codificar decisões locais como constantes acidentais. `OPEN-004/006/008/009` podem continuar abertas com gate explícito. `OPEN-014` não bloqueia desenvolvimento sintético para adultos enquanto cadastro/coleta de menores falhar fechado; bloqueia usuários menores e expansão. Simuladores substituíveis atendem desenvolvimento quando necessários.

### A1 — Fundação técnica

Backend: Django/DRF, PostgreSQL/PostGIS preparado, Redis/Celery, configuração por ambiente, erros estáveis, request ID, health, OpenAPI, lint, testes e CI.

Frontend após backend: Angular/PrimeNG, shell, tema, acessibilidade base, rotas, cliente HTTP, CSRF, tratamento de erro e estados de carregamento.

Saída: aplicação reproduzível, build e CI verdes.

### A2 — Auditoria

Backend: `AuditEvent`, contexto de request, serviço append-only, mascaramento e políticas de consulta.

Frontend após backend: consulta administrativa mínima, filtros e detalhe seguro.

Saída: ações sensíveis seguintes podem ser auditadas desde sua origem.

### A3 — Conta e sessão

Entrada: para desenvolvimento sintético, política fail-closed de menores documentada. Cadastro operacional real exige controle etário proporcional aprovado; nenhum mecanismo definitivo é presumido no schema/API.

Backend: `Account`, estados, senha, cadastro, login/logout, sessão Django, bloqueio, antienumeração e rate limit.

Frontend após backend: cadastro, login, logout, guarda de rota e estado autenticado.

Saída: conta criada e sessão segura sem definir papel pelo cliente.

### A4 — Verificação de contatos e recuperação

Backend: `ContactVerificationChallenge`, verificação de e-mail/telefone, recuperação de senha, expiração, consumo único e limite de tentativas.

Frontend após backend: solicitar/repetir código, confirmar contato e recuperar acesso.

Saída: contatos verificáveis sem OTP persistido ou exposto.

### A5 — Sessões revogáveis e MFA sensível

Backend: inventário e revogação de sessões, MFA para papéis internos e operações sensíveis.

Frontend após backend: minhas sessões, revogação e desafio MFA.

Saída: bloqueio e revogação interrompem acesso conforme política.

### A6 — Preparação de identidade Google

Backend: `ExternalIdentity`, provider `GOOGLE`, unicidade `(provider, subject)` e ausência de tokens.

Frontend: nenhuma implementação nesta etapa; não criar botão, rota ou configuração Google.

Saída: estrutura inativa e testada, sem autenticação social disponível.

### A7 — Organização da plataforma

Backend: `PlatformOrganization`, unicidade da organização ativa e políticas administrativas.

Frontend após backend: configuração institucional mínima e controlada.

Saída: a pessoa jurídica operadora existe independentemente de contas administrativas.

### A8 — Termos, aceites e consentimentos

Backend: `LegalDocument`, `LegalAcceptanceRecord` e `ConsentRecord`, com versão, vigência, finalidade, hash, concessão/retirada e evidência proporcional.

Frontend após backend: documento atual, aceite obrigatório separado de escolha opcional, retirada equivalente e históricos do usuário.

Saída: aceite e consentimento referenciam texto/versão exatos sem que um seja usado como prova do outro.

### A9 — Pessoa

Backend: `Person`, CPF protegido, propriedade, edição e política de privacidade.

Frontend após backend: dados pessoais, validações e correção permitida.

Saída: identidade civil permanece separada de autenticação e papel.

### A10 — Concessão e compatibilidade de papéis

Backend: `RoleAssignment` e operação transacional que concede `STUDENT`, `INSTRUCTOR`, `DOCTOR` ou `PSYCHOLOGIST` conforme policy versionada. Permitir coexistência compatível, negar combinações proibidas e impedir corrida concorrente ou autorização transitiva. `ClinicMembership` permanece vínculo organizacional separado.

Frontend após backend: seleção clara entre jornada de aluno ou instrutor, sem opção de acumular papéis.

Saída: uma conta possui no máximo um papel de negócio.

### A11 — Perfil do aluno

Backend: `StudentProfile`, regras de propriedade e edição.

Frontend após backend: onboarding, preferências e edição do aluno.

Saída: perfil existe somente quando o papel `STUDENT` está presente, sem impedir perfil profissional compatível nem compartilhar estado/autorização.

### A12 — Perfil do instrutor

Backend: `InstructorProfile`, dados profissionais, operação e política de edição. Preço/duração pertencem a `ServiceOffering` na Fase B.

Frontend após backend: onboarding e edição profissional em rascunho.

Saída: perfil existe somente quando o papel `INSTRUCTOR` está presente, com elegibilidade/publicação próprias e ainda não publicável.

### A13 — Aplicação do instrutor

Backend: `InstructorApplication`, uma aplicação ativa, máquina de estados, submissão e pendências.

Frontend após backend: wizard, resumo, submissão, acompanhamento e correção de pendências.

Saída: transições inválidas são rejeitadas e auditadas.

### A14 — Requisitos e documentos

Backend: `DocumentRequirement`, `InstructorDocument`, `OutboxEvent`, upload em quarentena, MIME/tamanho, hash, antivírus, storage privado, validade e URL assinada curta.

Frontend após backend: lista de requisitos, upload, substituição, progresso, estados e pendências.

Saída: documento nunca público e somente requisito aplicável pode ser submetido.

### A15 — Veículo

Backend: `Vehicle`, dados protegidos, estados, validade e vínculo ao próprio instrutor.

Frontend após backend: cadastro, edição, documentos/fotos permitidos e status.

Saída: veículo válido pode participar da política de publicação.

### A16 — Backoffice de revisão

Backend: filas, políticas por objeto, segregação de funções, aprovar/rejeitar documento, pedir informação, decidir aplicação, suspender/reativar.

Frontend após backend: fila, detalhe, visualização segura, decisão com motivo e histórico.

Saída: instrutor não revisa a si mesmo e toda decisão é auditada.

### A17 — Publicação e elegibilidade cadastral

Backend: política `can_publish_instructor`, motivos estruturados, expiração, suspensão e retirada automática de publicação.

Frontend após backend: checklist de progresso, motivos de inelegibilidade e estado público/operacional.

Saída: apenas instrutor cadastralmente apto pode ser publicado; ainda não implica pagamento habilitado.

### A18 — Consolidação cadastral

Backend: E2E, concorrência, autorização, expiração, tarefas agendadas, métricas, OpenAPI e rollback.

Frontend após backend: jornada responsiva e acessível completa de aluno, instrutor e revisor.

Saída: critério do primeiro ciclo atendido e registrado no checkpoint.

### Gate A19 — Google

Somente depois de A0–A18 concluídas: OIDC no backend, validação de `state`, `nonce`, issuer, audience e token; vínculo/desvínculo seguro; sessão Django.

Frontend após backend: botão Google e gerenciamento do vínculo.

Saída: acesso Google sem duplicar contas, alterar papel ou conceder elegibilidade.

## Fase B — Descoberta, agenda e negociação (M3)

Entrada: A18 concluída; `OPEN-003` aprovada para negociação/reserva e `OPEN-007` fechada antes de mapa.

### B1 — Área de serviço

Backend: `ServiceArea`, raio/cidades, precisão mínima e consultas PostGIS. Frontend: área de atuação sem expor residência. Testar geometrias inválidas, escopo e indisponibilidade do mapa.

### B2 — Oferta de serviço

Backend: `ServiceOffering`, preço/duração/moeda, veículo opcional, vigência e ativação condicionada à publicação. Frontend: criar/pausar oferta e comunicar inelegibilidade. Preço público vem da oferta, nunca de campo solto no perfil.

### B3 — Disponibilidade recorrente

Backend: `AvailabilityRule`, timezone IANA, duração/buffer aprovados e validações. Frontend: editor semanal acessível.

### B4 — Exceções e slots

Backend: `AvailabilityException`, precedência, geração de slots e expiração. Frontend: exceções/calendário. Slot exibido é indicativo.

### B5 — Marketplace de leitura

Backend: selectors públicos somente de instrutores/ofertas publicáveis, filtros allowlist, paginação, privacidade e métricas. Frontend: busca, filtros, resultados, perfil/oferta e estados vazios/degradados.

### B6 — Política, solicitação e contraproposta

Backend: `CommercialPolicy`, `LessonRequest` + `LessonProposal`, expiração, versões imutáveis, autorização e cálculo do servidor. Frontend: solicitar, contrapropor, aceitar/recusar e acompanhar condições/política.

### B7 — Aceite e reserva temporária

Backend: aceite idempotente cria `Booking=HELD` atomicamente, guarda snapshots, aplica constraint/lock de sobreposição e expira hold. Não existe criação avulsa. Frontend: confirmação do hold, contagem acessível, detalhe e histórico.

### B8 — Notificações transacionais

Backend: templates, `NotificationDelivery`, outbox, retry/alerta e preferências aplicáveis. Frontend: caixa/feedback mínimo. Falha de mensagem não desfaz o acordo; estado permanece consultável.

Saída: oferta elegível é encontrável e apenas um aceite concorrente obtém o slot com condições congeladas.

## Fase C — Ledger, pagamentos e repasses (M4)

Entrada: `OPEN-005` fechada; gateway/sandbox/contratos e política contábil aprovados; política comercial define efeitos financeiros.

### C1 — Núcleo do razão financeiro interno

Backend: `FinancialParty`, `LedgerAccount`, `LedgerTransaction` e `LedgerEntry`; plano de contas aprovado; BRL em centavos; balanceamento, idempotência, imutabilidade, reversão e provisionamento. Frontend: inspeção administrativa somente leitura.

### C2 — Recebedor do instrutor

Backend: `PaymentRecipient`, adaptador, KYC, idempotência, MFA e estados internos. Frontend: onboarding/status sem coletar cartão/segredo. `can_accept_paid_booking` exige recebedor e contas provisionadas.

### C3 — Intenção de pagamento e checkout

Backend: `Payment`, criação idempotente e estado consultável após timeout. Frontend: componente/redirect seguro do gateway e acompanhamento; retorno do browser não confirma.

### C4 — Recebimento de webhook

Backend: corpo bruto, assinatura, `WebhookReceipt`, resposta rápida, processamento assíncrono, eventos duplicados/fora de ordem e reprocessamento seguro.

### C5 — Comissão e lançamentos

Backend: snapshot de comissão/taxa/líquido, transações balanceadas e reconhecimento conforme política. Frontend: composição transparente e extratos segregados.

### C6 — Transferência e conciliação

Backend: `Transfer`, `ReconciliationRecord`, importação/paginação do provedor, divergência, resolução e alertas. Frontend: extrato do instrutor e painel da plataforma.

### C7 — Reembolso e chargeback

Backend: solicitação, autorização/limites, operação parcial/total, reversões/compensações e efeito separado no booking conforme política. Frontend: estado e histórico seguro.

### C8 — Consolidação financeira

E2E, concorrência, idempotência, assinatura/rotação, ordem de eventos, reconciliação, falha do gateway, alertas, runbook e OpenAPI. Saída: cobrança e repasse sandbox são explicados pelo ledger sem divergência.

## Fase D — Execução, disputa, suporte e reputação (M5)

Entrada: política de conclusão/no-show/disputa aprovada e efeitos financeiros implementados.

### D1 — Execução e conclusão comercial

Backend: check-in não oficial, conclusão bilateral, timeout/escalonamento e no-show. Frontend: ações contextuais e linguagem sem homologação.

### D2 — Disputa e evidências

Backend: `Dispute` + `DisputeEvidence`, prazos, privacidade, decisão estruturada e solicitação explícita de efeito financeiro. Frontend: abertura, acompanhamento, envio e backoffice.

### D3 — Suporte e denúncia

Backend: `SupportCase`, triagem, atribuição, SLA, conduta/segurança/privacidade e suspensão preventiva conforme policy. Frontend: caso e backoffice minimizado.

### D4 — Avaliação e moderação

Backend: `Review`, unicidade por participação, elegibilidade, moderação e denúncia. Frontend: avaliação pós-conclusão e exibição pública permitida.

### D5 — E2E do MVP funcional

Jornada completa, inclusive cancelamento, no-show, disputa, denúncia, reembolso, perda de elegibilidade e auditoria. Saída: critérios de `SCOPE.md` demonstrados em ambiente controlado.

## Fase E — Hardening, dados demo e homologação (M6)

Entrada: MVP funcional; `OPEN-004/006/008/009/014` fechadas antes de release candidate.

### E1 — Dados sintéticos e ambiente de demonstração

Factories e comando idempotente geram contas, ofertas, reservas e cenários financeiros marcados como demo somente fora de produção. Nenhum dado real/segredo.

### E2 — Cobertura não funcional

Testes de carga nos fluxos críticos, acessibilidade, browsers/dispositivos apoiados, contract tests, scans, threat model, revisão de autorização e pentest proporcional.

### E3 — Privacidade operacional

ROPA/base/retenção aprovados, fornecedores mapeados, canal e fluxo de direitos, exportação/correção/desativação, descarte e incident drill.

### E4 — Staging e release pipeline

Infra como código/config reproduzível, migração controlada, seed demo isolado, sandbox, secrets, smoke, preview de OpenAPI, promoção por artefato imutável e evidência de aprovação.

### E5 — Continuidade e observabilidade

SLIs/SLOs, dashboards/alertas acionáveis, backups, restore cronometrado, rollback/roll-forward, capacidade e runbooks testados.

### E6 — Homologação/UAT

Roteiros por aluno/instrutor/backoffice/financeiro/suporte, evidência de aceite, treinamento, termos/conteúdo revisados, defeitos triados e release candidate assinado por owners.

Saída: pacote de produção limitado aprovado; nenhuma falha crítica/alta sem aceitação formal temporária.

## Fase F — Piloto controlado (M7)

### F1 — Preparação e entrada

Congelar cidade, coortes, duração, métricas, limites, orçamento, suporte, on-call, playbooks, stop conditions e baseline. Recrutar/ofertar somente após checklist assinado.

### F2 — Lançamento progressivo

Deploy com pequeno lote, smoke real controlado, monitoramento reforçado e expansão por ondas. Reverter/pausar conforme stop conditions.

### F3 — Operação semanal

Conciliação diária, backup/alerta, suporte auditado, incidentes/fraude, métricas por coorte, entrevistas e revisão semanal sem alterar retroativamente critérios.

### F4 — Encerramento e decisão

Relatório de métricas/custos/riscos, aprendizados, go/iterate/no-go, ações corretivas, backlog e decisão de dados/contas do piloto.

## Fase G — Versão operacional inicial (M8)

### G1 — Correções e confiabilidade

Priorizar achados do piloto por risco/impacto, automatizar intervenções recorrentes e repetir gates afetados.

### G2 — Operação contínua

SLO/on-call, suporte, conciliação, releases, patching, revisão de acesso, restore/DR e custos em cadência definida.

### G3 — Expansão controlada na proposta aprovada

Aumentar aquisição/capacidade apenas dentro da região/escopo aprovado; nova jurisdição volta ao M0/M6 aplicável.

## Fase H — Evolução posterior (M9–M11)

Cada iniciativa começa com discovery, decisão de escopo, ADR, análise jurídica/privacidade/segurança, modelo de negócio, protótipo, teste e rollout: H1 SaaS do instrutor; H2 integrações oficiais autorizadas; H3 nova região/categoria; H4 app/chat/antifraude somente se justificado. Não há implementação “prévia” de endpoint oficial ou microserviço.

## Gate de cada etapa

1. decisões e dependências resolvidas;
2. fatia pequena e rollback/roll-forward definido;
3. migration/constraints e autorização revisadas quando aplicável;
4. regra em domínio/serviço, contrato OpenAPI e erros estáveis;
5. sucesso, negação, estado inválido, concorrência/idempotência e falha externa proporcionais;
6. auditoria, privacidade, segurança, observabilidade e dados avaliados;
7. frontend associado testado somente após backend estável;
8. documentação e checkpoint atualizados;
9. lint/test/build/CI verdes e diff restrito;
10. commit coerente e repositório executável.

## Ordem exata para iniciar

1. `GOV-001`: concluído — arquitetura nacional, primeira onda comercial de nove UFs e categoria B priorizada; cidades do piloto são configuração posterior.
2. `GOV-002`: validar matriz de requisitos/documentos na fonte oficial local.
3. `GOV-003`: aprovar fluxo de revisão, aplicação ativa e evidência de credenciamento oficial.
4. `GOV-004`: identificar organização operadora e responsáveis jurídico/privacidade/segurança/operação.
5. `GOV-005`: aprovar termos mínimos, separar aceite/consentimento, decidir público/idade e mapear pareceres de produção.
6. `GOV-006`: registrar fornecedores estruturais de desenvolvimento ou fakes/abstrações aprovados.
7. `FND-001`: scaffold backend e configuração.
8. `FND-002`: banco/PostGIS, Redis/Celery e ambiente local.
9. `FND-003`: qualidade, CI, health, request ID e OpenAPI.
10. `AUD-001`: auditoria base; depois seguir os IDs priorizados do backlog.

## Extensão do plano — demanda, matching e candidatos

Sem alterar o gate atual M0, incorporar quando as dependências forem liberadas:

### A20 — Candidato a instrutor e jornada orientativa

Após requisitos locais versionados de A14, implementar `InstructorCandidate`, checklist de qualificação e transição voluntária para aplicação de instrutor quando houver evidência necessária. Sem decisão oficial automatizada.

### A21 — Registro de verificação oficial

Implementar `OfficialRegistryVerification` e adaptador manual. Integração eletrônica fica desativada até fonte documentada/autorizada.

### B1A — Demanda do aluno

Após área geográfica e perfil do aluno, implementar `StudentDemand`, expiração, minimização geográfica e auditoria.

### B5A — Agregados de demanda e mapas

Expor clusters/agregados com limiar de privacidade e filtros aprovados. Não expor localização individual.

### B5B — Matching determinístico

Calcular compatibilidade por categoria, área/distância, disponibilidade, veículo/transmissão e demais critérios aprovados; registrar versão e explicação. Somente ofertas elegíveis.

### B5C — Conversão do match em negociação

Permitir que aluno/instrutor elegíveis iniciem o fluxo B6 a partir de um match, preservando origem e métricas.

### H1 — Academia do Instrutor evoluída

Após piloto, avaliar conteúdo estruturado, parceiros/cursos, SaaS e IA assistiva em iniciativa separada.

## Atualização v1.6 — modelo nacional e novos prestadores

Antes de iniciar migrations de negócio, usar `DATA_MODEL_MVP.md` como referência estrutural.

A implementação deve acrescentar, após a fundação técnica e antes do marketplace transacional completo:

1. seed das 27 UFs e municípios por fonte oficial aprovada;
2. camada regulatória e fontes de verificação;
3. perfis `Clinic`, `DoctorProfile` e `PsychologistProfile`;
4. credenciais e snapshots de verificação;
5. política de fluxo oficial por UF/serviço;
6. `StudentDemand`, matching determinístico e agregação privada para mapa;
7. jornada CNH informativa;
8. `Referral` para UFs/serviços em que o órgão competente designa o prestador;
9. somente depois, agenda/booking/pagamento onde o fluxo oficial e a política comercial permitirem.

RS, SC, SP, RJ e ES são a primeira onda técnica/comercial autorizada. AM, RO, AC e RR permanecem na matriz regulatória sem ativação automática. A migration nova separa `commercial_status` da prontidão regulatória contextual sem editar histórico.
