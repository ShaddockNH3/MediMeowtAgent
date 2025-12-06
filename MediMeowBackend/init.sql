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

-- ------------------------------------------------------------
-- 3.1 插入默认科室（只包含 questionnaire 文件夹中存在的科室）
-- ------------------------------------------------------------
INSERT INTO `departments` (`id`, `department_name`, `description`) VALUES
(UUID(), '儿科', '诊治儿童疾病，包括儿童常见病、多发病'),
(UUID(), '内分泌科', '诊治内分泌系统疾病，如糖尿病、甲状腺疾病等'),
(UUID(), '口腔科', '诊治口腔、牙齿相关疾病'),
(UUID(), '呼吸内科', '诊治呼吸系统疾病，如肺炎、哮喘、慢阻肺等'),
(UUID(), '妇科', '诊治女性生殖系统疾病'),
(UUID(), '心内科', '诊治心血管系统疾病'),
(UUID(), '泌尿外科', '诊治泌尿系统疾病'),
(UUID(), '消化内科', '诊治消化系统疾病，如胃炎、肠炎等'),
(UUID(), '皮肤科', '诊治皮肤疾病'),
(UUID(), '眼科', '诊治眼部疾病和视力问题'),
(UUID(), '神经内科', '诊治神经系统疾病'),
(UUID(), '耳鼻喉科', '诊治耳、鼻、喉部疾病'),
(UUID(), '肿瘤科', '诊治各类肿瘤疾病'),
(UUID(), '血液科', '诊治血液系统疾病'),
(UUID(), '骨科', '诊治骨骼、关节、肌肉疾病');

-- ------------------------------------------------------------
-- 3.2 创建测试用户 (生产环境请删除)
-- ------------------------------------------------------------
-- 密码: 凉柚使用ShenMiDaZhi，其1145144他用户使用12345678 (bcrypt加密后，10轮hash)
-- INSERT INTO `users` (`id`, `phone_number`, `password`, `username`, `gender`, `birth`) VALUES
-- ('2c6c341e-0c19-4e50-a3b5-7d15cbc98a24', '13850136583', '$2b$12$Fq8MfuJJ8zO8sOvb8wzwgOsotprv2oNT.2kuUJYnaOoYbD8jzuGJi', '凉柚', '男', '1995-05-20'),
-- (UUID(), '13900000002', '$2b$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', '李明', '女', '1988-08-15'),
-- (UUID(), '13900000003', '$2b$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', '王芳', '女', '1992-12-10'),
-- (UUID(), '13900000004', '$2b$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', '赵强', '男', '1985-03-25');

-- ------------------------------------------------------------  
-- 3.3 创建测试医生 (生产环境请删除)
-- ------------------------------------------------------------  
-- 密码: doctor123 (bcrypt加密后，12轮hash)
INSERT INTO `doctors` (`id`, `username`, `password`, `department_id`, `title`, `phone_number`) VALUES
('d1111111-1111-1111-1111-111111111111', '张医生', '$2b$12$DzYC0G6Ab/O4Ors8KIj79uIR825rDYAMfhSMuFXNKS1pM87HTWT56', 
 (SELECT id FROM departments WHERE department_name='心内科' LIMIT 1), '主任医师', '13800001001'),
('d2222222-2222-2222-2222-222222222222', '李医生', '$2b$12$DzYC0G6Ab/O4Ors8KIj79uIR825rDYAMfhSMuFXNKS1pM87HTWT56', 
 (SELECT id FROM departments WHERE department_name='儿科' LIMIT 1), '副主任医师', '13800001002'),
('d3333333-3333-3333-3333-333333333333', '王医生', '$2b$12$DzYC0G6Ab/O4Ors8KIj79uIR825rDYAMfhSMuFXNKS1pM87HTWT56', 
 (SELECT id FROM departments WHERE department_name='皮肤科' LIMIT 1), '主治医师', '13800001003'),
('d4444444-4444-4444-4444-444444444444', '赵医生', '$2b$12$DzYC0G6Ab/O4Ors8KIj79uIR825rDYAMfhSMuFXNKS1pM87HTWT56', 
 (SELECT id FROM departments WHERE department_name='耳鼻喉科' LIMIT 1), '主治医师', '13800001004');-- ------------------------------------------------------------
