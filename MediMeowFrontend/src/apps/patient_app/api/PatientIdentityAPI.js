// D:\code\ruangong\new\src\apps\patient_app\api\PatientIdentityAPI.js
import axios from 'axios'; // 确保你有一个配置好的 axios 实例
// 假设你有一个统一的 axios 服务实例，例如 src/api/request.js
// 如果没有，可以简单地在这里创建一个新的 axios 实例，或者从 PatientLoginAPI.js 导入 service。
// 为了演示，我们假设你有一个 service 实例从外部导入，或者在 PatientLoginAPI.js 定义的 service 可以复用。
// 如果是复用 PatientLoginAPI.js 中的 `service` 实例，那么导入路径为：
import { service } from './PatientLoginAPI.js'; // ⚡ 从同目录的 PatientLoginAPI 导入已配置的 service

// 定义病人身份信息录入接口
// ⚡ 注意：这里我暂时使用了一个占位符路径 '/patient/identity/submit'，
// ⚡ 你需要根据后端实际的身份证绑定或病人信息录入接口路径来替换它。
export const submitPatientIdentity = (data) => {
  return service.post('/patient/identity/submit', data);
  // 如果后端需要的是 /user/login 并且预期接收这些身份信息，则使用：
  // return service.post('/user/login', data);
};

// 未来也可以添加获取病人身份列表的接口等
// export const getPatientIdentities = () => {
//   return service.get('/patient/identities');
// };