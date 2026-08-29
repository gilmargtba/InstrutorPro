# LGPD e Privacidade

## CODEX 02D

Autorização da localização guarda finalidade, versão, timestamp e revogação. A policy exige autorização vigente; localização privada não é serializada e fica nula nas fixtures.

Fonte oficial do programa de privacidade, revisada em **22/07/2026** contra a LGPD, atos vigentes da ANPD e legislação digital correlata. Este documento converte requisitos em controles do produto, mas não substitui parecer jurídico. Bases legais, prazos não definidos em lei e papéis definitivos continuam bloqueantes antes de dados reais (`OPEN-004/008/014`).

## Decisões conservadoras do projeto

1. Nenhum dado pessoal real entra em desenvolvimento, demonstração ou piloto antes do gate de prontidão ao final deste documento.
2. Aceite de termos e consentimento LGPD são atos distintos. Aceitar contrato, aviso de privacidade ou política obrigatória não cria consentimento nem autoriza finalidade opcional.
3. Cookies, SDKs e pixels não estritamente necessários permanecem ausentes ou desativados até escolha granular. Publicidade comportamental, enriquecimento de perfil e venda de dados ficam fora do MVP.
4. Biometria, reconhecimento facial, cópia de cartão, tracking contínuo, IA sobre dados pessoais e decisão adversa baseada somente em perfil/score ficam fora do MVP.
5. Documento, CPF, endereço residencial, coordenada exata, dado financeiro, credencial e evidência nunca são públicos nem usados como identificador de URL, label de métrica ou conteúdo de log.
6. Transferência internacional só ocorre com hipótese legal, mecanismo válido, transparência e fluxo posterior documentados; contrato de fornecedor ou alegação de conformidade com GDPR, isoladamente, não bastam.
7. No MVP, cadastro operacional e coleta de dados de menores em demanda, mapa ou marketplace falham fechados; não se adota biometria para aferir idade. `OPEN-014` permanece gate de eventual expansão, e um aviso “18+” não afasta por si só o ECA Digital.
8. Regra automática determinística pode retirar publicação por expiração objetiva, mas deve informar motivo e versão da regra, notificar o afetado e oferecer contestação com revisão humana. Rejeição por fraude, risco ou inferência não será exclusivamente automatizada.

Estas restrições detalham `ADR-017–020` e não fecham as aprovações de Legal/Privacy.

## Normas e estado regulatório considerado

- LGPD, inclusive princípios, hipóteses dos arts. 7º/11, término do tratamento, direitos, segurança, agentes, encarregado e prestação de contas;
- Resolução CD/ANPD nº 2/2022 para agentes de pequeno porte, sem presumir enquadramento nem usar a flexibilização como padrão do projeto;
- Resolução CD/ANPD nº 15/2024 para incidentes, nº 18/2024 para o encarregado e nº 19/2024, retificada em 2025, para transferências internacionais;
- Resolução CD/ANPD nº 32/2026: na data da revisão, somente a União Europeia possui decisão brasileira de adequação;
- Marco Civil da Internet, inclusive guarda de registros de acesso à aplicação, e alterações regulamentares de 2026 a classificar juridicamente para o marketplace;
- Lei nº 15.211/2025 (ECA Digital) e regulamentação de 2026. As orientações definitivas da ANPD sobre aferição etária eram esperadas a partir de agosto de 2026 e devem ser revalidadas antes de implementar `OPEN-014`;
- Enunciado CD/ANPD nº 1/2023: as hipóteses dos arts. 7º/11 podem fundamentar tratamento de dados de crianças e adolescentes, sempre com observância e prevalência do melhor interesse no caso concreto;
- regulamentação geral dos direitos dos titulares ainda constava da Agenda Regulatória 2025–2026 e não figurava na lista de resoluções vigentes consultada. O projeto aplica os prazos já existentes em lei e revalida a norma antes de produção.

Fontes e links oficiais estão em `REFERENCES.md`.

## Governança e agentes de tratamento

A pessoa jurídica real configurada como `PlatformOrganization`, e não o registro de banco, será controladora das finalidades que determinar para o marketplace. O papel é funcional e deve ser decidido operação por operação:

| Relação/operação | Classificação inicial | Decisão pendente |
| --- | --- | --- |
| cloud, storage, mensagens, scan e observabilidade sob instrução | operador/suboperador | confirmar contrato, instruções e fluxos reais |
| gateway em checkout, KYC, antifraude e obrigações próprias | pode combinar operador e controlador independente | decompor por finalidade e dado |
| instrutor recebendo dados mínimos para executar a aula | provável controlador independente para finalidades profissionais próprias | delimitar contrato, transparência e uso posterior |
| plataforma e instrutor definindo juntos finalidade/meios essenciais | controladoria conjunta somente se os fatos demonstrarem | não presumir pelo mero compartilhamento |
| Detran/Senatran e demais autoridades | agentes públicos independentes | compartilhar somente com fundamento e canal autorizados |

O mapa registra controlador, operador, suboperador, terceiro controlador, instruções, responsabilidade por direitos/incidente e contato. O contrato não corrige uma classificação incompatível com a atividade real.

Em 29/08/2026, o responsável humano confirmou a exigência interna de Encarregado/DPO
formal e aprovou o modelo de serviço externo independente. Fornecedor, identidade, aceite,
ato formal, substituição e recursos continuam pendentes; nenhuma contratação foi iniciada.

Antes de dados reais, a plataforma designará encarregado mesmo que futuramente possa demonstrar enquadramento como agente de pequeno porte. A indicação exige ato formal preservado, identidade e canal público, comunicação em português, substituto, recursos, acesso à direção e verificação de conflito com funções que decidem finalidades/meios. A responsabilidade pela conformidade continua com o agente de tratamento, não é transferida ao encarregado.

