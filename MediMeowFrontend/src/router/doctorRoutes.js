// 用 @ 别名导入（推荐，与 tsconfig/vite 配置对齐，更稳定）
import DoctorLogin from '@/apps/doctor_app/components/DoctorLogin.vue';
import DoctorView from '@/apps/doctor_app/components/DoctorView.vue'; // 路径完全正确，无需改
import DoctorQueue from '@/apps/doctor_app/components/DoctorQueue.vue';
import DoctorSummary from '@/apps/doctor_app/components/DoctorSummary.vue';
import DoctorReport from '@/apps/doctor_app/components/DoctorReport.vue';
import DoctorQuestionnaireImport from '@/apps/doctor_app/components/DoctorQuestionnaireImport.vue';

// 路由配置部分完全不变！
const doctorRoutes = [
  {
    path: '/doctor/login',
    name: 'DoctorLogin',
    component: DoctorLogin,
  },
  {
    path: '/doctor',
    name: 'DoctorView',
    component: DoctorView,
    meta: { requiresAuth: true }
  },
  {
    path: '/doctor/queue',
    name: 'DoctorQueue',
    component: DoctorQueue,
    meta: { requiresAuth: true }
  },
  {
    path: '/doctor/summary/:record_id',
    name: 'DoctorSummary',
    component: DoctorSummary,
    meta: { requiresAuth: true }
  },
  {
    path: '/doctor/report/:record_id',
    name: 'DoctorReport',
    component: DoctorReport,
    meta: { requiresAuth: true }
  },
  {
    path: '/doctor/questionnaire/import',
    name: 'DoctorQuestionnaireImport',
    component: DoctorQuestionnaireImport,
    meta: { requiresAuth: true }
  },
];

export default doctorRoutes;