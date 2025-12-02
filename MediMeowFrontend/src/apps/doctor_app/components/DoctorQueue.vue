<template>
  <div class="queue-page">
    <!-- 页面头部（与其他页面统一） -->
    <div class="page-header">
      <h2 class="page-title">患者队列</h2>
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
        <div class="sidebar-item active">
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
        <div class="sidebar-item" @click="goToQuestionnaire">
          <i class="icon icon-questionnaire">📊</i>
          <span>问卷管理</span>
        </div>
      </aside>

      <!-- 右侧队列内容区 -->
      <main class="queue-content">
        <div class="queue-container">
          <div class="loading" v-if="loading">加载中...</div>
          <div class="error" v-if="errorMsg">{{ errorMsg }}</div>
          <ul class="queue-list" v-else>
            <li v-for="recordId in recordIds" :key="recordId">
              待诊患者 ID：{{ recordId }}
              <router-link :to="`/doctor/summary/${recordId}`" class="view-btn">
                查看病情摘要
              </router-link>
            </li>
          </ul>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { getDoctorQueue } from '../api/queue';
import type { DoctorQueueResponse } from '../api/queue';

const router = useRouter();
const loading = ref(false);
const errorMsg = ref('');
const recordIds = ref<string[]>([]);

// 医生信息（与其他页面统一，从localStorage读取）
const doctorInfo = computed(() => {
  const info = localStorage.getItem('doctorInfo');
  return info ? JSON.parse(info) : { username: '张医生', department: '呼吸内科' };
});
const doctorName = computed(() => doctorInfo.value.username);
const doctorDept = computed(() => doctorInfo.value.department);

/** 侧边栏跳转函数 - 修复路径和参数问题 */
const goToDetail = () => {
  if (recordIds.value.length > 0) {
    router.push(`/doctor/summary/${recordIds.value[0]}`);
  } else {
    errorMsg.value = '暂无可用的患者记录，无法跳转至详情';
  }
};

const goToRecord = () => {
  if (recordIds.value.length > 0) {
    router.push(`/doctor/report/${recordIds.value[0]}`);
  } else {
    errorMsg.value = '暂无可用的患者记录，无法跳转至电子病历';
  }
};

const goToQuestionnaire = () => {
  router.push('/doctor/questionnaire/import'); // 修正为有效路径
};

onMounted(() => {
  fetchQueue();
});

const fetchQueue = async () => {
  loading.value = true;
  try {
    const doctorInfoStr = localStorage.getItem('doctorInfo');
    if (!doctorInfoStr) throw new Error('未登录或医生信息缺失');
    
    const doctorInfo = JSON.parse(doctorInfoStr);
    const userId = doctorInfo.id;
    if (!userId) throw new Error('医生 ID 不存在');

    const res = await getDoctorQueue(userId);

    if (res.base.code === '10000') {
      recordIds.value = res.data.record_ids;
    } else {
      errorMsg.value = res.base.msg || '获取待诊列表失败';
    }
  } catch (error: any) {
    errorMsg.value = error.message || error.base?.msg || '网络异常，请重试';
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
/* 页面整体样式（与其他页面统一） */
.queue-page {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background-color: #f5f7fa;
  min-height: 100vh;
}

/* 页面头部（与其他页面统一） */
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

/* 内容容器（侧边栏+主内容区） */
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

/* 选中项高亮（患者队列） */
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

/* 右侧队列内容区 */
.queue-content {
  flex: 1;
  padding: 24px;
}

/* 队列容器样式 */
.queue-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px;
  background: linear-gradient(135deg, #f5fafe 0%, #eaf6fa 100%);
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

/* 加载状态样式 */
.loading {
  text-align: center;
  padding: 60px;
  color: #666;
  font-size: 16px;
  background-color: #f9f9f9;
  border-radius: 8px;
}

/* 错误提示样式 */
.error {
  text-align: center;
  padding: 24px;
  color: #f56c6c;
  font-size: 16px;
  background-color: #fff1f0;
  border-radius: 8px;
  border: 1px solid #fde2e2;
}

/* 列表容器样式 */
.queue-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

/* 列表项卡片式设计 */
.queue-list li {
  padding: 20px;
  border-radius: 8px;
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  margin-bottom: 16px;
  font-size: 14px;
  color: #333;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.3s ease;
}

.queue-list li:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.queue-list li:last-child {
  margin-bottom: 0;
}

/* 查看按钮样式 */
.view-btn {
  padding: 8px 16px;
  background-color: #409eff;
  color: #fff;
  border-radius: 6px;
  text-decoration: none;
  font-size: 14px;
  transition: all 0.3s ease;
}

.view-btn:hover {
  background-color: #3086d6;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
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