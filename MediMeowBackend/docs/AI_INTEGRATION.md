# 后端对接 AI 服务 - 快速上手指南

> 本文档面向**后端开发人员**，说明如何调用 AI 分析服务。配合 AI 团队的《对接文档.md》使用。

---

## 📌 一、快速理解：你要做什么？

```
用户提交问卷 → 后端接收 → 调用 AI 服务 → 获取分析结果 → 保存到数据库
                    ↑
                  你负责这里
```

**你的任务**：在已有的代码里，添加调用 AI 服务的逻辑。

**⚠️ 重要提示**：AI 分析通常需要 **1-2 分钟**，所以超时时间必须设置足够长（推荐 120 秒）！---

## 📋 二、需要修改的文件（只有 2 个）

| 文件 | 作用 | 需要做什么 |
|------|------|-----------|
| `.env` | 配置文件 | 添加 AI 服务地址 |
| `app/services/ai_service.py` | AI 调用逻辑 | 修改函数，调用 AI 服务 |

**不需要新建文件，不需要改其他代码！**

---

## 🚀 三、3 步完成对接

### 步骤 1：配置 AI 服务地址（1 分钟）

打开 `.env` 文件，在最后添加：

```env
# AI 服务配置
AI_SERVICE_URL=http://localhost:8080
AI_SERVICE_TIMEOUT=120
```

**说明**：
- `AI_SERVICE_URL`：AI 服务的地址（问 AI 团队要）
- `AI_SERVICE_TIMEOUT`：超时时间 120 秒（**AI 分析可能需要 1-2 分钟，必须设置足够长**）

---

### 步骤 2：安装 HTTP 客户端（1 分钟）

在终端运行：

```bash
pip install httpx
```

---

### 步骤 3：修改 `ai_service.py`（5 分钟）

打开 `app/services/ai_service.py`，找到 `analyze_questionnaire` 函数，用下面的代码**完全替换**：

```python
"""
AI 服务模块 - 调用 AI 分析问卷数据
"""
import json
import httpx
import os
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from config import settings


class AIService:
    @staticmethod
    async def analyze_questionnaire(
        questionnaire_data: Dict[str, Any],      # 问卷答案
        file_ids: Optional[List[str]] = None,    # 图片 ID 列表
        department_id: Optional[str] = None,     # 科室 ID
        db: Optional[Session] = None             # 数据库（用于读图片）
    ) -> Dict[str, Any]:
        """
        调用 AI 服务分析问卷
        
        返回格式：
        {
            "status": "SUCCESS",
            "is_department": true,
            "key_info": {
                "chief_complaint": "咳嗽",
                "key_symptoms": "持续咳嗽3天",
                "important_notes": "建议检查肺部"
            }
        }
        """
        
        print(f"[AI] 开始分析，科室: {department_id}")
        
        # 1. 准备数据
        payload = {
            "patient_text_data": json.dumps(questionnaire_data, ensure_ascii=False),
            "image_base64": "",  # 如果有图片，下面会填充
            "stream": False
        }
        
        # 2. 如果有图片，加载并转 Base64
        if file_ids and db:
            try:
                from app.models.questionnaire import UploadedFile
                import base64
                
                for file_id in file_ids:
                    file_record = db.query(UploadedFile).filter(
                        UploadedFile.id == file_id
                    ).first()
                    
                    if file_record and os.path.exists(file_record.file_path):
                        with open(file_record.file_path, "rb") as f:
                            img_data = base64.b64encode(f.read()).decode()
                            payload["image_base64"] = f"data:image/jpeg;base64,{img_data}"
                            break  # 暂时只支持一张图片
            except Exception as e:
                print(f"[AI] 图片加载失败: {e}")
        
        # 3. 调用 AI 服务（注意：AI 处理可能需要 1-2 分钟）
        try:
            async with httpx.AsyncClient(timeout=settings.AI_SERVICE_TIMEOUT) as client:
                print(f"[AI] 调用: {settings.AI_SERVICE_URL}，超时设置: {settings.AI_SERVICE_TIMEOUT}秒")
                print(f"[AI] ⏳ AI 分析中，预计需要 1-2 分钟，请耐心等待...")
                
                response = await client.post(
                    f"{settings.AI_SERVICE_URL}/api/analyze",
                    json=payload
                )
                
                if response.status_code != 200:
                    raise Exception(f"HTTP {response.status_code}")
                
                result = response.json()
                print(f"[AI] ✓ 成功，状态: {result.get('status')}")
                return result
        
        except httpx.TimeoutException:
            print(f"[AI] ✗ 超时（超过 {settings.AI_SERVICE_TIMEOUT} 秒）")
            print(f"[AI] 💡 提示：AI 分析需要较长时间，请在 .env 中增加 AI_SERVICE_TIMEOUT")
            return {"status": "ERROR", "is_department": True, "key_info": {
                "chief_complaint": "AI 服务超时",
                "key_symptoms": "",
                "important_notes": "AI 分析时间较长，请增加超时设置后重试"
            }}
        
        except Exception as e:
            print(f"[AI] 失败: {e}")
            return {"status": "ERROR", "is_department": True, "key_info": {
                "chief_complaint": "AI 服务不可用",
                "key_symptoms": "",
                "important_notes": "请稍后重试"
            }}
```

