from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.database import get_db
from app.models.doctor import Doctor
from app.models.department import Department
from app.models.medical_record import MedicalRecord
from app.models.questionnaire import QuestionnaireSubmission
from app.models.user import User
from app.schemas.doctor import DoctorLogin, DoctorReport
from app.utils import (
    verify_password,
    create_access_token,
    get_current_doctor,
    success_response,
    error_response
)

router = APIRouter(prefix="/doctor", tags=["医生模块"])


@router.post("/login")
async def doctor_login(
    username: str = Query(..., description="医生用户名"),
    password: str = Query(..., description="密码"),
    db: Session = Depends(get_db)
):
    """医生登录"""
    # 查找医生（使用用户名）
    doctor = db.query(Doctor).filter(
        Doctor.username == username,
        Doctor.deleted_at.is_(None)
    ).first()
    
    if not doctor or not verify_password(password, doctor.password):
        return error_response(code="10003", msg="用户名或密码错误")
    
    # 获取科室名称
    department = db.query(Department).filter(
        Department.id == doctor.department_id
    ).first()
    
    # 创建访问令牌
    access_token = create_access_token(
        data={"sub": doctor.id, "type": "doctor"}
    )
    
    doctor_info = {
        "id": doctor.id,
        "username": doctor.username,
        "department_name": department.department_name if department else None,
        "created_at": doctor.created_at.isoformat() if doctor.created_at else None,
        "updated_at": doctor.updated_at.isoformat() if doctor.updated_at else None,
        "deleted_at": doctor.deleted_at.isoformat() if doctor.deleted_at else None
    }
    
    return success_response(
        msg="登录成功",
        data={
            "token": access_token,
            "doctor": doctor_info
        }
    )


@router.get("/queue")
async def get_queue(
    user_id: str = Query(...),
    current_doctor: dict = Depends(get_current_doctor),
    db: Session = Depends(get_db)
):
    """获取待诊队列"""
    # 获取医生信息
    doctor = db.query(Doctor).filter(Doctor.id == user_id).first()
    if not doctor:
        return error_response(code="10004", msg="医生不存在")
    
    # 查询该医生科室的待诊记录
    records = db.query(MedicalRecord).filter(
        and_(
            MedicalRecord.department_id == doctor.department_id,
            MedicalRecord.status == "waiting",
            MedicalRecord.deleted_at.is_(None)
        )
    ).order_by(MedicalRecord.queue_number).all()
    
    # 返回就诊记录ID列表（UUID字符串）
    record_ids = [record.id for record in records]
    
    return success_response(data={"record_ids": record_ids})


@router.get("/summary/{record_id}")
async def get_summary(
    record_id: str,
    current_doctor: dict = Depends(get_current_doctor),
    db: Session = Depends(get_db)
):
    """获取病情摘要"""
    # 查询就诊记录
    record = db.query(MedicalRecord).filter(
        MedicalRecord.id == record_id,
        MedicalRecord.deleted_at.is_(None)
    ).first()
    
    if not record:
        return error_response(code="10005", msg="记录不存在")
    
    # 获取用户信息
    user = db.query(User).filter(
        User.id == record.user_id,
        User.deleted_at.is_(None)
    ).first()
    if not user:
        return error_response(code="10004", msg="用户不存在")
    
    # 获取问卷提交信息
    submission = db.query(QuestionnaireSubmission).filter(
        QuestionnaireSubmission.id == record.submission_id
    ).first()
    
    user_info = {
        "id": user.id,
        "phone_number": user.phone_number,
        "username": user.username,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None,
        "deleted_at": user.deleted_at.isoformat() if user.deleted_at else None
    }
    
    ai_result = submission.ai_result if submission and submission.ai_result else {}
    ai_result["submission_id"] = record.submission_id
    
    return success_response(
        data={
            "user": user_info,
            "ai_result": ai_result
        }
    )


@router.post("/report")
async def submit_report(
    report_data: DoctorReport,
    current_doctor: dict = Depends(get_current_doctor),
    db: Session = Depends(get_db)
):
    """提交诊断报告"""
    # 查询就诊记录
    record = db.query(MedicalRecord).filter(
        MedicalRecord.id == report_data.record_id,
        MedicalRecord.deleted_at.is_(None)
    ).first()
    
    if not record:
        return error_response(code="10005", msg="记录不存在")
    
    # 更新诊断报告
    record.report = report_data.text
    record.status = "completed"
    record.doctor_id = current_doctor["user_id"]
    
    db.commit()
    
    return success_response(msg="提交成功")
