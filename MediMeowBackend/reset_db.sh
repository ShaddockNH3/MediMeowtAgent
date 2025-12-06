#!/bin/bash

# MediMeow 数据库重置脚本
# 用于开发和测试环境快速重置数据库
# 如果数据库不存在，会自动运行初始化

set -e

echo "=========================================="
echo "MediMeow 数据库重置"
echo "=========================================="
echo ""

# 数据库配置
DB_HOST=${DB_HOST:-127.0.0.1}
DB_PORT=${DB_PORT:-3306}
DB_NAME=${DB_NAME:-medimeow_db}
DB_USER=${DB_USER:-root}
DB_PASS=${DB_PASS:-12345}

echo "📋 数据库配置:"
echo "   Host: $DB_HOST:$DB_PORT"
echo "   Database: $DB_NAME"
echo "   User: $DB_USER"
echo ""

# 检查数据库是否存在，如果不存在则运行初始化
echo "🔍 检查数据库状态..."
if ! mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASS" -e "USE $DB_NAME; SELECT 1" &>/dev/null; then
    echo "⚠️  数据库不存在或无法访问，运行初始化脚本..."
    if [ -f "./init_db.sh" ]; then
        ./init_db.sh
        echo ""
        echo "🔄 继续数据库重置..."
    else
        echo "❌ 找不到 init_db.sh 脚本，请先运行初始化"
        exit 1
    fi
else
    echo "✅ 数据库连接成功"
fi
echo ""

# 删除并重建数据库
echo "🗑️  删除旧数据库..."
mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASS" -e "DROP DATABASE IF EXISTS $DB_NAME;" 2>/dev/null || true

echo "📦 重新创建数据库..."
mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASS" -e "CREATE DATABASE $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 运行数据库迁移
echo "📥 运行数据库迁移..."
cd "$(dirname "$0")"
alembic upgrade head

echo ""
echo "✅ 数据库重置完成！"
echo ""

# 如果 alembic 没有创建表，作为回退执行 init.sql（确保 init.sql 在同一目录）
echo "🔁 检查核心表是否存在（回退检查）..."
if ! mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASS" -e "USE $DB_NAME; SHOW TABLES LIKE 'departments'" | grep -q departments; then
    echo "⚠️  未检测到核心表，尝试执行 init.sql 来创建表结构..."
    if [ -f "./init.sql" ]; then
        mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASS" < ./init.sql
        echo "✅ init.sql 执行完成"
    else
        echo "❌ 找不到 init.sql，无法回退创建表。请手动运行 init.sql 或修复 Alembic 迁移。"
    fi
else
    echo "✅ 核心表已存在，无需回退。"
fi

# 显示统计信息
echo "📊 数据统计:"
mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASS" "$DB_NAME" -e "
SELECT 
    '科室' as '类型', COUNT(*) as '数量' FROM departments WHERE deleted_at IS NULL
UNION ALL
SELECT '用户', COUNT(*) FROM users WHERE deleted_at IS NULL
UNION ALL
SELECT '医生', COUNT(*) FROM doctors WHERE deleted_at IS NULL
UNION ALL
SELECT '问卷', COUNT(*) FROM questionnaires WHERE deleted_at IS NULL
UNION ALL
SELECT '提交记录', COUNT(*) FROM questionnaire_submissions WHERE deleted_at IS NULL
UNION ALL
SELECT '就诊记录', COUNT(*) FROM medical_records WHERE deleted_at IS NULL;
"

echo ""
echo "📝 测试账号:"
echo "   用户 - 凉柚: 13850136583 / ShenMiDaZhi"
echo "   用户 - 李明: 13900000002 / 12345678"
echo "   医生 - 张医生: 张医生 / doctor123"
echo ""
echo "🚀 现在可以启动后端服务了！"
