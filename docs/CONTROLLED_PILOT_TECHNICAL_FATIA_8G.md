# Fatia 8G — retenção, restore e inventário MapTiler

Data: 18/09/2026. Escopo: preparação local do piloto controlado. Este documento não autoriza
deploy, acesso à VPS, dados pessoais reais, ativação de `REAL_*` ou `FULL_PRODUCTION`.

## 1. Retenção de analytics — `PASS`

Os eventos `SEARCH_PERFORMED`, `SEARCH_RESULT_IMPRESSION`,
`INSTRUCTOR_PROFILE_VIEWED` e `WHATSAPP_CONTACT_CLICKED` são eliminados definitivamente quando
`created_at < now - 90 dias`. Um evento exatamente no limite de 90 dias permanece; passa a ser
elegível somente quando se torna mais antigo que o limite.

- tarefa Celery: `marketplace.enforce_analytics_retention`;
- periodicidade: diária pelo Celery Beat já existente;
- comando de inspeção: `python manage.py enforce_marketplace_analytics_retention --dry-run`;
- comando efetivo: `python manage.py enforce_marketplace_analytics_retention`;
- lotes: 500 por padrão, configuráveis entre 1 e 5.000;
- transação: uma transação por lote; a falha de um lote não desfaz lote anterior nem altera o lote
  que falhou;
- idempotência: nova execução encontra apenas eventos ainda elegíveis;
- auditoria: somente janela, estratégia, contagens, lotes e classe do erro; nenhum identificador de
  sessão, telefone, texto de WhatsApp, endereço ou coordenada é registrado;
- fora do escopo: `AuditEvent`, eventos de segurança, aceites legais, solicitações de privacidade,
  verificações e decisões de publicação.

A exclusão não altera os agregados da janela corrente: eventos recentes continuam disponíveis e
os eventos vencidos já estavam fora do maior período analítico exposto, de 90 dias.

## 2. OPEN-009 — restore pré-deploy

`OPEN-009_CONTROLLED_PILOT=READY_FOR_PREDEPLOY_RESTORE_TEST`.

O procedimento está preparado, mas não foi executado nesta fatia porque acesso à VPS foi
expressamente proibido. Execução autorizada futura, sempre fora do banco ativo:

1. executar `PRODUCTION_ENV_FILE=.env.production ./scripts/backup-production.sh`;
2. registrar caminho, bytes e SHA-256 e conferir `sha256sum --check`;
3. validar o arquivo custom com `pg_restore --list`, sem restaurar no banco ativo;
4. criar banco temporário com nome novo e previamente conferido, por exemplo
   `instrutorpro_restore_drill_YYYYMMDD`;
5. restaurar com `pg_restore --no-owner --no-acl --exit-on-error` no banco temporário;
6. medir início/fim/duração e verificar conexão, quantidade de tabelas, migrations registradas e
   versão PostGIS; executar checks adicionais de consistência sem expor linhas pessoais;
7. registrar resultado, operador, versão da aplicação, SHA-256 e duração;
8. terminar conexões e destruir exclusivamente o banco temporário após validar duas vezes seu nome;
9. confirmar que o banco de produção não foi tocado e preservar o backup conforme política.

Critério para `PASS`: evidência do teste imediatamente antes da ativação, arquivo íntegro, restore
isolado concluído, checks aprovados, duração compatível com RTO de 8 horas e banco temporário
removido sem tocar produção.

## 3. Fluxo e classificação MapTiler

Fluxo observado no código:

`Angular -> API /geocoding/search ou /map/tiles -> adapter backend MapTiler -> coordenadas ->`
`selector PostGIS de instrutores`.

| Pergunta | Evidência objetiva |
| --- | --- |
| Browser chama MapTiler diretamente? | Não. Angular usa rotas relativas da API para geocoding e tiles. |
| Backend chama MapTiler? | Sim. `MapTilerGeocodingProvider` e `fetch_map_tile` usam `urlopen`. |
| Dados de geocoding enviados | texto digitado (cidade, bairro ou CEP), país BR, idioma PT, limite e autocomplete; chave no query string. |
| Dados de tiles enviados | zoom/x/y do tile, chave e User-Agent do servidor. O tile implica uma área do mapa. |
| IP pode chegar ao fornecedor? | Sim, o IP de saída do backend/VPS; o código não encaminha IP do browser. Logs do fornecedor ainda precisam de revisão. |
| Coordenadas são enviadas? | Na geocodificação, a consulta textual é enviada e coordenadas retornam. Em tiles, z/x/y codifica área. A busca PostGIS recebe coordenadas resolvidas sem nova chamada MapTiler. |
| Cidade/bairro/CEP são enviados? | Sim, quando presentes no texto digitado. |
| API key fica onde? | Somente no backend/configuração; não é entregue pelo frontend. |
| Restrição de origin | Não implementada no código. Como a chamada é servidor-servidor, origin HTTP do browser não acompanha a requisição. Restrições efetivas da chave/conta não foram comprovadas. |
| Fallback implementado | Não. `get_geocoding_provider()` sempre retorna MapTiler e tiles também dependem dele. |
| PostGIS após resolução | Sim. Com latitude/longitude já resolvidas, o selector espacial funciona sem nova chamada MapTiler. |

Classificação técnica: `FALLBACK_REQUIRES_IMPLEMENTATION`. MapTiler é requerido para resolver novo
texto e servir o mapa no fluxo atual; PostGIS não substitui o geocoder, embora execute a busca
espacial depois que as coordenadas existem. Nenhum fornecedor/fallback foi alterado nesta fatia.

