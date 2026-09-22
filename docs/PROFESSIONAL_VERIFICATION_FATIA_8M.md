# Fatia 8M — verificação profissional real

## Escopo autorizado

Esta fatia permite que o próprio instrutor solicite verificação profissional e que um operador
administrativo autorizado registre a análise. A aprovação confirma somente a verificação interna
da identidade profissional consultada. Ela não homologa aula, não representa autorização oficial,
não aprova publicação e não torna o perfil pesquisável.

Uploads reais, busca pública, publicação automática, pagamentos e Pro permanecem bloqueados.

## Fluxo

1. O instrutor autenticado abre `Status do cadastro` e escolhe `Solicitar verificação profissional`.
2. Informa o próprio CPF na área privada, confirma a finalidade e envia a solicitação.
3. O servidor valida o CPF, cifra-o com Fernet e grava apenas índice cego HMAC-SHA-256 separado e
   os dois últimos dígitos para máscara. O valor integral não aparece em API, lista ou log.
4. A solicitação percorre `DRAFT -> SUBMITTED -> UNDER_REVIEW -> VERIFIED|REJECTED`.
5. O admin com permissão explícita assume a solicitação. `select_for_update` e vínculo do revisor
   impedem decisões concorrentes por outro operador.
6. A aprovação exige método, fonte autorizada e data da consulta. A rejeição exige código de motivo
   e devolve ao titular apenas mensagem segura.

O reenvio de uma solicitação já enviada é idempotente. Uma rejeição permite nova solicitação sem
apagar o histórico e as auditorias anteriores.

## Dados e segurança

- `PII_FIELD_ENCRYPTION_KEY`: chave Fernet, exclusiva de produção e fora do Git.
- `PII_FINGERPRINT_KEY`: segredo HMAC separado, aleatório e com no mínimo 32 caracteres.
- CPF integral só pode ser revelado por uma tela administrativa excepcional, protegida por MFA,
  permissão `reveal_protected_identifier`, POST com CSRF, resposta `no-store` e auditoria.
- A fila requer `review_professional_verification`; criação e exclusão manual são bloqueadas.
- Não incluir CPF, ciphertext, fingerprint ou notas internas em observabilidade e suporte.

## Configuração

O gate é fail-closed:

```text
PROFESSIONAL_VERIFICATION_MODE=PRODUCTION
REAL_PROFESSIONAL_VERIFICATION=true
PII_FIELD_ENCRYPTION_KEY=<segredo Fernet>
PII_FINGERPRINT_KEY=<segredo HMAC separado>
```

`production_readiness` falha se o modo estiver em produção sem capability ou sem as duas chaves.
`REAL_DOCUMENT_UPLOADS=false` e `REAL_AUTOMATIC_PUBLICATION=false` devem permanecer inalterados.

## Deploy e rollback

Antes do deploy: backup do banco e do `.env.production`, validação dos segredos sem imprimi-los,
build das quatro imagens e `production_readiness`. Aplicar as migrations aditivas antes de recriar
somente `backend`, `frontend`, `worker` e `scheduler`. Não recriar PostgreSQL, Redis, gateway,
certificados ou volumes.

Rollback funcional: definir `PROFESSIONAL_VERIFICATION_MODE=DISABLED` e
`REAL_PROFESSIONAL_VERIFICATION=false`, reconstruir/recriar apenas os serviços da aplicação e
preservar tabelas, ciphertext, auditoria e chaves. A migration é aditiva e não deve ser revertida
em produção como resposta operacional inicial.
