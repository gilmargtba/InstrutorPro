# Registro de Decisões e Questões Abertas

Este documento é a fonte oficial de decisões consolidadas, contradições resolvidas e questões em aberto. Uma recomendação marcada como aberta não é uma decisão aceita.

## Estados

- **Aceita:** normativa até nova ADR que a substitua.
- **Proposta:** recomendação para decisão; implementação dependente não começa.
- **Adiada:** fora do gate atual.
- **Substituída:** preservada para histórico, sem efeito normativo.

## Decisões aceitas

| ADR     | Decisão e justificativa                                                                                    | Consequências e alternativas rejeitadas                                                                                           |
| ------- | ---------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| ADR-001 | **Monólito modular.** Domínio em formação, equipe pequena e transações cruzadas favorecem um deploy único. | Módulos têm limites explícitos; microserviços só por escala/isolamento comprovados.                                               |
| ADR-002 | **Django + DRF.** Produtividade, segurança madura, ORM transacional e backoffice.                          | Custom user na primeira migration; não usar SQLite como integração.                                                               |
| ADR-003 | **Angular + PrimeNG, mobile-first/PWA.** Portais ricos e web antes de app.                                 | App nativo é posterior; acessibilidade e responsividade entram desde o shell.                                                     |
| ADR-004 | **PostgreSQL + PostGIS.** Consistência, constraints e busca geográfica.                                    | UTC; UUID; BRL em centavos no ledger; extensões preparadas por migration.                                                         |
| ADR-005 | **Sessão Django na web.** Reduz exposição de tokens no browser.                                            | Cookie Secure/HttpOnly/SameSite e CSRF; OAuth/OIDC externo termina em sessão interna.                                             |
| ADR-006 | **Verificação interna manual primeiro.** Integrações públicas não bloqueiam validação.                     | Não é credenciamento oficial; requisito local é configurável e evidência fica auditada.                                           |
| ADR-007 | **Integrações por portas/adaptadores.** Fornecedor não define o domínio.                                   | Testes de contrato e falha; troca não altera estados internos.                                                                    |
| ADR-008 | **Auditoria desde a fundação e outbox antes de efeito assíncrono crítico.**                                | Auditoria append-only; evento de domínio e outbox na mesma transação.                                                             |
| ADR-009 | **Status cadastral, comercial, financeiro e oficial separados.**                                           | `Booking` não contém estados de reembolso/pagamento; correlação é por fatos e IDs.                                                |
| ADR-010 | **`ExternalIdentity` estrutural e Google adiado até Gate A19/M2.1.**                                       | Sem botão/endpoint/credencial no primeiro ciclo; `sub`, não e-mail, identifica vínculo.                                           |
| ADR-011 | **Papéis pessoais são cumuláveis somente por política explícita de compatibilidade.**                      | `STUDENT`, `INSTRUCTOR`, `DOCTOR` e `PSYCHOLOGIST` não são mutuamente exclusivos; cada perfil, requisito, credencial, verificação, publicação e autorização é independente. `CLINIC` é organização e administração futura usa `ClinicMembership`. |
| ADR-012 | **Publicação e habilitação financeira separadas.**                                                         | Publicável depende de elegibilidade cadastral; reserva paga também exige recebedor habilitado e estrutura do ledger provisionada. |
| ADR-013 | **Ledger interno por partidas dobradas, sem custódia.**                                                    | Núcleo é uma fatia inseparável; saldo derivado; gateway move dinheiro real.                                                       |
| ADR-014 | **Aceite cria a reserva temporária atomicamente.** Evita duas fontes de criação e preço divergente.        | Não há `POST /bookings` público independente; aceite idempotente retorna a reserva/hold.                                          |
| ADR-015 | **Política comercial versionada e snapshot no acordo.**                                                    | Valores e regras podem mudar sem reescrever contratos existentes; política exata ainda depende de `OPEN-003`.                     |
| ADR-016 | **Marca e imagens permanecem sujeitas à validação jurídica.** O nome de produto adotado é “InstrutorPro”.    | A adoção operacional não substitui busca, registro de marca/domínio nem autoriza app nativo, tracking ou UX representada.          |
| ADR-017 | **Aceite jurídico e consentimento LGPD são evidências distintas.** Contrato/aviso obrigatório não produz consentimento para finalidade opcional. | `LegalAcceptanceRecord` prova versão aceita; `ConsentRecord` prova concessão/retirada por finalidade. Nenhuma base legal é inferida por checkbox genérico. |
| ADR-018 | **Privacidade opt-in para tecnologia não essencial.** O MVP não carrega analytics/marketing/pixel/SDK não necessário antes da escolha granular. | Rejeitar é tão fácil e destacado quanto aceitar; sem adtech, venda/enriquecimento de dados, replay de sessão ou dark pattern. |
| ADR-019 | **Governança reforçada sem depender de dispensa de pequeno porte.** A plataforma nomeia encarregado e produz LIA/RIPD aplicável antes de dados reais. | Ato formal, canal público, substituto e conflito verificado; legítimo interesse exige LIA e tratamento de alto risco exige RIPD preventivo. |
| ADR-020 | **Nenhuma decisão adversa exclusivamente automatizada no MVP.** Expiração objetiva pode despublicar preventivamente, com explicação e contestação humana. | Fraude, risco, perfil ou inferência não rejeitam/suspendem definitivamente; regra, versão, dados e motivo seguro ficam auditáveis. |

