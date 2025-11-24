// 文件路径: src/apps/patient_app/api/PatientMyPageAPI.js

// 同样，我们复用已配置好的 service 实例
import { service } from './PatientLoginAPI.js';

/**
 * @description 获取当前登录用户的信息
 * @returns {Promise}
 */
export const getUserInfo = () => {
  // 根据接口文档，这是一个 GET 请求到 /user/info
  // Authorization 头会被我们之前写的请求拦截器自动加上
  return service.get('/user/info');
};