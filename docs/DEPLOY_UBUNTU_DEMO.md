# Deploy da demo no Ubuntu

Este ambiente usa somente dados sintéticos e não representa produção, homologação
regulatória ou autorização oficial. O desenvolvimento permanece no Windows; o Ubuntu
recebe apenas commits publicados na branch `main`.

## Requisitos do servidor

- Ubuntu Server 24.04 LTS recomendado;
- 2 vCPU, 4 GB RAM e 30 GB de disco como ponto inicial para a demo;
- Docker Engine com plugin Compose;
- Git e `curl`;
- portas SSH e HTTP liberadas no firewall. Libere HTTPS quando houver domínio/TLS.

## Instalação inicial

```bash
sudo apt update
sudo apt install -y ca-certificates curl git
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker "$USER"
```

Encerre e abra novamente a sessão SSH após adicionar o usuário ao grupo `docker`.
Clone o repositório privado usando uma chave SSH de deploy somente leitura ou uma
credencial GitHub apropriada; não grave token na URL ou no histórico do shell.

```bash
git clone https://github.com/gilmargtba/InstrutorPro.git
cd InstrutorPro
cp .env.demo.example .env.demo
chmod 600 .env.demo
```

Edite `.env.demo` no servidor. Gere valores diferentes e aleatórios para o segredo
Django, senha do Postgres e senha do Admin. `DATABASE_URL` deve conter a mesma senha
do Postgres. Troque `SERVER_IP_OR_DOMAIN` pelo IP público ou domínio, sem caminho.

## Primeiro deploy

```bash
chmod +x scripts/*.sh
./scripts/deploy-demo.sh
```

Acesse `http://IP_DO_SERVIDOR/`. Confirme também:

```bash
curl --fail http://127.0.0.1/api/v1/health/
curl --fail http://127.0.0.1/api/v1/readiness/
docker compose --env-file .env.demo -f compose.demo.yaml ps
```

Postgres, Redis, Django, Celery e scheduler ficam somente na rede Docker privada; só
o proxy frontend publica uma porta no host. Os volumes persistem entre atualizações.

## Atualizações após mudanças no Windows

Depois de testar e enviar os commits desta máquina ao GitHub, execute no Ubuntu:

```bash
cd InstrutorPro
./scripts/deploy-demo.sh
```

O script recusa árvore Git alterada, cria backup se o banco estiver rodando, usa
`git pull --ff-only`, reconstrói as imagens, aplica migrations/seeds idempotentes e
aguarda o readiness. Backups ficam em `backups/`, que não é versionado. Defina uma
política de cópia externa e retenção antes de usar dados que não sejam sintéticos.

## Diagnóstico e rollback

```bash
docker compose --env-file .env.demo -f compose.demo.yaml logs --tail=200 backend frontend
docker compose --env-file .env.demo -f compose.demo.yaml ps
git log --oneline -5
```

Para voltar o código, identifique o commit anterior, faça checkout dele de forma
explícita e recrie os containers. Não reverta migration de banco cegamente; prefira
roll-forward. Restauração de backup deve ser ensaiada antes do piloto.

## HTTPS

Não apresente login ou Admin por HTTP fora de uma rede confiável. Quando o domínio
apontar para o servidor, coloque um proxy TLS (Caddy, Nginx/Certbot ou Cloudflare) na
frente da porta interna, ajuste `CORS_ALLOWED_ORIGINS` para `https://DOMINIO`, defina
`DJANGO_HTTPS_ENABLED=true` e só habilite HSTS depois de validar HTTPS e renovação.
