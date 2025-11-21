from fastapi import APIRouter, Depends, UploadFile, File, Form, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import re
import pandas as pd
from io import BytesIO
from app.database import get_db
from app.models.questionnaire import Questionnaire, QuestionnaireSubmission, UploadedFile
from app.models.medical_record import MedicalRecord
from app.models.department import Department
from app.models.doctor import Doctor
from app.utils import (
    get_current_user,
    save_upload_file,
    success_response,
    error_response
)
from app.services.ai_service import AIService

router = APIRouter(prefix="/questionnaires", tags=["问卷模块"])


@router.post("/import")
async def import_questionnaire(
    questionnaire: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """导入问卷 - 从Excel文件导入问卷（仅医生可用）"""
    
    # 验证用户类型
    if current_user.get("user_type") != "doctor":
        return error_response(code="10009", msg="仅医生可以导入问卷")
    
    # 获取医生信息
    doctor = db.query(Doctor).filter(
        Doctor.id == current_user["user_id"],
        Doctor.deleted_at.is_(None)
    ).first()
    
    if not doctor:
        return error_response(code="10010", msg="医生信息不存在")
    
    department_id = doctor.department_id
    
    # 验证文件类型
    if not questionnaire.filename.endswith(('.xlsx', '.xls')):
        return error_response(code="10011", msg="仅支持 Excel 文件格式 (.xlsx, .xls)")
    
    try:
        # 读取Excel文件
        contents = await questionnaire.read()
        df = pd.read_excel(BytesIO(contents))
        
        # 验证必需的列
        required_columns = ['题号', '题目类型', '问题标题', '选项/范围(失效列)', '是否必填']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return error_response(
                code="10012", 
                msg=f"Excel文件缺少必需列: {', '.join(missing_columns)}"
            )
        
        # 解析问卷数据
        questions = []
        questionnaire_title = None
        questionnaire_description = None
        
        for index, row in df.iterrows():
            question_id = str(row['题号']).strip()
            question_type = str(row['题目类型']).strip()
            question_text = str(row['问题标题']).strip()
            options_str = str(row['选项/范围(失效列)']).strip() if pd.notna(row['选项/范围(失效列)']) else ""
            is_required = str(row['是否必填']).strip() == "是"
            
            # 第一行作为问卷标题（如果题号为空或特殊标记）
            if index == 0 and (not question_id or question_id.lower() in ['title', '标题']):
                questionnaire_title = question_text
                questionnaire_description = options_str if options_str else "通过Excel导入的问卷"
                continue
            
            # 构建问题对象
            question_obj = {
                "id": question_id,
                "question": question_text,
                "required": is_required
            }
            
            # 根据题目类型解析
            if question_type == "单选":
                question_obj["type"] = "single"
                # 解析选项，支持中文逗号和英文逗号分隔
                options = re.split(r'[,，]', options_str)
                question_obj["options"] = [opt.strip() for opt in options if opt.strip()]
                
            elif question_type == "多选":
                question_obj["type"] = "multi"
                options = re.split(r'[,，]', options_str)
                question_obj["options"] = [opt.strip() for opt in options if opt.strip()]
                
            elif question_type == "评分":
                question_obj["type"] = "scale"
                # 解析范围，例如 "1-5"
                range_match = re.search(r'(\d+)\s*[-~]\s*(\d+)', options_str)
                if range_match:
                    question_obj["scale"] = {
                        "min": int(range_match.group(1)),
                        "max": int(range_match.group(2))
                    }
                else:
                    # 默认1-5
                    question_obj["scale"] = {"min": 1, "max": 5}
                    
            elif question_type == "文本":
                question_obj["type"] = "text"
                # 文本题可以有placeholder
                if options_str and options_str != "nan":
                    question_obj["placeholder"] = options_str
            else:
                # 未知类型，跳过或记录警告
                print(f"⚠️ 未知题目类型: {question_type}, 题号: {question_id}")
                continue
            
            questions.append(question_obj)
        
        # 如果没有解析到标题，使用文件名作为标题
        if not questionnaire_title:
            questionnaire_title = questionnaire.filename.rsplit('.', 1)[0]
            questionnaire_description = "通过Excel导入的问卷"
        
        # 验证是否有问题
        if not questions:
            return error_response(code="10013", msg="Excel文件中没有有效的问题数据")
        
        # 查询该科室是否已有问卷
        existing_questionnaire = db.query(Questionnaire).filter(
            Questionnaire.department_id == department_id,
            Questionnaire.deleted_at.is_(None)
        ).order_by(Questionnaire.version.desc()).first()
        
        # 确定版本号
        new_version = 1
        if existing_questionnaire:
            new_version = existing_questionnaire.version + 1
            # 将旧版本设为 inactive
            existing_questionnaire.status = 'inactive'
        
        # 创建新问卷
        new_questionnaire = Questionnaire(
            department_id=department_id,
            title=questionnaire_title,
            description=questionnaire_description,
            questions=questions,
            version=new_version,
            status='active'
        )
        
        db.add(new_questionnaire)
        db.commit()
        db.refresh(new_questionnaire)
        
        print(f"✅ 问卷导入成功 - ID: {new_questionnaire.id}, 版本: {new_version}, 问题数: {len(questions)}")
        
        return success_response(
            msg="问卷导入成功",
            data={
                "questionnaire_id": new_questionnaire.id,
                "title": questionnaire_title,
                "version": new_version,
                "question_count": len(questions)
            }
        )
        
    except pd.errors.EmptyDataError:
        return error_response(code="10014", msg="Excel文件为空")
    except Exception as e:
        print(f"❌ 问卷导入失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response(code="10015", msg=f"问卷导入失败: {str(e)}")


@router.get("/submit")
async def get_submitted_questionnaires(
    user_id: Optional[str] = Query(None, description="用户ID，不传则获取当前用户的"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户的所有已提交问卷列表"""
    target_user_id = user_id if user_id else current_user["user_id"]
    
    # 查询该用户的所有就诊记录（按创建时间倒序）
    records = db.query(MedicalRecord).filter(
        MedicalRecord.user_id == target_user_id,
        MedicalRecord.deleted_at.is_(None)
    ).order_by(MedicalRecord.created_at.desc()).all()
    
    if not records:
        return success_response(
            msg="暂无就诊记录",
            data={"total": 0, "records": []}
        )
    
    status_map = {
        "waiting": "等待处理",
        "in_progress": "处理中",
        "completed": "已处理完",
        "cancelled": "已取消"
    }
    
    # 构造返回数据列表
    result_list = []
    for record in records:
        # 获取问卷提交信息
        submission = db.query(QuestionnaireSubmission).filter(
            QuestionnaireSubmission.id == record.submission_id
        ).first()
        
        if not submission:
            continue
        
        # 获取问卷信息
        questionnaire = db.query(Questionnaire).filter(
            Questionnaire.id == submission.questionnaire_id
        ).first()
        
        # 获取科室信息
        department = db.query(Department).filter(
            Department.id == record.department_id
        ).first()
        
        record_data = {
            "record_id": record.id,
            "submission_id": submission.id,
            "questionnaire_id": submission.questionnaire_id,
            "questionnaire_title": questionnaire.title if questionnaire else "未知问卷",
            "department_name": department.department_name if department else "未知科室",
            "status": status_map.get(record.status, "其他"),
            "status_code": record.status,
            "priority": record.priority,
            "queue_number": record.queue_number,
            "submit_time": submission.submit_time.strftime("%Y-%m-%d %H:%M:%S") if submission.submit_time else None,
            "created_at": record.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
        
        # 如果有AI分析结果，添加到返回数据
        if submission.ai_result:
            record_data["ai_result"] = {
                "is_department": submission.ai_result.get("is_department", True),
                "key_info": submission.ai_result.get("key_info", {})
            }
        
        result_list.append(record_data)
    
    return success_response(
        msg="获取成功",
        data={
            "total": len(result_list),
            "records": result_list
        }
    )


@router.get("/{department_id}")
async def get_questionnaire(
    department_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取问卷（根据科室ID）"""
    print(f"📋 请求获取问卷 - 科室ID: {department_id}, 用户ID: {current_user['user_id']}")
    
    # 查询该科室的激活问卷，优先返回 active 状态
    questionnaire = db.query(Questionnaire).filter(
        Questionnaire.department_id == department_id,
        Questionnaire.status == 'active',
        Questionnaire.deleted_at.is_(None)
    ).order_by(Questionnaire.version.desc()).first()
    
    if not questionnaire:
        # 检查科室是否存在
        department = db.query(Department).filter(
            Department.id == department_id
        ).first()
        
        if not department:
            print(f"❌ 科室不存在: {department_id}")
            return error_response(code="10006", msg=f"科室不存在 (ID: {department_id})")
        
        # 科室存在但没有问卷
        print(f"❌ 科室 '{department.department_name}' 暂无可用问卷")
        return error_response(code="10006", msg=f"该科室({department.department_name})暂无可用问卷")
    
    print(f"✅ 找到问卷: {questionnaire.title} (ID: {questionnaire.id})")
    
    # 查询用户已保存的答案
    saved_submission = db.query(QuestionnaireSubmission).filter(
        QuestionnaireSubmission.user_id == current_user["user_id"],
        QuestionnaireSubmission.questionnaire_id == questionnaire.id,
        QuestionnaireSubmission.status == "draft"
    ).first()
    
    saved_answers = []
    if saved_submission and saved_submission.answers:
        for q_id, value in saved_submission.answers.items():
            saved_answers.append({
                "question_id": q_id,
                "value": value
            })
    
    # 转换问题格式，确保符合 API 规范
    formatted_questions = []
    for question in questionnaire.questions:
        formatted_question = {
            "question_id": question.get("id", ""),              # 必需
            "question_type": question.get("type", "text"),      # 必需
            "label": question.get("question", ""),              # 必需（题目标题）
            "is_required": "是" if question.get("required", False) else "否",  # 必需
        }
        
        # 可选字段
        if "placeholder" in question:
            formatted_question["placeholder"] = question["placeholder"]
        
        if "options" in question:
            formatted_question["options"] = question["options"]
        
        if "max_files" in question:
            formatted_question["max_files"] = str(question["max_files"])
        
        formatted_questions.append(formatted_question)
    
    return success_response(
        data={
            "questionnaires_id": questionnaire.id,
            "questions": formatted_questions,
            "saved_answers": saved_answers
        }
    )



from fastapi import Body
from pydantic import BaseModel
class QuestionnaireSubmitRequest(BaseModel):
    questionnaire_id: str
    department_id: str
    answers: dict
    file_id: Optional[List[str]] = None

@router.post("/submit")
async def submit_questionnaire(
    body: QuestionnaireSubmitRequest = Body(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """提交问卷（JSON参数，file_id为数组）"""
    from app.utils.auth import verify_user_exists
    verify_user_exists(current_user["user_id"], current_user["user_type"], db)

    questionnaire_id = body.questionnaire_id
    department_id = body.department_id
    answers = body.answers
    file_id = body.file_id

    # 验证必填字段
    if not questionnaire_id:
        return error_response(code="10007", msg="缺少问卷ID (questionnaire_id)")
    if not department_id:
        return error_response(code="10007", msg="缺少科室ID (department_id)")
    if not answers:
        return error_response(code="10007", msg="缺少问卷答案 (answers)")

    # 创建问卷提交记录
    submission = QuestionnaireSubmission(
        user_id=current_user["user_id"],
        questionnaire_id=questionnaire_id,
        department_id=department_id,
        answers=answers,
        file_ids=file_id,
        status="pending"
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)

    # 创建就诊记录
    medical_record = MedicalRecord(
        user_id=current_user["user_id"],
        submission_id=submission.id,
        department_id=department_id,
        status="waiting"
    )
    db.add(medical_record)
    db.commit()
    db.refresh(medical_record)

    # 调用AI服务进行分析
    try:
        ai_result = await AIService.analyze_questionnaire(
            questionnaire_data=answers,
            file_ids=file_id,
            department_id=department_id,
            db=db
        )
        # 保存 key_info 部分（符合数据库结构）
        submission.ai_result = ai_result.get("key_info", ai_result)
        submission.status = "completed"
        db.commit()
    except Exception as e:
        print(f"AI分析失败: {str(e)}")
        # AI 失败不影响提交

    return success_response(
        msg="提交成功",
        data={"record_id": medical_record.id}
    )


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """文件上传"""
    try:
        # 保存文件
        file_id, file_path, file_size = await save_upload_file(file)
        
        # 创建文件记录
        uploaded_file = UploadedFile(
            id=file_id,
            filename=file.filename,
            file_path=file_path,
            file_size=str(file_size),
            content_type=file.content_type or "application/octet-stream"
        )
        
        db.add(uploaded_file)
        db.commit()
        
        return success_response(
            msg="上传成功",
            data={"file_id": file_id}
        )
    except Exception as e:
        return error_response(code="10008", msg=f"上传失败: {str(e)}")


@router.get("/record/{record_id}")
async def get_questionnaire_record(
    record_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取问卷信息"""
    # 查询就诊记录
    record = db.query(MedicalRecord).filter(
        MedicalRecord.id == record_id,
        MedicalRecord.deleted_at.is_(None)
    ).first()
    
    if not record:
        return error_response(code="10005", msg="记录不存在")
    
    # 获取问卷提交信息
    submission = db.query(QuestionnaireSubmission).filter(
        QuestionnaireSubmission.id == record.submission_id
    ).first()
    
    status_map = {
        "waiting": "等待处理",
        "in_progress": "处理中",
        "completed": "已处理完"
    }
    
    response_data = {
        "status": status_map.get(record.status, "其他")
    }
    
    if submission:
        response_data["submission_id"] = submission.id
        if submission.ai_result:
            response_data["is_department"] = submission.ai_result.get("is_department", True)
            response_data["key_info"] = submission.ai_result.get("key_info", {})
    
    return success_response(data=response_data)
