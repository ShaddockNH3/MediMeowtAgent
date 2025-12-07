<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { usePatientStore } from '../stores/patient'
import { Icon } from '@iconify/vue'
import Sidebar from '../components/Sidebar.vue'
import TopBar from '../components/TopBar.vue'

const router = useRouter()
const patientStore = usePatientStore()

const searchTerm = ref('')
const statusFilter = ref('全部状态')

const filteredPatients = computed(() => {
  return patientStore.patients.filter(patient => {
    // Search filter
    const search = searchTerm.value.toLowerCase()
    const nameMatch = patient.user?.username?.toLowerCase().includes(search)
    const phoneMatch = patient.user?.phone_number?.includes(search)
    
    // Status filter (Mock logic as backend doesn't return status in summary yet, assuming all in queue are 'waiting')
    // We can infer urgency or status if we had that data. For now, just pass through or simulate.
    const statusMatch = statusFilter.value === '全部状态' || true 
    
    return (nameMatch || phoneMatch) && statusMatch
  })
})

const maskName = (name) => {
    if (!name) return '未知'
    if (name.length <= 1) return '*'
    if (name.length === 2) return name[0] + '*'
    // For > 2 chars, keep first and last, mask middle
    return name[0] + '*'.repeat(name.length - 2) + name[name.length - 1]
}

const maskPhone = (phone) => {
    if (!phone) return '-'
    if (phone.length < 4) return phone 
    // Keep last 4, mask everything before
    return '*'.repeat(phone.length - 4) + phone.slice(-4)
}

const getStatusClass = (patient) => {
    // Mock random status for demo purposes since backend doesn't provide it in summary
    // In real app, `patient.status` would come from API
    return 'status-stable'
}


const getStatusLabel = (patient) => {
    return '待接诊'
}

const goToDetail = (recordId) => {
  router.push({ name: 'patient-detail', params: { id: recordId } })
}

onMounted(() => {
  patientStore.fetchQueue()
})
</script>

<template>
  <div class="app-container">
    <Sidebar />
    
    <div class="main-content">
      <TopBar>
         <template #title>患者管理</template>
      </TopBar>
      
      <div class="content-wrap">
        <!-- Search & Filter -->
        <div class="card mb-6">
          <div class="flex flex-wrap items-center gap-4">
            <div class="flex-1">
              <div class="relative">
                <Icon icon="mdi:magnify" class="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 text-xl" />
                <input 
                  v-model="searchTerm"
                  type="text" 
                  class="w-full pl-10 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
                  placeholder="搜索患者姓名、手机号"
                >
              </div>
            </div>
            
            <div class="flex space-x-3">
              <select v-model="statusFilter" class="px-4 py-3 border border-gray-300 rounded-lg bg-white outline-none focus:border-blue-500">
                <option>全部状态</option>
                <option>紧急</option>
                <option>待随访</option>
                <option>稳定</option>
              </select>
              
              <button 
                class="px-4 py-3 bg-blue-100 text-blue-700 rounded-lg font-medium flex items-center hover:bg-blue-200 transition"
                @click="patientStore.fetchQueue()"
              >
                <Icon icon="mdi:refresh" class="mr-2" :class="{ 'animate-spin': patientStore.loading }" />
                刷新列表
              </button>
            </div>
          </div>
        </div>
        
        <!-- List -->
        <div class="card">
          <div class="flex justify-between items-center mb-6">
            <h3 class="text-lg font-semibold text-gray-800">患者列表</h3>
            <div class="text-gray-500">共 {{ filteredPatients.length }} 位患者</div>
          </div>
          
          <div v-if="patientStore.loading && patientStore.patients.length === 0" class="p-8 text-center text-gray-500">
            <Icon icon="mdi:loading" class="animate-spin text-3xl mx-auto mb-2" />
            <p>正在加载患者数据...</p>
          </div>
          
          <div v-else-if="filteredPatients.length === 0" class="p-8 text-center text-gray-500">
             <Icon icon="mdi:clipboard-text-off-outline" class="text-4xl mx-auto mb-2 opacity-50" />
             <p>暂无待诊患者</p>
          </div>
          
          <div v-else class="table-container">
            <table class="patient-table">
              <thead>
                <tr>
                  <th>患者姓名</th>
                  <th>性别/年龄</th>
                  <th>联系电话</th>
                  <th>挂号时间</th>
                  <th>状态</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="patient in filteredPatients" :key="patient.record_id" class="hover:bg-gray-50 transition">
                  <td>
                    <div class="flex items-center">
                      <div class="mr-3 bg-blue-100 rounded-full w-8 h-8 flex items-center justify-center text-blue-600">
                        <Icon icon="mdi:account" />
                      </div>
                      <div class="font-medium">{{ maskName(patient.user?.username) }}</div>
                    </div>
                  </td>
                  <td>
                    {{ patient.user?.gender || '-' }} / {{ 
                        patient.user?.birth ? (new Date().getFullYear() - new Date(patient.user?.birth).getFullYear()) : '-' 
                    }}岁
                  </td>
                  <td>{{ maskPhone(patient.user?.phone_number) }}</td>
                  <td>{{ patient.time || '-' }}</td>
                  <td>
                    <span class="status-badge" :class="getStatusClass(patient)">
                      <Icon icon="mdi:clock-outline" class="mr-1 align-middle inline" />
                      {{ getStatusLabel(patient) }}
                    </span>
                  </td>

                  <td>
                    <button 
                        @click="goToDetail(patient.record_id)"
                        class="text-blue-600 hover:text-blue-800 font-medium flex items-center"
                    >
                      接诊 <Icon icon="mdi:arrow-right" class="ml-1" />
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          
          <!-- Pagination UI (Static for now) -->
          <div v-if="filteredPatients.length > 0" class="mt-8 flex justify-between items-center text-sm text-gray-500">
            <div>显示 {{ filteredPatients.length }} 条记录</div>
            <div class="flex space-x-2">
               <button class="px-3 py-1 border rounded hover:bg-gray-50">上一页</button>
               <button class="px-3 py-1 bg-blue-600 text-white rounded">1</button>
               <button class="px-3 py-1 border rounded hover:bg-gray-50">下一页</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.app-container {
  display: flex;
  min-height: 100vh;
  background: #F8FAFC;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.content-wrap {
  padding: 24px;
  flex: 1;
  overflow-y: auto;
}

.card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  padding: 24px;
}

.table-container {
  overflow-x: auto;
}

.patient-table {
  width: 100%;
  border-collapse: collapse;
}

.patient-table th {
  background: #F8FAFC;
  text-align: left;
  padding: 12px 16px;
  font-weight: 600;
  color: #64748B;
  border-bottom: 2px solid #E2E8F0;
  white-space: nowrap;
}

.patient-table td {
  padding: 16px;
  border-bottom: 1px solid #F1F5F9;
  color: #334155;
}

.status-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-stable { background: #F0FDF4; color: #166534; border: 1px solid #BBF7D0; }
.status-urgent { background: #FEF2F2; color: #991B1B; border: 1px solid #FECACA; }
</style>
