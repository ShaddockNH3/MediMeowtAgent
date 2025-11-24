<template>
  <div class="questionnaire-import">
    <div class="header">
      <h2>导入问卷</h2>
      <button @click="goBack" class="back-btn">返回医生主页</button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading">导入中...</div>

    <!-- 表单区域 -->
    <div v-else class="import-container">
      <!-- 错误提示 -->
      <div v-if="errorMsg" class="error">{{ errorMsg }}</div>

      <div class="form-item">
        <label class="form-label">选择问卷文件（仅支持.xlsx格式）：</label>
        <input
          type="file"
          accept=".xlsx"
          class="file-input"
          @change="handleFileChange"
        >
        <div v-if="selectedFile" class="file-info">已选择：{{ selectedFile.name }}</div>
      </div>

      <div class="form-actions">
        <button 
          @click="handleImport" 
          class="import-btn" 
          :disabled="!selectedFile || submitting"
        >
          {{ submitting ? '导入中...' : '开始导入' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { importQuestionnaire } from '../api/questionnaire';
import type { ImportQuestionnaireResponse } from '../api/questionnaire';

const router = useRouter();
const selectedFile = ref<File | null>(null); // 存储选中的文件
const loading = ref(false); // 整体加载状态
const submitting = ref(false); // 提交按钮加载状态
const errorMsg = ref(''); // 错误提示信息

/** 返回医生主页 */
const goBack = () => {
  router.push('/doctor');
};

/** 处理文件选择变化 */
const handleFileChange = (e: Event) => {
  const target = e.target as HTMLInputElement;
  if (target.files && target.files[0]) {
    selectedFile.value = target.files[0];
    errorMsg.value = ''; // 清除之前的错误提示
  }
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

    // 调用API导入问卷（响应为嵌套结构：base + ...）
    const res = await importQuestionnaire(selectedFile.value);

    // 处理接口返回结果：适配嵌套结构的base层级
    if (res.base.code === '10000') {
      alert(`问卷导入成功！${res.base.msg}`);
      router.push('/doctor'); // 导入成功后返回医生主页
    } else {
      errorMsg.value = res.base.msg || '问卷导入失败，请重试';
    }
  } catch (error: any) {
    // 捕获网络异常或接口错误，优先读取error中的base.msg
    errorMsg.value = error.base?.msg || '网络异常，请稍后重试';
    console.error('问卷导入失败：', error);
  } finally {
    submitting.value = false;
  }
};
</script>

<style scoped>
.questionnaire-import {
  padding: 24px;
  max-width: 800px;
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

.import-container {
  background-color: #fff;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
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

.form-item {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.file-input {
  display: block;
  margin-bottom: 8px;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
}

.file-info {
  color: #666;
  font-size: 14px;
}

.form-actions {
  text-align: right;
}

.import-btn {
  padding: 10px 24px;
  background-color: #409eff;
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.import-btn:hover {
  background-color: #3086d6;
}

.import-btn:disabled {
  background-color: #a0cfff;
  cursor: not-allowed;
}
</style>