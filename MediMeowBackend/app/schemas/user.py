from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
import re


class UserRegister(BaseModel):
    """用户注册请求"""
    phone_number: str = Field(..., min_length=11, max_length=11, description="手机号")
    password: str = Field(..., min_length=6, max_length=72, description="密码，至少6位，最多72字节")
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        """验证手机号格式"""
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('手机号格式不正确')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "phone_number": "13800138000",
                "password": "test123456"
            }
        }


class UserLogin(BaseModel):
    """用户登录请求"""
    phone_number: str = Field(..., min_length=11, max_length=11, description="手机号")
    password: str = Field(..., min_length=6, max_length=72, description="密码")
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        """验证手机号格式"""
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('手机号格式不正确')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "phone_number": "13800138000",
                "password": "test123456"
            }
        }


class UserBind(BaseModel):
    """绑定身份证请求"""
    username: str = Field(..., description="姓名")
    gender: str = Field(..., description="性别")
    birth: str = Field(..., description="出生年月日")
    ethnicity: str = Field(..., description="民族")
    origin: str = Field(..., description="籍贯")


class UserInfo(BaseModel):
    """用户信息"""
    id: str
    phone_number: str
    username: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserLoginResponse(BaseModel):
    """用户登录响应"""
    id: str
    phone_number: str
    username: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    deleted_at: Optional[str] = None