O ROPA terá uma linha por operação/finalidade, não apenas por tabela, contendo no mínimo: owner, titulares e fontes; dados comuns, sensíveis e inferidos; finalidade; hipótese legal e evidência; sistemas; destinatários e papéis; países/mecanismo de transferência; trigger/prazo/descarte; acessos; medidas de segurança; direitos; risco e vínculo com LIA/RIPD. Mudança material de finalidade, dado, fornecedor, país, público ou tecnologia exige revisão antes do deploy.

## Classificação e inventário inicial

CPF, documento de identidade, dado financeiro, autenticação e geolocalização não são automaticamente “dados sensíveis” do art. 5º, II, mas são tratados aqui como **alto impacto**. Diagnóstico, deficiência/necessidade de adaptação que revele saúde e biometria vinculada à pessoa são sensíveis e só podem usar hipótese do art. 11. Foto documental não será convertida em template biométrico.

As bases abaixo são candidatas. O ROPA deverá escolher e justificar base por finalidade; uma lista de bases separadas por “ou” não é aprovação.

| Operação e dados mínimos | Finalidade | Base a validar | Destinatário mínimo | Trigger de retenção |
| --- | --- | --- | --- | --- |
| e-mail/telefone, senha derivada, sessão e desafio | criar, autenticar, recuperar e proteger conta | contrato/pré-contrato para conta; legítimo interesse documentado para segurança | mensagem e segurança | expiração do segredo ou encerramento + prazo aprovado |
| nome, nascimento, CPF e endereço | identificar parte, contratar e evitar duplicidade | contrato/pré-contrato; obrigação somente com norma exata | equipe autorizada e fornecedor aprovado | fim da relação + obrigação/defesa |
| autorização e documentos do instrutor | revisar elegibilidade interna e preservar evidência | pré-contrato/contrato, obrigação específica ou exercício de direitos conforme operação | storage/scan/revisor autorizado | substituição, expiração ou fim da relação + obrigação/defesa |
| veículo, placa/Renavam e adaptações do veículo | validar oferta e executar aula | contrato/pré-contrato; obrigação específica quando comprovada | revisor e parte apenas no necessário | fim da oferta/vínculo + obrigação/defesa |
| necessidade de acessibilidade que revele saúde/deficiência | compatibilizar aluno, veículo e aula | hipótese específica do art. 11 ainda bloqueada em `OPEN-004` | somente matching/partes no momento necessário | fim da necessidade/reserva + prazo aprovado |
| cidade/área ou ponto de busca | descobrir oferta | contrato/pré-contrato ou legítimo interesse com LIA | mapas quando aprovado | sessão; persistir apenas precisão necessária |
| ponto/data/partes da aula | formar e executar reserva | contrato | partes, mapa e suporte necessário | encerramento + defesa aprovada |
| token/status de pagamento e recebedor | cobrar, liquidar, estornar e prevenir fraude | contrato e obrigações específicas | gateway, contabilidade e autoridade quando devido | obrigação financeira/fiscal/defesa |
| disputa, suporte, denúncia e evidência de usuário/terceiro | resolver caso, segurança e exercício de direitos | contrato, exercício de direitos ou legítimo interesse documentado | caso segregado, jurídico e parte só no necessário | encerramento + obrigação/defesa |
| avaliação e moderação | reputação e segurança do marketplace | contrato ou legítimo interesse com LIA | público só no conteúdo aprovado | vigência + defesa/política |
| acesso à aplicação, segurança e auditoria | segurança, responsabilização e obrigação de guarda | obrigação do Marco Civil para registro de acesso; legítimo interesse/LIA para telemetria adicional | observabilidade e equipe autorizada | seis meses para registro legal; demais classes conforme tabela |
| marketing e cookies não necessários | comunicação opcional, atribuição e medição | consentimento por finalidade/canal como padrão do MVP | provedor aprovado | retirada/fim da finalidade + prova mínima |
| pedido do titular e prova de atendimento | cumprir direitos e prestar contas | obrigação legal/regulatória e exercício de direitos | Privacy/Legal e operadores necessários | encerramento + prazo de prova aprovado |

Regras adicionais:

- permissão de geolocalização do navegador/sistema operacional não equivale, por si, a uma base legal LGPD;
- dado público ou manifestamente público continua sujeito a finalidade, boa-fé, necessidade, transparência e direitos; consulta oficial não autoriza replicar base inteira;
- dados enviados em campo livre, arquivo, EXIF ou evidência de terceiro são minimizados, redigidos ou rejeitados quando não necessários;
- KYC/biometria eventualmente exigidos pelo gateway são coletados diretamente por ele sempre que possível; a plataforma recebe apenas token, status e motivo seguro.

## Seleção de base legal

- **Contrato/pré-contrato:** somente quando o tratamento for objetivamente necessário ao núcleo do serviço e, no pré-contrato, ocorrer a pedido do titular. Conveniência, analytics e marketing não são empurrados para essa base.
- **Obrigação legal/regulatória:** o ROPA cita norma, artigo, categoria de dado, prazo e owner de revalidação; “compliance” genérico não é fundamento.
- **Exercício regular de direitos:** delimita processo ou risco defensivo plausível e não autoriza retenção preventiva ilimitada.
- **Legítimo interesse:** apenas para dado não sensível e depois de LIA por operação, com as fases finalidade, necessidade, balanceamento e salvaguardas. A LIA registra interesse concreto, expectativa do titular, impacto, opt-out/oposição, transparência e revisão; resultado negativo bloqueia o tratamento.
- **Consentimento:** usado apenas quando a escolha puder ser livre e não prejudicar serviço necessário. Deve ser granular, informado, inequívoco, comprovável e retirável com facilidade equivalente; silêncio, caixa pré-marcada, contrato ou uso continuado não valem.
- **Dado sensível:** exige hipótese do art. 11 e controles reforçados. Legítimo interesse do art. 7º, IX, não se aplica. Até validação, campos que revelem saúde/adaptação permanecem indisponíveis.

