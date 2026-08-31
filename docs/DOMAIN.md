# Modelo de Domínio

## CODEX 02E — workflow profissional DEMO auditado

O workflow sintético possui transições explícitas e transacionais:
`DRAFT → SUBMITTED → UNDER_REVIEW → APPROVED`, com rejeição a partir de
`UNDER_REVIEW`. A verificação percorre `NOT_STARTED → PENDING → VERIFIED|REJECTED`.
A publicação percorre `UNPUBLISHED → APPROVED → SUSPENDED|UNPUBLISHED`; aprovação exige
revisão, verificação SYNTHETIC válida e localização de atendimento autorizada. Campos
críticos recusam alteração posterior fora dos serviços de domínio.

A localização de atendimento percorre `NOT_GRANTED → GRANTED → REVOKED`, preservando
finalidade, versão, atores, datas e motivo. Revogação retira o perfil de novas buscas sem
apagar localização histórica, perfil, pessoa, conta, papel ou auditoria. O onboarding 02E
é somente DEMO sintética, não cadastro operacional ou autorização oficial.

## CODEX 02D — perfil e publicação sintéticos

Perfil, área, autorização de localização, verificação e decisão são fatos independentes. Aprovação SYNTHETIC não é autorização oficial. A policy remove suspensos, expirados ou revogados sem apagar históricos.

Fonte oficial de entidades, relações, vocabulário de estado e invariantes. A API não cria estados adicionais; políticas comerciais abertas em `DECISIONS.md` parametrizam o domínio sem serem inferidas pelo código.

## Contextos

1. Identidade
2. Pessoas e perfis
3. Credenciamento
4. Catálogo
5. Disponibilidade
6. Negociação
7. Reserva
8. Pagamentos
9. Reputação
10. Suporte e disputas
11. Compliance
12. Auditoria

## Relações centrais

```text
Account ─1:1─ Person ─┬─ 0..* RoleAssignment
   │                  ├─ 0..1 StudentProfile
   │                  └─ 0..1 perfis profissionais independentes
   │                         └─ InstructorApplication ─┬─ InstructorDocument
   │                                                   └─ Vehicle
   ├─ ContactVerificationChallenge
   ├─ ExternalIdentity
   ├─ LegalAcceptanceRecord ── LegalDocument
   └─ ConsentRecord ────────── LegalDocument

InstructorProfile ─┬─ ServiceArea
                   ├─ ServiceOffering
                   └─ AvailabilityRule/Exception

StudentProfile + InstructorProfile
   └─ LessonRequest ── LessonProposal (versões imutáveis)
                          └─ aceite atômico ── Booking
                                                    ├─ Payment ─ Transfer
                                                    ├─ Dispute/Evidence
                                                    └─ Review

Fatos financeiros ── LedgerTransaction ── LedgerEntry
Partes econômicas ── FinancialParty ── LedgerAccount
```

Referências são por UUID interno/público conforme exposição. Dados protegidos e evidências privadas nunca são usados como identificadores em URL.

## Entidades

### Account

Identidade autenticável com UUID, e-mail, telefone, senha, status, verificações, MFA e sessões. No `CODEX 02B`, `lifecycle_status` possui `ACTIVE`, `BLOCKED` e `DEACTIVATED`; `is_active` permanece sincronizado por serviço e constraint. O estado controla acesso à conta, nunca papel, credenciamento, elegibilidade ou publicação.

Uma conta pode receber múltiplos papéis pessoais compatíveis entre `STUDENT`, `INSTRUCTOR`, `DOCTOR` e `PSYCHOLOGIST`. Compatibilidade é decisão explícita de policy, nunca uma exclusividade global ou permissão transitiva. Cada papel possui perfil, requisitos, credenciais, verificações, publicação e autorização independentes. `CLINIC` é organização e seu acesso administrativo futuro ocorre por `ClinicMembership`.

Estados:

```text
PENDING
ACTIVE
BLOCKED
DEACTIVATED
DELETION_REQUESTED
ANONYMIZED
```

### ContactVerificationChallenge

Desafio de uso único para verificar e-mail, telefone ou recuperar acesso. Contém finalidade, destino normalizado/mascarado, hash do segredo, expiração, tentativas, consumo e correlação. Nunca persiste OTP em texto claro.

### ExternalIdentity

