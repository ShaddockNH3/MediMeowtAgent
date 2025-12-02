<template>
  <div class="doctor-home">
    <!-- 左侧侧边栏（与医生主页统一） -->
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

    <!-- 右侧主内容区（病情摘要界面） -->
    <main class="main-content">
      <!-- 顶部医生信息栏 -->
      <header class="top-bar">
        <div class="top-right">
          <span class="notify-icon">🔔</span>
          <span class="doctor-name">{{ doctorName }}</span>
          <span class="department">| {{ doctorDept }}</span>
        </div>
      </header>

      <!-- 核心内容区 -->
      <div class="content-area">
        <h2 class="page-title">患者病情摘要</h2>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading-state">
          <span class="loading-spinner">🔄</span>
          <p>正在加载患者病情数据...</p>
        </div>

        <!-- 错误状态 -->
        <div v-else-if="errorMsg" class="error-state">
          <span class="error-icon">❌</span>
          <p>{{ errorMsg }}</p>
          <button class="retry-btn" @click="fetchSummary">重试</button>
        </div>

        <!-- 病情摘要主体 -->
        <div v-else class="summary-container">
          <!-- 患者基本信息卡片 -->
          <div class="card basic-card">
            <h3 class="card-title">
              <i class="icon">👤</i> 患者基本信息
            </h3>
            <div class="info-grid">
              <div class="info-row">
                <label>姓名：</label>
                <span>{{ patientInfo.name }}</span>
              </div>
              <div class="info-row">
                <label>联系电话：</label>
                <span>{{ patientInfo.phone }}</span>
              </div>
              <div class="info-row">
                <label>用户ID：</label>
                <span>{{ patientInfo.id }}</span>
              </div>
              <div class="info-row">
                <label>注册时间：</label>
                <span>{{ formatTime(patientInfo.createdAt) }}</span>
              </div>
            </div>
          </div>

          <!-- AI病情分析卡片 -->
          <div class="card ai-card">
            <h3 class="card-title">
              <i class="icon">🩺</i> AI病情分析
            </h3>
            <div class="ai-grid">
              <div class="ai-row">
                <label>主诉：</label>
                <p>{{ symptomInfo.chiefComplaint }}</p>
              </div>
              <div class="ai-row">
                <label>关键症状：</label>
                <div class="symptom-tags">
                  <span 
                    v-for="symptom in symptomInfo.keySymptoms" 
                    :key="symptom" 
                    class="tag"
                  >
                    {{ symptom }}
                  </span>
                </div>
              </div>
              <div class="ai-row">
                <label>影像摘要：</label>
                <p>{{ symptomInfo.imageSummary || "无影像数据" }}</p>
              </div>
              <div class="ai-row">
                <label>重要备注：</label>
                <p>{{ symptomInfo.importantNotes }}</p>
              </div>
              <div class="ai-row">
                <label>提交ID：</label>
                <span>{{ symptomInfo.submissionId }}</span>
              </div>
              <div class="ai-row">
                <label>科室匹配：</label>
                <span class="match-tag" :class="symptomInfo.isDeptMatch ? 'match' : 'unmatch'">
                  {{ symptomInfo.isDeptMatch ? "匹配当前科室" : "非当前科室" }}
                </span>
              </div>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="btn-group">
            <button class="back-btn" @click="goToQueue">返回队列</button>
            <button class="report-btn" @click="goToRecord">生成电子病历</button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";

// 拆分导入：值导入（函数）+ 类型导入（接口/类型别名）
import { getDiseaseSummary } from "../api/summary";
import type { SummaryResponse, User, AiResult, KeyInfo } from "../api/summary";

// 路由与导航实例
const route = useRoute();
const router = useRouter();

// 响应式状态
const loading = ref(true);
const errorMsg = ref("");

// 医生信息（从localStorage读取，避免JSON.parse类型警告）
const doctorInfo = computed(() => {
  const rawInfo = localStorage.getItem("doctorInfo");
  if (!rawInfo) return { username: "张医生", department: "呼吸内科" };
  
  try {
    return JSON.parse(rawInfo) as { username: string; department: string };
  } catch {
    return { username: "张医生", department: "呼吸内科" };
  }
});
const doctorName = computed(() => doctorInfo.value.username);
const doctorDept = computed(() => doctorInfo.value.department);

// 患者基本信息（适配原有User类型）
const patientInfo = ref({
  id: "",
  name: "",
  phone: "",
  createdAt: "",
});

// 症状信息（适配原有AiResult和KeyInfo类型）
const symptomInfo = ref({
  chiefComplaint: "",
  keySymptoms: [] as string[],
  imageSummary: "",
  importantNotes: "",
  submissionId: "",
  isDeptMatch: false,
});

