<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth' // Need to update auth to handle patient login or generic login
import { Icon } from '@iconify/vue'
import request from '../../api/request'

const router = useRouter()
const authStore = useAuthStore()

const phone = ref('')
const password = ref('')
const loading = ref(false)
const errorMsg = ref('')

const handleLogin = async () => {
    if (!phone.value || !password.value) {
        errorMsg.value = '请输入手机号和密码'
        return
    }

    loading.value = true
    errorMsg.value = ''

    try {
        // Doc says Body, fetch test confirmed Form Data works.
        const params = new URLSearchParams()
        params.append('phone_number', phone.value)
        params.append('password', password.value)
        
        const res = await request.post('/user/login', params)
        const data = res.data 
        
        authStore.token = data.data?.token || data.token
        localStorage.setItem('token', authStore.token)
        localStorage.setItem('role', 'patient')
        authStore.role = 'patient'
        
        // Fetch full user info (login response doesn't include birth/gender/etc)
        try {
            const infoRes = await request.get('/user/info')
            const userInfo = infoRes.data?.data || infoRes.data
            authStore.user = userInfo
            localStorage.setItem('user', JSON.stringify(userInfo))
        } catch (e) {
            console.warn('Failed to fetch user info, using login response', e)
            authStore.user = data.data?.user || data.user
            localStorage.setItem('user', JSON.stringify(authStore.user))
        }

        router.push({ name: 'patient-home' })
    } catch (err) {
        console.error('Login Error:', err)
        errorMsg.value = err.response?.data?.base?.msg || err.message || '登录失败'
    } finally {
        loading.value = false
    }
}
</script>

<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header bg-green-600">
        <Icon icon="mdi:account" class="header-icon" />
        <h1 class="text-2xl font-bold mt-4">患者登录</h1>
        <p class="opacity-90 mt-2">MediMeow 智能医疗</p>
      </div>
      
      <div class="p-8">
        <div class="mb-6">
          <label class="block text-gray-700 mb-2">手机号</label>
          <input 
            v-model="phone"
            type="text" 
            class="form-input" 
            placeholder="请输入手机号"
            maxlength="11"
          >
        </div>
        
        <div class="mb-6">
          <label class="block text-gray-700 mb-2">密码</label>
          <input 
            v-model="password"
            type="password" 
            class="form-input" 
            placeholder="请输入密码"
            @keyup.enter="handleLogin"
          >
        </div>
        
        <div v-if="errorMsg" class="mb-4 text-red-500 text-sm text-center">
          {{ errorMsg }}
        </div>
        
        <button 
          class="login-btn bg-green-600 hover:bg-green-700" 
          :disabled="loading"
          @click="handleLogin"
        >
          {{ loading ? '登录中...' : '立即登录' }}
        </button>
        
        <div class="mt-4 text-center">
            <span class="text-gray-500">还没有账号？</span>
            <router-link :to="{ name: 'patient-register' }" class="text-green-600 font-bold hover:underline">
                去注册
            </router-link>
        </div>
        
        <div class="mt-2 text-center">
             <router-link to="/" class="text-gray-400 text-sm hover:text-gray-600">返回首页</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Reuse styles from Doctor login but override colors where needed */
.login-container {
  background: #F0FDF4; /* Light green bg */
  min-height: 100vh;
  width: 100vw;
  display: flex;
  justify-content: center;
  align-items: center;
}

.login-card {
  width: 400px;
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
}

.login-header {
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
  padding: 12px 16px;
  width: 100%;
  transition: border-color 0.3s;
}

.form-input:focus {
  border-color: #10B981;
  outline: none;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.15);
}

.login-btn {
  color: white;
  padding: 12px;
  border-radius: 6px;
  font-weight: 600;
  width: 100%;
  border: none;
  cursor: pointer;
  transition: background 0.3s;
}

.login-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}
</style>
