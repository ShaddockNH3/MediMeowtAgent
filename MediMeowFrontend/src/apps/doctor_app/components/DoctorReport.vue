<template>
  <div class="medical-record-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <h2 class="page-title">电子病历生成</h2>
      <div class="doctor-info">
        <span class="doctor-name">{{ doctorName }}</span> | 
        <span class="department">{{ doctorDept }}</span>
      </div>
    </div>

    <div class="content-wrapper">
      <!-- 左侧侧边栏（匹配图片样式） -->
      <aside class="sidebar">
        <!-- 侧边栏标题（医生工作站） -->
        <div class="sidebar-header">
          <i class="icon icon-station">👨‍⚕️</i>
          <span>医生工作站</span>
        </div>
        <!-- 菜单项 -->
        <div class="sidebar-item" @click="goToQueue">
          <i class="icon icon-queue">📋</i>
          <span>患者队列</span>
        </div>
        <div class="sidebar-item" @click="goToDetail">
          <i class="icon icon-detail">👤</i>
          <span>患者详情</span>
        </div>
        <div class="sidebar-item active">
          <i class="icon icon-record">📄</i>
          <span>电子病历</span>
        </div>
        <div class="sidebar-item" @click="goToQuestionnaire">
          <i class="icon icon-questionnaire">📊</i>
          <span>问卷管理</span>
        </div>
      </aside>

      <!-- 右侧病历内容区 -->
      <main class="record-content">
        <!-- 加载/错误状态 -->
        <div v-if="loading" class="loading-state">
          <span class="loading-spinner">🔄</span>
          <p v-if="errorMsg">{{ errorMsg }}</p>
          <p v-else>加载中...</p>
        </div>

        <!-- 病历表单 -->
        <div v-else class="record-form">
          <!-- 患者信息 -->
          <div class="patient-info">
            <span class="label">待诊记录ID：</span>
            <span class="value">{{ recordId }}</span>
          </div>
          <p class="hint-text">请完善以下病历信息：</p>

          <!-- 表单模块 -->
          <form @submit.prevent="handleSubmit" class="form-modules">
            <!-- 1. 主诉 -->
            <div class="form-module">
              <label class="module-label">主诉</label>
              <textarea
                v-model="formData.chiefComplaint"
                class="module-textarea"
                :disabled="submitting"
                placeholder="如：发热3天，伴咳嗽、咽痛"
              ></textarea>
            </div>

            <!-- 2. 现病史 -->
            <div class="form-module">
              <label class="module-label">现病史</label>
              <textarea
                v-model="formData.presentIllness"
                class="module-textarea"
                :disabled="submitting"
                placeholder="详细描述发病过程、症状变化等"
                rows="3"
              ></textarea>
            </div>

            <!-- 3. 既往史 -->
            <div class="form-module">
              <label class="module-label">既往史</label>
              <textarea
                v-model="formData.pastIllness"
                class="module-textarea"
                :disabled="submitting"
                placeholder="如：既往体健，无高血压、糖尿病史"
              ></textarea>
            </div>

            <!-- 4. 体格检查 -->
            <div class="form-module">
              <label class="module-label">体格检查</label>
              <textarea
                v-model="formData.physicalExam"
                class="module-textarea"
                :disabled="submitting"
                placeholder="如：体温38.5℃，咽部充血，扁桃体Ⅰ度肿大"
              ></textarea>
            </div>

            <!-- 5. 辅助检查 -->
            <div class="form-module">
              <label class="module-label">辅助检查</label>
              <textarea
                v-model="formData.auxiliaryExam"
                class="module-textarea"
                :disabled="submitting"
                placeholder="如：血常规：WBC 12.0×10⁹/L，中性粒细胞80%"
              ></textarea>
            </div>

            <!-- 6. 初步诊断（必填） -->
            <div class="form-module required">
              <label class="module-label">
                初步诊断
                <span class="required-mark">*</span>
              </label>
              <textarea
                v-model="formData.initialDiagnosis"
                class="module-textarea"
                :disabled="submitting"
                placeholder="如：急性上呼吸道感染"
              ></textarea>
              <div v-if="formError.initialDiagnosis" class="error-tip">
                {{ formError.initialDiagnosis }}
              </div>
            </div>

            <!-- 7. 处理意见（必填） -->
            <div class="form-module required">
              <label class="module-label">
                处理意见
                <span class="required-mark">*</span>
              </label>
              <textarea
                v-model="formData.treatmentAdvice"
                class="module-textarea"
                :disabled="submitting"
                placeholder="如：1. 布洛芬缓释胶囊 0.3g 口服 bid；2. 多饮水，休息；3. 3天后复诊"
                rows="3"
              ></textarea>
              <div v-if="formError.treatmentAdvice" class="error-tip">
                {{ formError.treatmentAdvice }}
              </div>
            </div>

            <!-- 操作按钮 -->
            <div class="btn-group">
              <button type="button" class="back-btn" @click="goBack" :disabled="submitting">
                返回详情
              </button>
              <button type="submit" class="submit-btn" :disabled="submitting">
                <span v-if="submitting" class="loading-icon">🔄</span>
                提交病历
              </button>
            </div>
          </form>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { submitDiagnosisReport } from '../api/report';
