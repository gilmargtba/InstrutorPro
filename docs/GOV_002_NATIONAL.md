# GOV-002 — Matriz Regulatória Nacional

Status: **ESTRUTURA E FORMATO NACIONAL APROVADOS; NENHUMA LINHA REGULATÓRIA OPERACIONALMENTE APROVADA** — 24/08/2026.

## Objetivo

Criar uma camada regulatória nacional versionada para a InstrutorPro, cobrindo instrutores, clínicas, médicos e psicólogos relacionados à jornada CNH, sem transformar a plataforma em autoridade de credenciamento.

## Escopo territorial

- Arquitetura: 27 UFs.
- Primeira onda técnica/comercial autorizada: **RS, SC, SP, RJ e ES**; AM, RO, AC e RR permanecem na matriz regulatória, sem ativação automática.
- Primeira onda de aprofundamento regulatório: **RS, SC, SP, RJ e ES**.
- Matriz regulatória inicial detalhada: **RS, SC, SP, RJ, ES, RO, AM, AC e RR**.
- Demais UFs: template e ativação progressiva.

## Camadas

1. Federal: CONTRAN, SENATRAN, RENACH e legislação federal aplicável.
2. Estadual: DETRAN/órgão competente, portarias, editais, serviços e listas/consultas oficiais.
3. InstrutorPro: política interna de evidência, revisão, publicação, expiração e auditoria.

## Matriz a preencher por UF e tipo

| Campo | Conteúdo |
| --- | --- |
| UF | 27 UFs; detalhamento inicial RS/SC/SP/RJ/ES/RO/AM/AC/RR |
| Tipo | INSTRUCTOR/CLINIC/DOCTOR/PSYCHOLOGIST |
| Autoridade | órgão competente |
| Ato/regra | referência e vigência |
| Requisitos | requisitos oficiais aplicáveis |
| Documentos/evidências | somente os necessários |
| Validade | quando aplicável |
| Consulta oficial | URL/canal/capacidade |
| Automação permitida | API/PUBLIC_LIST/MANUAL/DOCUMENT |
| Dados públicos mínimos | projeção permitida |
| Última validação | data |
| Owner | Compliance/Legal |

## Registro normalizado obrigatório

Cada regra regulatória é um registro independente e deve possuir, quando aplicável:

| Campo | Regra de preenchimento |
| --- | --- |
| `uf` | código da UF |
| `provider_type` | `INSTRUCTOR`, `CLINIC`, `DOCTOR` ou `PSYCHOLOGIST` |
| `capability_service` | serviço/capacidade regulada; primeira prioridade `FIRST_LICENSE/CATEGORY_B` |
| `requirement` | requisito descrito sem inferência |
| `credential_document` | credencial/documento exigido ou `RESEARCH_REQUIRED` |
| `authority` | órgão oficial competente |
| `official_source` | URL/ato oficial; sua presença não aprova a linha |
| `source_date` | data em que a fonte foi consultada |
| `effective_from` | início de vigência conhecido ou `UNKNOWN` |
| `effective_until` | fim de vigência conhecido ou `UNKNOWN` |
| `verification_method` | `DOCUMENT`, `MANUAL`, `PUBLIC_SOURCE` ou combinação aprovada |
| `official_flow_mode` | `FREE_CHOICE`, `ASSIGNED_BY_AUTHORITY`, `REFERRED` ou `UNKNOWN` |
| `review_status` | `RESEARCH_REQUIRED`, `HUMAN_REVIEW_REQUIRED`, `APPROVED`, `REJECTED` ou `SUPERSEDED` |
| `last_reviewed_at` | data/hora da última decisão humana; vazio enquanto não decidida |
| `notes` | restrição, gap e contexto sem dados pessoais |

Transições de `review_status` exigem decisão humana registrada. Uma URL, lista pública ou ato localizado nunca promove automaticamente uma linha a `APPROVED`.

## Catálogo inicial normalizado — primeira onda

Todas as linhas abaixo usam `capability_service=FIRST_LICENSE/CATEGORY_B`, `source_date=2026-08-24`, `effective_until=UNKNOWN`, `last_reviewed_at=PENDING_HUMAN_REVIEW` e autoridade DETRAN da respectiva UF. As fontes são as URLs oficiais catalogadas neste documento. O quadro é inventário de pesquisa, não configuração operacional.

