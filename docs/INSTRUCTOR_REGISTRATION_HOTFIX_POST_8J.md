# Correção pós-8J — cadastro real de instrutor

Data: 20–21/09/2026 (America/Sao_Paulo).

## Diagnóstico

- a rota pública `/cadastro/instrutor` respondia HTTP 200;
- `POST /api/v1/marketplace/accounts/register/` respondia HTTP 403 antes de persistir a
  requisição diagnóstica `example.invalid`;
- causa do 403: `REAL_PRODUCTION_AUTHORIZATION=NOT_GRANTED` e as capabilities
  `REAL_ACCOUNT_REGISTRATION`, `REAL_PERSONAL_DATA` e `REAL_INSTRUCTOR_REGISTRATION` falsas;
- o link da Home existia, mas a navegação superior escondia “Sou instrutor” em produção;
- após o cadastro, o frontend não abria onboarding real; a implementação anterior apontava para
  “Meus dados”, enquanto a única rota completa de onboarding era restrita a DEV/TEST;
- a tela de status em produção ainda consultava um endpoint `/demo/` inexistente.

`ROOT_CAUSE_INSTRUCTOR_REGISTRATION=CAPABILITIES_NOT_GRANTED_AND_REAL_ONBOARDING_NOT_ROUTED`

## Correção

- a navegação pública de produção aponta “Sou instrutor” para `/cadastro/instrutor`;
- cadastro bem-sucedido de instrutor segue para `/profissional/instrutor/onboarding`;
- o onboarding real salva somente apresentação, categoria, transmissão, WhatsApp profissional,
  oferta, veículo e área pública aproximada de atendimento pelo endpoint autenticado
  `PATCH /api/v1/account/me/`;
- a interface informa explicitamente que não se deve usar residência como centro público;
- não há upload documental no fluxo;
- a tela de status usa `/api/v1/account/me/` e informa que o cadastro não é publicado
  automaticamente;
- o exemplo de produção registra a decisão autorizada:
  `CONTROLLED_PILOT` com conta, dados pessoais e cadastro de instrutor habilitados.
- o validador de produção reporta o marcador de autorização efetivamente carregado do arquivo,
  evitando registrar `NOT_GRANTED` de forma fixa após a ativação controlada.

## Invariantes preservadas

- conta, pessoa, papel e aceite jurídico continuam numa única transação;
- Termos do Instrutor e Política vigentes continuam obrigatórios, versionados e auditáveis;
- todo instrutor nasce `verification_status=NOT_STARTED` e
  `publication_status=UNPUBLISHED`;
- cadastro aceita qualquer uma das 27 UFs válidas no onboarding;
- ausência de `RegulatoryReadiness` não bloqueia cadastro, mas impede publicação;
- `REAL_MARKETPLACE_SEARCH`, `REAL_WHATSAPP_CONTACT`, `REAL_MARKETPLACE_ANALYTICS`,
  `REAL_DOCUMENT_UPLOADS`, `REAL_AUTOMATIC_PUBLICATION`, `REAL_PAYMENTS` e
  `REAL_PRO_BILLING` permanecem falsas;
- MapTiler não participa da criação de conta; no onboarding, recebe somente cidade/UF para resolver
  um centro público aproximado, sem endereço residencial e sem bloquear a conta já criada.

## Validação local

- reprodução segura em produção antes da correção: rota HTTP 200 e API HTTP 403, sem criação;
- 21 testes focados de piloto: `PASS`;
- suíte backend: 199 testes `PASS`;
- Django check: `PASS`; migration check: sem deriva;
- Ruff check/format: `PASS`;
- Angular production build e testes headless: `PASS` (aviso preexistente de budget do mapa).

## Limite jurídico e operacional

A autorização cobre exclusivamente cadastro de instrutor no piloto controlado. `FULL_PRODUCTION`
continua bloqueada enquanto permanecerem pendentes o enquadramento DPO/pequeno porte, as decisões
jurídicas residuais de retenção e os demais gates documentados. Cadastro não constitui
credenciamento, verificação, elegibilidade, publicação ou homologação de aula.

## Deploy e smoke em produção

