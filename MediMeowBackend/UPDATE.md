### AI 服务对接实现
- **通信协议**：使用 gRPC 协议与 MediMeowAI 服务通信，提供高性能、低延迟的数据传输
- **数据处理**：自动构造患者文本数据，包括基本信息、问卷答案和主诉提取
- **图片分析**：支持上传图片文件，转换为 Base64 格式传递给 AI 服务进行分析
- **降级策略**：当 AI 服务不可用时，提供模拟结果确保系统稳定性
- **支持科室**：目前支持耳鼻喉科和呼吸科的智能分析

### AI 分析流程
1. 用户提交问卷和图片
2. 后端构造结构化数据（患者信息、症状描述、图片 Base64）
3. 通过 gRPC 调用 AI 服务进行分析
4. AI 返回结构化报告（主诉、关键症状、图片总结、重要备注）
5. 后端保存分析结果并返回给前端

### 错误处理
- **超时处理**：AI 分析设置 120 秒超时
- **降级策略**：AI 服务不可用时返回预定义结果

## 测试流程

### 运行完整测试

#### 激活AI端虚拟环境并运行服务
```bash
cd MediMeowAI
venv\Scripts\activate
python ai.py
```

#### 激活后端虚拟环境并运行测试
```bash
cd MediMeowBackend
venv\Scripts\activate
python run.py
python test_complete.py
```

#### notes
- 先前 medimeow_db 和 medimoew_db 字段，因历史遗留问题，导致这两个字段都存在。本次更新的测试基于 medimeow_db 进行，已将所有 medimoew_db 替换为 medimeow_db。
- 阿里 zhipuai api密钥是 052301319 申请的，为了测试方便没有删除，如需要使用自己的密钥可自行替换。
- 如果使用 --not-required 导出的依赖文件单安装后出现问题，可以考虑删除虚拟环境使用 requirements-all.txt 再次安装。