<template>
  <div class="doctor-home">
    <!-- 左侧侧边栏 -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <span class="station-icon">👨‍⚕️</span>
        <h1>医生工作站</h1>
      </div>
      <nav class="sidebar-nav">
        <a 
          class="nav-item" 
          :class="{ active: $route.path === '/doctor/queue' }"
          @click="goToQueue"
        >
          <span class="nav-icon">📋</span>
          <span>患者队列</span>
        </a>
        <a 
          class="nav-item" 
          :class="{ active: $route.path.startsWith('/doctor/summary') }"
          @click="goToDetailFromSidebar"
        >
          <span class="nav-icon">👤</span>
          <span>患者详情</span>
        </a>
        <a 
          class="nav-item" 
          :class="{ active: $route.path.startsWith('/doctor/report') }"
          @click="goToRecord"
        >
          <span class="nav-icon">📄</span>
          <span>电子病历</span>
        </a>
        <a 
          class="nav-item" 
          :class="{ active: $route.path === '/doctor/questionnaire/import' }"
          @click="goToImport"
        >
          <span class="nav-icon">📤</span>
          <span>导入问卷</span>
        </a>
      </nav>
    </aside>

    <!-- 右侧主内容区（彻底简化.value使用） -->
    <main class="main-content">
      <header class="top-bar">
        <div class="top-right">
          <span class="notify-icon">🔔</span>
          <span class="doctor-name">{{ doctorName }}</span>
          <span class="department">| {{ department }}</span>
        </div>
      </header>

      <div class="content-area">
        <h2 class="page-title">患者队列</h2>
        <div class="queue-header">
          <h3>待诊患者队列</h3>
          <p>当前有 {{ recordIds.length }} 名患者在排队等候</p>
        </div>

        <div v-if="loading" class="loading-state">加载待诊列表中...</div>
        <div v-if="errorMsg" class="error-state">{{ errorMsg }}</div>

        <div class="queue-list" v-else>
          <div 
            v-for="(recordId, index) in recordIds" 
            :key="recordId"
            class="queue-item"
            :class="{ 
              'first-patient': index === 0, 
              'selected': recordId === selectedRecordId 
            }"
            @click="handlePatientSelect(recordId)"
          >
            <span class="patient-id">待诊患者ID：{{ recordId }}</span>
            <button class="view-btn" @click="handleViewSummary(recordId)">
              查看病情摘要
            </button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import { getDoctorQueue } from "../api/queue";
import type { DoctorQueueResponse } from "../api/queue";

// 1. 彻底简化路由与状态（避免TS类型歧义）
const router = useRouter();
const recordIds = ref<string[]>([]);
// 关键：用空字符串代替null，消除空值类型问题
const selectedRecordId = ref<string>(""); 
const loading = ref(false);
const errorMsg = ref("");

// 2. 计算属性提取医生信息（避免JSON.parse的TS警告）
const doctorInfo = computed(() => {
  const info = localStorage.getItem("doctorInfo");
  return info ? JSON.parse(info) : { username: "张医生", department: "呼吸内科", id: "" };
});
const doctorName = computed(() => doctorInfo.value.username);
const department = computed(() => doctorInfo.value.department);
const doctorId = computed(() => doctorInfo.value.id);

// 3. 页面加载：极简逻辑+错误兜底
onMounted(async () => {
  loading.value = true;
  try {
    if (!doctorId.value) throw new Error("医生信息未找到");
    
    const res: DoctorQueueResponse = await getDoctorQueue(doctorId.value);
    recordIds.value = res.base.code === "10000" ? res.data.record_ids : [];
    errorMsg.value = res.base.code !== "10000" ? res.base.msg || "加载失败" : "";
  } catch (err: any) {
    errorMsg.value = err.message || "网络异常";
  } finally {
    loading.value = false;
  }
});

// 4. 统一事件处理（避免模板中直接操作.value）
const handlePatientSelect = (recordId: string) => {
  selectedRecordId.value = recordId;
  // 新增：存入localStorage，供其他页面跳转时使用
  localStorage.setItem("recentRecordId", recordId);
};

