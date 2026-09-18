# Tratamentos de dados do piloto controlado — Fatia 8E

Versão: `1.0`  
Data de avaliação: `18/09/2026`  
Escopo: `CONTROLLED_PILOT` em Porto Alegre/RS  
Resultado: `OPEN-008_CONTROLLED_PILOT=BLOCKED` e `OPEN-008_FULL_PRODUCTION=BLOCKED`

Este registro operacional complementa `LGPD.md` e a matriz de retenção da Fatia 8D. Ele não é
parecer jurídico, não aprova base legal e não amplia `SCOPE.md`, `DECISIONS.md` ou `PILOT.md`.

## Escopo e agente de tratamento

A organização operadora InstrutorProCNH é **controladora confirmada por decisão humana** para as
finalidades próprias de conta, autenticação, marketplace, segurança, auditoria, analytics,
direitos do titular e verificação/publicação interna. Permanecem pendentes a comprovação completa
da organização e a indicação formal do encarregado previstas em `ADR-050` e `ADR-052`.

O piloto exclui documentos profissionais, publicação automática, pagamentos, cobrança PRO,
crianças e `FULL_PRODUCTION`. Adolescentes continuam bloqueados até existir fluxo específico
aprovado. CPF de aluno, residência do instrutor, dado bancário, dado de pagamento, conversa de
WhatsApp e coordenada precisa persistida não integram o recorte.

### Fornecedores e destinatários

| Fornecedor/destinatário | Uso no piloto | Papel contratual | Estado/evidência |
| --- | --- | --- | --- |
| hospedagem/VPS | infraestrutura da aplicação e banco | não presumido | `PENDING_CONTRACT_REVIEW`; contrato, países, suboperadores, retenção e saída não constam como aprovados |
| MapTiler | geocodificação/tile por adapter do backend | não presumido | `PENDING_CONTRACT_REVIEW`; condições de `OPEN-007` continuam abertas |
| WhatsApp/Meta | destino externo escolhido pelo titular após o redirecionamento | não presumido | `PENDING_CONTRACT_REVIEW`; a plataforma registra apenas intenção de contato |
| provedor do canal de privacidade | recebimento inicial de solicitações | não presumido | `PENDING_CONTRACT_REVIEW`; canal existe, mas o papel contratual não foi confirmado |
| PostgreSQL/PostGIS e Redis autogeridos | componentes internos da mesma infraestrutura | `NOT_APPLICABLE` como fornecedor separado | acesso restrito pela operação; não autoriza terceiro tratamento |
| GitHub | código-fonte, sem dados do piloto | `NOT_APPLICABLE` | dados pessoais do piloto não devem ser versionados |

`PENDING_CONTRACT_REVIEW` não significa operador nem controlador confirmado. Nenhuma cláusula/DPA
foi presumida.

## Matriz de tratamento

`RETENTION_PERIOD_PENDING_LEGAL_REVIEW` significa que não há número pós-encerramento aprovado.
Durante o piloto, a regra conservadora é manter somente enquanto a conta/processo estiver ativo,
restringir no encerramento e submeter a destinação a `PrivacyRequest`, sem eliminação automática
de evidência que possa possuir exceção válida.