Vínculo opcional entre uma `Account` interna e uma identidade autenticada por provedor externo.

Campos mínimos: UUID, conta, provedor, identificador imutável do provedor (`subject`), e-mail informado no vínculo, data de criação e último uso.

Regras:

- preparar a entidade e suas constraints desde a fundação;
- suportar somente `GOOGLE` na primeira implementação;
- não implementar o fluxo Google no início do MVP;
- ativar login e vinculação somente após a conclusão das etapas cadastrais do primeiro ciclo;
- unicidade por `(provider, subject)`;
- uma identidade externa pertence a uma única conta interna;
- e-mail do provedor não é chave estável e não autoriza vínculo automático com conta existente;
- a conta interna continua sendo a fonte de status, papéis, aceites, consentimentos e autorização;
- não armazenar access token ou refresh token quando o uso for somente autenticação;
- impedir que o usuário remova seu último método válido de acesso.

Autenticação Google pode comprovar a identidade da conta no provedor e, quando a claim for validada, a posse do e-mail. Ela não comprova telefone, CPF, identidade civil, documentos, veículo, dados bancários ou elegibilidade.

### Person

Identidade civil: nome, CPF protegido, nascimento, nome preferido, endereço, cidade e UF. CPF possui representação normalizada protegida e fingerprint para unicidade quando juridicamente aprovada; valor completo nunca aparece em log, busca geral ou resposta pública. Endereço residencial e localização pública são conceitos separados.

### RoleAssignment

Concessão auditável de papel pessoal, com `person`, `role`, status derivado, `granted_at`, `granted_by`, `grant_reason`, `revoked_at`, `revoked_by` e `revoke_reason`. A policy exige a permissão explícita `people.manage_role_assignments`; ausência, conta inativa ou papel inválido falham fechado. Uma constraint parcial garante no máximo uma atribuição ativa por pessoa/papel. Revogação preserva a linha histórica e uma reatribuição cria novo ciclo. Papéis administrativos não criam papel profissional nem concedem capacidades transitivas.

### PlatformOrganization

Pessoa jurídica operadora do marketplace, independente de contas administrativas. Mantém identificação e configuração institucional necessárias a termos, contratos e titularidade financeira interna. No MVP existe uma organização ativa.

A configuração M1 é singleton e possui estados `INCOMPLETE`, `PENDING_VALIDATION` e
`VALIDATED`. Cadastro completo apenas produz `PENDING_VALIDATION`; a validação exige
comando humano separado e permissão explícita. Qualquer edição posterior remove a
validação anterior e incrementa a versão para impedir sobrescrita concorrente. CNPJ pode
ser digitado formatado, mas é persistido normalizado e validado pelo dígito verificador.

O requisito de uma organização ativa é de configuração/deploy, não a criação automática de uma pessoa jurídica fictícia. Razão social, CNPJ e dados contratuais são bloqueantes antes da publicação de termos reais.

Para LGPD, a pessoa jurídica real — não este registro — assume o papel funcional de controladora apenas nas operações cujas finalidades e meios essenciais determinar. A matriz de agentes por operação permanece bloqueada em `OPEN-004/008`.

### StudentProfile

Objetivo, categoria, experiência, transmissão, necessidade de veículo e localização padrão. Campo que revele saúde, deficiência ou necessidade de adaptação permanece ausente até hipótese do art. 11 da LGPD, minimização e controles serem aprovados.

Existe somente para conta com papel `STUDENT`; pode coexistir com perfil profissional compatível, mas não compartilha requisitos, estado, publicação ou autorização.

### InstructorProfile

Nome profissional, apresentação, categorias, experiência declarada, preço, raio, localização-base, publicação, operação e nota.

Existe somente para conta com papel `INSTRUCTOR`; pode coexistir com outros perfis compatíveis, preservando aplicação, evidência, elegibilidade, publicação e autorização próprias.

### LegalDocument / LegalAcceptanceRecord / ConsentRecord

`LegalDocument` representa termos, contrato, política, aviso ou texto de consentimento versionado, com tipo, finalidade, público, vigência, hash e estado de publicação.

`LegalAcceptanceRecord` prova aceite contratual/obrigatório, com conta, documento/versão, ação, data, origem e evidência mínima. Ciência do aviso de privacidade pode ser registrada sem fingir consentimento.