Finalidade nova ou incompatível não herda a base anterior. Produto registra a proposta, executa nova análise e, quando necessário, apresenta novo aviso/consentimento antes da coleta.

## Termos, avisos, consentimentos e cookies

`LegalDocument` versiona termos, contratos, políticas, avisos e textos de consentimento. A prova de aceite contratual usa `LegalAcceptanceRecord`; consentimento opcional e sua retirada usam `ConsentRecord`. Ambos são append-only, referenciam a versão/hash exibida e guardam somente evidência proporcional. A mera ciência de aviso de privacidade não é tratada como consentimento.

No MVP:

- primeiro carregamento instala somente cookies necessários de sessão, CSRF, segurança e preferências essenciais, cada qual com finalidade e duração documentadas;
- analytics, marketing, publicidade, replay de sessão, fingerprinting e conteúdo de terceiro não carregam antes da escolha aplicável;
- banner oferece “aceitar”, “rejeitar não necessários” e “gerenciar” com destaque equivalente; categorias opcionais começam desligadas;
- escolha e retirada ficam disponíveis permanentemente, sem dark pattern; retirada interrompe coleta futura e aciona descarte cabível;
- inventário técnico concilia periodicamente cookies/SDKs observados com a declaração publicada; dependência nova falha no CI ou no gate de release.

Documentos jurídicos mínimos antes de usuários reais: aviso de privacidade por público, política de cookies, termos separados de aluno/instrutor, contrato de intermediação, políticas comercial/conduta/avaliação/suporte e avisos contextuais para documento, localização, pagamento, compartilhamento e decisão automatizada.

## Minimização e proteção por padrão

- coleta é progressiva: conta não exige CPF, endereço, documento ou localização antes da etapa que os necessite;
- campo possui finalidade, obrigatoriedade, classificação, visibilidade e regra de retenção; opcional sem finalidade é removido;
- perfil e mapa públicos usam nome profissional e área suficiente, nunca residência, documento, placa completa ou agenda histórica;
- dado entre aluno e instrutor só é liberado no momento e escopo necessários à aula; contato alternativo não vira marketing;
- backoffice começa mascarado; elevação exige caso, finalidade, MFA quando aplicável, tempo limitado e auditoria revisável;
- logs, traces, analytics e filas usam IDs opacos e proíbem payload, coordenada exata, URL assinada, arquivo ou evidência;
- testes, suporte, screenshot e UAT usam dados sintéticos; cópia de produção é proibida;
- exportação remove dado de terceiro, segredo, regra antifraude e evidência alheia sem negar os dados do próprio titular;
- pseudonimização reduz exposição, mas não é anonimização. Só se declara anonimizado quando reidentificação por meios razoáveis não for possível e a avaliação estiver documentada.

## Retenção, hold e descarte

Não há retenção “para sempre”. A tabela aprovada em `OPEN-008` informa dado/finalidade, trigger, prazo ativo e pós-trigger, fundamento, legal hold, descarte no banco/storage/cache/busca, propagação a operador, backup, owner e teste.

Prazos normativos já identificados:

- registro de acesso à aplicação mantido sob sigilo e segurança por **seis meses**, nos termos do art. 15 do Marco Civil; não confundir com log de negócio, observabilidade ou `AuditEvent`;
- registro de incidente com dados pessoais preservado por **ao menos cinco anos**, conforme a Resolução CD/ANPD nº 15/2024;
- declaração completa de acesso do titular em até **15 dias** não define retenção do dado exportado; o artefato de exportação terá expiração curta aprovada.

Até os demais prazos serem aprovados:

| Classe | Regra fail-safe |
| --- | --- |
| OTP, token e sessão | expirar/inutilizar; conservar apenas metadado mínimo de segurança |
| busca/geolocalização | memória/sessão ou precisão reduzida; sem histórico contínuo |
| documento rejeitado/substituído | restringir imediatamente; descartar após janela aprovada se não houver decisão/hold |
| booking/pagamento/ledger | preservar fato necessário; desacoplar ou pseudonimizar PII quando cabível |
| disputa/auditoria | acesso estrito; não usar imutabilidade para reter payload pessoal excessivo |
| conta desativada | separar retenção justificada e eliminar/anonimizar o restante por workflow idempotente |
| backup | expirar por ciclo; após restore, reaplicar tombstones/solicitações antes de uso normal |

Legal hold exige caso, escopo, aprovador, início, revisão e expiração. `LedgerEntry`/`AuditEvent` confirmados não são apagados isoladamente, mas suas referências pessoais podem ser minimizadas ou pseudonimizadas. Jobs de lifecycle reconciliam banco, storage, cache, índice, fila morta, exportação e cópias de operador, com métricas de atraso e órfãos.

## Direitos dos titulares

Desativação técnica da `Account` no `CODEX 02B` não equivale a eliminação, anonimização nem atendimento automático de direito LGPD. Ela bloqueia acesso e preserva relações/histórico. Retenção, exceções legais, anonimização e eliminação cabível permanecem no fluxo segregado e na tabela de retenção futura; não existe hard delete automático nesta fatia.

