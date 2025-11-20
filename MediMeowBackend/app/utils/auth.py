from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from config import settings

# HTTP Bearer 认证
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码

    密码只包含ASCII字符（英文字母、数字、半角符号）
    bcrypt默认只接受前72字节的密码，超过部分会被忽略
    """
    # 确保密码是ASCII字符串并截断到72字节以内，与哈希时保持一致
    truncated_password = plain_password.encode('ascii', errors='ignore').decode('ascii')[:72]
    # 使用bcrypt直接验证
    return bcrypt.checkpw(truncated_password.encode('ascii'), hashed_password.encode('ascii'))
def get_password_hash(password: str) -> str:
    """获取密码哈希

    密码只包含ASCII字符（英文字母、数字、半角符号）
    bcrypt默认只接受前72字节的密码，超过部分会被忽略
    """
    # 确保密码是ASCII字符串并截断到72字节以内
    truncated_password = password.encode('ascii', errors='ignore').decode('ascii')[:72]
    # 使用bcrypt直接哈希
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(truncated_password.encode('ascii'), salt)
    return hashed.decode('ascii')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> dict:
    """验证令牌"""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """获取当前用户（仅验证 JWT token）"""
    token = credentials.credentials
    
    try:
        payload = verify_token(token)
    except HTTPException:
        # 重新抛出更友好的错误消息
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="登录已过期或无效，请重新登录",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    user_type = payload.get("type", "user")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="认证信息不完整，请重新登录",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {"user_id": user_id, "user_type": user_type}


def verify_user_exists(user_id: str, user_type: str, db: Session) -> None:
    """验证用户在数据库中是否存在
    
    Args:
        user_id: 用户ID
        user_type: 用户类型 (user/doctor)
        db: 数据库会话
        
    Raises:
        HTTPException: 用户不存在时抛出 401 错误
    """
    from app.models.user import User
    from app.models.doctor import Doctor
    
    if user_type == "doctor":
        user_exists = db.query(Doctor).filter(
            Doctor.id == user_id,
            Doctor.deleted_at.is_(None)
        ).first()
    else:
        user_exists = db.query(User).filter(
            User.id == user_id,
            User.deleted_at.is_(None)
        ).first()
    
    if not user_exists:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被删除，请重新登录",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_doctor(current_user: dict = Depends(get_current_user)) -> dict:
    """获取当前医生"""
    if current_user.get("user_type") != "doctor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要医生权限",
        )
    return current_user