-- 3.4 插入问卷示例数据（已由 import_questionnaires_from_md.py 脚本导入）
-- 注意：生产环境使用导入脚本而非此处的硬编码示例
-- 以下示例数据已注释，实际问卷由 docs/questionnaire/ 文件夹导入
-- ------------------------------------------------------------
-- INSERT INTO `questionnaires` (`id`, `department_id`, `title`, `description`, `questions`, `version`, `status`) VALUES
-- (UUID(), (SELECT id FROM departments WHERE department_name='心内科' LIMIT 1),
--  '心内科初诊分诊问卷',
--  '用于门诊心内科患者的初步症状评估与分诊',
--  '[{"id":"q1","type":"single","question":"您当前主要不适是什么？","options":["胸痛","心慌","气短","其他"]},
--      {"id":"q2","type":"multi","question":"是否有以下症状？","options":["乏力","头晕","恶心","呕吐"]},
--      {"id":"q3","type":"text","question":"其他补充说明（可选）"}]',
--  1, 'active'),
-- (UUID(), (SELECT id FROM departments WHERE department_name='儿科' LIMIT 1),
--  '儿童发热评估问卷',
--  '用于评估儿童发热时的症状、持续时间与严重程度',
--  '[{"id":"q1","type":"single","question":"孩子是否发热？","options":["是","否"]},
--      {"id":"q2","type":"single","question":"发热持续多久？","options":["<24小时","24-48小时",">48小时"]},
--      {"id":"q3","type":"single","question":"是否伴有抽搐？","options":["是","否"]},
--      {"id":"q4","type":"text","question":"其他症状或家长补充（可选）"}]',
--  1, 'active'),
-- (UUID(), (SELECT id FROM departments WHERE department_name='皮肤科' LIMIT 1),
--  '皮肤疹/瘙痒问卷',
--  '用于记录皮疹位置、持续时间与是否伴随其他系统症状',
--  '[{"id":"q1","type":"single","question":"皮疹开始于何时？","options":["<24小时","1-3天",">3天"]},
--      {"id":"q2","type":"multi","question":"皮疹分布在哪些部位？","options":["面部","躯干","四肢","粘膜"]},
--      {"id":"q3","type":"single","question":"是否伴随瘙痒？","options":["严重","轻微","无"]},
--      {"id":"q4","type":"text","question":"已采取的处理措施（可选）"}]',
--  1, 'active'),
-- (UUID(), (SELECT id FROM departments WHERE department_name='耳鼻喉科' LIMIT 1),
--  '耳鼻喉常见症状问卷',
--  '评估咽喉、鼻塞、眩晕等常见耳鼻喉症状',
--  '[{"id":"q1","type":"single","question":"主要症状是什么？","options":["咽痛","鼻塞/流涕","耳痛/耳鸣","眩晕","其他"]},
--      {"id":"q2","type":"single","question":"症状持续时间？","options":["<7天","7-14天",">14天"]},
--      {"id":"q3","type":"scale","question":"症状对生活影响程度（1-5，5 最严重）","scale":{"min":1,"max":5}},
--      {"id":"q4","type":"text","question":"既往相关病史（可选）"}]',
--  1, 'active');

-- ------------------------------------------------------------
-- 3.5 插入测试问卷提交记录 (生产环境请删除)
-- 注意：由于测试科室已更改为心内科，以下测试数据需对应调整
-- 建议使用实际导入的问卷进行测试
-- ------------------------------------------------------------
-- 准备变量
-- SET @user_liangyou = '2c6c341e-0c19-4e50-a3b5-7d15cbc98a24';
-- SET @q_cardiology = (SELECT id FROM questionnaires WHERE department_id=(SELECT id FROM departments WHERE department_name='心内科' LIMIT 1) LIMIT 1);
-- SET @dept_cardiology = (SELECT id FROM departments WHERE department_name='心内科' LIMIT 1);

-- -- 用户"凉柚"提交的心内科问卷 (10条测试数据)
-- SET @sub_id_1 = UUID();
-- INSERT INTO `questionnaire_submissions` (`id`, `user_id`, `questionnaire_id`, `department_id`, `answers`, `status`, `ai_result`, `submit_time`) VALUES
-- (@sub_id_1, @user_liangyou, @q_cardiology, @dept_cardiology, '{"q1":"胸痛","q2":["乏力"],"q3":"测试数据1"}', 'completed', '{"suggestion":"建议心内科就诊"}', DATE_SUB(NOW(), INTERVAL 10 MINUTE));

-- SET @sub_id_2 = UUID();
-- INSERT INTO `questionnaire_submissions` (`id`, `user_id`, `questionnaire_id`, `department_id`, `answers`, `status`, `ai_result`, `submit_time`) VALUES
-- (@sub_id_2, @user_liangyou, @q_cardiology, @dept_cardiology, '{"q1":"心慌","q2":["头晕"],"q3":"测试数据2"}', 'completed', '{"suggestion":"建议心内科就诊"}', DATE_SUB(NOW(), INTERVAL 9 MINUTE));

