# Prontidão pré-produção M1 — Porto Alegre/RS

Data da avaliação: **29/08/2026**

Escopo: visitante anônimo pesquisando instrutores e primeiro instrutor real cadastrado,
revisado, publicado, suspenso e retirado de novas buscas.

Resultado: **PRÉ-PRODUÇÃO M1 NOT READY**.

Esta avaliação não declara conformidade integral com a LGPD, não aprova regra jurídica e
não autoriza implementação ou deploy. Foram considerados o estado real do repositório,
as decisões humanas registradas e as fontes oficiais revalidadas nesta data.

## 1. GOV-002 M1

**PASS documental no recorte.** Somente `RS/INSTRUCTOR` e `FIRST_LICENSE/CATEGORY_B` são necessários neste
recorte; clínica, médico e psicólogo são `N/A` para o fluxo avaliado.

| Capacidade necessária | Estado | Evidência | Pendência impeditiva |
| --- | --- | --- | --- |
| autorização oficial individual | `APPROVED` para o M1 | DetranRS informa que somente IA constante da lista oficial pode ministrar aulas como autônomo | consulta manual antes de publicar/republicar e a cada 24h |
| categoria/serviço | `APPROVED` para Porto Alegre/B | DetranRS informa ACC/A/B e primeira habilitação/adição; Resolução CONTRAN 1.020/2025 disciplina aulas práticas | não se estende a outra categoria/UF |
| verificação | `APPROVED` sem upload | fonte/data/ator/resultado/regra registrados; tolerância 72h | implementação e homologação ainda pendentes |
| elegibilidade/publicação | `BLOCKED` | policy interna separa verificação, decisão e publicação | depende da linha aprovada, documentos reais, contato verificado e controles A14–A18 |
| suspensão/retirada | `CONDITIONAL` | serviços sintéticos suspendem e selectors retiram de novas buscas | homologação com estados/evidências reais e revisor independente pendente |

Houve autorização humana nominal para transformar `GOV002-RS-INSTRUCTOR` em `APPROVED`
somente no M1 Porto Alegre/categoria B.

## 2. GOV-003

**PASS operacional condicionado ao recorte.** O tabletop foi repetido após a aprovação RS e percorreu suspensão, retirada de novas buscas,
preservação histórica, auditoria, contestação e decisão compensatória. Permanecem abertos
contestação e decisão compensatória. `F-001/F-005` foram fechados, `F-004` é `N/A` no
caminho sem upload e `F-002` é condicional a conflito. Pendências jurídicas/LGPD continuam
em gates separados.

## 3. LGPD visitante

**FAIL para dado real.** O desenho minimizado está adequado para implementação: busca sem
cadastro, cidade/bairro/CEP explícito, sem GPS automático, CPF, CNH, telefone, e-mail,
nascimento ou endereço residencial; consulta sem histórico individual. Ainda faltam
controlador e canal reais, aviso contextual, LIA aprovada, RIPD M1, retenção final por
operador/cache, contrato do geocoder, segurança e homologação.

## 4. LGPD instrutor

**FAIL para dado real.** A separação necessária é:

- **privado:** identificação civil, CPF, contatos, nascimento quando necessário, endereço
  residencial, credenciais/documentos, evidências, veículo protegido, decisões internas,
  logs e auditoria;
- **público:** nome profissional, apresentação permitida, categorias verificadas,
  características públicas autorizadas, situação publicável e área/ponto de atendimento
  com precisão minimizada.

Nunca são públicos automaticamente CPF, CNH, documentos, residência, evidências,
credenciais, dados administrativos ou logs. Faltam organização/controlador, termos e
aviso aprovados, bases finais/LIA/RIPD, retenção, canal de direitos, HTTPS, storage privado,
scanner, MFA administrativo e implementação não sintética do primeiro ciclo.

## 5. Localização

**FAIL para dado real.** `PUBLIC SERVICE LOCATION` permanece separada da residência e a
autorização registra finalidade, versão, ator e concessão/revogação no desenho sintético.
Revogação remove o perfil de novas buscas. Faltam homologação real, precisão pública
aprovada, aviso/base final, retenção, testes anti-enumeração/revogação e condições do
MapTiler. PostGIS continua fonte de verdade.

## 6. OPEN-007

**BLOCKED.** A decisão técnica está tomada: MapTiler Cloud Flex, Leaflet, geocoding pelo
backend, endpoint `api.maptiler.eu`, PostGIS como fonte de verdade, sem GPS e fallback por
busca/lista de Porto Alegre. O plano Flex oficial consultado em 29/08/2026 custa
**US$ 30/mês**, inclui 25 mil sessões de mapa, 3 mil sessões de busca e 500 mil requisições
de API; excedentes publicados são US$ 2,50/1.000 sessões e US$ 0,15/1.000 requisições.

Faltam aceite do plano/termos, DPA, subprocessadores, países/transferência, retenção da
consulta, restrições de chave, budget/rate limit e testes de cobertura/falha. O endpoint
europeu é disponível apenas em plano pago e pode reduzir a priorização de geocoding fora
da Europa; a cobertura de Porto Alegre precisa ser homologada. Até lá, somente geocoder
local e dados sintéticos.

## 7. Primeiro visitante real

**BLOCKED.** Landing, busca sem login, PostGIS, mapa/lista e perfil demonstrativo existem.
O endpoint atual aceita coordenadas e retorna apenas registros `is_demo`; o geocoder é
local e a interface está marcada como demo. Não há catálogo de instrutores reais
publicáveis nem gate LGPD/MapTiler/produção aprovado.