Fluxo segregado: receber sem exigir login → autenticar proporcionalmente → classificar → localizar sistemas/fornecedores → tratar dado de terceiro/exceção → executar → revisar → responder gratuitamente → propagar a destinatários → auditar sem copiar todo o conteúdo.

Cobertura mínima: informação; confirmação e acesso; correção; compartilhamentos; anonimização/bloqueio/eliminação cabíveis; portabilidade quando regulamentada; retirada e consequências do consentimento; oposição; peticionamento; e revisão/explicação de decisão automatizada.

- confirmação/acesso simplificado são providos imediatamente quando seguros;
- declaração completa com origem, inexistência de registro, critérios e finalidade é entregue em até 15 dias;
- os demais SLAs permanecem em `OPEN-008` e nunca podem alongar prazo legal superveniente; a fila alerta antes do vencimento;
- impossibilidade imediata gera resposta com razões de fato/direito e canal de contestação; recusa genérica ou silêncio são proibidos;
- correção, eliminação, anonimização ou bloqueio são propagados imediatamente aos agentes com quem houve compartilhamento, ressalvadas as exceções legais documentadas;
- identidade é verificada pelo meio menos invasivo adequado ao risco; selfie/documento não são exigidos por padrão e pedido de privacidade não vira vetor de tomada de conta;
- pedido não é ticket comum visível ao suporte amplo. Exportação é assíncrona, criptografada, temporária, autenticada e auditada.

## Decisões automatizadas e elegibilidade

Cada avaliação automática que afete publicação, conta, oferta, pagamento ou reputação registra finalidade, dados usados, regra/modelo e versão, resultado, motivo seguro, data, possibilidade de erro/discriminação e rota de contestação.

Expiração objetiva pode despublicar preventivamente para cumprir a regra de elegibilidade, sem afirmar decisão oficial. O instrutor recebe motivo acionável e pode pedir revisão humana. Score secreto, inferência de fraude, perfil comportamental ou dado sensível não rejeita/suspende definitivamente no MVP. Segredo comercial pode limitar detalhe abusável, mas não elimina informação clara sobre critérios nem a auditabilidade exigida.

## Fornecedores e transferências internacionais

Due diligence cobre finalidade, papel real, instruções, dados, países de armazenamento/suporte, acesso remoto, suboperadores, segurança, direitos, retenção/devolução, portabilidade, auditoria, continuidade e saída. Contrato com operador exige confidencialidade, medidas, assistência a direitos/RIPD, deleção/devolução, autorização/aviso de suboperador e notificação de incidente à plataforma sem demora injustificada, com objetivo interno de até 24 horas após ciência.

Para cada fluxo internacional, o controlador verifica cumulativamente: aplicação da LGPD, hipótese dos arts. 7º/11, finalidade/minimização e mecanismo do art. 33. Na data desta revisão:

- destino coberto pela decisão de adequação da União Europeia pode usar esse mecanismo nos limites da Resolução nº 32/2026;
- demais destinos usam mecanismo válido, em regra as cláusulas-padrão da Resolução nº 19/2024 incorporadas integralmente e sem alteração, salvo outra hipótese legal comprovada;
- região brasileira não basta se suporte, telemetria, backup ou suboperador disponibilizar dados no exterior;
- transferência posterior recebe a mesma análise e transparência; troca de país/suboperador reabre o gate;
- quando solicitada, a íntegra das cláusulas usadas é fornecida ao titular em até 15 dias, resguardados segredos legítimos.

Nenhum fornecedor de produção é aprovado apenas por marca, certificação ou DPA genérico. O inventário guarda contrato/versão, mecanismo, países, suboperadores, owner e data de revalidação.

## Crianças, adolescentes e aferição de idade

O MVP não permite cadastro operacional de menores. O mecanismo definitivo de aferição etária não foi escolhido e `OPEN-014` permanece aberto para expansão futura. Como a lei considera serviços direcionados ou de acesso provável por menores, autodeclaração ou cláusula contratual pode ser insuficiente. Antes de qualquer expansão:

1. Product/Legal/Privacy classificam público, acesso provável e incidência do ECA Digital;
2. documentam alternativa menos invasiva de aferição, dados, precisão, retenção, falso positivo/negativo e recurso;
3. revalidam a orientação definitiva da ANPD esperada após a consulta de julho de 2026;
4. se menor entrar no escopo, atualizam `SCOPE`, realizam RIPD, aplicam melhor interesse prevalecente, proteção elevada, transparência adequada à idade e todas as obrigações do art. 14 da LGPD e do ECA Digital antes da coleta;
5. escolhem a base dos arts. 7º/11 por finalidade sem presumir consentimento como única opção; quando houver consentimento de criança, cumprem forma específica/em destaque, verificação do responsável por esforços razoáveis e as exceções estritas do art. 14.

Até lá, não se cria fluxo de responsável, perfil infantil, publicidade para menores ou inferência biométrica. Dado mínimo usado para provar faixa etária não será reutilizado para marketing ou perfil.

## Incidentes com dados pessoais

Security contém e preserva evidência; Privacy/Legal registra quando o controlador soube que dados pessoais foram afetados e avalia risco/dano relevante. Incidente comunicável é reportado pelo controlador à ANPD e aos titulares em até **três dias úteis** dessa ciência, ressalvada regra setorial. Se informações estiverem incompletas, comunicação preliminar justificada é complementada em até **vinte dias úteis**.

Operador informa a plataforma sem demora e fornece o necessário. Comunicação ao titular é direta/individual quando possível, em linguagem simples, e descreve dados, proteções, riscos, medidas, eventual demora, data de ciência e contato. Todo incidente, comunicado ou não, mantém por ao menos cinco anos decisão de risco, cronologia, evidências, medidas e justificativa. Ver `SECURITY.md` e `DEVOPS.md` para execução.

