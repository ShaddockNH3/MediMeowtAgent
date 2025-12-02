<template>
  <div class="import-questionnaire-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <h2 class="page-title">导入问卷</h2>
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
        <div class="sidebar-item" @click="goToRecord">
          <i class="icon icon-record">📄</i>
          <span>电子病历</span>
        </div>
        <div class="sidebar-item active">
          <i class="icon icon-questionnaire">📊</i>
          <span>问卷管理</span>
        </div>
      </aside>

      <!-- 右侧核心内容区 -->
      <main class="import-content">
        <!-- 加载状态 -->
        <div v-if="loading" class="loading-state">
          <span class="loading-spinner">🔄</span>
          <p>导入中...</p>
        </div>

        <!-- 导入表单区域 -->
        <div v-else class="import-container">
          <!-- 错误提示 -->
          <div v-if="errorMsg" class="error-alert">
            <span class="error-icon">⚠️</span>
            <p>{{ errorMsg }}</p>
          </div>

          <!-- 文件上传模块 -->
          <div class="upload-module">
            <h3 class="module-title">问卷文件上传</h3>
            
            <!-- 美化文件选择区域 -->
            <div class="file-upload-area">
              <input
                type="file"
                accept=".xlsx"
                class="file-input"
                @change="handleFileChange"
              >
              <div class="upload-hint">
                <span class="upload-icon">📤</span>
                <p>点击或拖拽文件至此处上传</p>
                <p class="upload-tip">支持.xlsx格式，单个文件不超过10MB</p>
              </div>
            </div>

            <!-- 已选择文件信息 -->
            <div v-if="selectedFile" class="file-info">
              <div class="file-details">
                <span class="file-name">{{ selectedFile.name }}</span>
                <span class="file-size">({{ formatFileSize(selectedFile.size) }})</span>
              </div>
              <button @click="clearFile" class="clear-file-btn">×</button>
            </div>
          </div>

          <!-- 操作按钮组 -->
          <div class="btn-group">
            <button @click="goBack" class="back-btn" :disabled="submitting">
              返回主页
            </button>
            <button 
              @click="handleImport" 
              class="import-btn" 
              :disabled="!selectedFile || submitting"
            >
              <span v-if="submitting" class="loading-icon">🔄</span>
              {{ submitting ? '导入中...' : '开始导入' }}
            </button>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { importQuestionnaire } from '../api/questionnaire';
import type { ImportQuestionnaireResponse } from '../api/questionnaire';

const router = useRouter();
const selectedFile = ref<File | null>(null); 
const loading = ref(false); 
const submitting = ref(false); 
const errorMsg = ref(''); 

// 医生信息
const doctorInfo = computed(() => {
  const info = localStorage.getItem('doctorInfo');
  return info ? JSON.parse(info) : { username: '张医生', department: '呼吸内科' };
});
const doctorName = computed(() => doctorInfo.value.username);
const doctorDept = computed(() => doctorInfo.value.department);

/** 侧边栏跳转函数 - 修复路径和参数问题 */
const goToQueue = () => router.push('/doctor/queue');

const goToDetail = () => {
  // 尝试从localStorage获取最近的患者recordId（若有）
  const recentRecordId = localStorage.getItem('recentRecordId');
  if (recentRecordId) {
    router.push(`/doctor/summary/${recentRecordId}`);
  } else {
    errorMsg.value = '请先从患者队列选择患者';
    setTimeout(() => router.push('/doctor/queue'), 1500);
  }
};

const goToRecord = () => {
  // 尝试从localStorage获取最近的患者recordId（若有）
  const recentRecordId = localStorage.getItem('recentRecordId');
  if (recentRecordId) {
    router.push(`/doctor/report/${recentRecordId}`);
  } else {
    errorMsg.value = '请先从患者队列选择患者';
    setTimeout(() => router.push('/doctor/queue'), 1500);
  }
};

/** 返回医生主页 */
const goBack = () => {
  router.push('/doctor');
};

