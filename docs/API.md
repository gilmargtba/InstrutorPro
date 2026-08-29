# Contrato da API

## CODEX 02E — onboarding sintético

`POST /api/v1/demo/instructor-onboarding/` aceita somente o formulário DEMO das cinco
etapas, exige confirmação de dados sintéticos e consentimento da localização de
atendimento. Não aceita CPF, CNH, residência ou upload. Cria conta sintética sem senha
utilizável e termina em `SUBMITTED/UNPUBLISHED`. Não há endpoint público de revisão,
verificação ou publicação.

## Configuração organizacional administrativa

`PlatformOrganization` é configurada exclusivamente no Django Admin. Não existe rota
pública em `/api/v1` para criar, alterar, validar ou consultar os dados administrativos
do controlador. Avisos/termos futuros só poderão consumir uma projeção pública mínima e
aprovada; esta fatia não criou essa projeção.

## Descoberta geoespacial demonstrativa

- `GET /api/v1/geocoding/search/?q=Porto%20Alegre`: catálogo sintético local.
- `GET /api/v1/instructors/search/?latitude=-30.0346&longitude=-51.2177&radius_km=10&category=B`: busca PostGIS; aceita `transmission` e `vehicle_available`.

A resposta é mínima, marcada `demo=true`, ordenada por distância e nunca contém
`private_location`, endereço, contato, credencial ou elegibilidade. Raios aceitos:
5, 10, 20 e 50 km.

Fonte oficial dos comportamentos HTTP internos. Endpoints são implementados somente na fase indicada pelo plano e publicados no OpenAPI quando existirem; esta lista não autoriza antecipar escopo nem inventar integração externa.

Base: `/api/v1`.

## Convenções

- JSON UTF-8; arquivo usa fluxo de upload explicitamente documentado;
- UUID opaco em recursos públicos; documento, CPF, placa completa e IDs de fornecedor não entram em URL pública;
- timestamps ISO 8601 com timezone e persistência UTC; datas civis sem conversão de timezone;
- dinheiro como objeto `{ "amount": 12345, "currency": "BRL" }`, em unidade mínima;
- paginação por cursor para listas mutáveis; `next_cursor` opaco e limite máximo do servidor;
- filtros com allowlist; ordenação estável; busca pública nunca retorna inelegíveis;
- sessão Django por cookie Secure/HttpOnly/SameSite; mutações exigem CSRF;
- `X-Request-ID` aceito se válido ou gerado; sempre retornado;
- `Idempotency-Key` obrigatório nas operações declaradas; chave é escopada por conta, operação e payload canônico;
- payload diferente com a mesma chave retorna `IDEMPOTENCY_KEY_REUSED`;
- cliente nunca define papel interno, status, elegibilidade, preço calculado, comissão ou lançamento;
- breaking change exige nova versão; campos aditivos respeitam compatibilidade e OpenAPI.

## Respostas

Recurso único usa o próprio objeto JSON. Lista:

```json
{
  "results": [],
  "page": {
    "next_cursor": null,
    "has_more": false
  }
}
```

Erro estável:

```json
{
  "error": {
    "code": "BOOKING_SLOT_UNAVAILABLE",
    "message": "O horário não está mais disponível.",
    "details": {},
    "request_id": "00000000-0000-0000-0000-000000000000"
  }
}
```

`message` é segura e traduzível; cliente decide pelo `code`. `details` não expõe existência de conta, dado protegido, stack, payload de fornecedor ou policy interna.

|        HTTP | Uso                                                             |
| ----------: | --------------------------------------------------------------- |
| 200/201/204 | sucesso conforme operação                                       |
|         400 | formato/validação sintática                                     |
|         401 | sessão ausente/inválida                                         |
|         403 | autenticado sem permissão ou MFA requerido                      |
|         404 | inexistente ou oculto por autorização por objeto                |
|         409 | estado, versão, idempotência ou concorrência conflitante        |
|         410 | desafio, hold ou URL temporária expirados quando seguro revelar |
|         422 | regra de domínio não satisfeita                                 |
|         429 | limite excedido, com retry seguro quando aplicável              |
|         503 | dependência indisponível sem confirmação do efeito              |

## Concorrência, versão e idempotência

