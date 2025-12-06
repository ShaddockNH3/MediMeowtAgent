<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'
import request from '../../api/request'

const route = useRoute()
const router = useRouter()

const deptId = route.params.deptId

if (!deptId) {
    router.replace({ name: 'department-list' })
}
const loading = ref(true)
const submitting = ref(false)
const questionnaire = ref(null)
const errorMsg = ref('')

// User inputs
const answers = ref({})
const basicInfo = ref({
    height: '',
    weight: ''
})
const fileIds = ref([])
const uploading = ref(false)

const handleFileUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return

    const formData = new FormData()
    formData.append('file', file)

    uploading.value = true
    try {
        const res = await request.post('/questionnaires/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        })
        if (res.data && res.data.file_id) {
            fileIds.value.push(res.data.file_id)
            // Store filename for display if needed, but backend only needs ID
        }
    } catch (err) {
        console.error('Upload failed', err)
        alert('图片上传失败')
    } finally {
        uploading.value = false
    }
}

const fetchQuestionnaire = async () => {
    loading.value = true
    try {
        const res = await request.get(`/questionnaires/${deptId}`)
        questionnaire.value = res.data
        
        // Initialize answers
        if (questionnaire.value.saved_answers && questionnaire.value.saved_answers.length > 0) {
            questionnaire.value.saved_answers.forEach(item => {
                answers.value[item.question_id] = item.value
            })
        }
    } catch (err) {
        console.error('Fetch questionnaire failed', err)
        errorMsg.value = err.response?.data?.msg || '无法加载问卷，请稍后重试'
    } finally {
        loading.value = false
    }
}

const submit = async () => {
    // Validate required fields
    if (!basicInfo.value.height || !basicInfo.value.weight) {
        alert('请填写身高和体重')
        return
    }
    
    // Validate required questions
    for (const q of questionnaire.value.questions) {
        if (q.is_required === '是' && !answers.value[q.question_id]) {
            alert(`请回答: ${q.label}`)
            return
        }
    }

    submitting.value = true
    try {
        const payload = {
            questionnaire_id: questionnaire.value.questionnaire_id,
            department_id: deptId,
            answers: answers.value,
            height: parseInt(basicInfo.value.height),
            weight: parseInt(basicInfo.value.weight),
            file_id: fileIds.value
        }
        
        await request.post('/questionnaires/submit', payload)
        
        alert('提交成功！请稍后查看AI分析结果')
        router.push({ name: 'patient-home' })
    } catch (err) {
        alert(err.response?.data?.msg || '提交失败')
    } finally {
        submitting.value = false
    }
}

const toggleMultiSelect = (qId, option) => {
    if (!answers.value[qId]) {
        answers.value[qId] = []
    }
    
    // Ensure it's treated as array
    if (!Array.isArray(answers.value[qId])) {
         answers.value[qId] = []
    }
    
    const idx = answers.value[qId].indexOf(option)
    if (idx > -1) {
        answers.value[qId].splice(idx, 1)
    } else {
        answers.value[qId].push(option)
    }
}

onMounted(() => {
    fetchQuestionnaire()
})
</script>

