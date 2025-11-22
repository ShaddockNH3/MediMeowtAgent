# config.py

import os
from dotenv import load_dotenv

# 加载 .env 文件
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env')
load_dotenv(dotenv_path=dotenv_path)

# ==========================
# API 配置
# =========================================================

# GLM-4.1V-Thinking-Flash 配置
GLM_API_BASE = "https://open.bigmodel.cn/api/paas/v4/"

# --- 词嵌入模型配置 ---
BGE_EMBEDDING_MODEL_NAME = "BAAI/bge-small-zh"

# ==========================
# 路径配置
# ==========================

# 获取 zhipuGLM 模块的根目录
_MODULE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 存放 TXT 病历文件的文件夹
DOCS_DIRECTORY = os.path.join(_MODULE_DIR, "medical_docs")

# 向量数据库存储路径
CHROMA_PERSIST_DIR = os.path.join(_MODULE_DIR, "chroma_db_medical")

# 默认测试图片路径
DEFAULT_IMAGE_PATH = os.path.join(_MODULE_DIR, "pic", "tongue_sample.png")

# LLM 参数
MAX_TOKENS = 2048
TEMPERATURE = 0.0
