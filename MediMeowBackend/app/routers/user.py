from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from pydantic import ValidationError
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, UserBind, UserLoginResponse
from app.utils import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    success_response,
    error_response
)

router = APIRouter(prefix="/user", tags=["用户模块"])


@router.post("/register")
async def register(
    phone_number: str = Form(..., min_length=11, max_length=11, description="手机号"),
    password: str = Form(..., min_length=6, max_length=72, description="密码，至少6位，最多72字节"),
    db: Session = Depends(get_db)
):
    """用户注册
    
    支持 application/json 和 multipart/form-data 两种格式
    
    表单字段:
    - phone_number: 手机号（11位，1开头）
    - password: 密码（至少6位）
    """
    try:
        # 验证手机号格式
        import re
        if not re.match(r'^1[3-9]\d{9}$', phone_number):
            return error_response(code="10001", msg="手机号格式不正确")
        
        # 检查手机号是否已存在
        existing_user = db.query(User).filter(
            User.phone_number == phone_number,
            User.deleted_at.is_(None)
        ).first()
        
        if existing_user:
            return error_response(code="10002", msg="手机号已被注册")
        
        # 创建新用户
        hashed_password = get_password_hash(password)
        new_user = User(
            phone_number=phone_number,
            password=hashed_password,
            username=f"默认用户{phone_number}"
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return success_response(msg="注册成功")
    except Exception as e:
        db.rollback()
        return error_response(code="10001", msg=f"注册失败: {str(e)}")


@router.post("/login")
async def login(
    phone_number: str = Form(..., min_length=11, max_length=11, description="手机号"),
    password: str = Form(..., min_length=6, max_length=72, description="密码"),
    db: Session = Depends(get_db)
):
    """用户登录
    
    支持 application/json 和 multipart/form-data 两种格式
    
    表单字段:
    - phone_number: 手机号
    - password: 密码
    """
    # 验证手机号格式
    import re
    if not re.match(r'^1[3-9]\d{9}$', phone_number):
        return error_response(code="10001", msg="手机号格式不正确")
    
    # 查找用户
    user = db.query(User).filter(
        User.phone_number == phone_number,
        User.deleted_at.is_(None)
    ).first()
    
    if not user or not verify_password(password, user.password):
        return error_response(code="10003", msg="手机号或密码错误")
    
    # 创建访问令牌
    access_token = create_access_token(
        data={"sub": user.id, "type": "user"}
    )
    
    # 按 API 文档数据结构定义：data.user 和 data.token
    return success_response(
        msg="登录成功",
        data={
            "user": {
                "id": user.id,
                "phone_number": user.phone_number,
                "username": user.username,
                "created_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S") if user.created_at else None,
                "updated_at": user.updated_at.strftime("%Y-%m-%d %H:%M:%S") if user.updated_at else None,
                "deleted_at": user.deleted_at.strftime("%Y-%m-%d %H:%M:%S") if user.deleted_at else None
            },
            "token": access_token
        }
    )


@router.get("/info")
async def get_user_info(
    user_id: str = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户信息"""
    # 如果没有提供user_id，使用当前用户ID
    target_user_id = user_id if user_id else current_user["user_id"]
    
    user = db.query(User).filter(
        User.id == target_user_id,
        User.deleted_at.is_(None)
    ).first()
    
    if not user:
        return error_response(code="10004", msg="用户不存在")
    
    user_info = {
        "id": user.id,
        "phone_number": user.phone_number,
        "username": user.username,
        "gender": user.gender,
        "birth": user.birth,
        "ethnicity": user.ethnicity,
        "origin": user.origin,
        "created_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S") if user.created_at else None,
        "updated_at": user.updated_at.strftime("%Y-%m-%d %H:%M:%S") if user.updated_at else None,
        "deleted_at": user.deleted_at.strftime("%Y-%m-%d %H:%M:%S") if user.deleted_at else None
    }
    
    return success_response(data=user_info)


@router.post("/bind")
async def bind_identity(
    username: str = Form(..., description="姓名"),
    gender: str = Form(..., description="性别"),
    birth: str = Form(..., description="出生年月日"),
    ethnicity: str = Form(..., description="民族"),
    origin: str = Form(..., description="籍贯"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """绑定身份证信息
    
    支持form-data和JSON两种格式
    """
    user = db.query(User).filter(
        User.id == current_user["user_id"],
        User.deleted_at.is_(None)
    ).first()
    
    if not user:
        return error_response(code="10004", msg="用户不存在")
    
    # 更新用户信息
    user.username = username
    user.gender = gender
    user.birth = birth
    user.ethnicity = ethnicity
    user.origin = origin
    
    db.commit()
    
    return success_response(msg="绑定成功")
