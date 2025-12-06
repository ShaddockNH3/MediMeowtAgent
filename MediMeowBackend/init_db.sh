#!/bin/bash

# 初始化数据库脚本
# 支持两种模式：
# 1. 使用 Docker Compose 启动 `db` 服务并在容器内执行 `init.sql`。
# 2. 在没有 Docker 的情况下，使用本地 `mysql` 客户端连接并执行 `init.sql`。

set -e

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$SCRIPT_DIR"

DB_HOST=${DB_HOST:-127.0.0.1}
DB_PORT=${DB_PORT:-3306}
DB_NAME=${DB_NAME:-medimeow_db}
DB_USER=${DB_USER:-root}
DB_PASS=${DB_PASS:-12345}

# Docker-compose 中的 root 密码默认值（与 docker-compose.yml 中的默认一致）
DB_ROOT_PASSWORD=${DB_ROOT_PASSWORD:-root_password}

echo "=========================================="
echo "MediMeow 初始化数据库 (init_db.sh)"
echo "=========================================="
echo "数据库目标: $DB_HOST:$DB_PORT  数据库: $DB_NAME  用户: $DB_USER"

if [ ! -f "./init.sql" ]; then
    echo "未找到本地 init.sql，无法初始化数据库。" >&2
    exit 1
fi

echo "使用本地 mysql 客户端连接并执行 init.sql..."
mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASS" < ./init.sql

echo "数据库初始化完成（本地客户端模式）。"