## Contradições encontradas e resolvidas

| ID      | Documentos e divergência                                                                                                | Impacto                                                             | Resolução aplicada                                                                                        | Justificativa                                                                     |
| ------- | ----------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| CON-001 | `README`, `CHECKPOINT`, `SCOPE` e `PROMPT` usavam “primeiro ciclo” ora para elegibilidade, ora para a jornada completa. | Agente poderia implementar marketplace/pagamento cedo.              | Primeiro ciclo = fundação cadastral; MVP = jornada transacional; piloto e VOI são entregas posteriores.   | Preserva o gate inegociável de elegibilidade.                                     |
| CON-002 | `DOMAIN` colocava `PAYMENT_PROCESSING`, `REFUND_PENDING` e `REFUNDED` em `Booking`, contra `AGENTS` e arquitetura.      | Estados divergentes e transições impossíveis de reconciliar.        | `Booking`, `Payment`, `Transfer`, `Dispute` e ledger têm ciclos independentes.                            | Estado agregado não deve copiar estado de outro agregado.                         |
| CON-003 | `API` expunha `POST /bookings` além do aceite de proposta.                                                              | Reserva/preço poderiam nascer sem acordo exato ou duplicar.         | Aceite idempotente cria hold e retorna booking; remoção da criação avulsa.                                | Uma única transação preserva proposta, slot e snapshot.                           |
| CON-004 | `AUTHORIZATION` exigia `instructor_financial_account`, entidade ausente no domínio.                                     | Implementador inventaria flag/entidade.                             | Habilitação usa `PaymentRecipient` ativo e `FinancialParty`/contas requeridas provisionadas.              | Reutiliza o modelo financeiro aprovado.                                           |
| CON-005 | `BUSINESS_MODEL` previa zero comissão para aluno trazido pelo instrutor, mas o MVP só descrevia leads do marketplace.   | Origem e cobrança sem modelo/API.                                   | Fluxo de alunos próprios foi movido para SaaS posterior.                                                  | Mantém um único modelo comercial no MVP.                                          |
| CON-006 | `PILOT` autorizava “mediar pagamento” em operação assistida sem limite explícito.                                       | Risco de coleta de cartão/dinheiro e custódia.                      | Suporte apenas orienta/reprocessa no gateway; nunca recebe credenciais ou valores.                        | Cumpre segurança e limite regulatório.                                            |
| CON-007 | Assets exibiam a marca anterior enquanto `CHECKPOINT` dizia nome em aberto.                                           | Marca poderia ser tratada como aprovada.                            | Nome operacional alterado para InstrutorPro; assets antigos continuam apenas como conceitos históricos.   | Evidência visual não substitui decisão nem validação jurídica.                    |
| CON-008 | `BACKLOG` chamava épicos de backlog implementável e não continha campos mínimos.                                        | Não havia unidade objetiva de execução.                             | Backlog foi decomposto em tarefas com fase, prioridade, dependência, módulos, aceite, testes e conclusão. | Permite execução sem replanejamento arbitrário.                                   |
| CON-009 | `IMPLEMENTATION_PLAN` terminava no E2E do MVP, embora a solicitação exigisse homologação a operação e evolução.         | Deploy, dados demo, piloto e continuidade ficavam sem ordem.        | Foram acrescentadas fases de hardening/homologação, piloto, VOI e evolução.                               | O plano agora cobre o ciclo integral.                                             |
| CON-010 | `MANIFEST` usava caminhos ambíguos e omitia a si próprio e os assets.                                                   | Auditoria não conseguia delimitar o pacote.                         | Caminhos relativos à raiz e classes normativa/suporte/governança/conceito.                                | Inventário verificável sem elevar imagem a regra.                                 |
| CON-011 | `REFERENCES` e documentos tratavam verificação interna sem explicitar a autorização oficial vigente do instrutor.       | Risco de publicar profissional não autorizado ou prometer validade. | Credenciamento oficial válido é evidência da elegibilidade, mas a plataforma não o concede/homologa.      | Alinha o produto à Resolução CONTRAN nº 1.020/2025 e regras vigentes a revalidar. |
| CON-012 | `DOMAIN`, `AUTHORIZATION`, `API`, plano e testes ainda impunham `STUDENT XOR INSTRUCTOR`, contrariando `AGENTS` e `CODEX_01_FOUNDATION`. | Uma pessoa seria obrigada a criar contas duplicadas e poderia herdar permissões indevidas. | Papéis pessoais compatíveis podem coexistir, mas capacidades, perfis, requisitos e publicação permanecem independentes; clínica continua organização. | Evita exclusividade global simplista sem conceder autorização transitiva. |

