<template>
  <div v-if="authPhase === 'loading'" class="fixed inset-0 flex w-full bg-surface-900 items-center justify-center">
      <div class="text-white animate-pulse">Invocando o RAG...</div>
  </div>
  <Setup v-else-if="authPhase === 'setup'" @setup-complete="checkAuthStatus" />
  <Login v-else-if="authPhase === 'login'" @login-success="checkAuthStatus" />
  
  <!-- Render the active route (Chat or Vault) when Authenticated -->
  <div v-else class="flex w-full h-full bg-[#0E0E10] text-[#E0E0E0] overflow-hidden">
    <SidebarTree class="w-64 border-r border-[#222222] bg-[#121214] flex-shrink-0" />
    <main class="flex-1 overflow-hidden relative focus:outline-none">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import Setup from './views/Setup.vue'
import Login from './views/Login.vue'
import SidebarTree from './components/Vault/SidebarTree.vue'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const authPhase = ref('loading')

const checkAuthStatus = async () => {
  try {
    const res = await fetch(`${API_BASE_URL}/v1/auth/status`)
    const data = await res.json()
    if (!data.is_setup) {
      authPhase.value = 'setup'
    } else {
      const token = localStorage.getItem('sovereign_token')
      if (!token) {
        authPhase.value = 'login'
      } else {
        authPhase.value = 'authenticated'
      }
    }
  } catch(e) {
    console.error("Auth Server offline", e)
  }
}

onMounted(() => {
  checkAuthStatus()
})
</script>
