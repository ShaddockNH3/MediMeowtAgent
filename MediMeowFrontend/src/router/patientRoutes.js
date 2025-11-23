// D:\code\ruangong\new\src\router\patientRoutes.js
import PatientLogin from '../apps/patient_app/PatientLogin.vue';
import PatientIdentity from '../apps/patient_app/PatientIdentity.vue';

const patientRoutes = [
  {
    path: '/patient/login', // 病患端主页可能就是登录页
    name: 'PatientHome',
    component: PatientLogin,
  },
  {
    path: '/patient/identity', // 登录成功后跳转到 /patient/identity
    name: 'PatientIdentity',
    component: PatientIdentity,
  },
  // ... 其他病患路由
];

export default patientRoutes;