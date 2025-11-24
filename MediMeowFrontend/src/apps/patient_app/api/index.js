import axios from 'axios'
import { ElMessage } from 'element-plus'

// 1. 创建 axios 实例
const request = axios.create({
  // *** 保持 /api 代理路径，与 vite.config.js 配合使用 ***
  baseURL: '/api', 
  timeout: 5000
})

// === 🚀 核心修改：新增请求拦截器来附加 Token ===
request.interceptors.request.use(
  (config) => {
    // 自动从 localStorage 读取 token 并附加到请求头
    const token = localStorage.getItem('userToken');
    if (token) {
      // 附加 Authorization 头部。请确认后端是否要求 'Bearer ' 前缀
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);
// ===================================================


// 2. 响应拦截器
request.interceptors.response.use(
  (res) => {
    // 解构后端返回的数据结构
    const { base, data } = res.data
    
    // 如果 data 存在，返回 data 部分
    if (data) {
      return data 
    }
    
    // 如果 base 里有错误信息（根据实际情况调整判断逻辑）
    if (base && base.code !== '200' && base.code !== '0') {
      ElMessage.error(base.msg || '请求出错')
      return Promise.reject(new Error(base.msg))
    }

    // 针对某些没有 data 也没有 base 错误的情况，返回整个响应体
    return res.data
  }, 
  (err) => {
    console.error('API Error:', err)
    
    // === 增强错误处理：针对授权失败跳转或提示 ===
    if (err.response && (err.response.status === 401 || err.response.status === 403)) {
        // 如果后端返回 401/403，给出更明确的提示
        ElMessage.error('权限验证失败，请重新登录。');
        // 实际项目中，您可能需要在这里添加路由跳转到登录页面的逻辑
    } else {
        ElMessage.error(err.message || '网络请求失败');
    }
    // ===========================================
    
    return Promise.reject(err)
  }
)

// --- 3. 接口定义 (保持不变) ---

// 获取所有科室
export const getDepartments = () => {
  return request.get('/departments')
}

// 获取问卷详情
export const getQuestionnaire = (deptId) => {
  return request.get(`/questionnaires/${deptId}`)
}

// 提交问卷
export const submitQuestionnaire = (data) => {
  return request.post('/questionnaires/submit', data)
}

// 文件上传
export const uploadFile = (file) => {
  const formData = new FormData()
  formData.append('file', file) 
  
  return request.post('/questionnaires/upload', formData, {
    headers: { 
      'Content-Type': 'multipart/form-data' 
    }
  })
}