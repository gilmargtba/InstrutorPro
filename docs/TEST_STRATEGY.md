# Estratégia de Testes

Fonte oficial dos níveis, cenários e gates. Critérios de negócio vêm de `DOMAIN.md`/`SCOPE.md`; cada tarefa detalha seus testes em `BACKLOG.md`.

## Pirâmide e ambientes

| Nível                          | Objetivo                                                      | Execução                              |
| ------------------------------ | ------------------------------------------------------------- | ------------------------------------- |
| domínio/unitário               | estados, cálculo, policy e invariantes rápidos                | a cada mudança                        |
| serviço + banco                | transação, constraint, lock, idempotência e auditoria         | CI com PostgreSQL/PostGIS real        |
| API/contrato                   | autenticação, schema, erro, autorização e compatibilidade     | CI; OpenAPI validado                  |
| adaptador/contrato externo     | tradução, timeout, retry, assinatura e erro                   | fake fiel + sandbox quando disponível |
| frontend component/integration | formulário, estado, autorização visual, erro e acessibilidade | CI por capacidade                     |
| E2E                            | jornadas críticas multiator                                   | gates M2, M5, M6 e release            |
| não funcional                  | carga, segurança, a11y, restore, rollback e operação          | antes do piloto e mudanças críticas   |

Teste não depende de ordem, horário real instável ou rede pública não controlada. Relógio/UUID/provedor são injetáveis. Banco SQLite não substitui PostgreSQL em integração.

## Cenários transversais obrigatórios

Para cada mutação aplicável: sucesso, não autenticado, sem papel, objeto alheio, estado inválido, input/mass assignment, repetição/idempotência, concorrência, auditoria, falha externa, observabilidade e rollback transacional.

### Identidade e autorização

- antienumeração, rate limit, sessão/CSRF/rotação/revogação e bloqueio;
- OTP hash/expiração/tentativas/consumo/replay;
- MFA, recovery e ação privilegiada sem step-up;
- papéis pessoais compatíveis podem coexistir; combinações negadas por policy falham atomicamente, e nenhum papel herda permissão, verificação, publicação ou perfil de outro;
- selector/lista e policy/detail têm o mesmo escopo;
- suporte/revisor/financeiro/admin não acumulam capacidade implícita;
- Google futuro: state/nonce/issuer/audience/sub, e-mail coincidente e último método.

### Credenciamento e documentos

- aplicação/transições/versionamento/uma ativa;
- requisito por jurisdição/categoria/vigência;
- MIME falso, polyglot quando relevante, tamanho/quota, malware, scanner/storage indisponível;
- URL curta expirada, IDOR, download/preview e retenção/substituição;
- self-review, stale decision, motivo/MFA/auditoria;
- dois revisores concorrentes, claim expirado, conflito de policy/version e repetição idempotente da mesma decisão;
- fonte oficial indisponível não vira rejeição automática; nova publicação permanece bloqueada sem tolerância aprovada;
- pendência, rejeição, suspensão e contestação preservam a decisão anterior e expõem somente motivo seguro;
- documento/veículo/contato expirado, suspensão/reativação e task perdida;
- perda de elegibilidade remove publicação dentro do SLO.

### Marketplace, agenda e reserva

- perfil público minimizado e inelegível ausente;
- precisão/consulta PostGIS, filtros, cursor e paginação concorrente;
- timezone/DST, exceção, horário passado, duração/buffer e geração de slots;
- proposta imutável, cálculo do servidor, policy/version e expiração;
- dois aceites simultâneos para instrutor/veículo/slot: apenas um hold;
- retry do aceite não cria booking; expiração/cancelamento libera uma vez;
- pagamento após hold expirado entra em tratamento/reconciliação definido, não confirma silenciosamente.

### Pagamento e ledger

- assinatura inválida/rotacionada, corpo alterado e replay;
- webhook duplicado/fora de ordem, crash entre receipt/efeito e reprocessamento;
- timeout na criação seguido de consulta sem cobrança duplicada;
- débitos iguais a créditos, BRL, valor positivo, imutabilidade e reversão vinculada;
- preço/comissão/líquido congelados e nunca aceitos do cliente;
- pagamento, transferência, reembolso e chargeback duplicados não duplicam lançamento;
- extratos de aluno/instrutor/plataforma segregados e saldo derivado;
- conciliação detecta faltante, duplicado, valor/data/parte divergentes;
- nenhum PAN/CVV/token sensível em banco, fixture, log ou erro.

### Execução, suporte e reputação