- recursos editáveis retornam `version`; update sensível envia `If-Match`/versão esperada;
- proposta aceita referencia `proposal_id` e `proposal_version` exatos;
- aceite, pagamento, recebedor, reembolso e operações financeiras exigem `Idempotency-Key`;
- upload possui correlação própria; substituição não apaga evidência já usada em decisão;
- webhooks usam ID do evento do provedor + hash permitido, além de assinatura;
- timeout de operação externa retorna estado consultável; cliente não deve assumir falha nem repetir sem a mesma chave;
- resposta idempotente repete status/corpo compatíveis da primeira conclusão.

## Representações mínimas

### Elegibilidade

```json
{
  "can_publish": false,
  "can_accept_paid_booking": false,
  "reasons": [
    { "code": "DOCUMENT_REQUIRED", "resource_id": "uuid", "action": "UPLOAD" }
  ],
  "rule_version": "eligibility/2026-07-22",
  "evaluated_at": "2026-07-22T12:00:00Z"
}
```

Razões são estruturadas, seguras e calculadas no backend. Não expõem regra de antifraude, mas permitem compreender a decisão objetiva e pedir revisão humana.

### Proposta e booking

Proposta inclui autor, destinatário, oferta, início/fim, ponto minimizado, veículo quando aplicável, preço total, versão de política e expiração. Booking retorna estado comercial, snapshots, `hold_expires_at` quando `HELD` e referências separadas a resumo de pagamento/disputa; nunca copia o estado financeiro para `status`.

### Extrato

Cada item informa fato, débito/crédito na perspectiva autorizada, valor, moeda, data efetiva, origem segura e saldo derivado quando suportado. Não oferece mutação, depósito, saque ou transferência entre usuários.

## Autenticação e conta — A3–A6

```http
POST   /auth/register
POST   /auth/login
POST   /auth/logout
POST   /auth/email/request-verification
POST   /auth/email/verify
POST   /auth/phone/request-code
POST   /auth/phone/verify
POST   /auth/password/request-reset
POST   /auth/password/reset
POST   /auth/mfa/challenge
GET    /me
GET    /me/sessions
DELETE /me/sessions/{session_id}
```

Registro recebe apenas dados de conta permitidos; papel é escolhido em operação posterior. Solicitações de login/recuperação usam respostas antienumeração. Segredo de desafio é write-only e nunca reaparece.

### Google — Gate A19/M2.1, rotas inexistentes antes do gate

```http
POST   /auth/google/start
GET    /auth/google/callback
POST   /me/external-identities/google/link
DELETE /me/external-identities/google
```

OIDC termina em sessão Django. Callback valida assinatura, issuer, audience, expiração, `state` e `nonce`; `sub` identifica o vínculo. Coincidência de e-mail não vincula conta. Link/unlink exige reautenticação e não remove o último método válido de acesso.

## Jurídico, pessoa e papel — A7–A11

```http
GET    /legal/documents/current?audience=STUDENT
POST   /me/legal-acceptances
GET    /me/legal-acceptances
POST   /me/consents
GET    /me/consents
POST   /me/consents/{consent_id}/withdraw
GET    /me/person
PATCH  /me/person
POST   /me/roles
GET    /me/roles
GET    /student/profile
PATCH  /student/profile
```

Aceite obrigatório registra contrato/termo exato em `LegalAcceptanceRecord`; concessão e retirada opcionais registram `ConsentRecord` por finalidade. Nenhuma rota de aceite concede consentimento, e retirada não desfaz tratamento anterior lícito nem impede finalidade sustentada por outra base informada.

O contrato futuro de papéis deverá permitir concessões idempotentes de `STUDENT`, `INSTRUCTOR`, `DOCTOR` e `PSYCHOLOGIST` conforme policy explícita de compatibilidade. Combinação incompatível retorna erro estável sem remover papéis existentes. Cada endpoint protegido exige papel, perfil, verificação e autorização próprios; papel coincidente não concede publicação nem capacidade transitiva. Administração de `Clinic` usa recurso organizacional `ClinicMembership`, não papel pessoal `CLINIC`. O path e payload definitivos serão estabilizados antes da implementação; o antigo contrato singular `POST /me/business-role` está substituído.

