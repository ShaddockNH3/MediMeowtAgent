import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
import config.config as config
import utils.utils as utils

def build_or_load_rag_index():
    """加载或从文档构建向量数据库"""
    bge_embeddings = utils.get_bge_embedding_model()
    
    # 1. 尝试加载现有数据库
    if os.path.exists(config.CHROMA_PERSIST_DIR):
        print("--- 正在加载现有 Chroma 数据库... ---")
        return Chroma(persist_directory=config.CHROMA_PERSIST_DIR, embedding_function=bge_embeddings)

    # 2. 检查文档目录
    if not os.path.exists(config.DOCS_DIRECTORY):
        print(f"--- 错误：请创建 {config.DOCS_DIRECTORY} 文件夹，并放入您的医疗TXT文件 ---")
        return None
    
    # 3. 构建新数据库
    print("--- 正在加载文档并构建向量数据库... ---")
    loader = DirectoryLoader(
        config.DOCS_DIRECTORY, 
        glob="**/*.txt", 
        loader_cls=TextLoader, 
        loader_kwargs={'encoding': 'utf-8'}
    )
    documents = loader.load()
    
    # 分块
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, length_function=len)
    chunks = text_splitter.split_documents(documents)
    
    # 存入 Chroma
    vectorstore = Chroma.from_documents(
        documents=chunks, 
        embedding=bge_embeddings, 
        persist_directory=config.CHROMA_PERSIST_DIR
    )
    print(f"--- 数据库构建完成！文档块数量: {len(chunks)} ---")
    return vectorstore
