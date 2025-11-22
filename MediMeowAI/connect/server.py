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
        # 1. 科室打回逻辑
        if patient_dept not in self.allowed_departments:
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
            # 构建服务请求
            service_request = ServiceRequest(
                patient_text_data=request.patient_text_data,
                image_base64=request.image_base64,
                stream=request.stream
            )
            
            # 调用AI分析服务
            result = process_medical_analysis(service_request)
            
            # 3. 同步/流式返回（均用bytes）
            if not request.stream:
                # 同步模式：返回完整报告
                if isinstance(result, ServiceReport):
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
                # 流式模式：逐块传输
                for chunk in result:
                    if chunk == "[STREAM_END]":
                        # 结束标记
                        yield pb2.StreamChunk(
                            chunk_data=chunk.encode('utf-8'),
                            is_end=True
                        )
                        break
                    else:
                        # 正常数据块
                        yield pb2.StreamChunk(
                            chunk_data=chunk.encode('utf-8'),
                            is_end=False
                        )
                        
        except Exception as e:
            # 处理异常
            error_msg = f"AI服务调用失败: {str(e)}"
            print(f"❌ 错误: {error_msg}")
            error_response = pb2.AnalysisReport(
                structured_report="",
                status="INTERNAL_ERROR",
                message=error_msg
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
        server.stop(0)

if __name__ == "__main__":
    run_server()