import type { SubmitReportParams, SubmitReportResponse } from '../api/report';

const route = useRoute();
const router = useRouter();

// 响应式状态
const loading = ref(true);
const submitting = ref(false);
const errorMsg = ref('');
const formError = ref({ initialDiagnosis: '', treatmentAdvice: '' });

// 医生信息
const doctorInfo = computed(() => {
  const info = localStorage.getItem('doctorInfo');
  return info ? JSON.parse(info) : { username: '张医生', department: '呼吸内科' };
});
const doctorName = computed(() => doctorInfo.value.username);
const doctorDept = computed(() => doctorInfo.value.department);

// 病历表单数据
const formData = ref({
  chiefComplaint: '',    // 主诉
  presentIllness: '',    // 现病史
  pastIllness: '',       // 既往史
  physicalExam: '',      // 体格检查
  auxiliaryExam: '',     // 辅助检查
  initialDiagnosis: '',  // 初步诊断（必填）
  treatmentAdvice: ''    // 处理意见（必填）
});

// 待诊记录ID
const recordId = ref('');

/** 侧边栏跳转函数 - 修复路径和参数问题 */
const goToQueue = () => router.push('/doctor/queue');
const goToDetail = () => {
  if (recordId.value) {
    router.push(`/doctor/summary/${recordId.value}`);
  } else {
    errorMsg.value = '缺少患者记录ID，无法跳转至详情';
    setTimeout(() => router.push('/doctor/queue'), 1500);
  }
};
const goToQuestionnaire = () => router.push('/doctor/questionnaire/import'); // 修正为有效路径

/** 返回患者详情页 */
const goBack = () => {
  router.push(`/doctor/summary/${recordId.value}`);
};

/** 表单校验 */
const validateForm = (): boolean => {
  formError.value = { initialDiagnosis: '', treatmentAdvice: '' };
  let isValid = true;
  if (!formData.value.initialDiagnosis.trim()) {
    formError.value.initialDiagnosis = '请填写初步诊断';
    isValid = false;
  }
  if (!formData.value.treatmentAdvice.trim()) {
    formError.value.treatmentAdvice = '请填写处理意见';
    isValid = false;
  }
  return isValid;
};

/** 提交病历 */
const handleSubmit = async () => {
  if (!validateForm()) return;
  if (submitting.value) return;

  try {
    submitting.value = true;
    errorMsg.value = '';

    const diagnosisText = `
【主诉】${formData.value.chiefComplaint || '无'}

【现病史】${formData.value.presentIllness || '无'}

【既往史】${formData.value.pastIllness || '无'}

【体格检查】${formData.value.physicalExam || '无'}

【辅助检查】${formData.value.auxiliaryExam || '无'}

【初步诊断】${formData.value.initialDiagnosis}

【处理意见】${formData.value.treatmentAdvice}
    `.trim();

    const submitParams: SubmitReportParams = {
      record_id: recordId.value,
      text: diagnosisText
    };

    const res: SubmitReportResponse = await submitDiagnosisReport(submitParams);
    if (res.base.code === '10000') {
      alert('病历提交成功！');
      router.push('/doctor/queue');
    } else {
      errorMsg.value = res.base.msg || '提交失败，请重试';
    }
  } catch (err: any) {
    errorMsg.value = err.message || '网络异常，请稍后重试';
  } finally {
    submitting.value = false;
  }
};