## Questões abertas

| ID       | Classe/gate                            | Questão                                                                         | Recomendação proposta                                                                            | Alternativas e impactos                                                                       | Dono                                       |
| -------- | -------------------------------------- | ------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------- | ------------------------------------------ |
| OPEN-002 | **Bloqueante para regra regulada/A14; não bloqueia fundação sintética** | Quais evidências e requisitos locais, validade e revisão? | Matriz normalizada baseada em fontes oficiais e revisão humana por linha. | URL/pesquisa não basta; nenhuma linha pode liberar elegibilidade/publicação sem aprovação. | COMPLIANCE + LEGAL |
| OPEN-003 | **Bloqueante B5/B6**                   | Comissão, preço, hold, cancelamento, no-show, conclusão e disputa.              | Uma política simples e versionada, validada por jurídico/finanças e testada no piloto.           | Regras flexíveis aumentam casos e suporte; regras rígidas elevam abandono/risco consumerista. | Product + Legal + Finance + Operations     |
| OPEN-004 | **Bloqueante antes de usuários reais** | Responsabilidade da plataforma, consumo, vínculo, seguros, termos e bases LGPD. | Parecer jurídico brasileiro documentado e termos aprovados.                                      | Operar só com disclaimers não reduz adequadamente o risco.                                    | Legal + Compliance                         |
| OPEN-005 | **Bloqueante C1**                      | Gateway, fluxo de split/KYC, tributação e política contábil.                    | RFP com sandbox e prova de webhook/conciliação; parecer jurídico-contábil antes do ledger final. | Checkout simples sem split muda repasse/risco; custódia pela plataforma está fora do escopo.  | Finance + Legal + Accounting + Engineering |
| OPEN-006 | **Bloqueante apenas no gate do provider real/A14/M6** | Quais fornecedores de produção, contratos, regiões e suboperadores serão adotados? | Desenvolvimento usa portas/adapters e simuladores para e-mail, storage privado, malware scan, mapas, pagamentos e notificações; produção exige decisão humana/contratual. | Escolher fornecedor definitivo agora cria acoplamento; não definir antes de produção impede avaliação de segurança/LGPD. | Engineering + Security/Privacy + Legal |
| OPEN-007 | **Bloqueante B1**                      | Provedor de mapas/geocoding e política de precisão/retenção.                    | Provedor com termos compatíveis e armazenar somente precisão necessária.                         | Geocoding próprio é caro; precisão residencial aumenta risco.                                 | Product + Privacy + Engineering            |
| OPEN-008 | **Bloqueante produção**                | Retenção por categoria, canal/SLA de direitos e papéis controlador-operador.    | ROPA e tabela de retenção aprovados por Legal/Privacy; automatizar conforme triggers.            | Prazos arbitrários geram descarte indevido ou excesso.                                        | Privacy + Legal                            |
| OPEN-009 | **Bloqueante produção/piloto**         | SLO, RPO, RTO, suporte, on-call, orçamento e limites financeiros/volume.        | Definir a partir do impacto e capacidade do piloto, testar restore e incidentes.                 | Metas altas elevam custo; metas vagas impedem gate objetivo.                                  | Operations + Engineering + Finance         |
| OPEN-010 | **Bloqueante piloto**                  | Metas numéricas, duração, coortes e regra go/no-go.                             | Congelar baseline antes de convidar usuários.                                                    | Ajustar metas durante piloto invalida a evidência.                                            | Product + Data + Operations                |
| OPEN-011 | **Não bloqueante até Gate A19/M2.1**   | Biblioteca OIDC e política de recuperação/vínculo Google.                       | Backend OIDC maduro, vinculação por reautenticação e recuperação independente.                   | Adiar indefinidamente não afeta o primeiro ciclo/MVP central.                                 | Security + Engineering                     |
| OPEN-012 | **Não bloqueante até VOI**             | A marca e o domínio InstrutorPro estão disponíveis e podem ser protegidos?       | Pesquisar e registrar marca/domínio antes de produção pública.                                   | Operar sem validação cria custo de troca e possível conflito marcário.                        | Founders + Legal + Marketing               |
| OPEN-013 | **Não bloqueante até pós-piloto**      | SaaS, alunos próprios, pacotes e assinatura.                                    | Pesquisa separada após dados do piloto.                                                          | Antecipar dilui o funil e cria novo modelo contratual.                                        | Product + Finance                          |
| OPEN-014 | **Bloqueante para cadastro operacional de menores/expansão futura** | Qual política e mecanismo proporcional serão adotados para menores? | No MVP, bloquear cadastro operacional e coleta de dados de menores em demanda/mapa/marketplace; não definir mecanismo definitivo ainda. | Admitir menores exige política específica, melhor interesse, avaliação do ECA Digital, RIPD e controles próprios. | Product + Legal + Privacy |

