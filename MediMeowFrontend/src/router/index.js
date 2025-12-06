import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            name: 'landing',
            component: () => import('../views/Landing.vue')
        },
        // Doctor Routes
        {
            path: '/doctor/login',
            name: 'doctor-login',
            component: () => import('../views/Login.vue')
        },
        {
            path: '/doctor/dashboard',
            name: 'dashboard', // Existing name kept for compatibility
            component: () => import('../views/Dashboard.vue'),
            meta: { requiresAuth: true, role: 'doctor' }
        },
        {
            path: '/doctor/patient/:id',
            name: 'patient-detail',
            component: () => import('../views/PatientDetail.vue'),
            meta: { requiresAuth: true, role: 'doctor' }
        },
        // Patient Routes
        {
            path: '/patient/login',
            name: 'patient-login',
            component: () => import('../views/patient/Login.vue')
        },
        {
            path: '/patient/register',
            name: 'patient-register',
            component: () => import('../views/patient/Register.vue')
        },
        {
            path: '/patient/bind-info',
            name: 'patient-bind',
            component: () => import('../views/patient/BindInfo.vue'),
            meta: { requiresAuth: true, role: 'patient' }
        },
        {
            path: '/patient/history',
            name: 'patient-history',
            component: () => import('../views/patient/HistoryList.vue'),
            meta: { requiresAuth: true, role: 'patient' }
        },
        {
            path: '/patient/record/:id',
            name: 'record-detail',
            component: () => import('../views/patient/RecordDetail.vue'),
            meta: { requiresAuth: true, role: 'patient' }
        },
        {
            path: '/patient/home',
            name: 'patient-home',
            component: () => import('../views/patient/Home.vue'),
            meta: { requiresAuth: true, role: 'patient' }
        },
        {
            path: '/patient/departments',
            name: 'department-list',
            component: () => import('../views/patient/DepartmentList.vue'),
            meta: { requiresAuth: true, role: 'patient' }
        },
        {
            path: '/patient/questionnaire/:deptId',
            name: 'questionnaire',
            component: () => import('../views/patient/Questionnaire.vue'),
            meta: { requiresAuth: true, role: 'patient' }
        },
        // Redirect
        {
            path: '/:pathMatch(.*)*',
            redirect: '/'
        }
    ]
})

router.beforeEach((to, from, next) => {
    const authStore = useAuthStore()

    // Check if route requires auth
    if (to.meta.requiresAuth) {
        if (!authStore.isLoggedIn) {
            if (to.meta.role === 'patient') {
                next({ name: 'patient-login' })
            } else {
                next({ name: 'doctor-login' })
            }
            return
        }

        // Role check (Optional based on implementation, here simplified)
        // In a real app we should check authStore.userType vs to.meta.role
    }

    // Public pages
    next()
})

export default router