- conclusão bilateral, timeout, no-show por parte e transições concorrentes;
- linguagem/contrato não afirma homologação oficial;
- disputa dentro/fora da janela, evidência privada, decisão e efeito financeiro separado;
- denúncia/suporte escopado, suspensão preventiva autorizada e notas internas ocultas;
- avaliação somente de participação concluída, uma vez, moderação e média reconstruível.

### Auditoria, privacidade e segurança

- todo evento sensível esperado e nenhum segredo/dado completo;
- configuração organizacional: singleton, CNPJ, incompleto/pendente/validado, edição
  invalidando validação, versão stale, permissões distintas de editar/validar, Admin
  deny-by-default, auditoria redigida e ausência em API pública;
- audit append-only, ator sistema, request ID e acesso autorizado;
- aceite obrigatório não cria consentimento; concessão/retirada são granulares, versionadas e equivalentes em facilidade;
- direitos cobrem resposta imediata/15 dias aplicável, exportação sem dado de terceiro, propagação, correção, desativação, retenção/hold e reexecução após restore;
- regra automática registra versão/motivo e admite contestação; score/inferência não produz decisão adversa final;
- cookies opcionais não carregam antes da escolha; aceitar/rejeitar têm destaque equivalente e inventário técnico concilia declaração;
- headers/cookies/CORS/CSRF, IDOR, SSRF quando houver fetch, injeção/XSS, upload e ausência de PII em telemetria;
- segredo ausente/rotacionado, dependência vulnerável e configuração production-safe.

## Dados de teste e demonstração

- factories sintéticas e determinísticas, sem CPF/documento/cartão real;
- arquivos de teste inofensivos e string de teste de antivírus somente em ambiente isolado;
- fixtures de fornecedor sanitizadas e cobertas por contrato/licença;
- seed demo idempotente, marcado e tecnicamente bloqueado em produção;
- testes limpam isolamento próprio e não dependem de dado compartilhado.

## E2E de referência

```text
instrutor cria/verifica conta e recebe papel `INSTRUCTOR` sem concessão transitiva de outros papéis
→ aceita termos, envia aplicação/documentos/veículo
→ revisor pede correção e aprova
→ policy publica
→ aluno encontra oferta e propõe
→ instrutor contrapropõe; aluno aceita e obtém hold
→ gateway confirma; booking confirma e ledger registra
→ aula conclui ou entra em no-show/disputa
→ repasse/reembolso reconcilia
→ avaliação elegível publica
```

Variações obrigatórias: perda de elegibilidade; dois alunos no mesmo slot; pagamento duplicado/atrasado; cancelamento; chargeback; disputa com evidência; denúncia; conta bloqueada e fornecedor indisponível.

## Critérios de aceite por marco

| Marco | Suite/evidência mínima                                                         |
| ----- | ------------------------------------------------------------------------------ |
| M0    | revisão documental e tabletop das decisões                                     |
| M1    | unit/service/API/frontend, sessão/CSRF/MFA, aceite ≠ consentimento, compatibilidade/autorização independente de papéis e auditoria |
| M2    | E2E credenciamento, upload/scan, expiração, autorização e acessibilidade       |
| M3    | PostGIS/timezone, privacidade pública, proposta e concorrência do hold         |
| M4    | contract/sandbox, webhook/idempotência, property tests do ledger e conciliação |
| M5    | E2E completo e caminhos alternativos de disputa/suporte/reputação              |
| M6    | regressão, direitos/retenção/RIPD, incident drill, a11y, scans/pentest, restore/rollback e UAT |
| M7    | smoke por onda, qualidade de analytics, reconciliação diária e drills          |
| M8    | SLO/error budget, DR periódico, patch/release e regressão contínua             |

## Gate de release

CI verde; cobertura de risco (não apenas percentual); migrations/OpenAPI sem quebra; nenhuma falha crítica/alta sem exceção formal; backup restaurado na janela; rollback/roll-forward ensaiado; smoke e alertas confirmados; UAT/owners aprovados; checkpoint e release notes atualizados.

Flaky test é defeito: quarentena só com owner, prazo e issue; não pode ocultar suite crítica. Evidências de gate guardam commit, ambiente, data, resultado e aprovador.

## ADMIN-PROD-01

- Admin recusa sessão autenticada sem MFA e aceita sessão TOTP verificada;
- formulário solicita OTP, enrolamento gera recovery codes e auditoria sem segredo;
- concessão atribui somente permissões explícitas;
- organização, auditoria, CSRF, autorização e regressão permanecem obrigatórios;
- produção exige smoke externo de TLS, renovação, health/readiness e login humano com TOTP.