-- SET @sub_id_3 = UUID();
-- INSERT INTO `questionnaire_submissions` (`id`, `user_id`, `questionnaire_id`, `department_id`, `answers`, `status`, `ai_result`, `submit_time`) VALUES
-- (@sub_id_3, @user_liangyou, @q_cardiology, @dept_cardiology, '{"q1":"气短","q2":["胸闷"],"q3":"测试数据3"}', 'completed', '{"suggestion":"建议心内科就诊"}', DATE_SUB(NOW(), INTERVAL 8 MINUTE));

-- SET @sub_id_4 = UUID();
-- INSERT INTO `questionnaire_submissions` (`id`, `user_id`, `questionnaire_id`, `department_id`, `answers`, `status`, `ai_result`, `submit_time`) VALUES
-- (@sub_id_4, @user_liangyou, @q_cardiology, @dept_cardiology, '{"q1":"胸痛","q2":["心慌"],"q3":"测试数据4"}', 'completed', '{"suggestion":"建议心内科就诊"}', DATE_SUB(NOW(), INTERVAL 7 MINUTE));

-- SET @sub_id_5 = UUID();
-- INSERT INTO `questionnaire_submissions` (`id`, `user_id`, `questionnaire_id`, `department_id`, `answers`, `status`, `ai_result`, `submit_time`) VALUES
-- (@sub_id_5, @user_liangyou, @q_cardiology, @dept_cardiology, '{"q1":"心悸","q2":["乏力"],"q3":"测试数据5"}', 'completed', '{"suggestion":"建议心内科就诊"}', DATE_SUB(NOW(), INTERVAL 6 MINUTE));

-- SET @sub_id_6 = UUID();
-- INSERT INTO `questionnaire_submissions` (`id`, `user_id`, `questionnaire_id`, `department_id`, `answers`, `status`, `ai_result`, `submit_time`) VALUES
-- (@sub_id_6, @user_liangyou, @q_cardiology, @dept_cardiology, '{"q1":"胸闷","q2":["头晕"],"q3":"测试数据6"}', 'completed', '{"suggestion":"建议心内科就诊"}', DATE_SUB(NOW(), INTERVAL 5 MINUTE));

-- SET @sub_id_7 = UUID();
-- INSERT INTO `questionnaire_submissions` (`id`, `user_id`, `questionnaire_id`, `department_id`, `answers`, `status`, `ai_result`, `submit_time`) VALUES
-- (@sub_id_7, @user_liangyou, @q_cardiology, @dept_cardiology, '{"q1":"心律不齐","q2":["胸痛"],"q3":"测试数据7"}', 'completed', '{"suggestion":"建议心内科就诊"}', DATE_SUB(NOW(), INTERVAL 4 MINUTE));

-- SET @sub_id_8 = UUID();
-- INSERT INTO `questionnaire_submissions` (`id`, `user_id`, `questionnaire_id`, `department_id`, `answers`, `status`, `ai_result`, `submit_time`) VALUES
-- (@sub_id_8, @user_liangyou, @q_cardiology, @dept_cardiology, '{"q1":"呼吸困难","q2":["气短"],"q3":"测试数据8"}', 'completed', '{"suggestion":"建议心内科就诊"}', DATE_SUB(NOW(), INTERVAL 3 MINUTE));

-- SET @sub_id_9 = UUID();
-- INSERT INTO `questionnaire_submissions` (`id`, `user_id`, `questionnaire_id`, `department_id`, `answers`, `status`, `ai_result`, `submit_time`) VALUES
-- (@sub_id_9, @user_liangyou, @q_cardiology, @dept_cardiology, '{"q1":"胸痛","q2":["恶心"],"q3":"测试数据9"}', 'completed', '{"suggestion":"建议心内科就诊"}', DATE_SUB(NOW(), INTERVAL 2 MINUTE));

-- SET @sub_id_10 = UUID();
-- INSERT INTO `questionnaire_submissions` (`id`, `user_id`, `questionnaire_id`, `department_id`, `answers`, `status`, `ai_result`, `submit_time`) VALUES
-- (@sub_id_10, @user_liangyou, @q_cardiology, @dept_cardiology, '{"q1":"体检","q2":["无症状"],"q3":"测试数据10"}', 'completed', '{"suggestion":"建议心内科就诊"}', DATE_SUB(NOW(), INTERVAL 1 MINUTE));

