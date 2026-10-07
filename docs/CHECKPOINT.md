# Checkpoint do Projeto

## Foto opcional do instrutor real — 07/10/2026

- A tela de cadastro profissional oferece envio separado de JPEG/PNG até 5 MB,
  com consentimento específico para exibição após revisão e publicação. O
  instrutor consulta o estado e acessa a própria foto por rota privada auditada.
- O backend valida assinatura/MIME/tamanho, exige storage privado e ClamAV
  disponíveis, bloqueia arquivo não limpo e segundo anexo pendente, e registra
  auditoria. A revisão humana existente no Admin decide a foto; a rota pública
  de dados reais exige foto aprovada, consentimento e elegibilidade/publicação
  efetiva do perfil. Nenhum gate de publicação é dispensado.
- Validação local: 373 testes backend, Ruff, Django check, migration check,
  58 testes Angular e build de produção passaram; sem migration nova.
  Avisos preexistentes de orçamento do bundle/SCSS permanecem.
  Publicação no remoto e deploy permanecem pendentes nesta fatia.

## Correção do zero no mapa local após contagem nacional — 06/10/2026

- A contagem nacional incluía o perfil GO com oferta ativa A, mas o mapa local
  selecionava B por padrão; isso produzia zero no clique apesar do perfil estar
  publicado. A busca local agora inicia em todas as categorias e preserva o
  filtro quando A–E é escolhido explicitamente, inclusive em links antigos.
- Sem categoria, a API só aceita oferta ativa de categoria declarada, devolve
  `offer_category` correspondente ao preço e o botão WhatsApp usa essa
  categoria. Um resultado vazio filtrado oferece “Ver todas as categorias”.
  Nenhum perfil, oferta, documento ou UF foi aprovado automaticamente.
- Validação local: 371 testes backend, 57 frontend, build Angular de produção,
  Ruff, Django check e migration check passaram; sem migration nova. Permanecem
  avisos preexistentes de orçamento do bundle/SCSS. Commit `b386ca5` enviado a
  `origin/main` e aplicado na VPS por fast-forward após backup validado do banco
  e dos documentos privados (`20261006T210558Z`). Backend/frontend reconstruídos
  e saudáveis; nenhuma migration a aplicar, Django check e migration check sem
  erro. Smoke público em Goiatuba/GO: todas as categorias=1 com oferta A, A=1,
  B=0; página do mapa HTTP 200. Nenhuma decisão administrativa foi alterada.

## Deploy da busca A–E e raio irrestrito — 06/10/2026

- `origin/main` e VPS receberam, por fast-forward, `7f5fc50` e `3d58a84`.
  Backup pré-deploy do banco e dos documentos privados passou em validação de
  arquivo e SHA-256; a restauração não foi executada nesta atualização.
- Imagens backend/frontend reconstruídas; migrations: nenhuma a aplicar.
  Containers backend/frontend saudáveis, Django check sem erros e migration
  check sem deriva. Health, readiness e página do mapa responderam HTTP 200.
- Smoke público de Goiatuba/GO, categoria A, sem `radius_km`: 1 instrutor
  retornado. Nenhuma UF, oferta ou perfil foi aprovado/publicado pelo deploy;
  flags comerciais/financeiras não foram alteradas.

## Categorias A–E no FREE e busca nacional — 06/10/2026

- Decisão comercial registrada: FREE não limita categorias e PRO não substitui
  verificação, prontidão de UF ou publicação manual.
- A API de busca aceita A–E e exige oferta ativa da categoria consultada;
  o preço exibido vem dessa oferta, não de outra categoria do mesmo perfil.
- O mapa restaura a categoria do link, inicia com “Qualquer distância (Brasil)”
  e não filtra veículo sem escolha do aluno. A busca continua limitada em
  quantidade de resultados, ordenada pela distância ao ponto informado.
- Nenhuma UF, perfil ou oferta foi ativada automaticamente. O deploy está
  registrado na seção acima.

## Busca pública com raio flexível — 06/10/2026

- A busca aceita raio inteiro de 1 a 5000 km ou distância irrestrita quando
  `radius_km` é omitido. A interface oferece campo em km e opção “Qualquer
  distância (Brasil)”, sem limitar resultados à UF do ponto pesquisado.
- Permanecem os gates de perfil publicado, categoria/oferta ativa e o limite
  configurado de resultados; a mudança não cria ofertas nem altera decisão
  regulatória. Em produção, o perfil real observado em Goiatuba tem apenas
  categoria/oferta A, portanto não aparece na busca B mesmo sem limite de raio.
- Validação local: 364 testes backend, 53 frontend, build Angular, Ruff,
  Django check e migration check passaram. Os avisos preexistentes de orçamento
  do build permanecem. O deploy posterior está registrado na seção acima.

## Painel único de aprovação e publicação — 05/10/2026

- O perfil administrativo real mostra, numa seção, todos os gates de
  publicação, documentos revisáveis, evidências da UF, categorias A–E e ofertas
  ativas. As ações de revisão da UF, verificação, rejeição, oferta e publicação
  ficam nessa página. O botão combinado exige confirmações humanas separadas
  e usa transação única; não libera UF sem fonte/vigência nem publica perfil
  sem oferta ativa por categoria, área, contato e visibilidade efetiva.
- O painel mostra exatamente quando falta oferta de uma categoria; não copia A
  para B. Após publicação, abre perfil público e busca pré-preenchida.
- Validação local: 361 testes backend, 47 testes frontend, Ruff, Django check,
  migration check e build Angular passaram. O build conserva avisos preexistentes
  de orçamento de bundle/SCSS.
- Deploy de `3abf23e` na VPS concluído após backup validado de banco e
  documentos privados. Atualização fast-forward, rebuild apenas do backend,
  container saudável, Django check, migration check e readiness pública passaram.
  Sem migration nova. Consulta somente leitura do perfil real em Goiatuba/GO:
  `UNDER_REVIEW`, verificação `VERIFIED`, publicação `UNPUBLISHED`; bloqueios
  calculados: GO `REVIEW_REQUIRED` e oferta B ausente/inativa. A fonte
  regulatória cadastrada contém os campos técnicos mínimos; a vigência e o
  mérito permanecem para confirmação humana de `gilmar`. Nenhuma UF, documento,
  instrutor ou oferta foi aprovado/publicado/criado pelo deploy.

## Revisão em uma tela e e-mail pós-publicação — 05/10/2026

- A tela de aprovação profissional permite conferir e marcar individualmente
  documentos limpos ainda pendentes. A decisão atômica grava a revisão dos
  anexos selecionados, método/fonte reais e verificação interna; anexo ainda
  pendente impede concluir a solicitação. Aprovação de UF e publicação continuam
  decisões humanas independentes.
- Uma publicação manual futura de perfil real cria um aviso transacional por
  e-mail, somente se o perfil estiver efetivamente visível. O envio usa o
  endereço cadastrado, sem CPF/documentos, estado de entrega na decisão de
  publicação, até três tentativas e retry pelo worker. Não há WhatsApp
  automático nem envio retroativo para publicações antigas.
- Migration aditiva `discovery.0011` guarda estado de entrega. Validação local:
  351 testes backend, Django check, migration check e Ruff passaram.
- Deploy de `e72d712` na VPS concluído após backup validado do banco e dos
  documentos privados em `/home/gilmar/backups/instrutorpro/production/`.
  Backend, worker e scheduler ficaram saudáveis; Django check, migration check,
  migration `discovery.0011` e readiness pública passaram. O worker registrou
  as tarefas de envio e retry. Conferência posterior: três perfis reais,
  nenhum publicamente visível, nenhum aviso gerado e nenhuma UF aprovada.
  SMTP está configurado, mas a entrega a um destinatário real só poderá ser
  confirmada após uma publicação manual elegível.

## Complementação documental da verificação real — 04/10/2026

- Solicitação `VERIFIED` permanece imutável. Um instrutor real verificado e não
  publicado pode abrir um novo rascunho de complementação vinculado à decisão
  anterior. O fluxo usa o upload privado existente e mantém CPF protegido.
- O envio exige ao menos um anexo aprovado pelo scanner; bloqueia a elegibilidade
  de publicação enquanto há rascunho ativo e volta a verificação corrente para
  pendente após a submissão. Cada anexo complementar exige revisão individual;
  nova verificação e publicação continuam decisões humanas separadas.
- A tela de status aponta para a complementação; a tela de verificação explica
  CNH/credenciamento, permite anexar e enviar sem reabrir a solicitação concluída.
  Rejeição permite nova tentativa, sem sobrescrever o histórico.
- Migration aditiva `discovery.0010` vincula a nova solicitação à verificação
  anterior. Nenhuma flag de produção, conta ou decisão administrativa foi alterada.
- Validação local: 343 testes backend e 47 frontend passaram; build Angular de
  produção passou com avisos preexistentes de orçamento. Publicação/deploy desta
  fatia ainda não foram executados.

## Correção da mensagem documental no status do instrutor — 02/10/2026

- A tela `Status do cadastro` deixou de afirmar que documentos ainda não foram
  solicitados, pois o upload voluntário pode estar disponível mesmo sem requisito
  territorial obrigatório. Ela encaminha à página de verificação para consultar
  a disponibilidade e os anexos.
- Quando a verificação já está `VERIFIED`, a tela explica que a solicitação
  encerrada não recebe novos anexos e identifica o link como visualização da
  verificação concluída. Nenhum documento, decisão ou gate de publicação mudou.
- Validação local: 46 testes Angular e build de produção passaram; os avisos
  preexistentes de orçamento de bundle/SCSS permanecem.
- Deploy autorizado pelo proprietário em 02/10/2026: o commit `538288b` foi
  enviado a `origin/main` e aplicado por fast-forward na VPS após backup
  validado do PostgreSQL e dos documentos privados (`20261002T175818Z`). Apenas
  o frontend foi reconstruído e substituído; ficou `Healthy`. A rota de status
  e o novo bundle responderam HTTPS 200, o texto corrigido consta no bundle e
  a readiness da API informou `status=ok`, banco `up`. Nenhuma migration, flag,
  decisão ou dado profissional foi alterado.

## Hotfix do Salvar na análise profissional — 02/10/2026

- O erro 403 foi reproduzido nos logs após aprovação humana: o POST em
  `/admin/discovery/professionalverificationrequest/.../change/` ainda oferecido
  na tela tentava editar uma solicitação já `VERIFIED` e era recusado por
  `save_model`. A decisão original permaneceu válida e auditada.
- A página agora permite editar metadados somente ao revisor atribuído durante
  `UNDER_REVIEW`; nos demais estados, mostra campos somente leitura e oculta
  Salvar. Um POST tardio é redirecionado com aviso, sem gravação nem nova decisão.
- Validação local: 342 testes backend no Docker isolado, Ruff check/format,
  Django check e migration check passaram. Nenhuma migration ou alteração de
  permissões é necessária.
- Deploy de produção em 02/10/2026: commit `e81d32b` enviado a `origin/main`
  e aplicado por fast-forward na VPS após backup validado do PostgreSQL e dos
  documentos privados (arquivos `20261002T165802Z`). Nenhuma migration foi
  aplicada; somente o backend foi reconstruído/substituído e ficou `Healthy`.
  Django check e prontidão técnica passaram; readiness HTTPS respondeu com
  banco `up`.
- Conferência somente de leitura do registro afetado: continua `VERIFIED`,
  decidido por `gilmar`, com os cinco eventos auditados preservados. No código
  ativo da VPS, `SAVE_ALLOWED=False` e todos os metadados de revisão estão
  somente leitura. Nenhuma decisão foi refeita durante o smoke.

## Ativação independente de busca e WhatsApp — 01/10/2026

- Autorização explícita do proprietário permite ligar busca pública e contato WhatsApp
  em produção separadamente dos gates financeiros e da aprovação das 27 UFs.
  Os selectors continuam exigindo verificação profissional, publicação manual,
  conta ativa e UF liberada para cada perfil; não houve aprovação automática.
- O registro minimizado de `WHATSAPP_CONTACT_CLICKED` passa a funcionar com
  contato ligado, mesmo com analytics geral desligado. Busca e visualização de
  perfil não são registradas nesse modo; conteúdo de conversa não é armazenado.