| UF | provider_type | requirement / credential_document | official_source | effective_from | verification_method | official_flow_mode | review_status | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RS | INSTRUCTOR | autorização de instrutor compatível com categoria/serviço; documento individual a confirmar | página Instrutor + Portaria 099/2026 | 2026 | `PUBLIC_SOURCE+MANUAL` | `UNKNOWN` | `HUMAN_REVIEW_REQUIRED` | confirmar vigência, campos mínimos e periodicidade |
| RS | CLINIC | credenciamento aplicável ao fluxo de habilitação; documento exato a confirmar | Profissionais Processo de Habilitação / Portarias | `UNKNOWN` | `DOCUMENT+MANUAL` | `UNKNOWN` | `HUMAN_REVIEW_REQUIRED` | confirmar livre escolha ou distribuição |
| RS | DOCTOR | credenciamento e especialidade aplicáveis; evidência individual | Profissionais Processo de Habilitação / Portaria 040/2026 | 2026 | `DOCUMENT+MANUAL` | `UNKNOWN` | `HUMAN_REVIEW_REQUIRED` | vínculo com estabelecimento não pode ser inferido |
| RS | PSYCHOLOGIST | credenciamento e especialidade aplicáveis; evidência individual | Profissionais Processo de Habilitação / Portaria 040/2026 | 2026 | `DOCUMENT+MANUAL` | `UNKNOWN` | `HUMAN_REVIEW_REQUIRED` | vínculo com estabelecimento não pode ser inferido |
| SC | INSTRUCTOR | credenciamento/autorização individual; documento exato a confirmar | CNH / Credenciados / Portarias | `UNKNOWN` | `PUBLIC_SOURCE+MANUAL` | `UNKNOWN` | `HUMAN_REVIEW_REQUIRED` | confirmar validade e escopo categoria B |
| SC | CLINIC | credenciamento de clínica médica/psicológica | Credenciados / Endereços | `UNKNOWN` | `PUBLIC_SOURCE+MANUAL` | `UNKNOWN` | `HUMAN_REVIEW_REQUIRED` | ROPA/LIA antes de ingestão sistemática |
| SC | DOCTOR | credenciamento individual e vínculo aplicável | Portarias | `UNKNOWN` | `PUBLIC_SOURCE+MANUAL` | `UNKNOWN` | `HUMAN_REVIEW_REQUIRED` | consolidar ato vigente e validade |
| SC | PSYCHOLOGIST | credenciamento individual e vínculo aplicável | Portarias | `UNKNOWN` | `PUBLIC_SOURCE+MANUAL` | `UNKNOWN` | `HUMAN_REVIEW_REQUIRED` | consolidar ato vigente e validade |
| SP | INSTRUCTOR | credenciamento de instrutor autônomo; documentos do portal | CNH Paulista / Portal dos Credenciados | `UNKNOWN` | `DOCUMENT+MANUAL` | `UNKNOWN` | `HUMAN_REVIEW_REQUIRED` | confirmar consulta individual e revalidação |
| SP | CLINIC | credenciamento prévio da clínica e documentos do portal | Portal dos Credenciados | `UNKNOWN` | `DOCUMENT+MANUAL` | `UNKNOWN` | `HUMAN_REVIEW_REQUIRED` | confirmar fluxo oficial do candidato |
| SP | DOCTOR | credenciamento prévio e vínculo com clínica | Portal dos Credenciados | `UNKNOWN` | `DOCUMENT+MANUAL` | `UNKNOWN` | `HUMAN_REVIEW_REQUIRED` | falta fonte individual consolidada |
| SP | PSYCHOLOGIST | credenciamento prévio e vínculo com clínica | Portal dos Credenciados | `UNKNOWN` | `DOCUMENT+MANUAL` | `UNKNOWN` | `HUMAN_REVIEW_REQUIRED` | falta fonte individual consolidada |
| RJ | INSTRUCTOR | autorização/credenciamento indispensável; evidência individual | Orientações para Cadastro / Portarias | 2026 | `DOCUMENT+PUBLIC_SOURCE+MANUAL` | `UNKNOWN` | `HUMAN_REVIEW_REQUIRED` | confirmar validade e consulta operacional |
| RJ | CLINIC | clínica credenciada no fluxo oficial | Consultas Habilitação / Distribuição de Candidatos | `UNKNOWN` | `PUBLIC_SOURCE+MANUAL` | `ASSIGNED_BY_AUTHORITY` | `HUMAN_REVIEW_REQUIRED` | não oferecer livre escolha quando houver distribuição oficial |
| RJ | DOCTOR | credenciamento individual no ecossistema da clínica | DETRAN-RJ / clínica designada | `UNKNOWN` | `DOCUMENT+MANUAL` | `ASSIGNED_BY_AUTHORITY` | `RESEARCH_REQUIRED` | evidência individual insuficiente |
| RJ | PSYCHOLOGIST | credenciamento individual no ecossistema da clínica | DETRAN-RJ / clínica designada | `UNKNOWN` | `DOCUMENT+MANUAL` | `ASSIGNED_BY_AUTHORITY` | `RESEARCH_REQUIRED` | evidência individual insuficiente |
| ES | INSTRUCTOR | registro/autorização no CEIT; documento individual | IS N 016/2026 | 2026 | `DOCUMENT+MANUAL` | `UNKNOWN` | `HUMAN_REVIEW_REQUIRED` | confirmar vigência e método de consulta |
| ES | CLINIC | credenciamento de clínica consultável no SIT/RENACH2 | SIT Consulta Clínicas / Habilitação | `UNKNOWN` | `PUBLIC_SOURCE+MANUAL` | `UNKNOWN` | `HUMAN_REVIEW_REQUIRED` | definir periodicidade e política de projeção |
| ES | DOCTOR | cadastro/vínculo profissional individual | SIT / Instruções de Serviço | `UNKNOWN` | `DOCUMENT+MANUAL` | `UNKNOWN` | `RESEARCH_REQUIRED` | consulta localizada é orientada à clínica |
| ES | PSYCHOLOGIST | cadastro/vínculo profissional individual | SIT / Instruções de Serviço | `UNKNOWN` | `DOCUMENT+MANUAL` | `UNKNOWN` | `RESEARCH_REQUIRED` | consulta localizada é orientada à clínica |

### Gaps consolidados da primeira onda

