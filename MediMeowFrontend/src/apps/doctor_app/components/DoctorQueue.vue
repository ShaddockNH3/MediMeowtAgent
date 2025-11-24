<template>
  <div class="queue-container">
    <h3>待诊列表</h3>
    <div class="loading" v-if="loading">加载中...</div>
    <div class="error" v-if="errorMsg">{{ errorMsg }}</div>
    <ul class="queue-list" v-else>
      <li v-for="recordId in recordIds" :key="recordId">
        待诊患者 ID：{{ recordId }}
        <!-- 添加跳转按钮，点击后进入病情摘要页面 -->
        <router-link 
          :to="`/doctor/summary/${recordId}`" 
          class="view-btn"
        >
          查看病情摘要
        </router-link>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router'; // 导入路由钩子
import { getDoctorQueue } from '../api/queue';
import type { DoctorQueueResponse } from '../api/queue';

const router = useRouter(); // 创建路由实例
const loading = ref(false);
const errorMsg = ref('');
const recordIds = ref<string[]>([]);

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
.queue-container {
  max-width: 800px;
  margin: 30px auto;
  padding: 24px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.loading {
  text-align: center;
  padding: 40px;
  color: #666;
  font-size: 14px;
}

.error {
  text-align: center;
  padding: 40px;
  color: #f56c6c;
  font-size: 14px;
}

.queue-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.queue-list li {
  padding: 16px;
  border-bottom: 1px solid #f5f5f5;
  font-size: 14px;
  color: #333;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.queue-list li:last-child {
  border-bottom: none;
}

.view-btn {
  padding: 6px 12px;
  background-color: #409eff;
  color: #fff;
  border-radius: 4px;
  text-decoration: none;
  font-size: 12px;
  transition: background-color 0.3s;
}

.view-btn:hover {
  background-color: #3086d6;
}
</style>