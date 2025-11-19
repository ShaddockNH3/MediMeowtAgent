from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DoctorLogin(BaseModel):
    """医生登录请求"""
    user_id: str = Field(..., description="医生ID")
    password: str = Field(..., description="密码")


class DoctorInfo(BaseModel):
    """医生信息"""
    id: str
    username: str
    department_name: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    deleted_at: Optional[str] = None


class DoctorReport(BaseModel):
    """医生提交诊断报告"""
    record_id: str = Field(..., description="就诊记录ID")
    text: str = Field(..., description="诊断内容")


class QueueResponse(BaseModel):
    """待诊队列响应"""
    record_ids: list[int]


class KeyInfo(BaseModel):
    """AI关键信息"""
    chief_complaint: str = Field(..., description="主诉概括")
    key_symptoms: str = Field(..., description="症状")
    image_summary: Optional[str] = Field(None, description="图片概述")
    important_notes: str = Field(..., description="医生需要注意")


class AIResult(BaseModel):
    """AI分析结果"""
    submission_id: str
    is_department: bool = Field(..., description="判断科室是否正确")
    key_info: KeyInfo


class SummaryResponse(BaseModel):
    """病情摘要响应"""
    user: dict
    ai_result: AIResult