// 时间格式化工具（处理空值）
const formatTime = (timeStr: string | undefined) => {
  if (!timeStr) return "未知";
  try {
    return new Date(timeStr).toLocaleString("zh-CN", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return "未知";
  }
};

// 数据获取函数（增加参数校验）
const fetchSummary = async () => {
  loading.value = true;
  errorMsg.value = "";
  
  try {
    // 严格校验路由参数
    const recordId = route.params.recordId as string;
    if (!recordId || recordId.trim() === "") {
      throw new Error("缺少有效的患者记录ID");
    }

    // 调用API并校验响应
    const res: SummaryResponse = await getDiseaseSummary(recordId);
    if (!res || res.base.code !== "10000") {
      throw new Error(res?.base?.msg || "获取病情摘要失败");
    }

    // 映射患者基本信息（类型断言确保安全）
    const user = res.data.user as User;
    patientInfo.value = {
      id: user.id || "未知",
      name: user.username || "未知",
      phone: user.phone_number || "未知",
      createdAt: user.created_at || "",
    };

    // 映射AI病情信息（类型断言+空值处理）
    const aiResult = res.data.ai_result as AiResult;
    const keyInfo = aiResult.key_info as KeyInfo;
    symptomInfo.value = {
      chiefComplaint: keyInfo.chief_complaint || "暂无",
      keySymptoms: keyInfo.key_symptoms 
        ? keyInfo.key_symptoms.split(/[,，;；]/).filter(s => s.trim() !== "") 
        : [],
      imageSummary: keyInfo.image_summary || "暂无",
      importantNotes: keyInfo.important_notes || "暂无",
      submissionId: aiResult.submission_id || "未知",
      isDeptMatch: aiResult.is_department || false,
    };
  } catch (err: any) {
    errorMsg.value = err.message || "网络异常，请稍后重试";
    console.error("病情摘要加载失败：", err);
  } finally {
    loading.value = false;
  }
};

// 路由跳转函数（增加安全性校验）
const goToQueue = () => router.push("/doctor");

const goToDetailFromSidebar = () => {
  const recordId = route.params.recordId as string;
  if (recordId) {
    router.push(`/doctor/summary/${recordId}`);
  } else {
    alert("请先选择有效的患者");
    router.push("/doctor");
  }
};

const goToRecord = () => {
  const recordId = route.params.recordId as string;
  if (recordId) {
    router.push(`/doctor/report/${recordId}`);
  } else {
    alert("请先选择患者以生成电子病历");
    router.push("/doctor");
  }
};

const goToImport = () => router.push("/doctor/questionnaire/import");

// 页面挂载时加载数据（确保DOM就绪）
onMounted(() => {
  // 延迟执行避免DOM渲染冲突
  setTimeout(fetchSummary, 100);
});
</script>

<style scoped>
/* 全局布局样式 */
.doctor-home {
  display: flex;
  height: 100vh;
  font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
  background-color: #f5f7fa;
  overflow: hidden;
}

/* 左侧侧边栏样式 */
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

/* 右侧主内容区样式 */
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

/* 内容区域样式 */
.content-area {
  padding: 30px;
}

.page-title {
  font-size: 22px;
  color: #1d2129;
  margin: 0 0 25px 0;
  font-weight: 600;
}

/* 加载/错误状态样式 */
.loading-state, .error-state {
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

/* 摘要容器样式 */
.summary-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card {
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  padding: 20px;
  transition: box-shadow 0.2s;
}

.card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.card-title {
  font-size: 16px;
  color: #1d2129;
  margin: 0 0 20px 0;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.icon {
  font-size: 18px;
  color: #1890ff;
}

/* 基本信息卡片样式 */
.basic-card .info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.info-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.info-row label {
  font-weight: 500;
  color: #4e5969;
  min-width: 60px;
  font-size: 14px;
}

.info-row span {
  color: #1d2129;
  font-size: 14px;
}

/* AI分析卡片样式 */
.ai-card .ai-grid {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.ai-row {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.ai-row label {
  font-weight: 500;
  color: #4e5969;
  font-size: 14px;
}

.ai-row p {
  margin: 0;
  color: #1d2129;
  line-height: 1.5;
  font-size: 14px;
}

.symptom-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  background-color: #e6f7ff;
  color: #1890ff;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  transition: background-color 0.2s;
}

.tag:hover {
  background-color: #bae7ff;
}

.match-tag {
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
}

.match-tag.match {
  background-color: #f6ffed;
  color: #52c41a;
}

.match-tag.unmatch {
  background-color: #fff1f0;
  color: #f5222d;
}

/* 按钮组样式 */
.btn-group {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  margin-top: 20px;
}

.back-btn, .report-btn {
  padding: 10px 20px;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.back-btn {
  background-color: #f5f7fa;
  color: #4e5969;
}

.back-btn:hover {
  background-color: #e5e9f2;
}

.report-btn {
  background-color: #1890ff;
  color: #ffffff;
}

.report-btn:hover {
  background-color: #096dd9;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .basic-card .info-grid {
    grid-template-columns: 1fr;
  }
  
  .sidebar {
    width: 180px;
  }
  
  .content-area {
    padding: 20px;
  }
}
</style>