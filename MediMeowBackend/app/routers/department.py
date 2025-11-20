from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.department import Department
from app.schemas.department import DepartmentCreate
from app.utils import (
    get_current_user,
    success_response,
    error_response
)

router = APIRouter(prefix="/department", tags=["科室模块"])


@router.get("")
async def get_departments(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取科室列表"""
    departments = db.query(Department).filter(
        Department.deleted_at.is_(None)
    ).all()
    
    department_list = []
    for dept in departments:
        department_list.append({
            "department_id": dept.id,
            "department_name": dept.department_name,
            "created_at": dept.created_at.isoformat() if dept.created_at else None,
            "updated_at": dept.updated_at.isoformat() if dept.updated_at else None,
            "deleted_at": dept.deleted_at.isoformat() if dept.deleted_at else None
        })
    
    return success_response(data={"department": department_list})


@router.post("")
async def create_department(
    dept_data: DepartmentCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建科室"""
    # 检查科室名称是否已存在
    existing_dept = db.query(Department).filter(
        Department.department_name == dept_data.department_name,
        Department.deleted_at.is_(None)
    ).first()
    
    if existing_dept:
        return error_response(code="10009", msg="科室名称已存在")
    
    # 创建新科室
    new_dept = Department(
        department_name=dept_data.department_name
    )
    
    db.add(new_dept)
    db.commit()
    db.refresh(new_dept)
    
    return success_response(msg="创建成功")


@router.delete("/departments/{department_id}")
async def delete_department(
    department_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除科室（软删除）"""
    department = db.query(Department).filter(
        Department.id == department_id,
        Department.deleted_at.is_(None)
    ).first()
    
    if not department:
        return error_response(code="10010", msg="科室不存在")
    
    # 软删除
    from datetime import datetime
    department.deleted_at = datetime.utcnow()
    db.commit()
    
    return success_response(msg="删除成功")


@router.put("/departments/{department_id}")
async def update_department(
    department_id: str,
    dept_data: DepartmentCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """修改科室"""
    department = db.query(Department).filter(
        Department.id == department_id,
        Department.deleted_at.is_(None)
    ).first()
    
    if not department:
        return error_response(code="10010", msg="科室不存在")
    
    # 检查新名称是否与其他科室重复
    existing_dept = db.query(Department).filter(
        Department.department_name == dept_data.department_name,
        Department.id != department_id,
        Department.deleted_at.is_(None)
    ).first()
    
    if existing_dept:
        return error_response(code="10009", msg="科室名称已存在")
    
    # 更新科室名称
    department.department_name = dept_data.department_name
    db.commit()
    db.refresh(department)
    
    department_info = {
        "department_id": department.id,
        "department_name": department.department_name,
        "created_at": department.created_at.isoformat() if department.created_at else None,
        "updated_at": department.updated_at.isoformat() if department.updated_at else None,
        "deleted_at": department.deleted_at.isoformat() if department.deleted_at else None
    }
    
    return success_response(
        msg="修改成功",
        data={"department": department_info}
    )
