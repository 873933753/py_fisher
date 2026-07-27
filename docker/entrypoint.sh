#!/bin/sh
set -e

# 只做启动前准备；真正跑什么服务由 Dockerfile 的 CMD（或 compose command）决定
echo "[entrypoint] APP_ENV=${APP_ENV:-unset}"
echo "[entrypoint] running alembic upgrade head"
alembic upgrade head

echo "[entrypoint] exec: $*"
exec "$@"
