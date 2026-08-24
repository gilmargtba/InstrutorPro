# GOV-003 — Política de revisão e aplicação ativa

Status: **SLAs OPERACIONAIS INICIAIS APROVADOS; TABLETOP PREPARADO E NÃO EXECUTADO** — 24/08/2026.

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

## Checklist do tabletop obrigatório — não executado

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

- [ ] recebimento do alerta e correlação do caso;
- [ ] preservação minimizada da evidência e da versão da fonte/regra;
- [ ] fundamento e autoridade para suspensão preventiva;
- [ ] notificação ao profissional;
- [ ] abertura e confirmação da contestação;
- [ ] revisão humana e conflito de interesse;
- [ ] consulta manual à fonte oficial;
- [ ] correção de falso positivo por decisão compensatória;
- [ ] manutenção motivada da suspensão quando confirmada;
- [ ] trilha de auditoria completa;
- [ ] comunicação final ao titular;
- [ ] encerramento formal do caso.

### Registro da sessão — preencher somente quando executada

| Campo | Valor |
| --- | --- |
| data | `NOT_EXECUTED` |
| participantes | `NOT_EXECUTED` |
| resultado | `NOT_EXECUTED` |
| problemas encontrados | `NOT_EXECUTED` |
| ações corretivas | `NOT_EXECUTED` |
| aprovação final | `NOT_EXECUTED` |

- [ ] registrar data, versão da matriz/policy, participantes por função e facilitador;
- [ ] caso feliz com autorização oficial válida e todos os requisitos;
- [ ] requisito obrigatório ausente e pedido de informação;
- [ ] documento ilegível, divergente, vencido ou adulterado;
- [ ] fonte oficial indisponível, instável ou contraditória;
- [ ] autorização oficial suspensa/cancelada após publicação interna;
- [ ] dois revisores concorrentes e decisão stale;
- [ ] tentativa de self-review, relação pessoal ou conflito de interesse;
- [ ] mudança de regra durante revisão;
- [ ] falha de storage, malware scanner, notificação e outbox;
- [ ] contestação com nova evidência e revisor diferente quando possível;
- [ ] minimização do acesso e ausência de documento/PII em log e resposta pública;
- [ ] rollback por decisão compensatória, sem editar histórico;
- [ ] registrar achados, owner funcional, prazo e decisão de aprovar/reprovar o gate.

Estado do checklist: **não executado**. Marcar itens somente durante sessão real com evidência preservada.

## Estado do gate

Os SLAs e papéis funcionais foram aprovados por decisão humana. O tabletop está formalmente preparado, porém **não executado**; sua execução e aprovação final continuam gate antes de operação real de revisão/publicação. Nenhum estado `ACTIVE` ou publicação é liberado por este documento isoladamente.