## 4. Matriz de revisão MapTiler

| ITEM | STATUS | EVIDENCE | BLOCKER |
| --- | --- | --- | --- |
| plano utilizado | `PENDING_VENDOR_REVIEW` | documentação anterior registra limite de uma chave e chave compartilhada DEMO/produção | confirmar plano/conta e uso permitido no piloto |
| termos aplicáveis | `PENDING_VENDOR_REVIEW` | termos públicos estão referenciados em `REFERENCES.md` | registrar versão aceita, entidade contratante e aplicabilidade |
| política de privacidade | `PENDING_VENDOR_REVIEW` | material público de dados pessoais/segurança está referenciado | confrontar política vigente com configuração real da conta |
| DPA | `PENDING_VENDOR_REVIEW` | nenhuma evidência de DPA aceito no repositório | obter/avaliar DPA quando aplicável |
| subprocessadores | `PENDING_VENDOR_REVIEW` | não comprovados no repositório | obter lista vigente e mecanismo de atualização |
| região de processamento | `PENDING_VENDOR_REVIEW` | endpoint europeu é documentado, mas settings usam endpoint padrão | decidir/contratar região e confirmar endpoint efetivo |
| retenção do fornecedor | `PENDING_VENDOR_REVIEW` | não comprovada para consultas/logs do plano real | prazo, finalidade e controles dos logs |
| transferência internacional | `PENDING_VENDOR_REVIEW` | região/subprocessadores reais não comprovados | países, mecanismo e avaliação aplicável |
| dados enviados | `TECHNICAL_INVENTORY_PASS` | adapter comprova texto, parâmetros, chave, User-Agent/IP de saída e z/x/y | confirmar logs/telemetria adicionais do fornecedor |
| chave/origins | `PENDING_VENDOR_REVIEW` | chave fica no backend; restrições da conta não são verificáveis no código | comprovar restrição compatível com chamada server-to-server e rotação |

Resultado do fornecedor: `PENDING_VENDOR_REVIEW`. Isso bloqueia a busca real dependente do
MapTiler, não as capacidades que não o utilizam.

## 5. Política de retenção restante

Nenhum prazo abaixo é apresentado como obrigação legal. São propostas operacionais para aprovação;
exceções por obrigação legal, fraude, incidente, disputa ou exercício regular de direitos exigem
hold documentado, acesso restrito e revisão.

| categoria | conta ativa | evento de encerramento | ação pós-encerramento | prazo operacional proposto | justificativa | exceções | owner |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ACCOUNT` | manter para autenticação/segurança | encerramento confirmado | bloquear acesso; eliminar segredo/sessão dispensável; depois eliminar ou anonimizar identificadores | 90 dias | reversão/correção e fechamento operacional | holds documentados | aprovar |
| `PERSON_PROFILE` | manter mínimo necessário | encerramento/correção | restringir e eliminar ou anonimizar | 90 dias | encerrar operação do perfil | holds documentados | aprovar |
| `INSTRUCTOR_PROFILE` | manter enquanto ativo/em revisão | encerramento ou despublicação | despublicar imediatamente, restringir e eliminar/anonimizar | 90 dias | impedir descoberta e concluir pendências | holds documentados | aprovar |
| `LEGAL_ACCEPTANCE` | manter registro imutável mínimo | fim da relação | restringir, sem apagar até definição jurídica | `PENDING_LEGAL_REVIEW` | prova da versão e momento do aceite | obrigação/disputa | jurídico; owner não basta |
| `PRIVACY_REQUEST` | manter durante atendimento | pedido encerrado | restringir, sem apagar até definição jurídica | `PENDING_LEGAL_REVIEW` | prestação de contas e defesa do titular | ANPD/disputa | jurídico; owner não basta |
| `AUDIT_LOG` | manter na janela de segurança | expiração da janela/encerramento | anonimizar ou eliminar salvo hold | 180 dias | investigação operacional do piloto | incidente/fraude/disputa | aprovar |
| `VERIFICATION` | manter enquanto válida | expiração/revogação/encerramento | restringir e eliminar após janela | 180 dias | rastrear decisão manual mínima | disputa/obrigação | aprovar, sujeito a revisão jurídica |
| `PUBLICATION_DECISION` | manter enquanto perfil publicável | despublicação/encerramento | restringir e eliminar após janela | 180 dias | provar quem publicou/despublicou e por quê | disputa/segurança | aprovar, sujeito a revisão jurídica |

`MARKETPLACE_ANALYTICS=DELETE_AFTER_90_DAYS` está aprovado e implementado.
`DPO_STATUS=PENDING_CLASSIFICATION` permanece sem alteração.

## Decisões de retenção que Gilmar precisa aprovar

1. Aprovar 90 dias após encerramento para `ACCOUNT`, `PERSON_PROFILE` e `INSTRUCTOR_PROFILE`, com
   bloqueio/despublicação imediatos e eliminação/anonimização ao final, salvo hold documentado.
2. Aprovar 180 dias para `AUDIT_LOG`, `VERIFICATION` e `PUBLICATION_DECISION`, com eliminação ou
   anonimização ao final e exceções documentadas.
3. Confirmar que `LEGAL_ACCEPTANCE` e `PRIVACY_REQUEST` continuam sem prazo numérico até revisão
   jurídica específica; nenhuma aprovação operacional deve inventar prazo legal para elas.