/** 处理文件选择变化 */
const handleFileChange = (e: Event) => {
  const target = e.target as HTMLInputElement;
  if (target.files && target.files[0]) {
    const file = target.files[0];
    if (file.type !== 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' && !file.name.endsWith('.xlsx')) {
      errorMsg.value = '仅支持.xlsx格式文件，请重新选择';
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      errorMsg.value = '文件大小超过10MB限制，请选择更小的文件';
      return;
    }
    selectedFile.value = file;
    errorMsg.value = ''; 
  }
};

/** 清除已选择的文件 */
const clearFile = () => {
  selectedFile.value = null;
  const fileInput = document.querySelector('.file-input') as HTMLInputElement;
  if (fileInput) fileInput.value = '';
};

/** 格式化文件大小 */
const formatFileSize = (size: number): string => {
  if (size < 1024) return `${size} B`;
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
  return `${(size / (1024 * 1024)).toFixed(1)} MB`;
};

/** 触发问卷导入逻辑 */
const handleImport = async () => {
  if (!selectedFile.value) {
    errorMsg.value = '请选择要导入的问卷文件';
    return;
  }

  try {
    submitting.value = true;
    errorMsg.value = '';

    const res: ImportQuestionnaireResponse = await importQuestionnaire(selectedFile.value);
    if (res.base.code === '10000') {
      alert(`问卷导入成功！${res.base.msg}`);
      router.push('/doctor'); 
    } else {
      errorMsg.value = res.base.msg || '问卷导入失败，请重试';
    }
  } catch (error: any) {
    errorMsg.value = error.message || '网络异常，请稍后重试';
  } finally {
    submitting.value = false;
  }
};
</script>

<style scoped>
/* 页面整体样式 */
.import-questionnaire-page {
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

/* 右侧导入内容区 */
.import-content {
  flex: 1;
  padding: 24px;
}

/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.loading-spinner {
  font-size: 28px;
  color: #1890ff;
  margin-bottom: 12px;
  animation: spin 1.5s linear infinite;
}

/* 导入容器 */
.import-container {
  background-color: #fff;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

/* 错误提示 */
.error-alert {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  color: #ef4444;
  font-size: 14px;
  background-color: #fff1f0;
  border-radius: 6px;
  border: 1px solid #fecdd3;
  margin-bottom: 20px;
}

.error-icon {
  font-size: 18px;
  flex-shrink: 0;
}

/* 上传模块 */
.upload-module {
  margin-bottom: 24px;
}

.module-title {
  font-size: 16px;
  font-weight: 600;
  color: #1d2129;
  margin-bottom: 16px;
}

/* 文件上传区域 */
.file-upload-area {
  position: relative;
  border: 2px dashed #e5e9f2;
  border-radius: 8px;
  padding: 40px 20px;
  text-align: center;
  background-color: #f8fafc;
  transition: all 0.2s;
  cursor: pointer;
}

.file-upload-area:hover {
  border-color: #1890ff;
  background-color: #f0f9ff;
}

.file-input {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
  z-index: 1;
}

.upload-hint {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.upload-icon {
  font-size: 32px;
  color: #1890ff;
  margin-bottom: 8px;
}

.upload-hint p {
  margin: 0;
  color: #64748b;
  font-size: 14px;
}

.upload-tip {
  font-size: 12px;
  color: #94a3b8;
}

/* 已选择文件信息 */
.file-info {
  margin-top: 16px;
  padding: 12px;
  background-color: #f8fafc;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border: 1px solid #e5e9f2;
}

.file-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.file-name {
  font-size: 14px;
  color: #1d2129;
  font-weight: 500;
}

.file-size {
  font-size: 12px;
  color: #94a3b8;
}

.clear-file-btn {
  background: transparent;
  border: none;
  color: #94a3b8;
  font-size: 16px;
  cursor: pointer;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.clear-file-btn:hover {
  background-color: #f1f5f9;
  color: #ef4444;
}

/* 按钮组 */
.btn-group {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
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

.import-btn {
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

.import-btn:disabled {
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
  .btn-group {
    flex-direction: column;
  }
  .back-btn, .import-btn {
    width: 100%;
  }
}
</style>