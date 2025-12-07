-- ============================================================
-- MediMeow Backend - 数据库初始化脚本
-- 数据库: MariaDB 10.5+ / MySQL 5.7+
-- 字符集: UTF-8 (utf8mb4)
-- ============================================================

-- 设置字符集和编码
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;
SET SQL_MODE = 'NO_AUTO_VALUE_ON_ZERO';
SET time_zone = '+08:00';

-- ============================================================
-- 1. 创建数据库
-- ============================================================

CREATE DATABASE IF NOT EXISTS medimeow_db 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

USE medimeow_db;

-- ============================================================
-- 2. 创建数据表
-- ============================================================

-- ------------------------------------------------------------
-- 2.1 科室表 (departments)
-- 存储医院科室信息
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `departments` (
    `id` VARCHAR(36) NOT NULL PRIMARY KEY COMMENT '科室ID (UUID)',
    `department_name` VARCHAR(100) NOT NULL UNIQUE COMMENT '科室名称',
    `description` TEXT COMMENT '科室描述',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `deleted_at` DATETIME DEFAULT NULL COMMENT '软删除时间',
    INDEX `idx_department_name` (`department_name`),
    INDEX `idx_deleted_at` (`deleted_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='科室表';

-- ------------------------------------------------------------
-- 2.2 用户表 (users)
-- 存储患者/用户信息
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `users` (
    `id` VARCHAR(36) NOT NULL PRIMARY KEY COMMENT '用户ID (UUID)',
    `phone_number` VARCHAR(20) NOT NULL UNIQUE COMMENT '手机号',
    `password` VARCHAR(255) NOT NULL COMMENT '密码 (bcrypt加密)',
    `username` VARCHAR(100) DEFAULT NULL COMMENT '用户姓名',
    `gender` VARCHAR(10) DEFAULT NULL COMMENT '性别',
    `birth` VARCHAR(20) DEFAULT NULL COMMENT '出生日期',
    `ethnicity` VARCHAR(50) DEFAULT NULL COMMENT '民族',
    `origin` VARCHAR(100) DEFAULT NULL COMMENT '籍贯',
    `avatar_url` VARCHAR(500) DEFAULT NULL COMMENT '头像URL',
    `email` VARCHAR(100) DEFAULT NULL COMMENT '邮箱',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `deleted_at` DATETIME DEFAULT NULL COMMENT '软删除时间',
    INDEX `idx_phone_number` (`phone_number`),
    INDEX `idx_deleted_at` (`deleted_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- ------------------------------------------------------------
-- 2.3 医生表 (doctors)
-- 存储医生信息
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `doctors` (
    `id` VARCHAR(36) NOT NULL PRIMARY KEY COMMENT '医生ID (UUID)',
    `username` VARCHAR(100) NOT NULL COMMENT '医生姓名',
    `password` VARCHAR(255) NOT NULL COMMENT '密码 (bcrypt加密)',
    `department_id` VARCHAR(36) NOT NULL COMMENT '所属科室ID',
    `title` VARCHAR(50) DEFAULT NULL COMMENT '职称 (主任医师/副主任医师/主治医师等)',
    `phone_number` VARCHAR(20) DEFAULT NULL COMMENT '联系电话',
    `email` VARCHAR(100) DEFAULT NULL COMMENT '邮箱',
    `avatar_url` VARCHAR(500) DEFAULT NULL COMMENT '头像URL',
    `description` TEXT COMMENT '医生简介',
    `status` VARCHAR(20) DEFAULT 'active' COMMENT '状态 (active/inactive/on_leave)',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `deleted_at` DATETIME DEFAULT NULL COMMENT '软删除时间',
    INDEX `idx_department_id` (`department_id`),
    INDEX `idx_status` (`status`),
    INDEX `idx_deleted_at` (`deleted_at`),
    CONSTRAINT `fk_doctors_department` FOREIGN KEY (`department_id`) 
        REFERENCES `departments` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='医生表';

-- ------------------------------------------------------------
-- 2.4 问卷表 (questionnaires)
-- 存储问卷模板
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `questionnaires` (
    `id` VARCHAR(36) NOT NULL PRIMARY KEY COMMENT '问卷ID (UUID)',
    `department_id` VARCHAR(36) NOT NULL COMMENT '所属科室ID',
    `title` VARCHAR(200) NOT NULL COMMENT '问卷标题',
    `description` TEXT COMMENT '问卷描述',
    `questions` JSON NOT NULL COMMENT '问题列表 (JSON格式)',
    `version` INT DEFAULT 1 COMMENT '问卷版本号',
    `status` VARCHAR(20) DEFAULT 'active' COMMENT '状态 (active/inactive/draft)',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `deleted_at` DATETIME DEFAULT NULL COMMENT '软删除时间',
    INDEX `idx_department_id` (`department_id`),
    INDEX `idx_status` (`status`),
    INDEX `idx_deleted_at` (`deleted_at`),
    CONSTRAINT `fk_questionnaires_department` FOREIGN KEY (`department_id`) 
        REFERENCES `departments` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='问卷模板表';

-- ------------------------------------------------------------
-- 2.5 上传文件表 (uploaded_files)
-- 存储用户上传的文件信息
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `uploaded_files` (
    `id` VARCHAR(36) NOT NULL PRIMARY KEY COMMENT '文件ID (UUID)',
    `filename` VARCHAR(255) NOT NULL COMMENT '原始文件名',
    `file_path` VARCHAR(500) NOT NULL COMMENT '文件存储路径',
    `file_size` BIGINT NOT NULL COMMENT '文件大小 (字节)',
    `content_type` VARCHAR(100) NOT NULL COMMENT 'MIME类型',
    `file_type` VARCHAR(50) DEFAULT NULL COMMENT '文件类型 (image/document/video等)',
    `uploaded_by` VARCHAR(36) DEFAULT NULL COMMENT '上传者ID',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
    `deleted_at` DATETIME DEFAULT NULL COMMENT '软删除时间',
    INDEX `idx_uploaded_by` (`uploaded_by`),
    INDEX `idx_file_type` (`file_type`),
    INDEX `idx_created_at` (`created_at`),
    INDEX `idx_deleted_at` (`deleted_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='上传文件表';

-- ------------------------------------------------------------
-- 2.6 问卷提交表 (questionnaire_submissions)
-- 存储用户提交的问卷答案
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `questionnaire_submissions` (
    `id` VARCHAR(36) NOT NULL PRIMARY KEY COMMENT '提交ID (UUID)',
    `user_id` VARCHAR(36) NOT NULL COMMENT '用户ID',
    `questionnaire_id` VARCHAR(36) NOT NULL COMMENT '问卷ID',
    `department_id` VARCHAR(36) NOT NULL COMMENT '科室ID',
    `answers` JSON NOT NULL COMMENT '答案数据 (JSON格式)',
    `file_ids` JSON DEFAULT NULL COMMENT '上传的文件ID列表',
    `height` INT DEFAULT NULL COMMENT '身高(cm)',
    `weight` INT DEFAULT NULL COMMENT '体重(kg)',
    `ai_result` JSON DEFAULT NULL COMMENT 'AI分析结果',
    `status` VARCHAR(20) DEFAULT 'pending' COMMENT '状态 (pending/processing/completed/draft)',
    `submit_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '提交时间',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `deleted_at` DATETIME DEFAULT NULL COMMENT '软删除时间',
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_questionnaire_id` (`questionnaire_id`),
    INDEX `idx_department_id` (`department_id`),
    INDEX `idx_status` (`status`),
    INDEX `idx_submit_time` (`submit_time`),
    INDEX `idx_deleted_at` (`deleted_at`),
    CONSTRAINT `fk_submissions_user` FOREIGN KEY (`user_id`) 
        REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `fk_submissions_questionnaire` FOREIGN KEY (`questionnaire_id`) 
        REFERENCES `questionnaires` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT `fk_submissions_department` FOREIGN KEY (`department_id`) 
        REFERENCES `departments` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='问卷提交表';

-- ------------------------------------------------------------
-- 2.7 就诊记录表 (medical_records)
-- 存储就诊记录和诊断信息
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `medical_records` (
    `id` VARCHAR(36) NOT NULL PRIMARY KEY COMMENT '就诊记录ID (UUID)',
    `user_id` VARCHAR(36) NOT NULL COMMENT '患者ID',
    `doctor_id` VARCHAR(36) DEFAULT NULL COMMENT '医生ID',
    `submission_id` VARCHAR(36) NOT NULL COMMENT '问卷提交ID',
    `department_id` VARCHAR(36) NOT NULL COMMENT '科室ID',
    `report` TEXT COMMENT '医生诊断报告',
    `diagnosis` VARCHAR(500) DEFAULT NULL COMMENT '诊断结果',
    `prescription` TEXT COMMENT '处方',
    `treatment_plan` TEXT COMMENT '治疗方案',
    `status` VARCHAR(20) DEFAULT 'waiting' COMMENT '状态 (waiting/in_progress/completed/cancelled)',
    `priority` VARCHAR(20) DEFAULT 'normal' COMMENT '优先级 (urgent/high/normal/low)',
    `queue_number` INT DEFAULT NULL COMMENT '排队号码',
    `appointment_time` DATETIME DEFAULT NULL COMMENT '预约时间',
    `consultation_time` DATETIME DEFAULT NULL COMMENT '就诊开始时间',
    `completion_time` DATETIME DEFAULT NULL COMMENT '就诊完成时间',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `deleted_at` DATETIME DEFAULT NULL COMMENT '软删除时间',
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_doctor_id` (`doctor_id`),
    INDEX `idx_submission_id` (`submission_id`),
    INDEX `idx_department_id` (`department_id`),
    INDEX `idx_status` (`status`),
    INDEX `idx_priority` (`priority`),
    INDEX `idx_appointment_time` (`appointment_time`),
    INDEX `idx_created_at` (`created_at`),
    INDEX `idx_deleted_at` (`deleted_at`),
    CONSTRAINT `fk_records_user` FOREIGN KEY (`user_id`) 
        REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `fk_records_doctor` FOREIGN KEY (`doctor_id`) 
        REFERENCES `doctors` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT `fk_records_submission` FOREIGN KEY (`submission_id`) 
        REFERENCES `questionnaire_submissions` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT `fk_records_department` FOREIGN KEY (`department_id`) 
        REFERENCES `departments` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='就诊记录表';

-- ------------------------------------------------------------
-- 2.8 系统日志表 (system_logs)
-- 存储系统操作日志
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `system_logs` (
    `id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY COMMENT '日志ID',
    `user_id` VARCHAR(36) DEFAULT NULL COMMENT '操作用户ID',
    `user_type` VARCHAR(20) DEFAULT NULL COMMENT '用户类型 (user/doctor/admin)',
    `action` VARCHAR(100) NOT NULL COMMENT '操作动作',
    `module` VARCHAR(50) NOT NULL COMMENT '模块名称',
    `ip_address` VARCHAR(50) DEFAULT NULL COMMENT 'IP地址',
    `user_agent` VARCHAR(500) DEFAULT NULL COMMENT '用户代理',
    `request_data` JSON DEFAULT NULL COMMENT '请求数据',
    `response_status` INT DEFAULT NULL COMMENT '响应状态码',
    `error_message` TEXT COMMENT '错误信息',
    `execution_time` INT DEFAULT NULL COMMENT '执行时间(毫秒)',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_user_type` (`user_type`),
    INDEX `idx_action` (`action`),
    INDEX `idx_module` (`module`),
    INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统日志表';

-- ============================================================
-- 3. 插入初始数据
-- ============================================================
-- 注意: 初始数据通过 init_db.sh 脚本自动导入
-- 顺序: 科室 → 医生 → 问卷

-- ============================================================
-- 4. 数据库配置优化
-- ============================================================

-- 恢复外键检查
SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
-- 初始化完成
-- ============================================================

-- 显示表信息
SELECT 
    TABLE_NAME AS '表名',
    TABLE_COMMENT AS '说明',
    TABLE_ROWS AS '预估行数',
    ROUND((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024, 2) AS '大小(MB)'
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'medimeow_db'
  AND TABLE_TYPE = 'BASE TABLE'
ORDER BY TABLE_NAME;
