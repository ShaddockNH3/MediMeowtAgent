<!-- D:\code\ruangong\new\src\apps\patient_app\PatientLogin.vue -->
<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="login-header">
          <el-icon :size="50" color="white"><UserFilled /></el-icon>
          <h1 class="title">智能问诊系统</h1>
          <p class="subtitle">欢迎</p>
        </div>
      </template>

      <div class="card-body">
        <!-- 登录表单 -->
        <el-form :model="loginForm" :rules="loginRules" ref="loginFormRef" label-position="top" class="login-form">
          <el-form-item label="用户名" prop="email">
            <el-input v-model="loginForm.email" placeholder="请输入用户名" size="large" clearable />
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" size="large" show-password />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleLogin" class="login-button" size="large" :loading="loading">
              登录
            </el-button>
          </el-form-item>
        </el-form>
        <div class="footer-actions">
          <el-link type="primary" @click="registerDialogVisible = true">没有账号？立即注册</el-link>
        </div>
      </div>
    </el-card>

    <!-- 注册弹窗 -->
    <el-dialog v-model="registerDialogVisible" title="新用户注册" width="400px" center @closed="resetRegisterForm">
      <el-form :model="registerForm" :rules="registerRules" ref="registerFormRef" label-position="top">
        <el-form-item label="邮箱/用户名" prop="email">
          <el-input v-model="registerForm.email" placeholder="设置您的账号" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="registerForm.password" type="password" placeholder="设置您的登录密码" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="registerForm.confirmPassword" type="password" placeholder="请再次输入密码" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="registerDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleRegister" :loading="loading">
          立即注册
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<!-- D:\code\ruangong\new\src\apps\patient_app\PatientLogin.vue -->
<!-- ... (template 和 script setup 的其他部分保持不变) ... -->

<script setup>
import { ref, reactive } from 'vue';
import { UserFilled } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';
import { login, register } from './api/PatientLoginAPI.js';
import { useRouter } from 'vue-router';

const router = useRouter();

const loading = ref(false);
const loginFormRef = ref(null);
const registerFormRef = ref(null);

const loginForm = reactive({ email: '', password: '' });
const registerForm = reactive({ email: '', password: '', confirmPassword: '' });

const registerDialogVisible = ref(false);

const validatePass = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'));
  } else if (value !== registerForm.password) {
    callback(new Error("两次输入的密码不一致!"));
  } else {
    callback();
  }
};

const loginRules = {
  email: [{ required: true, message: '请输入手机号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
};

// ======================= ✨ 核心修改区域 ✨ =======================
const registerRules = {
  // 手机号（email字段）的校验规则
  email: [
    { required: true, message: '请输入您的手机号', trigger: 'blur' },
    { pattern: /^1\d{10}$/, message: '请输入正确的11位手机号', trigger: 'blur' }
  ],
  // 密码的校验规则
  password: [
    { required: true, message: '请输入您的密码', trigger: 'blur' },
    { min: 6, max: 18, message: '密码长度需为 6-18 位', trigger: 'blur' }
  ],
  // 确认密码的校验规则 (保持不变)
  confirmPassword: [
    { required: true, validator: validatePass, trigger: 'blur' }
  ],
};
const handleLogin = async () => {
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      try {
        const res = await login(loginForm);
        // ======================= ✨ 最终修正 ✨ =======================
        // 根据您提供的后端返回结构 { base: { code: '...', msg: '...' } } 进行判断
        if (res && res.base && res.base.code === '10000') {
          ElMessage.success(res.base.msg || '登录成功！');
          console.log('登录成功响应:', res);
          router.push({ name: 'PatientIdentity' });
        } else {
          // 如果失败，显示后端返回的错误信息
          ElMessage.error(res?.base?.msg || '登录失败：用户名或密码错误');
        }
        // =============================================================
      } catch (error) {
        ElMessage.error(error?.base?.msg || '登录请求失败，请检查网络连接');
        console.error('登录失败响应:', error);
      } finally {
        loading.value = false;
      }
    }
  });
};

const handleRegister = async () => {
  await registerFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      try {
        const res = await register(registerForm);
        // ======================= ✨ 最终修正 ✨ =======================
        // 根据您提供的后端返回结构 { base: { code: '...', msg: '...' } } 进行判断
        if (res && res.base && res.base.code === '10000') {
          ElMessage.success(res.base.msg || '注册成功！请登录。');
          console.log('注册成功响应:', res);
          registerDialogVisible.value = false;
          loginForm.email = registerForm.email;
          loginForm.password = '';
        } else {
          // 如果失败，显示后端返回的错误信息
          ElMessage.error(res?.base?.msg || '注册失败：该用户已存在');
        }
        // =============================================================
      } catch (error) {
        ElMessage.error(error?.base?.msg || '注册请求失败，请检查网络连接');
        console.error('注册失败响应:', error);
      } finally {
        loading.value = false;
      }
    }
  });
};

const resetRegisterForm = () => {
  registerFormRef.value?.resetFields();
}
</script>
<!-- ... (style 部分保持不变) ... -->

<style scoped>
/* 桌面端基础样式 (保持不变) */
.login-container { 
  display: flex; 
  justify-content: center; 
  align-items: center; 
  min-height: 100vh; /* 使用 min-height 避免移动端浏览器地址栏影响 */
  width: 100%; 
  background-color: #f0f2f5; 
  padding: 20px; /* 为小屏幕增加一些边距 */
  box-sizing: border-box; /* 确保 padding 不会增加总宽度 */
}
.login-card { 
  width: 100%; /* 基础宽度设为100% */
  max-width: 420px; /* 最大宽度限制，保证桌面端效果 */
  border-radius: 12px; 
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); 
  overflow: hidden; 
}
.card-body { 
  padding: 30px; 
  padding-top: 10px; 
}
.login-header { 
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
.login-button { 
  width: 100%; 
  margin-top: 10px; 
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

/* ========================================= */
/*         🚀 移动端适配样式 🚀           */
/*  当屏幕宽度小于等于 768px 时应用以下样式  */
/* ========================================= */
@media (max-width: 768px) {
  .login-container {
    /* 关键修改：在移动端同样保持垂直居中 */
    align-items: center;   
    /* 保持水平居中 */
    justify-content: center;   
    /* 保留一些内边距，防止内容紧贴屏幕边缘 */
    padding: 20px;   
    /* 恢复背景色，使页面在内容较短时更美观 */
    background-color: #f0f2f5;   
  }

  .login-card {
    /* 移除桌面端的卡片样式，实现接近全屏效果但保持一点间距 */
    max-width: 100%;
    box-shadow: none;
    border-radius: 0; /* 移动端通常不需要圆角，使其与页面背景统一 */
    border: none;
  }

  .login-header {
    /* 减少头部的垂直内边距 */
    padding: 25px 20px;
  }

  .title {
    /* 缩小标题字体大小 */
    font-size: 22px;
  }

  .card-body {
    /* 减少内容区域的内边距 */
    padding: 25px 20px 20px 20px;
  }
}

/* ========================================= */
/*     为屏幕特别窄的手机做进一步优化      */
/*  当屏幕宽度小于等于 375px 时应用以下样式  */
/* ========================================= */
@media (max-width: 375px) {
  .login-header {
    padding: 20px;
    gap: 10px;
  }
  .title {
    font-size: 20px;
  }
  .subtitle {
    font-size: 14px;
  }
  .card-body {
    padding: 20px 15px;
  }
  :deep(.el-form-item) {
    margin-bottom: 20px;
  }
}
</style>