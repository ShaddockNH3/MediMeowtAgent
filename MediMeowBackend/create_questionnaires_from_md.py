#!/usr/bin/env python3
"""
从 Markdown 文件导入问卷到数据库
为每个科室创建问卷，并自动添加上传图片选项
"""
import sys
import os
import re
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.database import SessionLocal
from app.models.questionnaire import Questionnaire
from app.models.department import Department
from sqlalchemy import text
import uuid


def parse_markdown_questionnaire(md_content: str, department_name: str) -> dict:
    """解析 Markdown 格式的问卷"""
    
    # 提取所有问题
    questions = []
    
    # 匹配问题模式：C --> F1[问题1: 请选择您的耳部症状]
    question_pattern = r'C --> (\w+)\[问题\d+: (.+?)\]'
    question_matches = re.findall(question_pattern, md_content)
    
    for q_id, q_text in question_matches:
        question_obj = {
            "id": q_id.lower(),
            "type": "single",  # 默认单选
            "question": q_text.strip(),
            "required": True,
            "options": []
        }
        
        # 查找该问题的选项
        # 匹配选项模式：F1 --> F1a[A. 耳痛+发热+听力下降]
        option_pattern = rf'{q_id} --> {q_id}[a-z]\[([A-Z]\. .+?)\]'
        option_matches = re.findall(option_pattern, md_content)
        
        for option in option_matches:
            question_obj["options"].append(option.strip())
        
        if question_obj["options"]:
            questions.append(question_obj)
    
    # 根据科室类型添加对应的图片上传说明
    image_descriptions = {
        "儿科": "舌苔照片、皮疹照片、咽喉照片等",
        "耳鼻喉科": "咽喉照片、舌苔照片、耳部照片等",
        "皮肤科": "患处皮肤照片、皮疹照片等",
        "眼科": "眼部照片、视力检查报告等",
        "口腔科": "口腔照片、牙齿照片、X光片等",
        "骨科": "患处照片、X光片、CT报告等",
        "呼吸内科": "舌苔照片、胸片、CT报告等",
        "消化内科": "舌苔照片、B超报告、胃镜照片等",
        "心内科": "心电图、检查报告等",
        "神经内科": "检查报告、影像资料等",
        "内分泌科": "检查报告、B超照片等",
        "泌尿外科": "B超报告、检查报告等",
        "妇科": "B超报告、检查报告等",
        "血液科": "检查报告、化验单等",
        "肿瘤科": "检查报告、影像资料等"
    }
    
    # 添加既往病史输入框（倒数第二个问题）
    questions.append({
        "id": "medical_history",
        "type": "textarea",
        "question": "既往病史（选填）",
        "required": False,
        "placeholder": "请描述您的既往病史，如慢性病、手术史、过敏史等",
        "description": "如有高血压、糖尿病、心脏病等慢性病史，或曾经的手术史、药物过敏史等，请详细描述"
    })
    
    # 添加上传图片选项（作为最后一个问题）
    image_desc = image_descriptions.get(department_name, "相关检查照片、报告等")
    questions.append({
        "id": "upload_image",
        "type": "file",
        "question": f"请上传相关图片（选填）",
        "required": False,
        "accept": "image/*",
        "description": f"可上传{image_desc}，支持 JPG、PNG 格式，最大 10MB"
    })
    
    return {
        "title": f"{department_name}分诊问卷",
        "description": f"针对{department_name}患者的症状评估问卷",
        "questions": questions
    }


def import_questionnaires():
    """导入所有科室的问卷"""
    db = SessionLocal()
    
    try:
        # 问卷文件夹路径（项目根目录的上一级）
        questionnaire_dir = project_root.parent / "docs" / "questionnaire"
        
        if not questionnaire_dir.exists():
            print(f"❌ 问卷文件夹不存在: {questionnaire_dir}")
            return
        
        # 获取所有 Markdown 文件
        md_files = list(questionnaire_dir.glob("*.md"))
        
        print(f"📋 找到 {len(md_files)} 个问卷文件")
        print("="*60)
        
        # 第一步：删除所有现有问卷及相关数据（按照外键依赖顺序）
        print("\n🗑️  删除所有现有问卷及相关数据...")
        
        # 1. 先删除就诊记录（依赖 submission_id）
        from app.models.medical_record import MedicalRecord
        records_deleted = db.query(MedicalRecord).delete()
        print(f"   已删除 {records_deleted} 个就诊记录")
        
        # 2. 再删除问卷提交记录（依赖 questionnaire_id）
        from app.models.questionnaire import QuestionnaireSubmission
        submissions_deleted = db.query(QuestionnaireSubmission).delete()
        print(f"   已删除 {submissions_deleted} 个问卷提交记录")
        
        # 3. 最后删除问卷
        questionnaires_deleted = db.query(Questionnaire).delete()
        print(f"   已删除 {questionnaires_deleted} 个问卷")
        
        db.commit()
        
        print("\n" + "="*60)
        
        success_count = 0
        skip_count = 0
        error_count = 0
        
        for md_file in md_files:
            if md_file.name == "git.keep":
                continue
            
            # 从文件名提取科室名称
            department_name = md_file.stem  # 例如：儿科
            
            print(f"\n处理科室: {department_name}")
            
            # 查找科室
            department = db.query(Department).filter(
                Department.department_name == department_name,
                Department.deleted_at.is_(None)
            ).first()
            
            if not department:
                print(f"  ⚠️  科室 '{department_name}' 不存在，跳过")
                skip_count += 1
                continue
            
            # 不再检查是否已有问卷，因为已经全部删除
            
            try:
                # 读取并解析 Markdown 文件
                with open(md_file, 'r', encoding='utf-8') as f:
                    md_content = f.read()
                
                questionnaire_data = parse_markdown_questionnaire(md_content, department_name)
                
                # 验证问卷数据
                if not questionnaire_data["questions"]:
                    print(f"  ❌ 未能从文件中提取问题")
                    error_count += 1
                    continue
                
                # 创建问卷
                questionnaire = Questionnaire(
                    id=str(uuid.uuid4()),
                    department_id=department.id,
                    title=questionnaire_data["title"],
                    description=questionnaire_data["description"],
                    questions=questionnaire_data["questions"],
                    version=1,
                    status="active"
                )
                
                db.add(questionnaire)
                db.commit()
                
                print(f"  ✅ 成功创建问卷 (包含 {len(questionnaire_data['questions'])} 个问题)")
                success_count += 1
                
            except Exception as e:
                print(f"  ❌ 创建问卷失败: {str(e)}")
                error_count += 1
                db.rollback()
        
        print("\n" + "="*60)
        print(f"📊 导入完成:")
        print(f"   ✅ 成功: {success_count} 个")
        print(f"   ⚠️  跳过: {skip_count} 个")
        print(f"   ❌ 失败: {error_count} 个")
        
    except Exception as e:
        print(f"❌ 导入过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🏥 MediMeow 问卷导入工具")
    print("="*60)
    
    import_questionnaires()
    
    print("\n✨ 完成！\n")
