import axios from 'axios';

// 1. 修正响应类型：匹配接口文档的嵌套结构（base + data）
interface Doctor {
  id: string;
  username: string;
  department_name: string;
  created_at: string;
  updated_at: string;
  deleted_at?: string;
}

interface BaseResponse {
  code: string; // 成功标识为 '10000'
  msg: string;
}

// 完整响应类型（按接口文档定义）
export interface LoginResponse {
  base: BaseResponse; // 接口文档要求的base层级
  data: {             // 接口文档要求的data层级
    token: string;    // 医生登录凭证
    doctor: Doctor;   // 医生信息对象
  };
}

// 2. 创建axios实例（无需强制Content-Type，query参数无需特殊格式）
const service = axios.create({
  baseURL: '/api',
  timeout: 10000,
});

// 3. 请求拦截器：保留Token携带逻辑（登录后其他接口用）
service.interceptors.request.use(
  (config) => {
    const doctorToken = localStorage.getItem('doctorToken');
    if (doctorToken && config.headers) {
      config.headers['Authorization'] = `Bearer ${doctorToken}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 4. 响应拦截器：直接返回完整响应（匹配修正后的LoginResponse类型）
service.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API 请求失败:', error.response || error.message);
    if (error.response && error.response.data) {
      return Promise.reject(error.response.data);
    }
    return Promise.reject(error);
  }
);

// 5. 核心修正：登录参数放在 query 里（匹配接口文档的 in: query 要求）
export const doctorLogin = async (username: string, password: string): Promise<LoginResponse> => {
  // 第二个参数传空对象，第三个参数用 params 传递 query 参数
  return service.post('/doctor/login', {}, {
    params: { username, password } // 接口文档明确要求：username/password在query里
  });
};

export { service };