## Regra de decisão

### Registro de revisão controlada GOV-002 — 29/08/2026

O responsável humano autorizou o registro documental controlado das decisões da primeira onda, condicionado a evidência suficiente, ausência de dependência pendente e aprovação efetivamente expressa. A autorização não escolheu as opções levantadas na análise anterior e não aprovou nominalmente nenhuma das 20 linhas.

Por aplicação de `deny by default`, evidência encontrada, recomendação técnica, autorização para editar e aprovação documental permaneceram fatos distintos. O resultado registrado em `GOV_002_NATIONAL.md` foi: 0 linhas `APPROVED`, 16 linhas mantidas em `HUMAN_REVIEW_REQUIRED` e 4 mantidas em `RESEARCH_REQUIRED`. `P-002` continua aguardando aprovação de Compliance/Legal e `OPEN-002` permanece aberto. Não houve liberação de elegibilidade, publicação, usuário/profissional real ou integração oficial.

Cada questão fechada deve gerar ADR ou atualização desta tabela com: decisão, data, responsáveis, evidência, alternativas, consequência, rollback/revisão e documentos afetados. O checkpoint só remove o bloqueio depois que todas as fontes oficiais afetadas forem atualizadas.

## Propostas aguardando aprovação — 24/08/2026

| ID | Proposta | Evidência pendente para aceite |
| --- | --- | --- |
| P-002 | Adotar a matriz de `GOV_002_NATIONAL.md` e a revisão manual documentada como baseline de elegibilidade. | Aprovação Compliance/Legal, owner/periodicidade por linha e tratamento dos gaps individuais; fecha `OPEN-002` somente depois disso. |
| P-003 | Adotar `GOV_003_REVIEW_POLICY.md` para segregação, motivos, concorrência, expiração e contestação. | SLAs e papéis funcionais aprovados; tabletop continua não executado e bloqueia operação real de revisão/publicação. |

## Questões encerradas por decisão humana — 24/08/2026

