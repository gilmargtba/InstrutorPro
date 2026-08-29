# GOV-003 — Política de revisão e aplicação ativa

Status: **SLAs OPERACIONAIS INICIAIS APROVADOS; TABLETOP M1 EXECUTADO COM RESULTADO FAIL** — 29/08/2026.

## Objetivo

Definir como a InstrutorPro recebe, revisa, decide, reavalia e suspende aplicações de instrutores sem confundir decisão interna com autorização oficial. Esta política não autoriza publicação: depende da matriz `GOV-002` aprovada para a jurisdição e categoria.

## Princípios obrigatórios

1. Autorização/credenciamento oficial vigente é evidência necessária; a InstrutorPro não concede, certifica nem homologa essa condição.
2. Deny by default: requisito ausente, conflitante, vencido ou sem fonte aplicável impede aprovação/publicação.
3. O próprio instrutor, pessoa relacionada ou quem alterou a evidência fora do fluxo não pode revisá-la.
4. Documento, aplicação, decisão interna, condição oficial e publicação possuem estados separados.
5. Toda decisão registra regra e versão, jurisdição, categoria, evidências consideradas, ator, data, motivo estruturado e `AuditEvent`.
6. Arquivos permanecem em storage privado, passam por quarentena/scan e nunca aparecem em URL pública.
7. Indisponibilidade da fonte oficial não equivale automaticamente a perda de autorização; gera pendência ou suspensão preventiva conforme risco e última evidência válida.
8. Rejeição ou suspensão definitiva por suspeita, inconsistência ou fraude exige revisão humana. Expiração objetiva pode retirar publicação automaticamente, com motivo e contestação.

## Estados e transições

```text
DRAFT -> SUBMITTED -> UNDER_REVIEW
UNDER_REVIEW -> PENDING_INFORMATION -> SUBMITTED
UNDER_REVIEW -> APPROVED | REJECTED
APPROVED -> SUSPENDED | EXPIRED
SUSPENDED -> UNDER_REVIEW | REJECTED
DRAFT | SUBMITTED | PENDING_INFORMATION -> WITHDRAWN
```

- `SUBMITTED`: snapshot imutável da versão submetida e conjunto de requisitos aplicáveis.
- `UNDER_REVIEW`: claim transacional por revisor autorizado; claim expira e pode ser reatribuído com auditoria.
- `PENDING_INFORMATION`: contém códigos de motivo seguros, campos/evidências esperados e prazo definido pela operação aprovada; não expõe regra antifraude.
- `APPROVED`: decisão interna sobre uma versão exata; não altera o status oficial.
- `REJECTED`: exige motivo estruturado, explicação segura e canal de nova submissão/contestação.
- `SUSPENDED`: interrompe publicação preventivamente ou por perda confirmada de requisito, sem apagar histórico.
- `EXPIRED`: requisito temporal deixou de valer; reativação exige nova evidência e nova decisão.

## Fluxo de revisão

1. Na submissão, resolver `DocumentRequirement` pela combinação jurisdição, tipo de prestador, categoria e vigência.
2. Rejeitar transacionalmente submissão sem configuração ativa ou com versões conflitantes.
3. Verificar integridade técnica: MIME/conteúdo, tamanho, hash, malware scan e promoção da quarentena.
4. Conferir identidade mínima e correspondência entre aplicação, documento e evidência oficial.
5. Registrar consulta oficial ou revisão documental em `ProviderVerification`, com fonte, método, horário, resultado e validade conhecida.
6. Avaliar cada requisito separadamente; aprovação da aplicação exige todos os requisitos obrigatórios válidos.
7. Calcular elegibilidade em policy/serviço. Nunca aceitar `approved`, `verified` ou `can_publish` do cliente.
8. Emitir decisão e auditoria na mesma transação; efeito assíncrono crítico usa `OutboxEvent` idempotente.
9. Notificar o titular com conteúdo minimizado. Falha de mensagem não desfaz a decisão e entra em retry/alerta.

## Segregação e autorização

