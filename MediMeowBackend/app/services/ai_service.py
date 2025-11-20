"""
AI 服务模块

此模块用于与AI服务进行交互，分析问卷数据并返回分析结果
"""
from typing import Dict, Any, List
import json


class AIService:
    """AI服务类"""
    
    @staticmethod
    async def analyze_questionnaire(
        questionnaire_data: Dict[str, Any],
        file_ids: List[str] = None
    ) -> Dict[str, Any]:
        """
        分析问卷数据 (模拟AI分析)
        
        Args:
            questionnaire_data: 问卷数据
            file_ids: 上传的文件ID列表
            
        Returns:
            AI分析结果
        """
        # 模拟AI分析延迟
        import asyncio
        await asyncio.sleep(0.5)
        
        # 提取问卷中的关键信息
        chief_complaint = "患者主诉不适"
        symptoms_list = []
        
        # 尝试从问卷数据中提取症状信息
        for key, value in questionnaire_data.items():
            if value and isinstance(value, str):
                if len(value) > 10:  # 假设较长的回答包含有用信息
                    symptoms_list.append(value)
        
        key_symptoms = " | ".join(symptoms_list) if symptoms_list else "需要进一步询问症状详情"
        
        # 模拟AI分析结果
        result = {
            "is_department": True,
            "key_info": {
                "chief_complaint": chief_complaint,
                "key_symptoms": key_symptoms,
                "image_summary": f"已上传{len(file_ids)}个文件进行分析" if file_ids else "未上传图片",
                "important_notes": "建议医生重点关注患者症状的持续时间和严重程度",
                "risk_level": "中等",
                "suggested_department": "内科"
            },
            "analysis_time": "0.5s",
            "model_version": "v1.0-mock"
        }
        
        return result
    
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