- **RS:** vigência/periodicidade e `official_flow_mode` ainda precisam de decisão por tipo; evidência individual de saúde deve ser confirmada.
- **SC:** consolidar ato vigente, validade individual e fluxo oficial para os quatro tipos; ingestão de lista depende de ROPA/LIA.
- **SP:** confirmar consulta individual, revalidação e fluxo do candidato; médicos/psicólogos carecem de fonte individual consolidada.
- **RJ:** confirmar validade do instrutor; médicos/psicólogos permanecem em pesquisa; clínica usa distribuição oficial quando aplicável.
- **ES:** confirmar vigência/consulta do instrutor e fluxo da clínica; médicos/psicólogos permanecem em pesquisa individual.
- **INSTRUCTOR:** nenhuma das cinco linhas possui aprovação humana operacional; faltam periodicidade, validade e método final por UF.
- **CLINIC:** nenhuma linha aprovada; faltam decisão de fluxo, projeção pública, periodicidade e ROPA/LIA quando houver lista.
- **DOCTOR:** nenhuma linha aprovada; RJ/ES em pesquisa e RS/SC/SP aguardam revisão humana de evidência individual.
- **PSYCHOLOGIST:** nenhuma linha aprovada; mesmos gaps de evidência individual e vínculo aplicáveis a `DOCTOR`.

## Gates

Uma UF/tipo não passa a `ACTIVE` sem: fonte oficial revisada; regra vigente registrada; política de verificação; linguagem pública aprovada; LGPD/ROPA aplicável; operação de revisão/expiração; e fallback quando a fonte externa estiver indisponível.

## Requisitos mínimos normalizados para instrutor

Com base nos arts. 37 e 109–112 da Resolução CONTRAN nº 1.020/2025 e na Lei nº 12.302/2010, a configuração estadual deve conseguir representar, sem hard-code em view/API:

- identidade e correspondência com o titular da aplicação;
- autorização vigente emitida pelo órgão executivo de trânsito competente;
- UF, categoria/modalidade e escopo de atuação autorizados;
- cumprimento dos requisitos profissionais federais e da certidão exigida no pedido de autorização;
- situação de suspensão/cancelamento quando a fonte disponibilizar esse fato;
- veículo e vínculo institucional como requisitos separados quando aplicáveis;
- fonte, ato, versão/vigência, método de verificação, data da consulta e validade conhecida.

Ausência de campo público não autoriza inferência. Evidência faltante segue revisão documental/manual conforme `GOV_003_REVIEW_POLICY.md`.

## Recorte recomendado para a primeira ativação

Por decisão humana registrada no encerramento de `OPEN-001`, a primeira oferta prática priorizada é `FIRST_LICENSE / CATEGORY_B` para `INSTRUCTOR`: primeira habilitação, categoria B. A prioridade não limita estruturalmente cidades, UFs, categorias ou serviços futuros. Cidade de operação assistida/piloto é decisão operacional posterior e não altera o domínio.

Em 29/08/2026, Porto Alegre/RS foi escolhida como primeiro território operacional
controlado do M1. A decisão reduz a próxima análise à linha `RS/INSTRUCTOR` e à operação
na cidade, mas não promove seu `review_status`: ela permanece
`HUMAN_REVIEW_REQUIRED`, sem elegibilidade ou publicação real, até aprovação nominal de
Compliance/Legal e fechamento dos gaps registrados.

## Privacidade

Listas públicas são evidência potencial, não autorização genérica para replicação integral ou marketing. Dados de saúde/resultados de exames ficam fora do MVP por padrão. Geolocalização pública é minimizada.

## Fora do MVP

Formação/certificação, Academia do Instrutor e pré-análise de candidato a instrutor.

## Baseline federal validado — revisão 24/08/2026

### Resolução CONTRAN 1.020/2025

A Resolução CONTRAN nº 1.020/2025 está em vigor e é a referência federal principal para aprendizagem, habilitação e formação do candidato. Para a InstrutorPro, ficam registrados como baseline:

- a jornada de primeira habilitação inclui requerimento, curso teórico, RENACH/biometria, avaliação psicológica, exame de aptidão física e mental, exame teórico, aulas práticas, exame prático, PPD e CNH;
- compete aos órgãos executivos de trânsito dos Estados e DF autorizar instrutores e credenciar médicos e psicólogos;
- instrutores podem atuar de forma autônoma ou vinculada, observados os requisitos legais e a autorização competente;
- regras estaduais podem detalhar cadastro, operação, fiscalização, veículos, sistemas e procedimentos sem transformar a InstrutorPro em autoridade pública.

Fonte oficial: https://www.gov.br/transportes/pt-br/assuntos/transito/conteudo-contran/resolucoes/Resolucao10202025.pdf/@@download/file

### Saúde na jornada CNH

O domínio de saúde do MVP cobre somente descoberta, perfil, credenciamento declarado/verificado, localização, contato/encaminhamento e, quando juridicamente/operacionalmente permitido, agendamento. Resultado de exame, diagnóstico, laudo, prontuário, conclusão psicológica e demais dados de saúde não integram o MVP.

A Resolução CONTRAN nº 927/2022 permanece como referência específica para exame de aptidão física e mental, avaliação psicológica e credenciamento relacionado, devendo ser revalidada junto com atos supervenientes antes de cada ativação estadual.

Fonte oficial: https://www.gov.br/transportes/pt-br/assuntos/transito/conteudo-Senatran/resolucoes-contran

