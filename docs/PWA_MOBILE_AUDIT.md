# Auditoria PWA, Android e iOS — 17/10/2026

## Base compartilhada e limites atuais

- Há um único frontend Angular 22 em `frontend/`. O build web usa `src/index.html` e a API relativa `/api/v1`; o build Capacitor usa `src/index.mobile.html`, a API HTTPS de produção e o mesmo código de mapas, perfil público, localização e WhatsApp. O projeto iOS usa `ios/App/App.xcodeproj` com Swift Package Manager (`CapApp-SPM`), sem Podfile. Bundle ID: `br.com.instrutorprocnh.app`; iOS mínimo 15.
- O web/PWA usa sessão e CSRF de mesma origem. O app nativo deliberadamente usa `mobileRoutes`, somente busca pública de alunos, sem cookies de sessão. Cadastro/login de aluno e instrutor, painel e upload autenticado existem no site web; **não** foram liberados no app nativo. Isso requer um contrato de autenticação nativa, proteção CSRF/credenciais e testes em aparelhos reais, não apenas expor rotas.
- A busca pública, mapa e WhatsApp consultam a mesma API e os gates do backend. A localização é solicitada por ação do usuário. O app não deve persistir coordenada individual do aluno. A foto de perfil e documentos são enviados no fluxo web autenticado e sujeitos aos gates existentes.
- Disponibilidade, agendamento e histórico de aulas não são uma jornada comercial real autorizada neste MVP; rotas de aula/dashboards demonstrativos não devem ser apresentadas como reserva confirmada no PWA ou app. Notificação por e-mail de verificação/publicação é distinta de push; Android não tem push operacional (`google-services.json` opcional e plugin push ausente).

## PWA preparado nesta branch

- Manifesto e ícones da marca existente, modo `standalone`, metadados Safari, `viewport-fit=cover`, safe areas, instruções de instalação iPhone na página `/baixar-app` e aviso de atualização controlado pelo usuário.
- Service worker registrado apenas no web de produção, nunca em Capacitor. Ele guarda somente ícones/logotipo/manifesto/arquivo offline genérico e bundles Angular com hash. Navegações sempre consultam a rede; API, Admin, documentos, fotos privadas, tokens, páginas e respostas autenticadas não são guardados. Sem conexão, nenhuma conta ou documento fica acessível offline.
- O servidor está preparado para servir `manifest.webmanifest` com MIME correto e `sw.js` sem cache persistente do próprio script. Publicação HTTPS ainda depende de revisão de deploy; nenhum arquivo desta branch foi enviado à VPS.

## Identidade, privacidade e segurança

- Backend continua autoritativo para upload, antimalware, autorização por objeto, revisão humana, UF, publicação e contato. Uma foto segurando CNH é apenas evidência visual para revisor, **não** reconhecimento facial/biometria automática ou autorização oficial.
- A base legal, o aviso versionado, a retenção e eventual avaliação de risco para coleta de foto com CNH devem estar aprovados antes de habilitar uma nova coleta em produção. Esta mudança não altera flags de coleta. Não armazenar CNH/biometria em cache, logs, notificações ou mídia pública.
- Duplicidade de documento e exclusão segura exigem confirmação da política de retenção e testes de backend específicos antes de ampliar o fluxo para nativo. A rota de privacidade/conta existe no web, mas o percurso de exclusão de conta precisa de auditoria para App Store.

## Push e publicação Apple: preparação, não ativação

- Web Push no iPhone requer web app instalado na Tela de Início (iOS/iPadOS 16.4+), service worker, chave pública VAPID, assinatura no backend, HTTPS e pedido de permissão após gesto explícito. Ainda faltam endpoint autenticado de inscrição/cancelamento, preferências e consentimento versionado, outbox e deduplicação por evento+destinatário+canal. Nenhuma chave VAPID ou assinatura foi criada; o service worker atual não processa `push`.
- APNs nativo requer Apple Developer, entitlement/capability, credenciais privadas no Codemagic ou cofre, plugin nativo e API de token com revogação. Não há push iOS/Android ativo nesta branch. Payload futuro deve conter apenas texto mínimo e identificador opaco, nunca dados de CNH.
- O workflow de simulador Codemagic permanece sem assinatura. O workflow IPA mantém configuração futura de perfis/assinatura, mas **não** publica automaticamente no TestFlight ou App Store. Bundle ID, versão/build number, ícones, splash, descrições de permissão, política de privacidade, exclusão de conta e credenciais de revisão exigem checagem final em macOS/iPhone antes do envio manual.
- `Info.plist` já descreve localização sob ação do aluno; ainda não há captura de CNH no app nativo. Se isso for aprovado futuramente, adicionar as descrições de câmera/fototeca exigidas pelo mecanismo escolhido e testar o consentimento no iPhone antes de submeter à App Store — não declarar uma permissão sem funcionalidade correspondente.

## Validação e próximos gates

- Local: testes Angular (75), build web, build mobile, `cap sync ios`, Android `assembleDebug` e testes de política de cache PWA (4) passaram; os builds Angular mantêm avisos de orçamento preexistentes. O primeiro build Android precisou apontar o SDK já instalado nesta máquina, sem modificar o repositório.
- Não verificados aqui: instalação/standalone e sessão no Safari iPhone real; câmera e upload de CNH em iPhone; geolocalização/WhatsApp em iOS real; Xcode/IPA em macOS; assinatura Apple; push; reserva/histórico reais. O build de simulador Codemagic foi informado pelo proprietário como bem-sucedido, não reexecutado nesta branch.
- Para publicar o PWA futuramente: revisar privacidade e ambiente, fazer merge autorizado da branch, build web, deploy HTTPS, verificar resposta de manifesto/SW/MIME, instalar pelo Safari e ensaiar atualização, login/logout, busca e ausência de dados sensíveis em cache com iPhone real. Não instalar PWA como substituto de uma revisão regulatória.
- Para IPA futuro: configurar Apple Developer, App Store Connect e assinatura privada no Codemagic; executar manualmente o workflow assinado; testar o IPA em dispositivo e TestFlight; obter autorização separada antes de qualquer envio à Apple.

Fontes técnicas: [WebKit — Web Push em apps da Tela de Início](https://webkit.org/blog/13878/), [Capacitor — configuração iOS](https://capacitorjs.com/docs/ios/configuration).