- Teste de regressão confirmou que assinatura PRO ativa não altera verificação,
  publicação nem prontidão regulatória. Sem credencial Asaas de produção, preço
  PRO e integração financeira E2E, `REAL_PAYMENTS` e `REAL_PRO_BILLING` seguem
  `false`.
- Validação local: 341 testes backend e 45 testes Angular aprovados; Ruff
  check/format, Django check, migration check e build Angular de produção
  passaram. O build mantém avisos não bloqueantes de orçamento de bundle/SCSS.
- Deploy em 02/10/2026 UTC: commit `d59a5d5` enviado a `origin/main` e aplicado
  por fast-forward na VPS após backup validado do PostgreSQL e dos documentos
  privados (arquivos `20261002T014808Z`). Migration sem pendências, Django
  check e prontidão técnica passaram. Somente o backend foi reconstruído e
  substituído; ficou `Healthy`. A configuração privada anterior foi preservada
  em backup com acesso restrito.
- Flags efetivas: `REAL_MARKETPLACE_SEARCH=true` e `REAL_WHATSAPP_CONTACT=true`;
  `REAL_MARKETPLACE_ANALYTICS=false`, `REAL_PAYMENTS=false` e
  `REAL_PRO_BILLING=false`. A home respondeu 200 e readiness HTTPS informou
  banco `up`. Busca anônima em Brasília/DF retornou zero resultados sem erro;
  o resumo público retornou zero UFs com perfis elegíveis.
- MapTiler resolveu Brasília/DF, Goiânia/GO, São Paulo/SP, Rio de Janeiro/RJ,
  Florianópolis/SC e Manaus/AM. PostGIS 3.5 respondeu. Permanecem 27 análises
  regulatórias, zero aprovadas, zero UFs para publicação e zero instrutores
  reais publicados. Nenhuma aprovação, publicação, cobrança ou contato via
  WhatsApp com um perfil real foi executado.
- A conta existente `gilmar` segue ativa/staff e possui permissões efetivas de
  revisão profissional, documentos privados, RegulatoryReadiness e publicação;
  senha e conta não foram alteradas. As URLs administrativas protegidas
  responderam com redirecionamento para login anônimo; login humano não foi
  exercido. A VPS não possui credencial de produção Asaas nem segredo de webhook;
  o plano PRO segue em rascunho, sem preço e não público. Pagamento/PRO reais
  continuam bloqueados apenas por seus próprios gates.

## Triagem da verificação profissional no Admin — 30/09/2026

- A fila local de solicitações agora sinaliza pendências de documento, liberação antimalware e
  metadados da consulta. A decisão individual reúne evidências privadas autorizadas, método,
  fonte e confirmação humana; registro e aprovação são atômicos.
- A rejeição registra motivo estruturado somente após validar o revisor atribuído. Ações de
  aprovar/rejeitar em massa foram removidas. Nenhuma verificação, UF ou publicação real foi
  aprovada por esta alteração; não houve alteração de senha ou de configuração da VPS.
- Validação local: 339 testes backend no Docker isolado, Ruff check/format, Django check e
  migration check passaram. Nenhuma migration nova foi necessária.
- Deploy em 01/10/2026: o commit `6d82dd3` foi enviado à `origin/main` e aplicado por
  fast-forward na VPS, após backup validado do PostgreSQL e dos documentos privados em
  `/home/gilmar/backups/instrutorpro/production/` (arquivos de `20261001T172419Z`). Apenas o
  backend foi reconstruído/substituído e ficou `Healthy`; migration check e Django check na VPS
  passaram. A rota pública de readiness respondeu `status=ok`, banco `up`.
- Após o deploy, `REAL_PAYMENTS`, `REAL_PRO_BILLING`, `REAL_MARKETPLACE_SEARCH` e
  `REAL_WHATSAPP_CONTACT` continuaram `false`. Havia 0 solicitações profissionais verificadas,
  0 UFs regulatórias aprovadas, 0 UFs liberadas para publicação e 0 perfis reais publicados.
  Um perfil demonstrativo já tinha status de publicação aprovado; nenhuma decisão foi executada
  pelo deploy.

## Validação direta do MVP e sincronização — 29/09/2026

- `origin/main` e VPS sincronizados no commit `b717310` por push e
  fast-forward, após backup validado do banco e dos documentos privados. Apenas
  o backend foi reconstruído e voltou `Healthy`; migrations estavam aplicadas e
  Django check passou.
- Validação local: 336 testes backend, 45 testes Angular, Ruff check/format,
  Django check, migration check sem deriva e build Angular de produção passaram.
  O build mantém avisos não bloqueantes de orçamento de bundle/SCSS.
- Smoke externo após deploy: readiness com banco `up`; geocoding resolveu
  Brasília/DF, Goiânia/GO, São Paulo/SP, Rio de Janeiro/RJ, Florianópolis/SC e
  Manaus/AM. PostGIS 3.5 responde; não foi reproduzida perda de UF.
- Smoke técnico de documentos em produção passou para storage privado, ClamAV
  com assinaturas recentes, arquivo limpo, EICAR, falha fechada, autorização,
  IDOR, backup/restore técnico e remoção dos dados sintéticos. O limite
  configurado é 5 MiB; PDF/JPEG/PNG e limite são cobertos pela suíte.
- A conta existente `gilmar` permanece staff com permissão regulatória. Há 27
  análises `REVIEW_REQUIRED`, zero UFs aprovadas e zero UFs autorizadas para
  publicação. Existem 3 perfis reais, nenhum verificado ou publicado; nenhuma
  aprovação foi executada. Login humano de `gilmar` e jornada de e-mail externa
  não foram exercidos sem credencial/sessão do titular.
- Busca, contato WhatsApp e analytics reais permanecem bloqueados por
  `REAL_MARKETPLACE_SEARCH=false`, `REAL_WHATSAPP_CONTACT=false`,
  `REAL_MARKETPLACE_ANALYTICS=false` e
  `REAL_PRODUCTION_AUTHORIZATION=NOT_GRANTED`; a rota pública de estados
  retornou zero estados com perfis publicados elegíveis.
- Asaas sandbox foi validado somente por testes do adaptador: a VPS não tem
  `PAYMENT_PROVIDER=ASAAS`, `PAYMENT_ENVIRONMENT=sandbox`, chave sandbox nem
  token de webhook configurados. Checkout/customer/subscription/webhook/
  entitlement Asaas E2E seguem bloqueados; o adaptador ainda não está conectado
  ao fluxo público. `REAL_PAYMENTS=false` e `REAL_PRO_BILLING=false` foram
  reconfirmados, sem cobrança.

## Decisão comercial e primeiro adaptador Asaas sandbox — 29/09/2026

- Proprietário alterou o MVP para `MARKETPLACE_MODEL=LEAD_GENERATION`: busca,
  perfil e contato voluntário por WhatsApp; sem pagamento/reserva/comissão de
  aula. FREE permanece independente de PRO e de autorização regulatória.
- Asaas escolhido para investigação/implementação em sandbox. Adaptador local
  isolado usa somente `api-sandbox.asaas.com`, rejeita chave de produção,
  prepara customer, checkout hospedado mensal de cartão e consultas/cancelamento
  de assinatura. Nenhuma API pública ou capability de cobrança foi ativada.
- Webhook PRO, associação de cobrança à assinatura, reconciliação, inadimplência,
  renovação, cancelamento ao fim do período, preço PRO, testes E2E com conta
  Asaas e UI de assinatura ainda estão pendentes. Não chamar esta fatia de
  integração comercial completa. `REAL_PAYMENTS=false` e
  `REAL_PRO_BILLING=false`; nenhuma cobrança ou conta real criada.
- Validação: sete testes isolados do adaptador, Ruff check/format, 336 testes
  backend no Docker isolado e Django check passaram. O ambiente não possui
  credencial/token Asaas sandbox; portanto `SANDBOX_E2E=BLOCKED`, sem
  criação de customer/checkout no Asaas. Volumes e contêineres temporários
  de teste foram removidos, sem tocar os volumes existentes.

## Hotfix de geocodificação Brasília/DF — 28/09/2026

- Causa reproduzida com resposta real sanitizada do MapTiler: Brasília traz
  `subregion.62` com texto `Distrito Federal`, enquanto `region.1474` é
  `Região Centro-Oeste`; o parser anterior não lia `subregion` e devolvia UF vazia.
  Consulta por CEP também traz `place` Brasília após `municipality` Plano Piloto.
- Parser reconhece `region`/`subregion`, códigos estruturados e nomes estaduais
  exatos, normaliza as 27 UFs e não inventa sigla se o contexto for insuficiente
  ou contraditório. API informa `uf_resolution`; frontend exige confirmação
  explícita em caso incompleto. Busca geocodificada envia UF canônica e
  coordenadas ao filtro PostGIS, mantendo o fluxo GPS sem UF.
- Nenhuma migration, alteração de prontidão regulatória, aprovação de UF ou
  publicação de instrutor integra esta fatia. Busca real permanece desligada.
- Validação local: 329 testes backend e 45 Angular aprovados; Ruff,
  build Angular de produção, Django check e migration check passaram.
- Commit `a49aa61` enviado a `origin/main` e aplicado por fast-forward na VPS
  após backup novo validado de PostgreSQL e documentos privados, sem
  restauração, migration ou alteração de volumes. Apenas backend/frontend foram
  reconstruídos e substituídos; ambos ficaram `Healthy`.
- Smoke da API pública: `Brasília`, `Brasília DF`, `Brasília, DF` e CEP
  `70040-010` retornaram `city=Brasília`, `uf=DF` e `uf_resolution=RESOLVED`;
  Goiânia/GO, São Paulo/SP, Rio de Janeiro/RJ, Florianópolis/SC e Manaus/AM
  também retornaram UFs canônicas. HTTPS readiness informou banco `up`, home
  respondeu 200 e serviu o bundle frontend novo; Django check na VPS passou.
- Auditoria após deploy: 27 registros de prontidão, 27 `REVIEW_REQUIRED`,
  0 `APPROVED`, 0 UFs habilitadas para publicação. Busca real, contato real,
  pagamentos, billing PRO e publicação real permaneceram desligados; upload
  documental voluntário permaneceu ligado. Nenhum instrutor foi aprovado
  automaticamente por este hotfix.

## Deploy do painel regulatório por UF — 28/09/2026

- A VPS `179.199.136.4` foi atualizada por fast-forward de `ebd0999` para
  `a1ab4bb`, correspondente a `origin/main` no momento do deploy. As cópias
  locais não rastreadas de `.env.production` foram preservadas.
- Antes da atualização, `scripts/backup-production.sh` gerou e validou o dump
  PostgreSQL e o arquivo de documentos privados em
  `/home/gilmar/backups/instrutorpro/production/`, ambos com SHA-256; não houve
  restauração nem remoção de dados/volumes.
- Backend, worker e scheduler foram reconstruídos e iniciaram; o backend ficou
  `Healthy`. `territories.0005` aparece aplicada e `manage.py check` não encontrou
  problemas. PostgreSQL, Redis e ClamAV estavam saudáveis; gateway e frontend
  permaneciam em execução.
- HTTPS e página inicial responderam 200 com certificado válido; cadastro de
  instrutor, login admin e página de verificação responderam 200. O Admin
  redirecionou anonimamente para login, inclusive na rota de prontidão
  regulatória; a visualização autenticada ainda depende de conferência humana.
  `/api/v1/readiness/` respondeu `status=ok`, banco `up`; a API de verificação
  negou acesso anônimo (403), e o OPTIONS do cadastro respondeu 200.
- Conferência sanitizada no banco: `TOTAL_UFS=27`, `PENDING_UFS=27`,
  `APPROVED_UFS=0`, `PUBLICATION_UFS=0` e permissão de revisão de `gilmar=True`.
  Cadastro real de instrutor, verificação profissional e upload documental
  permaneceram habilitados; `REAL_MARKETPLACE_SEARCH`, contato real por WhatsApp,
  pagamentos e cobrança PRO permaneceram desabilitados.
- MapTiler respondeu a consulta pública de Brasília, mas a API retornou `uf`
  vazia nesse resultado. A integração está acessível, não homologada para todos
  os casos; busca pública não foi ativada. Não houve criação de conta, envio de
  documento pessoal, aprovação de UF ou publicação de instrutor no smoke.

