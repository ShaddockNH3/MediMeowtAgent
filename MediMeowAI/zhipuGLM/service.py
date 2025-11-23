import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

import os
import json
from typing import List, Generator, Union, Optional
from operator import itemgetter

from zhipuai import ZhipuAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma

# 导入底层依赖模块
import config.config as config
import prompts.prompts as prompts
import utils.utils as utils
import rag.rag_core as rag_core

# -----------------------------------------------------------------
# 1. Protobuf 消息结构模拟
# -----------------------------------------------------------------

class AnalysisRequest:
    """模拟 Protobuf 输入消息结构。"""
    def __init__(self, patient_text_data: str, image_base64: str, stream: bool = False):
        self.patient_text_data = patient_text_data
        self.image_base64 = image_base64
        self.stream = stream

class AnalysisReport:
    """模拟 Protobuf 输出消息结构"""
    def __init__(self, structured_report: str, status: str = "SUCCESS"):
        self.structured_report = structured_report
        self.status = status

# 流式传输的输出类型
StreamReport = Generator[str, None, None]

# -----------------------------------------------------------------
# 2. 全局依赖 
# -----------------------------------------------------------------
GLOBAL_VECTOR_STORE: Optional[Chroma] = None
GLOBAL_LLM = None
GLOBAL_ZHIPU_CLIENT: Optional[ZhipuAI] = None

def initialize_service():
    """
    服务初始化函数：加载 LLM 实例、向量数据库和智谱客户端。
    此函数必须在服务（如 FastAPI 应用）启动时运行一次。
    """
    global GLOBAL_VECTOR_STORE
    global GLOBAL_LLM
    global GLOBAL_ZHIPU_CLIENT
    
    try:
        GLOBAL_VECTOR_STORE = rag_core.build_or_load_rag_index()
        GLOBAL_LLM = utils.get_glm4_llm()
        GLOBAL_ZHIPU_CLIENT = ZhipuAI(api_key=os.environ["GLM_API_KEY"])
    except Exception as e:
        print(f"服务初始化失败: {e}")
        GLOBAL_VECTOR_STORE = None
        GLOBAL_LLM = None
        GLOBAL_ZHIPU_CLIENT = None
        
def _stage1_generate_description(llm, patient_text_data: str, image_base64: str) -> str:
    messages_stage1 = [
        SystemMessage(content="你是一位专业、客观的医疗助手，严格按照提供的格式输出。"),
        HumanMessage(
            content=[
                {"type": "text", "text": prompts.STAGE1_PROMPT_TEMPLATE.format(text_input=patient_text_data)},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
            ]
        )
    ]
    response = llm.invoke(messages_stage1)
    return response.content

def _stage2_retrieve_context(llm, multimodal_description_block: str, vector_store: Chroma) -> str:
    keyword_prompt = ChatPromptTemplate.from_template(prompts.RAG_RETRIEVAL_PROMPT)
    keyword_chain = keyword_prompt | llm | (lambda x: x.content)
    retrieval_keywords = keyword_chain.invoke({"report_fragment": multimodal_description_block})

    retriever = vector_store.as_retriever(search_kwargs={"k": 5})
    retrieved_docs: List[Document] = retriever.invoke(retrieval_keywords) 
    retrieved_context = "\n---\n".join([doc.page_content for doc in retrieved_docs])
    return retrieved_context

def _stage3_sync_generate_final_report(llm, patient_text_data: str, multimodal_description_block: str, retrieved_context: str) -> str:
    final_prompt = ChatPromptTemplate.from_template(prompts.FINAL_REPORT_PROMPT)
    final_chain = final_prompt | llm | (lambda x: x.content)
    final_report = final_chain.invoke({
        "original_text_data": patient_text_data,
        "multimodal_description": multimodal_description_block, 
        "retrieved_context": retrieved_context
    })
    return final_report

def _stage3_stream_generate_final_report(client: ZhipuAI, patient_text_data: str, multimodal_description_block: str, retrieved_context: str) -> StreamReport:
    prompt_text = prompts.FINAL_REPORT_PROMPT.format(
        original_text_data=patient_text_data,
        multimodal_description=multimodal_description_block,
        retrieved_context=retrieved_context
    )
    
    response = client.chat.completions.create(
        model="glm-4.1v-thinking-flash",
        messages=[{"role": "user", "content": prompt_text}],
        temperature=config.TEMPERATURE,
        max_tokens=config.MAX_TOKENS,
        stream=True
    )
    
    for chunk in response:
        if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
        
        if chunk.choices and chunk.choices[0].finish_reason:
            yield "[STREAM_END]"


# -----------------------------------------------------------------
# 3. 核心业务逻辑 
# -----------------------------------------------------------------

def process_medical_analysis(request: AnalysisRequest) -> Union[AnalysisReport, StreamReport]:
    """
    核心分析函数：兼容同步和流式传输。
    
    Args:
        request: 包含原始文本和图片Base64编码的请求对象。
        
    Returns:
        AnalysisReport (同步模式) 或 Generator[str] (流式模式)。
    """
    
    if GLOBAL_VECTOR_STORE is None or GLOBAL_LLM is None or GLOBAL_ZHIPU_CLIENT is None:
        return AnalysisReport(structured_report="医疗分析服务未就绪，请检查初始化状态。", status="SERVICE_UNAVAILABLE")

    try:
        # 阶段 1 和 2 必须同步完成
        multimodal_description_block = _stage1_generate_description(GLOBAL_LLM, request.patient_text_data, request.image_base64)
        retrieved_context = _stage2_retrieve_context(GLOBAL_LLM, multimodal_description_block, GLOBAL_VECTOR_STORE)
        
        # 阶段 3: 根据模式选择同步或流式生成
        if request.stream:
            return _stage3_stream_generate_final_report(
                GLOBAL_ZHIPU_CLIENT, 
                request.patient_text_data, 
                multimodal_description_block, 
                retrieved_context
            )
        else:
            final_report_text = _stage3_sync_generate_final_report(
                GLOBAL_LLM, 
                request.patient_text_data, 
                multimodal_description_block, 
                retrieved_context
            )
            return AnalysisReport(structured_report=final_report_text, status="SUCCESS")
        
    except Exception as e:
        error_msg = f"系统内部错误，无法完成分析。详情: {type(e).__name__}: {str(e)}"
        print(f"❌ AI分析过程发生异常: {error_msg}")
        import traceback
        print(f"🔍 详细堆栈:\n{traceback.format_exc()}")
        return AnalysisReport(structured_report=error_msg, status="INTERNAL_ERROR")
