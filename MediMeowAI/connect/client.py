import sys
import os
import base64
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import grpc
import medical_ai_pb2 as pb2
import medical_ai_pb2_grpc as pb2_grpc

def image_to_base64(image_path: str) -> str:
    """将图片转换为 Base64 编码字符串"""
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return f"data:image/png;base64,{encoded_string}"

def get_real_request_data(stream_mode: bool, patient_dept: str):
    """使用真实的患者数据和图片"""
    # 真实患者文本数据
    patient_text_data = """
    **患者基本信息**
    姓名：张同学
    性别：男
    年龄：20 岁
    职业：在校大学生
    身高：176 cm
    体重：85 kg
    BMI指数：约 27.4
    过敏史：无
    既往病史：无特殊说明

    **主诉与现病史**
    主诉：咽喉剧烈疼痛。
    症状描述：患者自述喉咙难受，伴有明显的痛感。
    """
    
    # 读取真实图片
    image_path = os.path.join(os.path.dirname(__file__), "pic", "tongue_sample.png")
    if not os.path.exists(image_path):
        print(f"错误：图片文件不存在 {image_path}")
        raise FileNotFoundError(f"图片文件不存在: {image_path}")
    
    image_base64 = image_to_base64(image_path)
    print(f"已加载图片：{image_path} (Base64长度: {len(image_base64)} 字符)")
    
    return pb2.AnalysisRequest(
        patient_text_data=patient_text_data,
        image_base64=image_base64,
        stream=stream_mode,
        patient_department=patient_dept
    )

def sync_call(patient_dept: str):
    print("\n" + "="*50)
    print(f"【同步调用测试 - 非流式RPC】病人选择科室：{patient_dept}")
    print("="*50)
    
    with grpc.insecure_channel('127.0.0.1:50051') as channel:
        stub = pb2_grpc.MedicalAIServiceStub(channel)
        request = get_real_request_data(stream_mode=False, patient_dept=patient_dept)
        
        # 使用新的非流式 RPC 方法
        sync_report = stub.ProcessMedicalAnalysisSync(request)
        
        if sync_report.status == "SUCCESS":
            print("同步调用成功，完整报告：")
            print(sync_report.structured_report)
        elif sync_report.status == "DEPARTMENT_ERROR":
            print(f"科室选择错误")
            print(f"   状态: {sync_report.status}")
            print(f"   消息: {sync_report.message}")
            print(f"   详情: {sync_report.structured_report}")
        else:
            print(f"同步调用失败")
            print(f"   状态: {sync_report.status}")
            print(f"   消息: {sync_report.message}")
            if sync_report.structured_report:
                print(f"   详情: {sync_report.structured_report}")

def stream_call(patient_dept: str):
    print("\n" + "="*50)
    print(f"【流式调用测试】病人选择科室：{patient_dept}")
    print("="*50)
    
    with grpc.insecure_channel('127.0.0.1:50051') as channel:
        stub = pb2_grpc.MedicalAIServiceStub(channel)
        request = get_real_request_data(stream_mode=True, patient_dept=patient_dept)
        response_iterator = stub.ProcessMedicalAnalysis(request)
        
        print("开始接收流式数据：")
        for response_chunk in response_iterator:
            # 流式：bytes→UTF-8字符串
            chunk_str = response_chunk.chunk_data.decode('utf-8')
            if chunk_str == "[STREAM_END]":
                print("\n流式接收完毕（收到结束标记）")
                break
            print(f"[流式chunk] {chunk_str}", end="")
            if not response_chunk.is_end:
                print("\n" + "-"*30)

if __name__ == "__main__":
    print("\n" + "="*80)
    print("医疗AI服务 gRPC 客户端测试（使用真实数据）")
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
    print("测试完成")
    print("="*80)