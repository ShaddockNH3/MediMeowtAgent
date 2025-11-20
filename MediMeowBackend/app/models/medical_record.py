from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Integer
from sqlalchemy.sql import func
from app.database import Base
import uuid


class MedicalRecord(Base):
    """就诊记录表"""
    __tablename__ = "medical_records"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    doctor_id = Column(String(36), ForeignKey("doctors.id"), nullable=True)
    submission_id = Column(String(36), ForeignKey("questionnaire_submissions.id"), nullable=False)
    department_id = Column(String(36), ForeignKey("departments.id"), nullable=False)
    
    # 医生诊断信息
    report = Column(Text, nullable=True, comment="医生诊断报告")
    diagnosis = Column(String(500), nullable=True, comment="诊断结果")
    prescription = Column(Text, nullable=True, comment="处方")
    treatment_plan = Column(Text, nullable=True, comment="治疗方案")
    
    # 状态和优先级
    status = Column(String(20), default="waiting", comment="状态 (waiting/in_progress/completed/cancelled)")
    priority = Column(String(20), default="normal", comment="优先级 (urgent/high/normal/low)")
    queue_number = Column(Integer, nullable=True, comment="排队号码")
    
    # 时间记录
    appointment_time = Column(DateTime(timezone=True), nullable=True, comment="预约时间")
    consultation_time = Column(DateTime(timezone=True), nullable=True, comment="就诊开始时间")
    completion_time = Column(DateTime(timezone=True), nullable=True, comment="就诊完成时间")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
