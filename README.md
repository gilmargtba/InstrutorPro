# Marketplace SaaS de Aulas Práticas de Direção

Base documental e técnica para construir uma plataforma que aproxima alunos e instrutores autônomos de direção, formaliza a contratação e cobra comissão. O repositório possui a fundação executável descrita no checkpoint; somente a atividade ali autorizada pode ser iniciada sem reinterpretar o produto.

O sistema realiza **verificação interna para publicação**. Não credencia instrutor perante órgão público, não homologa aula, não garante validade oficial e não substitui Detran ou Senatran.

## Estado e termos de entrega

- **Primeiro ciclo de implementação:** fundação cadastral, documental, de autorização, auditoria e elegibilidade; não é o MVP completo.
- **MVP funcional:** jornada transacional completa, de descoberta a avaliação, descrita em `docs/SCOPE.md`.
- **Piloto:** operação limitada do MVP em uma região, com entrada e saída definidas em `docs/PILOT.md`.
- **Versão operacional inicial (VOI):** produto endurecido para operação contínua após o gate do piloto.
- **Evolução posterior:** SaaS do instrutor, integrações oficiais e expansão, sempre condicionados aos gates.

`docs/SCOPE.md` é a fonte oficial desses limites. `docs/CHECKPOINT.md` informa o ponto atual.

## Hierarquia documental oficial

A hierarquia é de refinamento, não uma licença para documentos inferiores ampliarem decisões superiores:

```text
VISION
  └─ SCOPE
      ├─ BUSINESS_MODEL
      ├─ DOMAIN
      │   ├─ AUTHORIZATION
      │   └─ API
      └─ ARCHITECTURE
          ├─ INTEGRATIONS
          ├─ SECURITY ─ LGPD
          ├─ TEST_STRATEGY
          └─ DEVOPS

SCOPE + DECISIONS + RISKS
  └─ ROADMAP
      └─ IMPLEMENTATION_PLAN
          └─ BACKLOG
              └─ CHECKPOINT

PILOT refina a fase piloto; AGENTS e PROMPT governam a execução.
```

Regras de precedência:

1. `VISION.md` define propósito, mas não inclui funcionalidade.
2. `SCOPE.md` é a autoridade sobre inclusão, adiamento e exclusão.
3. `DECISIONS.md` registra decisões aceitas e questões abertas; decisão aberta não pode ser tratada como regra aprovada.
4. `DOMAIN.md` é a autoridade sobre conceitos, invariantes e estados; `API.md` apenas os expõe.
5. `AUTHORIZATION.md`, `SECURITY.md` e `LGPD.md` podem restringir uma operação, nunca ampliá-la.
6. `ROADMAP.md` organiza capacidades; `IMPLEMENTATION_PLAN.md` ordena dependências; `BACKLOG.md` decompõe trabalho; `CHECKPOINT.md` escolhe a próxima tarefa.
7. Em conflito não resolvido, prevalece a alternativa mais restritiva e a implementação para no gate correspondente. A divergência deve ser registrada em `DECISIONS.md`.
8. `GLOSSARY.md`, `REFERENCES.md`, imagens e este README apoiam navegação; não criam regra de negócio.

Não há referência normativa de volta de um documento-fonte para seu refinamento. Referências cruzadas laterais devem apontar a fonte oficial, evitando ciclos.

## Matriz de responsabilidade e dependências