| ID | Decisão aprovada | Consequências e revisão |
| --- | --- | --- |
| OPEN-001 | Arquitetura nacional para 27 UFs. Pela autorização humana `PRE-CODEX-02 FOUNDATION`, a primeira onda técnica é RS, SC, SP, RJ e ES; AM, RO, AC, RR e demais UFs não são ativadas automaticamente. Nenhuma cidade limita arquitetura ou domínio; cidades de operação assistida/piloto serão escolhidas posteriormente sem mudança estrutural. Primeira oferta prática priorizada: primeira habilitação, categoria B. | Demais categorias continuam suportáveis por regras versionadas. A migration nova materializa a separação comercial/regulatória sem editar migrations aplicadas. |

## Decisões de governança aceitas — 24/08/2026

| ADR | Decisão | Consequências |
| --- | --- | --- |
| ADR-035 | **Separar `commercial_status` de prontidão regulatória contextual.** | A migration `territories/0002` implementa estratégia comercial na UF e `RegulatoryReadiness` por UF, tipo de prestador e serviço/capacidade, com vigência, fonte e revisão humana. Nenhum registro é aprovado ou semeado automaticamente. |
| ADR-036 | **Desenvolvimento pode usar simuladores por adapters; provider de produção exige decisão posterior.** | E-mail, storage privado, malware scanner, mapas/geocoding, pagamentos e notificações permanecem substituíveis. Simulador não autoriza dado real, dinheiro real ou publicação. |
| ADR-037 | **MVP bloqueia operacionalmente menores até política específica aprovada.** | Não coletar dados de menores em cadastro, demanda, mapa ou marketplace. Mecanismo definitivo de aferição etária continua aberto para expansão futura. |
| ADR-038 | **Primeira oferta priorizada é `FIRST_LICENSE/CATEGORY_B`.** | Prioridade inicial em RS, SC, SP, RJ e ES; arquitetura continua apta a outras categorias/serviços por regra versionada. |
| ADR-039 | **SLAs iniciais do GOV-003 aprovados para o MVP.** | Revisão e correção cadastral em até 2 dias úteis; contestação recebida em 1 dia útil e análise inicial em 3 dias úteis. Consulta adicional exige motivo registrado. Prazos legais prevalecem para privacidade/LGPD. |
| ADR-040 | **GOV-004 não bloqueia desenvolvimento exclusivamente sintético.** | Dados organizacionais ficam `PENDING_HUMAN_INPUT` e passam a gate conforme homologação/produção; todos os aplicáveis são obrigatórios antes de usuários ou dados reais. |
| ADR-041 | **CODEX 02A usa comando interno deny-by-default e histórico por ciclo.** | `grant_role`/`revoke_role` exigem permissão explícita, motivo e ator; lock da pessoa e constraint parcial impedem duplicidade ativa; revogação preserva histórico e reatribuição cria nova linha; nenhum endpoint público foi autorizado. |
| ADR-042 | **CODEX 02B separa lifecycle de conta dos papéis.** | `ACTIVE`, `BLOCKED`, `DEACTIVATED` controlam acesso e sincronizam `is_active`; bloqueio/desativação preservam pessoa e papéis; reativação de bloqueada é explícita, desativada é terminal nesta fatia; versão/lock/constraint/auditoria protegem transições. |
| ADR-043 | **MAPA ONLINE 01 usa Leaflet/OpenStreetMap e geocoder local por adapters.** | PostGIS consulta pontos públicos sintéticos. O geocoder demo não usa rede/chave; `OPEN-007` continua bloqueando provider e dados reais. |
| ADR-044 | **CODEX 02D centraliza publicação profissional sintética.** | Papel não implica publicação; busca aplica todas as condições, e Admin protegido usa serviço deny-by-default. `OPEN-007` permanece aberto. |
| ADR-045 | **Gate LGPD mínimo da busca aprova somente dados sintéticos e o desenho minimizado.** Busca inicial sem login usa cidade/bairro/CEP explícito, sem GPS automático, histórico individual, saúde ou residência pública. Área do instrutor exige autorização operacional granular e revogável, separada de elegibilidade/publicação. | Busca real permanece bloqueada até controlador/canal, base/LIA, RIPD, retenção, provider, segurança e gates regulatórios/operacionais. `OPEN-007` não é fechado. |

## Decisões aceitas — consolidação 2026-08-19

