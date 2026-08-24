# Glossário

Os termos abaixo resumem as fontes normativas; em conflito, prevalecem `SCOPE.md` e `DOMAIN.md`.

**Primeiro ciclo:** fundação cadastral, documental, de autorização, auditoria e elegibilidade; não é o MVP completo.

**MVP funcional:** jornada transacional completa delimitada em `SCOPE.md`.

**Piloto:** operação real e limitada do MVP com gates e métricas congelados.

**Versão operacional inicial (VOI):** operação contínua após gate positivo do piloto e hardening.

**Aluno:** usuário que procura ou contrata aula.

**Instrutor:** profissional que oferece aula.

**Papel pessoal/de negócio:** capacidade `STUDENT`, `INSTRUCTOR`, `DOCTOR` ou `PSYCHOLOGIST` atribuída de forma auditável. Papéis compatíveis podem coexistir, sem herança de permissão, perfil, verificação ou publicação. Clínica é organização e usa membership.

**Instrutor aprovado:** aplicação aceita pela política interna.

**Instrutor elegível:** atende todas as condições operacionais atuais.

**Credenciamento oficial:** autorização do órgão competente, não criada pela plataforma.

**Verificação interna:** análise realizada pelo marketplace.

**Autorização/credenciamento oficial:** condição atribuída pelo órgão competente, usada como evidência quando aplicável e nunca criada pela plataforma.

**Marketplace:** ambiente de descoberta e contratação.

**SaaS do instrutor:** ferramentas recorrentes de gestão.

**Solicitação:** proposta ainda negociável.

**Oferta de serviço:** combinação publicável de categoria, duração, preço, veículo/área e vigência do instrutor.

**Política comercial:** versão imutável das regras de hold, cancelamento, no-show, conclusão e disputa aplicadas ao acordo.

**Hold:** reserva comercial temporária de um slot, criada atomicamente no aceite e sujeita a expiração.

**Reserva:** compromisso com condições congeladas.

**Aula comercial:** serviço contratado na plataforma.

**Aula oficial/homologada:** registro reconhecido pelo processo público competente.

**GMV:** valor total transacionado.

**Take rate:** receita da plataforma sobre GMV.

**Split:** divisão automática de pagamento.

**Recebedor:** conta do instrutor no provedor.

**Razão financeiro interno (ledger):** registro por partidas dobradas dos efeitos financeiros, sem representar conta bancária, conta de pagamento ou custódia.

**Parte financeira:** aluno, instrutor, plataforma ou provedor de liquidação identificado no ledger.

**Extrato financeiro:** visão autorizada dos lançamentos e saldos derivados de uma parte financeira.

**No-show:** ausência de uma das partes.

**Disputa:** contestação formal.

**Caso de suporte:** atendimento ou denúncia de conduta, segurança ou privacidade, separado da disputa financeira.

**Elegibilidade:** resultado calculado de regras.

**Aceite jurídico:** prova de que uma versão de contrato, termo ou aviso obrigatório foi apresentada/aceita; não constitui consentimento LGPD.

**Consentimento LGPD:** manifestação livre, informada, inequívoca, granular e revogável para uma finalidade que efetivamente use essa hipótese legal.

**Controlador/operador:** papéis funcionais de quem decide finalidade/meios essenciais e de quem trata sob instruções; são classificados por operação, não apenas pelo contrato.

**ROPA:** inventário de operações de tratamento por finalidade, base, dados, agentes, fluxo, retenção, segurança e direitos.

**LIA/RIPD:** avaliação de legítimo interesse e relatório de impacto à proteção de dados, usados preventivamente nos casos definidos em `LGPD.md`.

**RBAC/ABAC:** autorização por papel e por atributos/contexto.

**Idempotência:** repetição segura sem duplicar efeito.

**Outbox:** registro transacional de eventos.

**PostGIS:** extensão geográfica do PostgreSQL.

**Detran/Senatran:** órgãos estadual/federal de trânsito.

**Renach/Renavam:** registros nacionais relacionados a condutores e veículos.

**Datavalid:** serviço do Serpro para validações conforme contratação.

**Consulta Online Senatran:** serviço contratado para consultas autorizadas.

## Termos adicionados em 2026-08-19

- **StudentDemand:** necessidade de aula declarada pelo aluno, independente de proposta/reserva.
- **DemandMatch:** compatibilidade explicável entre demanda e oferta elegível.
- **DemandAggregate:** visão agregada de demanda por região, sujeita a limiar de privacidade.
- **InstructorCandidate:** interessado em tornar-se instrutor, ainda sem condição de oferta/publicação.
- **QualificationJourney:** checklist orientativo e versionado para acompanhar requisitos aplicáveis.
- **OfficialRegistryVerification:** evidência auditável de consulta/revisão em fonte oficial ou autorizada.
- **Academia do Instrutor:** hub orientativo da jornada de formação/regularização; não é autoridade certificadora.
