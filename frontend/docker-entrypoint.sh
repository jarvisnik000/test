#!/bin/sh
set -e

PORT="${PORT:-8080}"

sed -i "s/8080/$PORT/g" /etc/nginx/conf.d/default.conf

exec nginx -g "daemon off;"
