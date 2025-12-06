#!/usr/bin/env python3
"""
为每个科室创建一个医生账号
医生用户名 = 科室名
密码 = 123
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.database import SessionLocal
from app.models.department import Department
from app.models.doctor import Doctor
import uuid
import bcrypt


def create_doctors_for_departments():
    """为每个科室创建医生"""
    db = SessionLocal()
    
    try:
        # 获取所有科室
        departments = db.query(Department).filter(Department.deleted_at.is_(None)).all()
        
        if not departments:
            print("❌ 未找到科室数据，请先创建科室")
            return
        
        print(f"\n📋 找到 {len(departments)} 个科室")
        print("\n" + "="*60)
        print("👨‍⚕️ 创建医生账号...")
        print("="*60 + "\n")
        
        # 密码：123 (使用 bcrypt 加密，12轮)
        password = "123"
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')
        
        # 删除所有现有医生
        existing_doctors = db.query(Doctor).all()
        if existing_doctors:
            for doctor in existing_doctors:
                db.delete(doctor)
            db.commit()
            print(f"🗑️  已删除 {len(existing_doctors)} 个现有医生\n")
        
        created_count = 0
        
        for dept in departments:
            # 检查是否已存在同名医生
            existing = db.query(Doctor).filter(
                Doctor.username == dept.department_name,
                Doctor.deleted_at.is_(None)
            ).first()
            
            if existing:
                print(f"  ⚠️  医生已存在: {dept.department_name}")
                continue
            
            # 创建医生
            doctor = Doctor(
                id=str(uuid.uuid4()),
                username=dept.department_name,
                password=hashed_password,
                department_id=dept.id
            )
            db.add(doctor)
            print(f"  ✅ 创建医生: {dept.department_name} (科室: {dept.department_name})")
            created_count += 1
        
        db.commit()
        
        print(f"\n" + "="*60)
        print(f"📊 统计:")
        print(f"   ✅ 成功创建: {created_count} 个医生")
        print(f"   📝 用户名: 各科室名称")
        print(f"   🔐 密码: 123")
        print("="*60)
        
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🏥 为所有科室创建医生账号")
    print("="*60)
    
    create_doctors_for_departments()
    
    print("\n✨ 完成！\n")
