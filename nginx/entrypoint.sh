#!/bin/sh
set -eu

i=0
while [ "$i" -lt 30 ]; do
  if getent ahostsv4 api >/dev/null 2>&1 && getent ahostsv4 web >/dev/null 2>&1; then
    break
  fi
  i=$((i + 1))
  sleep 1
done

sh /opt/nginx/render-upstreams.sh /etc/nginx/conf.d/00-upstreams.conf
nginx -t
nginx -g "daemon off;" &
pid=$!

stop() {
  kill -TERM "$pid" 2>/dev/null || true
  wait "$pid" 2>/dev/null || true
  exit 0
}
trap stop TERM INT

while kill -0 "$pid" 2>/dev/null; do
  sleep 5
  if ! sh /opt/nginx/render-upstreams.sh /tmp/00-upstreams.conf; then
    continue
  fi
  current="$(cat /etc/nginx/conf.d/00-upstreams.conf)"
  fresh="$(cat /tmp/00-upstreams.conf)"
  if [ "$current" != "$fresh" ]; then
    cp /tmp/00-upstreams.conf /etc/nginx/conf.d/00-upstreams.conf
    if nginx -t; then
      nginx -s reload || true
    fi
  fi
done

wait "$pid"
