# Modelo de Dados Definitivo do MVP — InstrutorProcnh

## CODEX 02D

`Person → InstructorProfile → InstructorServiceArea`, com históricos em `ProfessionalVerification`, `PublicationDecision` e `LocationPublicationAuthorization`. Localização privada é distinta do ponto público.

Versão documental: 2.3

Este documento traduz `VISION.md`, `DOMAIN.md`, `GOV_002_NATIONAL.md` e `LGPD.md` para um modelo persistente inicial em Django + PostgreSQL/PostGIS. Ele é a referência para as migrations do MVP; mudanças estruturais posteriores exigem ADR/decisão registrada.

## 1. Princípios

- UUID como identificador público e interno das entidades de negócio.
- PostgreSQL + PostGIS para localização, distância, raio, áreas e agregações geográficas. O Django recomenda PostGIS como backend espacial maduro e rico em recursos.
- Nenhum CPF, CNH, CRM, CRP, endereço residencial, laudo ou documento privado em endpoints públicos.
- Resultado de exame, diagnóstico, laudo médico, prontuário e conteúdo de avaliação psicológica ficam fora do MVP.
- Fonte oficial e evidência de verificação são fatos separados do perfil comercial.
- Regras regulatórias são versionadas e parametrizadas por jurisdição; não usar `if uf == ...` como regra de negócio permanente.
- Localização pública é aproximada/operacional e separada de endereço residencial.
- Mapas de demanda usam agregação e limiar mínimo; nunca expõem ponto individual do aluno.

## 2. Identidade e papéis

### Account
Autenticação, status, contatos e sessão. `CODEX 02B` adiciona `lifecycle_status` (`ACTIVE`, `BLOCKED`, `DEACTIVATED`), última mudança/ator/motivo e `lifecycle_version`. A constraint `account_lifecycle_matches_is_active` impede combinações incoerentes. Histórico completo de transições permanece nos `AuditEvent`; nenhuma transição apaga `Person` ou `RoleAssignment`.

### Person
Dados civis protegidos. Relação 1:1 com Account quando aplicável.

### RoleAssignment
Papéis de negócio permitidos no MVP:

- `STUDENT`
- `INSTRUCTOR`
- `DOCTOR`
- `PSYCHOLOGIST`

Papéis internos administrativos permanecem separados.

A antiga exclusividade `STUDENT XOR INSTRUCTOR` é substituída por política de compatibilidade versionada. `STUDENT`, `INSTRUCTOR`, `DOCTOR` e `PSYCHOLOGIST` podem coexistir quando compatíveis, sempre com perfil, requisito, verificação, publicação e autorização independentes. Uma clínica é organização, não papel pessoal; administração usa `ClinicMembership`.

O `CODEX 02A` materializa ciclos históricos de `RoleAssignment`: concedente/motivo/data, revogador/motivo/data e status derivado `ACTIVE`/`REVOKED`. A constraint `uq_active_person_role` permite múltiplos ciclos históricos, mas somente um ativo por pessoa/papel. Toda mutação passa por serviço interno autorizado e gera auditoria minimizada.

## 3. Jurisdição e operação nacional

### CountrySubdivision
UF brasileira: código IBGE, sigla, nome, status operacional.

`commercial_status`: `PREPARATION`, `FIRST_WAVE`, `ACTIVE`, `PAUSED`.

`regulatory_status`: contextual por UF, tipo de prestador, serviço/capacidade, vigência, fonte e revisão humana; valores iniciais `NOT_REVIEWED`, `RESEARCHING`, `REVIEW_REQUIRED`, `APPROVED`, `SUSPENDED`.

Primeira onda técnica ativa nesta fundação: RS, SC, SP, RJ e ES. O modelo contém as 27 UFs; AM, RO, AC, RR e as demais permanecem `PREPARATION` e não são ativadas automaticamente. A migration `territories/0002` introduz `commercial_status` e `RegulatoryReadiness` contextual sem alterar a migration histórica.

### Fundação implementada antes do CODEX 02