const handleViewSummary = (recordId: string) => {
  selectedRecordId.value = recordId;
  localStorage.setItem("recentRecordId", recordId); // 新增：缓存最近选择的患者ID
  router.push(`/doctor/summary/${recordId}`);
};

// 5. 导航函数：路径对齐+缓存兜底
const goToQueue = () => router.push("/doctor/queue"); // 修改：匹配路由配置的队列页面

const goToDetailFromSidebar = () => {
  // 优化：优先用缓存的recordId，再用当前选中的
  const targetId = selectedRecordId.value || localStorage.getItem("recentRecordId");
  if (targetId) {
    router.push(`/doctor/summary/${targetId}`);
  } else {
    alert("请先选择患者或从队列中选择");
  }
};

const goToRecord = () => {
  // 优化：优先用缓存的recordId，再用当前选中的
  const targetId = selectedRecordId.value || localStorage.getItem("recentRecordId");
  if (targetId) {
    router.push(`/doctor/report/${targetId}`);
  } else {
    alert("请先选择患者或从队列中选择");
  }
};

const goToImport = () => router.push("/doctor/questionnaire/import");
</script>

<style scoped>
/* 样式完全复用，无修改 */
.doctor-home {
  display: flex;
  min-height: 100vh;
  font-family: "Microsoft YaHei", Arial, sans-serif;
}

.sidebar {
  width: 180px;
  background-color: #1A365D;
  color: #FFFFFF;
  padding: 20px 0;
  box-shadow: 2px 0 4px rgba(0, 0, 0, 0.1);
}
.sidebar-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 20px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}
.station-icon {
  font-size: 20px;
}
.sidebar-header h1 {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
}
.sidebar-nav {
  padding: 10px;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 15px;
  border-radius: 4px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: background 0.2s;
  font-size: 14px;
}
.nav-item.active {
  background-color: #2D5B99;
  font-weight: 500;
}
.nav-item:hover:not(.active) {
  background-color: #244A7C;
}
.nav-icon {
  font-size: 16px;
}

.main-content {
  flex: 1;
  background-color: #F5F7FA;
  display: flex;
  flex-direction: column;
}

.top-bar {
  height: 50px;
  background-color: #FFFFFF;
  border-bottom: 1px solid #E5E9F2;
  padding: 0 20px;
  display: flex;
  justify-content: flex-end;
  align-items: center;
}
.top-right {
  display: flex;
  align-items: center;
  gap: 15px;
  color: #4E5969;
  font-size: 14px;
}
.notify-icon {
  font-size: 18px;
  cursor: pointer;
}
.doctor-name {
  font-weight: 500;
}
.department {
  color: #86909C;
}

.content-area {
  padding: 20px 30px;
}
.page-title {
  font-size: 20px;
  color: #1D2129;
  margin: 0 0 20px 0;
}
.queue-header {
  margin-bottom: 15px;
}
.queue-header h3 {
  font-size: 16px;
  color: #1D2129;
  margin: 0 0 5px 0;
}
.queue-header p {
  color: #86909C;
  margin: 0;
  font-size: 14px;
}

.loading-state, .error-state {
  padding: 30px;
  background-color: #FFFFFF;
  border-radius: 6px;
  text-align: center;
  margin-top: 20px;
}
.error-state {
  color: #F5222D;
  background-color: #FFF1F0;
}

.queue-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 20px;
}
.queue-item {
  background-color: #FFFFFF;
  border: 1px solid #E5E9F2;
  border-radius: 4px;
  padding: 12px 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  transition: border-color 0.2s;
}
.queue-item.first-patient {
  background-color: #FFF9E8;
  border-left: 3px solid #FAAD14;
}
.queue-item.selected {
  border-color: #3B82F6;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.15);
}
.queue-item:hover {
  border-color: #C9CDD4;
}
.patient-id {
  font-size: 14px;
  color: #4E5969;
}
.view-btn {
  padding: 6px 12px;
  background-color: #1890FF;
  color: #FFFFFF;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}
.view-btn:hover {
  background-color: #096DD9;
}
</style>