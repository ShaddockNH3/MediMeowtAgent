// 文件路径: src/apps/patient_app/api/PatientLoginAPI.js
import axios from 'axios';

const service = axios.create({
  baseURL: '/api', 
  timeout: 10000,
});

// 请求拦截器
service.interceptors.request.use(
  (config) => {
    // 💡 核心修改：自动从 localStorage 读取 token 并附加到请求头
    const token = localStorage.getItem('userToken');
    if (token) {
      // 'Bearer ' 是 OAuth 2.0 规范，请根据后端要求确认是否需要
      config.headers['Authorization'] = `Bearer ${token}`;
    }

    // 关键点2: 自动将 POST 请求的数据转换为 FormData
    // 注意：如果 /user/bind 接口不接受 FormData，您可能需要为该接口单独处理或调整此逻辑
    if (config.method === 'post' && config.data) {
      const formData = new FormData();
      for (const key in config.data) {
        if (Object.prototype.hasOwnProperty.call(config.data, key)) {
          formData.append(key, config.data[key]);
        }
      }
      config.data = formData;
    }
    
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
  const apiData = {
    phone_number: data.email,
    password: data.password
  };
  return service.post('/user/login', apiData);
};

// 注册接口
export const register = (data) => {
  const apiData = {
    phone_number: data.email,
    password: data.password
  };
  return service.post('/user/register', apiData);
};

// 导出 service 实例，供其他模块复用
export { service };