## Painel regulatório por UF — implementação local e deploy concluído — 28/09/2026

- O Admin ganhou órgão da fonte, data da consulta, evidências e histórico desses
  campos, além de decisões individuais de manter em revisão e bloquear UF. A
  aprovação humana requer os campos preenchidos; a policy de publicação falha
  fechada se faltarem. A decisão de bloqueio revoga apenas a UF correspondente.
- Migration aditiva `territories.0005` aplicada na VPS no commit `a1ab4bb`;
  acesso SSH por chave dedicado foi configurado sem alterar senhas ou substituir
  as chaves já autorizadas.
- Cadastro e upload nacionais permanecem independentes de prontidão regulatória;
  busca e publicação real só retornam profissionais individualmente elegíveis em
  UFs explicitamente aprovadas. Nenhuma UF foi aprovada nesta fatia.
- Validação local: 290 testes backend e 42 frontend aprovados; Ruff, Django check,
  migration check e build Angular de produção passaram. Permanecem dois avisos
  preexistentes de orçamento de bundle/SCSS no build, sem falha.

## Triagem regulatória nacional e confirmação humana — 28/09/2026

- Inventário preliminar de 27 UFs documentado em `REGULATORY_READINESS_27_UFS.md`;
  nenhuma UF foi aprovada por essa triagem. Fontes incompletas e vigência não confirmada
  permanecem `NEEDS_REVIEW` no relatório (`REVIEW_REQUIRED` no banco).
- Painel administrativo e histórico de decisões preparados para revisão por UF. A
  conta existente `gilmar` é o responsável designado. Em 28/09, a VPS recebeu o
  commit `ebd0999`; o backend ficou saudável, `manage.py check` passou, a migration
  `territories.0004` estava aplicada e `/api/v1/readiness/` retornou banco `up`.
  Backup do banco e do volume documental foi validado antes da atualização.
- A carga controlada criou 27 registros `REVIEW_REQUIRED` e aprovou zero UFs.
  A conta administrativa existente `gilmar` recebeu as três permissões de revisão,
  sem criação de conta ou alteração de senha. Conferência posterior no banco:
  `TOTAL=27`, `PENDING=27`, `APPROVED=0`, `PUBLICATION_UFS=0` e
  `GILMAR_REVIEW_PERMISSION=True`. A visualização humana do painel ainda deve ser
  conferida; nenhuma revisão de vigência ou aprovação humana foi executada.
- Registro `APPROVED` requer decisão explícita de `gilmar`, fonte/norma,
  vigência e justificativa; autorização individual e publicação seguem gates separados.
- Validação local: 289 testes backend aprovados; 69 testes focados repetidos após
  reforço do gate de vigência, Ruff lint/formatação, Django check e verificação
  de migration aprovados. Busca real, pagamentos e publicação real permanecem
  desligados; não confundir cadastro da análise com autorização profissional.

- Atualizado em: **2026-09-28**
- Versão documental: **4.12**
- Código-fonte: **Upload privado voluntário ativo; triagem regulatória das 27 UFs implantada, pendente de revisão humana**

## Hotfix de upload voluntário — 27/09/2026

- Decisão expressa do proprietário: upload voluntário nas 27 UFs sem inventar requisitos
  estaduais, retenção legal ou aprovação de privacidade; decisão registrada em
  `PROFESSIONAL_DOCUMENT_UPLOAD_HOTFIX.md` e substitui o gate jurídico anterior de ativação.
- Tipo documental genérico e requisito estadual separados; migration 0012 aditiva.
  UI oferece anexos com zero requisitos e mostra estados de segurança amigáveis.
  Submissão bloqueia todo arquivo não-CLEAN; admin/download exigem revisor responsável.
- Backend final: 283 testes aprovados; Angular: 42 aprovados e build de produção PASS
  com avisos de budget existentes. Ruff lint/format, Django check, migration check e
  sintaxe shell aprovados. OpenAPI gera saída válida, mas reporta 24 rotas com serializers
  ausentes preexistentes fora do hotfix; não declarar documentação global sem pendências.
- Script de deploy com backup, smoke real, ativação condicional e restauração de flags em falha.
  SSH automático indisponível. A primeira execução assistida na VPS parou no smoke antes
  da ativação: EICAR concatenado a um cabeçalho PDF artificial não foi detectado.
  Diagnóstico em memória confirmou que PDF com anexo EICAR real é `BLOCKED`;
  fixture do smoke corrigida para esse formato. Reexecução assistida do commit
  `0c51b99638323efe888ec7de5093643a05834273` passou nos controles de
  storage privado, scanner, formatos, autorização, IDOR, backup/restauração isolada
  e limpeza técnica. Readiness retornou `status=ok`, banco `up`, e o script encerrou
  com `DOCUMENT_UPLOAD_PRODUCTION_STATUS=ENABLED`. Verificação e publicação
  automáticas continuam desligadas. Não houve aprovação de retenção/privacidade.

## Feedback do login público — 27/09/2026

- captura de produção confirmou POST do login com HTTP 400 e resposta genérica
  `Credenciais inválidas`, sem aviso visível no formulário;
- login passa a usar signals para feedback assíncrono, exibe aviso acessível com orientação
  para recuperação, estado `Entrando…`, validação local e bloqueio de envio duplicado;
- excesso de tentativas e falhas de rede/servidor recebem mensagens próprias e seguras,
  sem revelar existência/estado da conta nem reproduzir detalhes internos da API;
- cinco testes DOM no modo zoneless cobrem erro assíncrono, validação, throttling,
  indisponibilidade, retry e redirecionamento; suíte Angular completa: `41 SUCCESS`;
  build de produção aprovado com os dois avisos de budget preexistentes;
- sem alteração de backend, senha, conta, autorização ou migrations. Deploy pendente;
  recuperação por e-mail continua dependente de SMTP confirmado na VPS.

## Correções de homologação 8O — 27/09/2026

- evidências fornecidas pelo proprietário mostram deploy de `9cffbc0`, readiness aprovado,
  volume documental persistente e backup validado; restauração isolada de arquivo técnico passou
  com hash idêntico e limpeza dos arquivos técnicos, sem sobrescrever documentos existentes;
- scanner real respondeu PONG, carregou daily `28136` de 27/09 e passou scan limpo, EICAR e
  indisponibilidade simulada, somente em memória; isso não homologa o pipeline completo;
- FreshClam não resolvia DNS porque só tinha rede interna; correção persistente adiciona a rede
  de saída ao scanner, sem publicar portas e sem montar documentos nele;
- `/documents`, `/uploads` e `/private` responderam HTTP 200 `text/html`, compatível com fallback
  Angular, sem prova de exposição de arquivo. nginx passa a negar esses prefixos com 404;
- backend ainda precisa de `CLAMD_HOST`; acesso autorizado/IDOR, pipeline real, retenção na VPS,
  persistência após recriação e smoke final continuam pendentes. Não ativar uploads;
- correções de configuração desta seção ainda precisam ser implantadas e retestadas na VPS.
- validação local das correções: três testes de regressão e Ruff passaram; nginx 1.28 validou
  a sintaxe da configuração em container isolado. CI executa os três testes em cada release.

## Fatia 8O — homologação técnica em andamento (23/09/2026)

- commit `12eb56a` enviado a `origin/main`; CI inicial apontou somente formatação antiga; o commit
  `df6532d` corrigiu a formatação e adicionou Angular tests ao CI; backend e frontend passaram;
- inicialmente SSH de linha de comando reconheceu a chave de host, mas a VPS recusou autenticação por chave;
  backup, pull, migrations, ClamAV, EICAR, restore e smoke não foram executados na VPS;
- engine de retenção local agora exige política versionada, ativa e aprovada, suporta agendamento
  e legal hold e mantém descarte real inerte na ausência de política de produção; três testes com
  dados técnicos/sintéticos passaram, incluindo falha de storage e retry, além de 253 testes
  backend completos em 27/09; Ruff, Django check e migration check passaram;
- operações POST/DELETE de documentos separadas para eliminar colisões de operationId; a geração
  OpenAPI ainda apresenta erros preexistentes em outras APIs, sem afirmar contrato global limpo;
- autenticação SSH por chave novamente recusada em 27/09; deploy posteriormente executado pelo
  proprietário no terminal aberto, conforme evidências acima.
- rascunho técnico para revisão jurídica em
  `docs/PRIVACY_PROFESSIONAL_DOCUMENTS_REVIEW_DRAFT.md`; nenhuma Política publicada mudou;
- `REAL_DOCUMENT_UPLOADS=false` permanece obrigatório até o relatório final de homologação.

## Fatia 8N — upload documental profissional (23/09/2026)

- infraestrutura de upload privado vinculada ao rascunho de verificação, com requisitos versionados,
  aprovados e filtrados por UF/categoria, sem presumir regras estaduais;
- validação de arquivo, quarentena, integração clamd de falha fechada, promoção somente após
  resultado limpo, snapshot na submissão, download autenticado e auditoria;
- campos de retenção e suspensão de descarte criados sem estabelecer prazo jurídico nem executar
  eliminação automática; backup do volume privado foi incluído no script, pendente de teste de
  restauração em ambiente real;
- acesso direto às rotas de arquivo bloqueado no nginx; não há URL pública fornecida pela API;
- ativação continua **bloqueada** por homologação do scanner, volume/backup/restauração,
  política de retenção e versão jurídica da Política de Privacidade;
- validação local: 250 testes backend, 13 testes específicos de upload, Ruff, Django check,
  migrations e build Angular passaram; o ChromeHeadless não iniciou no Docker local por restrição
  de namespace, então a suíte Angular permanece pendente neste ambiente;
- detalhes, gates e rollback em `docs/PROFESSIONAL_DOCUMENT_UPLOAD_FATIA_8N.md`.

## Localização pt-BR do painel administrativo (22/09/2026)

- `LANGUAGE_CODE=pt-br` permanece como idioma global da aplicação;
- aplicativos, módulos, filas e permissões próprios do Django Admin receberam nomes oficiais em
  português do Brasil, eliminando os rótulos automáticos em inglês do menu e dos breadcrumbs;
- códigos técnicos, nomes de campos de API e valores internos de enumeração não foram traduzidos,
  preservando contratos e regras de negócio;
- migrations alteram somente metadados (`Meta options`), sem modificar ou apagar dados;
- páginas públicas já estavam em português; a correção concentra-se na navegação administrativa;
- validação local: teste direcionado do Admin com `20 passed`, suíte backend completa com
  `237 passed`, Ruff aprovado, Django check sem erros e nenhuma migration pendente;
- deploy ainda é necessário antes de considerar a tradução ativa em produção.

## Admin de produção — autenticação simples e painel operacional (22/09/2026)

- decisão do proprietário remove OTP somente do `/admin/`; logins públicos permanecem inalterados;
- autenticação administrativa aceita usuário ou e-mail único + senha e mantém conta ativa/staff,
  Axes, CSRF, HTTPS, cookies seguros, rotação de sessão e expiração de 30 minutos;
- login bem-sucedido, falha genérica sem identificador e logout geram `AuditEvent` sem credenciais;
- painel exibe contagens reais e atalhos de instrutores, fila profissional e auditoria, sem menu de
  pagamentos enquanto `REAL_PAYMENTS=false`;
- fila apresenta nome, UF, cidade, data, status, revisor e ação, mantendo CPF mascarado e consulta
  excepcional autorizada/auditada;
- grupos de menor privilégio são preparados por comando idempotente, sem criar usuários;
- associação a grupo é explícita, exige conta staff ativa, não concede superusuário e gera auditoria;
- `VERIFIED` continua distinto de `PUBLISHED`; uploads, publicação automática, pagamentos e Pro
  permanecem bloqueados;
- validação local: Django check e migration check passaram, Ruff passou e suíte backend completa
  encerrou com `236 passed`; Angular não foi alterado e não exige rebuild nesta fatia;
- deploy e smoke de produção ainda são obrigatórios antes de `ADMIN_PRODUCTION_READY=YES`.

## Fatia 8M — solicitação e revisão profissional real (22/09/2026)

- instrutor autenticado possui página privada para informar CPF e enviar solicitação idempotente;
- CPF validado, cifrado em repouso e deduplicado por índice cego HMAC com chave separada; APIs,
  listagens e logs recebem somente máscara/metadados;
