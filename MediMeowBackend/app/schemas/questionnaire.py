from pydantic import BaseModel, Field
from typing import Optional, List, Any


class Question(BaseModel):
    """问题模型"""
    question_id: str
    question_type: str = Field(..., description="问题类型: number, text, textarea, select, checkbox, image_upload")
    label: str = Field(..., description="题目标题")
    placeholder: Optional[str] = Field(None, description="输入提示")
    is_required: str = Field(..., description="是否必填")
    options: Optional[List[str]] = None
    max_files: Optional[str] = Field(None, description="图片上传限制")


class SavedAnswer(BaseModel):
    """保存的答案"""
    question_id: str
    value: str


class QuestionnaireDetail(BaseModel):
    """问卷详情"""
    questionnaires_id: str
    questions: List[Question]
    saved_answers: List[SavedAnswer] = []


class QuestionnaireSubmit(BaseModel):
    """问卷提交请求"""
    questionnaire_data: str = Field(..., description="json字符串")
    file_id: Optional[List[str]] = Field(None, description="上传的文件的id")


class QuestionnaireSubmitResponse(BaseModel):
    """问卷提交响应"""
    record_id: str


class FileUploadResponse(BaseModel):
    """文件上传响应"""
    file_id: str


class KeyInfo(BaseModel):
    """AI关键信息"""
    chief_complaint: str = Field(..., description="主诉概括")
    key_symptoms: str = Field(..., description="症状")
    image_summary: Optional[str] = Field(None, description="图片概述")
    important_notes: str = Field(..., description="医生需要注意")


class SubmissionStatus(BaseModel):
    """问卷提交状态"""
    status: str = Field(..., description="问卷状态")
    submission_id: Optional[str] = None
    is_department: Optional[bool] = Field(None, description="判断科室是否正确")
    key_info: Optional[KeyInfo] = None
