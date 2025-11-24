<!-- 文件路径: src/apps/patient_app/PatientIdentity.vue -->
<template>
  <div class="patient-identity-container">
    <el-card class="identity-card">
      <template #header>
        <div class="identity-header">
          <el-icon :size="50" color="white"><User /></el-icon>
          <h1 class="title">完善个人信息</h1>
          <p class="subtitle">请填写真실信息，以便为您提供更好的服务</p>
        </div>
      </template>

      <div class="card-body">
        <el-form :model="identityForm" :rules="identityRules" ref="identityFormRef" label-position="top" class="identity-form">
          <el-divider>基本信息</el-divider>
          
          <el-form-item label="姓名" prop="username">
            <el-input v-model="identityForm.username" placeholder="请输入您的真实姓名" size="large" clearable />
          </el-form-item>

          <el-form-item label="性别" prop="gender">
            <el-select v-model="identityForm.gender" placeholder="请选择性别" size="large" style="width: 100%;">
              <el-option label="男" value="男"></el-option>
              <!-- 💡 核心修复：修正了此处的闭合标签，移除了多余的 '-' -->
              <el-option label="女" value="女"></el-option>
            </el-select>
          </el-form-item>
          
          <el-form-item label="出生年月日" prop="birth">
             <el-date-picker
              v-model="identityForm.birth"
              type="date"
              placeholder="请选择您的出生日期"
              size="large"
              style="width: 100%;"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>
          
          <el-form-item label="民族" prop="ethnicity">
            <el-input v-model="identityForm.ethnicity" placeholder="例如：汉族" size="large" clearable />
          </el-form-item>

          <el-form-item label="籍贯" prop="origin">
            <el-input v-model="identityForm.origin" placeholder="例如：广东省广州市" size="large" clearable />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="handleSubmit" class="submit-button" size="large" :loading="loading">
              提交并绑定信息
            </el-button>
          </el-form-item>
        </el-form>
        <div class="footer-actions">
          <el-link type="info" @click="handleBackToMain">返回主页</el-link>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { User } from '@element-plus/icons-vue';
import { submitPatientIdentity } from '../api/PatientIdentityAPI.js';

const router = useRouter();
const loading = ref(false);
const identityFormRef = ref(null);

const identityForm = reactive({
  username: '',   
  gender: '',
  birth: '',
  ethnicity: '',
  origin: ''
});

const identityRules = {
  username: [{ required: true, message: '请输入您的姓名', trigger: 'blur' }],
  gender: [{ required: true, message: '请选择您的性别', trigger: 'change' }],
  birth: [{ required: true, message: '请选择您的出生年月日', trigger: 'change' }],
  ethnicity: [{ required: true, message: '请输入您的民族', trigger: 'blur' }],
  origin: [{ required: true, message: '请输入您的籍贯', trigger: 'blur' }],
};

const handleSubmit = async () => {
  await identityFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      try {
        const res = await submitPatientIdentity(identityForm);
        if (res && res.base && res.base.code === '10000') {
          ElMessage.success(res.base.msg || '个人信息绑定成功！');
          router.push({ name: 'PatientMain' });
        } else {
          ElMessage.error(res?.base?.msg || '信息绑定失败');
        }
      } catch (error) {
        ElMessage.error(error?.base?.msg || '信息绑定请求失败');
        console.error('信息绑定失败:', error);
      } finally {
        loading.value = false;
      }
    }
  });
};

const handleBackToMain = () => {
  router.push({ name: 'PatientMain' }); 
};
</script>

<style scoped>
/* 样式部分保持不变 */
.patient-identity-container { 
  display: flex; 
  justify-content: center; 
  align-items: center; 
  min-height: 100vh;
  width: 100%; 
  background-color: #f0f2f5; 
  padding: 20px; 
  box-sizing: border-box; 
  flex-direction: column;
}
.identity-card { 
  width: 100%; 
  max-width: 500px;
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
  margin-top: 20px;
}
.footer-actions { 
  text-align: center; 
  margin-top: 20px; 
}
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
:deep(.el-divider__text) {
  background-color: #fff;
  padding: 0 10px;
  color: #606266;
  font-size: 14px;
}
:deep(.el-divider) {
  margin: 30px 0;
}
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