# Configuração futura do gateway de pagamento

Asaas foi escolhido em 29/09/2026 somente para a assinatura PRO em sandbox.
A fundação preexistente continua sem cobrança real. O adaptador sandbox local
não está ligado a uma rota pública de checkout nem concede entitlement.

## Variáveis por ambiente

```text
PAYMENT_PROVIDER=ASAAS
PAYMENT_ENVIRONMENT=sandbox
PAYMENT_API_KEY=
PAYMENT_WEBHOOK_SECRET=
REAL_PAYMENTS=false
REAL_PRO_BILLING=false
```

Chaves e segredos ficam exclusivamente no secret store/arquivo de ambiente com permissão mínima,
nunca no Git, logs, frontend ou suporte. Produção e sandbox usam credenciais e endpoints separados.

## Credenciais a solicitar depois da seleção

- identificador da conta/estabelecimento e credencial de API server-side;
- segredo de webhook e procedimento de rotação sobreposta;
- credenciais e conta exclusivas de sandbox;
- identificadores/configuração de checkout, Pix, cartão e recorrência aprovados;
- configuração de recebedores/split somente após decisão jurídica, fiscal e contábil;
- allowlists, certificados ou mTLS, caso exigidos;
- acesso a relatórios de liquidação e reconciliação.

## Sequência de ativação

1. concluir a prova sandbox de PRO, definir preço e fechar os gates comerciais,
   contratuais, fiscais, contábeis e de privacidade ainda abertos;
2. implementar e revisar o adaptador concreto sem alterar o domínio;
3. configurar somente sandbox e validar assinatura, idempotência, retries e reconciliação;
4. executar testes de segurança, falha, refund e restore;
5. aprovar preço, entitlement, suporte, rollback e observabilidade;
6. liberar `REAL_PAYMENTS` e depois `REAL_PRO_BILLING` em mudança separada e autorizada.

O redirect/browser nunca confirma pagamento. Somente confirmação autenticada do backend/gateway
pode produzir transição financeira ou ativar assinatura PRO.

