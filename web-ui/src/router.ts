import { createRouter, createWebHistory } from 'vue-router'
import VaultView from './views/VaultView.vue'

const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: '/',
            redirect: '/vault'
        },
        {
            path: '/vault',
            name: 'vault',
            component: VaultView
        }
    ]
})

export default router
