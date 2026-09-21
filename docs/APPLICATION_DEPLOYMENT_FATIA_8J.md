# Fatia 8J — deploy seguro e fundação de pagamentos

Data da execução: 20/09/2026 (America/Sao_Paulo).

## Decisões independentes

- `APPLICATION_DEPLOY_DECISION=GO`
- `REAL_DATA_ACTIVATION_DECISION=NO_GO`
- `APPLICATION_DEPLOYED=YES`
- `REAL_MARKETPLACE_ENABLED=NO`
- `PAYMENT_INFRASTRUCTURE_READY=YES`

O deploy atualizou somente o código da aplicação. Ele não autorizou cadastro, tratamento de dados
reais, marketplace real, cobrança ou entitlement comercial PRO.

## Git, CI e pré-deploy

- `VPS_HEAD_BEFORE=5c354dc1184e22dd0c5deb20b9128c618b0c5348`
- commit funcional: `b8b738213e4d283b016a24cc220255d3cab6adf8`
- commit de infraestrutura do CI: `7e67b892e5194f26f6760f480ba7343eb4a70a34`
- backend e frontend do GitHub Actions: `PASS`
- backend: 198 testes aprovados; Ruff format/check, Django check e migration check aprovados;
- frontend: build Angular aprovado, mantendo apenas o aviso preexistente de budget;
- backup preservado e verificado por SHA-256 antes do pull;
- restore da Fatia 8I não foi repetido sem necessidade: a evidência `OPEN-009=PASS` permanece válida;
- VPS tinha 87 GB livres, PostgreSQL/Redis saudáveis, volumes preservados e worktree limpo.

## Deploy executado

- `git pull --ff-only` levou a VPS ao commit `7e67b892e5194f26f6760f480ba7343eb4a70a34`;
- imagens de backend, frontend, worker e scheduler foram reconstruídas;
- migrations normais aplicadas: `discovery.0005`, `payments.0001`, `privacy.0002` e
  `privacy.0003`;
- somente backend, frontend, worker e scheduler foram recriados;
- PostgreSQL, Redis, gateway, certificados, volumes e `.env.production` foram preservados;
- backend terminou saudável; frontend, worker e scheduler permaneceram ativos;
- logs recentes não apresentaram traceback, erro crítico, falha não tratada ou recusa de conexão;
- `VPS_HEAD_AFTER=7e67b892e5194f26f6760f480ba7343eb4a70a34` e `WORKTREE=CLEAN_YES`.

## Smoke e segurança

- `/`, `/api/v1/health/`, `/api/v1/readiness/`, política vigente e termos de aluno/instrutor:
  HTTP 200 por HTTPS;
- webhook de pagamento sem assinatura: HTTP 401;
- banco e Redis continuam sem portas publicadas; somente o gateway expõe 80/443;
- segredos permaneceram fora do Git e não foram impressos;
- configuração efetiva manteve `REAL_PRODUCTION_AUTHORIZATION=NOT_GRANTED`;
- capabilities de conta, dados pessoais, aluno, instrutor, busca, WhatsApp, analytics,
  documentos, publicação automática, pagamentos e PRO permaneceram `false`;
- `PAYMENT_PROVIDER` permaneceu vazio e `PAYMENT_ENVIRONMENT=sandbox`.

## Próxima ação do gateway

Fechar `OPEN-005`, comparar fornecedores usando `PAYMENT_PROVIDER_REQUIREMENTS.md`, selecionar o
primeiro gateway e implementar seu adaptador concreto. Depois, cadastrar credenciais exclusivas de
sandbox fora do Git e validar checkout/tokenização, assinatura, retries, idempotência, conciliação,
cancelamento e refund. A ativação de `REAL_PAYMENTS` e, posteriormente, `REAL_PRO_BILLING` exige
mudanças separadas e autorização explícita.