- `OPERATIONS`: recebe, tria, acompanha SLA e executa comunicações operacionais dentro da policy.
- `COMPLIANCE`: revisa requisitos, evidências, suspensão e contestação dentro do escopo aprovado.
- `LEGAL`: interpreta impacto jurídico e aprova linguagem/encaminhamento quando escalado; não substitui Compliance na conferência factual.
- `PRIVACY_SECURITY`: trata acesso, minimização, incidente e solicitação de privacidade conforme legislação/policy aplicável.
- `ADMIN`: administra a plataforma, mas não recebe automaticamente capacidade de revisar, aprovar, rejeitar ou publicar.
- Decisão sobre objeto próprio, relacionado ou previamente manipulado fora do fluxo é negada.

Toda ação sensível deverá registrar `actor`, papel funcional efetivo, `action`, objeto, timestamp, motivo e `before/after` quando aplicável. A existência de `ADMIN` não elimina auditoria, MFA, segregação nem autorização por objeto.

## Motivos estruturados mínimos

```text
REQUIREMENT_MISSING
DOCUMENT_UNREADABLE
DOCUMENT_MISMATCH
DOCUMENT_EXPIRED
OFFICIAL_AUTHORIZATION_NOT_CONFIRMED
OFFICIAL_AUTHORIZATION_INACTIVE
SOURCE_UNAVAILABLE
VEHICLE_REQUIREMENT_NOT_MET
INFORMATION_INCONSISTENT
REVIEW_CONFLICT
POLICY_VERSION_CONFLICT
```

O código público pode ser acompanhado por texto seguro e versionado. Nota interna, indicador antifraude e documento completo não são expostos ao candidato.

## Vigência, revalidação e perda de elegibilidade

- Cada evidência conserva `checked_at`, `valid_from`, `valid_until` quando conhecidos e `next_review_at` definido pela regra aprovada.
- Não se inventa validade quando a fonte não a publica; nesse caso a matriz define periodicidade de revisão humana.
- Job idempotente identifica vencimento/revisão pendente. A transição material ocorre em serviço transacional e gera auditoria/outbox.
- Suspensão, revogação ou expiração de requisito obrigatório remove publicação; ofertas ficam indisponíveis sem apagar histórico.
- Fonte indisponível usa o último fato válido somente dentro da tolerância expressamente aprovada na matriz. Sem tolerância definida, permanece `VERIFICATION_PENDING` e não há nova publicação.

## Contestação e correção

O titular pode corrigir evidência e contestar decisão. A contestação cria caso separado, preserva a decisão anterior e é analisada por pessoa diferente quando possível. A InstrutorPro corrige sua projeção interna; não altera registro do DETRAN/SENATRAN. O prazo/SLA precisa ser aprovado por Operations/Compliance antes de usuários reais e não será hard-coded.

## Concorrência, idempotência e falhas

- claim de revisão usa lock/versão para impedir duas decisões válidas sobre a mesma submissão;
- decisão repetida com a mesma chave e payload retorna o resultado existente; payload diferente conflita;
- decisão stale falha se documento, requisito, regra ou aplicação mudou;
- falha de storage, scanner ou fonte externa não promove documento nem aprova aplicação;
- reprocessamento de outbox não duplica notificação, suspensão ou publicação;
- rollback operacional é nova decisão compensatória auditada, nunca edição destrutiva do histórico.

## Evidência para aprovação deste gate

- matriz `GOV-002` aprovada para categoria/jurisdição inicial;
- funções responsáveis atribuídas: `OPERATIONS`, `COMPLIANCE`, `LEGAL`, `PRIVACY_SECURITY` e `ADMIN`; nomes pessoais podem ser associados no gate de homologação/produção aplicável;
- tabletop documentado: caso feliz, ausência, divergência, expiração, fonte indisponível, conflito de revisores, self-review e contestação;
- SLA de fila, pendência e contestação aprovado;
- fornecedor/fake de storage e scanner definido no `GOV-006` antes de upload real;
- aprovação nominal, data, versão e documentos afetados registradas em `DECISIONS.md` e `CHECKPOINT.md`.

## SLAs operacionais iniciais do MVP — aprovados

