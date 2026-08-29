# Autenticação e Autorização

## CODEX 02E

Submissão DEMO é permitida somente à conta sintética proprietária. Revisão, verificação,
publicação, suspensão, despublicação e revogação da localização exigem
`discovery.manage_instructor_publication` e conta operacional. O Admin mantém campos
críticos somente leitura e suas ações usam os mesmos serviços transacionais e auditados.

## CODEX 02D

Publicação exige `discovery.manage_instructor_publication` explícita e conta ativa. O serviço usa deny-by-default, lock, motivo e auditoria; não há endpoint administrativo público.

Fonte oficial de papéis e políticas. O sistema aplica deny by default no serviço e no selector; esconder controles no frontend não é autorização.

## Configuração da organização/controlador M1

O Django Admin reutilizado expõe a configuração singleton somente a conta operacional e
`is_staff` com permissão explícita `organizations.manage_platform_organization`. A ação
separada **Validar organização/controlador** exige
`organizations.validate_platform_organization`. Superusuário sem atribuição explícita
dessas permissões também falha fechado. Não existe exclusão pelo Admin nem endpoint
público de escrita/leitura administrativa.

Criação, edição e validação passam por serviços transacionais, lock e versão. A auditoria
preserva ator, ação, campos alterados e estados anterior/posterior; CNPJ é mascarado e
endereço, representante, telefones, contatos e DPO são redigidos no metadata. Editar uma
organização validada retorna o registro a `PENDING_VALIDATION` ou `INCOMPLETE`.

## Separação

- autenticação: quem é a conta;
- identidade civil: quem é a pessoa;
- papel: em qual capacidade atua;
- elegibilidade: pode operar agora;
- autorização: pode executar esta ação neste objeto.

Uma conta com papel profissional não está automaticamente apta ou publicada. `STUDENT`, `INSTRUCTOR`, `DOCTOR` e `PSYCHOLOGIST` podem coexistir quando a policy de compatibilidade permitir. Cada papel tem perfil, requisitos, credenciais, verificação, publicação e autorização independentes; possuir um papel nunca concede capacidade de outro. `CLINIC` é organização e o acesso administrativo futuro depende de `ClinicMembership`. Papéis internos continuam sujeitos à segregação e menor privilégio.

No `CODEX 02A`, `RoleAssignment` continua somente classificação de negócio. Concessão/revogação exige a permissão explícita `people.manage_role_assignments`; sem ela, a policy nega. Essa permissão autoriza o comando interno, mas não cria elegibilidade, verificação, publicação ou autorização operacional do papel concedido. `ClinicMembership` permanece separado e seus endpoints/policies operacionais continuam diferidos.

### Policy interna do CODEX 02A

- deny by default para ator ausente, inativo ou sem permissão explícita;
- serviço exige ator, contexto e motivo, sem confiar em valor enviado por frontend;
- `STUDENT`, `INSTRUCTOR`, `DOCTOR` e `PSYCHOLOGIST` não herdam capacidades entre si;
- `CLINIC` não é aceito pelo serviço de papéis pessoais;
- `ADMIN`/superusuário não transforma a pessoa-alvo em profissional verificado ou publicado;
- não há endpoint público de grant/revoke.

### Policy interna do CODEX 02B

- somente `Account.lifecycle_status=ACTIVE` junto de `is_active=True` pode operar;
- gestão exige `accounts.manage_account_lifecycle` atribuída explicitamente ao usuário/grupo; superusuário sem atribuição também é negado;
- `activate_account`, `block_account` e `deactivate_account` exigem ator operacional, contexto, motivo e versão esperada;
- `BLOCKED` pode ser reativada somente pelo comando explícito e autorizado;
- `DEACTIVATED` não pode ser reativada nesta fatia;
- bloquear/desativar não revoga papéis; revogar papel não bloqueia/desativa conta;
- nenhum papel pessoal concede administração do ciclo de vida;
- não há endpoint público de lifecycle.

## Papéis

```text
STUDENT
INSTRUCTOR
DOCTOR
PSYCHOLOGIST
SUPPORT_AGENT
DOCUMENT_REVIEWER
FINANCE_OPERATOR
COMPLIANCE_MANAGER
ADMINISTRATOR
AUDITOR
```

## Estratégia