`ConsentRecord` existe somente quando a hipótese legal for consentimento e registra finalidade granular, concessão ou retirada, texto/versão/hash apresentado, data, origem e evidência mínima. Retirada é append-only, tão acessível quanto a concessão e não altera fatos históricos. Nenhuma dessas entidades escolhe a base legal; a operação aprovada no ROPA é a fonte.

Aceite e consentimento nunca apontam apenas ao texto atual nem compartilham um checkbox genérico.

### InstructorApplication

```text
DRAFT
SUBMITTED
UNDER_REVIEW
PENDING_INFORMATION
APPROVED
REJECTED
SUSPENDED
EXPIRED
WITHDRAWN
```

Somente uma aplicação ativa por instrutor. Transições ocorrem por serviços explícitos e geram auditoria.

A revisão segue `GOV_003_REVIEW_POLICY.md`: a submissão congela versão e requisitos aplicáveis; decisão stale ou conflitante falha; pendência/rejeição usa motivo estruturado; aprovação interna não altera o fato oficial. `SOURCE_UNAVAILABLE` é motivo operacional, não prova automática de inaptidão. Expiração objetiva pode retirar publicação, mas rejeição/suspensão definitiva por suspeita exige decisão humana contestável.

### DocumentRequirement

Configuração versionada dos documentos exigidos por papel, categoria, cidade/UF e período de vigência. Define tipo, obrigatoriedade, validade e regras de substituição sem codificar requisitos locais em views.

### InstructorDocument

Tipo, número mascarado, emissor, emissão, validade, arquivo, hash, status, revisor e motivo.

```text
UPLOADED
SCANNING
UNDER_REVIEW
VERIFIED
REJECTED
EXPIRED
REVOKED
```

Depende de requisito documental aplicável e aplicação do instrutor. O arquivo percorre quarentena, validação e storage privado antes da revisão.

No recorte M1 sintético, os estados persistidos são `PENDING`, `UNDER_REVIEW`, `APPROVED`,
`REJECTED` e `EXPIRED`; `scan_status` permanece separado. A aprovação exige fixture limpa, válida e
revisor diferente do titular. O caminho interno é aleatório, o nome original não compõe a chave de
storage e o acesso ocorre somente por download autenticado e auditado. Arquivos reais permanecem
fechados até homologação do storage privado, scanner e controles LGPD.

### PracticalTrainingRequirement / PlatformLesson

A carga mínima prática é configuração versionada por UF, categoria, tipo de processo e vigência;
nenhuma quantidade é inferida a partir de número de solicitações/aulas. `PlatformLesson` registra
somente agenda/conclusão na plataforma. `official_record_status` é dimensão independente e começa
em `NOT_INTEGRATED`; portanto uma aula concluída na plataforma não é homologação nem registro
oficial.

### Vehicle

Proprietário declarado, placa/Renavam protegidos, marca/modelo, ano, transmissão, adaptações e status.

Estados mínimos:

```text
DRAFT
UNDER_REVIEW
ACTIVE
REJECTED
SUSPENDED
EXPIRED
```

### ServiceArea

Raio, cidades, polígonos futuros e pontos de encontro.

### ServiceOffering

Oferta publicável do instrutor para uma categoria: duração, preço-base, moeda, se usa veículo do instrutor, veículo elegível opcional, área de serviço, estado e vigência. Permite mais de uma combinação sem transformar `InstructorProfile` em tabela de preços.

```text
DRAFT
ACTIVE
PAUSED
ARCHIVED
```

Uma oferta somente fica `ACTIVE` se o instrutor for publicável e suas dependências forem válidas. A resposta pública calcula disponibilidade atual; não persiste elegibilidade como flag controlável pelo cliente.

### AvailabilityRule / AvailabilityException

Disponibilidade recorrente e exceções, sempre associadas a timezone IANA. Exceções vencem regras recorrentes. Disponibilidade exibida não garante reserva; somente a transação de aceite/hold confirma exclusividade.

### CommercialPolicy

Versão imutável e vigente das regras de hold, cancelamento, no-show, conclusão, disputa e efeitos comerciais/financeiros. Valores concretos dependem de `OPEN-003`. `LessonProposal` e `Booking` guardam a versão aplicada; alteração futura não reescreve acordos existentes.

### LessonRequest

```text
OPEN
COUNTERED
DECLINED
EXPIRED
CANCELLED
CONVERTED
```

