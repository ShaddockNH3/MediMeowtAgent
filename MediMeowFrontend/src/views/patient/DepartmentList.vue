<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'
import request from '../../api/request'

const router = useRouter()
const departments = ref([])
const loading = ref(true)
const error = ref(null)

const fetchDepartments = async () => {
    loading.value = true
    try {
        const res = await request.get('/departments')
        departments.value = res.data
    } catch (err) {
        console.error('Fetch departments failed', err)
        error.value = '无法加载科室列表'
    } finally {
        loading.value = false
    }
}

const selectDepartment = (deptId) => {
    router.push({ name: 'questionnaire', params: { deptId } })
}

onMounted(() => {
    fetchDepartments()
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
            <h1 class="text-lg font-bold">选择科室</h1>
        </div>
    </div>

    <div class="max-w-3xl mx-auto px-4 mt-6">
        <div v-if="loading" class="text-center py-20">
            <Icon icon="mdi:loading" class="animate-spin text-4xl text-green-600 mx-auto" />
            <p class="mt-4 text-gray-500">正在加载科室...</p>
        </div>

        <div v-else-if="error" class="text-center py-20">
            <Icon icon="mdi:alert-circle" class="text-4xl text-red-500 mx-auto" />
            <p class="mt-4 text-gray-600">{{ error }}</p>
            <button @click="fetchDepartments" class="mt-4 text-green-600 font-bold hover:underline">重试</button>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div 
                v-for="dept in departments" 
                :key="dept.department_id"
                @click="selectDepartment(dept.department_id)"
                class="bg-white p-6 rounded-xl shadow-sm border border-transparent hover:border-green-500 hover:shadow-md cursor-pointer transition flex items-center"
            >
                <div class="w-12 h-12 rounded-full bg-green-100 text-green-600 flex items-center justify-center mr-4">
                    <Icon icon="mdi:doctor" class="text-2xl" />
                </div>
                <div>
                    <h3 class="font-bold text-lg text-gray-800">{{ dept.department_name }}</h3>
                    <p class="text-sm text-gray-500">点击进入智能问诊</p>
                </div>
                <Icon icon="mdi:chevron-right" class="ml-auto text-gray-300 text-xl" />
            </div>
        </div>
    </div>
  </div>
</template>