## Primeira onda — matriz oficial inicial

A tabela abaixo é uma fotografia regulatória para desenho do produto. `PUBLIC_LIST` significa que foi localizada uma relação/consulta pública oficial adequada como evidência potencial; não autoriza replicação irrestrita, enriquecimento de perfil ou marketing.

| UF | Tipo | Baseline encontrado | Fonte/canal oficial | Verificação MVP | Estado interno inicial |
| --- | --- | --- | --- | --- | --- |
| RS | INSTRUCTOR | Portaria DETRAN/RS 099/2026; atuação autônoma autorizada para primeira habilitação em ACC/A/B; lista pública de IA autorizados | DetranRS — página Instrutor de Trânsito | `PUBLIC_LIST + MANUAL` | `HUMAN_REVIEW_REQUIRED` |
| RS | CLINIC/DOCTOR/PSYCHOLOGIST | DETRAN/RS publica fluxo de credenciamento de médicos e psicólogos; médico exige título de especialista em Medicina de Tráfego e psicólogo título de especialista em Psicologia do Trânsito; atuação ocorre no ecossistema de CFCs/Juntas conforme regra estadual | DetranRS — Profissionais Processo de Habilitação / Portarias | `DOCUMENT + MANUAL` | `HUMAN_REVIEW_REQUIRED` |
| SC | INSTRUCTOR | cadastro de instrutores credenciados/autônomos e credenciamento digital; lista pública no portal | DETRAN/SC — CNH / Credenciados | `PUBLIC_LIST + MANUAL` | `HUMAN_REVIEW_REQUIRED` |
| SC | CLINIC | listas públicas de clínicas médicas e psicológicas credenciadas | DETRAN/SC — Credenciados / Endereços | `PUBLIC_LIST + MANUAL` | `HUMAN_REVIEW_REQUIRED` |
| SC | DOCTOR/PSYCHOLOGIST | portarias públicas individualizam credenciamentos; vínculo e regra vigente devem ser confirmados no onboarding | DETRAN/SC — Portarias | `PUBLIC_SOURCE + MANUAL` | `HUMAN_REVIEW_REQUIRED` |
| SP | INSTRUCTOR | Detran-SP recebe credenciamento de instrutor autônomo; requisitos e fluxo publicados no portal | Detran-SP — CNH Paulista / Portal dos Credenciados | `DOCUMENT + MANUAL` | `HUMAN_REVIEW_REQUIRED` |
| SP | CLINIC | clínica médica/psicológica deve ser credenciada; portal publica requisitos, documentos e fluxo | Detran-SP — Portal dos Credenciados | `DOCUMENT + MANUAL` | `HUMAN_REVIEW_REQUIRED` |
| SP | DOCTOR/PSYCHOLOGIST | profissionais especialistas devem ser previamente credenciados para vinculação à clínica | Detran-SP — Portal dos Credenciados | `DOCUMENT + MANUAL` | `HUMAN_REVIEW_REQUIRED` |
| RJ | INSTRUCTOR | atividade autônoma regulamentada em 2026; autorização/credenciamento é indispensável; processo e publicação oficial documentados | DETRAN-RJ — Orientações para Cadastro / Portarias | `DOCUMENT + OFFICIAL_PUBLICATION + MANUAL` | `HUMAN_REVIEW_REQUIRED` |
| RJ | CLINIC | DETRAN-RJ mantém consulta pública de Clínicas de Medicina e Psicologia e distribuição de candidatos; na primeira habilitação a clínica é indicada eletronicamente pelo sistema, portanto a InstrutorPro não deve prometer livre escolha para o exame oficial | DETRAN-RJ — Consultas Habilitação / Distribuição de Candidatos | `PUBLIC_LIST + MANUAL` | `HUMAN_REVIEW_REQUIRED` |
| RJ | DOCTOR/PSYCHOLOGIST | exame médico e avaliação psicológica são realizados no ecossistema de clínicas credenciadas; o fluxo oficial direciona o candidato à clínica indicada. Publicação individual do profissional exige evidência adicional antes de ativação | DETRAN-RJ | `CLINIC_SOURCE + DOCUMENT + MANUAL` | `RESEARCH_REQUIRED` |
| ES | INSTRUCTOR | CEIT é a base estadual oficial; Instrução de Serviço N nº 016/2026 regulamenta registro, autorização e monitoramento do instrutor autônomo/vinculado | DETRAN/ES — IS 016/2026 | `DOCUMENT + MANUAL` | `HUMAN_REVIEW_REQUIRED` |
| ES | CLINIC | existe consulta pública oficial de clínicas por município/bairro no SIT/RENACH2; serviços oficiais do DETRAN/ES remetem à rede credenciada | DETRAN/ES — SIT Consulta Clínicas / Habilitação | `PUBLIC_LIST + MANUAL` | `HUMAN_REVIEW_REQUIRED` |
| ES | DOCTOR/PSYCHOLOGIST | profissionais atuam vinculados/cadastrados em clínicas credenciadas; a consulta pública localizada é de clínicas, não suficiente por si só para publicar perfil individual como verificado | DETRAN/ES — SIT / Instruções de Serviço | `CLINIC_SOURCE + DOCUMENT + MANUAL` | `RESEARCH_REQUIRED` |
| RO | INSTRUCTOR | DETRAN/RO mantém seção oficial e lista de instrutores autônomos autorizados em 2026, com município e contatos | Portal da Transparência DETRAN/RO — Instrutores Autônomos Autorizados | `PUBLIC_LIST + MANUAL` | `HUMAN_REVIEW_REQUIRED` |
| RO | CLINIC/DOCTOR/PSYCHOLOGIST | portal oficial possui área de empresas credenciadas, mas requisitos, vigência e evidência individual de saúde ainda não foram consolidados | DETRAN/RO — Transparência / Empresas Credenciadas | `DOCUMENT + MANUAL` | `RESEARCH_REQUIRED` |
| AM | INSTRUCTOR | Portaria Normativa nº 014/2026 regulamenta autorização de instrutor autônomo e veículos; serviço oficial mantém emissão de carteira de instrutor | DETRAN/AM — Portarias Normativas / Serviços | `DOCUMENT + MANUAL` | `HUMAN_REVIEW_REQUIRED` |
| AM | CLINIC/DOCTOR/PSYCHOLOGIST | DETRAN/AM mantém credenciados e atos de renovação de clínicas médicas e psicológicas; publicação individual exige evidência adicional | DETRAN/AM — Credenciados / Portarias | `PUBLIC_LIST + DOCUMENT + MANUAL` | `HUMAN_REVIEW_REQUIRED` |
| AC | INSTRUCTOR | Portarias DETRAN/AC nº 308 e 309/2026 disciplinam instrutor autônomo; autorização prévia tem validade de 12 meses e há lista pública oficial | DETRAN/AC — Instrutores Autônomos / DOE / Agência de Notícias do Acre | `PUBLIC_LIST + OFFICIAL_PUBLICATION + MANUAL` | `HUMAN_REVIEW_REQUIRED` |
| AC | CLINIC/DOCTOR/PSYCHOLOGIST | nenhuma fonte consolidada suficiente foi validada nesta rodada para publicação de estabelecimento ou profissional | DETRAN/AC | `DOCUMENT + MANUAL` | `RESEARCH_REQUIRED` |
| RR | INSTRUCTOR | fluxo oficial da primeira CNH admite instrutores autônomos credenciados; consulta de CFCs expõe instrutores associados, mas registros podem estar desatualizados e não bastam isoladamente | DETRAN/RR — Primeira CNH / CFCs credenciadas | `DOCUMENT + PUBLIC_SOURCE + MANUAL` | `HUMAN_REVIEW_REQUIRED` |
| RR | CLINIC/DOCTOR/PSYCHOLOGIST | DETRAN/RR oferece consultas de clínicas e distribuição oficial em programas; vigência e evidência individual precisam de revisão antes de publicação | DETRAN/RR — Clínicas/CFCs credenciadas | `PUBLIC_LIST + DOCUMENT + MANUAL` | `HUMAN_REVIEW_REQUIRED` |