- fila administrativa dedicada ordena envios antigos, bloqueia criação/exclusão manual e exige
  permissão, MFA, atribuição de revisor, método, fonte e data antes da aprovação;
- decisão é transacional e auditada; rejeição usa motivo estruturado e mensagem segura;
- `VERIFIED` não aprova nem publica o perfil. Documentos, busca, publicação, pagamentos e Pro
  continuam bloqueados por capabilities independentes;
- gate `PROFESSIONAL_VERIFICATION_MODE=PRODUCTION` exige capability e as duas chaves de proteção;
- telas privadas deixam de manter carregamento infinito quando a sessão autenticada não pertence a
  um instrutor e orientam nova entrada com a conta profissional;
- migrations são aditivas; rollback operacional desliga o gate e preserva dados/histórico;
- validação local: Ruff e migrations passaram; suíte backend completa com `226 passed`; Angular
  com `36 SUCCESS`; build de produção passou com os dois avisos de budget já conhecidos.

## Fatia 8L — cadastro nacional de instrutor em produção (21/09/2026)

- decisão do proprietário separa o cadastro real de instrutor do antigo marcador global de piloto:
  `INSTRUCTOR_REGISTRATION_MODE=PRODUCTION` autoriza somente conta, dados pessoais e onboarding;
- `REAL_PRODUCTION_AUTHORIZATION` pode permanecer `NOT_GRANTED`, mantendo busca, contato,
  analytics, documentos, publicação automática, pagamentos e Pro bloqueados;
- conta nasce ativa; perfil nasce `NOT_STARTED` para verificação e `UNPUBLISHED` para publicação;
  nenhuma UF recebe `RegulatoryReadiness` por consequência do cadastro;
- onboarding aceita as 27 UFs, categorias A–E, transmissão, WhatsApp, oferta, veículo e área pública.
  Cidade/UF são persistidas mesmo sem MapTiler; coordenada e autorização pública ficam opcionais;
- upload real de documento/foto continua bloqueado até storage privado e antimalware homologados;
- recuperação segura de senha foi implementada com resposta antienumeração, token de uso único,
  senha mínima de dez caracteres, auditoria e rate limit. Sem SMTP real o endpoint falha fechado
  antes de gerar token; a prontidão exige configuração transacional confirmada na VPS;
- o onboarding real bloqueia envio de campos obrigatórios inválidos, explicita o formato brasileiro
  do WhatsApp e apresenta por campo os detalhes de validação retornados pela API, sem reduzir a
  falha à mensagem genérica `Entrada inválida`;
- pendências jurídicas de DPO e retenção permanecem registradas e não são apresentadas como `PASS`.
  Analytics conserva descarte aprovado em 90 dias; prazos ainda não decididos não foram inventados;
- especificação e matriz operacional: `docs/INSTRUCTOR_REGISTRATION_PRODUCTION_FATIA_8L.md`.
- validação local: backend `219 passed`; cenários dirigidos `10 passed`; Angular `32 SUCCESS`;
  build de produção, Ruff, Django check e migration check passaram. Deploy/smoke ainda dependem da
  inspeção segura da VPS e da confirmação de e-mail transacional.

## Fatia 7 — Meus dados e privacidade (16/09/2026)

- Área autenticada permite ao titular consultar e alterar somente dados cadastrais e comerciais
  explicitamente permitidos. E-mail, papéis, plano e estados críticos permanecem fora do contrato.
- Alteração de categoria, transmissão ou veículo do instrutor falha fechada: invalida a verificação,
  retira a publicação e cria nova pendência e auditoria pelo serviço de domínio.
- Solicitações de acesso, correção, exclusão, portabilidade, revogação de consentimento e informação
  são registradas em `PrivacyRequest`; pedido de exclusão não apaga automaticamente conta, auditoria
  ou evidência sujeita a retenção.
- Política pública versionada identifica apenas `InstrutorProCNH`, CNPJ confirmado
  `10.280.826/0001-05` e canal `focusgtba@gmail.com`; razão social, endereço, representante e
  encarregado não confirmados não foram inventados.
- Admin de contas e pessoas usa busca mínima, estados críticos somente leitura e auditoria das
  alterações permitidas. Identidades externas e papéis não podem ser editados por esse backoffice.
- Esta implementação não concede autorização para usuários ou dados reais. `OPEN-004`,
  `OPEN-007`, `OPEN-008`, políticas/contratos e demais gates de produção continuam bloqueantes.

## Fatia 6 — domínio preparado localmente (14/09/2026)

- Autorização humana limitada: configurar HTTPS e www preservando IP e Gestor.
- Certificado separado da VPS para domínio e www válido até 13/12/2026. O segundo
  dry-run passou para ambos; a primeira falha "No such challenge" não teve causa determinada.
  Execução automática futura ainda não comprovada.
- Virtual hosts novos mantêm intactos os blocos do IP; ACME HTTP, Admin limitado e rotas
  do Gestor preservados. www redireciona com caminho/query para o domínio canônico.
- Teste isolado com Nginx 1.28, certificados fictícios e upstreams mock em
  `scripts/test-gateway-domain.sh`: PASS (sintaxe, IP/domínio, rotas mock, ACME,
  redirects com query e reload). Nunca executar esse script no gateway ativo.
- Gateway aplicado na VPS em 15/09/2026 após autorização humana para recriar somente
  `instrutorpro-gateway-1`; nenhum outro container, migration, segredo ou flag real foi alterado.
  O bind mount recebeu SHA-256 `0e51f07db4e56b5d7e5fe3dd6e1ea0985c559fc07d6a2fe2629fcf501254ded7`
  e `nginx -t` passou antes da ativação.
- Validação externa sem bypass TLS: domínio `200`, www `301` para o domínio canônico,
  caminho/query preservados, Gestor `307`, licenses `404` (conectividade, não aceite
  funcional), IP `200` e Gestor pelo IP `307`; todos com `ssl_verify_result=0`.
- As allowlists Django da composição DEMO foram atualizadas na VPS em 16/09/2026 para
  domínio, www e IP após backup protegido de `.env.demo`. Somente
  `instrutorpro-backend-1` foi recriado, com autorização humana; nenhum outro serviço ou
  volume foi alterado. A janela não foi medida e não deve ser declarada como zero downtime.
- Após a recriação, readiness, geocodificação de Porto Alegre e tile MapTiler responderam
  `200`; o backend confirmou domínio/www em `ALLOWED_HOSTS`, origens HTTPS em CORS/CSRF e
  chave MapTiler configurada sem expor seu valor. Essa evidência valida a DEMO técnica e
  não comprova requisitos contratuais do provider nem autoriza dados reais.
- Perfil `compose.production.yaml`, exemplo fail-closed e validador técnico foram preparados
  localmente em 16/09/2026. Mantêm volumes existentes, settings PRODUCTION, MFA e HTTPS;
  dados sintéticos e todas as flags reais ficam desligados. A chave MapTiler de produção e
  demais segredos devem ser inseridos diretamente pelo operador na VPS. O perfil ainda não
  foi aplicado e não constitui autorização para dados reais.
- Validação local: Compose config passou; 11 testes SaaS/produção passaram; o validador
  rejeitou placeholders e, com valores exclusivamente fictícios, concluiu os 12 gates técnicos
  com PASS e `REAL_PRODUCTION_AUTHORIZATION=NOT_GRANTED`. `check --deploy` manteve 12 avisos
  OpenAPI já conhecidos e HSTS preload deliberadamente desligado. A validação também encontrou
  e corrigiu o escaping do formatter JSON de logs, que antes impedia a inicialização do Django.

## Integração operacional preservada no gateway (11/09/2026)

- O gateway permanece somente na rede `instrutorpro_public`. A API do Gestor já está conectada
  a essa rede com alias `gestor_reposicao_api`; o alias pertence à API, nunca ao gateway.
- As rotas preexistentes `/gestao`, `/api/v1/licenses` e `/api/v1/sync` continuam encaminhadas ao
  Gestor Reposição sem publicar banco ou Redis.
- A conexão foi validada ao vivo sem recriar containers: Instrutor respondeu `200`, Gestor `307` e
  Licenses `404`, sem `502`.
- Antes de recriar o gateway, validar que a API do Gestor continua na rede compartilhada com
  esse alias. A persistência da conexão da API deve ser conferida no projeto do Gestor.
- Inspeção posterior confirmou API `172.18.0.5`, gateway `172.18.0.4` e `EXTRA_HOSTS=[]`.
  A ligação adicional do gateway à rede privada do Gestor era desnecessária e foi removida do
  Compose; nenhuma alteração em containers em execução foi feita nesta correção local.

## Consolidação de produto em 2026-08-19

Foram incorporados à documentação, sem liberar código nem remover gates existentes: mapa/lista de instrutores, demanda declarada por alunos, agregados geográficos de demanda, matching determinístico, captação de instrutores autorizados, funil de candidatos, registro de verificação oficial por fonte documentada/manual e Academia do Instrutor como hub orientativo. Novas decisões `ADR-021–026`, questões `OPEN-015–019` e riscos `R-026–030` foram registrados.

A fase continua **M0**, com `GOV-001/OPEN-001` concluído. Esta consolidação não autoriza scraping de portais públicos, IA no caminho crítico, publicação sem elegibilidade nem implementação antes dos gates.

## Fase atual

**INSTRUTORPROCNH DEMO 01 concluída.** O frontend contém experiência visual navegável e mobile-first apenas com fixtures sintéticas. CODEX 01, 02A e 02B permanecem preservados; CODEX 02C está suspenso e não deve ser retomado sem autorização explícita. Capacidades reguladas, usuários reais, perfis e publicação continuam condicionados aos respectivos gates.

## Últimas atividades concluídas

Fatia 4 concluída localmente em 11/09/2026: landing pública, busca por localidade, filtros por
transmissão/veículo/preço, ordenação por distância/preço, cartão e perfil passaram a usar oferta
comercial tipada em BRL e duração. Nota fictícia deixou de ser exposta. O contato profissional é
privado e normalizado; o endpoint auditado registra clique deduplicado por sessão/instrutor/hora e
retorna somente a URL `wa.me`, sem enviar mensagem automaticamente. Métricas mensais do painel
derivam de eventos reais da aplicação e mostram zero quando não há evento. A implementação mantém
somente categoria B e dados sintéticos conforme `OPEN-002`, não implementa pagamentos ou mapa de
demanda e não altera a VPS. Migration nova, Ruff, 123 testes backend, 14 testes frontend e build
Angular aprovados; validação funcional local no navegador deve constar na evidência final da fatia.

Profissionalização local iniciada em 02/09/2026: branding público corrigido para
`InstrutorProCNH`; header e footer deixaram de apresentar a experiência como demo; a landing passou
a oferecer pesquisa principal por cidade/bairro/CEP, CTA de instrutor e geolocalização voluntária
somente após clique, encaminhando ao mapa já conectado ao backend/PostGIS. Dados sintéticos,
fixtures e endpoints de teste permanecem identificados e isolados; esta fatia não ativa cadastro,
publicação ou dados reais e não foi implantada na VPS. Backend com 109 testes, Ruff, Django check e
build Angular aprovados; validação HTTP local de landing/readiness respondeu 200. A validação visual
completa dos fluxos autorizados continua pendente e não deve ser inferida deste registro.

Marca humana atualizada em 02/09/2026 de `InstrutorPro` para `InstrutorProCNH`, incluindo novo
logotipo vetorial, interface, títulos de página, acessibilidade, Admin, nome exibido no MFA,
OpenAPI e documentação. Identificadores técnicos legados em banco, containers, paths, nomes de
pacotes/classes e repositório permanecem inalterados para preservar compatibilidade operacional.
Esta alteração de apresentação não equivale a pesquisa, disponibilidade ou registro jurídico da
marca; `OPEN-012` continua aplicável.

