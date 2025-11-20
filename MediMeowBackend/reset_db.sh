#!/bin/bash

# MediMeow 数据库重置脚本
# 用于开发和测试环境快速重置数据库

set -e

echo "=========================================="
echo "MediMeow 数据库重置"
echo "=========================================="
echo ""

# 数据库配置
DB_HOST=${DB_HOST:-127.0.0.1}
DB_PORT=${DB_PORT:-3306}
DB_NAME=${DB_NAME:-medimoew_db}
DB_USER=${DB_USER:-root}
DB_PASS=${DB_PASS:-123456}

echo "📋 数据库配置:"
echo "   Host: $DB_HOST:$DB_PORT"
echo "   Database: $DB_NAME"
echo "   User: $DB_USER"
echo ""

# 检查 MySQL 是否可访问
echo "🔍 检查数据库连接..."
if ! mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASS" -e "SELECT 1" &>/dev/null; then
    echo "❌ 无法连接到数据库，请检查配置"
    exit 1
fi
echo "✅ 数据库连接成功"
echo ""

# 删除并重建数据库
echo "🗑️  删除旧数据库..."
mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASS" -e "DROP DATABASE IF EXISTS $DB_NAME;" 2>/dev/null || true

echo "📦 重新创建数据库..."
mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASS" -e "CREATE DATABASE $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 导入初始化脚本
echo "📥 导入初始化数据..."
mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASS" "$DB_NAME" < init.sql

echo ""
echo "✅ 数据库重置完成！"
echo ""

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
