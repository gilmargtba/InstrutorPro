# Segurança

## CODEX 02D

O Admin exige staff e permissões explícitas; aprovar/suspender chama serviço transacional auditado. Nenhum endpoint administrativo público foi criado.

Fonte oficial dos controles técnicos e operacionais. Autorização está em `AUTHORIZATION.md`; tratamento pessoal em `LGPD.md`; procedimentos de plataforma em `DEVOPS.md`.

## Objetivos e ameaças prioritárias

| Ativo/fluxo             | Ameaças principais                                                      | Controles mínimos                                                                                 |
| ----------------------- | ----------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| conta/sessão            | enumeração, credential stuffing, fixação, tomada e recuperação abusiva  | hash suportado, rate limit, sessão rotativa/revogável, CSRF, alerta e MFA sensível                |
| papel/elegibilidade     | elevação, corrida, publicação irregular, self-review                    | deny by default, policy por objeto, constraints/transação, segregação e auditoria                 |
| documentos              | malware, IDOR, URL pública, exfiltração e retenção excessiva            | quarentena, scan fail-closed, storage privado, URL curta, criptografia, acesso just-in-time       |
| marketplace/localização | enumeração, stalking e exposição residencial                            | precisão mínima, perfil público allowlist, rate limit e ausência de histórico desnecessário       |
| reserva                 | dupla reserva, replay e manipulação de preço                            | versão, idempotência, lock/constraint e snapshot do servidor                                      |
| pagamento/ledger        | webhook forjado, duplicação, regressão, ajuste fraudulento              | assinatura, idempotência, transições monotônicas, partidas dobradas, MFA/segregação e conciliação |
| backoffice              | conta compartilhada, privilégio excessivo, exportação e abuso interno   | MFA, RBAC/ABAC, sessão curta, justificação, alertas e revisão de acesso                           |
| supply chain/deploy     | segredo no repo, dependência/imagem vulnerável e alteração não revisada | secret scanning, lock, SCA/SAST, SBOM quando adotado, imagem imutável e aprovação                 |
| disponibilidade         | fila parada, saturação, fornecedor/banco/storage indisponível           | limites, timeouts, retries seguros, health, alertas, backup/restore e runbooks                    |

Threat model é revisado ao concluir A1, A18, C7 e antes do piloto; mudança de fluxo sensível atualiza o modelo.

## Baseline de identidade

- somente Account `ACTIVE` e `is_active=True` pode autenticar/operar; constraint impede divergência persistente;
- `BLOCKED` e `DEACTIVATED` fecham acesso sem apagar pessoa, papéis ou auditoria;
- transição de lifecycle exige permissão explicitamente atribuída, motivo, versão, lock e auditoria; superusuário não recebe bypass implícito;
- reativação de `BLOCKED` é comando explícito; `DEACTIVATED` permanece terminal até política futura aprovada;

- senha nunca logada e armazenada somente com hasher suportado/configurado;
- resposta antienumeração em login, registro, verificação e recuperação onde aplicável;
- rate limit por combinação segura de conta/IP/dispositivo, sem bloquear vítima indefinidamente;
- OTP aleatório, hash no banco, finalidade única, expiração, consumo único e tentativas limitadas;
- cookie `Secure`, `HttpOnly`, `SameSite` aprovado, escopo mínimo, rotação no login e proteção CSRF;
- revogação de sessão em bloqueio, troca/recuperação de senha e evento de risco conforme política;
- reautenticação/MFA para vínculo externo, mudança financeira, exportação e função privilegiada;
- recovery codes ou recuperação de MFA definidos antes de ativar MFA em produção;
- login externo não vincula conta por e-mail coincidente.

Valores de timeout, tentativas e rate limit são configuração segura aprovada e testada em A1/A4/A5; não são constantes arbitrárias espalhadas.

## Autorização e administração

- policy e selector aplicam o mesmo escopo;
- 404 pode ocultar existência de objeto alheio;
- serializers têm allowlist de entrada/saída;
- papéis internos expiram/revogam e são revisados;
- nenhuma conta compartilhada; conta de sistema sem login humano;
- acesso emergencial individual, temporário, alertado e revisado;
- visualização de documento/exportação é evento sensível com finalidade;
- ação administrativa recebe motivo; ajuste financeiro nunca é edição direta.

## Upload e documentos

- quotas e limites antes/durante o upload;
- nome fornecido não vira path; chave aleatória e bucket privado;
- extensão declarada, magic bytes/MIME e tipo permitido precisam concordar;
- scan assíncrono em namespace sem execução; indisponibilidade falha fechado;
- download usa disposição segura, tipo controlado e URL assinada curta;
- preview ativo é sanitizado ou convertido; nenhum HTML/script arbitrário;
- hash permite integridade/deduplicação controlada, não exposição pública;
- acesso e lifecycle são reconciliados com banco e política de retenção.

