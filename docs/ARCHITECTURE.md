# Arquitetura

Fonte oficial dos componentes e suas dependências. Estados e regras pertencem a `DOMAIN.md`; contratos HTTP a `API.md`; operação física a `DEVOPS.md`.

## Estilo

Monólito modular para validar o domínio com consistência transacional e operação simples.

```text
Angular/PWA
    |
Django + DRF
    |
    +-- accounts
    +-- people
    +-- instructors
    +-- verification
    +-- marketplace
    +-- scheduling
    +-- commercial_policies
    +-- bookings
    +-- payments
    +-- ledger
    +-- reviews
    +-- disputes
    +-- support
    +-- compliance
    +-- audit
    +-- notifications
    +-- integrations
    |
PostgreSQL + PostGIS
Redis + Celery
Object Storage
```

## Organização

```text
backend/
├── config/
├── apps/
│   ├── accounts/
│   ├── people/
│   ├── instructors/
│   ├── verification/
│   ├── marketplace/
│   ├── scheduling/
│   ├── bookings/
│   ├── payments/
│   ├── ledger/
│   ├── reviews/
│   ├── disputes/
│   ├── compliance/
│   ├── audit/
│   ├── notifications/
│   └── integrations/
├── tests/
└── manage.py

frontend/
└── src/app/{core,shared,auth,student,instructor,marketplace,finance,admin}
```

## Responsabilidade dos módulos

| Módulo                | Dono de                                                        | Pode depender de                                             |
| --------------------- | -------------------------------------------------------------- | ------------------------------------------------------------ |
| `accounts`            | conta, sessão, contato, MFA, identidade externa                | `audit`, `notifications` por serviços/eventos                |
| `people`              | pessoa e papel de negócio                                      | `accounts`, `audit`                                          |
| `compliance`          | organização, documentos, aceites, consentimentos e requisitos  | `accounts`, `people`, `audit`                                |
| `instructors`         | perfil, aplicação, documentos, veículo e elegibilidade         | `people`, `compliance`, `audit`, portas de storage/scan      |
| `marketplace`         | área, oferta, perfil público e busca                           | selectors de `instructors`, `scheduling`                     |
| `scheduling`          | regras/exceções, slots e sobreposição                          | `instructors`, `marketplace`                                 |
| `commercial_policies` | versões de política e cálculo de snapshots                     | configuração institucional; não depende de booking/pagamento |
| `bookings`            | solicitação, proposta, hold e ciclo comercial da aula          | `marketplace`, `scheduling`, `commercial_policies`, `people` |
| `ledger`              | partes, contas, transações e lançamentos                       | tipos financeiros próprios; não depende de API do gateway    |
| `payments`            | recebedor, cobrança, webhook, transferência e conciliação      | `bookings`, `ledger`, porta de pagamentos                    |
| `disputes`            | contestação comercial e evidência                              | `bookings`; solicita efeitos a `payments`, não o edita       |
| `reviews`             | avaliação e moderação                                          | leitura de `bookings` concluídos                             |
| `support`             | atendimento e denúncias                                        | referências aos agregados, sem assumir seus estados          |
| `notifications`       | templates e entregas                                           | outbox e portas de mensagem                                  |
| `audit`               | eventos append-only e consulta autorizada                      | contexto mínimo; nenhum módulo de negócio                    |
| `integrations`        | adaptadores de portas externas                                 | SDKs de fornecedor; nunca importado pelo domínio             |

Dependências entre módulos atravessam serviços públicos, selectors ou eventos; não importam tabelas internas para alterar estado. Ciclo de dependência é proibido. O backend valida essa direção por lint/teste arquitetural quando a estrutura existir.

## Camadas

- models: persistência;
- domain: regras;
- services: casos de uso;
- selectors: leitura;
- policies: autorização;
- tasks: assíncrono;
- api: HTTP;
- integrations: adaptadores;
- tests.

Evitar regra crítica em view, serializer, signal genérico ou frontend.

Fluxo de escrita:

