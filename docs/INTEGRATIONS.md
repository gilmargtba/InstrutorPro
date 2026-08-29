# Integrações

Fonte oficial das dependências externas, contratos, gates e estratégias de falha. Nenhuma integração domina o modelo interno:

```text
domínio → porta interna → adaptador → fornecedor
fornecedor → verificação/tradução → evento interno idempotente
```

## Inventário por fase

| Capacidade                | Fase mínima   |          Criticidade | Fonte interna           | Falha/contingência                                                                           |
| ------------------------- | ------------- | -------------------: | ----------------------- | -------------------------------------------------------------------------------------------- |
| e-mail/SMS OTP            | A4            | alta para onboarding | desafio + entrega       | retry limitado, expiração, troca de canal aprovada; nunca logar OTP                          |
| object storage            | A14           |              crítica | metadados/hash no banco | upload fica em quarentena; indisponibilidade bloqueia novo upload, não torna arquivo público |
| malware scanner           | A14           |              crítica | status do documento     | fail closed, retry/alerta; sem promoção sem resultado limpo                                  |
| Google OIDC               | Gate A19/M2.1 |                média | `ExternalIdentity`      | login local continua; não criar/vincular por e-mail                                          |
| mapas/geocoding           | B1            |                média | geometria minimizada    | busca por cidade/área degradada conforme política; sem precisão inventada                    |
| gateway                   | C2            |              crítica | Payment/ledger/receipt  | estado pendente, consulta/reconciliação; nunca inferir sucesso pelo timeout                  |
| WhatsApp/push             | posterior     |          baixa/média | `NotificationDelivery`  | e-mail/SMS ou caixa interna; conteúdo mínimo                                                 |
| Detran/Senatran/Datavalid | pós-piloto    |          regulatória | evidência versionada    | operação manual autorizada; não é dependência do MVP                                         |
| observabilidade           | A1/produção   |                 alta | logs/métricas/traces    | buffer/retention local segura e alerta; aplicação não vaza dados ao compensar falha          |

Seleção concreta exige owner, papel LGPD por operação, países de armazenamento/suporte/acesso, mecanismo de transferência internacional, contrato/DPA, SLA, preço, limites, sandbox, exportação/portabilidade, segurança, suboperadores, procedimento de incidente e estratégia de saída. Cláusula-padrão da ANPD, quando usada, entra integralmente e sem alteração; região brasileira não elimina transferência por acesso remoto/suboperador. Decisões são registradas em `DECISIONS.md`.

## Contratos internos

```python
class PaymentProvider: ...
class MapProvider: ...
class MessageProvider: ...
class ObjectStorage: ...
class MalwareScanner: ...
class ExternalIdentityProvider: ...
class IdentityValidationProvider: ...
class TrafficAuthorityProvider: ...
```

Portas usam DTOs internos e erros classificados (`temporary`, `permanent`, `unknown_effect`, `invalid_response`). Adaptadores definem timeout, retry somente seguro, idempotência/correlação e métricas. SDK e payload bruto não atravessam a camada de integração.

## Pagamentos

### Gate de seleção

Antes de `C1/C2`, validar em sandbox e contrato:

- marketplace brasileiro, recebedores e KYC;
- Pix e cartão/tokenização conforme escolha aprovada;
- split, retenções e liquidação sem custódia pela plataforma;
- idempotência, consulta pós-timeout e IDs estáveis;
- webhooks assinados, rotação de segredo e documentação de ordem/retry;
- reembolso parcial/total, chargeback e transferências;
- extrato/relatório exportável para conciliação;
- ambientes/credenciais segregados, limites e suporte de incidente;
- responsabilidades fiscais, jurídicas e contábeis aprovadas.

```python
class PaymentProvider:
    def create_recipient(self, command, idempotency_key): ...
    def get_recipient(self, external_id): ...
    def create_payment_intent(self, command, idempotency_key): ...
    def get_payment(self, external_id): ...
    def refund(self, command, idempotency_key): ...
    def get_transfer(self, external_id): ...
    def list_settlement_records(self, period, cursor): ...
    def verify_webhook(self, headers, raw_body): ...
    def parse_webhook(self, headers, raw_body): ...
```

O gateway movimenta os recursos reais. `Payment`, `Transfer`, recebedor, ledger e booking são correlacionados, mas independentes. Retorno do browser não confirma cobrança; timeout é efeito desconhecido até consulta/webhook/reconciliação. Evento antigo ou duplicado é guardado sem regredir estado.

## Webhooks

1. limitar tamanho e preservar corpo bruto necessário;
2. localizar configuração pelo path seguro;
3. verificar assinatura/tempo antes do parse de negócio;
4. persistir recibo por evento externo/hash permitido;
5. responder no prazo do fornecedor;
6. processar transição e ledger em transação idempotente;
7. marcar processado, ignorado ou falho com motivo;
8. permitir replay administrativo autorizado;
9. reconciliar lacunas e alertar fila/assinatura/divergência.

Payload retido é minimizado e protegido; dados de cartão nunca entram no sistema.

## Storage e malware

```text
requisição autorizada
→ upload para namespace de quarentena
→ validação de tamanho/extensão/MIME real
→ hash e scan
→ promoção atômica para namespace privado
→ metadado pronto para revisão
→ acesso temporário autorizado e auditado
```

Scanner indisponível falha fechado. Bucket/container não permite listagem pública, ACL individual pública nem URL permanente. Lifecycle só apaga conforme retenção/evidência e reconcilia órfãos.

## Mensagens

