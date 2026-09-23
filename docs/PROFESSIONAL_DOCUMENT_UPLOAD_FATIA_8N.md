# Fatia 8N — documentos profissionais privados (pré-ativação)

Estado em 23/09/2026: código local preparado, **não implantado**. `REAL_DOCUMENT_UPLOADS=false` em produção. Esta fatia não aprova regra documental de qualquer Detran e não altera a separação entre verificação e publicação.

## Fluxo implementado

- O instrutor autenticado salva CPF no rascunho e só vê requisitos previamente aprovados para sua UF, categoria e tipo `INSTRUCTOR`. Uma regra exige versão, vigência e referência de fonte. Não há preenchimento automático das 27 UFs.
- O arquivo recebe chave interna aleatória em volume privado, passa por validação de extensão, MIME, assinatura e limite atual de 5 MB. A quarentena é o estado inicial. O serviço clamd usa `INSTREAM`, timeout e falha fechada; erro do scanner mantém o documento pendente.
- Somente o resultado `CLEAN` é promovido para a área privada de revisão. A submissão exige todos os requisitos obrigatórios do momento e nenhum arquivo pendente/bloqueado. O snapshot dos requisitos é preservado na solicitação.
- O próprio instrutor pode remover o arquivo em `DRAFT`; depois de `SUBMITTED`, não pode alterar o conjunto. A revisão e o download exigem revisor designado e permissão explícita. O download é streaming autenticado, auditado, `nosniff` e sem cache.
- O Admin pode aprovar regras com fonte registrada e revisar documentos. O objeto real não permite edição manual dos campos nem exibe a chave física do arquivo no formulário. `VERIFIED` não implica `PUBLISHED`.
- O frontend mostra somente metadados e requisitos aplicáveis; não há URL pública de arquivo. O nginx bloqueia diretamente `/media`, `/quarantine`, `/private_documents` e `/professional-documents`.

## Pendências antes de ativar

1. Confirmar em ambiente real o volume privado, permissões e bloqueio HTTP direto, inclusive por hostname e IP.
2. Subir clamd com base de assinaturas atualizada e comprovar health check, detecção EICAR inofensiva, indisponibilidade e recuperação. A imagem foi declarada, mas ainda não homologada na VPS.
3. Validar backup **e restauração** do volume documental junto do banco. `scripts/backup-production.sh` agora prepara um arquivo TAR privado e checksum, mas não foi executado nem restaurado na VPS; backup na mesma VPS não substitui cópia protegida independente.
4. Aprovar política jurídica de retenção e descarte. Os campos `retention_expires_at` e `legal_hold` foram criados, mas não existe expurgo automático autorizado; nenhum prazo nacional foi presumido.
5. Revisar e aprovar nova versão da Política de Privacidade para explicitar finalidade, acesso, conservação e eliminação dos documentos. Não editar o texto jurídico sem aprovação.
6. Fazer smoke completo com arquivo não pessoal e confirmar que as regras aprovadas refletem apenas as UFs/categorias cuja fonte foi registrada.

Enquanto qualquer item acima estiver pendente, manter `REAL_DOCUMENT_UPLOADS=false`, `REAL_DOCUMENT_UPLOAD_ENABLED=false` e `PROFESSIONAL_DOCUMENT_UPLOAD_MODE=DISABLED` na VPS. Código e migrations aditivas podem ser entregues separadamente; ativação precisa de uma decisão operacional posterior e testes proporcionais.

## Rollback

Desligar as três configurações antes de reverter código. Não apagar documentos, migrations, snapshots nem auditoria. Preservar volume privado e backups para recuperação controlada.