O aceite de uma proposta aberta registra `accepted_at` nela e muda a solicitação diretamente para `CONVERTED` na mesma transação que cria o `Booking`. Se a criação do hold falhar, nenhum aceite/conversão é confirmado.

### LessonProposal

Versão imutável das condições propostas ou contrapropostas: solicitação, autor, data/local, duração, veículo, preço e expiração. O aceite referencia uma versão exata; preço e condições não são sobrescritos durante a negociação.

```text
OPEN
ACCEPTED
DECLINED
EXPIRED
WITHDRAWN
SUPERSEDED
```

Uma nova contraproposta torna a versão anterior `SUPERSEDED`. Somente uma proposta `OPEN`, vigente e dirigida ao ator pode ser aceita.

### Booking

```text
HELD
CONFIRMED
IN_PROGRESS
COMPLETION_PENDING
COMPLETED
CANCELLED
NO_SHOW
DISPUTED
CLOSED
```

`Booking` guarda proposta aceita, partes, oferta, slot, local minimizado, política e snapshots de preço/condições. `HELD` possui `expires_at`; confirmação exige `Payment=PAID` quando houver cobrança. `cancelled_by` e `no_show_party` são atributos, não estados combinatórios. Reembolso e processamento pertencem a `Payment`; repasse pertence a `Transfer`; validade oficial não pertence a nenhum estado comercial.

Não existe criação pública de booking sem aceite. Aceites concorrentes usam transação, constraint de sobreposição e chave de idempotência; apenas um pode criar o hold.

### Payment

```text
CREATED
PENDING
AUTHORIZED
PAID
FAILED
CANCELLED
PARTIALLY_REFUNDED
REFUNDED
CHARGEBACK
```

### FinancialParty

Parte econômica interna dos tipos `STUDENT`, `INSTRUCTOR`, `PLATFORM` ou `SETTLEMENT_PROVIDER`. Uma pessoa com múltiplos papéis não mistura automaticamente posições econômicas: cada relação financeira usa parte/escopo explicitamente definidos. A organização da plataforma possui parte própria.

### LedgerAccount

Subconta do razão financeiro interno, pertencente a uma `FinancialParty`, com código, categoria, moeda, natureza e estado. Não representa conta bancária nem conta de pagamento e não autoriza saque, transferência entre usuários ou saldo armazenado.

### LedgerTransaction / LedgerEntry

`LedgerTransaction` agrupa um fato financeiro idempotente e referencia sua origem. `LedgerEntry` registra débito ou crédito, valor positivo em unidade mínima e moeda. Uma transação confirmada é imutável, tem débitos iguais aos créditos e somente pode ser corrigida por reversão ou lançamento compensatório.

### PaymentRecipient

Vínculo do instrutor com o recebedor no gateway, com estado de KYC/habilitação e identificador externo protegido. Não contém dados de cartão.

Estados internos mínimos, mapeados sem copiar cegamente o fornecedor:

```text
NOT_STARTED
PENDING
ENABLED
RESTRICTED
DISABLED
```

### WebhookReceipt / IdempotencyRecord

`WebhookReceipt` preserva metadados e payload permitido, assinatura verificada, estado de processamento e correlação. `IdempotencyRecord` impede repetição de efeitos em operações críticas. Ambos antecedem qualquer mutação financeira externa.

### Transfer / ReconciliationRecord

`Transfer` acompanha o repasse externo sem misturar seu estado com `Payment`. `ReconciliationRecord` compara ledger, pagamentos, transferências e extratos do gateway, registrando divergências e resolução.

### Dispute / DisputeEvidence

Contestação vinculada à reserva, com estado, motivo, responsáveis, prazos, evidências privadas e resolução. Efeitos financeiros ocorrem por operações próprias e lançamentos no ledger.

```text
OPEN
AWAITING_EVIDENCE
UNDER_REVIEW
RESOLVED
CLOSED
```

Resolução registra resultado estruturado e motivo. O serviço financeiro decide eventual operação de reembolso/compensação; alterar a disputa não edita diretamente `Payment` ou ledger.

### SupportCase

Atendimento ou denúncia não necessariamente financeira, com tipo (`SUPPORT`, `CONDUCT_REPORT`, `SAFETY`, `PRIVACY`), prioridade, status, solicitante, partes relacionadas, responsável e notas privadas. Denúncia pode suspender preventivamente por política autorizada, mas não é confundida com `Dispute`.

