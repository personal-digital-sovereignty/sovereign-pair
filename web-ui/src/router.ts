import { createRouter, createWebHistory } from 'vue-router'
import VaultView from './views/VaultView.vue'
import DashboardView from './views/DashboardView.vue'
import ProjectsHubView from './views/ProjectsHubView.vue'

const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: '/',
            redirect: '/dashboard'
        },
        {
            path: '/dashboard',
            name: 'dashboard',
            component: DashboardView
        },
        {
            path: '/vault',
            name: 'vault',
            component: VaultView
        },
        {
            path: '/projects',
            name: 'projects',
            component: ProjectsHubView
        }
    ]
})

export default router
