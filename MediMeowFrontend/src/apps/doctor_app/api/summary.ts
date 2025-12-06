// summary.ts（保持不变，完全符合文档）
import { service } from './login';

// 基础响应结构
interface Base {
  code: string;
  msg: string;
}

// 用户信息类型
export interface User {
  id: string;
  phone_number: string;
  username: string;
  created_at: string;
  updated_at: string;
  deleted_at?: string;
}

// AI关键信息类型
export interface KeyInfo {
  chief_complaint: string;
  key_symptoms: string;
  image_summary?: string;
  important_notes: string;
}

// AI结果类型
export interface AiResult {
  submission_id: string;
  is_department: boolean;
  key_info: KeyInfo;
}

// 数据层级结构
interface Data {
  user: User;
  ai_result: AiResult;
}

// 病情摘要接口响应类型
export interface SummaryResponse {
  base: Base;
  data: Data;
}

// 获取病情摘要
export const getDiseaseSummary = async (recordId: string): Promise<SummaryResponse> => {
  const doctorToken = localStorage.getItem('doctorToken');
  return service.get(`/doctor/summary/${recordId}`, {
    headers: {
      'Authorization': doctorToken ? `Bearer ${doctorToken}` : ''
    }
  });
};