-- -- 用户"李明"提交的儿科问卷  
-- INSERT INTO `questionnaire_submissions` 
-- (`id`, `user_id`, `questionnaire_id`, `department_id`, `answers`, `status`, `ai_result`) VALUES
-- (UUID(),
--  (SELECT id FROM users WHERE phone_number='13900000002' LIMIT 1),
--  (SELECT id FROM questionnaires WHERE title='儿童发热评估问卷' LIMIT 1),
--  (SELECT id FROM departments WHERE department_name='儿科' LIMIT 1),
--  '{"q1":"是","q2":"24-48小时","q3":"否","q4":"孩子38.5度发热，精神状态良好"}',
--  'completed',
--  '{"is_department":true,"key_info":{"发热":"是","持续时间":"24-48小时","抽搐":"否"},"suggestion":"建议儿科门诊就诊，注意观察体温变化"}');

-- -- 用户"王芳"提交的皮肤科问卷
-- INSERT INTO `questionnaire_submissions` 
-- (`id`, `user_id`, `questionnaire_id`, `department_id`, `answers`, `status`) VALUES
-- (UUID(),
--  (SELECT id FROM users WHERE phone_number='13900000003' LIMIT 1),
--  (SELECT id FROM questionnaires WHERE title='皮肤疹/瘙痒问卷' LIMIT 1),
--  (SELECT id FROM departments WHERE department_name='皮肤科' LIMIT 1),
--  '{"q1":"1-3天","q2":["面部","四肢"],"q3":"严重","q4":"已使用抗过敏药"}',
--  'pending');

-- ------------------------------------------------------------
-- 3.6 插入测试就诊记录 (生产环境请删除)
-- 注意：测试科室已更改为心内科，对应调整就诊记录
-- ------------------------------------------------------------
-- 为问卷提交创建对应的就诊记录
-- SET @doctor_zhang = 'd1111111-1111-1111-1111-111111111111';

-- -- 凉柚的10条就诊记录
-- INSERT INTO `medical_records` (`id`, `user_id`, `doctor_id`, `submission_id`, `department_id`, `status`, `priority`, `created_at`) VALUES
-- (UUID(), @user_liangyou, @doctor_zhang, @sub_id_1, @dept_cardiology, 'waiting', 'normal', DATE_SUB(NOW(), INTERVAL 10 MINUTE)),
-- (UUID(), @user_liangyou, @doctor_zhang, @sub_id_2, @dept_cardiology, 'waiting', 'normal', DATE_SUB(NOW(), INTERVAL 9 MINUTE)),
-- (UUID(), @user_liangyou, @doctor_zhang, @sub_id_3, @dept_cardiology, 'waiting', 'normal', DATE_SUB(NOW(), INTERVAL 8 MINUTE)),
-- (UUID(), @user_liangyou, @doctor_zhang, @sub_id_4, @dept_cardiology, 'waiting', 'normal', DATE_SUB(NOW(), INTERVAL 7 MINUTE)),
-- (UUID(), @user_liangyou, @doctor_zhang, @sub_id_5, @dept_cardiology, 'waiting', 'normal', DATE_SUB(NOW(), INTERVAL 6 MINUTE)),
-- (UUID(), @user_liangyou, @doctor_zhang, @sub_id_6, @dept_cardiology, 'waiting', 'normal', DATE_SUB(NOW(), INTERVAL 5 MINUTE)),
-- (UUID(), @user_liangyou, @doctor_zhang, @sub_id_7, @dept_cardiology, 'waiting', 'normal', DATE_SUB(NOW(), INTERVAL 4 MINUTE)),
-- (UUID(), @user_liangyou, @doctor_zhang, @sub_id_8, @dept_cardiology, 'waiting', 'normal', DATE_SUB(NOW(), INTERVAL 3 MINUTE)),
-- (UUID(), @user_liangyou, @doctor_zhang, @sub_id_9, @dept_cardiology, 'waiting', 'normal', DATE_SUB(NOW(), INTERVAL 2 MINUTE)),
-- (UUID(), @user_liangyou, @doctor_zhang, @sub_id_10, @dept_cardiology, 'waiting', 'normal', DATE_SUB(NOW(), INTERVAL 1 MINUTE));

-- INSERT INTO `medical_records` 
-- (`id`, `user_id`, `submission_id`, `department_id`, `status`, `priority`) VALUES
-- (UUID(),
--  (SELECT id FROM users WHERE phone_number='13900000002' LIMIT 1),
--  (SELECT qs.id FROM questionnaire_submissions qs 
--   JOIN users u ON qs.user_id = u.id 
--   WHERE u.phone_number='13900000002' LIMIT 1),
--  (SELECT id FROM departments WHERE department_name='儿科' LIMIT 1),
--  'waiting',
--  'high');

