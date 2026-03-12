import { defineStore } from 'pinia'
import axios from 'axios'

export interface ProjectLink {
    id?: number
    url: string
    label: string
}

export interface ProjectLog {
    id?: number
    content: string
    created_at?: string
}

export interface Project {
    id: string
    tenant_id: string
    name: string
    purpose?: string
    traction_status: string // Ideation, Flowing, Blocked, Hibernating, Done
    next_action?: string
    energy_level: string // High, Med, Low
    progress_percent: number
    friction_radar?: string
    deadline?: string
    file_path?: string
    last_synced_at?: string
    created_at?: string
    updated_at?: string
    links: ProjectLink[]
    logs: ProjectLog[]
}

const getBaseURL = () => import.meta.env.VITE_RUST_CORE_URL || 'http://localhost:8001'
const getHeaders = () => {
    const token = localStorage.getItem('sovereign_token')
    return token ? { Authorization: `Bearer ${token}` } : {}
}

export const useProjectsStore = defineStore('projects', {
    state: () => ({
        projects: [] as Project[],
        loading: false,
        error: null as string | null
    }),
    actions: {
        async fetchProjects() {
            this.loading = true
            this.error = null
            try {
                const res = await axios.get(`${getBaseURL()}/v1/projects`, { headers: getHeaders() })
                this.projects = res.data
            } catch (err: any) {
                this.error = err.message || 'Failed to fetch projects'
            } finally {
                this.loading = false
            }
        },
        async createProject(payload: Partial<Project>) {
            try {
                const res = await axios.post(`${getBaseURL()}/v1/projects`, payload, { headers: getHeaders() })
                this.projects.push(res.data)
                return res.data
            } catch (err: any) {
                throw new Error(err.message || 'Create project failed')
            }
        },
        async updateProject(id: string, payload: Partial<Project>) {
            try {
                const res = await axios.put(`${getBaseURL()}/v1/projects/${id}`, payload, { headers: getHeaders() })
                const idx = this.projects.findIndex(p => p.id === id)
                if (idx !== -1) {
                    this.projects[idx] = res.data
                }
                return res.data
            } catch (err: any) {
                throw new Error(err.message || 'Update project failed')
            }
        },
        async deleteProject(id: string) {
            try {
                await axios.delete(`${getBaseURL()}/v1/projects/${id}`, { headers: getHeaders() })
                this.projects = this.projects.filter(p => p.id !== id)
            } catch (err: any) {
                throw new Error(err.message || 'Delete project failed')
            }
        }
    }
})