**完成！** 现在你的后端可以调用 AI 服务了。

---

## ✅ 四、测试对接是否成功

### 测试 1：检查 AI 服务是否启动

```bash
curl http://localhost:8080/health
```

**期望结果**：返回 `{"status": "healthy"}`

**如果失败**：联系 AI 团队，确认服务已启动。

---

### 测试 2：提交问卷测试

使用 Postman 或 curl：

```bash
curl -X POST http://localhost:8000/questionnaires/submit \
  -H "Authorization: Bearer <你的token>" \
  -H "Content-Type: application/json" \
  -d '{
    "questionnaire_id": "问卷ID",
    "department_id": "科室ID",
    "answers": {
      "q1": "咳嗽",
      "q2": ["乏力"]
    }
  }'
```

**查看后端日志**，应该看到：

```
[AI] 开始分析，科室: xxx
[AI] 调用: http://localhost:8080
[AI] 成功，状态: SUCCESS
```

---

## 🔧 五、常见问题

### Q1: `ModuleNotFoundError: No module named 'httpx'`

**原因**：没安装 httpx

**解决**：`pip install httpx`

---

### Q2: `Connection refused`

**原因**：AI 服务没启动

**解决**：

1. 确认 AI 服务已启动：`curl http://localhost:8080/health`
2. 检查 `.env` 中的 `AI_SERVICE_URL` 地址是否正确

---

### Q3: `Timeout`

**原因**：AI 分析需要时间（通常 1-2 分钟），超时时间设置太短

**解决**：

1. **增加超时时间**：`.env` 中改为 `AI_SERVICE_TIMEOUT=120`（推荐 120 秒）
2. 如果还超时，可以继续增加到 `180` 或 `300`
3. 超时时间必须大于 AI 实际处理时间
4. 如果经常超时，联系 AI 团队优化性能

---

### Q4: AI 服务返回错误

**查看日志**：后端日志会显示 AI 返回的错误信息

**解决**：联系 AI 团队，提供完整错误信息

---

## 📚 六、AI 接口规范（给 AI 团队看）

### AI 服务需要提供的接口

**接口地址**：`POST /api/analyze`

**请求格式**：

```json
{
  "patient_text_data": "{\"q1\": \"咳嗽\", \"q2\": [\"乏力\"]}",
  "image_base64": "data:image/jpeg;base64,/9j/4AAQ...",
  "stream": false
}
```

**响应格式**：

```json
{
  "status": "SUCCESS",
  "structured_report": "# 病历报告\n...",
  "is_department": true,
  "key_info": {
    "chief_complaint": "咳嗽",
    "key_symptoms": "持续咳嗽3天，伴有乏力",
    "image_summary": "舌苔略厚",
    "important_notes": "建议检查肺部"
  }
}
```

**状态码说明**：

| 状态码 | 说明 |
|--------|------|
| `SUCCESS` | 分析成功 |
| `SERVICE_UNAVAILABLE` | 服务不可用 |
| `INTERNAL_ERROR` | 内部错误 |

---

## 🎯 七、验收清单

完成以下所有项，说明对接成功：

- [ ] `.env` 已添加 `AI_SERVICE_URL`
- [ ] 已安装 `httpx`：`pip install httpx`
- [ ] `ai_service.py` 已更新为新代码
- [ ] AI 服务健康检查通过：`curl http://localhost:8080/health`
- [ ] 提交问卷，日志显示 `[AI] 成功`
- [ ] 数据库中 `questionnaire_submissions.ai_result` 有数据

---

## 📝 附录：完整的调用流程

```
1. 用户提交问卷
   ↓
2. questionnaire.py 的 submit_questionnaire() 函数接收
   ↓
3. 调用 AIService.analyze_questionnaire()
   ↓
4. ai_service.py 构造请求，发送 HTTP POST 到 AI 服务
   ↓
5. AI 服务分析并返回结果
   ↓
6. 保存 ai_result 到数据库
   ↓
7. 返回 record_id 给用户
```

---

**就这么简单！只需要 3 步，10 分钟完成对接。**