### Fontes oficiais da primeira onda

- RS — Instrutor de Trânsito: https://www.detran.rs.gov.br/instrutor
- RS — Portaria 099/2026: https://publicacoeslegais.detran.rs.gov.br/portaria-detran-rs-n-99-2026
- SC — CNH / instrutores: https://www.detran.sc.gov.br/cnh/
- SC — credenciados: https://www.detran.sc.gov.br/credenciados/
- SC — endereços/credenciados: https://www.detran.sc.gov.br/enderecos-unidades-e-credenciados/
- SC — portarias: https://mtsp.detran.sc.gov.br/portarias_web/portarias.php
- SP — CNH Paulista / instrutor autônomo: https://detran.sp.gov.br/cnhpaulista/
- SP — clínica médica/psicológica: https://credenciados.detran.sp.gov.br/classe-clinica-medica-psicologica
- RJ — instrutor autônomo: https://detran.rj.gov.br/menu/menu-habilitacao/orientacoes-para-cadastro.html
- ES — Instruções de Serviço: https://detran.es.gov.br/instrucoes-de-servico-detran-es
- ES — IS 016/2026: https://detran.es.gov.br/Media/detran/Legislacao/Instrucoes-de-servico-2026/IS%20N%20016.pdf
- RO — instrutores autônomos autorizados: https://transparencia.detran.ro.gov.br/secao/index/629
- AM — portarias normativas: https://www.detran.am.gov.br/acesso-informacao/publicacoes/portarias/portarias-normativas/
- AM — carteira de instrutor: https://www.detran.am.gov.br/servicos/1a-via-da-carteira-de-instrutor/
- AM — credenciados: https://www.detran.am.gov.br/credenciados/
- AC — instrutores autônomos: https://www.detran.ac.gov.br/instrutores-autonomos/
- AC — Portarias nº 308/309 de 2026: https://agencia.ac.gov.br/detran-estabelece-novos-criterios-para-credenciamento-de-instrutores-autonomos-e-funcionamento-de-autoescolas/
- RR — primeira CNH: https://www.detran.rr.gov.br/passo-a-passo-para-1a-cnh-do-brasil-2/
- RR — CFCs credenciadas: https://www.detran.rr.gov.br/habilitacao-cnh/consultas/cfcs-credenciadas/

## Regras de ativação da primeira onda

