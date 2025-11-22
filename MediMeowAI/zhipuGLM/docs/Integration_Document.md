## 📄 医疗 AI 分析服务 - Protobuf 对接文档

### 模块名称

`service.py`

### 目的

本模块提供核心 Python 接口，用于接收病人原始数据（文本 + 图片 Base64），执行三阶段 RAG 分析，并返回结构化的病历报告。**调用方（发送方）只需调用函数，无需关注内部的多模态或 RAG 逻辑。**

---

### 一、基础约定

1. **通信协议**：默认为 gRPC/HTTP，由 AI 接口对接人实现封装。
2. **数据格式**：传输的输入和输出均基于 Protobuf 消息体。

---

### 二、调用接口 (`service.process_medical_analysis`)

AI 服务端已封装一个统一函数，负责处理所有模式。

| 函数签名          | `process_medical_analysis(request) -> AnalysisReport 或 StreamReport`                        |
| :------------ | :------------------------------------------------------------------------------------------ |
| **Python 接口** | `process_medical_analysis(request: AnalysisRequest) -> Union[AnalysisReport, StreamReport]` |

#### 1. 输入消息 (`AnalysisRequest`)

此消息体由后端构建并发送。

| 字段名                 | 类型 (Protobuf) | 必填 | 示例值                            | 说明                            |
| :------------------ | :------------ | :- | :----------------------------- | :---------------------------- |
| `patient_text_data` | `string`      | 是  | `"主诉：喉咙疼痛，年龄：20..."`           | 包含主诉、BMI等原始文本信息。              |
| `image_base64`      | `string`      | 是  | `"data:image/jpeg;base64,..."` | 医疗影像图片（如舌苔）的 Base64 编码字符串。    |
| `stream`            | `bool`        | 否  | `True` / `False` (默认)          | `True`：要求流式返回；`False`：要求完整返回。 |

#### 2. 输出消息（同步模式 - `stream=False`）

| 字段名                 | 类型 (Protobuf) | 说明                                                             |
| :------------------ | :------------ | :------------------------------------------------------------- |
| `structured_report` | `string`      | 最终生成的结构化病历文本（Markdown 格式）。                                     |
| `status`            | `string`      | `SUCCESS`、`SERVICE_UNAVAILABLE` 或 `INTERNAL_ERROR` 等，用于判断业务状态。 |

#### 3. 输出消息（流式模式 - `stream=True`）

| 模式       | 返回类型                          | 说明                                              |
| :------- | :---------------------------- | :---------------------------------------------- |
| **流式**   | **Stream of `string` chunks** | 数据以字符串块（chunk）的形式连续返回。                          |
| **结束标记** | **`[STREAM_END]`**            | 当整个报告传输完毕后，会发送一个独立的字符串 `[STREAM_END]` 作为流的终止标记。 |

---

### 三、调用方（发送方）逻辑示例

这是负责发送数据的工程师需要实现的**核心逻辑**。

#### 1. 同步调用逻辑 (Sync Call)
```python
def process_sync(text_data: str, img_base64: str) -> str:
    """
    构造同步请求，并处理同步响应。
    """
    
    # 1. 构造请求，stream 字段为 False
    request = service.AnalysisRequest(
        patient_text_data=text_data,
        image_base64=img_base64,
        stream=False, # 核心：同步模式
    )

    # 2. 调用服务获取完整响应 (AnalysisReport 对象)
    response: service.AnalysisReport = CallPythonService(request)

    # 3. 检查状态
    if response.status == "SUCCESS":
        return response.structured_report
    else:
        # 对应 log.Error("分析失败: " + response.status)
        log_error(f"分析失败: {response.status}. 详情: {response.structured_report}")
        return ""
```


#### 2. 流式调用逻辑 (Stream Call)

```python
def process_stream(text_data: str, img_base64: str) -> None:
    """
    构造流式请求，并逐块处理返回数据。
    """
    
    # 1. 构造请求，stream 字段为 True
    request = service.AnalysisRequest(
        patient_text_data=text_data,
        image_base64=img_base64,
        stream=True, # 核心：流式模式
    )

    # 2. 调用服务获取 Stream/Generator
    stream: Generator[str, None, None] = CallPythonServiceStream(request)

    # 3. 逐块处理返回数据
    for chunk in stream:
        if chunk == "[STREAM_END]":
            break # 接收到结束标记
        
        # 对应 send_to_client(chunk)
        # 模拟将 chunk 发送到前端或后续处理逻辑
        print(chunk, end="", flush=True) 

    print("\n[Stream 接收完毕]")
```
