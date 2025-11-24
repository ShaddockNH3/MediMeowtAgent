<template>
  <div class="doctor-view">
    <h1>医生工作平台</h1>
    <div class="function-cards">
      <router-link to="/doctor/queue" class="card">
        <h3>待诊列表</h3>
        <p>查看并处理患者的待诊请求</p>
      </router-link>
      <router-link to="/doctor/questionnaire/import" class="card">
        <h3>导入问卷</h3>
        <p>上传.xlsx格式问卷，用于患者评估</p>
      </router-link>
    </div>
  </div>
</template>

<script setup>
// 无额外逻辑，仅作为路由跳转入口
</script>

<style scoped>
.doctor-view {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.function-cards {
  display: flex;
  gap: 24px;
  margin-top: 32px;
  flex-wrap: wrap;
}

.card {
  flex: 1;
  min-width: 280px;
  padding: 24px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  text-decoration: none;
  transition: transform 0.3s, box-shadow 0.3s;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.card h3 {
  color: #333;
  margin: 0 0 8px 0;
  font-size: 18px;
}

.card p {
  color: #666;
  margin: 0;
  font-size: 14px;
}
</style>