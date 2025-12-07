-- ============================================================
-- MediMeow Backend - 视图、存储过程和触发器初始化脚本
-- 注意: 此脚本应在数据导入完成后执行
-- ============================================================

USE miaomiao;

-- ============================================================
-- 1. 创建视图
-- ============================================================

-- ------------------------------------------------------------
-- 1.1 医生工作台视图
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
-- 1.2 患者就诊历史视图
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
-- 2. 创建存储过程
-- ============================================================

-- ------------------------------------------------------------
-- 2.1 自动分配队列号码
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
-- 3. 创建触发器
-- ============================================================

-- ------------------------------------------------------------
-- 3.1 就诊记录创建时自动分配队列号
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
-- 初始化完成
-- ============================================================
SELECT '视图、存储过程和触发器创建完成' AS status;
