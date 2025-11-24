<template>
  <div class="diagnosis-report">
    <div class="header">
      <h2>提交诊断结果</h2>
      <button @click="goBack" class="back-btn">返回病情摘要</button>
    </div>

    <!-- 加载状态（含错误提示） -->
    <div v-if="loading" class="loading">
      <div v-if="errorMsg" class="error">{{ errorMsg }}</div>
      <div v-else>提交中...</div>
    </div>

    <!-- 表单区域（加载状态隐藏） -->
    <div v-else class="form-container">
      <!-- 错误提示 -->
      <div v-if="errorMsg" class="error">{{ errorMsg }}</div>

      <!-- 诊断内容表单 -->
      <form @submit.prevent="handleSubmit" class="report-form">
        <div class="form-item">
          <label class="form-label">待诊记录ID：</label>
          <span class="record-id">{{ recordId }}</span> <!-- 展示当前记录ID，不可编辑 -->
        </div>
        <div class="form-item">
          <label class="form-label required">诊断内容：</label>
          <textarea
            v-model="diagnosisText"
            class="form-textarea"
            placeholder="请输入诊断结果（如：建议居家休息，按时服药，3天后复诊）"
            rows="6"
            :disabled="submitting"
          ></textarea>
          <div v-if="formError.text" class="form-error">{{ formError.text }}</div>
        </div>
        <div class="form-actions">
          <button type="submit" class="submit-btn" :disabled="submitting">
            提交诊断结果
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { submitDiagnosisReport } from '../api/report';
import type { SubmitReportParams, SubmitReportResponse } from '../api/report'; // 导入嵌套响应类型

// 路由实例（获取参数+跳转）
const route = useRoute();
const router = useRouter();

// 响应式变量：调整loading初始值为true，确保页面加载时先进入加载状态
const loading = ref(true); // 整体加载状态（含无record_id的初始检查）
const submitting = ref(false); // 提交按钮加载状态
const errorMsg = ref(''); // 全局错误提示（如无record_id、登录失效）
const formError = ref({ text: '' }); // 表单字段校验错误

// 表单数据：与SubmitReportParams参数类型对齐
const recordId = ref(''); // 待诊记录ID（从路由参数获取，必填）
const diagnosisText = ref(''); // 诊断内容（必填）

/**
 * 返回上一页（病情摘要页面）
 */
const goBack = () => {
  router.push(`/doctor/summary/${recordId.value}`);
};

/**
 * 表单校验：验证诊断内容必填且长度合规
 */
const validateForm = (): boolean => {
  formError.value = { text: '' };
  let isValid = true;

  // 校验诊断内容不为空
  if (!diagnosisText.value.trim()) {
    formError.value.text = '请输入诊断内容';
    isValid = false;
  }
  // 校验诊断内容长度（至少5个字符，避免无效内容）
  else if (diagnosisText.value.trim().length < 5) {
    formError.value.text = '诊断内容至少5个字符';
    isValid = false;
  }

  return isValid;
};

/**
 * 提交诊断结果：校验→调用API→处理结果
 */
const handleSubmit = async () => {
  // 1. 先做表单前端校验
  if (!validateForm()) return;

  // 2. 组装提交参数（严格匹配SubmitReportParams类型）
  const submitParams: SubmitReportParams = {
    record_id: recordId.value,
    text: diagnosisText.value.trim()
  };

  try {
    submitting.value = true;
    errorMsg.value = '';

    // 3. 调用API提交（响应为嵌套结构：base + ...）
    const res = await submitDiagnosisReport(submitParams);

    // 4. 处理接口返回结果：适配嵌套结构的base层级
    if (res.base.code === '10000') {
      alert('诊断结果提交成功！' + res.base.msg);
      // 提交成功后跳转回待诊列表
      router.push('/doctor/queue');
    } else {
      // 接口返回失败（如参数错误、后端异常）
      errorMsg.value = res.base.msg || '提交诊断结果失败，请重试';
    }
  } catch (error: any) {
    // 捕获网络异常（如后端未启动、跨域问题）
    errorMsg.value = error.base?.msg || '网络异常，请稍后重试';
    console.error('提交诊断结果失败：', error);
  } finally {
    submitting.value = false;
  }
};

/**
 * 页面挂载时：获取路由参数+验证登录状态
 */
onMounted(() => {
  try {
    // 1. 从路由参数中获取record_id（必填）
    const id = route.params.record_id as string;
    if (!id) {
      errorMsg.value = '缺少待诊记录ID，无法提交诊断结果';
      // 1.5秒后自动跳转回待诊列表，并终止加载状态以显示错误提示
      setTimeout(() => {
        router.push('/doctor/queue');
        loading.value = false;
      }, 1500);
      return;
    }
    recordId.value = id;

    // 2. 验证登录状态（未登录则跳回登录页）
    const token = localStorage.getItem('doctorToken');
    if (!token) {
      errorMsg.value = '未登录，请重新登录';
      setTimeout(() => {
        router.push('/doctor/login');
        loading.value = false;
      }, 1500);
      return;
    }

    // 3. 加载完成，显示表单
    loading.value = false;
  } catch (error) {
    errorMsg.value = '页面加载失败，请稍后重试';
    setTimeout(() => {
      router.push('/doctor/queue');
      loading.value = false;
    }, 1500);
  }
});
</script>

<style scoped>
/* 样式部分与原代码一致，无需修改 */
.diagnosis-report {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.back-btn {
  padding: 8px 16px;
  background-color: #666;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.back-btn:hover {
  background-color: #444;
}

.loading {
  text-align: center;
  padding: 60px;
  color: #666;
  font-size: 16px;
}

.error {
  text-align: center;
  padding: 16px;
  color: #f56c6c;
  font-size: 14px;
  margin-bottom: 16px;
  background-color: #fff1f0;
  border-radius: 4px;
}

.form-container {
  background-color: #fff;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.report-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-weight: 600;
  color: #333;
  font-size: 14px;
}

.form-label.required::after {
  content: '*';
  color: #f56c6c;
  margin-left: 4px;
}

.record-id {
  color: #666;
  font-size: 16px;
  padding: 8px 12px;
  background-color: #f9f9f9;
  border-radius: 4px;
  border: 1px solid #eee;
}

.form-textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  color: #333;
  resize: vertical;
  transition: border-color 0.3s;
}

.form-textarea:focus {
  outline: none;
  border-color: #409eff;
}

.form-textarea:disabled {
  background-color: #f9f9f9;
  cursor: not-allowed;
}

.form-error {
  color: #f56c6c;
  font-size: 13px;
  margin-top: 4px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 8px;
}

.submit-btn {
  padding: 10px 24px;
  background-color: #409eff;
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.submit-btn:hover {
  background-color: #3086d6;
}

.submit-btn:disabled {
  background-color: #a0cfff;
  cursor: not-allowed;
}
</style>