| Processo | Titular | Dados mínimos | Finalidade | Base legal proposta, não aprovada | Papel | Retenção e evento | Destino final/exceções | Status/revisão |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A. Conta/autenticação | aluno/instrutor | identificadores de conta, e-mail, credenciais derivadas, sessões e eventos de segurança | criar conta, autenticar e proteger acesso | contrato/procedimentos preliminares; segurança/fraude quando aplicável | controlador | criação até encerramento; pós-encerramento `RETENTION_PERIOD_PENDING_LEGAL_REVIEW` | `DELETE` para sessão/segredo dispensável; `RETAIN_WITH_JUSTIFICATION` ou `PENDING_REVIEW` para segurança/disputa | `LEGAL_REVIEW_RECOMMENDED`; bloqueado pelo gate transversal ADR-019/052 |
| B. Perfil do aluno | aluno | nome e dados cadastrais estritamente necessários; sem CPF por padrão e sem localização precisa persistida | operar a conta e permitir descoberta solicitada | contrato/procedimentos preliminares | controlador | perfil ativo até encerramento/correção; período posterior pendente | `DELETE`/`ANONYMIZE`; exceção somente documentada | `LEGAL_REVIEW_RECOMMENDED`; bloqueado pelo gate transversal |
| C. Perfil profissional | instrutor | nome público, contato operacional, categoria, oferta, veículo e área autorizada; sem residência/documento | onboarding, revisão e exibição manualmente aprovada | contrato/procedimentos preliminares; interesse legítimo apenas após LIA | controlador | cadastro até despublicação/encerramento; período posterior pendente | despublicar imediatamente; depois `DELETE`, `ANONYMIZE` ou exceção justificada | `BLOCKED`; LIA, encarregado e provider ainda pendentes |
| D. Termos/aceites | aluno/instrutor | conta, versões vigentes, hashes, instante e request ID | comprovar ciência e versão aceita | contrato/procedimentos preliminares e exercício regular de direitos | controlador | aceite até fim da relação; período posterior pendente | `RETAIN_WITH_JUSTIFICATION`/`PENDING_REVIEW`; nunca apagar automaticamente | `LEGAL_REVIEW_RECOMMENDED`; implementação transacional testada |
| E. PrivacyRequest | titular/representante | identidade mínima, tipo, estado, decisão, justificativa e trilha | autenticar, atender e demonstrar direito | obrigação legal/regulatória e exercício regular de direitos | controlador | abertura até encerramento; período posterior pendente | dados-alvo classificados em `DELETE`, `ANONYMIZE`, `RETAIN_WITH_JUSTIFICATION` ou `PENDING_REVIEW` | `OPERATIONALLY_DEFINED` no fluxo; prazo pós-encerramento requer revisão |
| F. Audit logs | usuários/operadores | ator, ação, objeto, resultado, request ID e instante; sem payload/segredo | segurança, responsabilização e defesa | obrigação aplicável, segurança/fraude e legítimo interesse após LIA | controlador | evento até expiração; janela não aprovada | `ANONYMIZE`/`DELETE`; legal hold/incidente/disputa somente com justificativa | `BLOCKED`; classes e prazo pós-evento não aprovados |
| G. Marketplace analytics | visitante/aluno/instrutor | evento deduplicado, sessão e janela agregada; sem telefone, conteúdo, fingerprint ou coordenada precisa | medir funcionamento básico do piloto | legítimo interesse sujeito a LIA | controlador | evento até agregação irreversível; janela bruta pendente | `ANONYMIZE` por agregação ou `DELETE` | `BLOCKED`; LIA e retenção bruta ausentes |
| H. Busca/localização | visitante/aluno | cidade, bairro ou CEP digitado; GPS somente por ação explícita e sem persistência precisa | responder à busca solicitada | pré-contrato/contrato quando autenticado; legítimo interesse proposto para visitante, sujeito a LIA | controlador | consulta até resposta; somente granularidade reduzida em analytics | descartar consulta individual; exceção de segurança sem conteúdo desnecessário | `BLOCKED`; LIA/RIPD e `OPEN-007` pendentes |
| I. Evento WhatsApp | visitante/aluno | identificador da oferta, intenção, request/session ID e instante; sem telefone/conversa | abrir contato externo solicitado e medir intenção | procedimento preliminar; analytics somente após LIA | controlador do evento próprio; papel externo não presumido | evento até deduplicação/agregação; prazo pendente | `ANONYMIZE`/`DELETE`; interação posterior ocorre fora da plataforma | `BLOCKED`; provider e finalidade analítica pendentes |
| J. Verification/PublicationDecision | instrutor/operador | status, autoridade, método, proveniência mínima, operador, decisão e instante; sem arquivo documental | revisão administrativa interna e publicação manual segura | contrato, segurança e exercício regular de direitos; interesse legítimo após LIA quando aplicável | controlador | decisão durante validade e despublicação; período posterior pendente | `RETAIN_WITH_JUSTIFICATION`/`PENDING_REVIEW`; despublicação imediata, sem exclusão automática da trilha | `BLOCKED`; base/retenção e gate de governança pendentes |

