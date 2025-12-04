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
          :class="{ 'active': $route.path === '/doctor' }"
          @click="goToQueue"
        >
          <span class="nav-icon">📋</span>
          <span>患者队列</span>
        </a>
        <a 
          class="nav-item" 
          :class="{ 'active': $route.path.startsWith('/doctor/summary') }"
          @click="goToDetailFromSidebar"
        >
          <span class="nav-icon">👤</span>
          <span>患者详情</span>
        </a>
        <a 
          class="nav-item" 
          :class="{ 'active': $route.path.startsWith('/doctor/report') }"
          @click="goToRecord"
        >
          <span class="nav-icon">📄</span>
          <span>电子病历</span>
        </a>
        <a 
          class="nav-item" 
          :class="{ 'active': $route.path === '/doctor/questionnaire/import' }"
          @click="goToImport"
        >
          <span class="nav-icon">📤</span>
          <span>导入问卷</span>
        </a>
      </nav>
    </aside>

    <!-- 右侧主内容区 -->
    <main class="main-content">
      <header class="top-bar">
        <div class="top-right">
          <span class="notify-icon">🔔</span>
          <span class="doctor-name">{{ doctorInfo.username }}</span>
          <span class="department">| {{ doctorInfo.department }}</span>
        </div>
      </header>

      <div class="content-area">
        <h2 class="page-title">患者队列</h2>
        <div class="queue-header">
          <h3>待诊患者队列</h3>
          <p>当前有 {{ patientList.length }} 名患者在排队等候</p>
        </div>

        <!-- 状态处理：加载中/错误/空列表 -->
        <div v-if="loading" class="loading-state">
          <span class="loading-spinner">🔄</span>
          <p>正在加载待诊患者列表...</p>
        </div>
        <div v-else-if="errorMsg" class="error-state">
          <span class="error-icon">❌</span>
          <p>{{ errorMsg }}</p>
          <button class="retry-btn" @click="loadPatientQueue">重试</button>
        </div>
        <div v-else-if="patientList.length === 0" class="empty-state">
          <p>暂无待诊患者</p>
        </div>
        
        <!-- 核心：患者列表 -->
        <div class="queue-list" v-else>
          <div 
            v-for="(patient, index) in patientList" 
            :key="patient.recordId"
            class="queue-item"
            :class="{ 
              'first-patient': index === 0,
              'selected': selectedRecordId === patient.recordId
            }"
            @click="handlePatientSelect(patient.recordId)"
          >
            <div class="patient-info">
              <span class="patient-name">
                {{ index + 1 }}. {{ patient.name }} 
                <span class="patient-gender-age">({{ patient.gender }}/{{ patient.age }}岁)</span>
              </span>
              <span class="patient-id-small">记录ID：{{ patient.recordId }}</span>
              <span class="patient-id-small">患者ID：{{ patient.userId }}</span>
              <span class="patient-complaint">主诉：{{ patient.chiefComplaint }}</span>
            </div>
            <button 
              class="view-btn" 
              @click.stop="handleViewSummary(patient.recordId)"
            >
              查看病情摘要
            </button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
// 导入路径已修正为../api/queue
import { getDoctorQueue, getPatientDetail } from "../api/queue";
import type { DoctorQueueResponse, PatientDetailResponse } from "../api/queue";

// 患者类型定义
interface PatientItem {
  recordId: string;  // 就诊记录ID
  userId: string;    // 患者用户ID
  name: string;      // 患者姓名
  gender: string;    // 性别
  age: number;       // 年龄
  chiefComplaint: string; // 主诉
}

// 响应式状态
const router = useRouter();
const patientList = ref<PatientItem[]>([]);
const selectedRecordId = ref<string>("");
const loading = ref(false);
const errorMsg = ref("");

// 医生信息（从localStorage获取，确保类型安全）
const doctorInfo = computed((): { username: string; department: string; id: string } => {
  try {
    const info = localStorage.getItem("doctorInfo");
    if (info) {
      const parsed = JSON.parse(info) as any;
      return {
        username: parsed.username || "张医生",
        department: parsed.department || "呼吸内科",
        id: parsed.id || ""
      };
    }
  } catch (e) {
    console.error("解析医生信息失败：", e);
  }
  // 默认值，确保返回类型一致
  return { username: "张医生", department: "呼吸内科", id: "" };
});

