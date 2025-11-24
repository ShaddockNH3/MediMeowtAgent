<template>
  <div class="disease-summary">
    <div class="header">
      <h2>病情摘要</h2>
      <button @click="goBack" class="back-btn">返回待诊列表</button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading">加载病情摘要中...</div>

    <!-- 错误提示 -->
    <div v-else-if="errorMsg" class="error">{{ errorMsg }}</div>

    <!-- 病情摘要内容 -->
    <div v-else class="summary-container">
      <!-- 用户基本信息 -->
      <div class="user-info card">
        <h3>患者信息</h3>
        <div class="info-item">姓名：{{ userInfo.username }}</div>
        <div class="info-item">手机号：{{ userInfo.phone_number }}</div>
        <div class="info-item">注册时间：{{ formatTime(userInfo.created_at) }}</div>
      </div>

      <!-- AI病情摘要 -->
      <div class="ai-summary card">
        <h3>AI辅助诊断摘要</h3>
        <div class="summary-item">
          <span class="label">主诉概括：</span>
          <span class="content">{{ aiResult.key_info.chief_complaint }}</span>
        </div>
        <div class="summary-item">
          <span class="label">核心症状：</span>
          <span class="content">{{ aiResult.key_info.key_symptoms }}</span>
        </div>
        <div class="summary-item" v-if="aiResult.key_info.image_summary">
          <span class="label">图片概述：</span>
          <span class="content">{{ aiResult.key_info.image_summary }}</span>
        </div>
        <div class="summary-item warning">
          <span class="label">医生注意事项：</span>
          <span class="content">{{ aiResult.key_info.important_notes }}</span>
        </div>
        <div class="summary-item">
          <span class="label">科室匹配：</span>
          <span class="content">{{ aiResult.is_department ? '匹配' : '不匹配' }}</span>
        </div>
      </div>

      <!-- 提交诊断结果跳转按钮 -->
      <div class="summary-actions">
        <router-link :to="`/doctor/report/${route.params.record_id}`" class="report-btn">
          进入提交诊断结果
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { getDiseaseSummary } from '../api/summary';
import type { SummaryResponse, AiResult, User } from '../api/summary'; // 导入修正后的嵌套类型

// 路由实例（获取参数+跳转）
const route = useRoute();
const router = useRouter();

// 响应式变量：初始值与类型定义严格对齐
const loading = ref(true);
const errorMsg = ref('');
const userInfo = ref<User>({
  id: '',
  phone_number: '',
  username: '',
  created_at: '',
  updated_at: ''
});
const aiResult = ref<AiResult>({
  submission_id: '',
  is_department: true,
  key_info: {
    chief_complaint: '',
    key_symptoms: '',
    image_summary: undefined,
    important_notes: ''
  }
});

// 格式化时间（兼容空值）
const formatTime = (timeStr: string) => {
  if (!timeStr) return '暂无';
  return new Date(timeStr).toLocaleString();
};

// 返回待诊列表
const goBack = () => {
  router.push('/doctor/queue');
};

onMounted(async () => {
  try {
    // 1. 获取路由参数中的record_id（从待诊列表跳转携带）
    const recordId = route.params.record_id as string;
    if (!recordId) {
      errorMsg.value = '缺少待诊记录ID，无法获取病情摘要';
      setTimeout(() => goBack(), 1500);
      return;
    }

    // 2. 验证登录状态（仅校验token存在，实际请求由service自动携带）
    const token = localStorage.getItem('doctorToken');
    if (!token) {
      errorMsg.value = '未登录，请重新登录';
      setTimeout(() => router.push('/doctor/login'), 1500);
      return;
    }

    // 3. 调用API获取病情摘要（响应为嵌套结构：base + data）
    const res = await getDiseaseSummary(recordId);
    
    // 4. 处理响应结果：适配嵌套结构的base和data层级
    if (res.base.code === '10000') {
      userInfo.value = res.data.user; // 从data层级读取user
      aiResult.value = res.data.ai_result; // 从data层级读取ai_result
    } else {
      errorMsg.value = res.base.msg || '获取病情摘要失败';
    }
  } catch (error) {
    errorMsg.value = '网络异常，请稍后重试';
    console.error('获取病情摘要失败：', error);
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.disease-summary {
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
  padding: 60px;
  color: #f56c6c;
  font-size: 16px;
}

.summary-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card {
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.card h3 {
  margin: 0 0 16px 0;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 8px;
}

.info-item {
  margin-bottom: 8px;
  color: #666;
}

.summary-item {
  margin-bottom: 12px;
  display: flex;
  flex-wrap: wrap;
}

.summary-item .label {
  font-weight: 600;
  color: #333;
  min-width: 100px;
}

.summary-item .content {
  color: #666;
  flex: 1;
}

.warning {
  background-color: #fff8f0;
  padding: 12px;
  border-radius: 4px;
}

.warning .content {
  color: #e6a23c;
}

/* 提交诊断按钮样式 */
.summary-actions {
  margin-top: 8px;
  text-align: right;
}

.report-btn {
  display: inline-block;
  padding: 10px 24px;
  background-color: #409eff;
  color: #fff;
  text-decoration: none;
  border-radius: 4px;
  font-size: 16px;
  transition: background-color 0.3s;
}

.report-btn:hover {
  background-color: #3086d6;
}
</style>