- templates versionados, finalidade e idioma;
- OTP separado de mensagem de marketing;
- destinatário normalizado e mascarado em logs;
- opt-out onde aplicável sem impedir mensagem estritamente transacional necessária;
- status interno comum, bounce/complaint e retry limitado;
- webhook de mensagem também verifica autenticidade e idempotência;
- WhatsApp apenas por canal oficial; sem automação por scraping.

## Mapas e localização

Busca por proximidade, área e ponto de encontro com precisão mínima. Termos do provedor devem permitir cache/armazenamento pretendido. Endereço residencial não é ponto público; logs não recebem coordenadas exatas. Se o provedor cair, a API retorna degradação explícita ou usa filtro geográfico já persistido, nunca distância fabricada.

## Google OIDC

Somente no Gate A19/M2.1. Solicitar `openid`, `email` e `profile` estritamente necessários; validar issuer, audience, assinatura, expiração, `state` e `nonce`; usar `sub`; terminar em sessão Django. Não armazenar tokens se não houver acesso posterior à API Google. Google não prova telefone, CPF, identidade civil, documento, veículo ou elegibilidade.

## Governo e validação oficial

- **Login Gov.br:** futuro, por fluxo oficial/credenciado; nunca pedir ou guardar senha, OTP, token ou sessão do cidadão.
- **Consulta Online Senatran:** serviço autorizado/contratado para finalidades permitidas; não é API genérica de agenda ou homologação.
- **Datavalid:** somente após necessidade, base legal, custo, retenção, contrato e homologação.
- **Detran estadual:** adaptador por jurisdição apenas com documentação e autorização formal.
- **CNH do Brasil:** pode ser fonte pública oficial para orientação/consulta prevista; não usar scraping autenticado ou automação não documentada.

O MVP usa verificação interna de evidências e exige autorização oficial vigente conforme regra local, mas não altera registro público. Operação manual deve registrar fonte, data, operador, resultado interno e evidência permitida.

## Testes e operação

Cada adaptador tem contract tests com sandbox/fake fiel, fixtures sanitizadas, timeout, resposta inválida, rate limit, duplicação, ordem inesperada e indisponibilidade. Produção tem dashboard por fornecedor, alertas, runbook, contato de escalonamento, rotação de credencial e teste periódico de contingência.

## Verificação oficial e fontes públicas — consolidação

A plataforma pode usar informação de Detran, Ciretran, Senatran ou autoridade competente somente por uma das rotas aprovadas:

1. API/serviço oficialmente documentado e com uso compatível;
2. provedor autorizado/contratado com base jurídica e segurança aprovadas;
3. evidência apresentada pelo usuário e revisão manual auditável;
4. consulta pública manual operacional quando termos, finalidade e dados permitirem.

É proibido depender de endpoint privado/não documentado, contornar controles, automatizar scraping autenticado ou coletar credencial Gov.br. Toda integração implementa timeout, retry seguro, circuit breaker quando aplicável, observabilidade, mapeamento de estados internos e fallback operacional.

### Porta proposta

```text
OfficialRegistryProvider
- verify_instructor(...)
- get_verification_status(...)
- get_supported_jurisdictions()
```

Nem toda fonte suportará busca nominal/listagem. A interface concreta deve expor somente capacidades oficialmente disponíveis; o domínio não presume acesso a uma lista nacional de profissionais.

### Mapas

Para o M1 de Porto Alegre/RS, MapTiler Cloud Flex é o provider preferencial aprovado de
forma condicionada em `ADR-047`. PostGIS executa as regras internas de raio e permanece
fonte de verdade; o provider não recebe perfis, elegibilidade ou catálogo de instrutores.
Geocoding ocorre no backend com consulta minimizada, `country=br`, recorte territorial,
timeout e erro estável. Leaflet permanece no frontend, sem controle de GPS. O fallback é
busca/lista por Porto Alegre usando centroide territorial local aprovado, sem inventar
precisão nem reutilizar resposta externa contra os termos.

`OPEN-007` deixa de ser escolha genérica de fornecedor, mas continua bloqueante para
produção até evidência de aceite do plano comercial/DPA, subprocessadores, países e
mecanismo de transferência, retenção da consulta, endpoint europeu, restrições de chave,
budget/rate limit e testes de indisponibilidade. Nenhum segredo ou chamada real é ativado
por esta decisão documental.

## Fontes oficiais e primeira onda

A matriz de verificação começa por **RS, SC, SP, RJ e ES** e detalha também **RO, AM, AC e RR**, mas o contrato técnico é nacional. Para cada UF e tipo (`INSTRUCTOR`, `CLINIC`, `DOCTOR`, `PSYCHOLOGIST`) registrar: órgão/fonte oficial, capacidade de consulta, campos disponíveis, termos/limites, atualização, fallback manual e evidência preservada.

## OPEN-006 — providers de desenvolvimento e produção

### Necessários para desenvolvimento

E-mail, armazenamento privado, malware scanner, mapas/geocoding, pagamentos e notificações podem usar simuladores/fakes fiéis atrás de portas/adapters. Simuladores devem suportar sucesso, timeout, indisponibilidade, retry e erro permanente, sem enviar mensagem real, persistir documento em storage público, geocodificar endereço real ou movimentar dinheiro.

### Necessários para produção

Providers reais exigem seleção e aprovação humana/contratual posterior, incluindo segurança, LGPD, região de dados, suboperadores, retenção, disponibilidade, portabilidade, custos, encerramento e resposta a incidente. Nenhum fornecedor comercial definitivo é escolhido nesta etapa.

O domínio não referencia SDK ou estado proprietário. Trocar provider preserva contratos internos, idempotência, auditoria e estados de negócio.

Estados sem integração homologada continuam suportados pelo domínio, porém a publicação/verificação segue operação manual auditável ou permanece indisponível conforme configuração. Não inferir credenciamento pela ausência/presença em buscador genérico.
