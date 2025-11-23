// 导入医生端视图组件
import DoctorView from '../apps/doctor_app/DoctorView.vue'

// 定义并导出医生端的所有路由
const doctorRoutes = [
  {
    path: '/doctor',
    name: 'DoctorHome',
    component: DoctorView
  },
  // C同学未来可以在这里继续添加新的医生端路由
  // 例如：
  // {
  //   path: '/doctor/dashboard',
  //   name: 'DoctorDashboard',
  //   component: () => import('../apps/doctor_app/DashboardPage.vue')
  // }
];

export default doctorRoutes;