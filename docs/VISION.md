# Visão do Produto

## Problema

Alunos precisam localizar instrutores adequados, entender preço, disponibilidade, veículo e região atendida. Instrutores autônomos precisam captar clientes, reduzir horários ociosos, formalizar acordos, receber pagamentos e construir reputação.

O processo costuma ser fragmentado entre redes sociais, WhatsApp, agenda informal, pagamentos sem conciliação e documentos verificados de modo inconsistente.

## Proposta

Criar uma plataforma que:

- publique somente instrutores aprovados pela política interna;
- facilite descoberta por localização e necessidade;
- registre oferta, solicitação, aceite e condições;
- formalize contratações originadas no marketplace;
- processe pagamento e comissão;
- registre conclusão e avaliação;
- mantenha trilha de auditoria;
- evolua para SaaS operacional do instrutor.

## Posicionamento

### Para o aluno

> Encontre um instrutor adequado, combine a aula e contrate com segurança.

### Para o instrutor

> Receba novos alunos, organize seus horários e formalize suas aulas.

### Para a plataforma

> Intermediar uma contratação confiável e receber comissão por resultado.

## Princípios

1. Intermediação, não homologação.
2. Confiança antes de escala.
3. Densidade local antes de expansão.
4. Transações originadas no marketplace dentro da plataforma no MVP.
5. Autorização explícita.
6. Integrações substituíveis.
7. Auditoria por padrão.
8. Coleta mínima de dados.
9. Operação manual auditável é aceitável.
10. Métricas orientam o roadmap.

Verificação, aprovação e publicação são decisões internas de confiança. A autorização oficial para atuar continua pertencendo ao órgão competente e deve existir como evidência aplicável; a plataforma não a concede.

## Não objetivos iniciais

- substituir Detran ou Senatran;
- registrar aula oficial;
- agendar exame em nome do aluno;
- armazenar credencial Gov.br;
- operar nacionalmente no lançamento;
- criar app nativo antes da validação web;
- formar ou certificar instrutores;
- garantir aprovação no exame.

## Indicador norteador

**Aulas pagas e concluídas por instrutor ativo por mês.**

Complementares: tempo até primeiro aluno, aceite, pagamento, repetição, cancelamento, no-show, margem e satisfação.

## Expansão consolidada da visão — oferta, demanda e formação de oferta

A plataforma passa a tratar explicitamente os dois lados do marketplace e o funil de formação de novos instrutores:

1. **Mapa de oferta para o aluno:** descoberta de instrutores publicáveis por localização aproximada, área atendida, categoria, veículo, transmissão, preço, avaliação e disponibilidade.
2. **Demanda declarada pelo aluno:** o aluno pode publicar uma necessidade com localização minimizada, categoria, preferência de veículo/transmissão, janela de horário, raio e demais critérios aprovados.
3. **Mapa agregado de demanda para o instrutor e operação:** clusters por cidade/região mostram oportunidade sem revelar endereço ou posição exata de alunos.
4. **Matching:** regras determinísticas classificam compatibilidade entre demanda e oferta; IA só poderá ser adicionada após caso validado, dados suficientes, explicabilidade e gate de privacidade.
5. **Captação de instrutores:** profissionais já autorizados podem entrar pelo funil “já sou instrutor”, comprovar evidências e solicitar publicação.
6. **Candidatos a instrutor:** interessados podem entrar pelo funil “quero me tornar instrutor” e receber uma pré-análise informativa de requisitos, sem declaração de aptidão oficial.
7. **Academia do Instrutor:** área educacional/orientativa para explicar jornada, requisitos, documentos, cursos/entidades aplicáveis e progresso do candidato. A plataforma não forma, certifica nem credencia no MVP.
8. **Verificação oficial substituível:** evidências provenientes de Senatran/Detran/Ciretran ou outra fonte competente podem ser registradas por integração documentada ou revisão manual auditável; não usar scraping autenticado nem credenciais Gov.br.

### Jornada ampliada

```text
ALUNO -> DEMANDA -> MATCH -> PROPOSTA -> RESERVA -> PAGAMENTO -> AULA -> AVALIAÇÃO
                         ^
                         |
INSTRUTOR -> OFERTA -----+

CANDIDATO -> PRÉ-ANÁLISE -> ORIENTAÇÃO/ACADEMIA -> AUTORIZAÇÃO OFICIAL EXTERNA
          -> COMPROVAÇÃO -> REVISÃO INTERNA -> PUBLICAÇÃO -> OFERTA
```

O objetivo estratégico continua sendo densidade local: a plataforma mede desequilíbrio entre demanda e oferta para orientar aquisição de instrutores e expansão geográfica.

## Visão consolidada nacional — 19/08/2026

A **InstrutorPro** é a plataforma nacional da jornada para a CNH. A experiência parte de uma landing simples — **Sou aluno** / **Sou profissional** — e conecta o usuário aos atores adequados da jornada, sem substituir CONTRAN, SENATRAN, DETRANs ou qualquer autoridade competente.

### Primeira onda operacional

RS, SC, SP, RJ e ES. AM, RO, AC e RR permanecem na matriz regulatória sem ativação automática; status comercial não equivale a aprovação regulatória. A arquitetura permanece nacional para as 27 UFs, com ativação progressiva por configuração e gates regulatórios, de oferta, suporte e operação.

### Atores do MVP

- aluno/candidato à habilitação;
- instrutor já autorizado/credenciado conforme a regra aplicável;
- clínica relacionada aos exames da CNH;
- médico credenciado/aplicável;
- psicólogo credenciado/aplicável;
- operação/administração InstrutorPro.

### Experiência central

`Jornada CNH → localização → mapa/lista → profissional/serviço → verificação → demanda/matching quando aplicável → agendamento/contratação → pagamento quando aplicável → execução → avaliação/auditoria`.

A opção **“Quero me tornar instrutor”** e a **Academia do Instrutor** são evolução posterior e não fazem parte do MVP atual.