```text
OPEN
TRIAGED
IN_PROGRESS
WAITING_USER
RESOLVED
CLOSED
```

### Review

Avaliação vinculada a reserva concluída, com autor, destinatário, nota, comentário, moderação e eventual denúncia. Uma participação avalia a contraparte uma única vez por reserva.

### AuditEvent / OutboxEvent

`AuditEvent` é trilha append-only de ações sensíveis, com ator opcional para eventos de sistema. `OutboxEvent` registra, na mesma transação do domínio, eventos destinados a processamento assíncrono, com entrega idempotente.

### NotificationDelivery

Registro técnico de mensagem transacional: template/versionamento, canal, destinatário referenciado/mínimo, correlação, estado, tentativas e provedor. Conteúdo sensível não é duplicado em log. Falha de notificação não desfaz silenciosamente uma transação concluída; gera retry/alerta conforme criticidade.

## Transições e autoridades

| Agregado              | Transição sensível                 | Autoridade                                                   | Pré-condições mínimas                                                   |
| --------------------- | ---------------------------------- | ------------------------------------------------------------ | ----------------------------------------------------------------------- |
| Account               | ativar/bloquear/desativar          | serviço interno com `accounts.manage_account_lifecycle` explícita | versão esperada, motivo, lock, constraint, auditoria; `DEACTIVATED` terminal nesta fatia |
| RoleAssignment        | conceder/revogar papel pessoal     | serviço interno com permissão explícita                      | ator autorizado, papel válido, motivo, lock da pessoa, constraint ativa e auditoria |
| InstructorApplication | submeter                           | próprio instrutor                                            | dados/requisitos, aceites obrigatórios e consentimentos aplicáveis vigentes |
| InstructorApplication | aprovar/rejeitar/pedir informação  | revisor autorizado                                           | segregação, versão atual, documentos/veículo avaliados, regra/fonte e motivo estruturado |
| InstructorDocument    | verificar/rejeitar/revogar         | revisor/sistema autorizado                                   | arquivo promovido após scan; requisito aplicável                        |
| ServiceOffering       | ativar                             | instrutor via serviço                                        | política de publicação verdadeira e dados completos                     |
| LessonProposal        | aceitar                            | destinatário da versão                                       | versão aberta, não expirada, oferta/instrutor válidos e slot disponível |
| Booking               | `HELD → CONFIRMED`                 | serviço de pagamento                                         | pagamento confiável e hold não expirado                                 |
| Booking               | concluir/no-show/cancelar/disputar | participante/suporte conforme política                       | janela, ator, evidência e política versionada                           |
| Payment               | marcar pago/reembolsado/chargeback | adaptador após evento verificado ou reconciliação controlada | assinatura, idempotência, correlação e transição válida                 |
| LedgerTransaction     | confirmar                          | serviço financeiro                                           | origem idempotente, moeda única e débitos = créditos                    |
| Dispute               | resolver                           | função autorizada e segregada                                | evidências/janela; motivo e decisão estruturada                         |

Transições administrativas excepcionais exigem motivo, MFA quando sensíveis e `AuditEvent`; nunca alteram diretamente uma coluna fora do serviço do agregado.

## Invariantes

