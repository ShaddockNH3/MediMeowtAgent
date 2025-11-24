#!/bin/bash

# MediMeow 数据库查看脚本
# 快速查看数据库中的数据

DB_HOST=${DB_HOST:-127.0.0.1}
DB_PORT=${DB_PORT:-3306}
DB_NAME=${DB_NAME:-medimeow_db}
DB_USER=${DB_USER:-root}
DB_PASS=${DB_PASS:-123456}

echo "=========================================="
echo "数据库数据查看"
echo "=========================================="
echo ""

echo "【1. 科室列表】"
mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASS" "$DB_NAME" -e "
SELECT 
    SUBSTRING(id, 1, 8) as 'ID前缀',
    department_name as '科室名称',
    description as '描述'
FROM departments 
WHERE deleted_at IS NULL 
ORDER BY created_at;
"

echo ""
echo "【2. 用户列表】"
mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASS" "$DB_NAME" -e "
SELECT 
    SUBSTRING(id, 1, 8) as 'ID前缀',
    phone_number as '手机号',
    username as '姓名',
    gender as '性别',
    birth as '出生日期'
FROM users 
WHERE deleted_at IS NULL 
ORDER BY created_at;
"

echo ""
echo "【3. 医生列表】"
mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASS" "$DB_NAME" -e "
SELECT 
    SUBSTRING(d.id, 1, 8) as 'ID前缀',
    d.username as '医生姓名',
    dept.department_name as '科室',
    d.title as '职称',
    d.phone_number as '电话'
FROM doctors d
LEFT JOIN departments dept ON d.department_id = dept.id
WHERE d.deleted_at IS NULL 
ORDER BY d.created_at;
"

echo ""
echo "【4. 问卷列表】"
mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASS" "$DB_NAME" -e "
SELECT 
    SUBSTRING(q.id, 1, 8) as 'ID前缀',
    q.title as '问卷标题',
    dept.department_name as '科室',
    q.version as '版本',
    q.status as '状态',
    JSON_LENGTH(q.questions) as '题目数'
FROM questionnaires q
LEFT JOIN departments dept ON q.department_id = dept.id
WHERE q.deleted_at IS NULL 
ORDER BY dept.department_name, q.version;
"

echo ""
echo "【5. 问卷提交记录】"
mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASS" "$DB_NAME" -e "
SELECT 
    SUBSTRING(qs.id, 1, 8) as 'ID前缀',
    u.username as '用户',
    q.title as '问卷标题',
    dept.department_name as '科室',
    qs.status as '状态',
    DATE_FORMAT(qs.submit_time, '%Y-%m-%d %H:%i') as '提交时间'
FROM questionnaire_submissions qs
LEFT JOIN users u ON qs.user_id = u.id
LEFT JOIN questionnaires q ON qs.questionnaire_id = q.id
LEFT JOIN departments dept ON qs.department_id = dept.id
WHERE qs.deleted_at IS NULL 
ORDER BY qs.submit_time DESC 
LIMIT 10;
"

echo ""
echo "【6. 就诊记录】"
mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASS" "$DB_NAME" -e "
SELECT 
    SUBSTRING(mr.id, 1, 8) as 'ID前缀',
    u.username as '患者',
    COALESCE(d.username, '未分配') as '医生',
    dept.department_name as '科室',
    mr.status as '状态',
    mr.priority as '优先级',
    mr.queue_number as '排队号',
    DATE_FORMAT(mr.created_at, '%Y-%m-%d %H:%i') as '创建时间'
FROM medical_records mr
LEFT JOIN users u ON mr.user_id = u.id
LEFT JOIN doctors d ON mr.doctor_id = d.id
LEFT JOIN departments dept ON mr.department_id = dept.id
WHERE mr.deleted_at IS NULL 
ORDER BY mr.created_at DESC 
LIMIT 10;
"

echo ""
echo "=========================================="
