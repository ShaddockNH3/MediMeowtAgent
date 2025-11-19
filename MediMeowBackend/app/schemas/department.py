from pydantic import BaseModel, Field
from typing import Optional


class DepartmentCreate(BaseModel):
    """创建科室请求"""
    department_name: str = Field(..., description="科室名称")


class DepartmentInfo(BaseModel):
    """科室信息"""
    department_id: str
    department_name: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    deleted_at: Optional[str] = None


class DepartmentList(BaseModel):
    """科室列表"""
    department: list[DepartmentInfo]
