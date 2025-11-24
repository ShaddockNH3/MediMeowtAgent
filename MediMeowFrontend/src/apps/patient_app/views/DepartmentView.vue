<template>
  <div class="dept-container">
    <h2>请选择就诊科室</h2>
    <div class="card-list">
      <el-card 
        v-for="item in deptList" 
        :key="item.department_id" 
        class="box-card"
        shadow="hover"
        @click="handleSelect(item.department_id)"
      >
        <div class="card-content">
          <h3>{{ item.department_name }}</h3>
          <el-icon><ArrowRight /></el-icon>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getDepartments } from '../api/index.js'
import { ArrowRight } from '@element-plus/icons-vue' // 记得引入图标

const router = useRouter()
const deptList = ref([])

onMounted(async () => {
  try {
    const data = await getDepartments()
    // 拦截器已经处理了 res.data，这里直接拿 data 即可
    // 此时 data 应该就是那个数组: [{ department_name: "...", ... }]
    deptList.value = data || []
  } catch (error) {
    console.error(error)
  }
})

// ... (文件顶部代码不变)

const handleSelect = (id) => {
  // 原代码: router.push(`/questionnaire/${id}`)
  // 修改后: 加上了 '/patient' 前缀，以匹配路由配置和守卫规则
  router.push(`/patient/questionnaire/${id}`);
};

// ... (文件底部代码不变)
</script>

<style scoped>
.dept-container { padding: 20px; max-width: 800px; margin: 0 auto; }
.card-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 20px; }
.box-card { cursor: pointer; transition: all 0.3s; display: flex; align-items: center; justify-content: center; height: 100px; }
.box-card:hover { transform: translateY(-5px); border-color: #409EFF; }
.card-content { display: flex; align-items: center; justify-content: space-between; width: 100%; padding: 0 10px; }
h3 { margin: 0; font-size: 18px; }
</style>