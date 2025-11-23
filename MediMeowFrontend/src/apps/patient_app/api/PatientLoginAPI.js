// D:\code\ruangong\new\src\apps\patient_app\api\PatientLoginAPI.js
import axios from 'axios';

// 这个TOKEN暂时不会被用到，但我们先保留它
const APIFOX_AUTH_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjEsInVzZXJOYW1lIjoiYWRtaW4iLCJlbWFpbCI6ImFkbWluQGV4YW1wbGUuY29tIiwiaWF0IjoxNzE2NDI1NjY0LCJleHAiOjE3NDc5NjE2NjR9.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c';

const service = axios.create({
  // 关键点1: 直接使用后端 IP 地址，绕开 Vite 代理
  baseURL: 'http://124.221.70.136:11391', 
  timeout: 10000,
});

// 请求拦截器
service.interceptors.request.use(
  (config) => {
    // 关键点2: 自动将 POST 请求的数据转换为 FormData
    if (config.method === 'post' && config.data) {
      const formData = new FormData();
      for (const key in config.data) {
        if (Object.prototype.hasOwnProperty.call(config.data, key)) {
          formData.append(key, config.data[key]);
        }
      }
      config.data = formData;
    }

    // ⚡⚡⚡ 最终解决方案：注释掉以下代码块 ⚡⚡⚡
    // 这就是导致CORS预检请求失败的根源。
    // 注释掉它之后，请求就会变为“简单请求”，不再触发OPTIONS预检。
    /*
    if (APIFOX_AUTH_TOKEN) {
      config.headers['Apifox-Auth'] = APIFOX_AUTH_TOKEN;
    }
    */
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器 (保持不变)
service.interceptors.response.use(
  (response) => {
    console.log('后端原始响应:', response.data); 
    return response.data; 
  },
  (error) => {
    console.error('API 请求出错:', error.response || error.message);
    if (error.response && error.response.data) {
        return Promise.reject(error.response.data);
    }
    return Promise.reject(error);
  }
);

// 登录接口
export const login = (data) => {
  // 处理字段名映射 (从 form 的 email 映射到 api 的 phone_number)
  const apiData = {
    phone_number: data.email,
    password: data.password
  };
  return service.post('/user/login', apiData);
};

// 注册接口
export const register = (data) => {
  // 同样处理字段名映射
  const apiData = {
    phone_number: data.email,
    password: data.password
  };
  return service.post('/user/register', apiData);
};

// 导出 service 实例，供其他模块复用
export { service };