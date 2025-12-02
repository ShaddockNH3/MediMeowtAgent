<template>
  <!-- 模板部分保持不变 -->
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
        <button type="submit" :disabled="loading" class="login-btn">
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>
      <p class="error-msg" v-if="errorMsg">{{ errorMsg }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
// 脚本部分保持不变
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { doctorLogin } from '../api/login';
import type { LoginResponse } from '../api/login';

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
    const res = await doctorLogin(username.value.trim(), password.value.trim()) as LoginResponse;

    if (res.base.code === '10000' && res.data.token) {
      localStorage.setItem('doctorToken', res.data.token);
      if (res.data.doctor) {
        localStorage.setItem('doctorInfo', JSON.stringify(res.data.doctor));
      }
      router.push('/doctor');
    } else {
      errorMsg.value = res.base.msg || '登录失败，请检查账号密码';
    }
  } catch (error: any) {
    console.error('登录请求失败:', error);
    errorMsg.value = error.base?.msg || '网络异常，请稍后重试';
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
/* 背景色与医生主页/待诊列表保持一致，增强风格统一性 */
.doctor-login {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5fafe 0%, #eaf6fa 100%);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  padding: 20px;
}

/* 登录卡片样式优化：立体+现代感 */
.login-card {
  width: 380px;
  padding: 36px 32px;
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  border: 1px solid #f0f5ff;
  position: relative;
  overflow: hidden;
  /* 新增：确保内部元素不会超出卡片（可选） */
  box-sizing: border-box;
}

/* 卡片顶部渐变装饰条，增强细节 */
.login-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(90deg, #3b82f6, #60a5fa);
}

/* 标题样式优化：专业+醒目 */
.login-card h2 {
  font-size: 24px;
  color: #1e293b;
  text-align: center;
  margin: 0 0 32px;
  font-weight: 600;
  position: relative;
}

/* 标题下方小横线，增强视觉焦点 */
.login-card h2::after {
  content: '';
  display: block;
  width: 60px;
  height: 3px;
  background-color: #3b82f6;
  margin: 12px auto 0;
  border-radius: 2px;
}

/* 表单项样式优化 */
.form-item {
  margin-bottom: 24px;
}

.form-item label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

/* 输入框样式增强：修复宽度溢出问题 */
.form-item input {
  width: 100%;
  padding: 14px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 15px;
  color: #1e293b;
  transition: all 0.3s ease;
  background-color: #f8fafc;
  /* 核心修改：盒模型改为border-box，padding不会撑大宽度 */
  box-sizing: border-box;
}

/* 输入框聚焦效果 */
.form-item input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  background-color: #ffffff;
}

/* 禁用状态样式优化 */
.form-item input:disabled {
  background-color: #f1f5f9;
  color: #94a3b8;
  cursor: not-allowed;
}

/* 登录按钮样式升级：更具交互感 */
.login-btn {
  width: 100%;
  padding: 14px;
  background: #3b82f6;
  color: #ffffff;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 16px;
  /* 按钮也统一盒模型（可选） */
  box-sizing: border-box;
}

/* 按钮禁用状态 */
.login-btn:disabled {
  background: #93c5fd;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 按钮hover效果 */
.login-btn:hover:not(:disabled) {
  background: #2563eb;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
}

/* 错误提示样式优化：更醒目且美观 */
.error-msg {
  margin-top: 0;
  font-size: 13px;
  color: #ef4444;
  text-align: center;
  padding: 8px;
  background-color: #fff1f0;
  border-radius: 6px;
  border: 1px solid #fecdd3;
}
</style>