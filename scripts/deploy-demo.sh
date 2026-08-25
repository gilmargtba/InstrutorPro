#!/bin/sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$project_dir"

if [ ! -f .env.demo ]; then
  echo "Erro: copie .env.demo.example para .env.demo e configure os valores." >&2
  exit 1
fi

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "Erro: existem alterações locais no servidor. Deploy interrompido." >&2
  exit 1
fi

if docker compose --env-file .env.demo -f compose.demo.yaml ps --status running db | grep -q db; then
  ./scripts/backup-demo.sh
fi

git pull --ff-only origin main
docker compose --env-file .env.demo -f compose.demo.yaml build
docker compose --env-file .env.demo -f compose.demo.yaml up -d --remove-orphans

attempt=0
until docker compose --env-file .env.demo -f compose.demo.yaml exec -T frontend \
  wget -qO- http://127.0.0.1:8080/api/v1/readiness/ >/dev/null; do
  attempt=$((attempt + 1))
  if [ "$attempt" -ge 30 ]; then
    echo "Erro: readiness não respondeu após o deploy." >&2
    docker compose --env-file .env.demo -f compose.demo.yaml ps
    exit 1
  fi
  sleep 2
done

docker compose --env-file .env.demo -f compose.demo.yaml ps
echo "Deploy concluído e readiness aprovado."
