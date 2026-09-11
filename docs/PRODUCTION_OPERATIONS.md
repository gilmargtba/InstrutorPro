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
