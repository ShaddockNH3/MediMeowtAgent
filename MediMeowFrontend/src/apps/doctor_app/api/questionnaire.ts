import { service } from './login';

// 基础响应结构（与医生端其他接口保持一致，匹配接口文档的 base 层级）
interface Base {
  code: string; // 成功标识为 '10000'
  msg: string;
}

/**
 * 导入问卷接口响应类型（完全匹配接口文档的嵌套结构：base 层级）
 */
export interface ImportQuestionnaireResponse {
  base: Base;
}

/**
 * 导入问卷（完全符合接口文档要求）
 * @param file - 待导入的.xlsx问卷文件
 * @returns 嵌套结构的导入结果提示
 */
export const importQuestionnaire = async (file: File): Promise<ImportQuestionnaireResponse> => {
  const formData = new FormData();
  formData.append('questionnaire', file); // 参数名与接口文档一致：questionnaire

  // 复用service实例：自动携带Token、拼接baseURL，无需额外配置
  return service.post('/questionnaires/import', formData);
};