<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { Icon } from '@iconify/vue'
import request from '../../api/request'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
    username: '',
    gender: '男',
    birth: '',
    ethnicity: '汉族',
    origin: ''
})

const loading = ref(false)
const errorMsg = ref('')

const handleBind = async () => {
    // Basic validation
    if (!form.value.username || !form.value.birth || !form.value.origin) {
        errorMsg.value = '请填写完整信息'
        return
    }

    loading.value = true
    errorMsg.value = ''

    try {
        // POST /user/bind
        // Converting to Form Data for consistency with Register/Login
        const params = new URLSearchParams()
        params.append('username', form.value.username)
        params.append('gender', form.value.gender)
        params.append('birth', form.value.birth)
        params.append('ethnicity', form.value.ethnicity)
        params.append('origin', form.value.origin)
        
        await request.post('/user/bind', params, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        })
        
        // On success, refresh user info or manually update store
        // We'll fetch updated info to be safe
        try {
           const res = await request.get('/user/info')
           authStore.user = res.data
           localStorage.setItem('user', JSON.stringify(res.data))
        } catch (e) {
           console.warn('Failed to refresh user info', e)
           // If fetch fails, at least update the username locally so UI looks okay
           authStore.user.username = form.value.username
           localStorage.setItem('user', JSON.stringify(authStore.user))
        }

        router.push({ name: 'patient-home' })
    } catch (err) {
        console.error(err)
        errorMsg.value = err.response?.data?.base?.msg || '提交失败，请重试'
    } finally {
        loading.value = false
    }
}
</script>

<template>
  <div class="bind-container">
    <div class="bind-card">
        <div class="bind-header bg-green-600">
            <Icon icon="mdi:card-account-details" class="text-4xl" />
            <h1 class="text-xl font-bold mt-2">完善实名信息</h1>
        </div>

        <div class="p-6">
            <div class="mb-4">
                <label class="block text-gray-700 text-sm font-bold mb-2">姓名</label>
                <input 
                    v-model="form.username"
                    type="text" 
                    class="form-input" 
                    placeholder="请输入真实姓名"
                >
            </div>

            <div class="mb-4">
                <label class="block text-gray-700 text-sm font-bold mb-2">性别</label>
                <div class="flex space-x-4">
                    <label class="flex items-center cursor-pointer">
                        <input type="radio" v-model="form.gender" value="男" class="mr-2">
                        <span>男</span>
                    </label>
                    <label class="flex items-center cursor-pointer">
                        <input type="radio" v-model="form.gender" value="女" class="mr-2">
                        <span>女</span>
                    </label>
                </div>
            </div>

            <div class="mb-4">
                <label class="block text-gray-700 text-sm font-bold mb-2">出生日期</label>
                <input 
                    v-model="form.birth"
                    type="date" 
                    class="form-input" 
                >
            </div>

            <div class="mb-4">
                <label class="block text-gray-700 text-sm font-bold mb-2">民族</label>
                <input 
                    v-model="form.ethnicity"
                    type="text" 
                    class="form-input" 
                    placeholder="例如：汉族"
                >
            </div>

            <div class="mb-6">
                <label class="block text-gray-700 text-sm font-bold mb-2">籍贯</label>
                <input 
                    v-model="form.origin"
                    type="text" 
                    class="form-input" 
                    placeholder="省/市/区"
                >
            </div>

            <div v-if="errorMsg" class="mb-4 text-red-500 text-sm text-center">
                {{ errorMsg }}
            </div>

            <button 
                @click="handleBind"
                :disabled="loading"
                class="w-full bg-green-600 text-white font-bold py-3 rounded-lg hover:bg-green-700 transition disabled:opacity-50"
            >
                {{ loading ? '提交中...' : '确认提交' }}
            </button>
            
            <button 
                @click="router.back()"
                class="w-full mt-3 text-gray-500 text-sm hover:underline"
            >
                返回
            </button>
        </div>
    </div>
  </div>
</template>

<style scoped>
.bind-container {
    background: #F3F4F6;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
}

.bind-card {
    background: white;
    width: 100%;
    max-width: 400px;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.bind-header {
    color: white;
    padding: 24px;
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
}

.form-input {
    width: 100%;
    padding: 10px;
    border: 1px solid #D1D5DB;
    border-radius: 6px;
    outline: none;
    transition: border-color 0.2s;
}

.form-input:focus {
    border-color: #10B981;
}
</style>