## Credenciamento do instrutor — A12–A17

```http
GET    /instructor/profile
PATCH  /instructor/profile
POST   /instructor/application
GET    /instructor/application
POST   /instructor/application/submit
GET    /instructor/document-requirements
GET    /instructor/documents
POST   /instructor/documents
POST   /instructor/documents/{document_id}/replacement
DELETE /instructor/documents/{document_id}
GET    /instructor/vehicles
POST   /instructor/vehicles
PATCH  /instructor/vehicles/{vehicle_id}
GET    /instructor/eligibility
POST   /instructor/eligibility-review-requests
```

Documento só pode ser removido se estiver em estado descartável e não for evidência; caso contrário é revogado/substituído conforme domínio. Upload passa por quarentena e scan antes de revisão. Download administrativo ou do titular usa autorização just-in-time e URL assinada curta/redirecionamento seguro, nunca URL persistida no recurso. Despublicação automática objetiva informa motivo/versão e admite pedido auditável de revisão humana.

## Oferta, disponibilidade e marketplace — B1–B4

```http
GET/POST    /instructor/service-areas
PATCH/DELETE /instructor/service-areas/{area_id}
GET/POST    /instructor/offerings
PATCH       /instructor/offerings/{offering_id}
POST        /instructor/offerings/{offering_id}/activate
POST        /instructor/offerings/{offering_id}/pause
GET/POST    /instructor/availability-rules
PATCH/DELETE /instructor/availability-rules/{rule_id}
GET/POST    /instructor/availability-exceptions
DELETE      /instructor/availability-exceptions/{exception_id}
GET         /marketplace/instructors
GET         /marketplace/instructors/{instructor_id}
GET         /marketplace/instructors/{instructor_id}/offerings
GET         /marketplace/offerings/{offering_id}/slots
GET         /marketplace/instructors/{instructor_id}/reviews
```

Filtros permitidos: ponto/raio ou cidade/UF, categoria, transmissão, veículo, data, faixa de preço e nota. Precisão residencial não é retornada. Slot é indicativo até o aceite transacional.

## Solicitações, propostas e reserva — B5–B6

```http
POST /lesson-requests
GET  /lesson-requests
GET  /lesson-requests/{request_id}
POST /lesson-requests/{request_id}/proposals
POST /lesson-proposals/{proposal_id}/accept
POST /lesson-proposals/{proposal_id}/decline
POST /lesson-requests/{request_id}/cancel
GET  /bookings
GET  /bookings/{booking_id}
POST /bookings/{booking_id}/cancel
```

`POST /lesson-proposals/{id}/accept` exige idempotência, trava proposta/slot, recalcula autorização/eligibilidade, cria um `Booking=HELD`, marca a solicitação convertida e retorna ambos. Não existe `POST /bookings` avulso. Cancelamento exige motivo permitido e retorna efeito comercial; eventual efeito financeiro é uma operação separada e pode ficar pendente.

## Recebedor, pagamento e ledger — C1–C7

```http
POST /instructor/payment-recipient
GET  /instructor/payment-recipient
POST /bookings/{booking_id}/payment-intent
GET  /payments/{payment_id}
POST /payments/{payment_id}/refund-requests
GET  /instructor/transfers
GET  /me/financial-statement
POST /webhooks/payments/{provider}
GET  /admin/finance/platform-statement
GET  /admin/finance/reconciliation
POST /admin/finance/reconciliation/{record_id}/resolve
POST /admin/payments/{payment_id}/refunds
```

Browser/redirect não confirma pagamento. Endpoint de webhook recebe corpo bruto, verifica assinatura antes de interpretar, persiste `WebhookReceipt` idempotente e responde rapidamente. Toda mutação financeira confirmada gera `LedgerTransaction` balanceada; reembolso, chargeback e ajuste criam reversão/compensação vinculada.

## Execução, disputa, suporte e reputação — D1–D3

```http
POST /bookings/{booking_id}/check-in
POST /bookings/{booking_id}/request-completion
POST /bookings/{booking_id}/confirm-completion
POST /bookings/{booking_id}/report-no-show
POST /bookings/{booking_id}/disputes
GET  /disputes/{dispute_id}
POST /disputes/{dispute_id}/evidence
POST /bookings/{booking_id}/reviews
GET  /reviews/{review_id}
POST /reviews/{review_id}/reports
POST /support-cases
GET  /support-cases/{case_id}
POST /support-cases/{case_id}/messages
```

