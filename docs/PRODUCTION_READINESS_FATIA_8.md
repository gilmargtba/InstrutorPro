# Fatia 8 — prontidão técnica de produção

## Limite de autorização

Esta fatia prepara e homologa tecnicamente a infraestrutura. Ela **não** autoriza usuários,
cadastros, documentos, publicação, demanda, pagamento ou qualquer outro dado real.

O marcador operacional obrigatório é:

```text
REAL_PRODUCTION_AUTHORIZATION=NOT_GRANTED
```

Todas as flags `REAL_*`, `PUBLIC_DEMAND_MAP_ENABLED` e as capacidades sintéticas permanecem
`false` em `PRODUCTION`. O comando `production_readiness` falha se alguma capacidade real for
habilitada.

## Evidências já obtidas em 16/09/2026

| Gate | Estado | Evidência |
| --- | --- | --- |
| `origin/main` contém a fatia anterior | PASS local | `origin/main` e `HEAD` em `cf98491933c6ed38d724ef21dbda38bbb6f9141a` antes desta fatia |
| DNS raiz | PASS externo | `instrutorprocnh.com.br` resolve para `179.199.136.4` |
| DNS `www` | PASS externo | CNAME para `instrutorprocnh.com.br` |
| HTTPS raiz | PASS externo | HTTP 200 e verificação TLS bem-sucedida |
| Redirecionamento `www` | PASS externo | HTTP 301 para `https://instrutorprocnh.com.br/` |
| Página `/privacidade` | PASS externo | HTTP 200 e verificação TLS bem-sucedida |
| Configuração `.env.production` na VPS | PASS técnico | arquivo em modo `600`, sem placeholders e validação fail-closed aprovada |
| Backup íntegro | PASS técnico | dump custom de 192302 bytes validado por `pg_restore --list`, com SHA-256 registrado |
| Restauração isolada | BLOCKED | ensaio de restauração ainda não executado (`OPEN-009`) |
| MapTiler técnico | PASS condicional | geocoding e tile retornaram 200; chave compartilhada com DEMO por limite do plano |
| MapTiler contratual | BLOCKED | chave dedicada, contrato/DPA, subprocessadores e retenção pendentes (`OPEN-007`) |
| Dados jurídicos da organização | BLOCKED | não serão inventados; comprovação, endereço, representação e DPO pendentes |
| Usuários e dados reais | BLOCKED | `OPEN-004`, `OPEN-008` e `OPEN-009`; autorização não concedida |
| Upload real/antimalware | BLOCKED | armazenamento privado existe, scanner real não foi homologado |
| Pagamentos | N/A | fora desta fatia e bloqueados por `OPEN-005` |

## Resultado do deploy técnico em 17/09/2026

- `TECHNICAL_PRODUCTION_READINESS=PASS`;
- `PRODUCTION_CONFIG_VALIDATION=PASS`;
- migrations pendentes: nenhuma;
- backend, PostgreSQL e Redis saudáveis; frontend, worker, scheduler e gateway ativos;
- raiz HTTPS `200`, `www` `301` para o domínio canônico e validação TLS sem erro;
- `/privacidade`, `/api/v1/readiness/`, geocoding MapTiler e tile MapTiler retornaram `200`;
- a chave MapTiler foi compartilhada conscientemente com DEMO devido ao limite de uma chave ativa
  do plano atual; isso basta para homologação técnica, não fecha `OPEN-007`;
- estado preservado: `REAL_PRODUCTION_AUTHORIZATION=NOT_GRANTED`.

## Inventário seguro na VPS

Depois de atualizar a árvore com `git pull --ff-only`, execute sem mostrar segredos:

```bash
cd /home/gilmar/InstrutorPro
chmod +x scripts/inspect-production-host.sh scripts/backup-production.sh scripts/validate-production-config.sh
./scripts/inspect-production-host.sh
```

O script mostra somente SHA, estado da árvore, permissões, flags não secretas e containers. Ele
não imprime senhas, chaves ou o conteúdo integral do arquivo de ambiente.

## Backup validado

Antes de qualquer `up` de produção:

```bash
cd /home/gilmar/InstrutorPro
PRODUCTION_ENV_FILE=.env.production ./scripts/backup-production.sh
```

O resultado só é aceitável com arquivo não vazio, `pg_restore --list` válido, SHA-256 e
`BACKUP_ARCHIVE_VALID=YES`. O backup fica fora do repositório e com modo `600`.

### Ensaio de restauração isolado

A restauração não deve apontar para o banco ativo. Crie um PostgreSQL/PostGIS temporário,
restaure nele o arquivo `.dump`, execute consultas de contagem e integridade e então remova apenas
o banco temporário. Registre SHA-256, início/fim, versão PostgreSQL/PostGIS, resultado e operador.
Esse ensaio exige autorização operacional separada porque cria e depois remove um banco de teste.

## Homologação técnica controlada

Com `.env.production` em modo `600`, placeholders removidos, chave MapTiler própria de produção e
backup válido:

```bash
cd /home/gilmar/InstrutorPro
PRODUCTION_ENV_FILE=.env.production ./scripts/validate-production-config.sh
docker compose --env-file .env.production -f compose.production.yaml up -d --build
docker compose --env-file .env.production -f compose.production.yaml ps
```

Não use `--remove-orphans`, não remova volumes e não execute seed. A composição reutiliza os
volumes nomeados existentes para preservar banco, Redis, arquivos privados, estáticos e
certificados. A mudança deve ser feita em janela controlada e validada por `readiness`, HTTPS,
privacidade, autenticação, MapTiler e logs.

## Rollback

Se a validação falhar, preserve logs e volumes, retorne ao commit anteriormente registrado com
`git switch --detach <sha-anterior>` e recrie a mesma composição com o arquivo de ambiente
preservado. Restaurar banco é último recurso e somente após confirmar que houve alteração de dados;
use exclusivamente o backup cujo SHA-256 e listagem tenham sido validados.

## Go/no-go

O máximo permitido nesta fatia é `TECHNICAL_PRODUCTION_READINESS=PASS` com
`REAL_PRODUCTION_AUTHORIZATION=NOT_GRANTED`. Qualquer entrada de usuário ou dado real permanece
**NO-GO** até o fechamento formal dos gates jurídicos, privacidade, MapTiler, recuperação e suporte.
