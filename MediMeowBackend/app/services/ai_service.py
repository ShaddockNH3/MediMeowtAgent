"""
AI 服务模块

此模块用于与AI服务进行交互，分析问卷数据并返回分析结果
"""
from typing import Dict, Any, List, Optional
import json
import grpc
import base64
import os
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import SessionLocal
from app.models.questionnaire import Questionnaire, QuestionnaireSubmission
from app.models.department import Department
from app.models.user import User
from .grpc_client import medical_ai_pb2 as pb2
from .grpc_client import medical_ai_pb2_grpc as pb2_grpc


class AIService:
    """AI服务类"""

    ALLOWED_DEPARTMENTS = ["耳鼻喉科", "呼吸科"]

    @staticmethod
    def _get_question_label_mapping(questionnaire_id: str, db: Session) -> Dict[str, str]:
        """获取问题ID到标签的映射"""
        questionnaire = db.query(Questionnaire).filter(Questionnaire.id == questionnaire_id).first()
        if not questionnaire or not questionnaire.questions:
            return {}

        question_mapping = {}
        for question in questionnaire.questions:
            if isinstance(question, dict) and 'id' in question and 'label' in question:
                question_mapping[question['id']] = question['label']
        return question_mapping

    @staticmethod
    def _get_department_name(department_id: str, db: Session) -> str:
        """获取科室名称"""
        department = db.query(Department).filter(Department.id == department_id).first()
        return department.department_name if department else "未知科室"

    @staticmethod
    def _get_user_info(user_id: str, db: Session) -> Dict[str, Any]:
        """获取用户信息"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"name": "未知患者", "gender": "未知", "age": "未知"}
        return {
            "name": user.username or "未知患者",
            "gender": user.gender or "未知",
            "age": "未知"  # User模型没有age字段
        }

    @staticmethod
    def _construct_patient_text_data(
        questionnaire_data: Dict[str, Any],
        question_mapping: Dict[str, str],
        department_name: str,
        user_info: Dict[str, Any]
    ) -> str:
        """构造患者文本数据"""
        text_parts = []

        # 基本信息
        text_parts.append("**患者基本信息**")
        text_parts.append(f"姓名：{user_info['name']}")
        text_parts.append(f"性别：{user_info['gender']}")
        text_parts.append(f"年龄：{user_info['age']}")
        text_parts.append(f"就诊科室：{department_name}")
        text_parts.append("")

        # 问卷答案
        text_parts.append("**问卷回答**")
        answers = questionnaire_data.get('answers', {})
        for question_id, answer in answers.items():
            label = question_mapping.get(question_id, f"问题{question_id}")
            text_parts.append(f"{label}：{answer}")
        text_parts.append("")

        # 主诉（从答案中提取关键信息）
        chief_complaint = AIService._extract_chief_complaint(answers, question_mapping)
        text_parts.append("**主诉**")
        text_parts.append(chief_complaint)

        return "\n".join(text_parts)

    @staticmethod
    def _extract_chief_complaint(answers: Dict[str, Any], question_mapping: Dict[str, str]) -> str:
        """从答案中提取主诉"""
        # 简单的提取逻辑，可以根据实际问题定制
        symptoms = []
        for question_id, answer in answers.items():
            if isinstance(answer, str) and len(answer.strip()) > 0:
                label = question_mapping.get(question_id, "")
                if any(keyword in label.lower() for keyword in ['症状', '不适', '疼痛', '问题']):
                    symptoms.append(answer.strip())

        if symptoms:
            return "；".join(symptoms)
        return "患者描述了相关症状，请查看问卷详情"

    @staticmethod
    def _call_grpc_ai_service(patient_text_data: str, image_base64: str, department_name: str) -> Dict[str, Any]:
        """调用gRPC AI服务"""
        try:
            ai_service_host = os.getenv('AI_SERVICE_HOST', '127.0.0.1:50051')
            with grpc.insecure_channel(ai_service_host) as channel:
                stub = pb2_grpc.MedicalAIServiceStub(channel)
                request = pb2.AnalysisRequest(
                    patient_text_data=patient_text_data,
                    image_base64=image_base64,
                    stream=False,
                    patient_department=department_name
                )

                response_iterator = stub.ProcessMedicalAnalysis(request)

                for response_chunk in response_iterator:
                    if response_chunk.is_end:
                        # 反序列化报告
                        sync_report = pb2.AnalysisReport.FromString(response_chunk.chunk_data)
                        if sync_report.status == "SUCCESS":
                            # 解析structured_report，假设是JSON字符串
                            try:
                                result_data = json.loads(sync_report.structured_report)
                                return {
                                    "is_department": True,
                                    "key_info": result_data.get("key_info", {}),
                                    "analysis_time": result_data.get("analysis_time", "0.5s"),
                                    "model_version": result_data.get("model_version", "v1.0"),
                                    "status": "success"
                                }
                            except json.JSONDecodeError:
                                return {
                                    "is_department": True,
                                    "key_info": {
                                        "chief_complaint": "AI分析完成",
                                        "key_symptoms": sync_report.structured_report,
                                        "image_summary": "图片已分析",
                                        "important_notes": "请查看详细报告",
                                        "risk_level": "中等",
                                        "suggested_department": department_name
                                    },
                                    "analysis_time": "0.5s",
                                    "model_version": "v1.0",
                                    "status": "success"
                                }
                        else:
                            raise Exception(f"AI服务返回失败: {sync_report.message}")
                    # 如果没有找到结束标记，继续循环

                # 如果循环结束仍未返回，抛出异常
                raise Exception("gRPC响应不完整，未收到结束标记")

        except Exception as e:
            raise Exception(f"gRPC调用失败: {str(e)}")

    @staticmethod
    def _get_fallback_result(department_name: str) -> Dict[str, Any]:
        """降级策略：返回模拟结果"""
        return {
            "is_department": True,
            "key_info": {
                "chief_complaint": "AI服务暂时不可用，请医生根据问卷判断",
                "key_symptoms": "需要医生进一步询问",
                "image_summary": "AI服务降级，未分析图片",
                "important_notes": "AI服务暂时不可用，建议人工判断",
                "risk_level": "未知",
                "suggested_department": department_name
            },
            "analysis_time": "0.0s",
            "model_version": "fallback-v1.0",
            "status": "fallback"
        }

    @staticmethod
    async def analyze_questionnaire(
        questionnaire_data: Dict[str, Any],
        file_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        分析问卷数据

        Args:
            questionnaire_data: 问卷数据，包含questionnaire_id, user_id, department_id, answers等
            file_ids: 上传的文件ID列表

        Returns:
            AI分析结果
        """
        db = SessionLocal()
        try:
            # 提取必要信息
            questionnaire_id = questionnaire_data.get('questionnaire_id')
            user_id = questionnaire_data.get('user_id')
            department_id = questionnaire_data.get('department_id')

            if not questionnaire_id or not user_id or not department_id:
                raise ValueError("缺少必要的数据：questionnaire_id, user_id, department_id")

            # 类型检查
            if not isinstance(questionnaire_id, str) or not isinstance(user_id, str) or not isinstance(department_id, str):
                raise ValueError("数据类型错误：questionnaire_id, user_id, department_id必须是字符串")

            # 获取科室名称并检查是否允许
            department_name = AIService._get_department_name(department_id, db)
            if department_name not in AIService.ALLOWED_DEPARTMENTS:
                raise ValueError(f"不支持的科室：{department_name}。只支持：{', '.join(AIService.ALLOWED_DEPARTMENTS)}")

            # 获取问题映射和用户信息
            question_mapping = AIService._get_question_label_mapping(questionnaire_id, db)
            user_info = AIService._get_user_info(user_id, db)

            # 构造患者文本数据
            patient_text_data = AIService._construct_patient_text_data(
                questionnaire_data, question_mapping, department_name, user_info
            )

            # 处理图片
            image_base64 = ""
            if file_ids:
                try:
                    # 处理第一个文件（假设是图片）
                    from app.utils.file_handler import get_file_path
                    file_path = get_file_path(file_ids[0])

                    # 读取文件并转换为base64
                    with open(file_path, 'rb') as image_file:
                        image_data = image_file.read()
                        image_base64 = base64.b64encode(image_data).decode('utf-8')

                    # 添加MIME类型前缀（简单判断文件类型）
                    file_ext = file_path.lower().split('.')[-1]
                    if file_ext in ['jpg', 'jpeg']:
                        image_base64 = f"data:image/jpeg;base64,{image_base64}"
                    elif file_ext == 'png':
                        image_base64 = f"data:image/png;base64,{image_base64}"
                    elif file_ext == 'gif':
                        image_base64 = f"data:image/gif;base64,{image_base64}"
                    else:
                        image_base64 = f"data:image/png;base64,{image_base64}"  # 默认当作PNG

                except Exception as e:
                    print(f"图片处理失败: {str(e)}")
                    image_base64 = ""

            # 调用gRPC AI服务
            try:
                result = AIService._call_grpc_ai_service(patient_text_data, image_base64, department_name)
                result["key_info"]["image_summary"] = f"已上传{len(file_ids) if file_ids else 0}个文件进行分析"
                return result
            except Exception as e:
                # 降级策略
                print(f"AI服务调用失败，使用降级策略: {str(e)}")
                result = AIService._get_fallback_result(department_name)
                result["key_info"]["image_summary"] = f"AI服务降级，未分析{len(file_ids) if file_ids else 0}个文件"
                return result

        except ValueError as e:
            # 数据验证错误
            raise e
        except Exception as e:
            # 其他错误，使用降级策略
            print(f"分析过程中发生错误: {str(e)}")
            return AIService._get_fallback_result("未知科室")
        finally:
            db.close()
    
    @staticmethod
    async def analyze_medical_image(file_path: str) -> str:
        """
        分析医学图片
        
        Args:
            file_path: 图片文件路径
            
        Returns:
            图片分析结果
        """
        # TODO: 实现图片分析功能
        return "图片分析结果示例"
    
    @staticmethod
    def format_ai_result(ai_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        格式化AI分析结果
        
        Args:
            ai_result: 原始AI分析结果
            
        Returns:
            格式化后的结果
        """
        return {
            "is_department": ai_result.get("is_department", True),
            "key_info": {
                "chief_complaint": ai_result.get("key_info", {}).get("chief_complaint", ""),
                "key_symptoms": ai_result.get("key_info", {}).get("key_symptoms", ""),
                "image_summary": ai_result.get("key_info", {}).get("image_summary"),
                "important_notes": ai_result.get("key_info", {}).get("important_notes", "")
            }
        }