Check-in não é homologação oficial. Evidências e mensagens de caso são privadas e têm tipos/tamanhos permitidos. Partes veem somente o subconjunto autorizado; nota interna e dados de terceiros são omitidos.

## Administração — por fase

```http
GET  /admin/instructor-applications
GET  /admin/instructor-applications/{application_id}
POST /admin/instructor-applications/{application_id}/request-information
POST /admin/instructor-applications/{application_id}/approve
POST /admin/instructor-applications/{application_id}/reject
POST /admin/instructors/{instructor_id}/suspend
POST /admin/instructors/{instructor_id}/reactivate
GET  /admin/documents/review-queue
POST /admin/documents/{document_id}/approve
POST /admin/documents/{document_id}/reject
GET  /admin/bookings
GET  /admin/payments
GET  /admin/disputes
POST /admin/disputes/{dispute_id}/resolve
GET  /admin/support-cases
POST /admin/support-cases/{case_id}/assign
POST /admin/support-cases/{case_id}/resolve
GET  /admin/audit-events
```

Toda decisão recebe motivo estruturado/texto seguro, versão esperada e MFA quando a matriz exigir. Acesso administrativo a documento completo e exportação são operações próprias, temporárias e auditadas.

## Privacidade — antes de produção

```http
POST /privacy/requests
GET  /privacy/requests/{request_id}
GET  /privacy/requests/{request_id}/export
POST /me/account-deactivation
```

`POST /privacy/requests` aceita titular autenticado ou canal externo com verificação posterior proporcional, é idempotente e retorna protocolo/status sem expor existência de conta. Exportação só existe após conclusão, com autenticação reforçada e artefato criptografado/temporário. Os contratos finais dependem da tabela de retenção e parecer de `OPEN-008`; confirmação/acesso simplificado são imediatos quando seguros e declaração completa observa o prazo legal de 15 dias. Eliminação não apaga ledger/auditoria/evidência legal isoladamente; executa anonimização, bloqueio ou retenção justificada por categoria e propaga a destinatários aplicáveis.

## Contrato OpenAPI e observabilidade

Cada operação documenta autenticação, papel/policy, request/response, erros de domínio, idempotência, rate limit, efeitos assíncronos e exemplos sem dado real. CI falha por schema inválido ou breaking change não versionada. Métricas usam nome da operação, status e duração; IDs/dados pessoais não viram label de alta cardinalidade.

## Demanda, matching e qualificação — extensão planejada

Rotas abaixo são contratos planejados e só existem após os respectivos gates:

```text
GET    /api/v1/marketplace/instructors
GET    /api/v1/marketplace/demand-aggregates
POST   /api/v1/student-demands
GET    /api/v1/student-demands/{id}
PATCH  /api/v1/student-demands/{id}
POST   /api/v1/student-demands/{id}/publish
POST   /api/v1/student-demands/{id}/cancel
GET    /api/v1/student-demands/{id}/matches

POST   /api/v1/instructor-candidates
GET    /api/v1/instructor-candidates/me/journey
PATCH  /api/v1/instructor-candidates/me/journey
GET    /api/v1/qualification/requirements

POST   /api/v1/admin/official-verifications
GET    /api/v1/admin/official-verifications/{id}
```

A resposta de match pode incluir distância aproximada, score e fatores permitidos, mas nunca endereço preciso, documentos, CPF, placa completa ou atributos usados apenas para controles internos. Endpoints administrativos exigem autorização por objeto, motivo/auditoria e MFA conforme sensibilidade.

## APIs previstas — jornada nacional

Namespaces planejados, sujeitos aos gates do plano: `/jurisdictions`, `/journey`, `/clinics`, `/health-professionals`, `/verification-sources`, `/regulatory-rules`, além dos endpoints existentes de marketplace/demanda. Endpoints públicos retornam apenas projeções minimizadas; evidências, documentos, coordenadas exatas e identificadores protegidos ficam em endpoints privados com autorização por objeto.
