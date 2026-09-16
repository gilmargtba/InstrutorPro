#!/bin/sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$project_dir"
env_file=${PRODUCTION_ENV_FILE:-.env.production}

if [ ! -f "$env_file" ]; then
    echo "FAIL: production environment file not found: $env_file" >&2
    exit 1
fi
if grep -Eq 'REPLACE_|change-with-|SERVER_IP_OR_DOMAIN' "$env_file"; then
    echo "FAIL: unresolved placeholder in $env_file" >&2
    exit 1
fi

docker compose --env-file "$env_file" -f compose.production.yaml config --quiet
docker compose --env-file "$env_file" -f compose.production.yaml run --rm --no-deps backend \
    python manage.py check --deploy
docker compose --env-file "$env_file" -f compose.production.yaml run --rm --no-deps backend \
    python manage.py production_readiness

echo PRODUCTION_CONFIG_VALIDATION=PASS
echo REAL_PRODUCTION_AUTHORIZATION=NOT_GRANTED
