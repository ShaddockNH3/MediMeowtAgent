-- 插入儿科示例问卷 (包含所有支持的问题类型：单选、多选、评分、文本、文件上传)
-- 该脚本会自动查找名称为 '儿科' 的科室并插入问卷

SET @dept_id = (SELECT id FROM departments WHERE department_name = '儿科' LIMIT 1);

INSERT INTO `questionnaires` (
    `id`, 
    `department_id`, 
    `title`, 
    `description`, 
    `questions`, 
    `version`, 
    `status`
) 
VALUES (
    UUID(), 
    @dept_id, 
    '儿科综合分诊问卷', 
    '包含单选、多选、评分、文本及图片上传功能的完整示例问卷', 
    '[
        {
            "id": "q1_fever",
            "type": "single",
            "question": "1. 孩子的发热情况如何？(单选)",
            "options": ["无发热", "低热 (37.3℃-38.0℃)", "中度发热 (38.1℃-39.0℃)", "高热 (>39.0℃)"],
            "required": true
        },
        {
            "id": "q2_symptoms",
            "type": "multi",
            "question": "2. 孩子伴随哪些症状？(多选)",
            "options": ["咳嗽", "流涕", "喉咙痛", "呕吐", "腹泻", "皮疹", "精神萎靡"],
            "required": false
        },
        {
            "id": "q3_status_score",
            "type": "scale",
            "question": "3. 请给孩子的精神状态打分 (1-10分，10分为状态最好)",
            "scale": {"min": 1, "max": 10},
            "required": true
        },
        {
            "id": "q4_description",
            "type": "text",
            "question": "4. 请详细描述病情经过及用药情况",
            "placeholder": "例如：发病时间、用过什么药、效果如何...",
            "required": true
        },
        {
            "id": "q5_images",
            "type": "file",
            "question": "5. 上传患处照片或相关检查报告",
            "max_files": 3,
            "required": false
        }
    ]', 
    1, 
    'active'
);

SELECT CONCAT('成功插入儿科问卷，科室ID: ', @dept_id) AS Result;
