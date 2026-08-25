#!/bin/sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$project_dir"

if [ ! -f .env.demo ]; then
  echo "Erro: .env.demo não encontrado em $project_dir" >&2
  exit 1
fi

mkdir -p backups
timestamp=$(date -u +%Y%m%dT%H%M%SZ)
output="backups/instrutorpro-demo-$timestamp.sql.gz"

docker compose --env-file .env.demo -f compose.demo.yaml exec -T db \
  sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB"' | gzip > "$output"

test -s "$output"
echo "Backup criado: $output"
