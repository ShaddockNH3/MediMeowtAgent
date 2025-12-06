<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'
import request from '../../api/request'

const router = useRouter()
const records = ref([])
const loading = ref(true)
const error = ref(null)

const fetchRecords = async () => {
    loading.value = true
    error.value = null
    try {
        const res = await request.get('/questionnaires/submit')
        records.value = res.data.records || []
    } catch (err) {
        console.error('Fetch history failed', err)
        error.value = '无法加载历史记录，请稍后重试'
    } finally {
        loading.value = false
    }
}

const goToDetail = (recordId) => {
    router.push({ name: 'record-detail', params: { id: recordId } })
}

onMounted(() => {
    fetchRecords()
})
</script>

<template>
  <div class="min-h-screen bg-gray-50 pb-12">
    <!-- Header -->
    <div class="bg-white shadow sticky top-0 z-10">
        <div class="max-w-3xl mx-auto px-4 py-4 flex items-center">
            <button @click="router.back()" class="mr-4 text-gray-600 hover:text-gray-900">
                <Icon icon="mdi:arrow-left" class="text-2xl" />
            </button>
            <h1 class="text-lg font-bold">历史问诊记录</h1>
        </div>
    </div>

    <div class="max-w-3xl mx-auto px-4 mt-6">
        <div v-if="loading" class="text-center py-20">
            <Icon icon="mdi:loading" class="animate-spin text-4xl text-green-600 mx-auto" />
            <p class="mt-4 text-gray-500">正在加载记录...</p>
        </div>

        <div v-else-if="error" class="text-center py-20">
            <Icon icon="mdi:alert-circle" class="text-4xl text-red-500 mx-auto" />
            <p class="mt-4 text-gray-600">{{ error }}</p>
            <button @click="fetchRecords" class="mt-4 text-green-600 font-bold hover:underline">重试</button>
        </div>

        <div v-else-if="records.length === 0" class="text-center py-20">
            <Icon icon="mdi:clipboard-text-off-outline" class="text-4xl text-gray-300 mx-auto" />
            <p class="mt-4 text-gray-500">暂无历史记录</p>
            <button @click="router.push({ name: 'department-list' })" class="mt-6 bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition">
                去导诊
            </button>
        </div>

        <div v-else class="space-y-4">
            <div 
                v-for="record in records" 
                :key="record.record_id" 
                @click="goToDetail(record.record_id)"
                class="bg-white p-4 rounded-xl shadow-sm border border-transparent hover:border-green-500 cursor-pointer transition"
            >
                <div class="flex justify-between items-start mb-2">
                    <div>
                        <span class="bg-blue-100 text-blue-700 text-xs px-2 py-1 rounded mr-2">{{ record.department_name }}</span>
                        <span class="font-bold text-gray-800">{{ record.questionnaire_title || '智能导诊' }}</span>
                    </div>
                    <span class="text-gray-400 text-sm">{{ record.created_at }}</span>
                </div>
                
                <div v-if="record.ai_result?.key_info" class="text-sm text-gray-600 mb-3 bg-gray-50 p-2 rounded line-clamp-2">
                    <span class="font-medium">主诉：</span> {{ record.ai_result.key_info['主诉'] || '无详细描述' }}
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
                    <span class="text-green-600 text-sm">查看详情 ></span>
                </div>
            </div>
        </div>
    </div>
  </div>
</template>
