# GOV-004 — Organização operadora e responsáveis

Status: **OPERADOR/CONTROLADOR E CANAL M1 IDENTIFICADOS; DEMAIS DADOS PENDENTES** — 29/08/2026.

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

Não há campo organizacional obrigatório antes do desenvolvimento exclusivamente sintético.
Valores fornecidos por decisão humana são registrados com sua proveniência; os demais
permanecem literalmente `PENDING_HUMAN_INPUT`.

| Campo | Valor atual | Necessário antes de |
| --- | --- | --- |
| razão social | `PENDING_HUMAN_INPUT` | homologação com contratos/avisos reais; produção |
| nome fantasia | `PENDING_HUMAN_INPUT` | homologação de conteúdo/identidade pública; produção |
| tipo de operador | `PESSOA_JURIDICA` — decisão humana de 29/08/2026 | M1 Porto Alegre/RS |
| CNPJ | `10.280.826/0001-05` — informado pelo responsável humano; razão social ainda sem comprovação | homologação contratual/fiscal; produção |
| endereço empresarial | `PENDING_HUMAN_INPUT` | termos, privacidade, contratos e produção |
| responsável legal | `PENDING_HUMAN_INPUT` | assinatura/aprovação de documentos; produção |
| contato operacional | `PENDING_HUMAN_INPUT` | homologação operacional/piloto; produção |
| contato de privacidade | `focusgtba@gmail.com` — canal inicial do M1 | homologação do fluxo de direitos; antes de qualquer dado real |
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

- operador/controlador declarado para o M1: pessoa jurídica, CNPJ
  `10.280.826/0001-05`, limitado ao recorte Porto Alegre/RS;
- canal inicial de privacidade e direitos: `focusgtba@gmail.com`;
- essa decisão não comprova razão social, representação, endereço, CNAE nem designa
  Encarregado/DPO;
- nome operacional do produto: `InstrutorPro`, sujeito à validação jurídica de marca/domínio;
- arquitetura: monólito modular nacional para 27 UFs;
- primeira onda técnica/comercial autorizada: RS, SC, SP, RJ e ES; AM, RO, AC e RR permanecem somente na matriz regulatória;
- nenhuma cidade única limita o domínio;
- clínica é organização do marketplace e não representa a organização operadora da plataforma.

## Critério de fechamento

`GOV-004` está fechado para desenvolvimento técnico sintético e possui operador/controlador
e canal inicial definidos para preparar o M1. Permanece aberto para produção: razão social,
representação, endereço e demais dados exigidos pelos documentos/contratos aplicáveis
precisam de comprovação; a designação formal de Encarregado/DPO continua separada. Não
publicar termos definitivos nem contratar usando informação não comprovada.