- RBAC para papéis;
- ABAC para contexto;
- autorização por objeto;
- políticas de elegibilidade;
- segregação de funções.

```text
can_publish_instructor =
  account.active
  AND email.verified
  AND phone.verified
  AND application.approved
  AND documents.valid
  AND vehicle.valid
  AND instructor.operational
```

```text
can_accept_paid_booking =
  can_publish_instructor
  AND payment_recipient.enabled
  AND financial_party.provisioned
  AND required_ledger_accounts.active
```

Publicação expressa aptidão cadastral e operacional. Habilitação para reserva paga acrescenta capacidade financeira; nenhum dos dois estados deve ser persistido como uma flag definida pelo cliente.

## Sessões

Para web: sessão Django, cookie HttpOnly/Secure, CSRF, rotação, revogação e expiração.

Para app futuro: OAuth 2.0/OIDC, access token curto e refresh rotativo.

## Identidade externa — Google

O modelo deve aceitar `ExternalIdentity` desde a fundação, mas o login Google não integra o início do MVP. Sua implementação somente pode começar depois que cadastro de conta, verificação de contatos, pessoa, perfis, aplicação de instrutor, documentos, veículo, revisão e elegibilidade estiverem concluídos e testados.

Quando ativado:

- usar OpenID Connect no backend e encerrar o fluxo com sessão Django;
- identificar a conta Google pela combinação de provedor e claim imutável `sub`;
- validar assinatura, emissor, audiência, expiração, `state` e `nonce`;
- não tratar coincidência de e-mail como autorização suficiente para vincular contas;
- exigir reautenticação para vincular ou desvincular uma identidade;
- auditar criação, uso, falha sensível e remoção do vínculo;
- manter telefone e demais verificações exigidas pelo domínio;
- não conceder papel, elegibilidade ou publicação a partir de claims do Google;
- não armazenar tokens do Google quando não houver necessidade de acessar APIs Google.

## MFA

Obrigatório para administração, revisão sensível, financeiro, mudança bancária, desbloqueio e exportações abrangentes.

Método, recuperação, frequência de reautenticação e sessão privilegiada são decisões de segurança configuráveis. Nenhum administrador contorna MFA por edição de banco em operação normal; acesso emergencial tem credencial individual, prazo, motivo, alerta e revisão posterior.

## Matriz de capacidades

`Próprio` exige vínculo por objeto; `escopo` limita organização/região/fila atribuída; `exceção` exige permissão específica, MFA e motivo. `ADMINISTRATOR` não recebe automaticamente capacidades de auditor independente ou financeiro.

| Capacidade                             |                  Student |               Instructor |                 Support |          Reviewer |                 Finance |            Compliance |                      Admin |                      Auditor |
| -------------------------------------- | -----------------------: | -----------------------: | ----------------------: | ----------------: | ----------------------: | --------------------: | -------------------------: | ---------------------------: |
| ler/editar perfil próprio              |                  próprio |                  próprio |                     não |               não |                     não |                   não |                    exceção |    leitura auditada limitada |
| criar solicitação                      |                  próprio |                      não |       exceção assistida |               não |                     não |                   não |                    exceção |                          não |
| contrapropor/aceitar como participante |                  próprio |                  próprio |       exceção assistida |               não |                     não |                   não |                    exceção |                          não |
| ler própria reserva                    |                  próprio |                  próprio |         escopo + motivo |               não |       financeiro mínimo |        caso atribuído |                    exceção |           leitura autorizada |
| enviar/substituir documento            |                      não |                  próprio | assistência sem decidir |               não |                     não |                   não |                    exceção |                          não |
| visualizar documento completo          |                      não |       próprio necessário |          não por padrão |    fila atribuída |                     não |        caso atribuído |                    exceção |         metadados por padrão |
| verificar/rejeitar documento           |                      não |                      não |                     não |    fila atribuída |                     não |     conforme política |          exceção segregada |                          não |
| decidir aplicação/suspensão            |                      não |                      não |                     não | conforme política |                     não |     conforme política |          exceção segregada |                          não |
| alterar recebedor                      |                      não |            próprio + MFA |                     não |               não |     revisão excepcional |                   não |                    exceção |                          não |
| criar reembolso/ajuste                 |        solicitar próprio |        consultar próprio |   registrar solicitação |               não |         permissão + MFA |                   não |          exceção segregada |                          não |
| resolver disputa                       |  parte fornece evidência |  parte fornece evidência |          caso atribuído |               não | executa efeito aprovado |      regra/compliance |                    exceção |                      leitura |
| moderar denúncia/avaliação             |                denunciar |                denunciar |                  escopo |               não |                     não |                escopo |                    exceção |                      leitura |
| exportar dados pessoais                |        próprio via fluxo |        próprio via fluxo |                     não |               não |                     não | função de privacidade |              exceção + MFA |                          não |
| consultar auditoria                    | próprios eventos seguros | próprios eventos seguros |                  escopo |            escopo |       escopo financeiro |                escopo |                    exceção | escopo amplo somente leitura |
| gerir papéis internos                  |                      não |                      não |                     não |               não |                     não |                   não | permissão específica + MFA |                          não |