| ADR | Decisão e justificativa | Consequências |
| --- | --- | --- |
| ADR-021 | **Marketplace de duas pontas com demanda explícita.** Além da busca de oferta, aluno pode publicar necessidade e a operação pode enxergar demanda agregada. | `StudentDemand` é agregado próprio; não cria booking nem expõe localização exata. |
| ADR-022 | **Matching determinístico e explicável no MVP.** | IA não é dependência; versão/fatores ficam auditáveis e somente instrutores elegíveis entram no match. |
| ADR-023 | **Funil separado para candidato a instrutor.** | Candidato não é instrutor publicável; pré-análise é orientação e não declaração oficial de aptidão. |
| ADR-024 | **Verificação oficial por fonte documentada/adaptador, com fallback manual.** | Sem scraping autenticado, endpoint privado ou credencial Gov.br; registrar fonte e data. |
| ADR-025 | **Academia do Instrutor começa como hub orientativo.** | Curso, certificação, marketplace educacional e monetização ficam para iniciativa posterior. |
| ADR-026 | **Mapas públicos usam minimização e agregação.** | Posição residencial exata não é exposta; agregados de demanda exigem limiar de privacidade. |

## Questões abertas adicionais — consolidação 2026-08-19

| ID | Classe/gate | Questão | Recomendação proposta | Dono |
| --- | --- | --- | --- | --- |
| OPEN-015 | **Bloqueante B5A** | Qual limiar mínimo e granularidade para exibir demanda agregada? | Definir com Privacy/Product antes do mapa de demanda. | Privacy + Product + Engineering |
| OPEN-016 | **Bloqueante M3** | Quais pesos/ordem e critérios entram no matching inicial? | Começar por regras simples, versionadas e testáveis; não usar atributos sensíveis. | Product + Operations + Privacy |
| OPEN-017 | **Bloqueante A20** | Qual conteúdo/requisitos podem aparecer na pré-análise por jurisdição? | Derivar somente de matriz oficial versionada e revisão de Compliance. | Compliance + Legal + Product |
| OPEN-018 | **Gate M10** | Quais consultas oficiais oferecem API/uso automatizado permitido em cada jurisdição? | Levantamento por fonte oficial; manter manual até aprovação. | Compliance + Engineering |
| OPEN-019 | **Pós-piloto/M9** | Academia terá parceiros, cursos, leads ou receita? | Decidir em iniciativa própria após dados de conversão e parecer jurídico/comercial. | Product + Legal + Finance |

## Decisões 19/08/2026 — escopo nacional

- **ADR-031 (substituída pela autorização PRE-CODEX-02):** InstrutorPro é nacional para 27 UFs; a primeira onda técnica/comercial fica em RS, SC, SP, RJ e ES. AM, RO, AC e RR permanecem na matriz regulatória sem ativação automática; nenhum status comercial aprova regulação.
- **ADR-032:** regras estaduais são dados/configuração versionados, nunca condicionais hardcoded por UF.
- **ADR-033:** MVP inclui descoberta/perfil de clínicas, médicos e psicólogos ligados à jornada CNH; resultado clínico/laudo não é armazenado por padrão.
- **ADR-034:** landing mantém duas entradas principais: `Sou aluno` e `Sou profissional`; profissional abre instrutor, clínica, médico e psicólogo.
- **ADR-035:** candidato a instrutor/Academia do Instrutor fica fora do MVP.
- **ADR-036:** mapa/demanda pública usa agregação e minimização; localização exata individual não é pública.
- **ADR-037:** uso de fonte oficial para verificação não autoriza prospecção massiva; finalidade/base/termos devem ser aprovados.

## DEC-1.6-001 — Modelo nacional multi-prestador

**Decisão:** o MVP nasce estruturalmente nacional e suporta aluno, instrutor, clínica, médico e psicólogo. Verificação oficial, publicação interna e perfil comercial são entidades/decisões distintas. O matching inicial é determinístico e explicável. Fluxos oficiais de saúde respeitam política por UF (`FREE_CHOICE`, `ASSIGNED_BY_AUTHORITY`, `REFERRED`, `UNKNOWN`).

**Motivo:** evitar acoplamento regulatório por estado, preservar LGPD/geoprivacidade e permitir expansão para 27 UFs sem refatoração estrutural.
