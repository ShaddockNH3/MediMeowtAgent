import sys
import os
import base64
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import grpc
import medical_ai_pb2 as pb2
import medical_ai_pb2_grpc as pb2_grpc

def get_fake_request_data(stream_mode: bool, patient_dept: str):
    """使用假的患者数据和图片进行测试"""
    # 假患者文本数据
    patient_text_data = """
    **患者基本信息**
    姓名：测试患者
    性别：女
    年龄：25 岁
    职业：测试员
    身高：165 cm
    体重：60 kg
    BMI指数：约 22.0
    过敏史：无
    既往病史：无特殊说明

    **主诉与现病史**
    主诉：测试症状。
    症状描述：这是一个测试案例，用于验证系统功能。
    """
    
    # 使用假的Base64图片数据（一个小的透明PNG）
    fake_image_base64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    print(f"✅ 使用假图片数据 (Base64长度: {len(fake_image_base64)} 字符)")
    
    return pb2.AnalysisRequest(
        patient_text_data=patient_text_data,
        image_base64=fake_image_base64,
        stream=stream_mode,
        patient_department=patient_dept
    )

def sync_call(patient_dept: str):
    print("\n" + "="*50)
    print(f"【同步调用测试】病人选择科室：{patient_dept}")
    print("="*50)
    
    with grpc.insecure_channel('127.0.0.1:50051') as channel:
        stub = pb2_grpc.MedicalAIServiceStub(channel)
        request = get_fake_request_data(stream_mode=False, patient_dept=patient_dept)
        response_iterator = stub.ProcessMedicalAnalysis(request)
        
        for response_chunk in response_iterator:
            if response_chunk.is_end:
                # 同步：bytes→Protobuf对象（反序列化）
                sync_report = pb2.AnalysisReport.FromString(response_chunk.chunk_data)
                if sync_report.status == "SUCCESS":
                    # 报告是UTF-8字符串，直接打印
                    print("✅ 同步调用成功，完整报告：")
                    print(sync_report.structured_report)
                else:
                    print(f"❌ 同步调用失败")
                    print(f"   状态: {sync_report.status}")
                    print(f"   消息: {sync_report.message}")
                    if sync_report.structured_report:
                        print(f"   详情: {sync_report.structured_report}")
                break

def stream_call(patient_dept: str):
    print("\n" + "="*50)
    print(f"【流式调用测试】病人选择科室：{patient_dept}")
    print("="*50)
    
    with grpc.insecure_channel('127.0.0.1:50051') as channel:
        stub = pb2_grpc.MedicalAIServiceStub(channel)
        request = get_fake_request_data(stream_mode=True, patient_dept=patient_dept)
        response_iterator = stub.ProcessMedicalAnalysis(request)
        
        print("📥 开始接收流式数据：")
        for response_chunk in response_iterator:
            # 流式：bytes→UTF-8字符串
            chunk_str = response_chunk.chunk_data.decode('utf-8')
            if chunk_str == "[STREAM_END]":
                print("\n📥 流式接收完毕（收到结束标记）")
                break
            print(f"[流式chunk] {chunk_str}", end="")
            if not response_chunk.is_end:
                print("\n" + "-"*30)

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🌟 医疗AI服务 gRPC 客户端测试（使用假数据）")
    print("="*80)
    
    # 测试 1: 同步调用 + 正确科室
    sync_call(patient_dept="耳鼻喉科")
    
    # 测试 2: 流式调用 + 正确科室
    # stream_call(patient_dept="耳鼻喉科")
    
    # 测试 3: 同步调用 + 错误科室
    # sync_call(patient_dept="内科")
    
    # 测试 4: 流式调用 + 错误科室
    # stream_call(patient_dept="内科")
    
    print("\n" + "="*80)
    print("✅ 测试完成")
    print("="*80)