- CI dos commits `d976fca` e `b640bfb`: backend e frontend aprovados;
- `VPS_HEAD_BEFORE=2fcfeb435c00b6f43197193b2047d5cfb30f24be`;
- `VPS_HEAD_AFTER=b640bfbd60a263b84679e6557b0d3eee749a93b1`;
- atualização feita por `git pull --ff-only origin main`;
- backup preservado em `.env.production.pre-instructor-hotfix-20260921`;
- somente `backend`, `frontend`, `worker` e `scheduler` foram reconstruídos/recriados;
  PostgreSQL, Redis, gateway, certificados e volumes foram preservados;
- configuração efetiva validada como `CONTROLLED_PILOT`, com conta, dados pessoais e cadastro de
  instrutor habilitados; todas as demais capabilities reais/comerciais permaneceram bloqueadas;
- `/cadastro/instrutor`, Termos do Instrutor e Política de Privacidade responderam HTTP 200;
- logs recentes: `RECENT_ERRORS=NONE`; worktree rastreado limpo;
- nenhum usuário ou identidade fictícia foi criado no smoke.

`FIRST_REAL_INSTRUCTOR_READY=YES`

## Edição segura do perfil já cadastrado

- a tela de status deixou de direcionar o instrutor ao painel legado e agora oferece a ação
  explícita `Editar perfil`, que abre o onboarding real autenticado;
- o formulário de edição hidrata apresentação, categorias, transmissão, WhatsApp profissional,
  oferta, veículo e área pública aproximada já persistidos antes de permitir novo envio;
- campos internos de verificação do veículo não retornam no `PATCH`, preservando o contrato de
  escrita e evitando alteração de estado pelo cliente;
- a edição continua sem publicar ou verificar automaticamente o instrutor e respeita as
  invalidações de segurança existentes para alterações sensíveis.

## Correção adicional de campos opcionais

- a tentativa seguinte revelou dois erros “Este campo não pode estar em branco” para `city` e
  `uf`: o formulário de instrutor enviava esses campos exclusivos do cadastro de aluno como
  strings vazias;
- o frontend agora omite `city` e `uf` no cadastro de instrutor, e o serializer aceita vazio nos
  campos opcionais; para aluno, a validação de domínio continua exigindo ambos;
- mensagens de validação agora incluem o nome seguro do campo, evitando erros duplicados sem
  contexto;
- validação: 28 testes focados e 206 testes backend `PASS`; Ruff, Django e migrations `PASS`;
  Angular production build `PASS` e 23 testes frontend `PASS`.

## Correção de feedback do formulário

- a primeira tentativa real do proprietário retornou HTTP 400 porque senha e confirmação tinham
  menos de 10 caracteres; nenhuma conta foi persistida;
- a resposta padronizada da API identificou os campos `password` e `password_confirmation` com
  comprimento inferior ao mínimo; não houve exceção de backend nem erro de capability;
- o campo visual de data usa `type=date` e envia ISO `AAAA-MM-DD`, contrato aceito pelo
  `DateField`; o formato visual localizado `DD/MM/AAAA` não é enviado como payload;
- o frontend consulta as versões jurídicas vigentes e envia os nomes e tipos esperados pelo
  serializer, incluindo audiência `INSTRUCTOR`, versões de Termos/Política e ambos os aceites;
- a interface agora informa previamente o mínimo de 10 caracteres, impede envio do formulário
  inválido e apresenta os detalhes de validação devolvidos pela API em vez da mensagem genérica;
- reprodução segura com domínio `example.invalid`: HTTP 400 com erro específico de comprimento;
- regressão ampliada cobre cadastro `201`, senha e data inválidas, aceites ausentes, capability
  bloqueada/liberada, e-mail duplicado, falha de persistência do aceite com rollback integral e
  instrutor `NOT_STARTED/UNPUBLISHED`;
- validação final: 27 testes focados e 205 testes backend `PASS`; Ruff, Django check e migration
  check `PASS`; Angular production build `PASS` e 22 testes frontend `PASS`.
- consulta sanitizada na VPS confirmou `ACCOUNT_ALREADY_EXISTS=NO`, seis contagens relacionadas
  zeradas e `SIGNUP_TRANSACTION=ROLLED_BACK`; as quatro capabilities necessárias estavam
  efetivamente carregadas no backend;
- frontend corrigido implantado no commit `c8057be`, sem recriar backend, PostgreSQL, Redis,
  volumes ou certificados; gateway apenas recarregado e `/cadastro/instrutor` respondeu HTTP 200.

`FIRST_REAL_INSTRUCTOR_READY=YES`