| Documento                | Responsabilidade oficial                                                  | Depende de                                |
| ------------------------ | ------------------------------------------------------------------------- | ----------------------------------------- |
| `VISION.md`              | problema, propósito, direção e princípios                                 | pesquisa e contexto regulatório           |
| `SCOPE.md`               | fronteiras de primeiro ciclo, MVP, piloto, VOI, futuro e fora de escopo   | visão e decisões aceitas                  |
| `BUSINESS_MODEL.md`      | atores econômicos, fluxo comercial, receita e responsabilidades propostas | escopo, jurídico/contábil                 |
| `DOMAIN.md`              | entidades, relações, estados, transições e invariantes                    | escopo e modelo de negócio                |
| `ARCHITECTURE.md`        | componentes, dependências, dados e topologia técnica                      | domínio e atributos de qualidade          |
| `AUTHORIZATION.md`       | papéis, políticas e segregação de funções                                 | domínio, segurança e LGPD                 |
| `API.md`                 | contratos HTTP, erros, concorrência e idempotência                        | domínio e autorização                     |
| `INTEGRATIONS.md`        | contratos externos, seleção, falhas e reconciliação                       | arquitetura, API e decisões de fornecedor |
| `SECURITY.md`            | ameaças, controles, incidentes e gates de segurança                       | arquitetura, autorização e LGPD           |
| `LGPD.md`                | governança, inventário, bases, agentes, direitos e controles de privacidade | domínio, segurança e parecer jurídico    |
| `TEST_STRATEGY.md`       | níveis, cenários, dados e gates de qualidade                              | critérios de domínio, API e fases         |
| `DEVOPS.md`              | ambientes, automação, deploy, observabilidade e continuidade              | arquitetura, segurança e SLOs aprovados   |
| `ROADMAP.md`             | fases macro, resultados e gates                                           | escopo, riscos e decisões                 |
| `IMPLEMENTATION_PLAN.md` | sequência técnica de construção e critérios por fase                      | roadmap e dependências técnicas           |
| `BACKLOG.md`             | tarefas pequenas, priorizadas e verificáveis                              | plano de implementação                    |
| `CHECKPOINT.md`          | estado, trabalho atual, próximo passo, bloqueios e atualização requerida  | backlog e evidência da execução           |
| `DECISIONS.md`           | ADRs, contradições resolvidas e questões abertas                          | todos os documentos afetados              |
| `RISKS.md`               | registro de riscos, sinais, responsáveis e respostas                      | negócio, técnica, jurídico e operação     |
| `PILOT.md`               | população, operação e critérios de entrada/saída do piloto                | escopo, roadmap e riscos                  |
| `M1_PREPRODUCTION_READINESS.md` | decisão objetiva de prontidão do recorte Porto Alegre/RS           | GOV-002/003, LGPD, segurança e produção   |
| `AGENTS.md`              | regras inegociáveis e método dos agentes                                  | governança do repositório                 |
| `PROMPT.md`              | instrução de retomada orientada pelo checkpoint                           | manifest, agentes, plano e checkpoint     |
| `GLOSSARY.md`            | vocabulário comum                                                         | fontes normativas                         |
| `REFERENCES.md`          | fontes externas oficiais e data de validação                              | pesquisa verificável                      |
| `MANIFEST.json`          | inventário e classificação dos artefatos                                  | árvore versionada                         |

## Fluxo consolidado do MVP

```text
instrutor internamente elegível e publicado
→ aluno encontra uma oferta
→ proposta e contraproposta versionadas
→ aceite cria reserva temporária
→ gateway confirma pagamento
→ reserva é confirmada
→ participantes registram execução/conclusão ou ocorrência
→ plataforma registra comissão e repasse no ledger
→ avaliação elegível é publicada
```

Valores, prazos e resultados de cancelamento, no-show, disputa e conclusão dependem das decisões bloqueantes listadas em `docs/DECISIONS.md`.

## Ordem de leitura e retomada

1. `docs/MANIFEST.json` e este README;
2. `docs/VISION.md`, `docs/SCOPE.md` e `docs/BUSINESS_MODEL.md`;
3. `docs/DOMAIN.md`, `docs/AUTHORIZATION.md` e `docs/API.md`;
4. `docs/ARCHITECTURE.md`, `docs/INTEGRATIONS.md`, `docs/SECURITY.md` e `docs/LGPD.md`;
5. `docs/TEST_STRATEGY.md` e `docs/DEVOPS.md`;
6. `docs/DECISIONS.md`, `docs/RISKS.md`, `docs/ROADMAP.md` e `docs/PILOT.md`;
7. `docs/IMPLEMENTATION_PLAN.md`, `docs/BACKLOG.md` e `docs/CHECKPOINT.md`;
8. `AGENTS.md` e `docs/PROMPT.md` antes de executar.