## LIA, RIPD e revisão contínua

LIA é obrigatória por decisão do projeto antes de usar legítimo interesse. RIPD é elaborado antes de tratamento de alto risco, dado sensível, geolocalização precisa/escala, nova aferição de idade, biometria, perfilização/decisão relevante ou quando solicitado pela ANPD. O relatório descreve necessidade/proporcionalidade, fluxo, riscos aos titulares, salvaguardas, risco residual, aprovadores e revisão; não é checklist retroativo.

Revisão ocorre no mínimo em cada marco e quando mudar finalidade, dado, público, fornecedor, país, norma, incidente, decisão automatizada ou risco. O monitor regulatório acompanha em especial direitos dos titulares, ECA Digital/aferição etária e regras de plataformas digitais publicadas após esta revisão.

## Gate de prontidão LGPD

Dados pessoais reais permanecem bloqueados até existir evidência de todos os itens:

| Evidência | Gate/owner |
| --- | --- |
| pessoa jurídica controladora, encarregado/substituto e canais públicos | `GOV-004`, Legal + Privacy |
| ROPA completo e matriz de agentes por operação | `OPEN-004/008`, Privacy + Legal |
| base escolhida por finalidade, LIA e RIPD aplicáveis | `OPEN-004`, Legal + Privacy + Product |
| público/idade e incidência do ECA Digital decididos | `OPEN-014`, Product + Legal + Privacy |
| tabela de retenção, jobs de descarte, holds e restore testados | `OPEN-008`, Privacy + Engineering + Operations |
| fornecedores, países, suboperadores, contratos e mecanismo internacional | `OPEN-006/007`, Privacy + Security + Legal |
| termos, avisos, aceite, consentimentos e cookies separados/testados | `GOV-005`, Legal + Product + Engineering |
| direitos com prazos, autenticação, propagação e teste ponta a ponta | `OPEN-008`, Privacy + Support + Engineering |
| acesso mínimo, redaction, upload privado, segurança e revisão de privilégios | M1/M2/M6, Security + Engineering |
| runbook/tabletop de incidente dentro dos prazos e contatos vigentes | M6, Security + Privacy + Legal |
| parecer jurídico brasileiro e risco residual formalmente aceito | `OPEN-004/008/014`, Legal + responsáveis nomeados |

Ausência de item mantém o tratamento correspondente desligado; disclaimer, checkbox genérico ou exceção verbal não remove o bloqueio.

## Adendo 19/08/2026 — jornada CNH, saúde, mapa e operação nacional

A ampliação para clínicas, médicos, psicólogos, mapa nacional e jornada CNH aumenta o risco de privacidade e **não autoriza ampliar coleta por conveniência**. A implementação segue privacy by design e minimização desde o schema/API.

### Controles obrigatórios adicionais

1. **Separação entre descoberta e dado de saúde.** Procurar clínica, médico ou psicólogo não autoriza coletar diagnóstico, laudo, resultado de exame, deficiência, condição clínica ou motivo médico. Resultado/laudo de exame fica fora do MVP salvo decisão jurídica, ROPA, hipótese do art. 11, RIPD e controles específicos.
2. **Geolocalização minimizada.** Localização exata do aluno é privada e efêmera sempre que possível. Mapa público usa ponto aproximado, área, cidade ou cluster. Mapa de demanda só publica agregados com limiar mínimo e proteção contra combinação de filtros/reidentificação.
3. **Credenciais e documentos profissionais.** CPF, documentos, números completos não necessários ao público e evidências de credenciamento ficam privados. Perfil público mostra somente atributos necessários à confiança e descoberta.
4. **Fontes públicas não equivalem a uso irrestrito.** Lista pública de DETRAN/SENATRAN pode servir como evidência de verificação somente após registrar finalidade, base legal, termos/capacidade de acesso, campos mínimos, atualização e política de contato. Dados públicos não autorizam prospecção massiva automática por padrão.
5. **Clínicas e profissionais como agentes.** A classificação controlador/operador/controlador independente deve ser decidida por operação. Encaminhar aluno a clínica/profissional não transfere automaticamente à InstrutorPro responsabilidade pelo tratamento clínico posterior, nem a elimina; contratos e fluxos reais determinam os papéis.
6. **Agendamento de exame.** Antes de enviar dados do aluno a clínica/profissional, definir campos mínimos, finalidade, base legal, transparência, retenção, destinatário e responsabilidade por direitos. Dados clínicos não retornam para a InstrutorPro por padrão.
7. **Jornada CNH.** O progresso exibido é orientativo. Não coletar prova documental de cada etapa apenas para “completar” a timeline quando não houver necessidade funcional/legal aprovada.
8. **Consentimento não é base universal.** Marketing, cookies opcionais e finalidades realmente opcionais usam mecanismo separado quando consentimento for a hipótese aprovada; contrato/legítimo interesse/obrigação legal devem ser analisados por finalidade no ROPA.
9. **Direitos do titular.** Deve existir canal para confirmação, acesso, correção, informação sobre compartilhamentos, oposição/revisão quando aplicável, portabilidade conforme regulamentação e eliminação quando cabível, com autenticação proporcional e propagação a operadores.
10. **Segurança.** MFA para backoffice e ações sensíveis; RBAC/ABAC por objeto; criptografia em trânsito e repouso; secrets fora do repositório; upload privado com scan/quarentena; logs redigidos; rate limit; trilha append-only para verificação, acesso administrativo e compartilhamentos relevantes.
11. **Retenção.** Nenhum prazo é inventado no código. Cada operação recebe trigger, prazo aprovado, exceção legal/defesa e rotina de descarte/anonymização verificável.
12. **Fornecedores e transferência internacional.** Mapas, analytics, cloud, mensagens, storage e pagamentos passam por inventário de subprocessadores, países, mecanismo de transferência e contrato antes de dados reais.
13. **Menores.** Cadastro operacional e coleta em demanda/mapa/marketplace permanecem bloqueados no MVP. `OPEN-014` continua gate explícito para expansão futura e não há mecanismo definitivo de aferição aprovado.
14. **RIPD/LIA.** Geolocalização em escala, matching, dados relacionados a saúde/acessibilidade, perfilamento, fontes governamentais e qualquer nova automação de risco devem ser avaliados antes de produção; quando aplicável, produzir RIPD/LIA e registrar risco residual.