| Evento | SLA interno aprovado |
| --- | --- |
| revisão de cadastro/documentação | meta de até 2 dias úteis |
| contestação — confirmação de recebimento | até 1 dia útil |
| contestação — análise inicial | até 3 dias úteis |
| contestação com consulta adicional | pode permanecer em análise, com motivo e andamento registrados |
| correção de dado cadastral | meta de até 2 dias úteis após validação da solicitação |
| solicitação de privacidade/LGPD | prazo da legislação aplicável; nenhum prazo jurídico novo é criado |

O sistema futuro deverá registrar recebimento, responsável, andamento, decisão, timestamps e evidências pertinentes. Os SLAs internos não substituem prazos legais e não são promessa pública automática. `OPERATIONS` acompanha capacidade/escalonamento; `COMPLIANCE` valida regra e evidência; `LEGAL` apoia linguagem/efeito jurídico; `PRIVACY_SECURITY` conduz os controles de privacidade e segurança.

## Checklist do tabletop obrigatório — executado em 29/08/2026

**Cenário formal:** “Um profissional publicado na InstrutorPro contesta sua suspensão após uma fonte oficial indicar possível irregularidade ou expiração de credencial.”

### Roteiro

1. `OPERATIONS` recebe o alerta e abre caso correlacionado ao profissional, fonte e regra.
2. `COMPLIANCE` preserva URL, timestamp, resposta/evidência permitida e versão da regra, sem coleta excessiva.
3. A policy avalia suspensão preventiva; quando aplicável, a decisão humana registra motivo, escopo e efeito sem alterar o fato oficial.
4. O profissional é notificado com linguagem segura, canal e prazo interno aplicável.
5. A contestação é recebida, confirmada em até 1 dia útil e preserva a decisão anterior.
6. Revisor humano diferente quando possível verifica conflito de interesse e inicia análise em até 3 dias úteis.
7. A fonte oficial e evidências complementares são consultadas manualmente, sem scraping ou endpoint não documentado.
8. Se falso positivo, decisão compensatória restaura somente o que a policy permitir, comunica o titular e mantém histórico.
9. Se irregularidade/expiração for confirmada, a suspensão é mantida com motivo, regra, evidência e via de correção futura.
10. Auditoria prova atores, papéis, ações, objeto, timestamps, motivos e mudanças de estado.
11. O titular recebe o resultado e as orientações permitidas, sem exposição de indicador antifraude ou dados de terceiros.
12. O caso é encerrado com resultado, problemas, ações corretivas e aprovação final registrada.

### Checklist específico

- [x] recebimento do alerta e correlação do caso;
- [x] preservação minimizada da evidência e da versão da fonte/regra;
- [x] fundamento e autoridade para suspensão preventiva;
- [x] notificação ao profissional;
- [x] abertura e confirmação da contestação;
- [x] revisão humana e conflito de interesse — falhou por ausência de segundo revisor;
- [x] consulta manual à fonte oficial — exercitada somente com resposta sintética;
- [x] correção de falso positivo por decisão compensatória;
- [x] manutenção motivada da suspensão quando confirmada;
- [x] trilha de auditoria completa no desenho do exercício;
- [x] comunicação final ao titular;
- [x] encerramento formal do caso com resultado `FAIL`.

### Registro da sessão

| Campo | Valor |
| --- | --- |
| data | 29/08/2026 |
| escopo | piloto M1, Porto Alegre/RS, `FIRST_LICENSE/CATEGORY_B`, cenário integralmente sintético |
| matriz/policy | `GOV_002_NATIONAL.md` e esta policy na revisão versionada no commit-base `9762cba` |
| participante humano | Gilmar Cesar Alves, atuando separadamente como `OPERATIONS`, `COMPLIANCE`, coordenação interna `LEGAL`, `PRIVACY_SECURITY` e `ADMIN` |
| facilitador/relator | Codex, sem papel de aprovador humano |
| resultado | `FAIL` — gate não aprovado para operação real |
| problemas encontrados | matriz `RS/INSTRUCTOR` não aprovada; ausência de revisor independente; validação jurídica externa pendente; storage/scanner real e seus controles não homologados |
| ações corretivas | AC-001 a AC-006 abaixo |
| aprovação final | `REPROVADO/PENDENTE`; nenhuma elegibilidade, revisão ou publicação real liberada |