## Localização, WhatsApp e encerramento

- Busca manual aceita somente cidade, bairro ou CEP. GPS exige ação explícita, serve à consulta
  solicitada e não deve gerar persistência de coordenada precisa. Analytics usa granularidade
  reduzida. Residência do instrutor nunca é pública.
- O evento WhatsApp registra somente intenção. Conteúdo, áudio, imagem, mensagem, conversa e
  telefone em analytics são proibidos; depois do redirecionamento há serviço externo.
- `PrivacyRequest` é o mecanismo de encerramento. Cada dado recebe decisão `DELETE`, `ANONYMIZE`,
  `RETAIN_WITH_JUSTIFICATION` ou `PENDING_REVIEW`, com ator, fundamento e data. Aceites e auditoria
  não são apagados automaticamente.

## Reavaliação objetiva do OPEN-008

Os tratamentos, minimização, canal, termos, política, aceite, eventos de retenção e exceções estão
agora documentados. O gate não pode receber `PASS`, porém, porque tratamentos indispensáveis ao
piloto continuam `BLOCKED`: `ADR-019/052` exigem encarregado e LIA/RIPD aplicáveis antes de dados
reais; `OPEN-007` ainda não confirmou os provedores; e não existe período/decisão final para logs,
analytics, localização e evidências. A política operacional não substitui essas aprovações.

Consequentemente:

- `OPEN-008_CONTROLLED_PILOT=BLOCKED`;
- `OPEN-008_FULL_PRODUCTION=BLOCKED`;
- nenhuma capability `REAL_*` pode ser ligada;
- nenhum deploy, migration de VPS ou cadastro real é autorizado por esta avaliação.

Mesmo que o OPEN-008 fosse posteriormente aprovado, `OPEN-009` e `OPEN-010` continuariam gates
independentes para início do piloto.

### Matriz final de capabilities

| Capability | Status | Evidência/bloqueador específico |
| --- | --- | --- |
| `REAL_ACCOUNT_REGISTRATION` | `BLOCKED` | `ADR-019/052`: encarregado formal e governança prévia a dado real ainda pendentes |
| `REAL_PERSONAL_DATA` | `BLOCKED` | retenção pós-encerramento e decisão das exceções ainda não aprovadas |
| `REAL_STUDENT_USE` | `BLOCKED` | depende de `REAL_ACCOUNT_REGISTRATION` e `REAL_PERSONAL_DATA`, ambos bloqueados |
| `REAL_INSTRUCTOR_REGISTRATION` | `BLOCKED` | perfil/verificação dependem de base, LIA quando aplicável e retenção de evidência aprovadas |
| `REAL_MARKETPLACE_SEARCH` | `BLOCKED` | LIA/RIPD da busca e condições contratuais MapTiler de `OPEN-007` pendentes |
| `REAL_WHATSAPP_CONTACT` | `BLOCKED` | papel/revisão do serviço externo e retenção do evento ainda pendentes |
| `REAL_MARKETPLACE_ANALYTICS` | `BLOCKED` | LIA e janela de retenção do evento bruto ainda pendentes |
| `REAL_DOCUMENT_UPLOADS` | `BLOCKED` | expressamente fora da Fatia 8E |
| `REAL_AUTOMATIC_PUBLICATION` | `BLOCKED` | expressamente fora; publicação continua decisão administrativa separada |
| `REAL_PAYMENTS` | `BLOCKED` | expressamente fora; `OPEN-005` não resolvido |
| `REAL_PRO_BILLING` | `BLOCKED` | expressamente fora da Fatia 8E |

## Referências oficiais de controle

- ANPD, *Guia Orientativo das Hipóteses Legais de Tratamento de Dados Pessoais — Legítimo
  Interesse* (finalidade, necessidade, balanceamento e salvaguardas).
- Resolução CD/ANPD nº 18/2024, regulamento da atuação do encarregado.
- ANPD, Perguntas Frequentes sobre término do tratamento e hipóteses de conservação.
