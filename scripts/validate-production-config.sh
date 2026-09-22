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
registration_mode=$(sed -n 's/^INSTRUCTOR_REGISTRATION_MODE=//p' "$env_file" | tail -n 1)
echo "INSTRUCTOR_REGISTRATION_MODE=${registration_mode:-DISABLED}"
verification_mode=$(sed -n 's/^PROFESSIONAL_VERIFICATION_MODE=//p' "$env_file" | tail -n 1)
echo "PROFESSIONAL_VERIFICATION_MODE=${verification_mode:-DISABLED}"
authorization=$(sed -n 's/^REAL_PRODUCTION_AUTHORIZATION=//p' "$env_file" | tail -n 1)
echo "REAL_PRODUCTION_AUTHORIZATION=${authorization:-NOT_GRANTED}"
