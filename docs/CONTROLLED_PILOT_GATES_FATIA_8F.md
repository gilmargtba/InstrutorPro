# Gates do piloto controlado — Fatia 8F

- Versão: `1.0`
- Avaliação: `18/09/2026`
- Escopo: Porto Alegre/RS, categoria B, sem pagamentos, documentos ou publicação automática
- Estado: propostas objetivas aguardando decisão do proprietário; nenhuma capability ativada

Este documento refina somente o `CONTROLLED_PILOT`. Não é parecer jurídico, não altera
`FULL_PRODUCTION` e não substitui aprovação expressa do proprietário ou revisão de fornecedor.

## 1. Encarregado e canal

`DPO_STATUS=PENDING_CLASSIFICATION`.

A Resolução CD/ANPD nº 2/2022 dispensa a indicação do encarregado para agente de tratamento de
pequeno porte elegível, desde que exista canal com o titular. O canal `focusgtba@gmail.com` já
existe, mas a dispensa ainda não pode ser aplicada porque faltam evidências para classificar a
organização. Também permanece vigente a decisão interna mais restritiva `ADR-019/052`, que somente
o proprietário pode substituir.

Informações empresariais faltantes, exatamente:

1. natureza jurídica e enquadramento atual como MEI, microempresa, empresa de pequeno porte,
   startup, pessoa jurídica sem fins lucrativos ou outra categoria admitida pelo regulamento;
2. receita bruta anual do agente e o limite legal aplicável ao enquadramento;
3. existência de grupo econômico de fato ou de direito e sua receita global;
4. confirmação de que a operação real se limita ao recorte deste piloto;
5. avaliação documentada dos critérios cumulativos de alto risco do art. 4º da Resolução nº 2:
   critério geral e critério específico;
6. responsável legal autorizado a declarar e comprovar as informações à ANPD, se solicitado.

Se o enquadramento for comprovado e o proprietário substituir `ADR-019/052`, o canal pode cumprir
o requisito aplicável sem DPO. Caso contrário, a indicação formal continua necessária.

## 2. Bases por processo

As bases abaixo são propostas operacionais e devem ser confirmadas por quem detém a decisão
jurídica. Aceite de Termos não é consentimento universal.

| Processo | Finalidade | Base proposta | LIA necessária? | Status |
| --- | --- | --- | --- | --- |
| criação da conta | executar cadastro solicitado | procedimentos preliminares/execução de contrato | não | `OPERATIONALLY_DEFINED` |
| Termos/aceites | vincular versão e provar aceite | execução de contrato e exercício regular de direitos | não | `OPERATIONALLY_DEFINED` |
| autenticação | executar acesso solicitado | execução de contrato | não | `OPERATIONALLY_DEFINED` |
| perfil do aluno | prestar conta e descoberta solicitada | execução de contrato | não | `OPERATIONALLY_DEFINED` |
| perfil do instrutor | executar onboarding e oferta solicitados | procedimentos preliminares/execução de contrato | não | `OPERATIONALLY_DEFINED` |
| busca manual | responder consulta por cidade/bairro/CEP | procedimentos preliminares solicitados pelo titular | não | `OPERATIONALLY_DEFINED`; provider pendente |
| localização | usar entrada manual; GPS somente por ação explícita, sem persistência precisa | procedimentos preliminares; consentimento apenas se futura finalidade opcional realmente exigir | não no desenho atual | `OPERATIONALLY_DEFINED` |
| link WhatsApp | abrir serviço externo por ação do usuário | procedimentos preliminares solicitados | não | `OPERATIONALLY_DEFINED`; aviso externo pendente |
| analytics mínimo | medir quatro eventos do piloto | legítimo interesse | sim | LIA-8F-01 `PASS`, condicionada à aprovação de 90 dias |
| registro legal de acesso | obrigação de guarda aplicável | cumprimento de obrigação legal/regulatória | não | `OPERATIONALLY_DEFINED` |
| telemetria adicional de auditoria/segurança | prevenção, detecção e responsabilização | legítimo interesse | sim | LIA-8F-02 `PASS`, com minimização e oposição quando aplicável |
| PrivacyRequest | atender e comprovar direitos | obrigação legal/regulatória e exercício regular de direitos | não | `OPERATIONALLY_DEFINED` |
| Verification | revisão administrativa solicitada, sem arquivo | execução de contrato e exercício regular de direitos | não | `OPERATIONALLY_DEFINED` |
| PublicationDecision | controlar publicação manual e contestável | execução de contrato e exercício regular de direitos | não | `OPERATIONALLY_DEFINED` |

