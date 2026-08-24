# Modelo de Negócio

Este documento é a fonte oficial do funcionamento econômico. Valores e políticas em aberto não podem ser codificados como definitivos; seus identificadores estão em `DECISIONS.md`.

## Atores econômicos e responsabilidades propostas

| Ator                  | Papel econômico                                                      | Responsabilidade operacional                                                               | Limite jurídico a validar                                                             |
| --------------------- | -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------- |
| Aluno                 | contratante e pagador da aula                                        | fornecer dados verdadeiros, aceitar condições, comparecer e reportar ocorrências           | condição de consumidor e efeitos do direito de arrependimento/cancelamento            |
| Instrutor autônomo    | ofertante e prestador do serviço                                     | manter credenciamento oficial válido, veículo/agenda, executar a aula e cumprir política   | autonomia, responsabilidade profissional, tributos e ausência de vínculo trabalhista  |
| Plataforma            | intermediadora, operadora do marketplace e recebedora da comissão    | verificar para publicação, formalizar condições, processar via gateway, suportar e auditar | extensão da responsabilidade solidária, deveres consumeristas, fiscais e de segurança |
| Gateway/arranjo       | processador e movimentador dos recursos reais                        | tokenizar, cobrar, criar recebedor, liquidar, estornar e informar eventos                  | KYC, split, retenção, chargeback e contratos do provedor                              |
| Fornecedores técnicos | operadores/fornecedores de storage, mensagem, mapa e observabilidade | tratar dados conforme contrato e instruções                                                | papel LGPD, suboperadores e transferências internacionais                             |
| Detran/Senatran       | autoridade pública, fora da cadeia comercial da plataforma           | credenciar/autorizar e operar processos oficiais                                           | plataforma não fala em nome do órgão nem presume acesso técnico                       |

A caracterização jurídica final depende de parecer brasileiro (`OPEN-004`). Até lá, as descrições acima são premissas de produto conservadoras, não parecer.

## Proposta comercial do MVP

- pesquisa e cadastro sem cobrança inicial;
- todas as reservas originadas no marketplace são pagas pelo gateway integrado;
- a plataforma recebe comissão por reserva liquidada conforme política aprovada;
- o instrutor recebe líquido conforme split, prazos, retenções e efeitos de cancelamento/chargeback;
- assinatura SaaS, leads trazidos pelo instrutor e pacotes pertencem à evolução posterior;
- nenhuma interface chama o ledger de carteira, conta bancária ou conta de pagamento.

## Formação do acordo

1. O instrutor publica uma `ServiceOffering` com preço, duração e condições permitidas.
2. O aluno cria solicitação e proposta; contrapropostas geram novas versões.
3. O aceite referencia a versão exata, a política comercial vigente e o cálculo do servidor.
4. O aceite cria uma reserva temporária, congela preço/comissão/condições e inicia o prazo de pagamento.
5. O gateway confirma ou rejeita o pagamento; somente confirmação confiável torna a reserva confirmada.
6. Conclusão, cancelamento, no-show, disputa, reembolso, comissão e repasse seguem fatos independentes e auditáveis.

Percentual de comissão, prazo do hold, regras de cancelamento/no-show, reconhecimento de receita, repasse e reservas financeiras continuam bloqueantes antes das fases correspondentes.

## Receita e ledger

```text
GMV = total de cobranças pagas por aulas
comissão bruta = valor definido no snapshot comercial
receita reconhecida = comissão elegível conforme política contábil aprovada
receita líquida = receita reconhecida - taxas - estornos - perdas - impostos atribuíveis
líquido do instrutor = valor da aula - comissão - encargos atribuíveis aprovados
```

O ledger interno por partidas dobradas explica cobrança, comissão, taxa, repasse, reembolso e chargeback:

