import { service } from './login';

// 基础响应结构（接口文档的 base 层级）
interface Base {
  code: string; // 成功标识为 '10000'
  msg: string;
}

// 用户信息类型（与接口字段一致）
export interface User {
  id: string;
  phone_number: string;
  username: string;
  created_at: string;
  updated_at: string;
  deleted_at?: string;
}

// AI结果类型（与接口字段一致）
export interface KeyInfo {
  chief_complaint: string;
  key_symptoms: string;
  image_summary?: string;
  important_notes: string;
}

export interface AiResult {
  submission_id: string;
  is_department: boolean;
  key_info: KeyInfo;
}

// 数据层级结构（接口文档的 data 层级）
interface Data {
  user: User;
  ai_result: AiResult;
}

/**
 * 病情摘要接口响应类型（完全匹配接口文档的嵌套结构：base + data）
 */
export interface SummaryResponse {
  base: Base;
  data: Data;
}

/**
 * 获取病情摘要（路径参数、请求头均符合接口要求）
 * @param recordId - 待诊记录ID（路径参数，与接口的 `in: path` 一致）
 * @returns 嵌套结构的响应数据
 */
export const getDiseaseSummary = async (recordId: string): Promise<SummaryResponse> => {
  return service.get(`/doctor/summary/${recordId}`);
};