Implementação do complemento do dossiê sintético concluída em 31/08/2026: credencial de instrutor registra UF,
identificador privado, emissão, validade, fonte, resultado, revisor, motivo e auditoria. Foto de
perfil é evidência independente, entra em quarentena com autorização de publicação e notice
versionado separados, e somente pode ser aprovada por revisor autorizado distinto. O Admin usa
acesso privado auditado; busca/lista expõem a foto apenas quando foto e publicação sintética estão
aprovadas, e exibem claims derivados somente de evidência limpa, aprovada e vigente. A fixture
visual é uma pessoa inteiramente sintética gerada para demonstração. Upload, revisão e publicação
de dados reais, base legal/notice definitivo e integrações oficiais continuam bloqueados.
Onboarding, etapa documental, mapa/lista e perfil público foram comprovados visualmente no
navegador. O aceite visual do backoffice permanece **PENDENTE**: a sessão sintética disponível não
possui autenticação administrativa/MFA, e permissões temporárias de modelo não contornaram esse
controle; elas foram integralmente revogadas após o teste. Portanto, o requisito visual completo do
item 13 ainda não deve ser considerado aceito.

`BCR-06/CERTIFICADO` resolvido em 30/08/2026: o certificado ECDSA da Let's Encrypt para
`179.199.136.4`, válido de 29/08/2026 a 04/09/2026, teve cadeia externa validada e renovação
simulada aprovada pelo Certbot às 06:30:47 UTC. O serviço `certbot-renew` já avalia renovação
a cada 12 horas, com webroot compartilhado, e o gateway Nginx recarrega a cada 6 horas.
HTTP→HTTPS, frontend, API, health, readiness, Admin, cookie CSRF `Secure` e headers de
segurança foram comprovados. Nenhum certificado foi forçado ou reinstalado; os demais
bloqueadores de produção permanecem independentes.

Verificação de deploy corrigida em 30/08/2026: o readiness interno executado pelo container frontend
passa a declarar `X-Forwarded-Proto: https`, evitando que o redirecionamento seguro `301` seja tratado
como indisponibilidade. A exigência de HTTPS permanece ativa e não foi afrouxada.

Mapa agregado nacional refinado em 30/08/2026: a ilustração conceitual foi substituída pela malha
local das 27 UFs obtida do IBGE, com seleção estadual e detalhamento por cidade. Somente RS, SC, SP,
RJ e ES recebem marcadores e contagens sintéticas; as demais UFs ficam neutras, sem sugerir ativação
operacional. A seleção de uma UF ativa encaminha à busca local de instrutores com a capital demo já
informada; o mapa de destino consulta somente publicações sintéticas. Nenhuma demanda ou localização
individual real foi adicionada.

Experiência visual da busca de instrutores refinada em 30/08/2026: entrada por cidade/bairro/CEP,
mapa Leaflet amplo, marcadores identificáveis, filtros, painel de resultados e alternância móvel
mapa/lista. A interface preserva identidade InstrutorProCNH, minimização sem GPS automático e dados
exclusivamente sintéticos; não altera elegibilidade, provider de produção, publicação real ou os
gates de `OPEN-007`.

Exceção temporária do painel autorizada em 29/08/2026 para avaliação por sócios e colaboradores:
MFA pode ser desativado somente no servidor de demonstração com dados sintéticos por flag segura por
padrão. Senha, staff, permissões explícitas, Axes, sessão curta e auditoria permanecem. Enquanto a
flag estiver desativada, `ADMIN-PROD-01` continua `NOT READY` e nenhum dado/profissional/publicação
real é permitido; reativar MFA é condição anterior a produção.

Configuração administrativa GOV-004 implementada em 29/08/2026 no app `organizations`:
`PlatformOrganization` singleton, CNPJ validado/normalizado, estados
`INCOMPLETE/PENDING_VALIDATION/VALIDATED`, edição e validação com permissões separadas,
lock/versão, auditoria redigida e Django Admin reutilizado. Migration
`organizations/0002_platformorganization.py` aplicada somente no banco local. Nenhum
dado real foi semeado, nenhum endpoint público, upload, deploy ou liberação de BCR-02 foi
criado. Foram aprovados 11 testes direcionados e 83 testes backend completos.

Dados organizacionais adicionais declarados pelo responsável humano em 29/08/2026:
razão social `FOCUS INFORMATICA E CELULAR LTDA`, endereço parcial
`RUA MATO GROSSO 1660`, representante parcial `Gilmar Cesar` e contato operacional
`64996765431`. O registro é documental e mantém pendentes comprovação, endereço completo,
nome civil/qualidade de representação e homologação do canal; nenhum dado foi gravado no
banco ou exposto pelo painel administrativo.

Cotação controlada para Encarregado/DPO externo enviada em 29/08/2026 a Seusdados,
Omnisblue e Global Data Solutions, com mensagem uniforme e matriz de avaliação. Os três
envios foram confirmados; as propostas continuam pendentes. Nenhum fornecedor foi
escolhido, nenhum contrato/custo foi aceito e nenhum dado de instrutor foi compartilhado.

Modelo de Encarregado/DPO externo independente aprovado em 29/08/2026, sem seleção de
fornecedor, contrato ou cobrança. A identidade e o ato formal continuam pendentes antes
de dados reais.

Exigência de Encarregado/DPO formal antes de dados reais aprovada em 29/08/2026. O canal
`focusgtba@gmail.com` permanece válido para contato inicial, mas não é nomeação. Pessoa ou
serviço, ato formal, substituição, recursos e avaliação de conflito continuam pendentes;
nenhum DPO foi inventado ou considerado designado.

Procedimento `GOV002-RS-INSTRUCTOR` aprovado por decisão humana em 29/08/2026 somente
para M1 Porto Alegre/categoria B: consulta manual voluntária sem upload, revalidação a
cada 24 horas e tolerância de 72 horas para indisponibilidade. A linha passou a
`APPROVED`; as outras 19 permanecem inalteradas. O tabletop GOV-003 foi repetido e obteve
`PASS` no mesmo recorte, com self-review/conflito ainda exigindo pessoa distinta. Isso não
libera dados reais ou implementação.

Operador/controlador do M1 registrado em 29/08/2026 como pessoa jurídica, CNPJ
`10.280.826/0001-05`, e canal inicial de privacidade `focusgtba@gmail.com`. A decisão não
comprova as declarações posteriores de razão social, representação e endereço parcial,
nem designa DPO. O caminho mínimo RS foi
reduzido: consulta manual oficial pode dispensar upload/storage/scanner no primeiro
instrutor se o procedimento proposto for aprovado; segundo revisor só é bloqueante para
self-review, relação ou conflito. Nenhum dado real ou código foi ativado.

Prontidão pré-produção M1 inicialmente avaliada em 29/08/2026 com resultado **`NOT READY`**. A análise
focada em Porto Alegre/RS consolidou seis bloqueadores reais: regra/operação RS,
operador/LGPD/jurídico, segregação, cadastro/documentos reais, MapTiler contratual e
plataforma segura de produção. A fonte oficial do DetranRS confirma categoria B e lista
de IA autorizados; naquela avaliação `GOV002-RS-INSTRUCTOR` ainda não tinha aprovação
nominal. A decisão posterior registrada acima substitui esse bloqueio, sem ativar dado
real, código, migration, deploy ou integração.

Tabletop obrigatório `GOV-003` do piloto M1 executado documentalmente em 29/08/2026,
com Gilmar Cesar Alves atuando separadamente nas cinco funções provisórias e Codex apenas
como facilitador/relator. O cenário e suas variantes usaram somente evidência sintética.
Resultado: **`FAIL`**. Permanecem abertos F-001 a F-006: linha `RS/INSTRUCTOR` não
aprovada, falta de revisor independente, validação jurídica externa, storage/scanner real,
tolerância da fonte e comprovação organizacional/DPO. Nenhuma elegibilidade, revisão ou publicação
real foi liberada.

Decisões territoriais e de provider do M1 registradas em 29/08/2026: Porto Alegre/RS é
o primeiro território operacional controlado, sem limitar a arquitetura nacional;
MapTiler Cloud Flex é o provider preferencial condicionado, com PostGIS como fonte de
verdade, geocoding no backend, Leaflet, sem GPS e fallback de busca/lista por Porto Alegre.
`OPEN-007` não é mais uma escolha genérica, mas produção permanece bloqueada até aceite
do plano/DPA, subprocessadores, países/transferência, retenção da consulta, endpoint
europeu, chaves/limites e testes. Nenhuma integração ou dado real foi ativado.

Gate LGPD mínimo da busca de instrutores documentado em 29/08/2026. Foram aprovados
somente a busca com dados sintéticos e o desenho minimizado: pesquisa sem login por
cidade/bairro/CEP explícito, sem GPS automático, histórico individual, saúde ou residência
pública; localização de serviço do instrutor permanece separada, granular, auditada e
revogável. O ROPA mínimo foi registrado. Busca e profissional reais continuam bloqueados
por LIA/RIPD, organização/canal, retenção, provider, segurança, elegibilidade e gates
regulatórios/operacionais; `OPEN-007` não foi fechado.

Revisão documental controlada de `GOV-002` registrada em 29/08/2026 para RS, SC, SP,
RJ e ES. A autorização humana permitiu registrar somente decisões suficientemente
sustentadas, mas não aprovou nominalmente nenhuma linha nem selecionou opções da análise
anterior. Resultado conservador: 0 linhas `APPROVED`, 16 permanecem
`HUMAN_REVIEW_REQUIRED` e 4 permanecem `RESEARCH_REQUIRED`. `OPEN-002` continua aberto;
nenhuma elegibilidade, publicação, pessoa real, integração ou funcionalidade foi liberada.

Deploy da demo no Ubuntu preparado em 24/08/2026: Compose isolado do ambiente local,
frontend Angular estático em Nginx, Django/Gunicorn, redes privadas para PostGIS/Redis,
volumes persistentes, configuração não versionada, backup pré-deploy, atualização
fast-forward e smoke/readiness. O ambiente continua exclusivamente sintético; domínio,
TLS e instalação no servidor dependem dos dados/acesso do operador.

CODEX 02E executado em 24/08/2026 com dados exclusivamente sintéticos: serviços
transacionais para submissão, revisão, verificação, publicação, suspensão/despublicação e
autorização/revogação da localização; proteção contra alteração direta; ações do Admin
ligadas aos serviços; onboarding Angular mobile-first em cinco etapas e timeline pós-envio.
O perfil termina enviado e não publicado. CODEX 02C permanece suspenso.

Interface e Admin padronizados para português do Brasil em 24/08/2026. PrimeNG/PrimeUI, que não era usado por componentes da demo e exibia aviso de licença sem chave, foi removido legitimamente; Angular, PrimeIcons, Leaflet e estilos próprios permanecem. Admin recebeu identidade InstrutorProCNH, nomes e colunas em português e booleanos Sim/Não. Migration `discovery/0003` altera somente metadados de apresentação.

CODEX 02D executado em 24/08/2026 com dados exclusivamente sintéticos: perfil, área pública, autorização, verificação SYNTHETIC, publicação auditada, policy central, Admin protegido e mapa elegível. CODEX 02C permanece suspenso.

MAPA ONLINE 01 executado em 24/08/2026: módulo `discovery`, migration nova, 11 pontos públicos sintéticos nas cinco UFs, geocoder local, busca espacial PostGIS e mapa Leaflet/OpenStreetMap sincronizado com lista e perfil demo. Nenhuma localização automática, pessoa real, elegibilidade, publicação ou CODEX 02C foi implementado.

INSTRUTORPROCNH DEMO 01 executada em 24/08/2026: landing InstrutorProCNH, jornada do aluno, descoberta de serviços, mapa/lista e perfil de instrutores fictícios, solicitação visual, matching mock, demanda fictícia, clínicas/exames, entrada profissional, dashboard do instrutor e mapa agregado de demanda. Dados ficam isolados em providers `Demo*`; não houve alteração de backend, migration, login, API, dado real ou integração. Build Angular aprovado, 7 testes frontend aprovados em Chrome Headless e 50 testes backend preservados.

CODEX 02B executado em 24/08/2026: `Account` recebeu estados `ACTIVE/BLOCKED/DEACTIVATED`, coerência com `is_active`, última mudança e versão; serviços internos autorizados implementam ativação, bloqueio e desativação sem exclusão; lock/versão/constraint resolvem concorrência e desativação é terminal nesta fatia. Migration `accounts/0003_alter_account_options_account_lifecycle_changed_at_and_more.py` aplicada. Foram aprovados 50 testes, sem endpoint público ou dados reais.

