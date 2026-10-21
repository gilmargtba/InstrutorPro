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

### Preparação do Google Maps na busca web

O Google Maps é opcional e, por padrão, permanece desligado. Antes de ativá-lo,
revisar os termos e a política de privacidade para o carregamento direto do
Google pelo navegador, confirmar as restrições da chave à Maps JavaScript API
e aos domínios HTTPS autorizados, além de definir orçamento/alertas de custo
adequados ao projeto. O orçamento da conta de faturamento não equivale a um
limite automático nem necessariamente se aplica só a este projeto.

Publicar e testar primeiro a política
`Referrer-Policy: strict-origin-when-cross-origin` do gateway no domínio
principal. Então, inserir a chave diretamente no `.env.production` da VPS,
nunca em Git, chat ou histórico de comandos. Configurar
`GOOGLE_MAPS_BROWSER_API_KEY`, `GOOGLE_MAPS_BROWSER_MAP_ID` e somente por último
`GOOGLE_MAPS_BROWSER_ENABLED=true`. Recriar o backend para carregar o ambiente
e conferir `GET /api/v1/map/browser-config/` sem imprimir a chave. Testar o
mapa no domínio real e o fallback em caso de erro; reverter a flag para
`false` se a API Google falhar. Não remover `MAPTILER_API_KEY`: geocodificação,
mapa do cadastro e fallback ainda dependem dela. Android/iOS não usam esta
chave de navegador.

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
