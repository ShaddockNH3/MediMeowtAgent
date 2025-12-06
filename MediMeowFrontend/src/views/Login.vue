<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { Icon } from '@iconify/vue'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const loading = ref(false)
const errorMsg = ref('')

const handleLogin = async () => {
  if (!username.value || !password.value) {
    errorMsg.value = '请输入用户名和密码'
    return
  }
  
  loading.value = true
  errorMsg.value = ''
  
  try {
    const success = await authStore.login(username.value, password.value)
    if (success) {
      router.push({ name: 'dashboard' })
    }
  } catch (err) {
    errorMsg.value = err.response?.data?.msg || err.message || '登录失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <Icon icon="mdi:doctor" class="header-icon" />
        <h1 class="text-2xl font-bold mt-4">医智 MedMind</h1>
        <p class="opacity-90 mt-2">安全登录您的专业医疗辅助平台</p>
      </div>
      
      <div class="p-8">
        <div class="mb-6">
          <label for="username" class="block text-gray-700 mb-2">用户名</label>
          <input 
            v-model="username"
            type="text" 
            id="username" 
            class="form-input" 
            placeholder="输入您的用户名"
            @keyup.enter="handleLogin"
          >
        </div>
        
        <div class="mb-6">
          <label for="password" class="block text-gray-700 mb-2">密码</label>
          <input 
            v-model="password"
            type="password" 
            id="password" 
            class="form-input" 
            placeholder="输入您的密码"
            @keyup.enter="handleLogin"
          >
        </div>
        
        <div v-if="errorMsg" class="mb-4 text-red-500 text-sm text-center">
          {{ errorMsg }}
        </div>
        
        <div class="flex justify-between items-center mb-6">
          <div>
            <input type="checkbox" id="remember" class="mr-2">
            <label for="remember" class="text-gray-600">记住我</label>
          </div>
          <a href="#" class="text-blue-600 hover:underline">忘记密码?</a>
        </div>
        
        <button 
          class="login-btn" 
          :disabled="loading"
          @click="handleLogin"
        >
          {{ loading ? '登录中...' : '登录系统' }}
        </button>
        
        <div class="mt-6 text-center text-gray-500 text-sm flex justify-center items-center">
          <Icon icon="mdi:shield-check" class="mr-1 inline-block" />
          医疗数据安全加密保障
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  background: #ECF0F1;
  min-height: 100vh;
  width: 100vw;
  display: flex;
  justify-content: center;
  align-items: center;
}

.login-card {
  width: 440px;
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
}

.login-header {
  background: #2C7DB1;
  padding: 30px;
  text-align: center;
  color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.header-icon {
  font-size: 48px;
}

.form-input {
  border: 1px solid #D1D5DB;
  border-radius: 6px;
  padding: 14px 16px;
  width: 100%;
  transition: border-color 0.3s;
}

.form-input:focus {
  border-color: #2C7DB1;
  outline: none;
  box-shadow: 0 0 0 3px rgba(44, 125, 177, 0.15);
}

.login-btn {
  background: #2C7DB1;
  color: white;
  padding: 14px;
  border-radius: 6px;
  font-weight: 600;
  letter-spacing: 0.5px;
  transition: background 0.3s;
  width: 100%;
  border: none;
  cursor: pointer;
}

.login-btn:hover:not(:disabled) {
  background: #24618d;
}

.login-btn:disabled {
  background: #7fb5d6;
  cursor: not-allowed;
}
</style>
