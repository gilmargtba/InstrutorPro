# ADMIN-PROD-01 — painel administrativo controlado

## Escopo

O Django Admin existente é reutilizado para organização/controlador, workflow profissional DEMO e
consulta de auditoria. O gate não libera cadastro público, dados/documentos reais de instrutor,
marketplace, pagamentos ou integrações governamentais. As ações profissionais existentes continuam
explicitamente DEMO até um gate próprio de elegibilidade real.

## Controles

- `DEBUG=False`, segredo somente por ambiente, hosts/origens explícitos;
- TLS público para `179.199.136.4`, cookies Secure, sessão de 30 minutos e encerramento no navegador;
- MFA TOTP obrigatório em todo o Admin, com dez códigos de recuperação de uso único;
- cinco falhas de login por combinação usuário/IP bloqueiam por uma hora;
- permissões ADMIN-PROD-01 explícitas e auditadas;
- banco, Redis e backend somente na rede privada; frontend ligado a `127.0.0.1:8080` em produção;
- seeds DEMO somente quando `DJANGO_LOAD_DEMO_DATA=true`.

## Bootstrap humano

Depois de criar uma senha forte sem registrá-la em shell, log ou Git:

```bash
docker compose --env-file .env.demo -f compose.demo.yaml exec backend \
  python manage.py createsuperuser
docker compose --env-file .env.demo -f compose.demo.yaml exec backend \
  python manage.py grant_admin_prod_access USUARIO
docker compose --env-file .env.demo -f compose.demo.yaml exec backend \
  python manage.py enroll_admin_mfa USUARIO
```

O último comando mostra uma URI TOTP e códigos de recuperação uma única vez. O responsável deve
escaneá-la no aplicativo autenticador e guardar os códigos offline. Segredos MFA não entram no Git,
documentação, logs ou relatório.

## Backup e rollback antes do deploy

1. Confirmar `/home/gilmar/InstrutorPro`, branch, HEAD e árvore limpa.
2. Criar diretório privado datado fora do repositório.
3. Executar `pg_dump -Fc` pelo container `db` e validar com `pg_restore --list`.
4. Registrar lista de volumes e copiar `.env.demo` preservando modo `0600`, sem exibir conteúdo.
5. Guardar o SHA anterior. Em falha, voltar o código a esse SHA por checkout explícito, reconstruir
   os serviços anteriores e restaurar o dump apenas se uma migration tiver alterado dados de modo
   incompatível. Nunca usar `git reset --hard` nem apagar volumes.

## HTTPS no IP

Usar Certbot 5.4 ou superior e certificado IP short-lived da Let's Encrypt, inicialmente em staging.
O arquivo `deploy/nginx/instrutorpro-ip.conf` termina TLS no Nginx do host e encaminha ao frontend em
`127.0.0.1:8080`. O timer systemd renova a cada 12 horas; a emissão dura cerca de seis dias, portanto
falha de renovação é bloqueador operacional.

## Critério de prontidão

READY exige evidência no Ubuntu de backup validado, certificado/renovação, migrations, containers,
health/readiness, login com senha+TOTP, negativa sem MFA/permissão, organização e auditoria. Enquanto
o acesso SSH e o bootstrap humano não ocorrerem, o estado é `BLOCKED`.
