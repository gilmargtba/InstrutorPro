# Operação de produção — preparação técnica

Status: **TECHNICAL PREPARATION ONLY — REAL PRODUCTION AUTHORIZATION NOT GRANTED**.

## Ambientes e configuração

Produção usa `APP_ENV=PRODUCTION` e `config.settings.production`. Segredos, banco,
Redis, hosts, origens HTTPS e uma chave MapTiler própria são obrigatórios e externos ao
repositório. O processo falha fechado quando essa configuração crítica está ausente.
Fixtures, cadastros e uploads sintéticos permanecem desligados. PostgreSQL e Redis ficam
somente em rede privada, sem publicação de `5432` ou `6379`.

O gate técnico combina `manage.py check --deploy` e `manage.py production_readiness`.
Um resultado positivo não aprova dados reais, conteúdo jurídico nem operação comercial.

Use `compose.production.yaml` exclusivamente com `.env.production`, criado a partir de
`.env.production.example`. O arquivo real é ignorado pelo Git. A composição preserva os
volumes existentes da VPS para permitir uma transição controlada; ela não deve ser iniciada
antes de backup atual, confirmação do SHA autorizado e validação da configuração.

Depois de inserir os segredos diretamente na VPS, incluindo uma chave MapTiler própria e
restrita de produção, execute `./scripts/validate-production-config.sh`. A validação não
imprime os segredos, não inicia o stack persistente e não concede autorização para dados
reais. Todas as flags de cadastro, publicação e demanda permanecem desligadas.

## Backup e restauração

- executar backup PostgreSQL criptografado em storage segregado, com identidade mínima e
  acesso auditado;
- definir retenção, RPO e RTO por decisão dos responsáveis antes da autorização real;
- verificar integridade de cada backup e testar restauração em ambiente isolado com dados
  sintéticos ou minimizados;
- registrar data, operador, versão, duração, resultado e evidência do teste;
- nunca testar restauração substituindo o banco ativo;
- documentar e ensaiar rollback de aplicação e migration compatível antes do rollout.

Retenção definitiva, destino, responsáveis e periodicidade permanecem pendentes de
aprovação operacional, jurídica e de privacidade.

O procedimento executável e os critérios de evidência do restore pré-deploy do piloto estão em
`CONTROLLED_PILOT_TECHNICAL_FATIA_8G.md`. Enquanto a execução na VPS não for autorizada, o estado é
`READY_FOR_PREDEPLOY_RESTORE_TEST`, nunca autorização para iniciar containers ou usar dados reais.