## 3. Testes de balanceamento

### LIA-8F-01 — analytics mínimo do marketplace: `PASS`

- finalidade/interesse: medir funcionamento e erros do piloto, não publicidade ou perfilização;
- necessidade: somente `SEARCH_PERFORMED`, `SEARCH_RESULT_IMPRESSION`,
  `INSTRUCTOR_PROFILE_VIEWED` e `WHATSAPP_CONTACT_CLICKED`;
- dados: hash de sessão, bucket horário, evento, oferta/profissional, categoria, cidade e UF;
- expectativa: compatível com operação básica e aviso transparente do piloto;
- impacto: baixo a moderado pela possibilidade de correlação limitada;
- direitos/liberdades: sem decisão adversa, venda, marketing ou contato automatizado;
- salvaguardas: sem telefone, CPF, endereço, conteúdo, documento, GPS preciso ou fingerprint;
  deduplicação, acesso restrito, 90 dias propostos e posterior anonimização/eliminação;
- oposição: `PrivacyRequest` e interrupção de analytics não essencial quando tecnicamente aplicável;
- conclusão: interesse não prevalece sem as salvaguardas; com elas, teste interno `PASS`. A janela
  de 90 dias ainda requer aprovação do proprietário.

### LIA-8F-02 — telemetria adicional de auditoria/segurança: `PASS`

- finalidade/interesse: detectar abuso, investigar incidente e demonstrar ação administrativa;
- necessidade: metadados mínimos de ator, ação, resultado, objeto, request ID e instante;
- dados: não registrar senha, token, conteúdo, documento ou payload integral;
- expectativa: compatível com uma conta autenticada e administração segura;
- impacto: moderado se houver correlação de atividade;
- direitos/liberdades: acesso restrito, explicação e contestação; nenhuma decisão final automática;
- salvaguardas: minimização, integridade append-only, segregação, legal hold justificado e descarte;
- oposição: aplicável à telemetria facultativa, sem suprimir guarda obrigatória ou evidência válida;
- conclusão: `PASS` interno no recorte mínimo. Expansão de finalidade exige nova LIA.

## 4. RIPD

`RIPD_STATUS=NOT_REQUIRED_FOR_CURRENT_SCOPE` como avaliação operacional, não dispensa geral.

O piloto proposto tem no máximo 13 adultos, uma cidade/categoria, não usa dados sensíveis,
crianças, biometria, documentos, pagamentos, GPS persistente, tracking contínuo ou decisão
exclusivamente automatizada. Portanto, não reúne no desenho atual um critério geral e um critério
específico de alto risco conforme o parâmetro do art. 4º da Resolução nº 2/2022. A ANPD recomenda
RIPD quando o tratamento puder gerar alto risco e pode solicitá-lo.

RIPD passa a `REQUIRED_BEFORE_PILOT` se o desenho mudar para menores, dados sensíveis, localização
precisa persistente, escala relevante, vigilância de área pública ou decisão automatizada com
efeito significativo. Para expansão/`FULL_PRODUCTION`, fica `RECOMMENDED/REQUIRED_LATER` conforme
nova avaliação. Esta conclusão exige aprovação da proposta que substitua a política interna mais
restritiva registrada em `ADR-019`.

## 5. Retenção operacional proposta

Os prazos são decisões operacionais conservadoras, não “prazos exigidos pela LGPD”.

| Categoria | Enquanto ativa | Evento e pós-encerramento | Destino | Justificativa/prazo | Revisão |
| --- | --- | --- | --- | --- | --- |
| `ACTIVE_ACCOUNT` | enquanto necessário à conta | encerramento restringe acesso e abre classificação | `DELETE`/`ANONYMIZE`, salvo exceção | sem prazo final numérico até classificar obrigação/disputa | jurídica para `FULL_PRODUCTION` |
| `SHORT_LIVED_OPERATIONAL` | somente execução/sessão | fim da finalidade ou até 24 horas | `DELETE` | minimização e recuperação técnica imediata | aprovação do proprietário |
| `AUDIT_EVIDENCE` | durante piloto | fim do piloto restringe acesso | `RETAIN` somente para segurança/defesa; demais `DELETE`/`ANONYMIZE` | prazo final pendente; legal hold deve ter justificativa e owner | jurídica antes de descarte definitivo |
| `LEGAL_ACCEPTANCE` | relação ativa | encerramento bloqueia uso comum | `RETAIN` com acesso restrito | provar versão/aceite; prazo final pendente | jurídica para prazo final |
| `PRIVACY_REQUEST` | tramitação | encerramento do pedido | `RETAIN` com acesso restrito | demonstrar atendimento; prazo final pendente | jurídica para prazo final |
| `MARKETPLACE_ANALYTICS` | janela móvel do piloto | 90 dias após evento | `ANONYMIZE` irreversivelmente ou `DELETE` | proposta operacional do piloto | aprovação do proprietário |
| `PROFESSIONAL_VERIFICATION` | enquanto decisão/vigência aplicável | despublicação, revogação ou fim da relação | `RETAIN` evidência mínima; excluir excesso | defesa/contestação, sem documento | jurídica para prazo final |

