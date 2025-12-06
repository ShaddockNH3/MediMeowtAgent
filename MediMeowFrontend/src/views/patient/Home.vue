<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { Icon } from '@iconify/vue'
import request from '../../api/request'

const router = useRouter()
const authStore = useAuthStore()
const userInfo = ref(authStore.user || {})
const historyRecords = ref([])
const loading = ref(false)

const departments = [
    { id: '1', name: '全科', icon: 'mdi:doctor' }, // Mocking Departments for now, ideally fetch from backend
]

const fetchRecords = async () => {
    loading.value = true
    try {
        const res = await request.get('/questionnaires/submit') // This gets history
        historyRecords.value = res.data.records
    } catch (err) {
        console.error('Fetch history failed', err)
    } finally {
        loading.value = false
    }
}

const fetchUserInfo = async () => {
   try {
       const res = await request.get('/user/info')
       userInfo.value = res.data
       authStore.user = res.data
       localStorage.setItem('user', JSON.stringify(res.data))
   } catch (err) {
       console.error(err)
   }
}

const startConsultation = () => {
    // For now, default to department 1 or let them choose. 
    // We will redirect to questionnaire page with department query.
    // Assuming Department ID 1 exists or handled.
    // In real app we need a department selection step if multiple exist.
    router.push({ name: 'department-list' })
}

const logout = () => {
    authStore.logout()
    router.push({ name: 'landing' })
}

onMounted(() => {
    fetchUserInfo()
    fetchRecords()
})
</script>

<template>
  <div class="patient-home">
    <!-- Header -->
    <header class="bg-white shadow">
        <div class="max-w-4xl mx-auto px-4 py-4 flex justify-between items-center">
            <div class="flex items-center">
                <Icon icon="mdi:medical-bag" class="text-3xl text-green-600 mr-2" />
                <span class="font-bold text-xl text-gray-800">MediMeow 个人中心</span>
            </div>
            <div class="flex items-center space-x-4">
                 <span class="text-gray-600">{{ userInfo.username || userInfo.phone_number }}</span>
                 <button @click="logout" class="text-gray-400 hover:text-red-500">
                     <Icon icon="mdi:logout" class="text-xl" />
                 </button>
            </div>
        </div>
    </header>

    <main class="max-w-4xl mx-auto px-4 py-8">
        <!-- Identity Card -->
        <div class="bg-white rounded-xl p-6 shadow-sm mb-8 flex items-center justify-between">
             <div class="flex items-center">
                 <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 mr-4">
                     <Icon icon="mdi:account" class="text-3xl" />
                 </div>
                 <div>
                     <h2 class="text-xl font-bold">{{ userInfo.username || '未实名用户' }}</h2>
                     <p class="text-gray-500">{{ userInfo.phone_number }}</p>
                 </div>
             </div>
             
             <div v-if="!userInfo.username || userInfo.username.startsWith('默认用户')">
                  <button 
                      @click="router.push({ name: 'patient-bind' })"
                      class="px-4 py-2 border border-blue-600 text-blue-600 rounded-lg text-sm hover:bg-blue-50"
                  >
                      完善实名信息
                  </button>
             </div>
        </div>

        <!-- Action Area -->
        <div class="mb-8">
            <h3 class="text-lg font-bold mb-4">快速就医</h3>
            <div class="grid grid-cols-2 gap-4">
                <button 
                    @click="startConsultation"
                    class="bg-green-600 text-white p-6 rounded-xl shadow-lg hover:bg-green-700 transition flex flex-col items-center justify-center h-32"
                >
                    <Icon icon="mdi:stethoscope" class="text-4xl mb-2" />
                    <span class="font-bold text-lg">AI 智能导诊</span>
                    <span class="text-white text-opacity-80 text-sm">填写问卷，快速分诊</span>
                </button>
                
                <button 
                    @click="router.push({ name: 'patient-history' })"
                    class="bg-white text-gray-700 p-6 rounded-xl shadow border hover:bg-gray-50 transition flex flex-col items-center justify-center h-32"
                >
                    <Icon icon="mdi:history" class="text-4xl mb-2 text-blue-500" />
                    <span class="font-bold text-lg">历史问诊</span>
                    <span class="text-gray-400 text-sm">查看过往就医记录</span>
                </button>
            </div>
        </div>

        <!-- History List -->
        <div>
            <h3 class="text-lg font-bold mb-4">最近记录</h3>
            
            <div v-if="loading" class="text-center py-8">
                <Icon icon="mdi:loading" class="animate-spin text-3xl mx-auto text-gray-400" />
            </div>
            
            <div v-else-if="historyRecords.length === 0" class="text-center py-12 bg-gray-50 rounded-xl border border-dashed border-gray-300">
                <Icon icon="mdi:clipboard-text-off-outline" class="text-4xl text-gray-300 mx-auto mb-2" />
                <p class="text-gray-500">暂无就诊记录</p>
            </div>
            
            <div v-else class="space-y-4">
                <div v-for="record in historyRecords" :key="record.record_id" class="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
                    <div class="flex justify-between items-start mb-2">
                        <div>
                            <span class="bg-blue-100 text-blue-700 text-xs px-2 py-1 rounded mr-2">{{ record.department_name }}</span>
                            <span class="font-bold text-gray-800">{{ record.questionnaire_title }}</span>
                        </div>
                        <span class="text-gray-400 text-sm">{{ record.created_at }}</span>
                    </div>
                    
                    <div v-if="record.ai_result?.key_info" class="text-sm text-gray-600 mb-3 bg-gray-50 p-2 rounded">
                        <span class="font-medium">主诉：</span> {{ record.ai_result.key_info['主诉'] || '无' }}
                    </div>
                    
                    <div class="flex justify-between items-center mt-2">
                        <div class="flex items-center">
                            <span 
                                class="w-2 h-2 rounded-full mr-2"
                                :class="{
                                    'bg-yellow-500': record.status_code === 'waiting',
                                    'bg-green-500': record.status_code === 'completed'
                                }"
                            ></span>
                            <span class="text-sm text-gray-500">{{ record.status }}</span>
                        </div>
                        <button 
                            @click="router.push({ name: 'record-detail', params: { id: record.record_id } })"
                            class="text-green-600 text-sm hover:underline"
                        >查看详情</button>
                    </div>
                </div>
            </div>
        </div>
    </main>
  </div>
</template>

<style scoped>
.patient-home {
    min-height: 100vh;
    background: #F9FAFB;
}
</style>
