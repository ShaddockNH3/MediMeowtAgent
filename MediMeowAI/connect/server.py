import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))  # 添加 connect 目录到路径
import grpc
from concurrent import futures
import time
import medical_ai_pb2 as pb2
import medical_ai_pb2_grpc as pb2_grpc

# 导入真实的AI服务
from zhipuGLM.service import (
    process_medical_analysis,
    initialize_service,
    AnalysisRequest as ServiceRequest,
    AnalysisReport as ServiceReport
)

class MedicalAIService(pb2_grpc.MedicalAIServiceServicer):
    def __init__(self):
        self.allowed_departments = ["耳鼻喉科", "呼吸科"]

    def ProcessMedicalAnalysis(self, request, context):
        patient_dept = request.patient_department
        print(f"📥 收到分析请求：科室={patient_dept}, 流式={request.stream}, 文本长度={len(request.patient_text_data)}, 图片Base64长度={len(request.image_base64)}")
        
        # 1. 科室打回逻辑
        if patient_dept not in self.allowed_departments:
            print(f"❌ 科室不匹配：{patient_dept} 不在允许列表 {self.allowed_departments} 中")
            if request.stream:
                # 流式：字符串→bytes（UTF-8编码）
                error_msg = f"[ERROR] 科室不匹配：您选择的「{patient_dept}」无法处理，请重新挂号（仅支持{self.allowed_departments}）"
                yield pb2.StreamChunk(
                    chunk_data=error_msg.encode('utf-8'),  # 字符串→bytes
                    is_end=True
                )
            else:
                # 同步：Protobuf对象→bytes（序列化）
                error_report = pb2.AnalysisReport(
                    status="DEPARTMENT_MISMATCH",
                    message=f"您选择的「{patient_dept}」无法处理，请重新挂号"
                )
                yield pb2.StreamChunk(
                    chunk_data=error_report.SerializeToString(),  # 序列化→bytes
                    is_end=True
                )
            return

        # 2. 调用真实的AI服务
        try:
            print("🤖 正在调用AI分析服务...")
            # 构建服务请求
            service_request = ServiceRequest(
                patient_text_data=request.patient_text_data,
                image_base64=request.image_base64,
                stream=request.stream
            )
            
            # 调用AI分析服务
            result = process_medical_analysis(service_request)
            print("✅ AI分析服务调用完成")
            
            # 3. 同步/流式返回（均用bytes）
            if not request.stream:
                print("📤 返回同步结果")
                # 同步模式：返回完整报告
                if isinstance(result, ServiceReport):
                    print(f"📋 报告状态: {result.status}, 报告长度: {len(result.structured_report)}")
                    sync_response = pb2.AnalysisReport(
                        structured_report=result.structured_report,
                        status=result.status,
                        message="AI分析完成"
                    )
                    yield pb2.StreamChunk(
                        chunk_data=sync_response.SerializeToString(),
                        is_end=True
                    )
                else:
                    # 服务返回错误
                    print("⚠️ AI服务返回类型异常")
                    error_response = pb2.AnalysisReport(
                        structured_report="",
                        status="INTERNAL_ERROR",
                        message="AI服务返回类型异常"
                    )
                    yield pb2.StreamChunk(
                        chunk_data=error_response.SerializeToString(),
                        is_end=True
                    )
            else:
                print("📤 开始流式传输")
                # 流式模式：逐块传输
                chunk_count = 0
                for chunk in result:
                    chunk_count += 1
                    if chunk == "[STREAM_END]":
                        print(f"🏁 流式传输结束，总块数: {chunk_count}")
                        # 结束标记
                        yield pb2.StreamChunk(
                            chunk_data=chunk.encode('utf-8'),
                            is_end=True
                        )
                        break
                    else:
                        # 正常数据块
                        print(f"📦 发送数据块 {chunk_count}: {len(chunk)} 字符")
                        yield pb2.StreamChunk(
                            chunk_data=chunk.encode('utf-8'),
                            is_end=False
                        )
                        
        except Exception as e:
            # 处理异常
            error_msg = f"AI服务调用失败: {str(e)}"
            print(f"❌ 错误: {error_msg}")
            print(f"🔍 异常类型: {type(e).__name__}")
            import traceback
            print(f"🔍 堆栈跟踪:\n{traceback.format_exc()}")
            # 截取错误消息的前200个字符，避免消息过长
            short_error_msg = str(e)[:200] + "..." if len(str(e)) > 200 else str(e)
            error_response = pb2.AnalysisReport(
                structured_report="",
                status="INTERNAL_ERROR",
                message=f"AI分析失败: {short_error_msg}"
            )
            yield pb2.StreamChunk(
                chunk_data=error_response.SerializeToString(),
                is_end=True
            )

def run_server():
    # 初始化AI服务（加载模型和向量数据库）
    print("🔄 正在初始化AI服务（加载LLM和RAG索引）...")
    initialize_service()
    print("✅ AI服务初始化完成")
    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_MedicalAIServiceServicer_to_server(MedicalAIService(), server)
    server.add_insecure_port('127.0.0.1:50051')
    server.start()
    print(f"🚀 gRPC服务端已启动：本地回环（127.0.0.1:50051），等待客户端连接...")
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        print("🛑 收到中断信号，正在停止服务器...")
        server.stop(0)
        print("✅ 服务器已停止")

if __name__ == "__main__":
    run_server()