Encerramento usa `PrivacyRequest` e registra `DELETE`, `ANONYMIZE`,
`RETAIN_WITH_JUSTIFICATION` ou `PENDING_REVIEW`. Backups seguem expiração operacional e não devem
ser restaurados para reativar dado eliminado fora de uma recuperação autorizada.

## 6. WhatsApp e MapTiler

### WhatsApp: `FOLLOW_UP`

A plataforma trata somente o clique/intenção, identificador da oferta e metadados mínimos. O
telefone profissional é usado para formar o link, mas não entra no evento analítico; conteúdo,
áudio, imagem e conversa não são lidos ou armazenados. Após o clique, há interação externa por
escolha do usuário. A revisão do serviço externo e um aviso contextual são follow-up para este
link simples, não blocker do cadastro. Tornam-se blocker se houver SDK, API, mensageria integrada,
sincronização de contatos ou ingestão de conversa.

### MapTiler: `PENDING_VENDOR_REVIEW`

- técnica: chave e adapter backend existem; navegador não recebe a chave;
- dados enviados: consulta digitada (cidade/bairro/CEP) no geocoding, coordenadas `z/x/y` do tile,
  IP público da VPS e User-Agent do servidor; não são enviados conta, telefone ou perfil;
- documentos faltantes: termos/plano aplicável, aviso/política do tratamento, DPA quando o papel e
  o tratamento o exigirem, subprocessadores, países/regiões, retenção de logs/consultas, mecanismo
  de transferência internacional aplicável e papel do fornecedor;
- transferência: possível, mas não confirmada sem região/contrato/logs do fornecedor;
- impacto: bloqueia somente `REAL_MARKETPLACE_SEARCH` que use MapTiler. Conta, perfil, aceite e
  PrivacyRequest não dependem dele; fallback local por cidade/lista deve ser avaliado separadamente.

## 7. OPEN-009 — perfil operacional proposto

| Item | Proposta | Classe |
| --- | --- | --- |
| suporte | `PILOT_SUPPORT_MODE=BEST_EFFORT`, sem SLA público | `REQUIRED_PILOT` |
| incidente | `focusgtba@gmail.com`, com autoridade de pausar entradas | `REQUIRED_PILOT` |
| backup | diário durante o piloto | `REQUIRED_PILOT` |
| restauração | teste documentado antes da primeira conta | `REQUIRED_PILOT` |
| RPO | 24 horas | `REQUIRED_PILOT` |
| RTO | 8 horas | `REQUIRED_PILOT` |
| suporte 24x7/SLA comercial | não prometido no piloto | `REQUIRED_FULL_PRODUCTION` |
| SLO/error budget definitivo | dimensionar após evidência do piloto | `REQUIRED_FULL_PRODUCTION` |
| orçamento empresarial/HA | fora do recorte sem pagamentos | `REQUIRED_FULL_PRODUCTION` |
| dashboard adicional | útil, não condiciona primeira conta se logs/readiness existem | `OPTIONAL` |

`OPEN-009_CONTROLLED_PILOT=AWAITING_OWNER_APPROVAL`. O restore já foi ensaiado na Fatia 8, mas
deve ser repetido imediatamente antes da ativação para satisfazer a proposta.

## 8. OPEN-010 — plano proposto

- duração: 30 dias a partir da primeira conta real;
- coorte máxima: 10 alunos e 3 instrutores adultos;
- território/categoria: Porto Alegre/RS, categoria B;
- idade: 18 anos ou mais; menores continuam bloqueados, sem consentimento parental presumido;
- pagamentos, upload documental e publicação automática: desabilitados;
- instrutor: não verificado/não publicado até decisão administrativa separada;
- objetivos: cadastro, aceite, busca, perfil, clique externo de WhatsApp, analytics, bugs e fluxo
  administrativo;
