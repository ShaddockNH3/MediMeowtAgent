<script setup>
import { computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'

const authStore = useAuthStore()
const router = useRouter()

const doctorName = computed(() => authStore.doctor?.username || '医生')
const departmentName = computed(() => authStore.doctor?.department_name || '科室')

const handleLogout = () => {
  authStore.logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <div class="top-bar">
    <div class="flex items-center">
      <h2 class="text-xl font-semibold text-gray-800">
        <slot name="title">工作台</slot>
      </h2>
    </div>
    
    <div class="flex items-center space-x-5">
      <div class="relative cursor-pointer hover:bg-gray-100 p-2 rounded-full">
        <Icon icon="mdi:bell-outline" class="text-xl text-gray-500" />
        <span class="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
      </div>
      
      <div class="flex items-center cursor-pointer hover:bg-gray-50 p-2 rounded-lg" @click="handleLogout" title="点击退出登录">
        <Icon icon="mdi:account-circle" class="mr-2 text-gray-500 text-2xl" />
        <span class="font-medium text-gray-700">{{ doctorName }}</span>
        <span class="mx-3 text-gray-300">|</span>
        <span class="text-gray-500 text-sm">{{ departmentName }}</span>
        <Icon icon="mdi:logout" class="ml-2 text-gray-400 hover:text-red-500" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.top-bar {
  height: 64px;
  background: white;
  border-bottom: 1px solid #E5E7EB;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}
</style>
