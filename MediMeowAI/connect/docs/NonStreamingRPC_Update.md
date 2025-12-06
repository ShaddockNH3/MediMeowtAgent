# AI 端 gRPC 非流式更新说明

## 修改日期
2025年12月6日

## 修改内容

### 1. Proto 定义更新 (`medical_ai.proto`)
- **新增**：非流式（同步）RPC 方法 `ProcessMedicalAnalysisSync`
- **保留**：流式 RPC 方法 `ProcessMedicalAnalysis`（用于特殊场景）

```protobuf
service MedicalAIService {
  // 非流式（同步）接口 - 推荐使用
  rpc ProcessMedicalAnalysisSync (AnalysisRequest) returns (AnalysisReport);
  
  // 流式接口 - 保留用于特殊场景
  rpc ProcessMedicalAnalysis (AnalysisRequest) returns (stream StreamChunk);
}
```

### 2. Server 实现更新 (`server.py`)
- **新增**：`ProcessMedicalAnalysisSync` 方法实现
- **特性**：
  - 直接返回 `AnalysisReport` 对象（非流式）
  - 自动强制使用同步模式（`stream=False`）
  - 更清晰的错误处理

### 3. Service 逻辑更新 (`zhipuGLM/service.py`)
- **新增**：科室错误检测
  - 如果报告内容包含"科室选择错误，请重新选择"或"科室选择错误"
  - 返回 `status="DEPARTMENT_ERROR"`
  - 其他情况返回 `status="SUCCESS"`

### 4. 客户端更新 (`client.py`)
- **更新**：`sync_call` 函数使用新的非流式 RPC 方法
- **简化**：直接接收 `AnalysisReport` 对象，无需解析流式响应

## 状态码说明

| 状态码 | 说明 | 触发条件 |
|--------|------|----------|
| `SUCCESS` | 分析成功 | AI 正常完成分析且无科室错误 |
| `DEPARTMENT_ERROR` | 科室选择错误 | 报告内容包含"科室选择错误" |
| `INTERNAL_ERROR` | 内部错误 | 服务异常或其他错误 |
| `SERVICE_UNAVAILABLE` | 服务不可用 | AI 服务未初始化 |

## 使用示例

### Python 客户端（推荐）
```python
import grpc
import medical_ai_pb2 as pb2
import medical_ai_pb2_grpc as pb2_grpc

with grpc.insecure_channel('127.0.0.1:50051') as channel:
    stub = pb2_grpc.MedicalAIServiceStub(channel)
    request = pb2.AnalysisRequest(
        patient_text_data="患者信息...",
        image_base64="data:image/jpeg;base64,...",
        stream=False,  # 此字段在同步RPC中会被忽略
        patient_department="耳鼻喉科"
    )
    
    # 使用新的非流式方法
    response = stub.ProcessMedicalAnalysisSync(request)
    
    if response.status == "SUCCESS":
        print(response.structured_report)
    elif response.status == "DEPARTMENT_ERROR":
        print("科室选择错误，请重新选择")
    else:
        print(f"错误: {response.status} - {response.message}")
```

## 测试方法

1. **启动 AI 服务端**：
```bash
cd /mnt/e/desktop/github/MediMeowtAgent/MediMeowAI/connect
python3 server.py
```

2. **运行测试客户端**：
```bash
cd /mnt/e/desktop/github/MediMeowtAgent/MediMeowAI/connect
python3 client.py
```

## 兼容性说明

- **向后兼容**：保留了原有的流式 RPC 方法 `ProcessMedicalAnalysis`
- **推荐使用**：新的非流式方法 `ProcessMedicalAnalysisSync`
- **后端对接**：后端应优先使用 `ProcessMedicalAnalysisSync` 方法

## 注意事项

1. 修改 proto 后需要重新生成 Python 代码：
   ```bash
   python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. medical_ai.proto
   ```

2. 科室错误检测依赖于 AI 输出内容，确保 prompt 中包含明确的错误提示格式

3. 非流式方法更适合大多数场景，流式方法仅在需要实时反馈时使用
