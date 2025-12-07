#!/bin/bash

# 初始化数据库脚本
# 支持两种模式：
# 1. 使用 Docker Compose 启动 `db` 服务并在容器内执行 `init.sql`。
# 2. 在没有 Docker 的情况下，使用本地 `mysql` 客户端连接并执行 `init.sql`。

set -e

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$SCRIPT_DIR"

# 加载 .env 文件
if [ -f ".env" ]; then
    echo "读取 .env 配置文件..."
    set -a
    source .env
    set +a
else
    echo "警告: 未找到 .env 文件，使用默认值"
fi

# 从 DATABASE_URL 解析数据库连接信息
# 格式: mysql+pymysql://user:password@host:port/database
if [ -n "$DATABASE_URL" ]; then
    # 提取用户名
    DB_USER=$(echo $DATABASE_URL | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
    # 提取密码
    DB_PASS=$(echo $DATABASE_URL | sed -n 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/p')
    # 提取主机
    DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
    # 提取端口
    DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
    # 提取数据库名
    DB_NAME=$(echo $DATABASE_URL | sed -n 's/.*\/\([^?]*\).*/\1/p')
fi

# 设置默认值（如果解析失败）
DB_HOST=${DB_HOST:-127.0.0.1}
DB_PORT=${DB_PORT:-3306}
DB_NAME=${DB_NAME:-medimeow_db}
DB_USER=${DB_USER:-root}
DB_PASS=${DB_PASS:-12345}

echo "=========================================="
echo "MediMeow 初始化数据库 (init_db.sh)"
echo "=========================================="
echo "数据库目标: $DB_HOST:$DB_PORT  数据库: $DB_NAME  用户: $DB_USER"
echo ""

# 检查数据库连接
echo "正在检查数据库连接..."
if ! MYSQL_PWD="$DB_PASS" mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" --protocol=TCP -e "SELECT 1" > /dev/null 2>&1; then
    echo "✗ 无法连接到数据库服务器"
    echo ""
    echo "请检查:"
    echo "  1. 数据库服务是否已启动"
    echo "  2. 连接信息是否正确: $DB_HOST:$DB_PORT"
    echo "  3. 用户名和密码是否正确: $DB_USER"
    echo ""
    echo "提示: 如果使用 Docker，请先启动数据库容器:"
    echo "  docker-compose up -d db"
    echo "  或检查容器状态: docker ps"
    echo ""
    exit 1
fi
echo "✓ 数据库连接成功"
echo ""

if [ ! -f "./init.sql" ]; then
    echo "未找到本地 init.sql，无法初始化数据库。" >&2
    exit 1
fi

echo "==========================================
警告: 此操作将删除现有数据库并重新创建
=========================================="
read -p "是否继续? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "操作已取消"
    exit 0
fi
echo ""

echo "正在删除旧数据库 $DB_NAME (如果存在)..."
MYSQL_PWD="$DB_PASS" mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" --protocol=TCP -e "DROP DATABASE IF EXISTS $DB_NAME;" 2>&1

echo "使用本地 mysql 客户端连接并执行 init.sql..."
MYSQL_PWD="$DB_PASS" mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" --protocol=TCP < ./init.sql

if [ $? -eq 0 ]; then
    echo "✓ 数据库结构创建成功"
else
    echo "✗ 数据库初始化失败" >&2
    exit 1
fi
echo ""

echo "=========================================="
echo "开始导入测试数据"
echo "========================================="
echo ""

# 步骤 1: 创建科室数据
echo "[1/3] 正在创建科室数据..."
python create_departments.py
if [ $? -eq 0 ]; then
    echo "✓ 科室数据创建成功"
else
    echo "✗ 科室数据创建失败"
    exit 1
fi
echo ""

# 步骤 2: 创建医生数据
echo "[2/3] 正在创建医生数据..."
python create_doctors_for_all_departments.py
if [ $? -eq 0 ]; then
    echo "✓ 医生数据创建成功"
else
    echo "✗ 医生数据创建失败"
    exit 1
fi
echo ""

# 步骤 3: 导入问卷数据
echo "[3/3] 正在导入问卷数据..."
python create_questionnaires_from_md.py
if [ $? -eq 0 ]; then
    echo "✓ 问卷数据导入成功"
else
    echo "✗ 问卷数据导入失败"
    exit 1
fi
echo ""

echo "=========================================="
echo "✓ 数据库初始化完成！"
echo "=========================================="
echo ""

# 步骤 4: 创建视图、存储过程和触发器
echo "[4/4] 正在创建视图、存储过程和触发器..."
if [ -f "./init_views_procedures.sql" ]; then
    MYSQL_PWD="$DB_PASS" mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" --protocol=TCP < ./init_views_procedures.sql
    if [ $? -eq 0 ]; then
        echo "✓ 视图、存储过程和触发器创建成功"
    else
        echo "✗ 视图、存储过程和触发器创建失败"
        exit 1
    fi
else
    echo "⚠ 未找到 init_views_procedures.sql，跳过此步骤"
fi
echo ""

echo "=========================================="
echo "✓ 所有初始化步骤完成！"
echo "=========================================="
echo ""
echo "已完成:"
echo "  1. 数据库结构创建"
echo "  2. 科室数据导入"
echo "  3. 医生数据导入"
echo "  4. 问卷数据导入"
echo "  5. 视图、存储过程和触发器创建"
echo ""
