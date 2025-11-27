import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

import os
from typing import List
from operator import itemgetter

# LangChain Imports
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.documents import Document

# 模块导入
import config.config as config
import prompts.prompts as prompts
import utils.utils as utils
import rag.rag_core as rag_core

def run_three_stage_rag(patient_text_data: str, image_path: str, vector_store):
    """
    执行三阶段 RAG 流程
    """
    llm = utils.get_glm4_llm()
    base64_image = utils.image_to_base64(image_path)
    
    # ----------------------------------------------------
    # 阶段 1: 多模态生成初步纯文本描述
    # ----------------------------------------------------
    print("\n--- 阶段 1: 正在使用 GLM-4 生成纯文本描述块... ---")
    messages_stage1 = [
        SystemMessage(content="你是一位专业、客观的医疗助手，严格按照提供的格式输出。"),
        HumanMessage(
            content=[
                {"type": "text", "text": prompts.STAGE1_PROMPT_TEMPLATE.format(text_input=patient_text_data)},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]
        )
    ]
    stage1_response = llm.invoke(messages_stage1)
    multimodal_description_block = stage1_response.content
    print("--- 阶段 1: 纯文本描述块生成成功！ ---")
    
    # ----------------------------------------------------
    # 阶段 2: RAG 检索
    # ----------------------------------------------------
    print("\n--- 阶段 2: RAG 检索中... ---")
    
    # 2.1 提取关键词
    keyword_prompt = ChatPromptTemplate.from_template(prompts.RAG_RETRIEVAL_PROMPT)
    keyword_chain = keyword_prompt | llm | (lambda x: x.content) # 使用 lambda 访问 .content
    retrieval_keywords = keyword_chain.invoke({"report_fragment": multimodal_description_block})
    print(f"--- 检索关键词: {retrieval_keywords} ---")

    # 2.2 执行检索
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})
    retrieved_docs: List[Document] = retriever.invoke(retrieval_keywords) 
    retrieved_context = "\n---\n".join([doc.page_content for doc in retrieved_docs])
    print(f"--- 阶段 2: 检索到 {len(retrieved_docs)} 个知识片段 ---")
    
    # ----------------------------------------------------
    # 阶段 3: 整合生成最终病历
    # ----------------------------------------------------
    print("\n--- 阶段 3: 整合信息，生成最终病历... ---")
    
    final_prompt = ChatPromptTemplate.from_template(prompts.FINAL_REPORT_PROMPT)
    final_chain = final_prompt | llm | (lambda x: x.content)
    
    final_report = final_chain.invoke({
        "original_text_data": patient_text_data,
        "multimodal_description": multimodal_description_block, 
        "retrieved_context": retrieved_context
    })
    
    return final_report

if __name__ == "__main__":
    print("\n" + "="*80)
    print("启动医疗 RAG 辅助系统")
    print("="*80)

    # 模拟输入数据
    PATIENT_TEXT_DATA = """
    **患者基本信息**
    姓名：张同学
    性别：男
    年龄：20 岁
    职业：在校大学生
    身高：176 cm
    体重：85 kg
    BMI指数：约 27.4
    过敏史：无
    既往病史：无特殊说明

    **主诉与现病史**
    主诉：咽喉剧烈疼痛。
    症状描述：患者自述喉咙难受，伴有明显的痛感。
    """
    
    # 检查图片
    if not os.path.exists(config.DEFAULT_IMAGE_PATH):
        print(f"\n--- 错误：请将您的测试图片命名为 {config.DEFAULT_IMAGE_PATH} 放入当前目录 ---")
        exit()
    
    # 构建/加载数据库
    vector_store = rag_core.build_or_load_rag_index()
    
    if vector_store:
        # 运行
        final_result = run_three_stage_rag(
            PATIENT_TEXT_DATA,
            config.DEFAULT_IMAGE_PATH,
            vector_store
        )
        
        print("\n" + "="*80)
        print("【最终结构化病历】")
        print("="*80)
        print(final_result)
        print("="*80)