CODEX 02A executado em 24/08/2026: `RoleAssignment` passou a preservar ciclos de concessão/revogação com atores e motivos; policy exige `people.manage_role_assignments`; comandos transacionais usam lock da pessoa e constraint parcial; auditoria registra grant/revoke e repetições idempotentes. Migration `people/0002_role_assignment_history_and_authorization.py` aplicada. Foram aprovados 31 testes, incluindo concorrência PostgreSQL, sem endpoint público ou dados reais.

Fechamento documental dos gates pré-CODEX 02 em 24/08/2026: `GOV-002` recebeu schema normalizado e 20 linhas conservadoras para RS/SC/SP/RJ/ES, sem nenhuma aprovação operacional; `FIRST_LICENSE/CATEGORY_B` foi confirmada como primeira oferta; papéis funcionais e SLAs de `GOV-003` foram aprovados; tabletop formal foi preparado e permanece não executado; `GOV-004` foi classificado por gates com todos os dados reais desconhecidos em `PENDING_HUMAN_INPUT`. Nenhum código, migration, usuário ou dado real foi alterado.

Autorização humana limitada `PRE-CODEX-02 FOUNDATION` executada em 24/08/2026: migrations novas criaram `Person`, `RoleAssignment`, `Clinic`, `ClinicMembership`, `commercial_status` e `RegulatoryReadiness`; nenhum endpoint público, perfil profissional, usuário real ou aprovação regulatória foi criado. O seed preserva 27 UFs e ativa somente RS/SC/SP/RJ/ES. Testes backend passaram com dados exclusivamente sintéticos.

Rodada documental de preparação do CODEX 02 concluída em 24/08/2026: `OPEN-001` fechado por decisão humana; política multi-papel aprovada; separação futura `commercial_status`/`regulatory_status` definida; estrutura nacional de `GOV-002` aprovada sem aprovar linhas/gaps; owners funcionais, SLA proposto e checklist não executado registrados no `GOV-003`; inventário pendente do `GOV-004`; providers de desenvolvimento/produção separados; política conservadora de menores e dívidas de segurança/frontend documentadas. Nenhum código funcional ou migration foi alterado.

Matriz regulatória inicial `GOV-002` ampliada em 24/08/2026 com **Rondônia, Amazonas, Acre e Roraima**, usando fontes oficiais e estados internos conservadores. A autorização PRE-CODEX-02 posterior manteve a primeira onda somente em RS/SC/SP/RJ/ES; RO/AM/AC/RR continuam sem ativação automática.

Matriz `GOV-002` revalidada e política `GOV-003` criada com estados, segregação, motivos, concorrência, falhas, expiração e contestação. A estrutura nacional de `GOV-002` foi posteriormente aprovada, sem aprovar linhas/gaps; `GOV-003` permanece proposta até tabletop e aceite funcional dos owners.

Identidade visual fornecida pelo responsável do projeto aplicada em 2026-08-24 ao cabeçalho do frontend e registrada em `docs/img/logo.jpg`; o asset substitui o marcador visual provisório sem alterar escopo funcional ou liberar CODEX 02.

Marca operacional e identificadores técnicos renomeados para **InstrutorProCNH** em 2026-08-23, incluindo interface, API/OpenAPI, Celery, frontend, documentação, CI e banco local. A pesquisa e proteção jurídica de marca/domínio permanecem abertas em `OPEN-012`.

Fundação técnica executável criada em 2026-08-23: Django/DRF com conta customizada e `ExternalIdentity` inativa; `AuditEvent` append-only com ator nulo; catálogo territorial idempotente; PostgreSQL/PostGIS, Redis e Celery; API `/api/v1`, health/readiness, request ID, erros estáveis e OpenAPI; shell Angular/PrimeNG responsivo e acessível; Docker Compose e CI. Foram comprovados migrations sem drift, 27 UFs/5 `FIRST_WAVE`, PostGIS 3.5, worker Celery, 6 testes backend, lint/formatação, schema, build frontend e audit npm sem vulnerabilidades conhecidas.

Auditoria de todos os artefatos do `docs/MANIFEST.json`: hierarquia e responsabilidades definidas; contradições registradas/resolvidas; domínio/API/arquitetura/autorização consolidados; roadmap até operação; plano A–H; backlog implementável; gates de segurança, LGPD, DevOps e piloto.

Revisão jurídico-técnica de privacidade em fontes oficiais vigentes em 22/07/2026: inventário e bases refinados; aceite separado de consentimento; encarregado/LIA/RIPD, cookies, direitos, transferência internacional, Marco Civil, ECA Digital, incidente e decisão automatizada convertidos em controles; `ADR-017–020` e `OPEN-014` registrados. Nenhum parecer ou gate de Legal/Privacy foi presumido como aprovado.

## Atividade em execução

Fatia 5 — Fundação SaaS + preparação técnica para produção autorizada em 11/09/2026,
sem cobrança e sem deploy. Foram criados Plan, Subscription, Entitlement e PlanEntitlement,
FREE idempotente, policy central de capacidades, analytics 7/30/90 a partir de MarketplaceEvent,
dashboard e página de plano do instrutor, Admin restrito e perfil de settings de produção
fail-closed. PRO permanece rascunho sem preço; pagamento não altera publicação. A organização
recebe somente CNPJ e canal de privacidade autorizados e permanece INCOMPLETE. Conteúdo jurídico,
dados reais, aprovação comercial/legal e deploy continuam bloqueados.

Dossiê M1 de instrutor, veículo, credencial e foto implementado em 31/08/2026 no recorte autorizado:
`DocumentRequirement` versiona UF/categoria/provedor/vigência; `InstructorDocument` preserva
versões, hash, validade, quarentena privada, revisão independente e auditoria; veículo separa
propriedade declarada de verificação. O onboarding aceita somente fixtures sintéticas com prefixo
`fixture-`, formatos PDF/PNG/JPEG, assinatura de conteúdo válida e até 5 MB. Download exige titular
ou permissão explícita e nunca existe rota pública de mídia. Requisitos obrigatórios vigentes passam
a bloquear aprovação/publicação quando não houver documento limpo, aprovado e válido.
`PracticalTrainingRequirement` parametriza carga mínima por território/categoria/processo/versão;
`PlatformLesson` mantém estado da plataforma separado de eventual registro oficial externo, sem
afirmar homologação. Upload real, storage/antimalware de produção, Detran/Senatran/Gov.br e
publicação real continuam desabilitados. A migration foi criada, sem aplicação ou deploy remoto.

Marketplace Core M1 autorizado em execução somente com dados sintéticos. A primeira fatia criou
`StudentProfile`, `StudentDemand`, `InstructorVehicle`, aceite de pré-requisitos e `LessonRequest`,
com sessão de aluno DEMO, agregação de demanda por limiar configurável, transições auditadas e tela
funcional em `/aluno/demanda`. As flags de cadastro/publicação/demanda real permanecem `false` por
padrão. `OPEN-015` não foi resolvido: o valor `3` existe apenas nos exemplos/testes sintéticos.

Fatia 2 de profissionalização concluída em 02/09/2026 no commit `54a1e70`: landing e header expõem encontrar instrutor,
entrar, criar conta, aluno e profissional; cadastro de aluno persiste `Account`, `Person`, papel
`STUDENT`, `StudentProfile`, categoria e transmissão preferida; login por e-mail cria sessão e
direciona à área do papel. O onboarding do instrutor possui pré-requisito e sete etapas persistentes
(`Dados`, `Foto`, `Atendimento`, `Veículo`, `Localização`, `Documentos` e `Revisão`), permite sair e
retomar no passo salvo e registra conta, perfil, veículo, autorização territorial, foto separada e
documentos privados. A submissão resulta em `SUBMITTED/UNPUBLISHED`, exibe status `EM ANÁLISE` e
permanece visível no Django Admin protegido por MFA. A integração Angular/Django usa o cookie
`csrftoken` e o cabeçalho `X-CSRFToken`, sem desativar a proteção CSRF. Fluxos A/B/C foram verificados
no navegador local com identidades e fixtures sintéticas; nenhuma flag real foi ativada, nenhum dado
real foi publicado e nenhum deploy Ubuntu foi realizado.

Fatia 3 de profissionalização concluída localmente com **PASS** em 04/09/2026: a busca usa o adapter MapTiler
no backend em vez do catálogo fixo, com chave em ambiente, restrição ao Brasil, autocomplete com
debounce, cidade/bairro/CEP e falhas explícitas. Leaflet inicia no Brasil, navega à localidade real,
agrupa marcadores e sincroniza mapa/lista. Geolocalização só ocorre após clique e a busca não cria
demanda nem persiste coordenada. PostGIS continua fonte de verdade para raio/distância, com limites
no servidor. A policy separa sintético/real no backend e expõe somente área, foto e verificações
aprovadas. Perfil público e `LessonRequest` persistente foram conectados por UUID. OPEN-007 segue
gate contratual de produção; nenhuma flag real foi ativada, a Fatia 4 não foi iniciada e a VPS não
foi alterada. A chave MapTiler DEV foi configurada somente no `.env` ignorado pelo Git e confirmada
no processo backend sem exposição do valor. Passaram no provider e no navegador: Goiânia, Porto
Alegre, São Paulo, CEP formatado, bairro/cidade/UF, mapa nacional e local, estado vazio, distância,
cartão, perfil público, solicitação, indisponibilidade e remoção de perfil sintético suspenso. A
geolocalização autorizada e negada passou em Chrome automatizado, mantendo busca manual no caso de
negação. Suítes backend/frontend, Django check, migrations check, Ruff, build e auditoria de
dependências de produção passaram. OPEN-007 permanece condicionado exclusivamente aos requisitos
contratuais de produção; nenhuma flag real foi ativada, a Fatia 4 não foi iniciada e a VPS não foi
alterada.

Busca nacional de instrutores implementada em 30/08/2026: `/aluno/instrutores` apresenta as 27
UFs, destaca e contabiliza somente UFs com perfis sintéticos atualmente publicáveis segundo a
policy central e abre `/aluno/instrutores/mapa` com a região-base ao selecionar uma UF ativa.
Estados sem instrutor permanecem visíveis sem contagem ou navegação. A agregação não expõe
localização residencial nem inclui perfil submetido, não verificado ou não publicado.

O certificado Let's Encrypt do endpoint `179.199.136.4` teve renovação simulada com sucesso em
30/08/2026; o mecanismo Docker `certbot-renew` verifica a cada 12 horas e o gateway recarrega a cada
6 horas. Essa evidência não equivale a domínio registrado nem amplia o gate de produção.

## Próxima atividade

Fatia 4 encerrada localmente. Aguardar autorização humana explícita para deploy, ativação de flags
reais, pagamentos, expansão além de categoria B ou retomada de `IAM-003`/CODEX 02C.

### Correção operacional da pré-produção — egress do geocodificador

- o backend da composição DEMO passou a participar das redes `private` e `public`;
- PostgreSQL e Redis permanecem exclusivamente na rede interna e sem portas públicas;
- a rede pública fornece somente o egress necessário ao provedor MapTiler configurado no backend;
- nenhuma Fatia 4, flag de dados reais ou nova capacidade de produto foi iniciada.

### Correção operacional da pré-produção — persistência de uploads

- `MEDIA_ROOT` (`/app/private_documents`) passou a usar o volume nomeado
  `demo_private_documents` nos serviços backend e worker;
- recriações dos containers deixam de remover fotos e documentos armazenados pela aplicação;
- o volume não é publicado pelo Nginx; downloads continuam passando pelas views autorizadas.

### Correção operacional da pré-produção — tiles do mapa

- a camada Leaflet deixou de consumir diretamente os servidores comunitários de tiles do
  OpenStreetMap, após bloqueio HTTP 403 por política de uso;
- tiles rasterizados passaram a ser obtidos do MapTiler por endpoint controlado do backend, com
  validação de coordenadas, timeout, resposta estável de indisponibilidade e cache público de uma hora;
- `MAPTILER_API_KEY` permanece somente no servidor e não é enviada ao navegador;
- a atribuição pública preserva os créditos de MapTiler e OpenStreetMap.

## Decisões abertas

