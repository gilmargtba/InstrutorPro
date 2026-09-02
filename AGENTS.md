# AGENTS.md

## Missão

Construir a InstrutorProCNH como plataforma nacional da jornada da CNH, conectando alunos a instrutores e, conforme o fluxo oficial aplicável, clínicas, médicos e psicólogos, com marketplace, verificação, contratação e operação segura.

## Objetivo do primeiro ciclo

Entregar a fundação cadastral, documental, de autorização e auditoria. Não avançar para marketplace antes de concluir elegibilidade.

## Regras inegociáveis

1. Não afirmar que o sistema homologa aula.
2. Não integrar endpoint governamental não documentado.
3. Não usar scraping autenticado em Detran/Senatran.
4. Não pedir senha ou token Gov.br.
5. Não publicar instrutor sem elegibilidade.
6. Não usar apenas `is_instructor`.
7. Não armazenar cartão.
8. Não expor documento em URL pública.
9. Não processar webhook sem assinatura e idempotência.
10. Não implementar regra crítica em view/serializer.
11. Não misturar status financeiro, comercial e oficial.
12. Não criar microserviços no MVP.
13. Não adicionar IA sem caso validado.
14. Não editar migration aplicada; criar nova.
15. Não executar ação destrutiva sem instrução explícita.
16. Não assumir uma regra global simplista de papéis. Compatibilidade entre `STUDENT`, `INSTRUCTOR`, `DOCTOR` e `PSYCHOLOGIST` deve seguir política explícita; clínica é organização e usa `ClinicMembership`.
17. Não tratar pré-análise de candidato como aptidão, certificação ou autorização oficial.
18. Não expor localização individual de aluno em mapa de demanda; usar agregação/minimização.
19. Não usar IA como dependência do matching do MVP; regras iniciais devem ser determinísticas e explicáveis.
20. Não automatizar prospecção/consulta de registro público sem fonte, finalidade e uso aprovados.

## Stack

Python/Django/DRF, PostgreSQL/PostGIS, Celery/Redis, Angular/PrimeNG, Docker, pytest e OpenAPI.

## Organização

Cada módulo pode conter `models`, `domain`, `services`, `selectors`, `policies`, `tasks`, `api` e `tests`, sem criar camadas vazias.

## Fluxo do agente

1. Ler `docs/MANIFEST.json`, `README.md` e `docs/CHECKPOINT.md`.
2. Ler as fontes oficiais relacionadas e o card do `BACKLOG.md`.
3. Executar somente a próxima tarefa liberada e confirmar dependências/gates.
4. Identificar decisão faltante; não inventar valor para destravar código.
5. Planejar pequena fatia vertical.
6. Implementar.
7. Testar.
8. Atualizar apenas as fontes documentais afetadas.
9. Atualizar checkpoint.
10. Revisar escopo, diff, segredos e dados.
11. Criar commit da fatia concluída, quando os critérios abaixo forem atendidos.
12. Parar em estado executável.

`SCOPE.md` define inclusão, `DOMAIN.md` define estados/invariantes, `DECISIONS.md` distingue aceito de aberto e `IMPLEMENTATION_PLAN.md`/`BACKLOG.md`/`CHECKPOINT.md` definem a ordem. Documento inferior não amplia fonte superior.

## Qualidade

Toda entrega considera autorização, concorrência, idempotência, auditoria, privacidade, falha externa, teste, observabilidade e rollback.

## Banco

UUID, constraints, índices, dinheiro em Decimal/menor unidade, UTC, transações, migrations pequenas, dados protegidos e sem signals para orquestração complexa.

## API

`/api/v1`, erros estáveis, request ID, paginação, OpenAPI e idempotência. Nunca confiar no cliente para preço, comissão, papel ou status.

## Segurança

Deny by default, autorização por objeto, storage privado, segredos fora do repo, logs minimizados, MFA sensível, rate limit, CSRF/CORS e quarentena de uploads.

## Testes obrigatórios

Sucesso, autorização negada, estado inválido, concorrência, idempotência, auditoria e falha de integração.

## Commits

Cada implementação deve terminar em um commit quando representar uma fatia vertical coerente, estiver em estado executável e tiver validação proporcional ao risco. Não criar commit para tentativa incompleta, teste quebrado ou alteração ainda em investigação.

Antes do commit:

1. executar os testes, lint e validações aplicáveis à alteração;
2. atualizar documentação e `CHECKPOINT.md` quando o comportamento, contrato ou estado do projeto mudar;
3. revisar o diff e incluir somente arquivos pertencentes à fatia implementada;
4. preservar alterações preexistentes ou não relacionadas feitas pelo usuário;
5. confirmar que nenhum segredo, credencial, dado sensível ou artefato local será versionado.

O commit é obrigatório para código, migration, correção, teste funcional ou mudança documental que conclua uma decisão do projeto. Pode ser adiado quando a fatia depender de outra alteração imediata para ficar executável, mas deve ser criado assim que o conjunto coerente estiver concluído.

Não criar commit vazio, não reescrever histórico, não usar `--amend` sem solicitação explícita e não fazer push automaticamente. Se o repositório ainda não estiver inicializado ou o usuário proibir commits, registrar essa condição na entrega em vez de forçar a operação.

Usar Conventional Commits, com escopo específico e mensagem que descreva o resultado:

```text
feat(accounts): add verified phone flow
feat(verification): add instructor review
fix(bookings): prevent overlapping slots
test(payments): cover duplicated webhook
docs(checkpoint): record milestone completion
```

## Definition of Done

Regra, teste, migration/constraint quando aplicável, permissão, auditoria, privacidade/segurança, observabilidade, rollback, documentação/OpenAPI, CI, checkpoint e commit coerente.

## Primeira entrega

AuditEvent, Account, ContactVerificationChallenge, ExternalIdentity inativa, PlatformOrganization, LegalDocument, LegalAcceptanceRecord e ConsentRecord separados, Person, RoleAssignment, perfis pessoais independentes e cumuláveis somente conforme policy explícita, InstructorApplication, DocumentRequirement, InstructorDocument, Vehicle, OutboxEvent antes de efeito assíncrono crítico, revisão administrativa, elegibilidade e testes. `CLINIC` permanece organização via `ClinicMembership`.

## Fora da primeira entrega

Pagamento, mapas, demanda/matching, app, Gov.br, integrações eletrônicas Senatran/Detran, Datavalid, chat, IA, Academia do Instrutor e microserviços. A modelagem documental dessas capacidades pode existir, mas sua implementação respeita os gates do plano.
