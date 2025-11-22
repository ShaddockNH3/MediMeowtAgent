# gRPC Server 与 AI 服务对接完成说明

## 配置步骤

1. **环境准备**：
   - 安装 Python 3.12
   - 创建虚拟环境：`python -m venv .venv`
   - 激活虚拟环境：`.\.venv\Scripts\Activate.ps1`

2. **依赖安装**：
   - 配置 pip 镜像：`pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple`
   - 安装依赖：`pip install grpcio grpcio-tools zhipuai langchain-core langchain-community chromadb`

3. **API 密钥配置**：
   - 在 `config/config.py` 中设置 `os.environ["GLM_API_KEY"] = "your_api_key_here"`
   - 获取密钥：访问 [智谱 AI 开放平台](https://bigmodel.cn/login?redirect=%2Fusercenter%2Fproj-mgmt%2Fapikeys)

4. **环境变量**：
   - 设置 Hugging Face 镜像：`$env:HF_ENDPOINT = "https://hf-mirror.com"`

## 测试方法

### 测试之前

首先在 connect 文件夹下创建一个 pic 文件夹并放一张图。

### 启动服务端
```bash
cd MediMeowAI/connect
python server.py
```

### 测试客户端
```bash
cd MediMeowAI/connect
python client.py
```

测试场景：
- 同步调用 + 正确科室（耳鼻喉科）

## 注意事项

- 首次运行需下载模型，可能需要几分钟
- 图片需为 Base64 格式（`data:image/jpeg;base64,...`）
- 支持耳鼻喉科和呼吸科科室验证

详细文档参考：`zhipuGLM/docs/对接文档.md` 和 `zhipuGLM/docs/配置文档.md`