1. `HUMAN_REVIEW_REQUIRED` não significa `APPROVED` nem `ACTIVE`.
2. Nenhum profissional é publicado como “credenciado pela InstrutorPro”. A UI deve usar linguagem como “credenciamento/autorização verificado em fonte oficial”, com fonte e data quando houver evidência suficiente.
3. Quando não existir consulta pública confiável, onboarding aceita evidência documental e encaminha para revisão manual.
4. Fonte oficial indisponível não converte automaticamente um profissional em inválido; o status vira `VERIFICATION_PENDING`/`SOURCE_UNAVAILABLE` conforme política.
5. A InstrutorPro não registra aula oficial, não escreve no RENACH/CEIT e não substitui apps/sistemas exigidos por SENATRAN/DETRAN.
6. Preços/taxas oficiais ou de exames nunca ficam hard-coded. São registros versionados com UF, ato, vigência, fonte e data de validação.
7. A ingestão de listas públicas deve ser aprovada no ROPA/LIA correspondente antes de persistir dados pessoais em lote.
8. Nenhuma lista pública cria automaticamente conta, perfil comercial, publicação, lead ou contato de marketing.
9. `ProviderVerification` registra evidência/fato oficial; a decisão interna de publicação é processo separado, versionado, auditável e revogável pela InstrutorPro.

## Fechamento parcial dos gaps de saúde — 19/08/2026

### RS

O DETRAN/RS possui fluxo oficial de credenciamento para médicos e psicólogos. Para o desenho do MVP, registrar que o médico de CFC deve possuir título de especialista em Medicina de Tráfego reconhecido pelo CFM e o psicólogo de CFC título de especialista em Psicologia do Trânsito reconhecido pelo CFP. O portal também referencia a Resolução CONTRAN 927/2022 e mantém processo de credenciamento/renovação/regularidade.

**Regra de produto:** o perfil InstrutorPro de médico/psicólogo no RS só recebe selo de verificação após evidência individual suficiente; vínculo com CFC não deve ser inferido apenas pelo nome do estabelecimento.

Fontes oficiais:
- https://www.detran.rs.gov.br/profissionais-processo-de-habilitacao
- https://publicacoeslegais.detran.rs.gov.br/portaria-detran-rs-n-40-2026

### RJ

O DETRAN-RJ mantém consulta oficial de Clínicas de Medicina e Psicologia e página de distribuição de candidatos. No fluxo de primeira habilitação, o sistema do DETRAN indica eletronicamente a clínica credenciada ao candidato. Em 2026, o órgão também publicou valores de R$ 90 para exame de aptidão física e mental e R$ 90 para avaliação psicológica; valores devem permanecer versionados e nunca hard-coded.

**Regra de produto crítica:** no RJ, a InstrutorPro pode informar/explicar a rede e exibir estabelecimentos públicos quando juridicamente aprovado, mas não pode apresentar a experiência como “escolha qualquer clínica para seu exame oficial” quando o procedimento aplicável utilizar distribuição/indicação pelo DETRAN. O CTA deve orientar o usuário a seguir a clínica designada no processo oficial.

Fontes oficiais:
- https://www.detran.rj.gov.br/consultas/consultas-hab.html
- https://www2.detran.rj.gov.br/portal/clinicas/candidatosClinicas
- https://www.detran.rj.gov.br/todos-os-servicos/servicos-hab/1-habilitacao.html

### ES

O DETRAN/ES possui consulta pública oficial de clínicas no SIT/RENACH2 com filtro por município e bairro. Serviços de habilitação do órgão apontam expressamente para clínicas médicas e psicológicas credenciadas. A documentação pública também confirma operação com profissionais médicos e psicólogos vinculados/cadastrados às clínicas.

**Regra de produto:** `Clinic` pode usar a consulta pública como evidência potencial. `Doctor` e `Psychologist` continuam exigindo evidência individual/documental antes de receber status verificado, pois a consulta pública localizada é orientada ao estabelecimento.

Fontes oficiais:
- https://renach2.es.gov.br/Habilitacao/publico/pub_consulta_Clinica.aspx
- https://detran.es.gov.br/habilitacao-3
- https://detran.es.gov.br/renovacao-de-cnh

### SC

O DETRAN/SC mantém listas oficiais separadas de clínicas médicas e clínicas psicológicas credenciadas, além de área pública de credenciados. Isso sustenta `PUBLIC_LIST + MANUAL` para estabelecimento. Antes de sincronização em lote, a InstrutorPro deve aprovar campos mínimos, periodicidade e fundamento no ROPA/LIA.

Fontes oficiais:
- https://www.detran.sc.gov.br/enderecos-unidades-e-credenciados/
- https://www.detran.sc.gov.br/credenciados/

### SP

O Portal dos Credenciados do DETRAN-SP confirma que o credenciamento é obrigatório para clínica atuar em exames médicos/psicológicos e que médicos e psicólogos especialistas devem estar previamente credenciados antes de serem incluídos na equipe da clínica. A verificação pública individual ainda não deve ser presumida.

Fonte oficial:
- https://credenciados.detran.sp.gov.br/classe-clinica-medica-psicologica

## Consequência para o modelo de dados

Adicionar/garantir no desenho definitivo:

- `jurisdiction_service_rule`: define se o serviço oficial permite escolha, distribuição, indicação ou outro fluxo por UF/serviço;
- `provider_verification`: fonte, data, método, escopo da evidência e validade;
- `provider_affiliation`: vínculo profissional-estabelecimento com início/fim e evidência;
- `official_fee_rule`: valor, ato, vigência, UF e serviço, sem hard-code;
- `public_listing_policy`: campos que podem ser projetados na UI e fundamento da publicação;
- `verification_status`: `PENDING`, `VERIFIED`, `EXPIRED`, `SOURCE_UNAVAILABLE`, `REJECTED`;
- `official_flow_mode`: `FREE_CHOICE`, `ASSIGNED_BY_AUTHORITY`, `REFERRED`, `UNKNOWN`.

