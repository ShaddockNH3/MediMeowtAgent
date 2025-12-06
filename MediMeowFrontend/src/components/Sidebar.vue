<script setup>
import { Icon } from '@iconify/vue'
</script>

<template>
  <div class="sidebar">
    <div class="px-4 py-6 text-center">
      <Icon icon="mdi:doctor" class="text-3xl mx-auto" />
      <h1 class="text-xl font-bold mt-4">医生工作站</h1>
    </div>
    
    <nav class="mt-8">
      <router-link to="/" class="nav-link block py-3 px-6 hover:bg-gray-700 flex items-center" active-class="active">
        <Icon icon="mdi:account-group" class="mr-3 text-xl" /> 患者管理
      </router-link>
      <a href="#" class="nav-link block py-3 px-6 hover:bg-gray-700 flex items-center">
        <Icon icon="mdi:card-account-details" class="mr-3 text-xl" /> 病历详情
      </a>
      <a href="#" class="nav-link block py-3 px-6 hover:bg-gray-700 flex items-center">
        <Icon icon="mdi:stethoscope" class="mr-3 text-xl" /> 诊断工具
      </a>
      <a href="#" class="nav-link block py-3 px-6 hover:bg-gray-700 flex items-center">
        <Icon icon="mdi:chart-line" class="mr-3 text-xl" /> 统计分析
      </a>
      <a href="#" class="nav-link block py-3 px-6 hover:bg-gray-700 flex items-center">
        <Icon icon="mdi:cog" class="mr-3 text-xl" /> 系统设置
      </a>
    </nav>
  </div>
</template>

<style scoped>
.sidebar {
  width: 240px;
  background: #34495E;
  color: white;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.nav-link {
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  transition: all 0.3s;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.nav-link.active {
  background: #2C7DB1;
  color: white;
  border-left: 4px solid #85c1e9;
}
</style>
