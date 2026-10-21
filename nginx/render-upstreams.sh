#!/bin/sh
set -eu

dest="${1:-/etc/nginx/conf.d/00-upstreams.conf}"
tmp="${dest}.tmp"

collect() {
  host="$1"
  getent ahostsv4 "$host" 2>/dev/null | awk '/STREAM/ {print $1}' | sort -u || true
}

write_one() {
  name="$1"
  host="$2"
  port="$3"
  echo "upstream ${name} {"
  ips="$(collect "$host")"
  if [ -z "$ips" ]; then
    echo "    server 127.0.0.1:9 down;"
  else
    printf '%s\n' "$ips" | while IFS= read -r ip; do
      if [ -n "$ip" ]; then
        echo "    server ${ip}:${port} max_fails=2 fail_timeout=5s;"
      fi
    done
  fi
  echo "}"
  echo
}

{
  write_one api_upstream api 8000
  write_one web_upstream web 3000
  write_one bot_upstream bot 8081
} > "$tmp"

mv "$tmp" "$dest"