- métricas: cadastros/falhas, buscas, impressões, perfis, cliques de WhatsApp, erros, incidentes e
  `PrivacyRequest`; clique não é venda;
- revisão: `GO`, `ITERATE` ou `NO_GO` após 30 dias, sem expansão automática ou meta comercial.

`OPEN-010_CONTROLLED_PILOT=AWAITING_OWNER_APPROVAL`.

## 9. Decisões que Gilmar precisa aprovar

| Decisão | Proposta | Risco | Impacto se não aprovar |
| --- | --- | --- | --- |
| enquadramento/DPO | fornecer os seis dados empresariais e decidir se substitui `ADR-019/052` após classificação | moderado | conta/dados reais continuam bloqueados |
| idade | piloto exclusivo para maiores de 18 anos | baixo | cadastro real continua bloqueado |
| analytics | quatro eventos mínimos, retenção de 90 dias e LIA-8F-01 | baixo/moderado | analytics real continua bloqueado |
| auditoria | aceitar LIA-8F-02 para telemetria mínima não coberta por obrigação | baixo/moderado | evidência adicional fica bloqueada |
| retenção | aprovar a política operacional da seção 5, mantendo prazos finais jurídicos pendentes | moderado | `OPEN-008_CONTROLLED_PILOT` não passa |
| operação | best effort, RPO 24h, RTO 8h, backup diário, contato e restore prévio | moderado | `OPEN-009_CONTROLLED_PILOT` não passa |
| plano/coorte | 30 dias, 10 alunos, 3 instrutores, Porto Alegre/RS, categoria B | baixo/moderado | `OPEN-010_CONTROLLED_PILOT` não passa |
| RIPD | aceitar `NOT_REQUIRED_FOR_CURRENT_SCOPE` e gatilhos de reavaliação | moderado | política interna anterior continua bloqueando o piloto |
| WhatsApp | aceitar link externo com aviso contextual, sem integração/analytics de telefone | baixo | contato WhatsApp real continua bloqueado |
| MapTiler | concluir revisão dos documentos listados ou aprovar fallback sem o fornecedor | moderado | busca real via MapTiler continua bloqueada |

## 10. Estado dos gates e capabilities

- `OPEN-008_CONTROLLED_PILOT=AWAITING_OWNER_APPROVAL`;
- `OPEN-009_CONTROLLED_PILOT=AWAITING_OWNER_APPROVAL`;
- `OPEN-010_CONTROLLED_PILOT=AWAITING_OWNER_APPROVAL`;
- `OPEN-008_FULL_PRODUCTION=BLOCKED_EXTERNAL`;
- `OPEN-009_FULL_PRODUCTION=AWAITING_OWNER_APPROVAL`;
- `OPEN-010_FULL_PRODUCTION=AWAITING_OWNER_APPROVAL`.

| Capability | Status | Último blocker |
| --- | --- | --- |
| `REAL_ACCOUNT_REGISTRATION` | `AWAITING_OWNER_APPROVAL` | classificação DPO/política interna e idade mínima |
| `REAL_PERSONAL_DATA` | `AWAITING_OWNER_APPROVAL` | política operacional de retenção |
| `REAL_STUDENT_USE` | `AWAITING_OWNER_APPROVAL` | coorte/plano e dependências de conta/dados |
| `REAL_INSTRUCTOR_REGISTRATION` | `AWAITING_OWNER_APPROVAL` | coorte/plano, retenção e governança do perfil |
| `REAL_MARKETPLACE_SEARCH` | `BLOCKED_EXTERNAL` | revisão MapTiler ou decisão de fallback |
| `REAL_WHATSAPP_CONTACT` | `AWAITING_OWNER_APPROVAL` | aviso de serviço externo e decisão do link simples |
| `REAL_MARKETPLACE_ANALYTICS` | `AWAITING_OWNER_APPROVAL` | retenção de 90 dias e LIA-8F-01 |
| `REAL_DOCUMENT_UPLOADS` | `BLOCKED` | fora do piloto |
| `REAL_AUTOMATIC_PUBLICATION` | `BLOCKED` | fora do piloto |
| `REAL_PAYMENTS` | `BLOCKED` | fora do piloto e `OPEN-005` |
| `REAL_PRO_BILLING` | `BLOCKED` | fora do piloto |

## Referências oficiais

- Resolução CD/ANPD nº 2/2022, especialmente arts. 3º, 4º, 5º e 11.
- ANPD, página orientativa sobre Relatório de Impacto à Proteção de Dados Pessoais.
- ANPD, Guia Orientativo sobre Hipóteses Legais — Legítimo Interesse.