### Gate LGPD para clínicas/médicos/psicólogos

Nenhum dado real é compartilhado com clínica, médico ou psicólogo até existirem: operação no ROPA; base legal aprovada; aviso de privacidade correspondente; matriz de agentes; contrato/termos aplicáveis; minimização de payload; retenção; fluxo de direitos; controles de segurança; teste de autorização; e decisão explícita sobre se a InstrutorPro apenas descobre/encaminha ou também agenda/processa pagamento.

### Referência regulatória

A ANPD orienta que adequação envolve mapear e registrar operações, identificar bases legais/finalidades, adotar medidas técnicas/administrativas e manter canal com titulares. A classificação de controlador/operador decorre da atividade real, e a atuação do encarregado é regulada pela Resolução CD/ANPD nº 18/2024. O projeto adota esses pontos como gates de governança, sem presumir dispensa de pequeno porte.

## Fontes públicas de DETRAN/SENATRAN e perfis profissionais — regra do MVP

A existência de lista, portaria, Diário Oficial ou consulta pública não elimina a incidência da LGPD. Para a primeira onda técnica/comercial (RS, SC, SP, RJ e ES) e para qualquer UF da matriz regulatória, eventual coleta de dados de profissionais a partir de fonte oficial segue estes controles:

1. **Descoberta não é publicação automática.** Um registro encontrado em fonte oficial pode alimentar verificação ou fila interna, mas não cria automaticamente perfil comercial público na InstrutorPro.
2. **Minimização.** Persistir somente atributos necessários para provar autorização/credenciamento e permitir descoberta segura: tipo profissional, nome profissional quando necessário, UF/município, identificador público estritamente necessário, status, validade quando publicada, fonte e `verified_at`.
3. **Sem prospecção massiva por padrão.** Telefone, e-mail, endereço residencial e outros contatos obtidos de fonte pública não entram automaticamente em campanhas. Prospecção exige finalidade, base legal, LIA quando aplicável, transparência, oposição e política comercial aprovadas.
4. **Reivindicação de perfil.** Quando viável, a experiência preferida é `CLAIM_PROFILE`: a InstrutorPro mostra somente o mínimo permitido/necessário e convida o próprio profissional a autenticar, complementar e aceitar os termos antes da publicação comercial completa.
5. **Proveniência obrigatória.** Todo dado importado/confirmado guarda `source_authority`, `source_url`, `source_checked_at`, `verification_method`, `rule_version` e, quando necessário, hash/evidência sem copiar conteúdo excessivo.
6. **Correção e contestação.** O profissional pode contestar divergência. A InstrutorPro não altera o registro oficial; corrige/despublica sua própria projeção e orienta o titular a procurar o órgão competente quando a origem do erro for a fonte pública.
7. **Expiração/revalidação.** Status oficial não é eterno. Perfis dependentes de credencial têm `next_verification_at`; fonte indisponível gera pendência, não conclusão adversa automática.
8. **Mapa e localização.** Clínica pode exibir endereço comercial validado. Profissional pessoa física não terá residência ou coordenada privada inferida/exposta; mapa usa local de atendimento declarado/autorizado ou granularidade reduzida.

No `MAPA ONLINE 01`, todos os pontos são sintéticos. O schema separa
`private_location` de `public_service_location`, o seed mantém o campo privado
nulo e a API não o serializa. Não há geolocalização do navegador e o geocoder
local não transmite texto. Isso não fecha `OPEN-007` para produção.
9. **Dados de saúde do candidato.** Busca por clínica/médico/psicólogo, clique, agendamento e etapa da jornada não devem ser usados para inferir diagnóstico, condição de saúde ou perfil sensível. Resultado de exame/laudo não é coletado no MVP.
10. **Scraping e automação.** Nenhum crawler autenticado, quebra de CAPTCHA, contorno de rate limit ou uso de endpoint não documentado é requisito do produto. Automação só entra após revisão de termos, finalidade, segurança, proporcionalidade e capacidade técnica da fonte.

Antes de sincronização em lote de fonte pública, `OPEN-008` deve conter o prazo de retenção e `OPEN-004`/ROPA deve registrar finalidade e hipótese legal da operação específica.


## Inferência de saúde por navegação

A simples busca, visualização ou clique do usuário em clínica, médico, psicólogo ou etapa da Jornada CNH não deve ser convertido em perfil de saúde, diagnóstico presumido ou segmentação publicitária sensível. Telemetria deve ser minimizada e separada de qualquer dado clínico. Resultados de exame, laudos, prontuários e conclusões psicológicas permanecem fora do MVP.

## Gate mínimo LGPD — busca de instrutores por localização (29/08/2026)