/** 页面挂载 */
onMounted(() => {
  try {
    const id = route.params.record_id as string;
    if (!id) throw new Error('缺少待诊记录ID');
    recordId.value = id;

    const token = localStorage.getItem('doctorToken');
    if (!token) throw new Error('未登录，请重新登录');

    loading.value = false;
  } catch (err: any) {
    errorMsg.value = err.message || '页面加载失败';
    setTimeout(() => router.push('/doctor/queue'), 1500);
  }
});
</script>

<style scoped>
/* 页面整体样式 */
.medical-record-page {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background-color: #f5f7fa;
  min-height: 100vh;
}

/* 头部样式 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background-color: #fff;
  border-bottom: 1px solid #e5e9f2;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #1d2129;
  margin: 0;
}

.doctor-info {
  font-size: 14px;
  color: #86909c;
}

/* 内容容器 */
.content-wrapper {
  display: flex;
}

/* 左侧侧边栏（匹配图片样式） */
.sidebar {
  width: 180px;
  background-color: #0F2E57; /* 图片同款深蓝色背景 */
  color: #fff;
  padding: 0;
  box-shadow: 2px 0 8px rgba(0,0,0,0.1);
}

/* 侧边栏标题（医生工作站） */
.sidebar-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 16px 20px;
  font-size: 16px;
  font-weight: 600;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

/* 侧边栏菜单项 */
.sidebar-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 20px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s;
}

/* 选中项高亮 */
.sidebar-item.active {
  background-color: #1A4B8C; /* 选中项亮蓝色背景 */
}

.sidebar-item:hover:not(.active) {
  background-color: #153A69;
}

/* 侧边栏图标 */
.icon {
  font-size: 18px;
  width: 20px; /* 固定图标宽度，文字对齐 */
  text-align: center;
}

/* 右侧病历内容区 */
.record-content {
  flex: 1;
  padding: 24px;
}

/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.loading-spinner {
  font-size: 24px;
  color: #1890ff;
  margin-bottom: 8px;
  animation: spin 1.5s linear infinite;
}

/* 患者信息 */
.patient-info {
  font-size: 16px;
  margin-bottom: 8px;
}

.patient-info .label {
  font-weight: 500;
  color: #4e5969;
}

.patient-info .value {
  color: #1d2129;
}

.hint-text {
  font-size: 14px;
  color: #86909c;
  margin-bottom: 20px;
}

/* 表单模块样式 */
.form-modules {
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-module {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.module-label {
  font-weight: 500;
  color: #1d2129;
  font-size: 14px;
}

.module-textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #e5e9f2;
  border-radius: 4px;
  font-size: 14px;
  color: #1d2129;
  resize: vertical;
  min-height: 60px;
}

.module-textarea:disabled {
  background-color: #f5f7fa;
  color: #86909c;
  cursor: not-allowed;
}

/* 必填项样式 */
.required .module-label {
  position: relative;
}

.required-mark {
  color: #f5222d;
  font-size: 14px;
  margin-left: 4px;
}

/* 错误提示 */
.error-tip {
  font-size: 12px;
  color: #f5222d;
  margin-top: 4px;
}

/* 按钮组 */
.btn-group {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 12px;
}

.back-btn {
  padding: 8px 16px;
  background-color: #fff;
  border: 1px solid #e5e9f2;
  border-radius: 4px;
  color: #4e5969;
  cursor: pointer;
  font-size: 14px;
}

.submit-btn {
  padding: 8px 16px;
  background-color: #1890ff;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.submit-btn:disabled {
  background-color: #91d5ff;
  cursor: not-allowed;
}

.loading-icon {
  font-size: 14px;
  animation: spin 1.5s linear infinite;
}

/* 动画 */
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 响应式适配 */
@media (max-width: 768px) {
  .content-wrapper {
    flex-direction: column;
  }
  .sidebar {
    width: 100%;
    display: flex;
    flex-wrap: wrap;
  }
  .sidebar-header {
    width: 100%;
  }
  .sidebar-item {
    flex: 1;
    justify-content: center;
    padding: 12px 8px;
  }
}
</style>