1. Perfil não publica sem elegibilidade.
2. Documento vencido pode remover elegibilidade.
3. Instrutor não revisa seus documentos.
4. Horários confirmados não se sobrepõem.
5. Preço congela após aceite.
6. Webhook duplicado não duplica efeito.
7. Avaliação exige aula concluída.
8. Mudança bancária exige autenticação reforçada.
9. Exclusão não apaga evidência legal necessária.
10. Status oficial e interno são independentes.
11. Uma conta pode acumular papéis pessoais compatíveis, mas nenhuma permissão, elegibilidade, publicação ou posição financeira é herdada entre papéis.
12. Publicável não significa habilitado para reserva paga.
13. Todo lançamento financeiro confirmado é imutável e balanceado.
14. Saldo é derivado de lançamentos; não é editável.
15. O ledger interno não representa custódia nem conta de pagamento.
16. Estado comercial não copia estado financeiro nem estado oficial.
17. Um aceite cria no máximo um booking e referencia uma proposta/política exatas.
18. Um booking não sobrepõe outro booking bloqueante para o mesmo instrutor/veículo; a lista de estados bloqueantes é definida no serviço e protegida no banco.
19. Reserva paga só confirma a partir de confirmação confiável do provedor; retorno do browser não confirma pagamento.
20. Oferta pública não expõe endereço residencial, documento, CPF, placa completa ou localização mais precisa que a necessária.
21. Denúncia de conduta/segurança e disputa financeira são casos distintos, ainda que correlacionados.
22. A autorização oficial do instrutor é requisito de evidência configurado para a jurisdição; aprovação interna nunca a substitui.
23. Toda política que afeta preço, cancelamento, no-show, conclusão ou disputa é versionada e preservada no acordo.
24. Dados demonstrativos são sintéticos e inequivocamente marcados; nunca são misturados à produção.
25. Aceite contratual, ciência de aviso e consentimento LGPD são fatos distintos; nenhum substitui o outro.
26. Despublicação automática por expiração registra regra/versão/motivo, notifica e admite contestação humana; perfil/score não gera decisão adversa final no MVP.
27. Dado declarado de menor de 18 anos falha fechado até `OPEN-014`; isso não presume afastamento do ECA Digital.

## Regras ainda não definidas

Os seguintes valores não são parte do domínio até a decisão correspondente: prazo do hold, duração mínima/máxima, buffers, comissão, tolerância de atraso, janelas e percentuais de cancelamento/no-show, prova de conclusão, prazo e resultados de disputa, retenção, limites de reembolso e método de aferição etária. O modelo deve suportar a política aprovada, mas sua implementação só começa nos gates de `DECISIONS.md`.

## Domínio adicional — demanda, matching e formação de oferta

### StudentDemand

Necessidade publicada pelo aluno. Contém aluno, jurisdição, ponto/área geográfica minimizada, raio, categoria pretendida, preferência de veículo/transmissão, janela de disponibilidade, faixa de preço opcional, estado, expiração e versão da política aplicável.

```text
DRAFT
OPEN
MATCHED
CONVERTED
EXPIRED
CANCELLED
```

`StudentDemand` não é booking nem proposta. `CONVERTED` referencia a negociação/reserva originada, sem copiar seus estados.

### DemandMatch

Resultado materializado ou calculado de compatibilidade entre `StudentDemand` e `ServiceOffering`/instrutor elegível. Registra versão do algoritmo/regra, score opcional, fatores explicáveis, distância aproximada e estado operacional. Não concede elegibilidade nem autorização.

```text
CANDIDATE
NOTIFIED
ENGAGED
DISMISSED
STALE
```

### InstructorCandidate

Pessoa/conta que declarou interesse em se tornar instrutor, mas ainda não possui perfil publicável de instrutor. Mantém jornada separada de `InstructorProfile` e não pode receber reservas.

### QualificationJourney / QualificationRequirementProgress

Checklist orientativo versionado por jurisdição para o candidato acompanhar requisitos e evidências. O resultado é sempre informativo (`PENDING`, `DECLARED_MET`, `EVIDENCE_PENDING`, `VERIFIED_INTERNAL`, `NOT_APPLICABLE`) e não usa o termo `APT` como decisão oficial.

### OfficialRegistryVerification

Registro de uma consulta ou revisão de evidência oficial: autoridade/fonte, método (`MANUAL`, `DOCUMENTED_API`, `AUTHORIZED_PROVIDER`), identificador mínimo permitido, data/hora, resultado normalizado, validade quando disponível, evidência protegida, revisor/adaptador e versão da regra. Não armazena senha/token Gov.br e não presume que ausência em consulta significa inaptidão sem regra oficial que o suporte.

### DemandAggregate

Projeção/consulta agregada por célula geográfica/cidade e filtros permitidos. Deve aplicar limiar mínimo e regras de privacidade antes de exposição a instrutores ou público.

### Invariantes adicionais

28. Demanda pública nunca revela localização residencial exata do aluno.
29. Apenas instrutor elegível/publicável participa do matching comercial.
30. Matching não altera elegibilidade e não cria booking automaticamente.
31. Pré-análise de candidato é orientação; somente autoridade competente concede autorização oficial.
32. Resultado oficial registra fonte e data e pode expirar/requerer nova verificação.
33. Ausência/falha de integração oficial não pode ser convertida automaticamente em rejeição definitiva.
34. Dados agregados de demanda respeitam limiar de anonimização/minimização definido antes do piloto.
35. Contato de prospecção e notificações respeitam base legal, preferências, opt-out e política aprovada.