```text
API/Task → validação de entrada → policy → application service
        → domínio + transaction + constraints
        → audit/outbox na mesma transação → resposta
```

Selectors são somente leitura e aplicam escopo autorizado. Tasks chamam os mesmos serviços de aplicação; não duplicam regra.

## Banco

- UUID;
- constraints;
- índices;
- transações;
- UTC;
- dinheiro em Decimal ou menor unidade;
- auditoria separada;
- PostGIS.

Constraints cobrem unicidade, exclusividade de papel, integridade do ledger e sobreposição que o PostgreSQL puder garantir. Locks e idempotência complementam constraints; não as substituem. Migrations são pequenas, forward-compatible e acompanhadas de estratégia de rollback/roll-forward.

## Eventos/outbox

Eventos: InstructorApproved, BookingConfirmed, PaymentPaid, BookingCompleted, DocumentExpired e DisputeOpened.

Usar outbox transacional antes de broker complexo.

`OutboxEvent` entra antes do primeiro evento assíncrono crítico e é gravado na mesma transação da mudança de domínio. Consumidores precisam ser idempotentes.

Entrega é pelo menos uma vez. “Publicado” e “processado” são marcadores distintos; retry com backoff e dead-letter operacional não pode perder a correlação. Auditoria não é substituída pela outbox.

## Celery

E-mail, OTP, antivírus, webhook, conciliação, expiração, documentos e agregação de avaliações.

O recebimento HTTP do webhook verifica assinatura e persiste o recibo idempotente antes de responder. Processamento pesado é assíncrono. Expiração de hold/documento tem varredura reconciliadora para tolerar tarefas perdidas.

## Contratos externos

```python
class PaymentProvider: ...
class MapProvider: ...
class MessageProvider: ...
class IdentityValidationProvider: ...
class TrafficAuthorityProvider: ...
class MalwareScanner: ...
```

As portas vivem próximas do caso de uso; adaptadores concretos ficam em `integrations`. DTOs de fornecedor são traduzidos na borda e não vazam para modelos.

## Login social preparado

`accounts` deve possuir um modelo interno `ExternalIdentity` desacoplado do fornecedor. A migration e as constraints entram na fundação; adaptador, endpoints, credenciais e interface Google ficam desativados até a conclusão do marco cadastral e de credenciamento.

Quando ativado, o Google será o único provedor inicialmente. O callback OIDC será processado pelo Django, que criará uma sessão web normal. Tokens do provedor não serão usados como sessão da API nem persistidos se o escopo for apenas autenticação.

## Razão financeiro interno

`ledger` mantém o registro financeiro por partidas dobradas, separado dos estados de `payments`, `bookings` e do gateway. O núcleo é formado por `FinancialParty`, `LedgerAccount`, `LedgerTransaction` e `LedgerEntry` e deve ser entregue como uma única fatia consistente.

- aluno, instrutor e plataforma têm partes financeiras independentes;
- uma conta de usuário nunca representa simultaneamente aluno e instrutor;
- a plataforma possui subcontas próprias de comissão, taxas, liquidação, estorno e perdas;
- contas técnicas representam compensação no gateway;
- saldo é derivado e qualquer projeção é reconstruível/reconciliável;
- lançamentos confirmados são append-only e balanceados;
- o ledger não oferece carteira, custódia, saque ou transferência entre usuários;
- o dinheiro real permanece no gateway/arranjo contratado.

`can_accept_paid_booking` exige recebedor `ENABLED` e `FinancialParty`/contas obrigatórias provisionadas; não existe uma flag genérica `instructor_financial_account`.

## API

`/api/v1`, OpenAPI, paginação, erros estáveis, idempotência, request ID e rate limit.

## Frontend

Angular + PrimeNG, mobile-first, PWA, acessível, formulários em etapas e mensagens claras sobre verificação interna.

Estado autoritativo permanece no backend. O frontend não calcula elegibilidade, preço final, comissão, permissão ou transição; apresenta motivos estruturados e trata repetição/reconexão com chaves idempotentes quando aplicável.

## Topologia e dados

