import os
import base64
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_openai import ChatOpenAI
import config.config as config

def get_bge_embedding_model():
    """配置 BAAI/bge-small-zh 本地词嵌入模型 (零成本)"""
    model_name = config.BGE_EMBEDDING_MODEL_NAME
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': True}
    
    # 使用 HuggingFaceBgeEmbeddings
    return HuggingFaceBgeEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )

def get_glm4_llm():
    """配置GLM-4.1V-Thinking-Flash 模型"""
    return ChatOpenAI(
        model="glm-4.1v-thinking-flash",  
        temperature=config.TEMPERATURE,
        openai_api_base=config.GLM_API_BASE,
        openai_api_key=os.environ["GLM_API_KEY"],
        max_tokens=config.MAX_TOKENS
    )

def image_to_base64(image_path: str) -> str:
    """将图片文件转换为 Base64 字符串"""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"未找到图片文件: {image_path}")
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")
