import { defineStore } from 'pinia'
import request from '../api/request'
import { useAuthStore } from './auth'

export const usePatientStore = defineStore('patient', {
    state: () => ({
        patients: [],
        loading: false,
        error: null,
        currentPatient: null
    }),
    actions: {
        async fetchQueue() {
            this.loading = true
            this.error = null
            const authStore = useAuthStore()

            try {
                if (!authStore.doctor) {
                    throw new Error("No doctor logged in")
                }

                // 1. Get Queue IDs
                const queueRes = await request.get('/doctor/queue', {
                    params: { user_id: authStore.doctor.id }
                })
                const recordIds = queueRes.data.record_ids || []

                if (recordIds.length === 0) {
                    this.patients = []
                    return
                }

                // 2. Fetch details for each record
                // Note: In a real app we would want a bulk API or pagination with details.
                // This is the workaround for the N+1 problem.
                const detailPromises = recordIds.map(id =>
                    request.get(`/doctor/summary/${id}`)
                        .then(res => ({
                            record_id: id,
                            // API returns {base: {...}, data: {...}}, extract inner data
                            ...(res.data?.data || res.data)
                        }))
                        .catch(err => {
                            console.error(`Failed to fetch summary for ${id}`, err)
                            return null
                        })
                )

                const details = await Promise.all(detailPromises)
                this.patients = details.filter(item => item !== null)

            } catch (err) {
                console.error('Fetch queue failed:', err)
                this.error = err.message || '获取患者列表失败'
            } finally {
                this.loading = false
            }
        },

        async submitDiagnosis(recordId, text) {
            try {
                await request.post('/doctor/report', {
                    record_id: recordId,
                    text: text
                })
                // Remove from local queue or update status
                this.patients = this.patients.filter(p => p.record_id !== recordId)
                return true
            } catch (err) {
                console.error('Submit report failed', err)
                throw err
            }
        }
    }
})
