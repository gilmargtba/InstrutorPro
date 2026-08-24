# Escopo do Produto

Este documento é a fonte oficial de fronteiras. Outros documentos podem detalhar, mas não incluir funcionalidade por conta própria.

## Definições de entrega

| Entrega                         | Resultado observável                                                                                                                 | Limite                                                                        |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------- |
| Primeiro ciclo de implementação | instrutor passa por cadastro, documentos, revisão e elegibilidade auditáveis                                                         | sem marketplace, agenda, pagamento, mapa, chat ou integração pública          |
| MVP funcional                   | jornada CNH conecta aluno a instrutor e permite descoberta de clínicas/profissionais, com contratação de aula percorrendo negociação, reserva, pagamento, execução, eventual disputa e avaliação | arquitetura nacional, primeira onda técnica/comercial RS/SC/SP/RJ/ES, AM/RO/AC/RR somente na matriz regulatória, providers substituíveis e operação assistida |
| Piloto                          | MVP operado com usuários reais e métricas, sob limites e critérios de `PILOT.md`                                                     | não equivale a expansão nem valida todas as hipóteses nacionais               |
| Versão operacional inicial      | operação contínua após piloto aprovado, com suporte, SLOs, continuidade e processo de release sustentáveis                           | mesma proposta central e expansão controlada                                  |
| Evolução posterior              | SaaS do instrutor, integrações oficiais e expansão geográfica                                                                        | exige evidência e novo gate de escopo                                         |

“Primeiro ciclo” e “MVP” não são sinônimos. O ciclo cadastral é pré-requisito do MVP.

## Primeiro ciclo de implementação

Inclui:

- fundação local/CI, configuração e observabilidade mínima;
- `Account`, verificação de contato, recuperação, sessões e MFA sensível;
- `ExternalIdentity` apenas estrutural e inativa;
- pessoa, papéis pessoais compatíveis por policy explícita e perfis independentes, sem autorização transitiva;
- organização operadora, documentos jurídicos, aceites obrigatórios e consentimentos opcionais separados;
- aplicação de instrutor, requisitos documentais versionados, upload privado e quarentena;
- veículo, revisão administrativa, suspensão, expiração e elegibilidade calculada;
- auditoria, autorização por objeto, OpenAPI, testes e backoffice mínimo.

Não inclui busca, disponibilidade, negociação, reserva, pagamento, avaliação, mapas ou integração governamental.

## MVP funcional

### Identidade e confiança

- tudo do primeiro ciclo;
- publicação apenas de instrutor internamente elegível;
- comunicação inequívoca de que a plataforma não concede credenciamento oficial;
- login Google opcional somente no gate posterior ao credenciamento cadastral.

### Descoberta e oferta

- área de serviço e busca geográfica;
- filtros por categoria, transmissão, oferta com/sem veículo, preço e disponibilidade;
- perfil público minimizado;
- oferta de serviço com preço/duração definidos pelo instrutor dentro das políticas da plataforma;
- disponibilidade recorrente e exceções.

### Negociação e reserva

- solicitação, proposta e contraproposta imutáveis;
- aceite de uma versão exata;
- reserva temporária criada atomicamente no aceite;
- prevenção de sobreposição e expiração do hold;
- notificações transacionais;
- uma política versionada de cancelamento, no-show, conclusão e disputa, ainda a aprovar em `DECISIONS.md`.

### Pagamento e receita

- um gateway brasileiro selecionado com recebedor/KYC, Pix e cartão se aprovados na seleção;
- cobrança de todas as reservas originadas no marketplace por meio do gateway no MVP;
- comissão definida no backend e congelada no aceite;
- webhook assinado e idempotente;
- reembolso e chargeback;
- transferências e conciliação;
- ledger interno por partidas dobradas, sem custódia, carteira, saldo armazenado, saque ou transferência entre usuários;
- extratos segregados de aluno, instrutor e plataforma.

### Execução, suporte e reputação

- registro de início/conclusão ou no-show conforme política aprovada;
- disputa comercial com evidências privadas;
- denúncia de segurança/conduta separada da disputa financeira;
- backoffice de suporte e moderação;
- avaliação única por participação após conclusão elegível.

### Operação e conformidade

- administração com menor privilégio, MFA e trilha de auditoria;
- LGPD, canal de direitos, retenção aprovada e resposta a incidente;
- dados sintéticos de demonstração;
- staging, homologação, deploy, monitoramento, alertas, backup e restauração testada;
- runbooks do gateway, mensagens, mapas, storage, banco, workers e webhooks.

## Restrições do MVP e piloto

- arquitetura, cadastros, regras territoriais e descoberta preparados para as 27 UFs;
- primeira onda técnica/comercial: RS, SC, SP, RJ e ES; AM, RO, AC e RR permanecem na matriz regulatória sem ativação automática; nenhuma cidade limita arquitetura/domínio e cidades de operação assistida/piloto são configuração posterior;
- primeira oferta prática priorizada: primeira habilitação, categoria B, sem impedir categorias futuras conforme regra aplicável;
- ativação por UF/cidade controlada por configuração e gate regulatório/operacional;
- categorias de instrutor habilitadas conforme regra federal e estadual vigente, sem assumir categoria B como regra nacional;
- um gateway, um provedor de mapas, um storage e provedores mínimos de mensagem;
- verificação interna manual, com tarefas automáticas apenas de apoio;
- uma moeda (`BRL`) e valores em centavos no ledger;
- web responsiva/PWA; sem app nativo;
- comunicação assíncrona transacional; sem chat em tempo real;
- suporte assistido pode orientar e reprocessar operações autorizadas, mas nunca receber senha, OTP, cartão ou dinheiro em nome das partes.

