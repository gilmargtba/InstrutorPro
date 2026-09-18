# Matriz de retenção do piloto controlado — Fatia 8D

Status em 18/09/2026: **OPEN-008 PARTIAL**. Esta matriz delimita os tratamentos necessários ao
piloto, mas não substitui revisão jurídica nem autoriza dados pessoais reais.

| Categoria | Finalidade no piloto | Papel pretendido | Base a confirmar | Retenção operacional | Evento inicial/final | Ação final | Exceções/revisão |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Conta | autenticação, segurança e exercício de direitos | controlador | execução de contrato e legítimo interesse, sujeitos a validação | enquanto ativa | criação/encerramento | bloquear acesso e restringir o registro até regra de eliminação aprovada | fraude, disputa e obrigação legal; prazo jurídico pendente |
| Dados cadastrais | operar perfil do aluno ou instrutor | controlador | execução de contrato, sujeita a validação | enquanto necessários ao perfil ativo | coleta/encerramento ou correção | corrigir, anonimizar ou eliminar conforme solicitação e regra aprovada | obrigação legal e defesa de direitos; prazo pendente |
| Aceites legais | provar versão e momento do aceite | controlador | cumprimento de obrigação e exercício regular de direitos, sujeitos a validação | durante a relação e período posterior ainda não definido | aceite/fim da relação | restringir acesso e eliminar ao fim do prazo aprovado | litígio e obrigação legal; prazo jurídico pendente |
| Solicitações de privacidade | atender e demonstrar direitos do titular | controlador | cumprimento de obrigação legal | enquanto necessárias à tramitação e prestação de contas | abertura/encerramento do pedido | restringir e eliminar após prazo aprovado | ANPD, disputa e obrigação legal; prazo pendente |
| Logs de auditoria | segurança, rastreabilidade e responsabilização | controlador | legítimo interesse e obrigação legal, sujeitos a LIA/revisão | janela operacional ainda não aprovada | evento/expiração da janela | anonimizar ou eliminar, preservando apenas exceção autorizada | incidente, fraude, disputa; prazo e segregação pendentes |
| Analytics do marketplace | medir busca, impressão, visualização e contato sem conteúdo | controlador | legítimo interesse, sujeito a LIA | agregação por sessão e janela horária; prazo total pendente | evento/expiração da janela | agregar irreversivelmente ou eliminar | sem fingerprinting e sem conteúdo de WhatsApp |
| Perfil profissional | permitir revisão manual e descoberta somente após aprovação | controlador | execução de contrato e legítimo interesse, sujeitos a validação | enquanto o perfil estiver ativo ou em revisão | cadastro/despublicação ou encerramento | despublicar imediatamente; depois restringir e eliminar conforme regra aprovada | disputa, segurança e obrigação legal; prazo pendente |
| Evidência de verificação | provar decisão manual sem reter documento | controlador | legítimo interesse/exercício de direitos, sujeitos a validação | durante validade e período posterior não definido | verificação/expiração ou revogação | restringir e eliminar após prazo aprovado | registrar apenas autoridade, método, data, operador, status e referência mínima permitida |

Documentos profissionais reais, cartões, conteúdo de conversa no WhatsApp e coordenada residencial
precisa não fazem parte desta matriz porque continuam proibidos no piloto.

## Conclusão do gate

`OPEN-008=PARTIAL`: categorias, finalidades, minimização, eventos e ações foram identificados, mas
faltam a confirmação formal das bases, dos papéis do agente, das exceções e dos prazos posteriores
ao encerramento. Até essa decisão, `REAL_PERSONAL_DATA` e todas as capacidades que dela dependem
devem permanecer desabilitadas. Nenhum prazo legal foi presumido.
