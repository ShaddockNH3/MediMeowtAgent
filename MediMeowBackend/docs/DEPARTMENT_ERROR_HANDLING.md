# 后端 DEPARTMENT_ERROR 状态处理说明

## 修改日期
2025年12月6日

## 修改内容

### 1. AI 服务层 (`app/services/ai_service.py`)

#### 修改点：`_call_grpc_ai_service` 方法

**变更前**：
- 使用流式 RPC 方法 `ProcessMedicalAnalysis`
- 仅处理 `SUCCESS` 状态

**变更后**：
- 使用非流式 RPC 方法 `ProcessMedicalAnalysisSync`
- 新增 `DEPARTMENT_ERROR` 状态处理

#### DEPARTMENT_ERROR 返回结构
```python
{
    "is_department": False,
    "key_info": {
        "chief_complaint": "科室选择错误",
        "key_symptoms": "<AI返回的详细错误信息>",
        "image_summary": "由于科室选择错误，未进行完整分析",
        "important_notes": "请重新选择正确的科室",
        "risk_level": "未评估",
        "suggested_department": "请根据症状重新选择"
    },
    "analysis_time": "0.1s",
    "model_version": "v1.0",
    "status": "department_error",
    "structured_report": "<AI返回的原始报告>",
    "error_message": "科室选择错误，请重新选择正确的科室"
}
```

### 2. 路由层 (`app/routers/questionnaire.py`)

#### 修改点：`get_submitted_questionnaires` 接口返回数据

**新增字段**：
- `ai_result.status` - AI 分析状态（`success` / `department_error` / `fallback`）
- `ai_result.error_message` - 当状态为 `department_error` 时的错误提示

#### 返回数据示例

**正常情况**：
```json
{
    "code": "00000",
    "msg": "获取成功",
    "data": {
        "total": 1,
        "records": [
            {
                "record_id": "xxx",
                "ai_result": {
                    "is_department": true,
                    "key_info": {
                        "chief_complaint": "咽喉疼痛",
                        "key_symptoms": "...",
                        ...
                    },
                    "status": "success"
                }
            }
        ]
    }
}
```

**科室错误情况**：
```json
{
    "code": "00000",
    "msg": "获取成功",
    "data": {
        "total": 1,
        "records": [
            {
                "record_id": "xxx",
                "ai_result": {
                    "is_department": false,
                    "key_info": {
                        "chief_complaint": "科室选择错误",
                        "key_symptoms": "根据您的症状，建议选择耳鼻喉科就诊",
                        ...
                    },
                    "status": "department_error",
                    "error_message": "科室选择错误，请重新选择正确的科室"
                }
            }
        ]
    }
}
```

### 3. Protobuf 定义更新

#### 文件：`app/services/grpc_client/medical_ai.proto`

**新增**：非流式 RPC 方法
```protobuf
service MedicalAIService {
  // 非流式（同步）接口 - 推荐使用
  rpc ProcessMedicalAnalysisSync (AnalysisRequest) returns (AnalysisReport);
  
  // 流式接口 - 保留用于特殊场景
  rpc ProcessMedicalAnalysis (AnalysisRequest) returns (stream StreamChunk);
}
```

**已重新生成**：
- `medical_ai_pb2.py`
- `medical_ai_pb2_grpc.py`

## 状态说明

| 状态值 | 说明 | is_department | 前端处理建议 |
|--------|------|---------------|--------------|
| `success` | AI 分析成功 | true/false | 正常显示分析结果 |
| `department_error` | 科室选择错误 | false | 提示用户重新选择科室，显示 AI 建议 |
| `fallback` | AI 服务降级 | true | 显示降级提示，引导人工判断 |

## 前端集成建议

### 1. 检测科室错误
```javascript
if (record.ai_result && record.ai_result.status === 'department_error') {
    // 显示科室选择错误提示
    showDepartmentError(record.ai_result.error_message);
    // 显示 AI 建议的科室
    showSuggestedDepartment(record.ai_result.key_info.key_symptoms);
}
```

### 2. UI 提示
- 错误标题：`record.ai_result.key_info.chief_complaint`（"科室选择错误"）
- 错误详情：`record.ai_result.key_info.key_symptoms`（AI 给出的建议）
- 操作按钮：提供"重新选择科室"按钮

### 3. 用户流程
1. 用户提交问卷到错误科室（例如内科）
2. AI 分析发现症状应该去耳鼻喉科
3. 返回 `status: "department_error"`
4. 前端提示："您选择的科室可能不匹配您的症状，建议选择耳鼻喉科就诊"
5. 用户可以重新提交到正确科室

## 测试方法

### 1. 启动 AI 服务端
```bash
cd /mnt/e/desktop/github/MediMeowtAgent/MediMeowAI/connect
python3 server.py
```

### 2. 启动后端服务
```bash
cd /mnt/e/desktop/github/MediMeowtAgent/MediMeowBackend
python run.py
```

### 3. 测试场景

**场景 1：正确科室**
- 提交咽喉疼痛症状到"耳鼻喉科"
- 预期：`status: "success"`, `is_department: true`

**场景 2：错误科室**
- 提交咽喉疼痛症状到"内科"
- 预期：`status: "department_error"`, `is_department: false`

## 兼容性说明

- ✅ 向后兼容：旧版本前端不会报错，只是不显示新增的错误提示
- ✅ 降级策略：AI 服务不可用时自动降级，返回 `status: "fallback"`
- ✅ 错误处理：所有异常都有捕获，不会影响主流程

## 注意事项

1. **数据库迁移**：无需数据库迁移，`ai_result` 字段为 JSON 类型，可直接存储新结构
2. **日志记录**：AI 服务调用失败会在控制台打印详细日志
3. **性能影响**：使用非流式 RPC 后响应速度略有提升（减少了流式传输开销）
4. **错误恢复**：用户重新提交到正确科室后，新的就诊记录会正常处理
