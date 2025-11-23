<!-- D:\code\ruangong\new\src\apps\patient_app\PatientIdentity.vue -->
<template>
  <div class="patient-identity-container">
    <el-card class="identity-card">
      <template #header>
        <div class="identity-header">
          <el-icon :size="50" color="white"><User /></el-icon> <!-- 使用 ElIcon User 图标 -->
          <h1 class="title">病人身份信息</h1>
          <p class="subtitle">完善您的身份信息，以便为您提供更好的服务</p>
        </div>
      </template>

      <div class="card-body">
        <el-form :model="identityForm" :rules="identityRules" ref="identityFormRef" label-position="top" class="identity-form">
          <!-- 登录核心字段（根据 shenfen.html 提供的，用于认证） -->
          <el-form-item label="手机号码" prop="phone_number">
            <el-input v-model="identityForm.phone_number" placeholder="请输入您的注册手机号" size="large" clearable />
          </el-form-item>
          <el-form-item label="登录密码" prop="password">
            <el-input v-model="identityForm.password" type="password" placeholder="请输入您的登录密码" size="large" show-password />
          </el-form-item>

          <el-divider>病人基本信息</el-divider>

          <el-form-item label="身份证号码" prop="id_card">
            <el-input v-model="identityForm.id_card" placeholder="请输入18位身份证号码" size="large" clearable />
          </el-form-item>
          <el-form-item label="真实姓名" prop="patient_name">
            <el-input v-model="identityForm.patient_name" placeholder="请输入真实姓名" size="large" clearable />
          </el-form-item>
          <el-form-item label="年龄" prop="age">
            <el-input-number v-model="identityForm.age" :min="1" :max="120" placeholder="请输入年龄" size="large" controls-position="right" style="width: 100%;" />
          </el-form-item>
          <el-form-item label="性别" prop="gender">
            <el-select v-model="identityForm.gender" placeholder="请选择性别" size="large" style="width: 100%;">
              <el-option label="男" value="male"></el-option>
              <el-option label="女" value="female"></el-option>
              <el-option label="其他" value="other"></el-option>
            </el-select>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="handleSubmit" class="submit-button" size="large" :loading="loading">
              提交信息并绑定身份证
            </el-button>
          </el-form-item>
        </el-form>
        <div class="footer-actions">
          <el-link type="info" @click="handleLogout">返回登录/退出</el-link>
        </div>
      </div>
    </el-card>
  </div>
</template>

<!-- D:\code\ruangong\new\src\apps\patient_app\PatientIdentity.vue -->
<script setup>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { User } from '@element-plus/icons-vue';
import { submitPatientIdentity } from './api/PatientIdentityAPI.js';

const router = useRouter();
const loading = ref(false);
const identityFormRef = ref(null);

const identityForm = reactive({
  phone_number: '',
  password: '',
  id_card: '',
  patient_name: '',
  age: undefined,
  gender: ''
});

const identityRules = {
  phone_number: [
    { required: true, message: '请输入手机号码', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  password: [{ required: true, message: '请输入登录密码', trigger: 'blur' }],
  id_card: [
    { required: true, message: '请输入身份证号码', trigger: 'blur' },
    { pattern: /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/, message: '请输入正确的身份证号码', trigger: 'blur' }
  ],
  patient_name: [{ required: true, message: '请输入真实姓名', trigger: 'blur' }],
  age: [
    { required: true, message: '请输入年龄', trigger: 'blur' },
    { type: 'number', message: '年龄必须为数字', trigger: 'change' }
  ],
  gender: [{ required: true, message: '请选择性别', trigger: 'change' }],
};

const handleSubmit = async () => {
  await identityFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      try {
        const res = await submitPatientIdentity(identityForm);
        if (res) {
          ElMessage.success('病人身份信息提交成功！');
          console.log('身份信息提交成功响应:', res);
          // 提交成功后可能根据需求做进一步跳转
        } else {
          ElMessage.error(res?.msg || '信息提交失败');
        }
      } catch (error) {
        ElMessage.error(error.msg || '信息提交请求失败');
        console.error('身份信息提交失败:', error);
      } finally {
        loading.value = false;
      }
    }
  });
};

