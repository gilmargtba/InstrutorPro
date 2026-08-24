# GOV-004 — Organização operadora e responsáveis

Status: **ESTRUTURA E GATES APROVADOS; DADOS REAIS PENDENTES DE ENTRADA HUMANA** — 24/08/2026.

## Objetivo

Identificar a pessoa jurídica que operará a InstrutorPro e associar responsáveis reais aos gates antes de produção ou dados reais. Este documento não presume constituição, representação, contrato ou autorização inexistente.

## Papéis funcionais adotados

- `OPERATIONS`
- `COMPLIANCE`
- `LEGAL`
- `PRIVACY_SECURITY`
- `ADMIN`

As funções permitem atribuir trabalho e risco durante desenvolvimento. Não substituem nomeação formal, segregação, contato ou responsabilidade legal.

## Cadastro pendente da organização operadora

Não há campo organizacional obrigatório antes do desenvolvimento exclusivamente sintético. Todos os valores desconhecidos permanecem literalmente `PENDING_HUMAN_INPUT`.

| Campo | Valor atual | Necessário antes de |
| --- | --- | --- |
| razão social | `PENDING_HUMAN_INPUT` | homologação com contratos/avisos reais; produção |
| nome fantasia | `PENDING_HUMAN_INPUT` | homologação de conteúdo/identidade pública; produção |
| CNPJ | `PENDING_HUMAN_INPUT` | homologação contratual/fiscal; produção |
| endereço empresarial | `PENDING_HUMAN_INPUT` | termos, privacidade, contratos e produção |
| responsável legal | `PENDING_HUMAN_INPUT` | assinatura/aprovação de documentos; produção |
| contato operacional | `PENDING_HUMAN_INPUT` | homologação operacional/piloto; produção |
| contato de privacidade | `PENDING_HUMAN_INPUT` | homologação do fluxo de direitos; antes de qualquer dado real |
| encarregado/DPO, quando aplicável | `PENDING_HUMAN_INPUT` | decisão LGPD/documentos e produção; nomeação conforme aplicabilidade legal |
| contato jurídico | `PENDING_HUMAN_INPUT` | homologação jurídica/contestação; produção |
| domínio oficial | `PENDING_HUMAN_INPUT` | configuração de hosts, origens, e-mail e produção pública |
| política de privacidade | `PENDING_HUMAN_INPUT` | homologação jurídica com dados reais; produção |
| termos de uso | `PENDING_HUMAN_INPUT` | homologação jurídica com usuários reais; produção |

### Classificação por gate

- **Antes de desenvolvimento sintético:** nenhum dos campos acima; usar somente organizações, domínios e contatos fictícios marcados como sintéticos.
- **Antes de homologação:** fornecer os campos ligados ao fluxo que será homologado. Homologação puramente técnica e sintética pode continuar sem dados reais; homologação jurídica, operacional ou de comunicações exige razão social/nome fantasia/CNPJ/endereço/responsável e contatos/documentos aplicáveis.
- **Antes de produção ou qualquer usuário/dado real:** todos os campos aplicáveis devem estar preenchidos, revisados e aprovados; política de privacidade e termos devem apontar para a entidade real e versão exata.

## Informações já conhecidas

- nome operacional do produto: `InstrutorPro`, sujeito à validação jurídica de marca/domínio;
- arquitetura: monólito modular nacional para 27 UFs;
- primeira onda técnica/comercial autorizada: RS, SC, SP, RJ e ES; AM, RO, AC e RR permanecem somente na matriz regulatória;
- nenhuma cidade única limita o domínio;
- clínica é organização do marketplace e não representa a organização operadora da plataforma.

## Critério de fechamento

`GOV-004` está fechado para desenvolvimento técnico sintético porque sua estrutura e seus gates foram aprovados. Permanece aberto para homologação não sintética e produção até que os campos aplicáveis sejam fornecidos com evidência. Não publicar termos definitivos, contratar em nome de entidade não identificada, receber usuário real ou declarar a organização identificada enquanto os respectivos campos permanecerem pendentes.