-- INSERT INTO `medical_records` 
-- (`id`, `user_id`, `submission_id`, `department_id`, `status`, `priority`) VALUES
-- (UUID(),
--  (SELECT id FROM users WHERE phone_number='13900000003' LIMIT 1),
--  (SELECT qs.id FROM questionnaire_submissions qs 
--   JOIN users u ON qs.user_id = u.id 
--   WHERE u.phone_number='13900000003' LIMIT 1),
--  (SELECT id FROM departments WHERE department_name='皮肤科' LIMIT 1),
--  'waiting',
--  'normal');

--  (SELECT id FROM departments WHERE department_name='心内科' LIMIT 1), '主治医师');

-- ============================================================
-- 4. 创建视图 (可选)
-- ============================================================

-- ------------------------------------------------------------
-- 4.1 医生工作台视图
-- 显示医生的待诊患者信息
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW `v_doctor_queue` AS
SELECT 
    mr.id AS record_id,
    mr.queue_number,
    mr.status,
    mr.priority,
    mr.created_at AS register_time,
    u.id AS user_id,
    u.username AS patient_name,
    u.phone_number AS patient_phone,
    u.gender,
    u.birth,
    d.id AS doctor_id,
    d.username AS doctor_name,
    dept.department_name,
    qs.ai_result
FROM medical_records mr
JOIN users u ON mr.user_id = u.id
LEFT JOIN doctors d ON mr.doctor_id = d.id
JOIN departments dept ON mr.department_id = dept.id
JOIN questionnaire_submissions qs ON mr.submission_id = qs.id
WHERE mr.deleted_at IS NULL 
  AND u.deleted_at IS NULL
  AND (d.deleted_at IS NULL OR d.id IS NULL)
  AND dept.deleted_at IS NULL;

-- ------------------------------------------------------------
-- 4.2 患者就诊历史视图
-- 显示患者的就诊历史记录
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW `v_patient_history` AS
SELECT 
    mr.id AS record_id,
    mr.user_id,
    mr.status,
    mr.diagnosis,
    mr.created_at AS visit_date,
    mr.completion_time,
    d.username AS doctor_name,
    d.title AS doctor_title,
    dept.department_name,
    qs.submit_time,
    qs.status AS submission_status
FROM medical_records mr
LEFT JOIN doctors d ON mr.doctor_id = d.id
JOIN departments dept ON mr.department_id = dept.id
JOIN questionnaire_submissions qs ON mr.submission_id = qs.id
WHERE mr.deleted_at IS NULL 
  AND (d.deleted_at IS NULL OR d.id IS NULL)
  AND dept.deleted_at IS NULL;

-- ============================================================
-- 5. 创建存储过程 (可选)
-- ============================================================

-- ------------------------------------------------------------
-- 5.1 自动分配队列号码
-- ------------------------------------------------------------
DELIMITER $$

CREATE PROCEDURE `sp_assign_queue_number`(
    IN p_record_id VARCHAR(36),
    IN p_department_id VARCHAR(36)
)
BEGIN
    DECLARE v_queue_number INT;
    
    -- 获取当天该科室的最大队列号
    SELECT COALESCE(MAX(queue_number), 0) + 1 
    INTO v_queue_number
    FROM medical_records
    WHERE department_id = p_department_id
      AND DATE(created_at) = CURDATE()
      AND deleted_at IS NULL;
    
    -- 更新记录的队列号
    UPDATE medical_records
    SET queue_number = v_queue_number
    WHERE id = p_record_id;
END$$

DELIMITER ;

-- ============================================================
-- 6. 创建触发器 (可选)
-- ============================================================

-- ------------------------------------------------------------
-- 6.1 就诊记录创建时自动分配队列号
-- 修改为 BEFORE INSERT 以避免更新同表的错误
-- ------------------------------------------------------------
DELIMITER $$

CREATE TRIGGER `trg_medical_record_queue`
BEFORE INSERT ON `medical_records`
FOR EACH ROW
BEGIN
    DECLARE v_queue_number INT;
    
    -- 如果 queue_number 为 NULL，自动分配
    IF NEW.queue_number IS NULL THEN
        -- 获取当天该科室的最大队列号
        SELECT COALESCE(MAX(queue_number), 0) + 1 
        INTO v_queue_number
        FROM medical_records
        WHERE department_id = NEW.department_id
          AND DATE(created_at) = CURDATE()
          AND deleted_at IS NULL;
        
        -- 设置新记录的队列号
        SET NEW.queue_number = v_queue_number;
    END IF;
END$$

DELIMITER ;

-- ============================================================
-- 7. 数据库配置优化建议
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