## API e aplicação

### Separação entre desenvolvimento e produção

Os seis avisos observados por `manage.py check --deploy` pertencem à configuração local de desenvolvimento e não autorizam seu uso em produção. O ambiente produtivo terá settings separados e deverá comprovar: HTTPS; HSTS com rollout seguro; `DEBUG=False`; chave longa e aleatória fornecida por secret manager/environment; cookies de sessão e CSRF com `Secure`; políticas adequadas de CSRF/sessão; e hosts/origens explicitamente permitidos. A configuração local permanece apropriada para HTTP de desenvolvimento e não será artificialmente tratada como produção.

- HTTPS/HSTS em produção, headers seguros e CORS restrito;
- validação de tamanho/profundidade/tipo; paginação e timeouts;
- ORM parametrizado e escaping contextual no frontend;
- proteção contra SSRF em qualquer fetch externo, allowlist e bloqueio de rede interna;
- erro sem stack/segredo e request ID correlacionado;
- idempotência e controle de concorrência conforme `API.md`;
- dependência externa recebe timeout, retry apenas seguro e circuit breaker quando útil;
- health não expõe versão sensível, segredos ou detalhes internos.

## Pagamentos e ledger

- cartão é tokenizado/coletado pelo gateway e nunca atravessa/persiste no backend quando o provedor permitir;
- segredo de webhook por ambiente, rotação sobreposta e verificação do corpo bruto;
- recibo antes do efeito, transição válida e reconciliação independente;
- comissão/preço calculados no backend e snapshots imutáveis;
- lançamentos balanceados/append-only; correção por reversão/compensação;
- mudança de recebedor com MFA, alerta, eventual cooling-off e revisão conforme decisão;
- limites e dupla aprovação para reembolso/ajuste definidos antes do piloto;
- dashboard/alerta de assinatura inválida, backlog e divergência.

## Criptografia, chaves e segredos

- TLS em trânsito e criptografia gerenciada em banco, backup e storage;
- campos de alto risco recebem proteção adicional/pseudonimização conforme threat model;
- chaves e segredos em gerenciador, por ambiente e menor privilégio;
- rotação e revogação testadas; segredo não entra em repo, imagem, ticket ou log;
- acesso de produção é temporário/auditado; dump não sai sem autorização e proteção;
- fingerprint para unicidade de identificador usa chave separada e versionável quando adotado.

## Logs e telemetria

Permitir request ID, ator opaco autorizado, ação, alvo opaco, status, duração, origem e motivo seguro. Proibir senha, token, OTP, cookie, cartão, CPF/documento/placa completos, URL assinada, corpo de upload e evidência. Labels não contêm IDs pessoais. Redação automática é testada; acesso e retenção da telemetria seguem menor privilégio.

## Engenharia segura

- revisão de código e migration; branch protection quando repositório remoto existir;
- formatter/lint/type checks adotados, SAST, SCA, secret scan e container scan;
- locks e atualização regular de dependências;
- testes de autorização, mass assignment, IDOR, upload, webhook, idempotência e concorrência;
- DAST/pentest proporcional antes do piloto e após mudanças críticas;
- dados sintéticos; nenhum segredo/PII real em fixture, screenshot ou erro;
- vulnerabilidade tem severidade, owner, prazo e exceção formal temporária.

## Resposta a incidente

```text
detectar → classificar → conter → preservar evidência
→ avaliar dados/impacto → erradicar/recuperar
→ comunicar quando aplicável → retrospectiva e controles
```

O controlador avalia comunicação à ANPD/titulares conforme a Resolução CD/ANPD nº 15/2024; quando houver risco ou dano relevante, o prazo regulatório geral é de três dias úteis desde a ciência de que dados pessoais foram afetados, ressalvada regra específica. Comunicação preliminar incompleta é justificada e complementada em até vinte dias úteis. Operador notifica a plataforma sem demora, com objetivo contratual interno de até 24 horas. O runbook identifica encarregado/representante, jurídico, segurança, comunicação e operação. Todo incidente com dados pessoais, comunicado ou não, mantém avaliação e registro por ao menos cinco anos; detalhes finais ficam na tabela de retenção aprovada.

## Gates de segurança

| Gate       | Evidência obrigatória                                                                          |
| ---------- | ---------------------------------------------------------------------------------------------- |
| A1         | secrets/config, headers/cookies, CI scans, logging/redaction e threat model inicial            |
| A18        | autorização por objeto, upload privado, MFA admin, auditoria e teste de perda de elegibilidade |
| C7         | webhook, idempotência, ledger, reconciliação, limites e testes de fraude técnica               |
| pré-piloto | pentest/revisão, vulnerabilidades críticas/altas tratadas, incident drill e acessos revisados  |
| produção   | restore/rollback, rotação, monitoramento, contatos e exceções aceitas por owner                |
