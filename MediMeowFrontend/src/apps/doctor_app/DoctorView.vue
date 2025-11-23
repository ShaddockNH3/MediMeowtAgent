<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="login-header doctor-header">
           <!-- 您可以更换一个更适合医生的图标，比如用 Element Plus 自带的 Suitcase -->
          <el-icon :size="50" color="white"><Suitcase /></el-icon>
          <h1 class="title">医生工作台</h1>
          <p class="subtitle">欢迎登录</p>
        </div>
      </template>

      <el-form :model="loginForm" label-position="top" class="login-form">
        <el-form-item label="用户名">
          <el-input 
            v-model="loginForm.username" 
            placeholder="请输入用户名" 
            size="large"
          />
        </el-form-item>
        
        <el-form-item label="密码">
            <el-input 
              v-model="loginForm.password" 
              type="password"
              placeholder="请输入密码" 
              size="large"
              show-password
            />
        </el-form-item>

        <el-form-item>
          <el-button 
            type="primary" 
            @click="handleLogin" 
            class="login-button" 
            size="large"
            :class="'doctor-button'"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { reactive } from 'vue';
import { Suitcase } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';

const loginForm = reactive({
  username: '',
  password: '',
});

const handleLogin = () => {
  // TODO: 对接医生登录API
  console.log('医生尝试登录:', loginForm);
  ElMessage.info('医生登录功能待开发');
};
</script>

<style scoped>
/* 复用病人登录页的大部分样式 */
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  width: 100%;
  background-color: #f0f2f5;
}

.login-card {
  width: 420px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden; 
}

.login-header {
  color: white;
  padding: 40px 20px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

/* 医生端的专属颜色 */
.doctor-header {
  background-color: #00796b; /* 一个沉稳的绿色系 */
}

.title {
  font-size: 26px;
  font-weight: 600;
  margin: 0;
}

.subtitle {
  font-size: 16px;
  margin: 0;
  opacity: 0.9;
}

.login-form {
  padding: 30px;
}

.login-button {
  width: 100%;
  margin-top: 10px;
}

.doctor-button {
    background-color: #00796b;
    border-color: #00796b;
}

:deep(.el-card__header) {
  padding: 0;
  border-bottom: none;
}
:deep(.el-form-item) {
  margin-bottom: 28px;
}
</style>