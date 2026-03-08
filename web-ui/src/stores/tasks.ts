import { defineStore } from 'pinia'
import axios from 'axios'

export interface Task {
    id: string
    project_id: string
    tenant_id: string
    title: string
    description?: string
    status: string // TODO, DOING, DONE, BLOCKED
    priority: string // High, Medium, Low
    order_index: number
    deadline?: string
    file_path?: string
    last_synced_at?: string
    created_at?: string
    updated_at?: string
}

const getBaseURL = () => import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const getHeaders = () => {
    const token = localStorage.getItem('sovereign_token')
    return token ? { Authorization: `Bearer ${token}` } : {}
}

export const useTasksStore = defineStore('tasks', {
    state: () => ({
        tasks: [] as Task[],
        loading: false,
        error: null as string | null
    }),
    getters: {
        tasksByProject: (state) => {
            return (projectId: string) => state.tasks.filter(t => t.project_id === projectId)
        }
    },
    actions: {
        async fetchProjectTasks(projectId: string) {
            this.loading = true
            this.error = null
            try {
                const res = await axios.get(`${getBaseURL()}/v1/projects/${projectId}/tasks`, { headers: getHeaders() })

                // Remove old tasks from this project to avoid duplicates, then append new
                this.tasks = [...this.tasks.filter(t => t.project_id !== projectId), ...res.data]
            } catch (err: any) {
                this.error = err.message || 'Failed to fetch tasks'
            } finally {
                this.loading = false
            }
        },
        async createTask(projectId: string, payload: Partial<Task>) {
            try {
                const res = await axios.post(`${getBaseURL()}/v1/projects/${projectId}/tasks`, payload, { headers: getHeaders() })
                this.tasks.push(res.data)
                return res.data
            } catch (err: any) {
                throw new Error(err.message || 'Create task failed')
            }
        },
        async updateTask(taskId: string, payload: Partial<Task>) {
            try {
                const res = await axios.put(`${getBaseURL()}/v1/tasks/${taskId}`, payload, { headers: getHeaders() })
                const idx = this.tasks.findIndex(t => t.id === taskId)
                if (idx !== -1) {
                    this.tasks[idx] = res.data
                }
                return res.data
            } catch (err: any) {
                throw new Error(err.message || 'Update task failed')
            }
        },
        async deleteTask(taskId: string) {
            try {
                await axios.delete(`${getBaseURL()}/v1/tasks/${taskId}`, { headers: getHeaders() })
                this.tasks = this.tasks.filter(t => t.id !== taskId)
            } catch (err: any) {
                throw new Error(err.message || 'Delete task failed')
            }
        }
    }
})