O acúmulo provisório de funções foi aceito apenas para o exercício. Cada intervenção
abaixo identifica o papel funcional. Quando independência ou qualificação externa é
necessária, o exercício registra pendência em vez de presumir aprovação.

### Cronologia exercitada

| Marco | Papel | Evento/decisão simulada | Evidência preservada | Resultado |
| --- | --- | --- | --- | --- |
| T+00 | `OPERATIONS` | recebe alerta sintético e abre caso correlacionado ao profissional, fonte e regra | ID sintético, UF/categoria, código do alerta e versão da regra; sem documento ou PII em log | caso aberto |
| T+10 | `COMPLIANCE` | confere fonte, timestamp e resposta permitida | URL, horário lógico, hash/metadado e resultado sintéticos minimizados | evidência preservada; mérito pendente |
| T+20 | `COMPLIANCE` | avalia suspensão preventiva por possível expiração | `SOURCE_UNAVAILABLE` ou `DOCUMENT_EXPIRED`, conforme variante; nunca altera fato oficial | suspensão apenas simulada; produção bloqueada |
| T+30 | `OPERATIONS` | prepara comunicação segura e canal de contestação | template sem antifraude, documento ou dado de terceiro | SLA de recebimento em 1 dia útil aplicável |
| T+1d | `OPERATIONS` | confirma contestação sintética e preserva decisão anterior | ID do caso, recebimento e nova evidência sintética | contestação aberta |
| T+1d | `COMPLIANCE` | verifica self-review/conflito antes de assumir análise | ator e papéis efetivos | conflito detectado: não há segundo revisor humano |
| T+3d | `LEGAL` | avalia necessidade de interpretação jurídica | questão e escalonamento minimizados | parecer externo continua `PENDING` |
| T+3d | `PRIVACY_SECURITY` | verifica minimização, acesso e ausência de PII em logs/resposta pública | checklist sintético de acesso/log | desenho aceito para teste; homologação real pendente |
| encerramento | `ADMIN` | verifica que administração não concede poder de revisão/publicação | matriz de autorização e trilha por papel | nenhuma liberação concedida |

### Variantes e decisões por função

| Variante | Decisão exercitada | Resultado esperado pela policy |
| --- | --- | --- |
| caso feliz | `COMPLIANCE` só poderia aprovar uma versão exata com todos os requisitos e linha regulatória aprovada | bloqueado no M1 porque `RS/INSTRUCTOR` permanece `HUMAN_REVIEW_REQUIRED` |
| requisito ausente | `COMPLIANCE` registra `REQUIREMENT_MISSING`; `OPERATIONS` solicita informação com prazo | `PENDING_INFORMATION`, sem publicação |
| ilegível/divergente/vencido | `COMPLIANCE` usa motivo estruturado aplicável | pendência, rejeição ou expiração conforme evidência; revisão humana para fraude |
| fonte indisponível/contraditória | `COMPLIANCE` registra `SOURCE_UNAVAILABLE`, sem inventar validade ou tolerância | `VERIFICATION_PENDING`; nenhuma nova publicação |
| perda após publicação | `COMPLIANCE` aplica suspensão preventiva conforme regra e preserva fato oficial | retirada simulada da publicação; histórico mantido |
| decisão concorrente/stale | serviço rejeita a segunda decisão após mudança de versão/regra/evidência | conflito auditado; nenhum overwrite |
| self-review/relação/conflito | claim é negado e encaminhado a outro revisor | `PENDING`, pois não há revisor independente designado |
| regra muda durante revisão | snapshot antigo não é reaproveitado silenciosamente | decisão stale; reavaliação com nova versão |
| falha de storage/scanner | documento não é promovido | bloqueio técnico; provider/homologação continuam pendentes |
| falha de notificação/outbox | decisão não é desfeita; retry idempotente e alerta | nenhuma duplicação; homologação real pendente |
| contestação com nova evidência | decisão anterior é preservada e novo ciclo é criado | análise por pessoa diferente `PENDING` |
| falso positivo | nova decisão compensatória, nunca edição do histórico | restauração somente após policy/evidência válidas |
| irregularidade confirmada | suspensão motivada é mantida e titular recebe orientação segura | sem exposição de antifraude ou terceiros |

