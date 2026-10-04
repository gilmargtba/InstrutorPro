# Upload profissional voluntário — decisão expressa de 27/09/2026

O proprietário autorizou implementar, enviar para `origin/main` e implantar o upload real
voluntário nas 27 UFs, condicionado aos controles técnicos. Esta decisão substitui a exigência
anterior de retenção/privacidade aprovadas como gate de ativação desta funcionalidade.
Não aprova uma política jurídica, prazo de retenção nem lista estadual de documentos.

## Contrato e domínio

Complementação pós-verificação (04/10/2026): uma solicitação `VERIFIED` é imutável.
O instrutor real verificado e não publicado pode abrir um novo rascunho vinculado à
decisão anterior, anexar CNH como `OTHER_PROFESSIONAL` ou credenciamento como
`PROFESSIONAL_CERTIFICATE`, e enviar para nova análise humana. A submissão exige ao
menos um arquivo CLEAN; todos os anexos complementares exigem aprovação individual
do revisor. O CPF não é reaberto, o arquivo não ganha URL pública e o envio torna a
verificação corrente pendente, sem publicação automática. Uma complementação rejeitada
pode ser refeita; o histórico anterior não é sobrescrito. Perfil já publicado não usa
esse fluxo, para não mudar silenciosamente uma publicação ativa.

- `document_upload_available` / `documents_enabled` dependem das flags documentais,
  modo `PRODUCTION`, scanner configurado e storage privado; não dependem de uma lista estadual.
- Autorização documental em modo `PRODUCTION` é específica: não liga pagamentos,
  publicação automática nem outras capacidades proibidas pelo gate global.
- Documento voluntário usa `document_type`: `PROFESSIONAL_CREDENTIAL`,
  `PROFESSIONAL_CERTIFICATE` ou `OTHER_PROFESSIONAL`, sem `requirement_id`.
  Requisito territorial continua separado, versionado e aprovado com fonte legítima.
- Migration 0012 torna o vínculo territorial opcional e exige tipo voluntário válido
  e solicitação vinculada quando não há requisito. Nenhum requisito estadual é criado.
- CPF salvo, proprietário autenticado e solicitação DRAFT são obrigatórios para upload.
  PDF/JPEG/PNG, extensão única, MIME, assinatura e limite de 5 MB são validados no serviço.
- Arquivo inicia na quarentena. Scanner indisponível mantém PENDING; detecção mantém BLOCKED;
  somente CLEAN é promovido ao storage de evidências. Qualquer não-CLEAN bloqueia submissão,
  inclusive quando a flag é desligada. Arquivos voluntários não são obrigatórios.
- Admin mostra somente CLEAN ao revisor responsável com permissão documental explícita;
  download autenticado, auditado, sem cache. Titular não tem download de revisão.
  Anexo ou aprovação de arquivo não verifica nem publica automaticamente o instrutor.
- Retenção segue `POLICY_PENDING` sem prazo fabricado quando não há política aprovada;
  rotina de descarte permanece dependente da política válida. Privacidade continua pendente.

## Implantação assistida

A conexão SSH automatizada não está autenticada. Executar no terminal já aberto da VPS:

```bash
cd /home/gilmar/InstrutorPro
(
  set -eu
  test -z "$(git status --porcelain --untracked-files=no)"
  printf 'VPS_HEAD_BEFORE='; git rev-parse HEAD
  sh scripts/backup-production.sh
  git pull --ff-only origin main
  sh scripts/deploy-professional-upload.sh --deploy-and-enable
)
```

O script confirma branch/HEAD/árvore limpa e flags inicialmente OFF, preserva backup do banco,
documentos e configuração; rebuild/restart limita-se à aplicação e scanner. Não executa
`down -v`, reset, remoção de volumes ou restauração sobre dados de produção.

Antes e depois da ativação executa `check_document_upload --confirm-technical-test`:
scan real limpo/EICAR, falha fechada, formatos/tamanho, promoção, quarentena,
autorização/IDOR, download autorizado e backup/restauração isolada com hash.
As contas de teste não têm senha utilizável. Banco é rollback-only e arquivos ficam em
diretório temporário exclusivo dentro do volume privado, removido ao concluir ou falhar.
O comando não altera flags persistentes e não toca em documentos existentes.
O teste de frescor é técnico (assinaturas carregadas com menos de 48 h), não regra legal.

Na primeira execução assistida, o smoke parou antes de ativar as flags: o teste usava
EICAR apenas concatenado a um cabeçalho `%PDF`, que o ClamAV considerou limpo.
O diagnóstico na VPS confirmou EICAR puro `BLOCKED`, mas os prefixos PDF/JPEG
artificiais `CLEAN`. Um PDF com EICAR como anexo interno retornou `BLOCKED` no
scanner real. O smoke agora usa esse PDF com catálogo, objeto incorporado e xref
válidos; mantém a exigência de bloqueio pelo pipeline completo. Não se alterou a
política do scanner nem se dispensou a verificação de vírus.

O script liga apenas `REAL_DOCUMENT_UPLOADS=true`, `REAL_DOCUMENT_UPLOAD_ENABLED=true`
e `PROFESSIONAL_DOCUMENT_UPLOAD_MODE=PRODUCTION` depois do PASS técnico. Se falhar após
ativação, restaura a configuração anterior e recria backend/worker/scheduler; mantém
código/migration e todos os dados. Rollback operacional posterior: desligar essas três
flags e recriar esses serviços, sem desfazer migration que já tenha documentos genéricos.

## Estado verificável da entrega

Na execução assistida da VPS em 27/09/2026, o commit `0c51b99` produziu
`DOCUMENT_TECHNICAL_SMOKE=PASS` antes e depois de ligar as flags, readiness
`status=ok` com banco `up` e `DOCUMENT_UPLOAD_PRODUCTION_STATUS=ENABLED`.
Os controles de storage privado, EICAR, fail-closed, autorização, IDOR e
backup/restauração técnica isolada passaram. Verificação e publicação automáticas
permanecem desligadas. O teste usa dados sintéticos com rollback e não substitui
um teste manual do fluxo de um instrutor real no navegador.
Revisão de privacidade e política de retenção de produção: **PENDING**, não PASS.
Requisitos estaduais aprovados observados na última consulta: **0 UFs**.
