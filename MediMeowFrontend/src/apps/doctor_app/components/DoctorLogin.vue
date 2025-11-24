<template>
  <!-- 模板部分保持不变，无需修改 -->
  <div class="doctor-login">
    <div class="login-card">
      <h2>医生登录</h2>
      <form @submit.prevent="handleLogin">
        <div class="form-item">
          <label>用户名</label>
          <input 
            type="text" 
            v-model="username" 
            placeholder="请输入用户名（示例：张医生）" 
            required
            :disabled="loading"
          >
        </div>
        <div class="form-item">
          <label>密码</label>
          <input 
            type="password" 
            v-model="password" 
            placeholder="请输入密码（示例：doctor123）" 
            required
            :disabled="loading"
          >
        </div>
        <button type="submit" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>
      <p class="error-msg" v-if="errorMsg">{{ errorMsg }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { doctorLogin } from '../api/login';
import type { LoginResponse } from '../api/login'; // 类型导入保持不变

const username = ref('');
const password = ref('');
const loading = ref(false);
const errorMsg = ref('');
const router = useRouter();

const handleLogin = async () => {
  errorMsg.value = '';
  
  if (!username.value.trim() || !password.value.trim()) {
    errorMsg.value = '用户名和密码不能为空';
    return;
  }

  try {
    loading.value = true;
    // 调用修正后的 API（参数自动拼到 URL query，响应是嵌套结构）
    const res = await doctorLogin(username.value.trim(), password.value.trim()) as LoginResponse;

    // 核心修改：按接口文档的嵌套结构解析响应
    if (res.base.code === '10000' && res.data.token) {
      // 从 data 层级获取 token 和 doctor 信息
      localStorage.setItem('doctorToken', res.data.token);
      if (res.data.doctor) {
        localStorage.setItem('doctorInfo', JSON.stringify(res.data.doctor));
      }
      router.push('/doctor'); // 登录成功跳主页
    } else {
      // 从 base 层级获取错误信息
      errorMsg.value = res.base.msg || '登录失败，请检查账号密码';
    }
  } catch (error: any) {
    console.error('登录请求失败:', error);
    // 适配后端返回的错误结构（优先取 base.msg，无则显示通用提示）
    errorMsg.value = error.base?.msg || '网络异常，请稍后重试';
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
/* 样式部分保持不变，无需修改 */
.doctor-login {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f7fa;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.login-card {
  width: 350px;
  padding: 24px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.form-item {
  margin-bottom: 20px;
}

.form-item label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: #333;
}

.form-item input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.form-item input:focus {
  outline: none;
  border-color: #409eff;
}

button {
  width: 100%;
  padding: 12px;
  background: #409eff;
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.3s;
}

button:disabled {
  background: #a0cfff;
  cursor: not-allowed;
}

button:hover:not(:disabled) {
  background: #3086e0;
}

.error-msg {
  margin-top: 12px;
  font-size: 13px;
  color: #f56c6c;
  text-align: center;
}
</style>