## Escopo definitivo do piloto

O piloto executa o MVP funcional em produção limitada com 20–50 instrutores elegíveis como meta de oferta, população de alunos controlada, suporte em horário publicado, limites financeiros e de volume configurados, conciliação diária e revisão semanal. Cidade, duração, orçamento, limites e responsáveis são bloqueios de entrada, não valores a serem inventados na implementação. Os critérios completos estão em `PILOT.md`.

## Versão operacional inicial

Inclui somente após gate positivo do piloto:

- correções de confiabilidade, segurança e usabilidade identificadas no piloto;
- operação contínua com SLOs, plantão e capacidade aprovados;
- suporte e conciliação sustentáveis;
- automação das intervenções manuais recorrentes, preservando auditoria;
- expansão moderada de aquisição na mesma região ou em região formalmente aprovada.

## Evolução posterior

- alunos próprios do instrutor, agenda e link próprios;
- pacotes, lembretes, calendário e assinatura SaaS;
- login Gov.br, Consulta Online Senatran, Datavalid ou Detran apenas com base legal, contrato, documentação e homologação;
- novas categorias/UFs por configuração e análise local;
- app nativo, chat, antifraude avançado e seguros/parcerias se métricas justificarem.

## Fora de escopo até decisão explícita

- conceder, prometer ou registrar credenciamento oficial;
- homologar aula, presença, carga horária ou exame perante órgão público;
- agenda de exame;
- scraping autenticado ou endpoint governamental não documentado;
- pedir ou guardar senha, OTP, token ou sessão Gov.br;
- biometria e rastreamento GPS contínuo;
- certificação/formação de instrutores;
- garantia de aprovação em exame;
- ativação simultânea e irrestrita das 27 UFs sem gates regulatórios, de oferta, suporte e operação;
- carteira, custódia, saque livre, transferência entre usuários ou operação como instituição de pagamento;
- armazenamento de cartão;
- microserviços, IA, precificação dinâmica e múltiplos provedores por categoria no MVP.

## Critérios de aceite do MVP

1. Jornadas funcionam sem edição manual de banco e com autorização por objeto.
2. Somente instrutor elegível aparece; perda de elegibilidade o remove dentro do SLO aprovado.
3. Aceite cria uma única reserva para a proposta e impede sobreposição concorrente.
4. Preço, comissão, política e condições são snapshots de versões do servidor.
5. Confirmação financeira nasce apenas de evento confiável do gateway; duplicação não duplica efeito.
6. Ledger permanece balanceado e reconciliável; cartão e credenciais externas não são armazenados.
7. Cancelamento, no-show, conclusão e disputa seguem política aprovada e auditável.
8. Avaliação exige participação elegível e não expõe dados privados.
9. Backoffice aplica segregação, MFA, motivo e auditoria.
10. Segurança, LGPD, restore, rollback, alertas, OpenAPI, testes e homologação passam pelos gates documentados.
11. Interfaces e comunicações não afirmam homologação oficial.
12. Piloto só inicia quando todos os bloqueios de entrada de `PILOT.md` estiverem fechados.

## Consolidação de escopo — demanda, matching e jornada do instrutor

### Incluído no MVP funcional

- alternância entre lista e mapa para descoberta de instrutores;
- busca geográfica por raio/área atendida com precisão pública minimizada;
- criação e gestão de `StudentDemand` pelo aluno;
- visualização agregada de cidades/regiões com demanda, sem exposição individual;
- matching determinístico por critérios aprovados, com explicação dos principais fatores;
- convite/notificação a instrutores compatíveis conforme consentimentos e política de comunicação;
- funil de entrada para instrutor já autorizado/credenciado conforme a jurisdição;
- cadastro e descoberta de clínicas, médicos e psicólogos relacionados aos exames da jornada CNH, sujeitos a fonte oficial, verificação e regra estadual;
- registro auditável de evidência oficial e origem/data da verificação;
- operação manual de verificação quando não houver integração oficial documentada e autorizada.

### Academia do Instrutor no MVP

A Academia no MVP é um **hub orientativo**, com checklist versionado, progresso e links/fontes oficiais aprovados. Não vende nem ministra curso obrigatório, não certifica e não protocola credenciamento em nome do usuário. Marketplace de cursos, afiliados, publicidade, parceria educacional e automação de protocolo exigem iniciativa posterior e validação jurídica/comercial.

### IA

IA não é dependência do MVP. O primeiro matching é determinístico e auditável. Uma camada de IA pode futuramente sugerir ordenação, explicar compatibilidade, auxiliar atendimento ou analisar dados agregados, sem decisão adversa exclusivamente automatizada e sem substituir fonte oficial.
