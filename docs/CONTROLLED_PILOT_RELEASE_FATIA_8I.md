# Fatia 8I — decisão de liberação do controlled pilot

Data da verificação: 20/09/2026. Decisão: `PREDEPLOY_DECISION=NO_GO`.

## Resultado executivo

O gate operacional do piloto foi demonstrado na VPS sem alterar o banco ativo: backup custom do
PostgreSQL, integridade SHA-256, restauração isolada, validação estrutural e remoção do banco
temporário passaram. Assim, `OPEN-009_CONTROLLED_PILOT=PASS`.

O piloto com pessoas reais não foi ativado. `OPEN-004` continua bloqueante antes de usuários
reais; `OPEN-008_CONTROLLED_PILOT=BLOCKED` porque ainda faltam retenções jurídicas completas e
evidência empresarial para classificar o enquadramento do encarregado. A busca real tem ainda o
blocker isolado `MAPTILER=PENDING_VENDOR_REVIEW`. Nenhum desses estados foi convertido em `PASS`
por existir código ou por decisão administrativa.

## Evidência local

- base local e `origin/main`: `38c306504d3c98adba9c5f8e736a858bf53d68e3`;
- backend completo: 192 testes aprovados;
- testes nacionais e de retenção: 30 aprovados;
- Ruff, Django check e `makemigrations --check --dry-run`: aprovados;
- build Angular de produção: aprovado, com o aviso preexistente de budget SCSS.

## Inventário e continuidade na VPS

- commit encontrado na VPS: `5c354dc1184e22dd0c5deb20b9128c618b0c5348`;
- backend, PostgreSQL e Redis saudáveis; frontend, gateway, worker e scheduler ativos;
- PostgreSQL 17.5, PostGIS 3.5.2 e Redis `PONG`;
- gateway é o único serviço expondo portas 80/443; PostgreSQL e Redis não publicam portas;
- disco: 96 GB, 87 GB livres, 11% utilizado;
- migrations existentes exibidas como aplicadas; nenhuma migration foi aplicada nesta execução;
- `.env.production` presente com modo 600 e capabilities reais antigas mantidas `false`;
- `REAL_PRODUCTION_AUTHORIZATION=NOT_GRANTED` permaneceu inalterado.

### Backup e restauração isolada

- caminho: `/home/gilmar/backups/instrutorpro/production/instrutorpro-20260920T234416Z.dump`;
- tamanho: 213586 bytes;
- SHA-256: `11bd3b41efadf54e334a137808593b1f70a70d31b87b7808cf851a2e90a93936`;
- `pg_restore --list`: `PASS`;
- verificação do arquivo `.sha256`: `OK`;
- banco temporário: `instrutorpro_restore_drill_8i_20260920`;
- duração da restauração: 3 segundos;
- validação: 54 tabelas, 59 migrations e PostGIS 3.5.2;
- banco temporário removido; banco de produção não tocado; backup preservado.

## Gates jurídicos e de fornecedores

`DPO_STATUS=PENDING_CLASSIFICATION`. O canal `focusgtba@gmail.com` existe, mas não comprova a
dispensa. Faltam evidências da categoria jurídica/empresarial, receita bruta do exercício anterior
(ou comprovação proporcional aplicável), existência e receita global de grupo econômico e
documentação que sustente a inexistência de hipótese de tratamento de alto risco excludente.

`RETENTION_CONTROLLED_PILOT=BLOCKED`: analytics tem descarte definitivo testado em 90 dias, mas
conta/perfil, evidências de aceite, pedidos de privacidade e registros jurídicos ainda não têm
ciclo pós-encerramento integralmente aprovado. `RETENTION_FULL_PRODUCTION=BLOCKED`.

`MAPTILER=PENDING_VENDOR_REVIEW`: o backend atua como proxy para geocoding/tiles. Faltam aprovação
contratual desse uso, plano aplicável, DPA quando aplicável, subprocessadores, retenção,
transferências e evidência da restrição da chave. O blocker é isolado à busca e dependências do
fornecedor; não é atribuído ao cadastro.

## Matriz final

| Capability | Enabled | Evidência/blocker |
| --- | --- | --- |
| `REAL_ACCOUNT_REGISTRATION` | `false` | `OPEN-004` e `OPEN-008`; classificação DPO e retenção pendentes |
| `REAL_PERSONAL_DATA` | `false` | `OPEN-004` e `OPEN-008`; tratamento real não autorizado |
| `REAL_STUDENT_USE` | `false` | depende de conta e dados pessoais reais |
| `REAL_INSTRUCTOR_REGISTRATION` | `false` | código nacional testado, mas conta/dados reais bloqueados |
| `REAL_MARKETPLACE_SEARCH` | `false` | `MAPTILER=PENDING_VENDOR_REVIEW` e dados reais indisponíveis |
| `REAL_WHATSAPP_CONTACT` | `false` | fluxo aprovado, mas depende de perfil real autorizado |
| `REAL_MARKETPLACE_ANALYTICS` | `false` | retenção de 90 dias passou; depende do fluxo real ainda bloqueado |
| `REAL_DOCUMENT_UPLOADS` | `false` | limite permanente do piloto |
| `REAL_AUTOMATIC_PUBLICATION` | `false` | limite permanente; publicação exige gates próprios |
| `REAL_PAYMENTS` | `false` | fora do piloto |
| `REAL_PRO_BILLING` | `false` | fora do piloto |

## Decisão operacional

- `OPEN-008_CONTROLLED_PILOT=BLOCKED`;
- `OPEN-009_CONTROLLED_PILOT=PASS`;
- `OPEN-010_CONTROLLED_PILOT=PASS`;
- `PREDEPLOY_DECISION=NO_GO`;
- `REAL_PRODUCTION_AUTHORIZATION=NOT_GRANTED`;
- `READY_FOR_FIRST_REAL_ACCOUNT=NO`;
- `NATIONAL_INSTRUCTOR_REGISTRATION=CODE_READY_NOT_ENABLED`;
- `NATIONAL_MARKETPLACE_SEARCH=BLOCKED_MAPTILER_AND_REAL_DATA`;
- `HTTPS=ACTIVE_ON_GATEWAY_80_443_NO_POST_DEPLOY_SMOKE_REQUIRED`;
- `HEALTH=PASS_EXISTING_STACK`;
- `SECURITY_CHECK=PARTIAL`: banco/cache sem exposição e segredos não exibidos; como houve `NO_GO`,
  não houve smoke pós-deploy nem mudança que permitisse atestar uma nova configuração;
- `MIGRATIONS_APPLIED=NONE`;
- `FULL_PRODUCTION=NOT_AUTHORIZED`.

Por `NO_GO`, a VPS não recebeu `git pull`, migrations, rebuild, reinício ou alteração de flags.
O commit da VPS continua `5c354dc1184e22dd0c5deb20b9128c618b0c5348`.