## 8. Primeiro instrutor real

**BLOCKED.** O workflow atual cria somente conta sem senha e perfil `is_demo=True`, exige
confirmação sintética e usa verificação `SYNTHETIC`. Não existem cadastro real completo,
verificação de contato, identidade civil protegida operacional, requisitos/documentos
versionados, upload privado/scan, veículo real, verificação oficial M1, elegibilidade real,
termos/aceites, MFA/revisão independente e publicação real homologada.

## 9. HTTPS

**BLOCKED.** A configuração demo suporta cookies seguros, redirect e HSTS quando variáveis
são habilitadas, mas não há domínio/TLS de produção configurado e comprovado. HTTP não é
aceitável para senha, credencial, documento ou administração real. Visitante anônimo só
deve acessar produção pública depois do baseline HTTPS e de segurança, mesmo consultando
apenas dados públicos.

## 10. Painel administrativo M1

**PARCIAL.** Django Admin possui ações auditadas para o workflow sintético e permissão
explícita, mas faltam MFA, contas/funções segregadas, segundo revisor, fila/documentos
reais, acesso just-in-time, sessão privilegiada, testes de escopo e homologação de
produção. `ADMIN` não recebe poder automático de revisão/publicação.

## 11. Bloqueadores críticos restantes

| Bloqueador concreto | Regra/evidência | Risco | O que falta | Quem decide | Ação mínima |
| --- | --- | --- | --- | --- | --- |
| BCR-01 — regra e operação RS | `GOV002-RS-INSTRUCTOR=APPROVED` no M1 | risco controlado documentalmente | falta implementação/homologação | Compliance + Engineering | implementar exatamente o procedimento aprovado |
| BCR-02 — LGPD/jurídico | operador PJ/CNPJ e canal inicial foram definidos; razão social/representação, aviso, LIA/RIPD e retenção seguem pendentes | tratamento sem transparência, base ou responsabilidade comprovada | comprovação institucional aplicável, termos/aviso, bases/LIA/RIPD, retenção e eventual Encarregado | responsável humano + Privacy/Legal; terceiro qualificado quando exigido | preparar e aprovar pacote LGPD M1 |
| BCR-03 — segregação condicional | policy bloqueia self-review/relação/manipulação prévia; segundo revisor em contestação é “quando possível” | conflito de interesse | segunda pessoa somente para caso próprio/relacionado/conflitante; revisão posterior não substitui independência | Administração + Compliance | primeiro instrutor deve ser independente de Gilmar; caso conflitante fica bloqueado |
| BCR-04 — cadastro/verificação real minimizados | implementação é `DEMO/SYNTHETIC`; consulta oficial pode dispensar upload no primeiro piloto | vazamento ou publicação inválida | cadastro seguro, contato, termos, registro manual oficial, elegibilidade, MFA e testes; storage/scan saem do caminho imediato somente se o procedimento RS for aprovado | Product/Engineering + Security/Operations | aprovar procedimento sem upload e depois autorizar implementação |
| BCR-05 — mapas | `OPEN-007` tem escolha técnica, não aceite contratual/LGPD | transferência/retenção/custo e indisponibilidade não controlados | contrato/DPA/subprocessadores/países/retenção/chaves/limites/testes | Privacy + Legal + Engineering + responsável financeiro | concluir checklist contratual MapTiler Flex |
| BCR-06 — plataforma de produção | `SECURITY/DEVOPS` exigem HTTPS, MFA, restore, observabilidade, contatos e homologação | credenciais/documentos expostos ou serviço irrecuperável | domínio/TLS, settings/segredos, backup/restore, alertas/runbooks, scans e testes | Security/Operations + Administração | preparar staging/produção e executar gate técnico antes de dados reais |

Não foram criados gates novos; os seis itens consolidam dependências legais,
regulatórias, de privacidade, segurança e técnica já existentes.

## 12. Decisões humanas restantes

Operador/canal, procedimento RS e modelo de DPO externo independente foram aprovados. A
solicitação uniforme foi enviada a três fornecedores, sem seleção ou contratação; as
respostas permanecem pendentes. Depois: fornecedor/identidade/ato formal, aprovação da LIA/RIPD/avisos,
aceite MapTiler e autorização do card de implementação production-ready.

## 13. Arquivos alterados

Registrados no commit documental desta avaliação; nenhuma alteração de código, migration,
banco, Ubuntu ou deploy integra esta etapa.

## 14. Commit

O commit-base local de privacidade `a684cf1` pertence ao trabalho autorizado anterior,
altera `CHECKPOINT`, `DECISIONS`, `LGPD` e `REFERENCES` e não está em `origin/main`.
Também estão locais `9762cba` e `f96edcb`. Esta avaliação deve formar um único commit
documental e não autoriza push.

## 15. Checkpoint final

O M1 continua documentalmente delimitado em Porto Alegre/RS, mas não pode receber dados
ou profissionais reais. `CODEX 02C/IAM-003`, pagamentos, Pix, split, IA, integrações
governamentais, scraping e importação automática continuam suspensos.

**PRÉ-PRODUÇÃO M1 NOT READY — EXISTEM OS SEGUINTES BLOQUEADORES CRÍTICOS: LGPD/JURÍDICO, CADASTRO/VERIFICAÇÃO REAIS, MAPTILER CONTRATUAL E PLATAFORMA SEGURA DE PRODUÇÃO. SEGREGAÇÃO É CONDICIONAL AO CONFLITO DO CASO.**