- aluno, instrutor, plataforma e provedor de liquidação são partes financeiras distintas;
- lançamentos confirmados são imutáveis, balanceados e corrigidos por reversão/compensação;
- saldo é derivado; preço e comissão nunca vêm do frontend;
- gateway movimenta os recursos reais; o sistema não oferece custódia, depósito, saque ou transferência entre usuários;
- `Payment`, `Transfer`, `Booking` e ledger têm estados independentes e correlacionados.

O plano de contas, momento de reconhecimento, alocação de taxas e tratamento de chargeback exigem política contábil aprovada antes de `C1`.

## Hipóteses a validar no piloto

| Hipótese                      | Indicador                                  | Evidência mínima para decisão                                          |
| ----------------------------- | ------------------------------------------ | ---------------------------------------------------------------------- |
| há densidade local suficiente | instrutores ativos e cobertura geográfica  | meta definida em `PILOT.md`, não apenas cadastros                      |
| aluno paga pela intermediação | busca → pagamento                          | funil instrumentado e entrevistas de abandono                          |
| comissão é aceitável          | aceite do instrutor e evasão               | coorte por taxa, sem desconto mascarar resultado                       |
| valor compensa custos         | margem de contribuição por aula            | gateway, mensagens, suporte, verificação, estorno e impostos incluídos |
| há repetição                  | segunda reserva dentro da janela aprovada  | coorte de alunos elegíveis                                             |
| confiança reduz fricção       | conversão e satisfação                     | pesquisa e motivos de suporte/cancelamento                             |
| operação é sustentável        | minutos de suporte e divergências por aula | registro de toda intervenção manual                                    |

As metas numéricas são definidas em `PILOT.md` antes da entrada, para evitar ajustar o critério ao resultado.

## Redução legítima de desintermediação

Pagamento protegido pelo gateway, comprovante, política clara, suporte, agenda, reputação e conveniência. Não usar bloqueios abusivos, ocultar contato necessário à execução ou prometer proteção inexistente.

## Responsabilidades que precisam de validação

| Decisão                                      | Gate                            | Responsáveis pela resposta             |
| -------------------------------------------- | ------------------------------- | -------------------------------------- |
| cidade, categoria e público inicial          | antes de `A0` concluir          | Product + Operations + Compliance      |
| comissão e promoções                         | antes de negociação ser fechada | Product + Finance                      |
| cancelamento, no-show, conclusão e disputa   | antes de `B6`                   | Product + Legal + Operations + Finance |
| termos, responsabilidade, seguro e vínculo   | antes de usuários reais         | Legal + Compliance                     |
| gateway, split, KYC, fluxo e chargeback      | antes de `C1`                   | Finance + Legal + Engineering          |
| tributação, nota e reconhecimento de receita | antes de `C1`                   | Accounting + Legal + Finance           |
| SLA de suporte e orçamento do piloto         | antes de staging operacional    | Operations + Product                   |

## Fase SaaS posterior

Agenda própria, link, alunos particulares, pacotes, calendário, lembretes, financeiro e assinatura somente após o piloto provar uso operacional recorrente. Essa fase terá modelo comercial e termos próprios; não herda silenciosamente as regras de comissão do marketplace.

## Funis adicionais de aquisição

A plataforma passa a medir três funis relacionados:

1. **Aluno:** necessidade -> match -> contratação -> aula concluída -> repetição.
2. **Instrutor autorizado:** aquisição -> comprovação/revisão -> publicação -> primeiro aluno -> utilização recorrente.
3. **Candidato a instrutor:** interesse -> pré-análise -> jornada orientativa -> autorização externa -> comprovação -> publicação.

A receita do MVP continua vinculada à contratação/aula conforme política a aprovar. Academia, indicação de cursos, publicidade, lead educacional, assinatura SaaS e outras monetizações não são presumidas; exigem decisão própria, transparência comercial e validação jurídica antes de ativação.

Métricas adicionais: demandas abertas por cidade, razão demanda/instrutor publicável, taxa de match, tempo até primeiro match, cobertura geográfica, conversão candidato->instrutor publicado e tempo entre entrada do candidato e publicação.
