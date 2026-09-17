#!/bin/sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$project_dir"
env_file=${PRODUCTION_ENV_FILE:-.env.production}

echo "HEAD=$(git rev-parse HEAD)"
echo "ORIGIN_MAIN=$(git rev-parse origin/main)"
if [ -n "$(git status --porcelain=v1)" ]; then
    echo "WORKTREE=CLEAN_NO"
else
    echo "WORKTREE=CLEAN_YES"
fi

if [ ! -f "$env_file" ]; then
    echo "PRODUCTION_ENV=PRESENT_NO"
    exit 1
fi
echo "PRODUCTION_ENV=PRESENT_YES"

env_mode=$(stat -c '%a' "$env_file")
echo "PRODUCTION_ENV_MODE=$env_mode"
if [ "$env_mode" != "600" ]; then
    echo "FAIL: $env_file must have mode 600" >&2
    exit 1
fi

for variable in \
    SYNTHETIC_MARKETPLACE_ENABLED SYNTHETIC_DOCUMENT_UPLOAD_ENABLED \
    REAL_STUDENT_REGISTRATION_ENABLED REAL_INSTRUCTOR_REGISTRATION_ENABLED \
    REAL_INSTRUCTOR_PUBLICATION_ENABLED REAL_STUDENT_DEMAND_ENABLED \
    REAL_DOCUMENT_UPLOAD_ENABLED PUBLIC_DEMAND_MAP_ENABLED; do
    value=$(sed -n "s/^${variable}=//p" "$env_file" | tail -n 1 | tr '[:upper:]' '[:lower:]')
    if [ "$value" != "false" ]; then
        echo "$variable=FAIL_EXPECTED_FALSE"
        exit 1
    fi
    echo "$variable=FALSE"
done

authorization=$(sed -n 's/^REAL_PRODUCTION_AUTHORIZATION=//p' "$env_file" | tail -n 1)
if [ "$authorization" != "NOT_GRANTED" ]; then
    echo "REAL_PRODUCTION_AUTHORIZATION=FAIL_EXPECTED_NOT_GRANTED"
    exit 1
fi
echo "REAL_PRODUCTION_AUTHORIZATION=NOT_GRANTED"

docker compose --env-file "$env_file" -f compose.production.yaml config --quiet
echo "COMPOSE_CONFIG=PASS"
docker compose --env-file "$env_file" -f compose.production.yaml ps
