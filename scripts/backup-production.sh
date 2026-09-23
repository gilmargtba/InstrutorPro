#!/bin/sh
set -eu
umask 077

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$project_dir"

env_file=${PRODUCTION_ENV_FILE:-.env.production}
backup_root=${PRODUCTION_BACKUP_DIR:-/home/gilmar/backups/instrutorpro/production}

if [ ! -f "$env_file" ]; then
    echo "FAIL: production environment file not found: $env_file" >&2
    exit 1
fi

mkdir -p "$backup_root"
chmod 700 "$backup_root"
timestamp=$(date -u +%Y%m%dT%H%M%SZ)
temporary="$backup_root/.instrutorpro-$timestamp.dump.tmp"
output="$backup_root/instrutorpro-$timestamp.dump"
documents_temporary="$backup_root/.private-documents-$timestamp.tar.tmp"
documents_output="$backup_root/private-documents-$timestamp.tar"

cleanup() {
    rm -f -- "$temporary" "$documents_temporary"
}
trap cleanup EXIT HUP INT TERM

docker compose --env-file "$env_file" -f compose.production.yaml exec -T db \
    sh -c 'pg_dump --format=custom --no-owner --no-acl -U "$POSTGRES_USER" -d "$POSTGRES_DB"' \
    > "$temporary"

test -s "$temporary"
docker compose --env-file "$env_file" -f compose.production.yaml exec -T db \
    pg_restore --list < "$temporary" > /dev/null
docker compose --env-file "$env_file" -f compose.production.yaml exec -T backend \
    tar -C /app/private_documents -cf - . > "$documents_temporary"
test -s "$documents_temporary"
tar -tf "$documents_temporary" > /dev/null
mv -- "$temporary" "$output"
mv -- "$documents_temporary" "$documents_output"
trap - EXIT HUP INT TERM
chmod 600 "$output" "$documents_output"

sha256sum "$output" > "$output.sha256"
sha256sum "$documents_output" > "$documents_output.sha256"
chmod 600 "$output.sha256" "$documents_output.sha256"

echo "BACKUP_PATH=$output"
echo "BACKUP_BYTES=$(wc -c < "$output" | tr -d ' ')"
echo "BACKUP_SHA256=$(cut -d ' ' -f 1 "$output.sha256")"
echo "BACKUP_ARCHIVE_VALID=YES"
echo "PRIVATE_DOCUMENT_BACKUP_PATH=$documents_output"
echo "PRIVATE_DOCUMENT_BACKUP_BYTES=$(wc -c < "$documents_output" | tr -d ' ')"
echo "PRIVATE_DOCUMENT_BACKUP_SHA256=$(cut -d ' ' -f 1 "$documents_output.sha256")"
echo "PRIVATE_DOCUMENT_BACKUP_ARCHIVE_VALID=YES"
echo "RESTORE_EXECUTED=NO"
