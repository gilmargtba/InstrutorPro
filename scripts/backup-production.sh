#!/bin/sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$project_dir"

env_file=${PRODUCTION_ENV_FILE:-.env.production}
backup_root=${PRODUCTION_BACKUP_DIR:-/home/gilmar/backups/instrutorpro/production}

if [ ! -f "$env_file" ]; then
    echo "FAIL: production environment file not found: $env_file" >&2
    exit 1
fi

mkdir -p "$backup_root"
timestamp=$(date -u +%Y%m%dT%H%M%SZ)
temporary="$backup_root/.instrutorpro-$timestamp.dump.tmp"
output="$backup_root/instrutorpro-$timestamp.dump"

cleanup() {
    rm -f -- "$temporary"
}
trap cleanup EXIT HUP INT TERM

docker compose --env-file "$env_file" -f compose.production.yaml exec -T db \
    sh -c 'pg_dump --format=custom --no-owner --no-acl -U "$POSTGRES_USER" -d "$POSTGRES_DB"' \
    > "$temporary"

test -s "$temporary"
docker compose --env-file "$env_file" -f compose.production.yaml exec -T db \
    pg_restore --list < "$temporary" > /dev/null
mv -- "$temporary" "$output"
trap - EXIT HUP INT TERM
chmod 600 "$output"

sha256sum "$output" > "$output.sha256"
chmod 600 "$output.sha256"

echo "BACKUP_PATH=$output"
echo "BACKUP_BYTES=$(wc -c < "$output" | tr -d ' ')"
echo "BACKUP_SHA256=$(cut -d ' ' -f 1 "$output.sha256")"
echo "BACKUP_ARCHIVE_VALID=YES"
echo "RESTORE_EXECUTED=NO"