## Extensão do domínio — Jornada CNH e profissionais de saúde

### Jurisdiction / OperationTerritory

Representa as 27 UFs e a ativação operacional por configuração, sem cidade estruturalmente obrigatória. A decisão territorial de 24/08/2026 estabelece:

- `commercial_status` representa estratégia operacional/comercial da InstrutorPro: `PREPARATION`, `FIRST_WAVE`, `ACTIVE`, `PAUSED`;
- `regulatory_status` representa prontidão interna para uma capacidade regulada: `NOT_REVIEWED`, `RESEARCHING`, `REVIEW_REQUIRED`, `APPROVED`, `SUSPENDED`;
- `regulatory_status` é contextual, não uma flag global: considera UF, tipo de prestador, serviço/capacidade, vigência, fonte e revisão humana;
- `commercial_status` nunca concede autorização, verificação ou publicação;
- a primeira onda técnica/comercial autorizada é RS, SC, SP, RJ e ES; AM, RO, AC e RR permanecem na matriz regulatória sem ativação automática; cidade de operação assistida/piloto é configuração posterior;
- `FederativeUnit.commercial_status` materializa somente a estratégia comercial; `RegulatoryReadiness` registra contexto separado por UF, tipo de prestador e capacidade, com vigência, fonte e revisão humana opcionais;
- a migration nova `territories/0002` preserva as cinco UFs da primeira onda e remove os campos legados sem editar `territories/0001_initial.py`;
- nenhum registro regulatório é criado pelo seed e nenhum papel implica verificação, publicação ou permissão.

## PRE-CODEX-02 FOUNDATION

`Account` continua responsável apenas por autenticação. `Person` é uma relação 1:1 opcional criada quando a conta representa pessoa natural e, nesta fundação, não coleta CPF, CNH ou outros identificadores civis. `RoleAssignment` permite zero ou mais papéis cumuláveis entre `STUDENT`, `INSTRUCTOR`, `DOCTOR` e `PSYCHOLOGIST`, com unicidade por pessoa/papel e sem herança de permissões. `Clinic` é organização; sua associação humana ocorre exclusivamente por `ClinicMembership` explícito. Perfis profissionais, elegibilidade, verificação e publicação permanecem fora desta execução.

## CODEX 02A — ROLE ASSIGNMENT

`grant_role()` e `revoke_role()` são comandos internos transacionais. Ambos validam policy deny-by-default, papel, motivo e contexto do ator; serializam comandos da mesma pessoa com `select_for_update`; e registram `AuditEvent` na mesma transação. Repetição retorna o ciclo vigente/mais recente sem duplicar estado e produz evento de no-op auditável. A clínica continua fora do enum pessoal. Nenhum endpoint ou perfil foi criado nesta fatia.

## CODEX 02B — ACCOUNT LIFECYCLE

`activate_account()`, `block_account()` e `deactivate_account()` são comandos internos transacionais. `ACTIVE` permite autenticação/operação protegida; `BLOCKED` e `DEACTIVATED` mantêm a conta e relações, mas definem `is_active=False`. `BLOCKED → ACTIVE` exige comando explícito, permissão, motivo e versão vigente. `DEACTIVATED` é terminal no CODEX 02B; eventual restauração exige futura decisão e serviço próprio. Repetição do estado já alcançado é no-op sem novo evento. `select_for_update`, versão otimista e constraint de coerência protegem concorrência; desativação tem precedência terminal sobre bloqueio concorrente.

### RegulatoryRule / VerificationSource

Regra versionada por escopo federal/estadual, tipo de prestador, vigência e fonte oficial. `VerificationSource` registra órgão, URL/identificador oficial, método permitido (`API`, `PUBLIC_LIST`, `MANUAL`, `DOCUMENT`) e data da última validação. Mudança normativa não reescreve evidência histórica.

### ClinicProfile

Perfil de estabelecimento relacionado aos exames da jornada CNH: razão/nome público, CNPJ protegido quando necessário, UF/cidade, localização pública minimizada, serviços declarados, credenciamento informado, status de verificação e vínculo com profissionais. Publicação depende de regra aplicável e evidência aprovada.

### HealthProfessionalProfile