const handleLogout = () => {
  // ⚡ 修正跳转路径/名称
  // 方式一：使用完整的路由路径
  router.push('/patient/login');
  // 方式二（推荐）：使用路由名称
  // router.push({ name: 'PatientLogin' }); 
  
  // ⚡ 额外建议：清空本地存储的认证信息，模拟真正退出登录
  // 例如：localStorage.removeItem('userToken');
  ElMessage.info('已退出登录');
};
</script>

<!-- (template and style remain unchanged) -->

<style scoped>
/* ========================================= */
/*             病人身份模块样式                */
/*        （沿用登录页的风格，并适配移动端）       */
/* ========================================= */
.patient-identity-container { 
  display: flex; 
  justify-content: center; 
  align-items: center; 
  min-height: 100vh;
  width: 100%; 
  background-color: #f0f2f5; 
  padding: 20px; 
  box-sizing: border-box; 
  flex-direction: column; /* 允许在内容过多时垂直排列 */
}
.identity-card { 
  width: 100%; 
  max-width: 500px; /* 卡片最大宽度略大一些，以容纳更多表单项 */
  border-radius: 12px; 
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); 
  overflow: hidden; 
}
.card-body { 
  padding: 30px; 
  padding-top: 10px; 
}
.identity-header { 
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
.subtitle { 
  font-size: 16px; 
  margin: 0; 
  opacity: 0.9; 
}
.submit-button { 
  width: 100%; 
  margin-top: 20px; /* 增加按钮上边距 */
}
.footer-actions { 
  text-align: center; 
  margin-top: 20px; 
}

/* 覆盖 Element Plus 默认样式 */
:deep(.el-card__header) { 
  padding: 0; 
  border-bottom: none; 
}
:deep(.el-card__body) { 
  padding: 0; 
}
:deep(.el-form-item) { 
  margin-bottom: 24px; 
}
:deep(.el-form-item__label) { 
  color: #333; 
  margin-bottom: 8px !important; 
  font-weight: 500; 
}
/* 分割线样式 */
:deep(.el-divider__text) {
  background-color: #fff;
  padding: 0 10px;
  color: #606266;
  font-size: 14px;
}
:deep(.el-divider) {
  margin: 30px 0;
}

/* ========================================= */
/*         🚀 移动端适配样式 🚀           */
/*  当屏幕宽度小于等于 768px 时应用以下样式  */
/* ========================================= */
@media (max-width: 768px) {
  .patient-identity-container {
    padding: 20px;   
  }
  .identity-card {
    max-width: 100%;
    box-shadow: none;
    border-radius: 0; 
    border: none;
  }
  .identity-header {
    padding: 25px 20px;
  }
  .title {
    font-size: 22px;
  }
  .subtitle {
    font-size: 14px;
  }
  .card-body {
    padding: 25px 20px 20px 20px;
  }
  .submit-button {
    margin-top: 15px;
  }
  :deep(.el-divider) {
    margin: 25px 0;
  }
  :deep(.el-form-item) { 
    margin-bottom: 20px; 
  }
}

/* ========================================= */
/*     为屏幕特别窄的手机做进一步优化      */
/*  当屏幕宽度小于等于 375px 时应用以下样式  */
/* ========================================= */
@media (max-width: 375px) {
  .identity-header {
    padding: 20px;
    gap: 10px;
  }
  .title {
    font-size: 20px;
  }
  .subtitle {
    font-size: 13px;
  }
  .card-body {
    padding: 20px 15px;
  }
  :deep(.el-form-item) {
    margin-bottom: 18px;
  }
  :deep(.el-divider) {
    margin: 20px 0;
  }
}
</style>