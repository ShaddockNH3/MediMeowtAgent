import axios from 'axios'
import { useAuthStore } from '../stores/auth'

const service = axios.create({
    baseURL: '/api', // Proxy will handle this
    timeout: 5000
})

// Request interceptor
service.interceptors.request.use(
    (config) => {
        const authStore = useAuthStore()
        if (authStore.token) {
            config.headers['Authorization'] = `Bearer ${authStore.token}`
        }
        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

// Response interceptor
service.interceptors.response.use(
    (response) => {
        const res = response.data
        // Backend returns { base: { code: "10000", msg: "..." }, data: ... }
        // Check res.base.code
        if (res.base && res.base.code !== '10000') {
            console.error('Error:', res.base.msg)

            // Handle auth errors
            if (res.base.code === '401' || res.base.code === '10003') {
                const authStore = useAuthStore()
                authStore.logout()
                location.reload()
            }

            return Promise.reject(new Error(res.base.msg || 'Error'))
        } else {
            return res
        }
    },
    (error) => {
        console.error('API Error:', error)
        return Promise.reject(error)
    }
)

export default service