`Account` autentica; `Person` representa opcionalmente a pessoa natural sem armazenar CPF/CNH; `RoleAssignment` associa zero ou mais papéis pessoais compatíveis; `Clinic` representa organização e `ClinicMembership` associa a pessoa com autorização explícita. Perfis e estados profissionais permanecem planejados, não implementados.

### Municipality
Código IBGE, UF, nome, slug e ponto/centroide quando necessário.

### RegulatoryRule
Regra versionada federal/estadual por tipo de prestador, vigência e fonte legal.

### VerificationSource
Fonte oficial ou autorizada: SENATRAN, DETRAN, consulta pública, integração formal ou revisão manual.

## 4. Perfis

### StudentProfile
Objetivo da jornada, categoria pretendida, preferências não sensíveis e município padrão.

### InstructorProfile
Pessoa profissional, apresentação, categorias, experiência declarada, estado de publicação e reputação agregada.

### Clinic
Organização prestadora: razão social/nome público, CNPJ protegido, contatos públicos, UF/município, localização operacional, serviços e publicação.

### ClinicMembership
Vínculo entre Account e Clinic com papel (`OWNER`, `MANAGER`, `STAFF`) e vigência.

### DoctorProfile
Pessoa profissional com dados públicos mínimos, registro profissional protegido/mascarado, UF de registro, vínculos com clínicas e publicação.

### PsychologistProfile
Pessoa profissional com dados públicos mínimos, registro profissional protegido/mascarado, UF de registro, vínculos com clínicas e publicação.

### ProfessionalClinicLink
Vínculo versionado entre médico/psicólogo e clínica, com estado e vigência.

## 5. Credenciamento e verificação

### Credential
Credencial declarada de instrutor, clínica, médico ou psicólogo.

Campos centrais:
- `subject_type`
- `subject_id`
- `credential_type`
- `jurisdiction_scope`
- `uf`
- número protegido + representação mascarada
- emissão/validade
- status declarado

### CredentialEvidence
Arquivo/evidência privada associada à credencial, com hash, storage privado, scan e revisão.

### OfficialVerification
Snapshot de verificação:
- sujeito/credencial
- fonte
- método (`API`, `PUBLIC_QUERY`, `MANUAL`, `DOCUMENT_REVIEW`)
- status observado
- payload mínimo normalizado
- referência/URL da fonte quando permitido
- `checked_at`
- `valid_until` quando aplicável
- revisor quando manual

Estados:
- `PENDING`
- `VERIFIED`
- `NOT_FOUND`
- `DIVERGENT`
- `EXPIRED`
- `REVOKED`
- `INCONCLUSIVE`

Nunca interpretar `NOT_FOUND` automaticamente como fraude ou inaptidão.

### PublicationDecision
Decisão interna da InstrutorProcnh, separada da autorização estatal. Registra sujeito, decisão, motivos, regra/política, autor e data.

## 6. Localização, catálogo e descoberta

### ServiceArea
Área de atendimento de instrutor/clínica/profissional: município, raio e futura geometria/polígono.

### ServiceOffering
Serviço ofertado:
- aula prática
- exame/avaliação como informação/agendamento quando juridicamente permitido
- duração/preço somente quando aplicável
- categoria
- veículo/transmissão quando aula
- vigência

### OfficialFlowPolicy
Política por UF + tipo de serviço:
- `FREE_CHOICE`
- `ASSIGNED_BY_AUTHORITY`
- `REFERRED`
- `UNKNOWN`

A UI e API devem respeitar essa política antes de permitir seleção/agendamento.

## 7. Demanda do aluno e matching

### StudentDemand
Necessidade publicada pelo aluno.

Campos mínimos:
- aluno
- tipo de necessidade (`INSTRUCTOR`, `MEDICAL_EXAM`, `PSYCHOLOGICAL_EVALUATION`, `CLINIC`)
- UF/município
- ponto privado opcional
- raio
- categoria CNH quando aplicável
- transmissão/veículo quando aplicável
- janelas de preferência
- faixa de preço opcional
- status
- expiração

Estados:
- `DRAFT`
- `ACTIVE`
- `MATCHED`
- `CONVERTED`
- `EXPIRED`
- `CANCELLED`

