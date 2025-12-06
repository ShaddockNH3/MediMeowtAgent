<script setup>
import { useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'

const router = useRouter()
</script>

<template>
  <div class="landing-container">
    <div class="content-box text-center">
      <div class="mb-8">
        <Icon icon="mdi:medical-bag" class="text-6xl text-blue-600 mx-auto" />
        <h1 class="text-4xl font-bold mt-4 text-gray-800">医智 MedMind</h1>
        <p class="text-xl text-gray-600 mt-2">智能医疗辅助决策系统</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mt-12">
        <!-- Patient Entrance -->
        <div class="role-card" @click="router.push({ name: 'patient-login' })">
          <div class="icon-wrapper bg-green-100 text-green-600">
            <Icon icon="mdi:account" class="text-4xl" />
          </div>
          <h2 class="text-2xl font-semibold mt-4">我是患者</h2>
          <p class="text-gray-500 mt-2">在线问诊 · 智能预检 · 健康档案</p>
          <button class="mt-6 btn-outline-green">进入患者端</button>
        </div>

        <!-- Doctor Entrance -->
        <div class="role-card" @click="router.push({ name: 'doctor-login' })">
          <div class="icon-wrapper bg-blue-100 text-blue-600">
            <Icon icon="mdi:doctor" class="text-4xl" />
          </div>
          <h2 class="text-2xl font-semibold mt-4">我是医生</h2>
          <p class="text-gray-500 mt-2">患者管理 · 辅助诊断 · 病历处理</p>
          <button class="mt-6 btn-outline-blue">进入医生端</button>
        </div>
      </div>

      <div class="mt-16 text-gray-400 text-sm">
        © 2025 MedMind 医智科技 · 为医疗赋能
      </div>
    </div>
  </div>
</template>

<style scoped>
.landing-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.content-box {
  max-width: 900px;
  width: 100%;
}

.role-card {
  background: white;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.role-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.role-card:hover .btn-outline-green {
  background: #10B981;
  color: white;
}

.role-card:hover .btn-outline-blue {
  background: #2563EB;
  color: white;
}

.icon-wrapper {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
}

.btn-outline-green {
  padding: 10px 24px;
  border: 2px solid #10B981;
  color: #10B981;
  border-radius: 50px;
  font-weight: 600;
  background: transparent;
  transition: all 0.3s;
}

.btn-outline-blue {
  padding: 10px 24px;
  border: 2px solid #2563EB;
  color: #2563EB;
  border-radius: 50px;
  font-weight: 600;
  background: transparent;
  transition: all 0.3s;
}
</style>