// 加载患者队列（核心修正：解决第205行报错）
const loadPatientQueue = async () => {
  loading.value = true;
  errorMsg.value = "";
  patientList.value = [];
  
  try {
    // 1. 获取医生ID，确保非空
    const doctorId = doctorInfo.value.id;
    if (!doctorId) {
      throw new Error("医生ID获取失败，请重新登录");
    }
    
    // 2. 调用API获取待诊患者的record_ids列表
    const queueRes: DoctorQueueResponse = await getDoctorQueue(doctorId);
    
    // 3. 检查API返回状态
    if (!queueRes || queueRes.base.code !== "10000") {
      throw new Error(`获取队列失败：${queueRes?.base?.msg || "未知错误"}`);
    }
    
    // 4. 提取record_ids
    const recordIds = queueRes?.data?.record_ids || [];
    
    // 5. 批量获取每个患者的详细信息
    if (recordIds.length > 0) {
      const patientPromises = recordIds.map(async (recordId: string) => {
        try {
          const detailRes: PatientDetailResponse = await getPatientDetail(recordId);
          
          if (!detailRes || detailRes.base.code !== "10000" || !detailRes.data) {
            return {
              recordId,
              userId: recordId,
              name: `未知患者(${recordId.slice(-4)})`,
              gender: "未知",
              age: 0,
              chiefComplaint: "无"
            };
          }
          
          const patientData = detailRes.data;
          return {
            recordId,
            userId: patientData.id,
            name: patientData.name,
            gender: patientData.gender,
            age: patientData.age,
            chiefComplaint: patientData.chiefComplaint
          };
        } catch (e) {
          console.error(`获取患者${recordId}详情失败：`, e);
          return {
            recordId,
            userId: recordId,
            name: `未知患者(${recordId.slice(-4)})`,
            gender: "未知",
            age: 0,
            chiefComplaint: "无"
          };
        }
      });
      
      // 等待所有请求完成
      patientList.value = await Promise.all(patientPromises);
      
      // 核心修正：解决第205行报错 - 显式获取并校验第一个患者
      if (patientList.value.length > 0) {
        const firstPatient = patientList.value[0];
        // 显式校验firstPatient非空，让TypeScript明确识别
        if (firstPatient) {
          selectedRecordId.value = firstPatient.recordId;
          localStorage.setItem("recentRecordId", selectedRecordId.value);
        }
      }
    }
  } catch (err: any) {
    errorMsg.value = err.message || "网络异常，加载失败";
    console.error("加载患者队列失败：", err);
  } finally {
    loading.value = false;
  }
};

// 患者选中处理
const handlePatientSelect = (recordId: string) => {
  selectedRecordId.value = recordId;
  localStorage.setItem("recentRecordId", recordId);
};

// 查看病情摘要（已修正：添加非空校验）
const handleViewSummary = (recordId: string) => {
  // 查找患者并显式校验
  const patient = patientList.value.find(p => p.recordId === recordId);
  if (!patient) {
    console.warn(`未找到recordId为${recordId}的患者`);
    alert("该患者信息不存在，请重试");
    return;
  }

  // 安全访问patient属性
  console.log("[队列页] 点击查看病情摘要：", {
    recordId,
    patientName: patient.name,
    patientUserId: patient.userId
  });

  selectedRecordId.value = recordId;
  localStorage.setItem("recentRecordId", recordId);
  router.push(`/doctor/summary/${recordId}`);
};

// 路由跳转函数
const goToQueue = () => router.push("/doctor");

const goToDetailFromSidebar = () => {
  const targetId = selectedRecordId.value || localStorage.getItem("recentRecordId");
  if (targetId) {
    router.push(`/doctor/summary/${targetId}`);
  } else {
    alert("请先选择有效的患者");
    router.push("/doctor");
  }
};

const goToRecord = () => {
  const targetId = selectedRecordId.value || localStorage.getItem("recentRecordId");
  if (targetId) {
    router.push(`/doctor/report/${targetId}`);
  } else {
    alert("请先选择患者以生成电子病历");
    router.push("/doctor");
  }
};

