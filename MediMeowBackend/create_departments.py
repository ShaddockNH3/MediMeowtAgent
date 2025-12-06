#!/usr/bin/env python3
"""
创建科室（只创建 questionnaire 文件夹中存在的科室）
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.database import SessionLocal
from app.models.department import Department
import uuid


def create_departments_from_questionnaires():
    """根据问卷文件夹中的 MD 文件创建科室"""
    db = SessionLocal()
    
    # 问卷文件夹路径
    questionnaire_dir = project_root.parent / "docs" / "questionnaire"
    
    if not questionnaire_dir.exists():
        print(f"❌ 问卷文件夹不存在: {questionnaire_dir}")
        return
    
    # 获取所有 Markdown 文件，从文件名提取科室名称
    md_files = list(questionnaire_dir.glob("*.md"))
    required_departments = [f.stem for f in md_files if f.name != "git.keep"]
    
    print(f"📋 从问卷文件夹找到 {len(required_departments)} 个科室")
    
    try:
        # 第一步：删除所有现有数据（按外键依赖顺序）
        print("\n🗑️  删除所有现有数据...")
        
        # 1. 删除就诊记录
        from app.models.medical_record import MedicalRecord
        records_deleted = db.query(MedicalRecord).delete()
        print(f"   已删除 {records_deleted} 个就诊记录")
        
        # 2. 删除问卷提交记录
        from app.models.questionnaire import QuestionnaireSubmission
        submissions_deleted = db.query(QuestionnaireSubmission).delete()
        print(f"   已删除 {submissions_deleted} 个问卷提交记录")
        
        # 3. 删除问卷
        from app.models.questionnaire import Questionnaire
        questionnaires_deleted = db.query(Questionnaire).delete()
        print(f"   已删除 {questionnaires_deleted} 个问卷")
        
        # 4. 删除医生（doctors 表有外键引用 departments）
        from app.models.doctor import Doctor
        doctors_deleted = db.query(Doctor).delete()
        print(f"   已删除 {doctors_deleted} 个医生")
        
        # 5. 删除科室
        departments_deleted = db.query(Department).delete()
        print(f"   已删除 {departments_deleted} 个科室")
        
        db.commit()
        
        print("\n" + "="*60)
        print("📝 创建新科室...")
        print("="*60 + "\n")
        
        # 第二步：创建新科室
        created_count = 0
        
        for dept_name in required_departments:
            department = Department(
                id=str(uuid.uuid4()),
                department_name=dept_name
            )
            db.add(department)
            print(f"  ✅ 创建科室: {dept_name}")
            created_count += 1
        
        db.commit()
        
        print(f"\n📊 统计:")
        print(f"   ✅ 成功创建: {created_count} 个科室")
        
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🏥 重建科室（仅保留 questionnaire 文件夹中的科室）")
    print("="*60 + "\n")
    
    create_departments_from_questionnaires()
    
    print("\n✨ 完成！\n")
