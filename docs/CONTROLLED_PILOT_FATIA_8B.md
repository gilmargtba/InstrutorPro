# Fatia 8B — piloto real controlado

Data da avaliação: 17/09/2026.

## Resultado

O estado `CONTROLLED_PILOT` e a matriz granular foram implementados com comportamento
fail-closed. Nenhuma capacidade real foi ativada nesta entrega.

O bloqueio imediato para abertura de cadastro real é específico: não existe Termo de Uso
publicado, versionado e revisado nem persistência de aceite com usuário, versão dos termos,
versão da política e data/hora. A Política de Privacidade publicada não substitui os Termos.
Não foi criado texto jurídico presumido.

## Matriz verificada

| Capacidade | Estado | Evidência/razão |
| --- | --- | --- |
| Cadastro real de conta | BLOCKED | aceite versionado dos Termos ausente |
| Dados pessoais reais | BLOCKED | depende de cadastro real e gates LGPD abertos |
| Uso real por aluno | BLOCKED | fluxo real ainda não implementado/testado |
| Cadastro real de instrutor | BLOCKED | fluxo real ainda não implementado/testado |
| Busca de marketplace real | BLOCKED | nenhum perfil real aprovado em teste |
| Contato WhatsApp real | BLOCKED | teste real não executado |
| Analytics real | BLOCKED | teste real não executado |
| Upload documental real | BLOCKED | storage privado e antimalware não homologados |
| Publicação automática | BLOCKED | proibida no piloto; `PublicationDecision` permanece obrigatório |
| Pagamentos | BLOCKED | fora da autorização |
| Cobrança PRO | BLOCKED | fora da autorização |
| Produção comercial completa | NOT AUTHORIZED | `FULL_PRODUCTION` não autorizado |

## Estados e regras

- `NOT_GRANTED`: qualquer capability configurada como verdadeira invalida a prontidão.
- `CONTROLLED_PILOT`: somente capabilities explicitamente permitidas e configuradas podem
  ficar efetivas.
- `FULL_PRODUCTION`: existe como estado técnico, mas não foi configurado nem autorizado.
- documentos, publicação automática, pagamentos e cobrança PRO são recusados no piloto,
  mesmo se uma variável de ambiente for alterada por engano.
- os aliases antigos continuam fechados em produção e não concedem acesso.

## Validação local

- lint Ruff: aprovado;
- testes focados de prontidão/capabilities: 7 aprovados;
- suíte backend: 151 aprovados;
- migration: nenhuma criada;
- deploy/VPS: não executado, pois nenhuma capability real atingiu seus gates.

## Próximo gate executável

1. fornecer e aprovar o texto dos Termos de Uso aplicável a aluno e instrutor;
2. implementar `LegalDocument` e `LegalAcceptanceRecord` (ou equivalentes) com versões
   imutáveis e aceite transacional;
3. implementar cadastro real com autorização por objeto e sem upload documental;
4. repetir testes automatizados e smoke test real;
5. somente então configurar `CONTROLLED_PILOT` e as capabilities cujo teste real passou.