const goToImport = () => router.push("/doctor/questionnaire/import");

// 页面挂载时加载患者队列
onMounted(() => {
  loadPatientQueue();
});
</script>

<style scoped>
/* 全局布局 */
.doctor-home {
  display: flex;
  height: 100vh;
  font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
  background-color: #f5f7fa;
  overflow: hidden;
}

/* 侧边栏样式 */
.sidebar {
  width: 200px;
  background-color: #1a365d;
  color: #ffffff;
  padding: 20px 0;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.08);
}

.sidebar-header {
  padding: 0 20px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.15);
  display: flex;
  align-items: center;
  gap: 10px;
}

.station-icon {
  font-size: 24px;
}

.sidebar-header h1 {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
}

.sidebar-nav {
  padding: 20px 10px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 15px;
  border-radius: 4px;
  cursor: pointer;
  margin-bottom: 8px;
  font-size: 14px;
  transition: background-color 0.2s ease;
}

.nav-item.active {
  background-color: #2d5b99;
}

.nav-item:hover:not(.active) {
  background-color: #244a7c;
}

.nav-icon {
  font-size: 16px;
}

/* 主内容区 */
.main-content {
  flex: 1;
  overflow-y: auto;
}

.top-bar {
  height: 60px;
  background-color: #ffffff;
  border-bottom: 1px solid #e5e9f2;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding: 0 30px;
}

.top-right {
  display: flex;
  align-items: center;
  gap: 15px;
  font-size: 14px;
}

.notify-icon {
  font-size: 20px;
  cursor: pointer;
  transition: color 0.2s;
}

.notify-icon:hover {
  color: #1890ff;
}

.doctor-name {
  font-weight: 500;
  color: #1d2129;
}

.department {
  color: #86909c;
}

.content-area {
  padding: 30px;
}

.page-title {
  font-size: 22px;
  color: #1d2129;
  margin: 0 0 25px 0;
  font-weight: 600;
}

/* 队列头部 */
.queue-header {
  margin-bottom: 20px;
}

.queue-header h3 {
  font-size: 16px;
  color: #1d2129;
  margin: 0 0 5px 0;
}

.queue-header p {
  color: #86909c;
  margin: 0;
  font-size: 14px;
}

/* 状态样式 */
.loading-state, .error-state, .empty-state {
  background-color: #ffffff;
  border-radius: 8px;
  padding: 40px;
  text-align: center;
  margin: 20px 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.loading-spinner {
  font-size: 32px;
  display: block;
  margin-bottom: 15px;
  animation: spin 1.5s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.error-icon {
  font-size: 32px;
  color: #f5222d;
  display: block;
  margin-bottom: 15px;
}

.retry-btn {
  padding: 8px 16px;
  background-color: #1890ff;
  color: #ffffff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 10px;
  transition: background-color 0.2s;
}

.retry-btn:hover {
  background-color: #096dd9;
}

/* 队列列表 */
.queue-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 20px;
}

.queue-item {
  background-color: #ffffff;
  border: 1px solid #e5e9f2;
  border-radius: 4px;
  padding: 15px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  cursor: pointer;
  transition: all 0.2s;
}

.queue-item:hover {
  border-color: #c9cdd4;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.queue-item.first-patient {
  background-color: #fff9e8;
  border-left: 3px solid #faad14;
}

.queue-item.selected {
  border-color: #3b82f6;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.15);
}

/* 患者信息 */
.patient-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
  flex: 1;
  margin-right: 15px;
}

.patient-name {
  font-size: 14px;
  color: #4e5969;
  font-weight: 500;
}

.patient-gender-age {
  font-size: 12px;
  color: #86909c;
  font-weight: normal;
}

.patient-id-small {
  font-size: 12px;
  color: #86909c;
}

.patient-complaint {
  font-size: 13px;
  color: #666;
  margin-top: 5px;
}

/* 按钮样式 */
.view-btn {
  padding: 8px 16px;
  background-color: #1890ff;
  color: #ffffff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
  align-self: center;
}

.view-btn:hover {
  background-color: #096dd9;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .sidebar {
    width: 180px;
  }
  
  .content-area {
    padding: 20px;
  }
  
  .queue-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .view-btn {
    align-self: flex-end;
  }
}
</style>