<!-- 文件路径: src/apps/patient_app/PatientMainPage.vue -->
<template>
  <div class="patient-main-container">
    <el-container class="main-layout-container">
      <!-- 顶部头部区域 -->
      <el-header class="main-header">
        <div class="header-left">
          <el-icon :size="30" color="white"><HomeFilled /></el-icon>
          <span class="app-title">智能问诊系统</span>
        </div>
        <div class="header-right">
          <el-button type="text" @click="handleLogout" class="logout-button">
            <el-icon><SwitchButton /></el-icon>
            退出登录
          </el-button>
        </div>
      </el-header>

      <!-- 主要内容区域 -->
      <el-main class="main-content">
        <h2 class="welcome-message">欢迎，用户！请选择您要进行的操作：</h2>

        <!-- 功能卡片区域 -->
        <el-row :gutter="20" class="feature-cards-row">
          <el-col :xs="24" :sm="12" :md="8" :lg="6">
            <el-card class="feature-card" shadow="hover" @click="goToIdentity">
              <div class="card-icon"><el-icon><User /></el-icon></div>
              <div class="card-title">身份验证</div>
              <div class="card-description">完善或查看您的身份信息</div>
            </el-card>
          </el-col>

          <el-col :xs="24" :sm="12" :md="8" :lg="6">
            <el-card class="feature-card" shadow="hover" @click="goToQuestionnaire">
              <div class="card-icon"><el-icon><Tickets /></el-icon></div>
              <div class="card-title">问卷信息</div>
              <div class="card-description">填写健康问卷或查看结果</div>
            </el-card>
          </el-col>

          <el-col :xs="24" :sm="12" :md="8" :lg="6">
            <el-card class="feature-card" shadow="hover" @click="goToMyPage">
              <div class="card-icon"><el-icon><Avatar /></el-icon></div>
              <div class="card-title">我的</div>
              <div class="card-description">个人中心、设置等</div>
            </el-card>
          </el-col>

          <el-col :xs="24" :sm="12" :md="8" :lg="6">
            <el-card class="feature-card" shadow="hover" @click="goToConsultation">
              <div class="card-icon"><el-icon><ChatDotRound /></el-icon></div>
              <div class="card-title">在线咨询</div>
              <div class="card-description">与医生进行在线交流</div>
            </el-card>
          </el-col>
        </el-row>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { HomeFilled, User, Tickets, Avatar, SwitchButton, ChatDotRound } from '@element-plus/icons-vue';

const router = useRouter();

// 退出登录
const handleLogout = () => {
  localStorage.removeItem('userToken'); 
  ElMessage.info('您已成功退出登录！');
  router.push({ name: 'PatientLogin' });
};

// 跳转到身份验证页面
const goToIdentity = () => {
  router.push({ name: 'PatientIdentity' });
};

// ======================= 核心修改点 =======================
// 将这里的提示信息改为实际的路由跳转
const goToQuestionnaire = () => {
  // 跳转到科室选择页面，让用户选择科室后再进入问卷
  // 这里的 'DepartmentSelection' 是我们将在路由文件中定义的名字
  router.push({ name: 'DepartmentSelection' });
};
// ========================================================

// 跳转到“我的”页面
const goToMyPage = () => {
  router.push({ name: 'PatientMyPage' }); 
};

// 占位符函数，未来可实现
const goToConsultation = () => {
  ElMessage.info('在线咨询功能待开发...');
};
</script>

<!-- style 部分保持不变 -->
<style scoped>
.patient-main-container {
  min-height: 100vh;
  background-color: #f0f2f5;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 20px;
  box-sizing: border-box;
}
.main-layout-container {
  width: 100%;
  max-width: 1200px;
  background-color: #fff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-radius: 12px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  min-height: calc(100vh - 40px);
}
.main-header {
  background-color: #3c8abe;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 60px;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}
.app-title {
  font-size: 24px;
  font-weight: 600;
  margin: 0;
}
.logout-button {
  color: white;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 5px;
}
.logout-button:hover {
  text-decoration: underline;
  color: #ecf5ff;
}
.main-content {
  padding: 30px;
  flex-grow: 1;
}
.welcome-message {
  font-size: 22px;
  color: #333;
  margin-bottom: 30px;
  text-align: center;
}
.feature-cards-row {
  justify-content: center;
}
.feature-card {
  text-align: center;
  padding: 20px;
  margin-bottom: 20px;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.3s ease;
  height: 200px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}
.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}
.card-icon {
  font-size: 60px;
  color: #3c8abe;
  margin-bottom: 15px;
}
.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 5px;
}
.card-description {
  font-size: 14px;
  color: #666;
  min-height: 40px;
}
@media (max-width: 768px) {
  .patient-main-container {
    padding: 0;
    align-items: stretch;
  }
  .main-layout-container {
    max-width: 100%;
    min-height: 100vh;
    border-radius: 0;
    box-shadow: none;
  }
  .main-header {
    height: 50px;
    padding: 0 15px;
  }
  .app-title {
    font-size: 20px;
  }
  .header-left .el-icon {
    font-size: 25px !important;
  }
  .logout-button {
    font-size: 14px;
  }
  .main-content {
    padding: 20px;
  }
  .welcome-message {
    font-size: 18px;
    margin-bottom: 25px;
  }
  .feature-card {
    height: auto;
    min-height: 160px;
    padding: 15px;
  }
  .card-icon {
    font-size: 48px;
    margin-bottom: 10px;
  }
  .card-title {
    font-size: 16px;
  }
  .card-description {
    font-size: 12px;
  }
}
@media (max-width: 375px) {
  .app-title {
    font-size: 18px;
  }
  .logout-button {
    font-size: 13px;
    gap: 3px;
  }
  .main-content {
    padding: 15px;
  }
  .welcome-message {
    font-size: 16px;
    margin-bottom: 20px;
  }
  .card-icon {
    font-size: 40px;
  }
}
</style>