Status: **APROVADO PARA DADOS SINTÉTICOS E PARA O DESENHO TÉCNICO MINIMIZADO; PENDENTE PARA DADOS/PESSOAS REAIS**.

Este recorte não declara conformidade LGPD integral. Ele cobre somente a operação: visitante informa cidade, bairro ou CEP → a plataforma geocodifica de forma minimizada → consulta área pública de serviço → retorna instrutores elegíveis/publicados → exibe mapa/lista e perfil. Solicitação de contato/aula, demanda do aluno, pagamento, marketing e integrações oficiais são operações diferentes e não herdam este gate.

### Registro da operação de tratamento — ROPA mínimo

| Campo | Registro aprovado ou estado atual |
| --- | --- |
| identificador | `ROPA-DISCOVERY-LOCATION-001` |
| finalidade | permitir que o visitante encontre instrutores em uma região informada explicitamente |
| titulares | visitante/aluno pesquisando e instrutor cuja área de serviço é exibida |
| dados do visitante | texto explícito de cidade/bairro/CEP; coordenada derivada apenas durante a consulta; IP/user-agent somente no registro técnico legalmente aplicável |
| dados do instrutor | nome profissional e atributos públicos permitidos; área/ponto público de serviço autorizado; nunca residência por padrão |
| dados excluídos | CPF, CNH, nascimento, telefone, documento, endereço residencial, GPS automático, saúde, diagnóstico, laudo, prontuário e resultado psicológico |
| fontes | entrada explícita do visitante; área de serviço declarada/autorizada pelo instrutor; elegibilidade vem de processo separado |
| sistemas | frontend, API/selector público, PostGIS e MapTiler condicionado em `ADR-047` |
| compartilhamentos | MapTiler recebe consulta minimizada somente após condições contratuais de `OPEN-007`; nenhum instrutor recebe a consulta individual |
| controlador | pessoa jurídica operadora declarada para o M1, CNPJ `10.280.826/0001-05`; razão social/representação pendentes de comprovação em `GOV-004` |
| operadores/suboperadores | infraestrutura/geocoding/observabilidade `PENDING` até seleção, contrato, países e subprocessadores |
| canal de direitos | `focusgtba@gmail.com`, canal inicial do M1; Encarregado/DPO formal é exigido, mas ainda não foi designado |
| owner | Gilmar Cesar Alves nas funções provisórias de Product/Privacy/Legal/Operations; aprovações externas permanecem separadas quando exigidas |

### Necessidade e minimização

- pesquisa inicial deve funcionar sem conta e sem autenticação;
- entrada permitida: cidade, bairro ou CEP digitado pelo visitante; o produto pode aceitar combinação equivalente menos precisa quando suficiente;
- GPS preciso automático e pedido de permissão do navegador permanecem desativados;
- endereço completo é rejeitado ou reduzido antes de log/cache; campo livre não pode ser reutilizado para perfil, marketing ou inferência;
- coordenada derivada existe em memória durante a consulta e não compõe histórico de negócio;
- logs, traces, métricas, analytics, chaves de cache e erros não carregam texto bruto de busca, CEP completo ou coordenada exata;
- telemetria de produto permanece desligada neste recorte. Agregação futura exige finalidade própria, limiar aprovado em `OPEN-015` e revisão deste ROPA;
- registro de acesso à aplicação, quando aplicável, é operação técnica separada: sua retenção legal não autoriza guardar a consulta geográfica.

### Base legal proposta

1. **Busca anônima iniciada pelo visitante:** legítimo interesse, art. 7º, IX, proposto para dado não sensível e restrito à resposta imediata solicitada. O interesse concreto é disponibilizar descoberta regional; a expectativa é compatível com o ato de digitar uma região; não há perfilização, marketing, contato ou histórico. A adoção para dado real depende de LIA aprovada por Legal/Privacy e da identificação do controlador.
2. **Área pública de serviço do instrutor:** contrato/procedimentos preliminares, art. 7º, V, proposto para publicar a área escolhida pelo próprio profissional como parte do serviço solicitado. A autorização operacional granular não é tratada automaticamente como consentimento LGPD. Legal/Privacy deve validar a base e o aviso antes do primeiro profissional real.
3. **Auditoria da autorização/revogação:** exercício regular de direitos e legítimo interesse de responsabilização são candidatos; a base final e o prazo permanecem `PENDING` em `OPEN-004/008`.

Consentimento não é adotado como base universal. Se Legal/Privacy decidir que a publicação opcional exige consentimento, a operação deverá usar `ConsentRecord`, texto granular e retirada equivalente antes de dados reais.

### Retenção e descarte

| Dado | Regra deste recorte |
| --- | --- |
| texto/coordenada da pesquisa | memória da requisição/sessão; descarte ao terminar; sem histórico individual |
| cache técnico | somente chave reduzida/não reversível ou região normalizada; TTL técnico a aprovar e sem associação a pessoa/conta |
| telemetria de demanda | não coletada; agregação futura depende de `OPEN-015` |
| área pública do instrutor | enquanto autorização operacional e publicação estiverem vigentes |
| evidência de autorização/revogação | preservar finalidade, versão, ator e timestamps pelo prazo de auditoria/defesa ainda `PENDING` em `OPEN-008` |
| revogação | retirar imediatamente das novas buscas dependentes da localização; histórico mínimo não é apagado |
| registro de acesso à aplicação | operação segregada e prazo legal aplicável; não inclui consulta ou coordenada |

O prazo exato de cache, auditoria pós-revogação, backup e descarte por operador permanece pendente. Por isso, a retenção está suficiente para desenvolvimento sintético, não para produção real.

### Localização pública do instrutor