| ID       | Classe         | Resumo                                                          | Gate                 |
| -------- | -------------- | --------------------------------------------------------------- | -------------------- |
| OPEN-002 | resolvido M1 / bloqueante demais escopos | RS/Porto Alegre/B aprovado; demais linhas pendentes | A14/M2 |
| OPEN-003 | adiado | financeiro de aulas fora do MVP de leads | fase futura |
| OPEN-004 | bloqueante     | responsabilidade, consumo, vínculo, seguro, termos e bases LGPD | usuários reais/M6    |
| OPEN-005 | parcial | Asaas sandbox escolhido; PRO real exige preço, contrato, tributação, privacidade e E2E | cobrança real PRO |
| OPEN-006 | parcial        | provider real, contratos, regiões e suboperadores; simuladores liberados para desenvolvimento | provider real/A14/M6 |
| OPEN-007 | condicional/bloqueante produção | Integração/testes DEV concluídos; faltam contrato/DPA, subprocessadores, países, retenção e aceite do endpoint europeu | B1/M3 |
| OPEN-008 | bloqueante     | retenção, direitos e papéis de tratamento                       | produção/M6          |
| OPEN-009 | bloqueante     | SLO, RPO/RTO, suporte, orçamento e limites                      | piloto/M6            |
| OPEN-010 | bloqueante     | metas, duração, coortes e go/no-go do piloto                    | M7                   |
| OPEN-011 | não bloqueante | biblioteca/política OIDC Google                                 | Gate M2.1            |
| OPEN-012 | não bloqueante | nome, marca e domínio                                           | produção pública/VOI |
| OPEN-013 | parcial | FREE/PRO no MVP; preço e ativação paga pendentes | PRO real |
| OPEN-014 | diferido       | menores bloqueados no MVP; mecanismo/política para expansão futura | expansão com menores |

Detalhes, recomendação, alternativas, impactos e owner estão em `DECISIONS.md`.

## Bloqueios

- `GOV002-RS-INSTRUCTOR` e o tabletop passaram no recorte M1; qualquer outra linha/escopo continua bloqueada por `OPEN-002`;
- operador PJ/CNPJ, razão social declarada e canais iniciais estão definidos; comprovação, endereço completo, representação, DPO e documentos aplicáveis permanecem pendentes para homologação/produção;
- provider real continua bloqueado até decisão contratual, mas adapters/simuladores estão liberados para desenvolvimento (`OPEN-006`);
- menores permanecem bloqueados no MVP; `OPEN-014` não bloqueia desenvolvimento sintético para adultos, mas bloqueia qualquer expansão/cadastro operacional de menores.

Os demais bloqueios são diferidos até seus gates; não impedem pesquisa/decisões M0, mas impedem a fase dependente.

## Riscos ativos

Prioridade imediata: `R-001` publicação irregular, `R-003` responsabilidade jurídica, `R-005` LGPD sem base/agente/retenção/transferência, `R-012` risco de custódia, `R-015` recuperação não provada, `R-016/017` densidade/economia, `R-019` suporte, `R-021` mudança regulatória, `R-024` métricas retroativas e `R-025` menor sem proteção/aferição adequada. Registro completo em `RISKS.md`.

## Documentos que precisam ser atualizados

- Após `GOV-001`: `SCOPE.md`, `PILOT.md`, `DECISIONS.md`, `RISKS.md`, `REFERENCES.md` e este checkpoint.
- Após `GOV-002/003`: `DOMAIN.md`, `AUTHORIZATION.md`, `TEST_STRATEGY.md`, `BACKLOG.md` e este checkpoint.
- Após `GOV-004/005`: `LGPD.md`, `DOMAIN.md`, `API.md`, `DECISIONS.md`, `RISKS.md`, termos/avisos e este checkpoint; fechar ou manter explicitamente `OPEN-004/008/014`.
- Após cada decisão/implementação: somente fontes afetadas, OpenAPI/README técnico quando houver código, e este checkpoint.

Não há documento conhecido pendente desta auditoria; as atualizações acima dependem de decisões ainda não disponíveis.

## Critério do primeiro ciclo

Pessoa cria conta, verifica contatos, aceita termos e recebe `INSTRUCTOR` conforme policy de compatibilidade, sem herdar permissões de outros papéis; preenche perfil/aplicação próprios, envia documentos/veículo, submete, recebe pendência, corrige, é aprovada, fica elegível/publicável nesse papel e perde a publicação quando requisito deixa de valer — sem edição manual de banco, com autorização, privacidade, auditoria, testes e operação observável.

## Gate seguinte

Marketplace (M3) somente após M2 aceito. Google é gate opcional M2.1. Pagamento só após `OPEN-005`; piloto só após M6 e checklist de `PILOT.md`.

### Fatia 8 — prontidão técnica sem autorização de dados reais

- adicionada validação fail-closed para todas as capacidades `REAL_*`, inclusive upload documental;
- criada rotina de backup PostgreSQL em formato custom, com validação por `pg_restore --list`,
  SHA-256, permissão `600` e armazenamento fora do repositório;
- criado inventário seguro da VPS que não imprime segredos e exige `.env.production` em modo `600`;
- DNS, HTTPS, redirecionamento de `www` e `/privacidade` foram verificados externamente;
- deploy técnico, backup/restore na VPS e MapTiler exclusivo de produção ainda exigem evidência
  operacional; usuários e dados reais permanecem bloqueados por `OPEN-004/007/008/009`;
- estado obrigatório: `REAL_PRODUCTION_AUTHORIZATION=NOT_GRANTED`.
- deploy técnico de produção concluído em 17/09/2026: serviços saudáveis, nenhuma migration
  pendente, HTTPS/redirect/privacidade/readiness/geocoding/tile aprovados externamente;
- backup custom validado com 192302 bytes e SHA-256 registrado; ensaio de restauração isolado
  aprovado com 48 tabelas, 55 migrations e PostGIS 3.5.2, seguido da remoção verificada somente
  do banco temporário; SLO, RPO/RTO, suporte e demais itens de `OPEN-009` continuam pendentes;
- MapTiler usa temporariamente a mesma chave de DEMO por limite do plano; a integração técnica
  passou, mas chave dedicada e obrigações contratuais continuam em `OPEN-007`.

## Regra de retomada

1. Ler `README.md`, `DECISIONS.md`, `IMPLEMENTATION_PLAN.md`, `BACKLOG.md` e este arquivo.
2. Executar somente o próximo gate documental liberado (`GOV-002/003/004`) ou, após autorização humana explícita, a primeira fatia delimitada do CODEX 02.
3. Scaffold/fundação pode seguir somente conforme `CODEX_01_FOUNDATION.md`; não liberar capacidades reguladas, usuários reais ou publicação antes dos respectivos gates.
4. Ao concluir uma tarefa: validar, atualizar fontes/checkpoint, revisar diff e criar commit convencional.

### Fatia 8B — fundação do piloto controlado (17/09/2026)

- implementados os estados `NOT_GRANTED`, `CONTROLLED_PILOT` e `FULL_PRODUCTION` sem
  autorizar este último;
- adicionada matriz granular fail-closed para cadastro, dados pessoais, uso por aluno,
  cadastro de instrutor, busca, WhatsApp e analytics;
- documentos, publicação automática, pagamentos e cobrança PRO são proibidos em
  `CONTROLLED_PILOT`, mesmo diante de configuração acidental;
- nenhuma capability real foi habilitada ou implantada: o cadastro real está bloqueado
  especificamente pela ausência de Termos de Uso publicados/versionados e de registro de
  aceite conforme exigido pela própria Fatia 8B; `OPEN-004/008/009/010` permanecem abertos;
- validação local: Ruff aprovado, 7 testes focados e suíte backend completa com 151 testes
  aprovados; nenhuma migration necessária;
- relatório e matriz: `docs/CONTROLLED_PILOT_FATIA_8B.md`.

### Fatia 8C — Termos e aceite versionado (17/09/2026)

- publicados no banco os Termos de Uso 1.0 separados para aluno e instrutor, com título,
  audiência, vigência, conteúdo integral fornecido, estado e SHA-256;
- criadas páginas públicas `/termos/aluno` e `/termos/instrutor`, além de APIs públicas dos
  documentos vigentes;
- `LegalAcceptanceRecord` referencia conta, versão exata dos Termos, Política de Privacidade
  vigente, instante e request ID; o aceite é idempotente, auditado e separado de consentimento;
- conteúdo publicado e aceite são imutáveis; alteração material requer nova versão;
- histórico é restrito à própria conta e o Admin não pode editar ou excluir aceites;
- migrations sem deriva, Ruff aprovado, frontend compilado e suíte backend com 161 testes
  aprovados;
- nenhuma capability real foi ativada ou implantada. O anexo recebido termina truncado no item
  7, antes dos critérios completos de integração com cadastro/deploy; essa autorização ausente
  não foi presumida. `FULL_PRODUCTION`, documentos, pagamentos, PRO e publicação automática
  continuam bloqueados.

### Fatia 8D — integração local do cadastro real (18/09/2026)

- cadastro de aluno e instrutor foi ligado aos Termos e à Política vigentes numa única transação;
  falha de validação ou persistência do aceite desfaz conta, pessoa, papel e perfil;
- as rotas públicas de cadastro e o selector real foram preparados com separação explícita entre
  ofertas/contatos `SYNTHETIC` e `REAL`; analytics e WhatsApp reais falham fechados por capability;
- perfis de instrutor nascem `UNPUBLISHED/NOT_STARTED`; upload documental e publicação automática
  permanecem desabilitados;
- a matriz `CONTROLLED_PILOT_RETENTION_FATIA_8D.md` classifica `OPEN-008` como **PARTIAL** porque
  bases, papéis, exceções e prazos pós-encerramento ainda exigem decisão jurídica formal;
- por consequência, nenhuma capability real foi habilitada e nenhum deploy da Fatia 8D foi feito.
- o onboarding cadastral real passou a criar oferta e veículo em modo `REAL`, sem aceitar estado de
  verificação/publicação pelo cliente e sem solicitar documentos profissionais;
- a verificação manual real exige autoridade, método e operador, grava proveniência mínima em
  `ProfessionalVerification` e permite publicação somente por serviço administrativo auditado;
  nenhum arquivo documental é retido e a publicação automática continua proibida;
- o ciclo real de WhatsApp/analytics possui teste de deduplicação, não retorna o telefone bruto em
  campo próprio e não persiste conteúdo de conversa.

### Fatia 8E — fechamento operacional do OPEN-008 (18/09/2026)

- criada a matriz versionada `CONTROLLED_PILOT_DATA_PROCESSING_FATIA_8E.md`, cobrindo os dez
  processos exigidos, minimização, fornecedor, base proposta, retenção, encerramento e exceções;
- a organização operadora foi registrada como controladora das finalidades próprias, sem presumir
  papel ou DPA de hospedagem, MapTiler, WhatsApp ou provedor do canal de privacidade;
- `OPEN-008_CONTROLLED_PILOT=BLOCKED` e `OPEN-008_FULL_PRODUCTION=BLOCKED`: tratamentos necessários
  ainda dependem de LIA/RIPD, encarregado formal, revisão dos providers e retenções aprovadas;
- `OPEN-009` e `OPEN-010` também continuam gates independentes do piloto. Nenhuma capability
  `REAL_*` foi habilitada, nenhuma VPS foi alterada e nenhum cadastro real foi executado.
- validação local: 173 testes backend aprovados; Ruff format/check aprovados após formatação
  mecânica de três arquivos da Fatia 8D; Django check e migration check aprovados; build Angular
  aprovado com aviso preexistente de budget no mapa. O comando de readiness executado no ambiente
  local de desenvolvimento falhou corretamente em `APP_ENV`, `DEBUG`, `SECRET_KEY`, `CSRF`,
  `HTTPS` e `SYNTHETIC`; a configuração real da VPS não foi inspecionada porque o gate de deploy
  não foi alcançado.

### Fatia 8F — propostas objetivas dos gates do piloto (18/09/2026)

- `CONTROLLED_PILOT_GATES_FATIA_8F.md` separa obrigação, boa prática, decisão do proprietário,
  requisito de produção e blocker externo;
- `DPO_STATUS=PENDING_CLASSIFICATION`: o canal existe, mas faltam enquadramento, receita, grupo
  econômico, avaliação de alto risco e responsável pela comprovação; `ADR-019/052` não foi
  substituída sem aprovação humana;