Perfil de `DOCTOR` ou `PSYCHOLOGIST`, com conselho/registro profissional, UF, vínculos com clínicas, serviços aplicáveis, credenciamento/autorização exigidos pela jurisdição e status de verificação. Dados de saúde do aluno **não** integram perfil público nem devem ser compartilhados com o marketplace além do mínimo necessário.

### ClinicProfessionalAffiliation

Vínculo temporal entre clínica e profissional, com papel, vigência, fonte/evidência e status. Não presume vínculo empregatício nem substitui cadastro oficial.

### CnhJourney / JourneyStep

Modelo orientativo da jornada do usuário. Etapas e ordem devem ser versionadas por regra vigente; o sistema não declara conclusão oficial perante órgão público. Pode apontar serviços disponíveis para a etapa, preservando separação entre orientação InstrutorPro e ato oficial.

### Regra de papel

A modelagem futura deve substituir qualquer exclusividade legada `STUDENT`/`INSTRUCTOR` por compatibilidade explícita entre papéis, sem multiplicar contas. Autorização usa papel/capacidade/perfil e vínculo organizacional, preservando segregação e menor privilégio.

### Fora do MVP

`InstructorCandidate`, pré-análise para tornar-se instrutor e `InstructorQualificationJourney` ficam desativados/fora da implementação atual. A extensibilidade futura não autoriza coleta antecipada de dados para essa finalidade.


## Fluxo oficial por jurisdição

Serviços de saúde ligados à CNH não podem assumir livre escolha em todas as UFs. O domínio deve suportar `official_flow_mode` (`FREE_CHOICE`, `ASSIGNED_BY_AUTHORITY`, `REFERRED`, `UNKNOWN`) por UF e tipo de serviço. O exemplo inicial mais importante é RJ, onde o processo oficial pode indicar eletronicamente a clínica. O CTA da InstrutorPro deve respeitar essa regra.

## Extensão nacional do domínio — v1.6

O modelo persistente detalhado do MVP está em `DATA_MODEL_MVP.md` e passa a complementar este documento.

A plataforma suporta os papéis pessoais `STUDENT`, `INSTRUCTOR`, `DOCTOR` e `PSYCHOLOGIST`, com compatibilidade explícita. `Clinic` é organização e usa `ClinicMembership` para administração; `CLINIC_MANAGER` não é tratado como profissão pessoal nem substitui o vínculo organizacional.

Entram no núcleo do domínio: `CountrySubdivision`, `Municipality`, `RegulatoryRule`, `VerificationSource`, `Clinic`, `DoctorProfile`, `PsychologistProfile`, `Credential`, `OfficialVerification`, `PublicationDecision`, `OfficialFlowPolicy`, `StudentDemand`, `DemandMatch`, `DemandAggregate`, `Referral`, `JourneyDefinition` e `StudentJourney`.

O matching inicial é determinístico, versionado e explicável. A verificação oficial e a decisão interna de publicação são fatos distintos. A InstrutorPro não homologa profissional, exame ou conclusão de etapa oficial.

## Complemento M1 — credencial e foto do instrutor

`InstructorDocument` representa evidência privada e versionada. Quando a evidência é credencial do
instrutor, UF, identificador, emissão e validade permanecem internos; a revisão registra resultado,
fonte, ator, horário e motivo. `PENDING`, `UNDER_REVIEW`, `APPROVED`, `REJECTED` e `EXPIRED` são fatos
internos e não equivalem a homologação pelo Detran.

`ProfilePhoto` é independente dos documentos regulatórios. Upload, autorização para uso na
descoberta pública e ciência do notice são fatos separados. A revisão percorre `PENDING` para
`APPROVED`, `REJECTED` ou `REPLACEMENT_REQUESTED`, sempre por serviço de domínio e sem self-review.
Uma foto somente pode sair pela rota pública quando estiver aprovada, possuir autorização e o perfil
também estiver publicado; antes disso, o acesso é privado, autorizado e auditado.

Claims públicos de verificação são derivados de evidência limpa, aprovada e não vencida. Número de
credencial, arquivo, endereço residencial, CPF, CNH, placa completa, Renavam e justificativas de
revisão nunca integram o serializer público. Ausência, pendência, rejeição ou expiração de requisito
obrigatório bloqueia publicação; credencial isolada nunca concede elegibilidade.