`PRIVATE/RESIDENTIAL LOCATION` e `PUBLIC SERVICE LOCATION` permanecem campos e finalidades separados. Residência nunca é copiada, inferida ou geocodificada para exposição pública por padrão. Para entrar em busca real, a área de serviço exige:

- instrutor elegível e publicado pela policy aplicável;
- ação afirmativa do próprio profissional ou ator autorizado;
- finalidade `DISCOVERY_PUBLIC_SERVICE_LOCATION`;
- versão/hash do aviso ou política apresentada;
- ponto/área e precisão pública escolhidos;
- ator, data/hora, origem e trilha de auditoria;
- revogação acessível, com despublicação das novas buscas sem apagar histórico necessário;
- selector público deny-by-default e serializer sem localização privada.

Autorização de localização não concede papel, credenciamento, elegibilidade ou publicação.

### Segurança, direitos e riscos

Controles mínimos: TLS; rate limit e proteção contra enumeração; precisão pública mínima; selector/serializer allowlist; segregação entre localização privada e pública; logs redigidos; acesso administrativo auditado; cache sem texto bruto; testes de revogação, IDOR, radius scraping, erro do geocoder e ausência de residência.

Direitos aplicáveis incluem informação, confirmação/acesso quando houver dado associado, correção da área pelo instrutor, oposição ao legítimo interesse, retirada/revogação quando aplicável e eliminação/bloqueio cabíveis. O canal inicial do M1 é `focusgtba@gmail.com`; sua homologação no aviso e no procedimento de atendimento continua necessária. A definição não nomeia Encarregado/DPO.

| Risco | Mitigação | Estado residual |
| --- | --- | --- |
| reidentificar residência do instrutor | área/ponto de serviço escolhido, precisão reduzida e residência separada | aceite formal de Privacy pendente |
| criar histórico de deslocamento/interesse do aluno | consulta efêmera, sem login obrigatório, sem GPS e sem telemetria individual | baixo no desenho; validar implementação |
| fornecedor receber consulta/coordenada | backend adapter, minimização, contrato, países/suboperadores e retenção | MapTiler escolhido; ativação bloqueada pelas condições de `OPEN-007/006` |
| enumeração/stalking de profissionais | apenas publicáveis, precisão mínima, rate limit e anti-scraping | teste e limiares pendentes |
| continuar visível após revogação | retirada transacional das novas buscas, auditoria e teste de reconciliação | validar código antes de dado real |
| inferência de saúde ou perfil sensível | busca exclusiva de instrutor, sem saúde/analytics/marketing | proibido por policy |
| acesso por menor | operação real permanece bloqueada por `OPEN-014` | não resolvido neste gate |

### LIA e RIPD

- **ROPA:** operação e campos mínimos registrados acima; aprovação nominal dos responsáveis e matriz final de agentes permanecem pendentes.
- **LIA:** necessária pela decisão interna do projeto antes de usar legítimo interesse. O controlador e o owner provisório estão identificados; o teste preliminar é favorável apenas ao desenho estrito — finalidade específica, consulta iniciada pelo visitante, dado não sensível, ausência de conta/GPS/histórico/marketing e salvaguardas — mas a LIA ainda exige aprovação humana registrada e validação jurídica externa quando aplicável.
- **RIPD:** recomendado pela ANPD para tratamento potencialmente de alto risco e obrigatório pela política interna antes de geolocalização em escala. Deve ser concluído antes do piloto com dados reais, mesmo sem GPS preciso, cobrindo fluxo, provider, escala, enumeração, retenção, direitos e risco residual.

### Resultado A–F

| Item | Status | Condição ou gate restante |
| --- | --- | --- |
| A — busca com dados sintéticos | `LIBERADA` | manter fixtures marcadas, geocoder local e ausência de PII |
| B — busca do aluno sem login | `LIBERADA PARA IMPLEMENTAÇÃO/TESTE SINTÉTICO`; `BLOQUEADA PARA DADO REAL` | LIA aprovada, controlador/canal reais, aviso contextual, segurança e teste |
| C — cidade/bairro/CEP informado | `LIBERADO PARA IMPLEMENTAÇÃO/TESTE SINTÉTICO`; `BLOQUEADO PARA DADO REAL` | MapTiler escolhido; faltam aceite contratual/LGPD de `OPEN-007` e condições de B |
| D — geolocalização precisa automática | `BLOQUEADA` | fora deste recorte; exigiria nova decisão, RIPD e revisão de necessidade/base |
| E — área de atendimento autorizada do instrutor | `LIBERADA COMO POLÍTICA E PARA SINTÉTICO`; `BLOQUEADA PARA PROFISSIONAL REAL` | base/aviso aprovados, elegibilidade, GOV-002/003, controlador/canal, retenção, segurança e teste de revogação |
| F — primeiro instrutor real | `BLOQUEADO` | GOV-002 por linha, GOV-003 tabletop, GOV-004/005, OPEN-004/006/007/008/014 aplicáveis, LIA/RIPD e homologação técnica/operacional |

### Caminho mínimo e card de código

O caminho mínimo para um instrutor real é: escolher uma UF/linha regulatória nominalmente aprovada → concluir GOV-003 → identificar controlador/canal e aprovar aviso/base/LIA/RIPD/retenção/provider → homologar elegibilidade/publicação e revogação → ativar lote controlado sem pagamento.

Os cards relacionados são `MKT-001` (área geográfica) e `MKT-004` (busca/perfil minimizados). Eles **não estão liberados para implementação real**, pois dependem de `CRD-007` e `OPEN-007`; a busca sintética equivalente já existe no `MAPA ONLINE 01`. Nenhum novo card de código é iniciado por este gate.
