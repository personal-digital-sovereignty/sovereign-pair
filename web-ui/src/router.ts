import { createRouter, createWebHistory } from 'vue-router'
import ChatView from './views/ChatView.vue'
import VaultView from './views/VaultView.vue'
import DashboardView from './views/DashboardView.vue'
import ProjectsHubView from './views/ProjectsHubView.vue'
import SettingsView from './views/SettingsView.vue'

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
            path: '/chat',
            name: 'chat',
            component: ChatView
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
        },
        {
            path: '/settings',
            name: 'settings',
            component: SettingsView
        }
    ]
})

export default router