```text
Internet → proxy/WAF → frontend estático + Django web
                              ├─ PostgreSQL/PostGIS
                              ├─ Redis (cache/fila, nunca fonte financeira)
                              ├─ workers/scheduler
                              └─ portas → storage/mensagens/mapas/gateway

telemetria ← proxy + web + worker + banco + integrações
backup ← banco + storage + configuração recuperável
```

- banco é fonte dos agregados, auditoria, outbox e ledger;
- object storage privado é fonte dos arquivos; banco mantém metadados/hash;
- Redis não guarda estado irrecuperável;
- nenhum ambiente de teste recebe dados reais;
- staging usa contas sandbox e configuração separada;
- produção usa segredos gerenciados, rede mínima e acesso administrativo auditado.

## Atributos de qualidade

| Atributo         | Mecanismo                                                         | Gate verificável                  |
| ---------------- | ----------------------------------------------------------------- | --------------------------------- |
| consistência     | transação, constraint, lock, idempotência                         | concorrência e retry em testes    |
| segurança        | deny by default, MFA, storage privado, segredo gerenciado         | checklist/threat model e testes   |
| privacidade      | minimização, segregação e lifecycle de dados                      | ROPA/retenção e teste de direitos |
| auditabilidade   | eventos append-only e correlação                                  | ações sensíveis cobertas          |
| resiliência      | timeout, retry seguro, circuit breaker quando útil, reconciliação | falhas de contrato e runbooks     |
| operabilidade    | logs, métricas, traces seletivos, health/readiness                | alertas e smoke em staging        |
| recuperabilidade | backup criptografado e restore testado                            | RPO/RTO aprovados antes do piloto |

## Evolução

Extrair serviços somente por escala independente, limite organizacional estável, isolamento regulatório ou carga específica.

## Extensão arquitetural — geografia, demanda e matching

Adicionar módulos no monólito modular somente quando a fase correspondente for liberada:

```text
demands/          # StudentDemand e agregações
matching/         # regras determinísticas e explicação de compatibilidade
qualification/    # candidato e Academia/checklists
registries/       # portas/adaptadores de verificação oficial
```

PostGIS é a fonte geoespacial do MVP para áreas, distância, raio e agregações. Coordenadas precisas permanecem protegidas; APIs públicas retornam geometria/precisão reduzida conforme política.

`MatchingService` recebe demanda + ofertas elegíveis e produz candidatos com `rule_version` e fatores explicáveis. Não chama modelo de IA no caminho crítico do MVP. Futuro `MatchingRanker` inteligente deve ficar atrás de interface substituível e feature flag.

`OfficialRegistryProvider` é uma porta com operações mínimas de verificação suportadas pela fonte. Adaptadores só são ativados quando a integração for documentada/autorizada. Revisão manual é um adaptador operacional válido e auditável.

## Arquitetura nacional e ecossistema CNH

A aplicação permanece monólito modular Django/DRF + Angular/PrimeNG + PostgreSQL/PostGIS + Redis/Celery. A expansão nacional deve ocorrer por **configuração e dados versionados**, não por branches de código por UF.

Novos módulos lógicos previstos: `jurisdictions`, `regulatory`, `clinics`, `health_professionals`, `journey` e `verification`. O módulo geográfico atende mapa/lista de instrutores, clínicas e profissionais, além de demanda agregada. PostGIS é a fonte de consultas espaciais; coordenadas exatas privadas não são retornadas em endpoints públicos.

Integrações oficiais usam adapters por capacidade e fonte. Nenhum adapter pode depender, como requisito do MVP, de scraping autenticado, credencial Gov.br do usuário ou endpoint não documentado.

### MAPA ONLINE 01

O módulo `discovery` separa `public_service_location` de `private_location`. A
busca usa GeoDjango/PostGIS (`distance_lte` e `Distance`). O frontend encapsula
Leaflet/OpenStreetMap em `MapProvider`. `GeocodingProvider` é substituível; o
adapter demo atual resolve offline apenas cinco cidades e não transmite consultas.
Produção continua bloqueada por `OPEN-007` e avaliação LGPD.
