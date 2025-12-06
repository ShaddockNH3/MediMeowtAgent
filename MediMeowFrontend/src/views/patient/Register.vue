<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'
import request from '../../api/request'

const router = useRouter()

const phone = ref('')
const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const errorMsg = ref('')

const handleRegister = async () => {
    if (!phone.value || !password.value) {
        errorMsg.value = '请输入手机号和密码'
        return
    }
    
    if (password.value !== confirmPassword.value) {
        errorMsg.value = '两次输入的密码不一致'
        return
    }
    
    if (phone.value.length !== 11) {
        errorMsg.value = '请输入有效的11位手机号'
        return
    }

    loading.value = true
    errorMsg.value = ''

    try {
        // Doc says Body, fetch test confirmed Form Data (x-www-form-urlencoded) works.
        const params = new URLSearchParams()
        params.append('phone_number', phone.value)
        params.append('password', password.value)
        
        await request.post('/user/register', params)
        alert('注册成功，请登录')
        router.push({ name: 'patient-login' })
    } catch (err) {
        console.error('Register Error:', err)
        errorMsg.value = err.response?.data?.base?.msg || err.message || '注册失败'
    } finally {
        loading.value = false
    }
}
</script>

<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header bg-green-600">
        <Icon icon="mdi:account-plus" class="header-icon" />
        <h1 class="text-2xl font-bold mt-4">用户注册</h1>
      </div>
      
      <div class="p-8">
        <div class="mb-4">
          <label class="block text-gray-700 mb-2">手机号</label>
          <input 
            v-model="phone"
            type="text" 
            class="form-input" 
            placeholder="请输入11位手机号"
            maxlength="11"
          >
        </div>
        
        <div class="mb-4">
          <label class="block text-gray-700 mb-2">设置密码</label>
          <input 
            v-model="password"
            type="password" 
            class="form-input" 
            placeholder="至少6位密码"
          >
        </div>

        <div class="mb-6">
            <label class="block text-gray-700 mb-2">确认密码</label>
            <input 
              v-model="confirmPassword"
              type="password" 
              class="form-input" 
              placeholder="再次输入密码"
            >
          </div>
        
        <div v-if="errorMsg" class="mb-4 text-red-500 text-sm text-center">
          {{ errorMsg }}
        </div>
        
        <button 
          class="login-btn bg-green-600 hover:bg-green-700" 
          :disabled="loading"
          @click="handleRegister"
        >
          {{ loading ? '注册中...' : '立即注册' }}
        </button>
        
        <div class="mt-4 text-center">
            <span class="text-gray-500">已有账号？</span>
            <router-link :to="{ name: 'patient-login' }" class="text-green-600 font-bold hover:underline">
                去登录
            </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  background: #F0FDF4;
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
