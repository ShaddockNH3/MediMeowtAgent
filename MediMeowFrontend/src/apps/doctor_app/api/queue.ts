// api/queue.ts
// 导入基础服务（从login.ts获取，确保路径正确）
import { service } from './login';

// 基础返回结构（所有接口通用的base层级）
export interface Base {
  code: string; // 接口状态码，成功值为'10000'
  msg: string;  // 接口返回消息
}

// ==========================
// 1. 患者队列接口相关类型与函数
// ==========================

/**
 * 队列接口返回类型（/doctor/queue）
 * 对应OpenAPI文档的返回结构：base + data.record_ids
 */
export interface DoctorQueueResponse {
  base: Base;
  data: {
    record_ids: string[]; // 待诊患者的记录ID列表
  };
}

/**
 * 获取待诊患者队列的record_ids
 * @param userId - 医生用户ID（必填，对应OpenAPI的user_id查询参数）
 * @returns 包含record_ids的响应数据
 */
export const getDoctorQueue = async (
  userId: string
): Promise<DoctorQueueResponse> => {
  // 从localStorage获取医生登录令牌
  const doctorToken = localStorage.getItem('doctorToken');
  
  // 调用队列接口，传递user_id查询参数和Authorization头
  return service.get('/doctor/queue', {
    params: { user_id: userId }, // 严格匹配OpenAPI的查询参数名
    headers: {
      'Authorization': `Bearer ${doctorToken}` // 严格匹配OpenAPI的Bearer Token格式
    }
  });
};

// ==========================
// 2. 患者详情接口相关类型与函数
// ==========================

/**
 * 患者详情接口返回类型（/doctor/patient/detail）
 * 用于获取单个患者的基本信息（姓名、性别、年龄、主诉等）
 */
export interface PatientDetailResponse {
  base: Base;
  data: {
    id: string;         // 患者实际ID
    name: string;       // 患者姓名
    gender: string;     // 性别（男/女）
    age: number;        // 年龄
    chiefComplaint: string; // 主诉
    waitTime?: string;  // 等待时间（可选字段，后端未返回则前端处理）
  };
}

/**
 * 根据record_id获取患者详情
 * @param recordId - 就诊记录ID（必填，对应接口的record_id查询参数）
 * @returns 包含患者基本信息的响应数据
 */
export const getPatientDetail = async (
  recordId: string
): Promise<PatientDetailResponse> => {
  // 从localStorage获取医生登录令牌
  const doctorToken = localStorage.getItem('doctorToken');
  
  // 调用患者详情接口，传递record_id查询参数和Authorization头
  return service.get(`/doctor/patient/detail`, {
    params: { record_id: recordId }, // 接口所需的查询参数
    headers: {
      'Authorization': `Bearer ${doctorToken}` // 严格匹配Bearer Token格式
    }
  });
};