<template>
  <div class="q-page bg-gray-50 min-h-screen pb-12">
    <!-- Header -->
    <div class="bg-white shadow sticky top-0 z-10">
        <div class="max-w-3xl mx-auto px-4 py-4 flex items-center">
            <button @click="router.back()" class="mr-4 text-gray-600 hover:text-gray-900">
                <Icon icon="mdi:arrow-left" class="text-2xl" />
            </button>
            <h1 class="text-lg font-bold">智能导诊问卷</h1>
        </div>
    </div>

    <!-- Loading / Error -->
    <div v-if="loading" class="text-center py-20">
        <Icon icon="mdi:loading" class="animate-spin text-4xl text-green-600 mx-auto" />
        <p class="mt-4 text-gray-500">正在加载问卷...</p>
    </div>

    <div v-else-if="errorMsg" class="text-center py-20">
        <Icon icon="mdi:alert-circle" class="text-4xl text-red-500 mx-auto" />
        <p class="mt-4 text-gray-600">{{ errorMsg }}</p>
        <button @click="router.push({ name: 'patient-home' })" class="mt-6 text-green-600">返回首页</button>
    </div>

    <!-- Content -->
    <div v-else class="max-w-3xl mx-auto px-4 mt-6">
        <!-- Basic Info Card -->
        <div class="bg-white rounded-xl p-6 shadow-sm mb-6">
            <h2 class="font-bold text-lg mb-4 flex items-center">
                <span class="w-1 h-6 bg-green-500 rounded mr-2"></span>
                基本信息
            </h2>
            <div class="grid grid-cols-2 gap-4">
                <div>
                    <label class="block text-gray-700 text-sm font-bold mb-2">身高 (cm) <span class="text-red-500">*</span></label>
                    <input 
                        v-model="basicInfo.height"
                        type="number" 
                        class="w-full border rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-green-500"
                        placeholder="请输入身高"
                    >
                </div>
                <div>
                    <label class="block text-gray-700 text-sm font-bold mb-2">体重 (kg) <span class="text-red-500">*</span></label>
                    <input 
                        v-model="basicInfo.weight"
                        type="number" 
                        class="w-full border rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-green-500"
                        placeholder="请输入体重"
                    >
                </div>
            </div>
        </div>

        <!-- Questions -->
        <div class="bg-white rounded-xl p-6 shadow-sm">
            <h2 class="font-bold text-lg mb-6 flex items-center">
                <span class="w-1 h-6 bg-blue-500 rounded mr-2"></span>
                症状描述
            </h2>

            <div v-for="(q, idx) in questionnaire.questions" :key="q.question_id" class="mb-8 last:mb-0">
                <div class="mb-3 text-gray-800 font-medium text-lg">
                    {{ idx + 1 }}. {{ q.label }} 
                    <span v-if="q.is_required === '是'" class="text-red-500 text-sm align-top">*</span>
                </div>

                <!-- Single Choice -->
                <div v-if="q.question_type === 'single'" class="space-y-2">
                    <label v-for="opt in q.options" :key="opt" class="flex items-center p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition" :class="{'bg-green-50 border-green-500': answers[q.question_id] === opt}">
                        <input 
                            type="radio" 
                            :name="q.question_id"
                            :value="opt"
                            v-model="answers[q.question_id]"
                            class="mr-3 text-green-600 focus:ring-green-500"
                        >
                        <span>{{ opt }}</span>
                    </label>
                </div>

                <!-- Multi Choice -->
                <div v-else-if="q.question_type === 'multi'" class="space-y-2">
                    <label v-for="opt in q.options" :key="opt" class="flex items-center p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition" :class="{'bg-green-50 border-green-500': answers[q.question_id] && answers[q.question_id].includes(opt)}">
                        <input 
                            type="checkbox" 
                            :value="opt"
                            :checked="answers[q.question_id] && answers[q.question_id].includes(opt)"
                            @change="toggleMultiSelect(q.question_id, opt)"
                            class="mr-3 text-green-600 focus:ring-green-500"
                        >
                        <span>{{ opt }}</span>
                    </label>
                </div>

                <!-- Text -->
                <div v-else-if="q.question_type === 'text' || q.question_type === 'textarea'">
                    <textarea 
                        v-model="answers[q.question_id]"
                        class="w-full border rounded-lg p-3 h-32 focus:outline-none focus:ring-2 focus:ring-green-500"
                        :placeholder="q.placeholder || '请输入详细描述...'"
                    ></textarea>
                </div>
                
                 <!-- Scale (Rating) -->
                <div v-else-if="q.question_type === 'scale' || q.question_type === 'rating'" class="flex items-center justify-between bg-gray-50 p-4 rounded-lg">
                     <div class="text-sm text-gray-500">程度 (1-10)</div>
                     <div class="flex gap-2">
                         <button 
                             v-for="i in 10" 
                             :key="i"
                             class="w-8 h-8 rounded-full border flex items-center justify-center transition"
                             :class="answers[q.question_id] === i ? 'bg-green-600 text-white border-green-600' : 'bg-white text-gray-600 hover:border-green-400'"
                             @click="answers[q.question_id] = i"
                         >
                             {{ i }}
                         </button>
                     </div>
                </div>

                <!-- File Upload -->
                <div v-else-if="q.question_type === 'file'" class="space-y-4">
                    <div class="flex items-center gap-4">
                        <label class="cursor-pointer bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 px-4 py-2 rounded-lg transition flex items-center">
                            <Icon icon="mdi:cloud-upload" class="mr-2 text-xl" />
                            <span>{{ uploading ? '上传中...' : '选择图片' }}</span>
                            <input type="file" class="hidden" accept="image/*" @change="handleFileUpload" :disabled="uploading">
                        </label>
                        <span class="text-sm text-gray-500">已上传 {{ fileIds.length }} 张图片</span>
                    </div>
                </div>
            </div>
            
            <div class="mt-8 pt-6 border-t">
                <button 
                    @click="submit"
                    :disabled="submitting"
                    class="w-full bg-green-600 text-white rounded-xl py-4 font-bold text-lg shadow-lg hover:bg-green-700 transition disabled:opacity-70 flex justify-center items-center"
                >
                    <Icon v-if="submitting" icon="mdi:loading" class="animate-spin mr-2" />
                    {{ submitting ? '正在分析提交...' : '提交问卷' }}
                </button>
            </div>
        </div>
    </div>
  </div>
</template>

<style scoped>
.q-page {
    font-family: 'Segoe UI', sans-serif;
}
</style>