### DemandMatch
Resultado explicável entre demanda e oferta/profissional.

Campos:
- demanda
- alvo
- distância
- score total
- componentes do score em JSON estruturado
- motivos de inclusão/exclusão
- versão do algoritmo
- data de cálculo

O MVP usa matching determinístico. IA não decide elegibilidade nem autorização.

### DemandAggregate
Agregado materializado/cacheável por município/UF/categoria/faixa temporal para mapas e radar de expansão. Deve aplicar limiar de privacidade e nunca conter identificador de aluno.

## 8. Agenda e contratação

### AvailabilityRule / AvailabilityException
Agenda recorrente e exceções com timezone IANA.

### LessonRequest / LessonProposal
Negociação de aula entre aluno e instrutor, com versões imutáveis.

### Booking
Reserva confirmada após aceite/hold. Para serviços de saúde oficiais, só existe se a política da UF permitir que a InstrutorProcnh participe do agendamento; caso contrário, registrar apenas encaminhamento informativo quando aprovado.

### Referral
Encaminhamento para clínica/profissional/fluxo oficial quando a InstrutorProcnh não controla o agendamento. Não presume conclusão do exame e não armazena resultado clínico.

## 9. Pagamento, reputação e suporte

Mantêm-se as entidades já definidas em `DOMAIN.md`:
- `Payment`
- `Transfer`
- `LedgerTransaction`
- `LedgerEntry`
- `ReconciliationRecord`
- `Review`
- `Dispute`
- `SupportCase`

Pagamento de aula entra no MVP conforme gate comercial/jurídico. Monetização de exames/clínicas não é presumida.

## 10. Jornada CNH

### JourneyDefinition
Modelo versionado de jornada por contexto regulatório.

### JourneyStepDefinition
Etapas informativas e ordem de apresentação.

### StudentJourney
Instância do aluno sem armazenar dado clínico sensível desnecessário.

### StudentJourneyStep
Estado informativo da etapa:
- `NOT_STARTED`
- `IN_PROGRESS`
- `ACTION_REQUIRED`
- `DONE_DECLARED`
- `NOT_APPLICABLE`

`DONE_DECLARED` significa declaração/registro operacional permitido, não homologação oficial pela InstrutorProcnh.

## 11. Auditoria e LGPD

### AuditEvent
Append-only para ações sensíveis.

### DataProcessingActivity
Catálogo/ROPA operacional por finalidade, categoria de dado, base legal aprovada, retenção e agentes envolvidos.

### DataSubjectRequest
Solicitações de acesso, correção, oposição, portabilidade quando aplicável, anonimização/eliminação quando cabível e revisão.

### ConsentRecord / LegalAcceptanceRecord
Mantidos separados conforme `LGPD.md`.

## 12. Índices e constraints essenciais

- GiST em campos geográficos usados em busca por distância/interseção.
- índice por `(uf, municipality, publication_status)` nos prestadores.
- índice por `(status, expires_at)` em demandas.
- unicidade/versionamento coerente em regras regulatórias e políticas de fluxo.
- uma verificação oficial nunca sobrescreve histórico anterior.
- publicação exige `PublicationDecision` válida.
- credenciais vencidas disparam reavaliação, não edição destrutiva do histórico.
- pontos privados de aluno não entram em serializers públicos.

## 13. Ordem de migrations recomendada

1. identidade/auditoria/legal;
2. UF/município/jurisdição;
3. perfis de aluno e profissionais;
4. credenciais/evidências/verificações;
5. catálogo/áreas/ofertas/fluxos oficiais;
6. demanda/matching/agregados;
7. agenda/negociação/booking/referral;
8. pagamentos/ledger;
9. jornada CNH;
10. reputação/suporte/LGPD operacional.

## 14. Fora do MVP

- Academia do Instrutor / candidato a instrutor;
- armazenamento de laudos, diagnósticos ou resultado psicológico/médico;
- decisão regulatória por IA;
- scraping autenticado ou automação contra fonte sem autorização;
- app nativo;
- monetização automática de exames sem validação jurídica/regulatória.
