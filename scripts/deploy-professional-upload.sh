#!/bin/sh
# Owner-authorized hotfix. Run on the existing VPS checkout, never against a new database.
set -eu
umask 077
test "${1:-}" = "--deploy-and-enable"
cd /home/gilmar/InstrutorPro
test "$(git branch --show-current)" = main
test -z "$(git status --porcelain --untracked-files=no)"
test "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)"
printf 'VPS_HEAD_AFTER='; git rev-parse HEAD

dc() { docker compose --env-file .env.production -f compose.production.yaml "$@"; }
dc exec -T backend python manage.py shell -c \
  'from django.conf import settings; assert not settings.REAL_DOCUMENT_UPLOADS; assert not settings.REAL_DOCUMENT_UPLOAD_ENABLED'
test "$(docker inspect instrutorpro-backend-1 --format '{{range .Mounts}}{{if eq .Destination "/app/private_documents"}}{{.Type}}{{end}}{{end}}')" = volume
sh scripts/backup-production.sh
backup_dir=/home/gilmar/backups/instrutorpro/config
mkdir -p "$backup_dir"
chmod 700 "$backup_dir"
config_backup="$backup_dir/env-upload-hotfix-$(date -u +%Y%m%dT%H%M%SZ)"
cp -- .env.production "$config_backup"
chmod 600 "$config_backup"

dc build backend worker scheduler frontend
dc run --rm --no-deps backend python manage.py migrate --noinput
dc --profile document-upload up -d --no-deps --wait --wait-timeout 180 clamav
dc up -d --no-deps --wait --wait-timeout 180 backend frontend worker scheduler
dc exec -T backend python manage.py check
dc exec -T backend python manage.py check_document_upload --confirm-technical-test

# Only reached after all live technical checks pass. No privacy/retention approval is fabricated.
env_changed=no
rollback() {
    result=$?
    if [ "$result" -ne 0 ] && [ "$env_changed" = yes ]; then
        cp -- "$config_backup" .env.production
        dc up -d --no-deps --wait --wait-timeout 180 backend worker scheduler || true
        echo 'DOCUMENT_UPLOAD_PRODUCTION_STATUS=BLOCKED'
        echo 'BLOCKER=POST_ACTIVATION_CHECK_FAILED_FLAGS_RESTORED'
    fi
    exit "$result"
}
trap rollback EXIT
python3 - <<'PY'
import os
import tempfile
from pathlib import Path
path = Path('.env.production')
updates = {'REAL_DOCUMENT_UPLOADS': 'true', 'REAL_DOCUMENT_UPLOAD_ENABLED': 'true',
           'PROFESSIONAL_DOCUMENT_UPLOAD_MODE': 'PRODUCTION'}
lines = [line for line in path.read_text().splitlines()
         if line.split('=', 1)[0].strip() not in updates]
lines.extend(f'{key}={value}' for key, value in updates.items())
fd, name = tempfile.mkstemp(prefix='.env-upload-', dir='.')
try:
    with os.fdopen(fd, 'w') as stream:
        stream.write('\n'.join(lines) + '\n')
    os.chmod(name, 0o600)
    os.replace(name, path)
finally:
    if os.path.exists(name):
        os.unlink(name)
PY
env_changed=yes
dc up -d --no-deps --wait --wait-timeout 180 backend worker scheduler
dc exec -T backend python manage.py check
dc exec -T backend python manage.py shell -c \
  'from django.conf import settings; from apps.marketplace.real_documents import upload_available; assert settings.REAL_DOCUMENT_UPLOADS; assert settings.REAL_DOCUMENT_UPLOAD_ENABLED; assert settings.PROFESSIONAL_DOCUMENT_UPLOAD_MODE == "PRODUCTION"; assert not getattr(settings,"REAL_AUTOMATIC_PUBLICATION",False); assert upload_available(); print("REAL_DOCUMENT_UPLOADS=true"); print("PROFESSIONAL_DOCUMENT_UPLOAD_MODE=PRODUCTION")'
dc exec -T backend python manage.py check_document_upload --confirm-technical-test
curl --fail --silent --show-error --max-time 20 https://instrutorprocnh.com.br/api/v1/readiness/
echo
echo 'DOCUMENT_UPLOAD_PRODUCTION_STATUS=ENABLED'
echo 'AUTOMATIC_VERIFICATION=DISABLED'
echo 'AUTOMATIC_PUBLICATION=DISABLED'
env_changed=no
