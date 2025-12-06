from sqlalchemy import Column, String, DateTime, Text, JSON, Integer
from sqlalchemy.sql import func
from app.database import Base
import uuid


class Questionnaire(Base):
    """问卷表"""
    __tablename__ = "questionnaires"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    department_id = Column(String(36), nullable=False)
    title = Column(String(200), nullable=False)  # 问卷标题
    description = Column(Text, nullable=True)  # 问卷描述
    questions = Column(JSON, nullable=False)  # 问题列表
    version = Column(Integer, default=1)  # 问卷版本号
    status = Column(String(20), default='active')  # active/inactive/draft
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)


class QuestionnaireSubmission(Base):
    """问卷提交表"""
    __tablename__ = "questionnaire_submissions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False)
    questionnaire_id = Column(String(64), nullable=False)
    department_id = Column(String(36), nullable=False)
    answers = Column(JSON, nullable=False)  # 答案数据
    file_ids = Column(JSON, nullable=True)  # 上传的文件ID列表
    
    # 用户身高体重
    height = Column(Integer, nullable=True, comment="身高(cm)")
    weight = Column(Integer, nullable=True, comment="体重(kg)")
    
    # AI分析结果
    ai_result = Column(JSON, nullable=True)
    status = Column(String(20), default="pending")  # pending, processing, completed, draft
    submit_time = Column(DateTime(timezone=True), server_default=func.now(), comment="提交时间")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)


class UploadedFile(Base):
    """上传文件表"""
    __tablename__ = "uploaded_files"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(String(20), nullable=False)
    content_type = Column(String(100), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
