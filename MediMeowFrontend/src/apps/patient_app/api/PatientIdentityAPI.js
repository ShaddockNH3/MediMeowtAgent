// 文件路径: src/apps/patient_app/api/PatientIdentityAPI.js
import { service } from './PatientLoginAPI.js'; 

// 定义病人身份信息绑定接口
export const submitPatientIdentity = (data) => {
  // 💡 核心修改：接口路径更新为 /user/bind
  return service.post('/user/bind', data);
};