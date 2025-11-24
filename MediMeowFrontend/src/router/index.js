import { createRouter, createWebHistory } from 'vue-router';
import patientRoutes from './patientRoutes'; // 患者端路由（你的原有文件）
import doctorRoutes from './doctorRoutes'; // 新增的医生端路由

const routes = [
  ...patientRoutes,
  ...doctorRoutes,
  // 可添加其他公共路由...
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// 路由守卫：分别处理医生、患者的登录态
router.beforeEach((to, from, next) => {
  const isDoctorRoute = to.path.startsWith('/doctor');
  const isPatientRoute = to.path.startsWith('/patient');
  const doctorToken = localStorage.getItem('doctorToken');
  const patientToken = localStorage.getItem('userToken');

  if (isDoctorRoute) {
    if (to.meta.requiresAuth && !doctorToken) {
      next('/doctor/login'); // 医生未登录→跳医生登录页
    } else {
      next();
    }
  } else if (isPatientRoute) {
    if (to.meta.requiresAuth && !patientToken) {
      next('/patient/login'); // 患者未登录→跳患者登录页
    } else {
      next();
    }
  } else {
    next();
  }
});

export default router;