A UI deve consultar `official_flow_mode` antes de exibir CTA de agendamento/escolha de clínica.

## Próxima pesquisa regulatória

Antes do `ACTIVE` da primeira onda, fechar os gaps `RESEARCH_REQUIRED`, priorizando:

1. SP — localizar/confirmar consulta pública individual ou formalizar política documental para instrutores, médicos e psicólogos;
2. SC — confirmar campos públicos mínimos e periodicidade de atualização antes de qualquer sincronização;
3. RS — confirmar se existe consulta pública individual de médicos/psicólogos adequada à verificação automática;
4. RJ — consolidar atos de credenciamento individual e regras atuais de distribuição por tipo de serviço;
5. ES — localizar ato consolidado mais recente para credenciamento individual de médico/psicólogo e vínculo com clínica;
6. RO — consolidar regras e consultas de clínicas, médicos e psicólogos; revisar minimização da lista de instrutores, que atualmente inclui contatos pessoais;
7. AM — confirmar lista individual vigente de instrutores e profissionais de saúde e a vigência operacional da Portaria Normativa nº 014/2026;
8. AC — consolidar clínicas, médicos e psicólogos e confirmar o canal oficial durável das Portarias nº 308/309 de 2026;
9. RR — confirmar atualização/validade das consultas de CFCs, instrutores e clínicas e localizar o ato específico do instrutor autônomo;
10. iniciar matriz das demais 18 UFs sem bloquear o MVP da primeira onda.

## Evidência de revalidação — 24/08/2026

Foram reabertas e conferidas as fontes oficiais centrais: Resolução CONTRAN nº 1.020/2025; páginas e atos de RS, SC, SP, RJ e ES; lista oficial de instrutores do DETRAN/RO; portarias e serviços do DETRAN/AM; portarias/lista divulgadas pelo DETRAN/AC; e consultas/fluxo de primeira CNH do DETRAN/RR. A revalidação confirma a arquitetura da matriz, mas não substitui parecer nem aprovação nominal de Compliance/Legal.

## Registro controlado da primeira onda — 29/08/2026

Ator da decisão: **responsável humano do projeto, por autorização explícita registrada na sessão de 29/08/2026**.

Escopo da autorização: registrar somente decisões sustentadas pela documentação existente, sem converter evidência, recomendação técnica ou autorização para editar em aprovação regulatória. A autorização não selecionou opções decisórias nem aprovou nominalmente qualquer linha. Aplicando `deny by default`, nenhuma linha mudou para `APPROVED` ou `ACTIVE`.

Metadados comuns: decisão anterior e final referem-se a `review_status`; impacto comum é bloqueio de elegibilidade/publicação real até aprovação nominal; as fontes são as proveniências já catalogadas, não nova consulta externa nesta sessão.