## Regras por objeto

- uma conta pode atuar em múltiplos papéis pessoais compatíveis, sempre selecionando o papel/contexto da ação;
- policy, selector e serviço verificam o perfil/capacidade exatos; não existe autorização transitiva entre papéis;
- aluno acessa somente suas reservas;
- instrutor acessa reservas vinculadas;
- suporte registra motivo;
- documentos por necessidade;
- financeiro segregado;
- exportações com permissão específica.

- proposta só pode ser aceita pelo destinatário da versão atual;
- reserva só é lida pelas partes ou por função interna com necessidade registrada;
- reviewer não decide objeto próprio, relacionado ou previamente alterado fora do fluxo;
- claim de fila não concede decisão após mudança da aplicação, evidência ou regra; versão stale é negada;
- `DOCUMENT_REVIEWER` decide apenas requisitos e aplicações dentro do escopo atribuído; suspensão, contestação ou exceção exige a capacidade específica definida em `GOV_003_REVIEW_POLICY.md`;
- suporte não altera preço, comissão, ledger ou evidência; aciona serviços autorizados;
- documento completo é acesso just-in-time, com finalidade, prazo e auditoria;
- filtro/selector aplica o mesmo escopo da policy para impedir enumeração por listagem;
- contas bloqueadas perdem sessões e não executam mutações, salvo fluxos explícitos de recuperação/direitos.

## Ciclo dos papéis

- papel pessoal é concedido transacionalmente após identidade/termos mínimos e validação de compatibilidade;
- repetição idempotente da mesma concessão é aceita; combinação incompatível retorna erro estável sem afetar papéis existentes;
- adicionar ou remover papel não converte nem apaga outro perfil; revogação e efeitos são escopados ao papel;
- desativação/anonymização não concede reutilização automática da identidade para outro papel;
- papel interno exige concedente autorizado, início, expiração opcional, revogação e auditoria;
- privilégios temporários expiram automaticamente e são revisados periodicamente;
- conta de sistema não recebe papel humano nem sessão interativa.

## Decisão de policy

Policies recebem ator, objeto, ação e contexto confiável (organização, MFA recente, request ID, finalidade e estado). Retornam permitido/negado e código de motivo seguro. O domínio continua validando invariantes mesmo após autorização; autorização não torna uma transição inválida válida.

## Autorização financeira

- aluno lê somente seu extrato financeiro;
- instrutor lê somente seu extrato, recebedor e transferências;
- operador financeiro não aprova documentos de instrutor;
- conta financeira da plataforma é independente das contas dos usuários;
- ajustes exigem permissão específica, MFA, motivo e lançamento compensatório;
- lançamentos confirmados são imutáveis e não podem ser apagados;
- saldo financeiro é calculado pelos lançamentos, nunca informado pelo frontend.

Operações financeiras usam permissões separadas para solicitar, aprovar quando exigido e executar. Limites monetários e dupla aprovação são definidos em `OPEN-003/005`; até lá, não se presume que um único papel possa concluir ajuste excepcional.

## Privacidade e suporte

Atendimento usa visão minimizada por padrão. Elevação para dado protegido exige caso, finalidade e auditoria. Direitos do titular são autenticados proporcionalmente ao risco; a pessoa que solicita exportação ou correção não ganha acesso a evidência de terceiros.

## Gov.br futuro

Somente fluxo oficial e homologado. Nunca armazenar senha, OTP, token ou sessão do cidadão.
