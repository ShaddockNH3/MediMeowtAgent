from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base
import uuid


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    username = Column(String(100), nullable=True)
    
    # 身份证信息
    gender = Column(String(10), nullable=True)
    birth = Column(String(20), nullable=True)
    ethnicity = Column(String(50), nullable=True)
    origin = Column(String(100), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
