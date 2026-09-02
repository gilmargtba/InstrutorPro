# Codex 01 — Fundação Técnica InstrutorProcnh

## Objetivo
Criar somente a fundação executável do monólito modular InstrutorProcnh. Não implementar marketplace, mapa, matching, pagamentos, integrações governamentais ou fluxos clínicos nesta tarefa.

## Leitura obrigatória antes de alterar arquivos
1. `README.md`
2. `AGENTS.md`
3. `docs/MANIFEST.json`
4. `docs/CHECKPOINT.md`
5. `docs/ARCHITECTURE.md`
6. `docs/DATA_MODEL_MVP.md`
7. `docs/LGPD.md`
8. `docs/SECURITY.md`
9. `docs/IMPLEMENTATION_PLAN.md`
10. `docs/BACKLOG.md`

Se houver conflito, seguir a hierarquia documental definida no README e não inventar decisões `OPEN-*`.

## Escopo desta execução

### Backend
- Python + Django + Django REST Framework.
- PostgreSQL com PostGIS; não usar SQLite como substituto de integração.
- Redis + Celery preparados, sem criar jobs de negócio prematuramente.
- Configuração por ambiente e `.env.example` sem segredos.
- API versionada em `/api/v1`.
- endpoint de health/readiness.
- request/correlation ID.
- formato estável de erros.
- OpenAPI.
- pytest, lint e formatação.
- Docker Compose para desenvolvimento.
- criar módulos vazios apenas quando necessários; preferir monólito modular.

### Frontend
- Angular + PrimeNG.
- shell responsivo inicial inspirado na referência visual aprovada da InstrutorProcnh, sem copiar código proprietário externo.
- rotas públicas mínimas e página placeholder.
- cliente HTTP preparado para `/api/v1`.
- tratamento global de erro/loading.
- acessibilidade base.

### Dados territoriais
Criar catálogo territorial nacional desde o início:
- Brasil;
- 27 UFs;
- marcar `RS`, `SC`, `SP`, `RJ` e `ES` como `FIRST_WAVE`;
- demais UFs como `NATIONAL_READY`/não ativadas comercialmente.

Não cadastrar profissionais reais, clínicas reais ou dados pessoais nesta seed.

### Auditoria mínima
Criar a infraestrutura inicial de `AuditEvent` conforme a documentação, permitindo ator nulo/sistema. Não registrar segredos, documentos, CPF integral, tokens ou dados clínicos.

## Regras obrigatórias
- Plataforma nacional; primeira onda operacional: RS, SC, SP, RJ e ES.

> Registro histórico: este era o critério comprovado na fundação. A decisão humana de 24/08/2026 ampliou a primeira onda comercial para AM, RO, AC e RR e determinou a futura separação `commercial_status`/`regulatory_status`. A implementação dessa transição exige migration nova; este documento não autoriza editar a migration aplicada nem significa aprovação regulatória.
- Não codificar regra estadual como `if UF == ...`; regras regulatórias serão dados/versionadas.
- Não criar endpoint DETRAN/SENATRAN fictício.
- Não fazer scraping.
- Não armazenar laudo, diagnóstico, prontuário, resultado médico ou psicológico.
- Não implementar `Quero me tornar instrutor`/Academia do Instrutor no MVP.
- Não implementar IA no matching.
- Não criar microserviços.
- Não criar pagamento nesta tarefa.
- Não criar perfis comerciais a partir de registros públicos.

## Preparação para papéis futuros
A fundação deve suportar posteriormente os papéis de pessoa `STUDENT`, `INSTRUCTOR`, `DOCTOR`, `PSYCHOLOGIST` e papéis organizacionais de clínica via `ClinicMembership`. Não implementar os perfis completos nesta tarefa.

Uma conta não deve ser arquitetada com a premissa rígida `STUDENT XOR INSTRUCTOR` como única possibilidade do sistema. Restrições de compatibilidade de papéis serão definidas por política de domínio, preservando clínica como organização.

## Estrutura sugerida
Backend modular, por exemplo:
`core`, `accounts`, `audit`, `territories`, `regulatory`, `providers`, `marketplace`, `bookings`, `payments`, sem preencher módulos futuros com código especulativo.

Frontend organizado por `core`, `shared` e features.

## Critérios de aceite
1. `docker compose up` inicia banco/PostGIS, Redis, backend e frontend em desenvolvimento.
2. migrations aplicam em banco vazio.
3. seed territorial é idempotente e contém 27 UFs.
4. health/readiness responde corretamente.
5. OpenAPI é gerável.
6. testes backend passam.
7. lint/formatação passam.
8. build frontend passa.
9. nenhum segredo no repositório.
10. nenhum dado pessoal real em fixture/seed/teste.
11. README técnico recebe comandos exatos de instalação, execução, migration, seed e testes.
12. `CHECKPOINT.md` é atualizado apenas se todos os critérios forem comprovados.

## Fora do escopo
Cadastro completo, autenticação social, documentos profissionais, clínicas, médicos, psicólogos, mapa, geocoding, demanda, matching, agenda, booking, pagamento, avaliação, notificações reais, integrações oficiais e deploy de produção.

## Entrega do Codex
Ao terminar, informar:
- arquivos principais criados/alterados;
- versões escolhidas e justificativa curta;
- comandos executados;
- resultado dos testes/build;
- migrations criadas;
- riscos/pendências;
- próximo card liberado.

Não fazer push. Commit Conventional Commit somente se o repositório Git estiver disponível e todos os critérios aplicáveis estiverem verdes.
