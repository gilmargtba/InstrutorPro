# Fatia 8H — abrangência nacional de cadastro e busca

Data: 20/09/2026. Estado: implementação local concluída; ativação e deploy não autorizados.

## Decisão e limites

Cadastro de instrutor, área pública de atendimento e busca são estruturalmente nacionais. O
catálogo interno contém as 27 UFs e a busca usa distância PostGIS, sem condicional por cidade ou
primeira onda. A cidade, o centro público da área e o raio são dados de atendimento; residência e
localização privada não são publicadas.

Cadastro não significa verificação, elegibilidade ou publicação. Todo perfil real nasce
`DRAFT/NOT_STARTED/UNPUBLISHED`. A publicação exige conta e papel ativos, perfil aprovado,
verificação vigente, autorização da área, oferta `REAL`, decisão administrativa e uma linha
`RegulatoryReadiness` vigente em `APPROVED` para
`INSTRUCTOR/INSTRUCTOR_PUBLICATION`. Ausência, pendência ou expiração bloqueia publicação e
também exclui o perfil do selector público. Nenhuma aprovação regulatória foi semeada.

MapTiler continua `PENDING_VENDOR_REVIEW`: bloqueia a busca real dependente de geocoding/tiles,
mas não bloqueia cadastro nem edição da área pública. PostGIS permanece fonte de verdade depois
da resolução de coordenadas. O estado vazio usa: “Ainda não encontramos instrutores disponíveis
nesta região.”

## Matriz nacional

| UF | Cadastro | Busca técnica | Verificação | Publicação pública |
| --- | --- | --- | --- | --- |
| AC | PREPARADO | PENDENTE_MAPTILER | PENDENTE_REGULATÓRIO | BLOQUEADA |
| AL | PREPARADO | PENDENTE_MAPTILER | PENDENTE_REGULATÓRIO | BLOQUEADA |
| AP | PREPARADO | PENDENTE_MAPTILER | PENDENTE_REGULATÓRIO | BLOQUEADA |
| AM | PREPARADO | PENDENTE_MAPTILER | PENDENTE_REGULATÓRIO | BLOQUEADA |
| BA | PREPARADO | PENDENTE_MAPTILER | PENDENTE_REGULATÓRIO | BLOQUEADA |
| CE | PREPARADO | PENDENTE_MAPTILER | PENDENTE_REGULATÓRIO | BLOQUEADA |
| DF | PREPARADO | PENDENTE_MAPTILER | PENDENTE_REGULATÓRIO | BLOQUEADA |
| ES | PREPARADO | PENDENTE_MAPTILER | PENDENTE_REGULATÓRIO | BLOQUEADA |
| GO | PREPARADO | PENDENTE_MAPTILER | PENDENTE_REGULATÓRIO | BLOQUEADA |
| MA | PREPARADO | PENDENTE_MAPTILER | PENDENTE_REGULATÓRIO | BLOQUEADA |
| MT | PREPARADO | PENDENTE_MAPTILER | PENDENTE_REGULATÓRIO | BLOQUEADA |
| MS | PREPARADO | PENDENTE_MAPTILER | PENDENTE_REGULATÓRIO | BLOQUEADA |
| MG | PREPARADO | PENDENTE_MAPTILER | PENDENTE_REGULATÓRIO | BLOQUEADA |
| PA | PREPARADO | PENDENTE_MAPTILER | PENDENTE_REGULATÓRIO | BLOQUEADA |
| PB | PREPARADO | PENDENTE_MAPTILER | PENDENTE_REGULATÓRIO | BLOQUEADA |
| PR | PREPARADO | PENDENTE_MAPTILER | PENDENTE_REGULATÓRIO | BLOQUEADA |
| PE | PREPARADO | PENDENTE_MAPTILER | PENDENTE_REGULATÓRIO | BLOQUEADA |
| PI | PREPARADO | PENDENTE_MAPTILER | PENDENTE_REGULATÓRIO | BLOQUEADA |
| RJ | PREPARADO | PENDENTE_MAPTILER | PENDENTE_REGULATÓRIO | BLOQUEADA |
| RN | PREPARADO | PENDENTE_MAPTILER | PENDENTE_REGULATÓRIO | BLOQUEADA |
| RS | PREPARADO | PENDENTE_MAPTILER | APROVADA_SOMENTE_PORTO_ALEGRE_B | CONDICIONAL_A_REGISTRO_VIGENTE |
| RO | PREPARADO | PENDENTE_MAPTILER | PENDENTE_REGULATÓRIO | BLOQUEADA |
| RR | PREPARADO | PENDENTE_MAPTILER | PENDENTE_REGULATÓRIO | BLOQUEADA |
| SC | PREPARADO | PENDENTE_MAPTILER | PENDENTE_REGULATÓRIO | BLOQUEADA |
| SP | PREPARADO | PENDENTE_MAPTILER | PENDENTE_REGULATÓRIO | BLOQUEADA |
| SE | PREPARADO | PENDENTE_MAPTILER | PENDENTE_REGULATÓRIO | BLOQUEADA |
| TO | PREPARADO | PENDENTE_MAPTILER | PENDENTE_REGULATÓRIO | BLOQUEADA |

`PREPARADO` descreve código testado, não capability ativa. A exceção documental de RS não cria
automaticamente a linha operacional de prontidão e não se estende a outra cidade/categoria.

## Evidências

- cadastro/onboarding testado em Porto Alegre, São Paulo, Rio de Janeiro, Goiânia,
  Florianópolis, Vitória e Manaus;
- UF fora do catálogo é rejeitada;
- área privada permanece nula e perfil permanece não publicado;
- selector real exclui dados sintéticos e exclui UF sem prontidão explícita;
- filtro público conserva as condições de conta, papel, perfil, verificação, autorização,
  validade, modo real e prontidão territorial;
- nenhum deploy ou dado real foi executado.

## Próximo gate seguro da Fatia 8H

`PREDEPLOY_DECISION=NO_GO`: `DPO_STATUS=PENDING_CLASSIFICATION`, retenções jurídicas ainda
pendentes e `MAPTILER_STATUS=PENDING_VENDOR_REVIEW`. Portanto não há autorização para ativar
capabilities ou executar deploy.
