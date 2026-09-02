# Blueprint de Migrations — MVP InstrutorProCNH

Este documento define a ordem de criação do schema. Ele não substitui `DATA_MODEL_MVP.md` nem autoriza implementar fases bloqueadas.

## Princípios
- UUID como chave primária para entidades de negócio.
- UTC para timestamps.
- PostGIS para geografia.
- constraints e índices no banco para invariantes estáveis.
- migrations pequenas e cumulativas; migration aplicada nunca é editada.
- dados regulatórios e comerciais versionáveis; não codificar regras por UF em condicionais dispersas.
- nenhum dado clínico sensível no MVP.

## Sequência proposta

### M001 — core/territories
`Country`, `FederativeUnit` e metadados comerciais. Seed Brasil + 27 UFs. A `PRE-CODEX-02 FOUNDATION` materializou `commercial_status` e `RegulatoryReadiness` contextual na nova migration `territories/0002`; RS, SC, SP, RJ e ES ficam `FIRST_WAVE`, e todas as demais UFs ficam `PREPARATION`. Nenhuma prontidão regulatória é semeada.

### M002 — audit
`AuditEvent` append-only, ator opcional, request_id, ação, objeto, metadados minimizados e timestamp.

### M003 — accounts
Custom `Account` desde a primeira migration do app. `accounts/0003_alter_account_options_account_lifecycle_changed_at_and_more` implementa lifecycle, ator/motivo/timestamp, versão otimista, permissão explícita e constraint de coerência com `is_active`; contas históricas inativas migram conservadoramente para `DEACTIVATED`. Não adicionar perfis profissionais aqui.

### M004 — identity/legal
`Person`, `RoleAssignment`, `LegalDocument`, `LegalAcceptanceRecord`, `ConsentRecord`, `ContactVerificationChallenge` e `ExternalIdentity` inativa.

Implementado: `Person` e estrutura inicial de `RoleAssignment` em `people/0001`; histórico, atores/motivos, permissão explícita e unicidade parcial ativa em `people/0002_role_assignment_history_and_authorization`. Documentos, aceites, consentimentos e desafios continuam diferidos.

### M005 — students
`StudentProfile` e estrutura mínima de `StudentJourney`, sem dados clínicos/resultados de exames.

### M006 — providers
`InstructorProfile`, `DoctorProfile`, `PsychologistProfile`, `Clinic`, `ClinicMembership`, `ProfessionalClinicLink`.

Implementado antecipadamente apenas como estrutura: `Clinic` e `ClinicMembership` em `organizations/0001`. Onboarding, perfis e vínculos profissionais continuam diferidos.

### M007 — regulatory
`RegulatoryRule`, `VerificationSource`, `Credential`, `OfficialVerification`, `PublicationDecision`. Suportar escopo federal/UF, vigência e tipo de prestador.

### M008 — instructor onboarding
`InstructorApplication`, requisitos/documentos e `Vehicle`, respeitando storage privado e quarentena quando implementados.

### M009 — geography/services
`ServiceArea`, `ServiceOffering`, disponibilidade recorrente/exceções. Geometrias PostGIS com índices espaciais.

### M010 — demand/matching
`StudentDemand`, `DemandMatch`, `DemandAggregate`. Localização individual privada; agregados públicos devem aplicar limiares/política de privacidade.

### M011 — booking/referral
`Booking`, `Referral` e `official_flow_mode` (`FREE_CHOICE`, `ASSIGNED_BY_AUTHORITY`, `REFERRED`, `UNKNOWN`).

### M012 — finance
Somente após gate financeiro: ledger, `Payment`, `Transfer`, `Refund`, reconciliação e idempotência.

### M013 — trust/ops
`Review`, `SupportCase`, `NotificationDelivery`, outbox e demais estruturas operacionais aprovadas.

## Regras de papel
Pessoa e organização são conceitos distintos. Clínica é organização. Papéis de pessoa previstos: `STUDENT`, `INSTRUCTOR`, `DOCTOR`, `PSYCHOLOGIST`; vínculo administrativo com clínica usa `ClinicMembership`. Compatibilidades/proibições devem ser política explícita, não uma restrição global simplista `STUDENT XOR INSTRUCTOR` aplicada a todo o produto.

## Geolocalização
- coordenada precisa de aluno é privada;
- endereço residencial de profissional não é automaticamente ponto público de atendimento;
- pontos/áreas públicos derivam de local de serviço aprovado;
- índices GiST para geometrias consultadas;
- agregados de demanda não podem permitir reidentificação por baixa contagem.

## Regulatório
`RegulatoryRule` deve suportar as 27 UFs, ainda que a primeira onda de preenchimento profundo seja RS/SC/SP/RJ/ES, com detalhamento regulatório adicional de RO/AM/AC/RR. Fonte, vigência, última revisão e status de validação são obrigatórios para regra usada em decisão automática.
