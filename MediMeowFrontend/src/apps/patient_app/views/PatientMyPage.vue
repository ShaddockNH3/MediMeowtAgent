<!-- 文件路径: src/apps/patient_app/PatientMyPage.vue -->
<template>
  <div class="my-page-container">
    <el-card class="info-card" v-loading="loading">
      <template #header>
        <div class="info-header">
          <el-icon :size="50" color="white"><Avatar /></el-icon>
          <h1 class="title">我的个人信息</h1>
        </div>
      </template>

      <div class="card-body">
        <el-descriptions v-if="userInfo" :column="1" border size="large">
          <!-- 基础信息 -->
          <el-descriptions-item label="用户ID">{{ userInfo.id }}</el-descriptions-item>
          <el-descriptions-item label="绑定手机号">{{ userInfo.phone_number }}</el-descriptions-item>
          <el-descriptions-item label="姓名">{{ userInfo.username }}</el-descriptions-item>
          
          <!-- 💡 核心修改：新增的身份信息展示 -->
          <!-- 使用 v-if 判断，只有当后端返回这些字段时才显示 -->
          <el-descriptions-item v-if="userInfo.gender" label="性别">{{ userInfo.gender }}</el-descriptions-item>
          <el-descriptions-item v-if="userInfo.birth" label="出生日期">{{ userInfo.birth }}</el-descriptions-item>
          <el-descriptions-item v-if="userInfo.ethnicity" label="民族">{{ userInfo.ethnicity }}</el-descriptions-item>
          <el-descriptions-item v-if="userInfo.origin" label="籍贯">{{ userInfo.origin }}</el-descriptions-item>

          <!-- 时间信息 -->
          <el-descriptions-item label="注册时间">{{ userInfo.created_at }}</el-descriptions-item>
          <el-descriptions-item label="信息更新时间">{{ userInfo.updated_at }}</el-descriptions-item>
        </el-descriptions>

        <el-empty v-else-if="!loading" description="未能获取到用户信息"></el-empty>

        <div class="footer-actions">
          <el-button type="primary" size="large" @click="handleBackToMain" class="back-button">
            返回主页
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { Avatar } from '@element-plus/icons-vue';
import { getUserInfo } from '../api/PatientMyPageAPI.js';

const router = useRouter();
const loading = ref(true);
const userInfo = ref(null);

onMounted(() => {
  fetchUserInfo();
});

const fetchUserInfo = async () => {
  try {
    const res = await getUserInfo();
    if (res && res.base && res.base.code === '10000') {
      // 这里的 res.data 会自动包含所有后端返回的字段
      userInfo.value = res.data; 
      ElMessage.success('用户信息获取成功！');
    } else {
      ElMessage.error(res?.base?.msg || '获取用户信息失败');
    }
  } catch (error) {
    ElMessage.error(error?.base?.msg || '请求用户信息接口失败');
    console.error('获取用户信息失败:', error);
  } finally {
    loading.value = false;
  }
};

const handleBackToMain = () => {
  router.push({ name: 'PatientMain' });
};
</script>

<style scoped>
/* 样式部分无需修改 */
.my-page-container { 
  display: flex; 
  justify-content: center; 
  align-items: center; 
  min-height: 100vh;
  width: 100%; 
  background-color: #f0f2f5; 
  padding: 20px; 
  box-sizing: border-box; 
}
.info-card { 
  width: 100%; 
  max-width: 600px;
  border-radius: 12px; 
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); 
  overflow: hidden; 
}
.card-body { 
  padding: 30px; 
}
.info-header { 
  background-color: #3c8abe; 
  color: white; 
  padding: 40px 20px; 
  text-align: center; 
  display: flex; 
  flex-direction: column; 
  align-items: center; 
  gap: 15px; 
}
.title { 
  font-size: 26px; 
  font-weight: 600; 
  margin: 0; 
}
.footer-actions { 
  text-align: center; 
  margin-top: 30px; 
}
.back-button {
  width: 100%;
}
:deep(.el-card__header) { 
  padding: 0; 
  border-bottom: none; 
}
:deep(.el-card__body) { 
  padding: 0; 
}
:deep(.el-descriptions__label) {
  font-weight: bold;
}
</style>