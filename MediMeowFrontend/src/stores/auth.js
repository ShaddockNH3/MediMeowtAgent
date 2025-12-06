import { defineStore } from 'pinia'
import request from '../api/request'

export const useAuthStore = defineStore('auth', {
    state: () => ({
        token: localStorage.getItem('token') || '',
        doctor: JSON.parse(localStorage.getItem('doctor') || 'null'),
        user: JSON.parse(localStorage.getItem('user') || 'null'),
        role: localStorage.getItem('role') || '' // 'doctor' or 'patient'
    }),
    getters: {
        isLoggedIn: (state) => !!state.token
    },
    actions: {
        // Doctor Login
        async login(username, password) {
            try {
                const res = await request.post('/doctor/login', null, {
                    params: { username, password }
                })

                const data = res.data
                this.token = data.token
                this.doctor = data.doctor
                this.role = 'doctor'

                localStorage.setItem('token', this.token)
                localStorage.setItem('doctor', JSON.stringify(this.doctor))
                localStorage.setItem('role', 'doctor')

                return true
            } catch (error) {
                console.error('Login failed:', error)
                throw error
            }
        },
        logout() {
            this.token = ''
            this.doctor = null
            this.user = null
            this.role = ''
            localStorage.removeItem('token')
            localStorage.removeItem('doctor')
            localStorage.removeItem('user')
            localStorage.removeItem('role')
        }
    }
})
