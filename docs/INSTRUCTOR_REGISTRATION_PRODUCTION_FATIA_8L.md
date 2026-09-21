# Fatia 8L — cadastro de instrutor em produção real

- Data da decisão: 21/09/2026
- Escopo: conta e onboarding nacional de instrutor, 27 UFs
- Autorização: decisão expressa do proprietário
- Não inclui: publicação automática, documentos reais, marketplace real, pagamentos ou Pro

## Decisão e separação de capabilities

O cadastro do instrutor deixa de depender de `CONTROLLED_PILOT`. A autorização específica é
`INSTRUCTOR_REGISTRATION_MODE=PRODUCTION`, combinada com:

```text
REAL_ACCOUNT_REGISTRATION=true
REAL_PERSONAL_DATA=true
REAL_INSTRUCTOR_REGISTRATION=true
```

O marcador global pode permanecer `REAL_PRODUCTION_AUTHORIZATION=NOT_GRANTED`. Isso preserva o
fechamento das capabilities não relacionadas e impede que cadastro seja confundido com produção
integral da plataforma.

## Invariantes preservados

- conta criada com lifecycle `ACTIVE`;
- perfil criado com verificação `NOT_STARTED` e publicação `UNPUBLISHED`;
- papel é concedido pelo servidor e o cliente não pode elevar papel;
- Terms Instructor e Privacy vigentes são aceitos na mesma transação da conta;
- documento jurídico publicado é imutável, possui SHA-256 e o aceite guarda `accepted_at` e
  `request_id`;
- verificação e publicação não são aceitas no contrato de edição do titular;
- publicação continua condicionada a verificação, prontidão regulatória da UF e decisão manual;
- `REAL_DOCUMENT_UPLOADS`, `REAL_AUTOMATIC_PUBLICATION`, `REAL_PAYMENTS` e `REAL_PRO_BILLING`
  permanecem falsas.

## Onboarding nacional

O formulário permite nome profissional, apresentação, categorias A–E, transmissão, WhatsApp,
preço, duração, veículo, cidade, UF e área pública aproximada. O catálogo rejeita sigla inválida e
cobre as 27 UFs. Ausência de `RegulatoryReadiness` não impede cadastro; impede publicação.

Localização privada e área pública continuam separadas. O instrutor pode buscar bairro/ponto
comercial ou ajustar marcador aproximado, com aviso para nunca indicar residência. Se MapTiler
falhar ou ainda não estiver operacional, cidade e UF são salvas e o ponto permanece nulo e não
autorizado. Logo, `REAL_MARKETPLACE_SEARCH` continua um gate independente.

Foto e documentos reais não são coletados nesta fase. O onboarding informa a pendência; não cria
upload disfarçado nem bloqueia os demais dados. A ativação futura exige storage privado,
antimalware e revisão dos controles já documentados.

## Conta, e-mail e segurança

Login e logout usam sessão segura existente. A recuperação possui solicitação genérica, token do
Django de uso único, confirmação com senha mínima de dez caracteres e auditoria. Cadastro, login e
reset possuem throttles distintos. Em produção, a prontidão técnica exige backend SMTP não-console,
host e remetente configurados; credenciais permanecem exclusivamente no `.env.production`.
Sem essa configuração, o endpoint de solicitação falha fechado com `503` antes de gerar token,
evitando que um link de recuperação seja impresso pelo backend de e-mail de console.

O deploy conserva `DEBUG=false`, TLS/cookies seguros, CSRF/CORS/hosts explícitos, PostgreSQL e Redis
sem portas públicas, secrets fora do Git e allowlist de campos no onboarding. Nenhum endpoint do
titular aceita estados de verificação/publicação.

## LGPD e retenção

`DPO_STATUS=PENDING_CLASSIFICATION` permanece pendência documental e não é convertido em `PASS`.
Ele não é usado como variável de runtime. Canal de privacidade, direitos do titular, My Data,
solicitações, auditoria, Terms e Privacy permanecem ativos.

A retenção de analytics de marketplace continua em 90 dias com `DELETE`. Categorias cujo prazo
jurídico ainda não foi aprovado permanecem explicitamente pendentes; esta fatia não inventa prazo.

## Rollback

1. definir `INSTRUCTOR_REGISTRATION_MODE=DISABLED`;
2. recriar somente backend/frontend da aplicação;
3. não apagar contas já criadas, banco, Redis, volumes, certificados ou evidências jurídicas;
4. manter capabilities não relacionadas inalteradas.

Desabilitar novos cadastros não revoga contas existentes nem altera manualmente verificação ou
publicação.

## Evidência local antes do deploy

- backend completo: `219 passed`;
- cenários dirigidos de cadastro nacional e recuperação: `10 passed`;
- Ruff format/check: `PASS`;
- Django system check: `PASS`;
- `makemigrations --check --dry-run`: nenhuma alteração pendente;
- Angular: `31 SUCCESS`;
- build Angular de produção: `PASS`, com os dois avisos de budget já registrados;
- OpenAPI: geração concluída sem warnings; permanecem 22 fallbacks preexistentes de `APIView`
  fora dos endpoints alterados nesta fatia.

Essas evidências validam o código local. O estado real de SMTP, runtime, deploy e smoke deve ser
confirmado separadamente na VPS antes de declarar a prontidão de produção como `YES`.
