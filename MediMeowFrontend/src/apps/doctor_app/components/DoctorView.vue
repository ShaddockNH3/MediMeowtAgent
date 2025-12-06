<template>
  <div class="doctor-home">
    <!-- 左侧侧边栏（保持原导航） -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <span class="station-icon">👨‍⚕️</span>
        <h1>医生工作站</h1>
      </div>
      <nav class="sidebar-nav">
        <a 
          class="nav-item" 
          :class="{ active: $route.path === '/doctor' }"
          @click="goToHome"
        >
          <span class="nav-icon">📋</span>
          <span>患者队列</span>
        </a>
        <a 
          class="nav-item" 
          :class="{ active: $route.path.startsWith('/doctor/summary') }"
          @click="goToDetail"
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

    <!-- 右侧主内容区（动态显示真实患者信息） -->
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

        <!-- 状态提示（网络异常/加载中） -->
        <div v-if="loading" class="loading-state">加载待诊列表中...</div>
        <div v-if="errorMsg" class="error-state">{{ errorMsg }}</div>

        <!-- 患者队列列表（动态显示真实/虚拟数据） -->
        <div class="queue-list" v-else>
          <div 
            v-for="(recordId, index) in recordIds" 
            :key="recordId"
            class="queue-item"
            :class="{ 'first-patient': index === 0 }"
          >
            <!-- 患者信息：动态显示真实/虚拟数据 -->
            <div class="patient-info">
              <span class="patient-index">{{ index + 1 }}.</span>
              <span class="patient-name">{{ getPatientInfo(recordId).name }}</span>
              <span class="patient-gender-age">{{ getPatientInfo(recordId).gender }}/{{ getPatientInfo(recordId).age }}岁</span>
              <div class="patient-ids">
                <span>记录ID：{{ recordId }}</span>
                <span>患者ID：{{ recordId }}</span>
              </div>
              <span class="patient-complaint">主诉：{{ getPatientInfo(recordId).chiefComplaint }}</span>
            </div>
            <!-- 查看病情摘要按钮 -->
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
// 1. 导入队列接口 + 患者详情接口（获取真实患者信息）
import { getDoctorQueue, getPatientDetail } from "../api/queue";
// 2. 导入对应的类型定义
import type { DoctorQueueResponse, PatientDetailResponse } from "../api/queue";

// 响应式状态
const router = useRouter();
const recordIds = ref<string[]>([]);
const loading = ref(false);
const errorMsg = ref("");

// 3. 新增：存储后端返回的真实患者信息（recordId -> 患者详情）
const patientRealInfo = ref<Record<string, {
  name: string;      // 真实姓名
  gender: string;    // 真实性别
  age: number;       // 真实年龄
  chiefComplaint: string; // 真实主诉
}>>({});

// 医生信息（从localStorage读取）
const doctorInfo = computed(() => {
  const info = localStorage.getItem("doctorInfo");
  return info ? JSON.parse(info) : { username: "张医生", department: "呼吸内科", id: "" };
});
const doctorName = computed(() => doctorInfo.value.username);
const department = computed(() => doctorInfo.value.department);
const doctorId = computed(() => doctorInfo.value.id);

// 4. 页面加载：请求患者队列 + 批量请求患者真实详情
onMounted(async () => {
  loading.value = true;
  try {
    if (!doctorId.value) throw new Error("医生信息未找到");
    
    // 步骤1：获取患者队列的record_ids
    const queueRes: DoctorQueueResponse = await getDoctorQueue(doctorId.value);
    if (queueRes.base.code !== "10000") throw new Error(queueRes.base.msg || "队列加载失败");
    recordIds.value = queueRes.data.record_ids;

    // 步骤2：批量请求每个患者的真实详情（获取姓名、性别、年龄、主诉）
    if (recordIds.value.length > 0) {
      // 并行请求所有患者详情，提高性能
      const patientPromises = recordIds.value.map(async (id) => {
        try {
          const detailRes: PatientDetailResponse = await getPatientDetail(id);
          if (detailRes.base.code === "10000") {
            // 存储真实患者信息到映射表
            patientRealInfo.value[id] = {
              name: detailRes.data.name || `未知患者(${id.slice(-4)})`,
              gender: detailRes.data.gender || "未知",
              age: detailRes.data.age || 0,
              chiefComplaint: detailRes.data.chiefComplaint || "无"
            };
          }
        } catch (err) {
          // 单个患者详情请求失败不影响整体，仅打印警告
          console.warn(`获取患者${id}详情失败：`, err);
        }
      });
      // 等待所有请求完成
      await Promise.all(patientPromises);
    }
  } catch (err: any) {
    errorMsg.value = err.message || "网络异常";
  } finally {
    loading.value = false;
  }
});

// 5. 新增：动态获取患者信息（优先真实，次选虚拟）
const getPatientInfo = (recordId: string) => {
  // 如果有后端返回的真实数据，直接使用
  if (patientRealInfo.value[recordId]) {
    return patientRealInfo.value[recordId];
  }
  // 无真实数据时，返回虚拟兜底（保证页面正常显示）
  return {
    name: `未知患者(${recordId.slice(-4)})`,
    gender: "未知",
    age: 0,
    chiefComplaint: "无"
  };
};

// 点击查看病情摘要（跳转详情页）
const handleViewSummary = (recordId: string) => {
  localStorage.setItem("recentRecordId", recordId);
  router.push(`/doctor/summary/${recordId}`);
};

// 导航函数
const goToHome = () => router.push("/doctor");
const goToDetail = () => {
  const targetId = localStorage.getItem("recentRecordId");
  targetId ? router.push(`/doctor/summary/${targetId}`) : alert("请先选择患者");
};
const goToRecord = () => {
  const targetId = localStorage.getItem("recentRecordId");
  targetId ? router.push(`/doctor/report/${targetId}`) : alert("请先选择患者");
};
const goToImport = () => router.push("/doctor/questionnaire/import");
</script>

<style scoped>
/* 全局布局 */
.doctor-home {
  display: flex;
  min-height: 100vh;
  font-family: "Microsoft YaHei", Arial, sans-serif;
}

/* 侧边栏样式 */
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

/* 主内容区 */
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

/* 患者队列区域 */
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

/* 状态提示 */
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

/* 患者队列列表（与图二样式一致） */
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
  align-items: flex-start;
  border-left: 3px solid #FAAD14;
}
.queue-item.first-patient {
  background-color: #FFF9E8;
}

/* 患者信息样式 */
.patient-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.patient-index {
  font-weight: 600;
  margin-right: 8px;
}
.patient-name {
  font-size: 14px;
  color: #4E5969;
  font-weight: 500;
}
.patient-gender-age {
  font-size: 12px;
  color: #86909C;
  margin-left: 8px;
}
.patient-ids {
  font-size: 12px;
  color: #86909C;
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin: 4px 0;
}
.patient-complaint {
  font-size: 12px;
  color: #86909C;
}

/* 按钮样式 */
.view-btn {
  padding: 6px 12px;
  background-color: #1890FF;
  color: #FFFFFF;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
  align-self: center;
}
.view-btn:hover {
  background-color: #096DD9;
}
</style>