# Correção pós-8J — cadastro real de instrutor

Data: 20/09/2026 (America/Sao_Paulo).

## Diagnóstico

- a rota pública `/cadastro/instrutor` respondia HTTP 200;
- `POST /api/v1/marketplace/accounts/register/` respondia HTTP 403 antes de persistir a
  requisição diagnóstica `example.invalid`;
- causa do 403: `REAL_PRODUCTION_AUTHORIZATION=NOT_GRANTED` e as capabilities
  `REAL_ACCOUNT_REGISTRATION`, `REAL_PERSONAL_DATA` e `REAL_INSTRUCTOR_REGISTRATION` falsas;
- o link da Home existia, mas a navegação superior escondia “Sou instrutor” em produção;
- após o cadastro, o frontend não abria onboarding real; a implementação anterior apontava para
  “Meus dados”, enquanto a única rota completa de onboarding era restrita a DEV/TEST;
- a tela de status em produção ainda consultava um endpoint `/demo/` inexistente.

`ROOT_CAUSE_INSTRUCTOR_REGISTRATION=CAPABILITIES_NOT_GRANTED_AND_REAL_ONBOARDING_NOT_ROUTED`

## Correção

- a navegação pública de produção aponta “Sou instrutor” para `/cadastro/instrutor`;
- cadastro bem-sucedido de instrutor segue para `/profissional/instrutor/onboarding`;
- o onboarding real salva somente apresentação, categoria, transmissão, WhatsApp profissional,
  oferta, veículo e área pública aproximada de atendimento pelo endpoint autenticado
  `PATCH /api/v1/account/me/`;
- a interface informa explicitamente que não se deve usar residência como centro público;
- não há upload documental no fluxo;
- a tela de status usa `/api/v1/account/me/` e informa que o cadastro não é publicado
  automaticamente;
- o exemplo de produção registra a decisão autorizada:
  `CONTROLLED_PILOT` com conta, dados pessoais e cadastro de instrutor habilitados.

## Invariantes preservadas

- conta, pessoa, papel e aceite jurídico continuam numa única transação;
- Termos do Instrutor e Política vigentes continuam obrigatórios, versionados e auditáveis;
- todo instrutor nasce `verification_status=NOT_STARTED` e
  `publication_status=UNPUBLISHED`;
- cadastro aceita qualquer uma das 27 UFs válidas no onboarding;
- ausência de `RegulatoryReadiness` não bloqueia cadastro, mas impede publicação;
- `REAL_MARKETPLACE_SEARCH`, `REAL_WHATSAPP_CONTACT`, `REAL_MARKETPLACE_ANALYTICS`,
  `REAL_DOCUMENT_UPLOADS`, `REAL_AUTOMATIC_PUBLICATION`, `REAL_PAYMENTS` e
  `REAL_PRO_BILLING` permanecem falsas;
- MapTiler não participa da criação de conta nem do onboarding.

## Validação local

- reprodução segura em produção antes da correção: rota HTTP 200 e API HTTP 403, sem criação;
- 21 testes focados de piloto: `PASS`;
- suíte backend: 199 testes `PASS`;
- Django check: `PASS`; migration check: sem deriva;
- Ruff check/format: `PASS`;
- Angular production build e testes headless: `PASS` (aviso preexistente de budget do mapa).

## Limite jurídico e operacional

A autorização cobre exclusivamente cadastro de instrutor no piloto controlado. `FULL_PRODUCTION`
continua bloqueada enquanto permanecerem pendentes o enquadramento DPO/pequeno porte, as decisões
jurídicas residuais de retenção e os demais gates documentados. Cadastro não constitui
credenciamento, verificação, elegibilidade, publicação ou homologação de aula.
