<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'
import request from '../../api/request'

const route = useRoute()
const router = useRouter()
const recordId = route.params.id
const record = ref(null)
const loading = ref(true)
const error = ref(null)

const fetchDetail = async () => {
    loading.value = true
    try {
        const res = await request.get(`/questionnaires/record/${recordId}`)
        record.value = res.data
    } catch (err) {
        console.error('Fetch detail failed', err)
        error.value = '无法加载详情'
    } finally {
        loading.value = false
    }
}

// Simple Markdown Formatter
const formatMarkdown = (text) => {
    if (!text) return ''
    // 1. Handle bold (**text**)
    let html = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    // 2. Handle headers (### Header)
    html = html.replace(/### (.*)/g, '<h3 class="text-lg font-bold mt-4 mb-2 text-gray-800">$1</h3>')
    // 3. Handle list items (* Item)
    html = html.replace(/^\* (.*)/gm, '<li class="ml-4 list-disc">$1</li>')
    // 4. Handle newlines
    html = html.replace(/\n/g, '<br>')
    return html
}

onMounted(() => {
    fetchDetail()
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
            <h1 class="text-lg font-bold">导诊详情</h1>
        </div>
    </div>

    <div v-if="loading" class="text-center py-20">
        <Icon icon="mdi:loading" class="animate-spin text-4xl text-green-600 mx-auto" />
        <p class="mt-4 text-gray-500">正在加载...</p>
    </div>

    <div v-else-if="error" class="text-center py-20">
        <Icon icon="mdi:alert-circle" class="text-4xl text-red-500 mx-auto" />
        <p class="mt-4 text-gray-600">{{ error }}</p>
    </div>

    <div v-else class="max-w-3xl mx-auto px-4 mt-6 space-y-6">
        <!-- Status Card -->
        <div class="bg-white rounded-xl p-6 shadow-sm flex justify-between items-center">
             <div>
                <h2 class="font-bold text-lg text-gray-800 mb-1">当前状态</h2>
                <div class="text-sm text-gray-500">ID: {{ record.submission_id?.slice(0, 8) }}...</div>
             </div>
             <div class="flex items-center">
                 <div class="px-3 py-1 bg-green-100 text-green-700 rounded-full font-medium flex items-center">
                    <Icon icon="mdi:check-circle" class="mr-1"/>
                    {{ record.status === 'success' ? '已完成' : record.status }}
                 </div>
             </div>
        </div>

        <!-- AI Analysis (Key Info) -->
        <div v-if="record.key_info" 
             class="bg-white rounded-xl p-6 shadow-sm border-l-4 transition-colors duration-300"
             :class="record.is_department ? 'border-blue-500' : 'bg-red-50 border-red-500'"
        >
            <h2 class="font-bold text-lg mb-4 flex items-center" :class="record.is_department ? 'text-blue-700' : 'text-red-700'">
                <Icon :icon="record.is_department ? 'mdi:robot-excited-outline' : 'mdi:alert-circle'" class="mr-2 text-2xl" />
                {{ record.is_department ? 'AI 智能分析摘要' : '科室选择错误' }}
            </h2>
            
            <div v-if="record.is_department">
                <div class="mb-4">
                     <div class="bg-blue-50 p-3 rounded-lg">
                         <span class="text-xs text-blue-600 font-bold uppercase tracking-wider">风险等级</span>
                         <div class="font-bold text-blue-900 text-lg">{{ record.key_info.risk_level || '未知' }}</div>
                     </div>
                </div>

                <div class="space-y-4">
                    <div class="border-t pt-4">
                        <p class="text-gray-800 leading-relaxed" v-html="formatMarkdown(record.key_info.chief_complaint)"></p>
                    </div>
                </div>
            </div>

            <!-- Error State Content -->
            <div v-else class="text-center py-6">
                <div class="text-3xl font-bold text-red-600 mb-2">科室选择错误</div>
                <p class="text-red-500 text-lg">请重新选择正确的科室进行问诊</p>
                <div v-if="record.key_info.important_notes" class="mt-6 p-4 border border-red-200 bg-white rounded-lg text-left">
                     <h3 class="font-bold text-red-800 mb-2 flex items-center">
                         <Icon icon="mdi:alert-circle-outline" class="mr-1"/> 原因/建议
                     </h3>
                     <p class="text-red-900">{{ record.key_info.important_notes }}</p>
                </div>
            </div>
        </div>

        <!-- Department Referral (Success) -->
        <div v-if="record.is_department && record.department_name" class="bg-white rounded-xl p-6 shadow-sm">
             <h2 class="font-bold text-lg mb-4 flex items-center text-gray-800">
                <Icon icon="mdi:hospital-building" class="mr-2 text-2xl text-green-600" />
                就诊建议
             </h2>
             <div class="bg-green-50 p-6 rounded-xl border border-green-200 text-center">
                 <Icon icon="mdi:check-circle" class="text-5xl text-green-500 mx-auto mb-4" />
                 <p class="text-xl text-gray-800 font-medium">
                     请到 <span class="text-green-600 font-bold text-2xl">{{ record.department_name }}</span> 问诊
                 </p>
                 <p class="text-gray-500 mt-2">请携带好相关证件前往挂号</p>
             </div>
        </div>

        <!-- Q&A History -->
        <div v-if="record.questions && record.questions.length" class="bg-white rounded-xl p-6 shadow-sm">
            <h2 class="font-bold text-lg mb-4 flex items-center text-gray-800">
                <Icon icon="mdi:forum-outline" class="mr-2 text-2xl text-purple-600" />
                问诊记录
            </h2>
            <div class="space-y-6">
                <div v-for="(q, idx) in record.questions" :key="q.question_id" class="border-b last:border-0 pb-4 last:pb-0">
                    <div class="text-gray-500 text-sm mb-1">问题 {{ idx + 1 }}</div>
                    <div class="font-medium text-gray-900 mb-2">{{ q.label }}</div>
                    <div class="bg-purple-50 text-purple-900 px-3 py-2 rounded-lg inline-block">
                        {{ q.user_answer }}
                    </div>
                </div>
            </div>
        </div>

        <!-- Basic Info -->
        <div class="bg-white rounded-xl p-6 shadow-sm">
            <h2 class="font-bold text-lg mb-4 text-gray-800">基础数据</h2>
            <div class="grid grid-cols-2 gap-4">
                 <div class="p-3 bg-gray-50 rounded-lg text-center">
                     <div class="text-gray-500 text-sm">身高</div>
                     <div class="font-bold text-lg">{{ record.height || '-' }} cm</div>
                 </div>
                 <div class="p-3 bg-gray-50 rounded-lg text-center">
                     <div class="text-gray-500 text-sm">体重</div>
                     <div class="font-bold text-lg">{{ record.weight || '-' }} kg</div>
                 </div>
            </div>
        </div>
    </div>
  </div>
</template>
