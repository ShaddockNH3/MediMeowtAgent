import { createRouter, createWebHistory } from 'vue-router'

// 1. 导入各个模块的路由配置
import patientRoutes from './patientRoutes'
import doctorRoutes from './doctorRoutes'

// 2. 将所有模块的路由数组合并成一个
const routes = [
  // 应用级别的路由（如首页重定向、404页面等）可以放在这里
  {
    path: '/',
    redirect: '/patient/login'
  },

  // 使用展开运算符 (...) 将模块路由合并进来
  ...patientRoutes,
  ...doctorRoutes,
  
  // 可以在最后加一个 404 页面
  // { path: '/:pathMatch(.*)*', name: 'NotFound', component: NotFoundView }
]

// 3. 创建和导出 router 实例（这部分逻辑不变）
const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router