- LIA deixa de ser exigida genericamente e fica limitada a analytics mínimo e telemetria
  adicional, com dois testes internos `PASS`; RIPD fica `NOT_REQUIRED_FOR_CURRENT_SCOPE` no desenho
  pequeno, adulto e sem tratamento de alto risco identificado;
- retenção, operação best effort e coorte de 30 dias/10 alunos/3 instrutores foram propostas, não
  aprovadas. `OPEN-008/009/010_CONTROLLED_PILOT=AWAITING_OWNER_APPROVAL`;
- MapTiler permanece `PENDING_VENDOR_REVIEW` e bloqueia somente a busca real que dependa dele;
  WhatsApp como link externo é follow-up, não integração presumida;
- nenhuma capability foi ativada e nenhum deploy/VPS foi executado.
- aprovação parcial do proprietário registrada em 18/09/2026: idade 18+, analytics por 90 dias,
  LIA-8F-01/02, best effort com RPO 24h/RTO 8h/backup diário, piloto de 30 dias com coorte 10+3,
  RIPD não requerido no escopo atual e fluxo externo WhatsApp;
- `OPEN-010_CONTROLLED_PILOT=PASS`; `OPEN-009_CONTROLLED_PILOT=BLOCKED_TECHNICAL` até restore
  pré-ativação; `OPEN-008_CONTROLLED_PILOT=AWAITING_OWNER_APPROVAL` pela retenção completa e
  `DPO_STATUS=PENDING_CLASSIFICATION`. MapTiler segue `PENDING_VENDOR_REVIEW`;
- a retenção de analytics aprovada ainda exige implementação/teste de descarte em 90 dias.
  Nenhuma capability foi habilitada e nenhum deploy foi autorizado.

### Fatia 8G — retenção técnica e preparação pré-deploy (18/09/2026)

- implementada exclusão definitiva, diária e em lotes dos quatro eventos aprovados de analytics
  quando têm mais de 90 dias; o limite exato permanece até se tornar estritamente mais antigo;
- o Celery Beat existente agenda a tarefa e o management command suporta dry-run, contagens,
  lotes transacionais, idempotência e auditoria agregada sem PII, inclusive em falha parcial;
- `OPEN-009_CONTROLLED_PILOT=READY_FOR_PREDEPLOY_RESTORE_TEST`: procedimento isolado, checks e
  evidências estão definidos; nenhuma VPS foi acessada e a execução continua obrigatória antes da
  ativação;
- o fluxo MapTiler é backend-only, mas envia consulta textual e área do tile ao fornecedor; PostGIS
  pesquisa sem nova chamada depois de receber coordenadas. Como não há resolver/tile local,
  `FALLBACK_REQUIRES_IMPLEMENTATION` e o fornecedor segue `PENDING_VENDOR_REVIEW`;
- prazos de 90 dias para perfis/conta e 180 dias para auditoria/verificação/publicação são apenas
  propostas ao proprietário; aceites e pedidos de privacidade continuam
  `PENDING_LEGAL_REVIEW`; `DPO_STATUS=PENDING_CLASSIFICATION`;
- nenhuma capability real foi ativada, nenhum dado pessoal real foi usado e nenhum deploy foi
  executado.

### Fatia 8H — cadastro e busca nacionais (20/09/2026)

- cadastro/onboarding e área pública de atendimento foram validados nas 27 UFs, com evidência
  representativa em sete capitais de diferentes regiões;
- a busca deixou de iniciar artificialmente em Porto Alegre e continua baseada em PostGIS;
- publicação e selector público real agora exigem prontidão territorial explícita, vigente e
  aprovada; nenhuma UF é aprovada automaticamente;
- a interface de cadastro de aluno usa o catálogo fechado das 27 UFs e a API rejeita códigos
  inexistentes para aluno e instrutor;
- `PREDEPLOY_DECISION=NO_GO`: DPO/enquadramento, retenções jurídicas e revisão MapTiler continuam
  pendentes. Nenhuma capability foi ativada e nenhum deploy foi executado;
- matriz e evidências: `docs/CONTROLLED_PILOT_NATIONAL_SCOPE_FATIA_8H.md`.

### Fatia 8I — prova de restauração e decisão de pre-deploy (20/09/2026)

- validações locais passaram: 192 testes backend, 30 testes focados nacionais/retention, Ruff,
  Django check, migration check e build Angular de produção;
- inventário da VPS confirmou serviços saudáveis, PostgreSQL 17.5/PostGIS 3.5.2, Redis `PONG`,
  banco/cache sem portas públicas e 87 GB livres;
- backup custom de 213586 bytes passou em `pg_restore --list` e SHA-256; restauração isolada em
  banco temporário levou 3 segundos e validou 54 tabelas, 59 migrations e PostGIS 3.5.2;
- o banco temporário foi removido, o banco ativo não foi tocado e o backup foi preservado;
- `OPEN-009_CONTROLLED_PILOT=PASS`, porém `PREDEPLOY_DECISION=NO_GO`: `OPEN-004` e
  `OPEN-008_CONTROLLED_PILOT=BLOCKED`, `DPO_STATUS=PENDING_CLASSIFICATION` e MapTiler pendente para
  busca real;
- nenhuma capability, flag, migration ou serviço da VPS foi alterado. Evidência completa em
  `docs/CONTROLLED_PILOT_RELEASE_FATIA_8I.md`.

### Fatia 8J — deploy independente e fundação de pagamentos (20/09/2026)

- deploy do código e ativação de capabilities reais passam a ser decisões independentes;
- criada a fundação de pagamentos com customer, order, transaction e recibo de webhook separados
  de `Subscription`, valores em menor unidade e estados explícitos;
- porta `PaymentProvider` e fake determinístico permitem testar idempotência, assinatura, eventos
  duplicados, transições e entitlement sem dinheiro ou rede real;
- endpoint de webhook verifica assinatura antes de interpretar, deduplica pelo ID externo, valida
  valor/transição e não registra payload ou segredo em auditoria;
- frontend PRO já permanece em “EM BREVE”, sem preço, checkout ou coleta de cartão;
- nenhum fornecedor foi escolhido; requisitos e credenciais futuras foram documentados em
  `PAYMENT_PROVIDER_REQUIREMENTS.md` e `PAYMENT_GATEWAY_SETUP.md`;
- `REAL_PAYMENTS=false` e `REAL_PRO_BILLING=false` continuam fixos em produção. Implementação não
  fecha `OPEN-005` nem autoriza cobrança.
- CI do commit `7e67b892e5194f26f6760f480ba7343eb4a70a34` passou com 198 testes backend,
  Ruff, Django/migrations e build Angular; o GDAL requerido pelo stack GIS foi instalado no job;
- backup e SHA-256 foram reconfirmados antes do deploy; a VPS foi atualizada por fast-forward do
  commit `5c354dc` para `7e67b89`, preservando banco, Redis, volumes, gateway e certificados;
- foram aplicadas as migrations `discovery.0005`, `payments.0001`, `privacy.0002` e
  `privacy.0003`; backend terminou saudável, demais serviços ativos e logs recentes sem erros;
- smoke externo confirmou frontend, health, readiness, Política e Termos com HTTP 200 e webhook
  sem assinatura com HTTP 401;
- `APPLICATION_DEPLOYED=YES`, `REAL_MARKETPLACE_ENABLED=NO` e
  `PAYMENT_INFRASTRUCTURE_READY=YES`; todas as capabilities reais e comerciais permanecem falsas.
  Evidência completa em `docs/APPLICATION_DEPLOYMENT_FATIA_8J.md`.

### Correção pós-8J — cadastro real de instrutor (20/09/2026)

- diagnóstico confirmou rota pública HTTP 200 e API HTTP 403 porque a autorização estava
  `NOT_GRANTED` e as três capabilities necessárias estavam falsas;
- o frontend também não possuía onboarding real em produção e a tela de status consultava rota
  `/demo/`; ambos foram corrigidos sem liberar documentos, busca, contato ou publicação;
- o fluxo autorizado usa `CONTROLLED_PILOT` com conta, dados pessoais e cadastro de instrutor;
  Termos/Política permanecem transacionais e o perfil nasce não verificado/não publicado;
- o validador operacional passa a reportar o marcador de autorização carregado, sem valor fixo;
- cadastro/onboarding aceita as 27 UFs; prontidão territorial continua gate independente de
  publicação e MapTiler não participa do cadastro;
- validação local: 21 testes focados e 199 backend aprovados, Ruff, Django/migrations, build Angular
  e testes frontend aprovados. Evidência em `docs/INSTRUCTOR_REGISTRATION_HOTFIX_POST_8J.md`.
- deploy concluído em 21/09/2026 no commit `b640bfb`: serviços saudáveis, rotas jurídica e de
  cadastro HTTP 200, capabilities autorizadas carregadas, nenhuma identidade fictícia criada e
  `FIRST_REAL_INSTRUCTOR_READY=YES`.
- tentativa real identificou senha com menos de 10 caracteres; o frontend passou a bloquear esse
  envio e exibir o detalhe retornado pela API. Build aprovado e suíte frontend com 22 testes.
- regressão do incidente ampliada para senha/data inválidas, aceites ausentes, e-mail duplicado e
  rollback integral: 27 testes focados e suíte backend com 205 testes aprovados; Ruff, Django e
  migrations sem falhas ou deriva.
- verificação sanitizada em produção confirmou ausência da conta e rollback integral da tentativa;
  frontend corrigido implantado no commit `c8057be`, sem tocar banco/Redis/volumes/certificados,
  com rota de cadastro HTTP 200. O proprietário pode repetir o cadastro real.
- segunda tentativa revelou `city` e `uf` vazios enviados para instrutor embora fossem opcionais;
  contrato corrigido nos dois lados sem relaxar a obrigatoriedade para aluno. Validação local:
  28 testes focados, 206 backend e 23 frontend aprovados, com build e checks aprovados.
- onboarding de instrutor deixou de exigir coordenadas manuais: cidade e UF acionam a busca
  backend existente, que preenche um centro público aproximado somente quando o resultado pertence
  à mesma UF; latitude/longitude ficam somente leitura e residência não é solicitada. Build Angular
  aprovado e 25 testes frontend passaram.
- a ação da tela de status agora abre o editor real do perfil, e o onboarding recarrega todos os
  campos persistidos antes da edição sem reenviar estados internos de verificação do veículo.
- geocodificação de cidade/UF passou a inferir a sigla pelos nomes oficiais das 27 UFs quando o
  MapTiler não fornece `short_code`, corrigindo a rejeição indevida de Goiatuba/GO; 6 testes
  focados e 208 testes backend passaram, com Ruff, Django e migrations aprovados.
- onboarding permite escolher bairro/ponto público ou ajustar marcador no mapa sem armazenar o
  texto pesquisado; coordenadas públicas são aproximadas no backend para duas casas decimais.
  Validação: 34 testes focados, 208 backend e 28 frontend, além de build Angular, Ruff, Django e
  migrations aprovados.

### Sprint comercial — fluxo real de revisão e publicação (27/09/2026)

- a solicitação de verificação real agora avança o estado do perfil de `DRAFT` para `SUBMITTED`, e a
  análise administrativa sincroniza `UNDER_REVIEW`, `VERIFIED` ou `REJECTED` com auditoria;
- a decisão manual de publicação reconhece a evidência `MANUAL_AUTHORIZED_SOURCE` somente quando
  ligada a uma solicitação verificada e decidida por administrador. A autorização territorial vigente,
  a área de atendimento e os demais gates de publicação continuam obrigatórios;
- o Admin ganhou fila de perfis reais verificados e botões individuais para publicar, suspender e
  despublicar com confirmação, motivo obrigatório e auditoria. Ações em massa DEMO não processam
  perfis reais;
- validação local: 286 testes backend, 42 frontend, Ruff, Django check, migration check e build
  Angular passaram. O build ainda alerta para orçamento de bundle/SCSS, sem falhar;
- isto não habilita a busca real nem comprova entrega de e-mail, MapTiler, foto real ou jornada humana
  na VPS. `REAL_MARKETPLACE_SEARCH` deve continuar desativado até aprovação territorial explícita e
  validação técnica de produção. Nenhum dado profissional fictício foi criado para liberar o fluxo.
