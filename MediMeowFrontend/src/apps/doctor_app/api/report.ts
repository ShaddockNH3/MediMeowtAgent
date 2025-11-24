import { service } from './login';

// 基础响应结构（接口文档的 base 层级，与医生端其他接口保持一致）
interface Base {
  code: string; // 成功标识为 '10000'
  msg: string;
}

// 请求参数类型（与接口文档完全一致：record_id + text，必填）
export interface SubmitReportParams {
  record_id: string;
  text: string;
}

// 响应类型（完全匹配接口文档的嵌套结构：仅包含 base 层级）
export interface SubmitReportResponse {
  base: Base;
}

/**
 * 提交诊断报告（完全符合接口文档要求）
 * @param params - 诊断参数（record_id + 诊断内容text）
 * @returns 嵌套结构的提交结果
 */
export const submitDiagnosisReport = async (
  params: SubmitReportParams
): Promise<SubmitReportResponse> => {
  // 1. 请求体格式：axios 自动将 params 转为 JSON，Content-Type 设为 application/json（符合接口要求）
  // 2. 认证：service 实例自动携带 Authorization 头（符合接口要求）
  // 3. 路径与方法：POST /doctor/report（符合接口要求）
  return service.post('/doctor/report', params);
};