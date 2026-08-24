# Plano do Piloto Controlado

Fonte oficial do piloto. A funcionalidade é definitiva; cidade, duração, orçamento, limites e thresholds numéricos continuam bloqueantes porque a documentação não contém evidência para escolhê-los. Esses campos são congelados em `PIL-001`, antes do primeiro usuário real.

## Objetivo e pergunta de decisão

Validar se, em uma região limitada, há oferta elegível suficiente, alunos convertem e repetem, a margem de contribuição é defensável e segurança/suporte/conciliação permanecem controláveis. Resultado: `GO`, `ITERATE` ou `NO_GO`, nunca expansão automática.

## Escopo definitivo

- cidade/região de operação assistida escolhida no planejamento do piloto, sem alterar o `OPEN-001` nacional já fechado; categoria B priorizada;
- meta de 20–50 instrutores **elegíveis e com oferta ativa**, distribuídos na área e horários relevantes;
- alunos adquiridos em coortes/ondas limitadas;
- jornada completa do MVP, inclusive pagamento, cancelamento, no-show, disputa, denúncia, avaliação e direitos;
- gateway/fornecedores reais aprovados, limites financeiros/volume configurados;
- operação assistida, conciliação diária, suporte em horário publicado, on-call de incidente e revisão semanal;
- web/PWA; sem app nativo, chat, biometria, tracking contínuo, integração governamental ou nova região.

Suporte pode orientar cadastro/agenda/checkout, reenviar ação segura e acionar serviço administrativo autorizado, sempre registrando a intervenção. Nunca recebe senha, OTP, cartão, token, dinheiro ou altera banco/ledger manualmente.

## Checklist de entrada

- M0–M6 aceitos e `REL-006` homologado;
- organização, cidade/categoria, regras locais e autorização/evidência aprovadas;
- termos, política comercial, privacidade, fornecedores e pareceres vigentes;
- critérios, coortes, duração, orçamento, comissão e baseline congelados;
- SLO, RPO/RTO, suporte/on-call, capacidade e limites definidos;
- segurança/pentest, rights flow, incident drill, backup restore, rollback e runbooks aprovados;
- gateway/ledger/conciliação/chargeback testados; contas e credenciais reais segregadas;
- dashboards/analytics validados sem PII indevida;
- recrutamento, treinamento, contatos e stop conditions comunicados.

Qualquer item ausente impede início; “corrigir durante o piloto” não substitui gate crítico.

## Parâmetros a congelar em PIL-001

| Campo                                                  | Status atual              | Owner                             |
| ------------------------------------------------------ | ------------------------- | --------------------------------- |
| cidade/área operacional do piloto                      | bloqueante do próprio piloto, não da arquitetura/CODEX 02 | Product + Operations + Compliance |
| datas/duração e tamanho das ondas                      | bloqueante `OPEN-010`     | Product + Data                    |
| comissão/preço/promoção/cancelamento                   | bloqueante `OPEN-003`     | Product + Finance + Legal         |
| orçamento e limite por transação/dia/coorte            | bloqueante `OPEN-009/010` | Finance + Operations              |
| horário/SLA/escalonamento de suporte                   | bloqueante `OPEN-009`     | Operations                        |
| thresholds de funil/repetição/margem/satisfação/fraude | bloqueante `OPEN-010`     | Product + Data + Finance          |
| SLO/RPO/RTO e error budget                             | bloqueante `OPEN-009`     | Engineering + Operations          |

## Execução

### Oferta

Recrutar por contato direto, associações, indicação e parceiros. Contar como oferta somente instrutor elegível, publicável, com recebedor habilitado, oferta/agenda ativa e onboarding concluído. Medir cobertura espacial/temporal, tempo de aprovação, pendências e ativação.

### Demanda

Aquisição limitada por intenção local, indicação, conteúdo/parcerias e canais aprovados. Instrumentar origem/coorte e consentimento de marketing; não ampliar spend antes de qualidade/conciliação da onda anterior.

### Ondas

Começar no menor lote operacional, executar smoke e janela de observação, então ampliar até limite congelado. Feature flags/allowlists não contornam autorização. Toda mudança de regra durante o piloto é registrada e separa a coorte; critério de saída original não é reescrito.

### Rotina

- contínuo: alertas, segurança, disponibilidade e stop conditions;
- diário: pagamentos/transferências/ledger, filas, backup, casos críticos e intervenção manual;
- semanal: funil/coortes, oferta, margem, suporte, fraude, satisfação, risco e decisões;
- fim: export reprodutível, entrevistas, relatório, decisão e destino dos dados.

## Métricas e denominadores

| Dimensão       | Métricas mínimas                                                                               |
| -------------- | ---------------------------------------------------------------------------------------------- |
| oferta         | cadastrados, elegíveis, oferta ativa, cobertura, slots e tempo até ativo                       |
| funil          | visitas/buscas → perfil → solicitação → proposta aceita → pagamento → conclusão                |
| qualidade      | cancelamento por parte/motivo, no-show, disputa, denúncia, refund/chargeback e satisfação      |
| retenção       | segunda solicitação/pagamento/conclusão por coorte e janela congelada                          |
| economia       | GMV, comissão, taxas, perdas, custo variável, suporte e margem de contribuição por aula/coorte |
| operação       | casos/minutos/intervenções por aula, SLA, backlog, divergência e reprocessamento               |
| tecnologia     | SLO/error budget, latência/erro, fila/webhook, incidentes, RPO/RTO e falha de fornecedor       |
| segurança/LGPD | acessos anômalos, fraude, vulnerabilidade, pedido de titular, incidente e tempo de resposta    |

Cada métrica define evento, denominador, exclusões, janela, fonte e owner antes do lançamento. Métrica sem qualidade verificada não sustenta `GO`.

## Stop conditions

Pausar novas entradas/cobranças ou o piloto conforme runbook quando houver: publicação irregular; risco imediato à segurança; incidente de dados relevante; webhook/ledger/conciliação sem confiança; gateway/serviço crítico fora do limite; fraude/chargeback além do threshold; suporte sem capacidade; RPO/RTO/SLO rompido sem contenção; ordem jurídica/regulatória ou termo inválido.

Owner on-call pode pausar de forma conservadora; retorno exige causa/impacto, reconciliação, correção/mitigação, smoke e aprovador definidos.

## Critério de saída

- **GO:** todos os mínimos congelados atingidos, margem não negativa após custos variáveis conforme política, risco crítico controlado e operação suportável; libera M8, não expansão irrestrita.
- **ITERATE:** hipótese promissora, mas gap tratável com nova mudança/coorte e orçamento aprovado; volta a M6/M7 afetado.
- **NO_GO:** demanda/economia/risco/operação não sustentam continuação ou stop condition irremediável; encerra aquisição/transações e executa plano de dados/contratos.

Relatório final contém população/coortes, mudanças, métricas contra baseline, custos, incidentes, entrevistas, vieses, riscos, decisão/assinaturas, backlog e tratamento de contas/dados.