## Regra de início

Resolver `GOV-001` a `GOV-006` do backlog e registrar as respostas antes de criar o projeto Django. Não avançar para marketplace antes do gate de elegibilidade; não avançar para pagamento antes dos pareceres e da política comercial; não avançar ao piloto antes dos gates de segurança, privacidade, restauração e homologação.

## Consolidação 1.2 — 2026-08-19

A visão documental inclui marketplace geográfico de duas pontas: mapa/lista de instrutores, demanda do aluno, matching determinístico, captação de instrutores, candidato/Academia do Instrutor e verificação oficial por adaptadores documentados ou revisão manual. A implementação continua bloqueada pelos gates registrados em `docs/CHECKPOINT.md`.

## Atualização de escopo — 19/08/2026

A InstrutorProCNH está definida como **plataforma nacional da jornada CNH**, preparada para as 27 UFs. A primeira onda técnica/comercial autorizada é **RS, SC, SP, RJ e ES**; AM, RO, AC e RR permanecem na matriz regulatória sem ativação automática. O MVP contempla aluno, instrutor já autorizado/credenciado, clínica, médico e psicólogo, com mapa/lista, demanda/matching para instrutores, verificação e jornada orientativa. “Quero me tornar instrutor”/Academia do Instrutor está fora do MVP. Consulte `docs/GOV_002_NATIONAL.md` e o adendo de `docs/LGPD.md`.


## Atualização v1.5
GOV-002 recebeu baseline federal e matriz regulatória inicial RS/SC/SP/RJ/ES, ampliada para RO/AM/AC/RR, com reforço LGPD para fontes públicas e perfis profissionais.

## Atualização documental v1.6

O modelo de dados do MVP nacional foi consolidado em `docs/DATA_MODEL_MVP.md`. Ele cobre as 27 UFs e os atores do MVP: aluno, instrutor, clínica, médico e psicólogo, além de credenciamento/verificação, mapa, demanda, matching, agenda, referral, Jornada CNH, pagamento e LGPD. A primeira onda técnica/comercial é RS, SC, SP, RJ e ES; Academia do Instrutor continua fora do MVP.

## Atualização documental v1.7

A fundação técnica foi liberada de forma controlada por `docs/CODEX_01_FOUNDATION.md`. O produto é nacional (27 UFs), com primeira onda técnica/comercial em RS, SC, SP, RJ e ES. `docs/MIGRATION_BLUEPRINT_MVP.md` define a ordem proposta de schema sem antecipar gates regulatórios, financeiros ou de privacidade. Academia/“Quero me tornar instrutor” permanece fora do MVP.

## Fundação técnica executável

O CODEX 01 entrega Django 5.2 LTS/DRF, PostgreSQL 17 + PostGIS 3.5, Redis 7.4,
Celery 5.5 e Angular 22 + PrimeNG 22 em um monólito modular. A marca e o conteúdo da
interface continuam provisórios. Não há cadastro, perfil comercial, marketplace ou
integração oficial nesta fundação.

### Pré-requisitos e configuração

- Docker Desktop com Compose;
- ou Python 3.13 e Node.js 22 para validações locais;
- copie `.env.example` para `.env` e troque o segredo local. Nunca versione `.env`.

### Execução com Docker

```powershell
Copy-Item .env.example .env
docker compose up --build -d
docker compose ps
```

Serviços: frontend em `http://localhost:4200`, API em `http://localhost:8000/api/v1`,
documentação OpenAPI em `http://localhost:8000/api/v1/docs/`, health em
`/api/v1/health/` e readiness em `/api/v1/readiness/`.

### Banco, catálogo territorial e schema

```powershell
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py seed_territories
docker compose exec backend python manage.py makemigrations --check --dry-run
docker compose exec backend python manage.py spectacular --file /tmp/openapi.yaml --validate
```

