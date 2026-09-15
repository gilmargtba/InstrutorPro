#!/bin/sh
# Run only in an isolated nginx:1.28-alpine container, never in the live gateway.
set -eu
apk add --no-cache openssl curl >/dev/null
for name in 179.199.136.4 instrutorprocnh.com.br; do
    mkdir -p "/etc/letsencrypt/live/$name"
    openssl req -x509 -newkey rsa:2048 -nodes -days 1 -subj "/CN=$name" \
        -keyout "/etc/letsencrypt/live/$name/privkey.pem" \
        -out "/etc/letsencrypt/live/$name/fullchain.pem" 2>/dev/null
done
cp /gateway.conf /etc/nginx/conf.d/default.conf
cat > /etc/nginx/conf.d/test-upstreams.conf <<'EOF'
server {
    listen 8080;
    listen 8000;
    location / { return 200 "test-upstream"; }
    location /gestao { return 307 /gestao/login; }
    location /api/v1/licenses { return 404; }
    location /api/v1/sync { return 204; }
}
EOF
mkdir -p /var/www/certbot/.well-known/acme-challenge
printf 'test-challenge' > /var/www/certbot/.well-known/acme-challenge/probe
nginx -t
nginx
check() {
    scheme="$1"; host="$2"; path="$3"; expected="$4"
    port=80
    [ "$scheme" != https ] || port=443
    # -k is exclusively for throwaway self-signed test certificates.
    code=$(curl --noproxy '*' -ksS --resolve "$host:$port:127.0.0.1" \
        -o /dev/null -w '%{http_code}' "$scheme://$host$path")
    [ "$code" = "$expected" ] || { echo "FAIL $host$path $code != $expected"; exit 1; }
}
for host in 179.199.136.4 instrutorprocnh.com.br; do
    check https "$host" / 200
    check https "$host" /gestao/ 307
    check https "$host" /api/v1/licenses 404
    check https "$host" /api/v1/sync 204
done
for host in instrutorprocnh.com.br www.instrutorprocnh.com.br; do
    check http "$host" /.well-known/acme-challenge/probe 200
    headers=$(curl --noproxy '*' -sSI --resolve "$host:80:127.0.0.1" \
        "http://$host/example?keep=1")
    printf '%s' "$headers" | grep -q '301 Moved Permanently'
    printf '%s' "$headers" | grep -q 'Location: https://instrutorprocnh.com.br/example?keep=1'
done
headers=$(curl --noproxy '*' -ksSI --resolve www.instrutorprocnh.com.br:443:127.0.0.1 \
    'https://www.instrutorprocnh.com.br/example?keep=1')
printf '%s' "$headers" | grep -q '^HTTP/.* 301'
printf '%s' "$headers" | grep -qi 'location: https://instrutorprocnh.com.br/example?keep=1'
nginx -s reload
check https instrutorprocnh.com.br / 200
echo GATEWAY_DOMAIN_TEST=PASS
