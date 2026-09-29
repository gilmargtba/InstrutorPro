# Requisitos para seleção do gateway de pagamento

Status em 29/09/2026: Asaas selecionado pelo proprietário apenas para preparar
a assinatura PRO em sandbox. Os critérios abaixo eram do modelo anterior de
pagamento de aulas; split/recebedor do instrutor não fazem parte do MVP atual.
Preço PRO, contrato, tributação, privacidade, teste E2E e autorização de
cobrança real permanecem pendentes. `REAL_PAYMENTS=false` e
`REAL_PRO_BILLING=false`.
O Asaas documenta autenticação do webhook por `authToken` enviado no cabeçalho
`asaas-access-token`, e não assinatura HMAC do corpo. O requisito histórico de
"webhook assinado" abaixo não deve ser implementado literalmente para Asaas;
validar token em tempo constante, ID do evento, idempotência e reconciliação.

## Capacidades obrigatórias

O processo de seleção deve demonstrar em sandbox e contrato:

- Pix e cartão por checkout hospedado ou tokenização; o InstrutorProCNH não recebe PAN/CVV;
- assinatura/recorrência com estados explícitos e consulta reconciliável;
- webhook assinado sobre corpo bruto, ID estável, retries documentados e rotação de segredo;
- idempotência nas criações, estorno total/parcial, cancelamento e consulta pós-timeout;
- API e sandbox separados, documentação versionada, limites e suporte de incidente;
- exportação de liquidação/conciliação e estratégia de saída/portabilidade;
- cadastro/KYC da empresa, recebedores, split e prazo de liquidação compatíveis com o modelo;
- responsabilidades fiscais, contábeis, consumeristas, antifraude e de chargeback aprovadas;
- DPA/papel LGPD, subprocessadores, países, retenção e transferência internacional avaliados.

## Evidências comerciais pendentes

Taxas, antecipação, reservas, prazo de liquidação, limites, SLA e exigências de cadastro devem ser
obtidos em proposta formal. Nenhum preço ou fornecedor é inferido neste documento. `OPEN-005`
permanece bloqueante para dinheiro real.

## Prova técnica comparável

Cada candidato deve executar os mesmos casos: criar pagamento idempotente, timeout de efeito
desconhecido, webhook válido/inválido/duplicado/fora de ordem, recusa, cancelamento, estorno,
rotação do segredo, indisponibilidade, reconciliação e exportação. A decisão registra trade-offs,
owner, rollback e evidências; somente então um adaptador concreto pode ser adicionado.