| Identificador | UF/tipo | Decisão anterior → final | Fundamento e evidência/fonte registrada | Dependências remanescentes |
| --- | --- | --- | --- | --- |
| `GOV002-RS-INSTRUCTOR` | RS / INSTRUCTOR | `HUMAN_REVIEW_REQUIRED` → `HUMAN_REVIEW_REQUIRED` | Portaria DETRAN/RS 099/2026 e página Instrutor de Trânsito; há evidência potencial, sem decisão nominal | vigência, documento individual, campos mínimos, periodicidade e `official_flow_mode` |
| `GOV002-RS-CLINIC` | RS / CLINIC | `HUMAN_REVIEW_REQUIRED` → `HUMAN_REVIEW_REQUIRED` | Profissionais Processo de Habilitação/portarias; documento e fluxo exatos não aprovados | evidência do estabelecimento, validade, projeção pública e modo de fluxo |
| `GOV002-RS-DOCTOR` | RS / DOCTOR | `HUMAN_REVIEW_REQUIRED` → `HUMAN_REVIEW_REQUIRED` | Profissionais Processo de Habilitação e Portaria 040/2026; especialidade registrada, evidência individual ainda não aprovada | credenciamento individual, validade, vínculo e periodicidade |
| `GOV002-RS-PSYCHOLOGIST` | RS / PSYCHOLOGIST | `HUMAN_REVIEW_REQUIRED` → `HUMAN_REVIEW_REQUIRED` | Profissionais Processo de Habilitação e Portaria 040/2026; especialidade registrada, evidência individual ainda não aprovada | credenciamento individual, validade, vínculo e periodicidade |
| `GOV002-SC-INSTRUCTOR` | SC / INSTRUCTOR | `HUMAN_REVIEW_REQUIRED` → `HUMAN_REVIEW_REQUIRED` | páginas CNH/Credenciados/Portarias; lista é evidência potencial, não aprovação | ato vigente, documento, validade, categoria B e periodicidade |
| `GOV002-SC-CLINIC` | SC / CLINIC | `HUMAN_REVIEW_REQUIRED` → `HUMAN_REVIEW_REQUIRED` | Credenciados e Endereços/Unidades; listas oficiais localizadas | campos mínimos, periodicidade, ROPA/LIA, projeção e fluxo oficial |
| `GOV002-SC-DOCTOR` | SC / DOCTOR | `HUMAN_REVIEW_REQUIRED` → `HUMAN_REVIEW_REQUIRED` | Portarias públicas individualizam credenciamentos, sem baseline individual aprovado | ato vigente, validade, vínculo e periodicidade |
| `GOV002-SC-PSYCHOLOGIST` | SC / PSYCHOLOGIST | `HUMAN_REVIEW_REQUIRED` → `HUMAN_REVIEW_REQUIRED` | Portarias públicas individualizam credenciamentos, sem baseline individual aprovado | ato vigente, validade, vínculo e periodicidade |
| `GOV002-SP-INSTRUCTOR` | SP / INSTRUCTOR | `HUMAN_REVIEW_REQUIRED` → `HUMAN_REVIEW_REQUIRED` | CNH Paulista/Portal dos Credenciados documentam o fluxo | consulta individual ou política documental, validade e revalidação |
| `GOV002-SP-CLINIC` | SP / CLINIC | `HUMAN_REVIEW_REQUIRED` → `HUMAN_REVIEW_REQUIRED` | Portal dos Credenciados confirma credenciamento prévio | fluxo do candidato, vigência, projeção pública e periodicidade |
| `GOV002-SP-DOCTOR` | SP / DOCTOR | `HUMAN_REVIEW_REQUIRED` → `HUMAN_REVIEW_REQUIRED` | Portal exige credenciamento antes do vínculo à clínica, mas não há fonte individual consolidada | evidência individual, validade, vínculo e método final |
| `GOV002-SP-PSYCHOLOGIST` | SP / PSYCHOLOGIST | `HUMAN_REVIEW_REQUIRED` → `HUMAN_REVIEW_REQUIRED` | Portal exige credenciamento antes do vínculo à clínica, mas não há fonte individual consolidada | evidência individual, validade, vínculo e método final |
| `GOV002-RJ-INSTRUCTOR` | RJ / INSTRUCTOR | `HUMAN_REVIEW_REQUIRED` → `HUMAN_REVIEW_REQUIRED` | Orientações para Cadastro/Portarias registram autorização indispensável | validade, consulta operacional e periodicidade |
| `GOV002-RJ-CLINIC` | RJ / CLINIC | `HUMAN_REVIEW_REQUIRED` → `HUMAN_REVIEW_REQUIRED` | Consultas Habilitação/Distribuição de Candidatos sustentam `ASSIGNED_BY_AUTHORITY` | vigência por serviço, campos públicos, periodicidade e linguagem/CTA aprovados |
| `GOV002-RJ-DOCTOR` | RJ / DOCTOR | `RESEARCH_REQUIRED` → `RESEARCH_REQUIRED` | fonte da clínica designada não comprova credenciamento individual suficiente | localizar ato/evidência individual, validade e vínculo; depois revisão humana |
| `GOV002-RJ-PSYCHOLOGIST` | RJ / PSYCHOLOGIST | `RESEARCH_REQUIRED` → `RESEARCH_REQUIRED` | fonte da clínica designada não comprova credenciamento individual suficiente | localizar ato/evidência individual, validade e vínculo; depois revisão humana |
| `GOV002-ES-INSTRUCTOR` | ES / INSTRUCTOR | `HUMAN_REVIEW_REQUIRED` → `HUMAN_REVIEW_REQUIRED` | IS N 016/2026 registra CEIT/autorização e monitoramento | confirmar vigência, evidência individual, consulta e periodicidade |
| `GOV002-ES-CLINIC` | ES / CLINIC | `HUMAN_REVIEW_REQUIRED` → `HUMAN_REVIEW_REQUIRED` | SIT/RENACH2 e páginas de Habilitação oferecem consulta oficial de clínicas | fluxo, periodicidade, campos mínimos, ROPA/LIA e projeção |
| `GOV002-ES-DOCTOR` | ES / DOCTOR | `RESEARCH_REQUIRED` → `RESEARCH_REQUIRED` | SIT/Instruções de Serviço confirmam ecossistema de clínicas, não prova individual | localizar ato/evidência individual, validade, vínculo e modo de fluxo |
| `GOV002-ES-PSYCHOLOGIST` | ES / PSYCHOLOGIST | `RESEARCH_REQUIRED` → `RESEARCH_REQUIRED` | SIT/Instruções de Serviço confirmam ecossistema de clínicas, não prova individual | localizar ato/evidência individual, validade, vínculo e modo de fluxo |

Resultado documental: **0 `APPROVED`, 16 `HUMAN_REVIEW_REQUIRED`, 4 `RESEARCH_REQUIRED`**. A estrutura nacional e o recorte `FIRST_LICENSE/CATEGORY_B` permanecem decisões aceitas; o conteúdo operacional das linhas continua pendente. `OPEN-002` não foi fechado.

## Estado do gate

A estrutura nacional de `GOV-002` está aprovada: 27 UFs, regras versionadas e separação entre estratégia comercial, evidência oficial e publicação interna. O conteúdo de cada linha continua **não aprovado** enquanto faltarem revisão dos owners funcionais, periodicidade, evidência suficiente e tratamento dos gaps listados. Itens `RESEARCH_REQUIRED` permanecem pendentes; nenhuma linha passa a `APPROVED`/`ACTIVE` por inferência.