### Evidências do exercício

- policy, motivos, estados, SLAs e roteiro deste documento;
- matriz `GOV_002_NATIONAL.md`, na qual `RS/INSTRUCTOR` continua
  `HUMAN_REVIEW_REQUIRED`;
- atribuição humana das cinco funções para o tabletop, com acumulação provisória e
  exigência explícita de segregação;
- decisões `ADR-039`, `ADR-046` e `ADR-047` e bloqueios de `CHECKPOINT.md`;
- nenhuma evidência pessoal, documento real, consulta oficial real, scraping, upload,
  integração externa ou publicação foi utilizada.

### Achados e ações corretivas

| ID | Severidade | Achado/falha | Owner funcional | Ação corretiva / critério de fechamento | Estado |
| --- | --- | --- | --- | --- | --- |
| F-001 | crítica | `RS/INSTRUCTOR` não possui aprovação nominal em GOV-002 | `COMPLIANCE` + `LEGAL` | aprovar nominalmente a linha com fonte, vigência, gaps e owner; validação externa quando exigir interpretação jurídica | `OPEN` |
| F-002 | crítica | uma única pessoa acumula revisão, contestação e administração; não há revisor independente | `ADMIN` + `COMPLIANCE` | designar segundo revisor autorizado e testar conflito/self-review com atores distintos | `OPEN` |
| F-003 | alta | coordenação jurídica interna não substitui parecer profissional | `LEGAL` | obter validação jurídica externa para fundamentos/efeitos que a exijam | `OPEN` |
| F-004 | alta | storage privado, quarentena e scanner reais não estão selecionados/homologados | `PRIVACY_SECURITY` + `OPERATIONS` | fechar provider aplicável, contrato, falhas, retenção e teste antes de upload real | `OPEN` |
| F-005 | alta | tolerância para fonte oficial indisponível não está aprovada na linha RS | `COMPLIANCE` | definir por fonte/regra; até lá manter `VERIFICATION_PENDING` | `OPEN` |
| F-006 | média | DPO/Encarregado, controlador e canal reais permanecem pendentes | `PRIVACY_SECURITY` + `LEGAL` | fechar `GOV-004`/gate LGPD aplicável sem equiparar designação provisória a DPO formal | `OPEN` |

As ações correspondentes são `AC-001` a `AC-006`, na mesma ordem dos achados. Nenhuma
recebe prazo inventado; prazo e responsável nominal adicional exigem decisão humana.

- [x] registrar data, versão da matriz/policy, participantes por função e facilitador;
- [x] caso feliz com autorização oficial válida e todos os requisitos;
- [x] requisito obrigatório ausente e pedido de informação;
- [x] documento ilegível, divergente, vencido ou adulterado;
- [x] fonte oficial indisponível, instável ou contraditória;
- [x] autorização oficial suspensa/cancelada após publicação interna;
- [x] dois revisores concorrentes e decisão stale;
- [x] tentativa de self-review, relação pessoal ou conflito de interesse;
- [x] mudança de regra durante revisão;
- [x] falha de storage, malware scanner, notificação e outbox;
- [x] contestação com nova evidência e revisor diferente quando possível;
- [x] minimização do acesso e ausência de documento/PII em log e resposta pública;
- [x] rollback por decisão compensatória, sem editar histórico;
- [x] registrar achados, owner funcional e decisão de reprovar o gate; prazos permanecem pendentes de decisão humana.

Estado do checklist: **executado com evidência sintética e resultado `FAIL`**.

## Estado do gate

Os SLAs e papéis funcionais foram aprovados por decisão humana. O tabletop M1 foi
executado em 29/08/2026 e resultou em **`FAIL`** pelos achados abertos acima. O gate
continua reprovado antes de operação real de revisão/publicação. Nenhum estado `ACTIVE`,
elegibilidade ou publicação é liberado por este documento isoladamente.