O seed idempotente cria Brasil e as 27 UFs. A migration nova da `PRE-CODEX-02 FOUNDATION` separa `commercial_status` da prontidão regulatória contextual: `RS`, `SC`, `SP`, `RJ` e `ES` ficam `FIRST_WAVE`; as outras 22 UFs ficam `PREPARATION`. Nenhum registro de `RegulatoryReadiness` é criado automaticamente e nenhum status comercial significa aprovação regulatória.

### Testes e qualidade

```powershell
docker compose exec backend pytest
docker compose exec backend ruff format --check .
docker compose exec backend ruff check .
Set-Location frontend
npm ci
npm run build
npm audit --audit-level=high
```

Para encerrar os serviços sem apagar os volumes:

```powershell
docker compose down
```

## Demo visual InstrutorProCNH

`INSTRUTORPROCNH DEMO 01` é uma experiência navegável exclusivamente sintética. Ela não
representa elegibilidade, publicação regulatória, matching definitivo, contratação,
pagamento ou integração oficial.

```powershell
docker compose up --build -d
docker compose restart frontend
```

Abra `http://localhost:4200`. Para executar somente o frontend:

```powershell
Set-Location frontend
npm ci
npm start
```

Fixtures e providers substituíveis ficam em
`frontend/src/app/demo/demo-data.providers.ts`; a demo não usa API nem persistência.

### Mapa online sintético

O mapa usa Leaflet/OpenStreetMap e consulta Django/PostGIS. Execute:

```powershell
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py seed_demo_instructors
```

Pesquise `Porto Alegre`, `Florianópolis`, `São Paulo`, `Rio de Janeiro` ou
`Vitória`. Não há chave nesta demo; o geocoder é local. Provider de produção
permanece pendente.

A busca visual começa por cidade/bairro/CEP informado pelo visitante e abre um mapa amplo com
marcadores, filtros e painel responsivo de resultados. O fluxo não solicita GPS automático, mantém
PostGIS como fonte da consulta e exibe somente profissionais e avaliações sintéticos nesta etapa.

O painel profissional de demanda usa a malha local das 27 UFs fornecida pelo IBGE. Somente os cinco
estados ativos na primeira onda visual (`RS`, `SC`, `SP`, `RJ` e `ES`) recebem destaque e contagens;
as demais UFs aparecem de forma neutra, como territórios em preparação. Todas as contagens e cidades
desse painel continuam exclusivamente sintéticas e não representam demanda real. Ao selecionar uma
UF ativa, a demo abre `/aluno/instrutores` com a capital demonstrativa correspondente e executa a
busca local dos profissionais sintéticos publicados no PostGIS.

### Organização/controlador no painel administrativo

O cadastro M1 reutiliza o Django Admin em `http://localhost:8000/admin/`, menu
**Configurações → Organização / Controlador**. Não há registro real inicial nem endpoint
público. Uma conta `is_staff` precisa receber explicitamente:

- `organizations.manage_platform_organization` para criar/editar;
- `organizations.validate_platform_organization` para executar a ação **Validar
  organização/controlador selecionado**.

Crie a conta local, quando necessário, com `docker compose exec backend python manage.py
createsuperuser`. Depois execute `docker compose exec backend python manage.py
grant_organization_admin SEU_USUARIO`; o comando exige conta `is_staff` ativa, concede
somente as duas permissões e registra auditoria. Superusuário sem atribuição explícita
continua negado por policy. O primeiro salvamento incompleto fica `INCOMPLETE`; com CNPJ, razão social,
endereço, representante, contato operacional e canal de privacidade preenchidos, fica
`PENDING_VALIDATION`. A ação Validar altera para `VALIDATED`; qualquer edição posterior
exige nova validação.

O perfil de produção controlado exige MFA TOTP, rate limiting e permissões explícitas
adicionais. Consulte `docs/ADMIN_PROD_01.md`; isso não converte o workflow profissional
DEMO em publicação real.

### Demo em Ubuntu

O fluxo separado para publicar e atualizar a demo sintética em um servidor Ubuntu
está em `docs/DEPLOY_UBUNTU_DEMO.md`. Use `compose.demo.yaml` e `.env.demo`; o Compose
local acima continua dedicado ao desenvolvimento.
