# DevOps, Implantação e Operação

Fonte oficial de ambientes, automação, release, observabilidade e continuidade. Valores de SLO/RPO/RTO permanecem bloqueados em `OPEN-009` até aprovação; o processo para defini-los já é obrigatório.

## Ambientes e promoção

| Ambiente   | Dados/integrações                                         | Finalidade                            | Acesso                        |
| ---------- | --------------------------------------------------------- | ------------------------------------- | ----------------------------- |
| local      | sintéticos, fakes/emuladores                              | desenvolvimento reproduzível          | desenvolvedor                 |
| test/CI    | factories efêmeras, sem rede não controlada               | validação automatizada                | pipeline                      |
| staging    | sintéticos/demo, sandboxes e configuração production-like | integração, UAT, migration e operação | equipe autorizada             |
| production | dados reais mínimos, fornecedores reais                   | piloto/VOI                            | just-in-time, MFA e auditoria |

Contas, redes, buckets, bancos, credenciais e callbacks são segregados. Produção não recebe seed demo; staging não recebe dump real salvo exceção formal, minimizada e protegida.

## Serviços e infraestrutura

Frontend estático/PWA, proxy/WAF, backend web, worker, scheduler, PostgreSQL/PostGIS, Redis, object storage privado, secret manager e telemetria. Infra/configuração são reproduzíveis e revisadas; Redis não é fonte de estado irrecuperável.

Capacidade inicial mede web/worker, conexões do banco, fila, storage, throughput de webhook e integrações. Auto-scaling, se adotado, respeita limites do banco/fornecedor e não substitui teste de carga.

## CI

Dívida técnica registrada em 24/08/2026: adicionar Chrome/Chromium Headless ao ambiente de teste frontend ou adotar runner equivalente; executar `npm test -- --browsers=ChromeHeadless` na CI; e limpar com segurança builds/caches locais antigos (`dist/embrea`, `test-out`, schedules/caches ignorados) sem alterar migration histórica. O build Angular permanece obrigatório e aprovado; teste compilado sem execução por ausência do browser não equivale a suíte aprovada.

1. validar manifest/Markdown/JSON e ausência de segredo;
2. instalar por lockfile e verificar dependências/licenças/vulnerabilidades;
3. format/lint/type check adotado;
4. unit/service/API/frontend com PostgreSQL/PostGIS;
5. migration drift/check e OpenAPI compatível;
6. build frontend/backend e scan de imagem;
7. artefato imutável identificado pelo commit;
8. relatórios/evidências preservados.

Branch/review policy é ativada quando remoto existir. Exceção de scan tem severidade, justificativa, owner e expiração.

## CD e release

```text
commit aprovado → artefato imutável → staging
→ migration expand/compatible → smoke/UAT/gates
→ aprovação → produção limitada → smoke/monitorar → ampliar
```

- backup/check antes de migration sensível;
- preferir expand/migrate/contract em releases separados;
- app mantém compatibilidade durante rollout;
- migration longa tem estimativa, lock/timeout e plano de interrupção;
- rollback de app e roll-forward de schema são definidos; migration destrutiva não é revertida cegamente;
- feature flag tem owner, default seguro, data de remoção e não contorna autorização;
- release note inclui commit, migrations, flags, risco, observação e rollback;
- mudança financeira/privacidade crítica requer aprovadores correspondentes.

## Health, logs e telemetria

- liveness prova processo; readiness prova dependências estritamente necessárias sem causar carga;
- logs estruturados: tempo, nível, serviço, ambiente, operação, request ID, ator/alvo opacos permitidos, duração/status;
- métricas: golden signals, pool/banco, cache, fila/worker, upload/scan, auth, eligibility, busca, holds, pagamento/webhook, ledger/conciliação e funil;
- traces seletivos sem payload pessoal, sampling configurável e correlação;
- dashboards por jornada e serviço; labels sem PII/alta cardinalidade.

SLIs/SLOs e error budgets são aprovados antes do piloto: disponibilidade das jornadas, latência, erro, atraso de fila/webhook, retirada de elegibilidade, divergência financeira, RPO/RTO e tempo de resposta operacional.

## Alertas

Cada alerta tem sintoma acionável, severidade, owner/on-call, canal, deduplicação, runbook e teste. Cobrir indisponibilidade, erro/latência, banco/pool, fila parada/idade, task falha, webhook acumulado/assinatura, divergência financeira, storage/scan, backup/restore, segurança/acesso e esgotamento de capacidade. Métrica de negócio sem ação imediata vai para dashboard, não pager.

## Backup e recuperação

Escopo: PostgreSQL, object storage/versionamento, configuração/IaC e metadados necessários; segredos são recuperáveis pelo gestor, não copiados em arquivo comum.

- criptografia, acesso mínimo, região/cópia conforme risco e retenção aprovada;
- backup automatizado monitorado e teste de integridade;
- restore em ambiente isolado, com validação de banco↔storage↔ledger;
- pedidos de eliminação/retenção são reaplicados após restore antes de reabrir uso;
- RPO/RTO definidos por impacto e medidos no ensaio;
- evidência registra início/fim, ponto recuperado, perda, falhas e owner;
- DR completo antes do piloto e na cadência aprovada na VOI.

## Runbooks mínimos

Gateway indisponível/efeito desconhecido, webhook backlog/assinatura, divergência do ledger, mensagens/OTP, mapa, scanner, storage, banco, Redis/fila/workers, perda de elegibilidade atrasada, deploy/migration falha, vazamento/conta tomada, backup/restore e fornecedor comprometido. Cada runbook contém detecção, impacto, passos seguros, autorização, comunicação, rollback/contingência, preservação de evidência e encerramento.

## Operação diária e periódica

| Cadência           | Atividades                                                          |
| ------------------ | ------------------------------------------------------------------- |
| contínua           | alertas, filas, disponibilidade e segurança                         |
| diária no piloto   | conciliação, falhas de tarefa/webhook, backup e casos críticos      |
| semanal            | métricas do piloto, custos, suporte, vulnerabilidades e capacidade  |
| por release        | gates, migration, smoke, observação e nota                          |
| periódica aprovada | access review, rotação, patching, restore/DR, fornecedor e retenção |

Frequências finais e owners são definidos em `OPEN-009`; ausência bloqueia piloto.

## Rollback e mudança

Falha funcional usa flag/rollback de app quando schema compatível. Dado incorreto usa serviço/migration corretiva auditável; não apagar ou editar produção manualmente. Efeito externo/financeiro usa reconciliação e operação compensatória, nunca “rollback” local que contradiga o gateway. Toda intervenção excepcional tem ticket/caso, ator, comando seguro, evidência e revisão.

## Prontidão para piloto/produção

Infra reproduzível; segredos/fornecedores production-ready; capacidade medida; SLO/on-call e limites definidos; observabilidade/alertas/runbooks testados; backup restaurado dentro de RPO/RTO; rollback ensaiado; domínio/DNS/TLS e contatos operacionais válidos; segurança/LGPD/jurídico/finanças aprovados; suporte treinado; release candidate homologado.
