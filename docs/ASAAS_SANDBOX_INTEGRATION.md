# Integração Asaas — preparação restrita a sandbox

Decisão do proprietário: o MVP é geração de leads; Asaas serve exclusivamente à
assinatura opcional PRO, nunca ao pagamento da aula. A primeira fatia é um
adaptador local, ainda sem checkout público ou webhook de produção. Nenhuma
credencial deve entrar no Git, no frontend, em logs ou no chat.

## Contrato técnico verificado em 29/09/2026

- API sandbox `https://api-sandbox.asaas.com/v3` com `access_token` e
  `User-Agent`; chaves de produção são rejeitadas pelo adaptador.
- Customer usa `externalReference` para correlação; o serviço de aplicação
  deverá consultar/reutilizar cliente existente antes de criar, pois o Asaas
  permite duplicatas.
- Checkout hospedado `RECURRENT` cria a jornada de assinatura, mas resposta de
  criação ou redirecionamento do browser **não confirma** pagamento.
- Neste primeiro adaptador, cartão recorrente é o único meio preparado. Pix
  exige prova específica de recorrência antes de ser oferecido; boleto não
  está incluído.
- Webhook usa o cabeçalho `asaas-access-token` configurado no Asaas, não HMAC
  do corpo. Eventos têm ID estável e podem ser entregues mais de uma vez;
  o processamento deverá validar token, deduplicar ID e conciliar o estado.

Fontes oficiais: [autenticação](https://docs.asaas.com/docs/authentication),
[criar cliente](https://docs.asaas.com/reference/create-new-customer),
[checkout recorrente](https://docs.asaas.com/docs/checkout-with-subscription-recurring),
[checkout hospedado](https://docs.asaas.com/docs/asaas-checkout),
[webhooks](https://docs.asaas.com/docs/receive-asaas-events-at-your-webhook-endpoint),
[idempotência](https://docs.asaas.com/docs/how-to-implement-idempotence-in-webhooks),
[cancelar assinatura](https://docs.asaas.com/reference/remove-subscription).

## Gates pendentes

Preço mensal real de PRO, dados/conta sandbox do proprietário, URL de webhook
acessível ao Asaas, serviço de assinatura idempotente e auditado, estados de
período pago, autorização da UI, segurança/privacidade, reconciliação e ciclo
E2E ainda não foram concluídos. Sem esses itens, não definir
`REAL_PAYMENTS=true` nem `REAL_PRO_BILLING=true`. O adaptador também não altera
`RegulatoryReadiness`, verificação ou publicação do instrutor.
