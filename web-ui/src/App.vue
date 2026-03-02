<template>
  <div v-if="authPhase === 'loading'" class="fixed inset-0 flex w-full bg-surface-900 items-center justify-center">
      <div class="text-white animate-pulse">Invocando o RAG...</div>
  </div>
  <Setup v-else-if="authPhase === 'setup'" @setup-complete="checkAuthStatus" />
  <Login v-else-if="authPhase === 'login'" @login-success="checkAuthStatus" />
  
  <!-- Render the active route (Chat or Vault) when Authenticated -->
  <div v-else class="flex w-full h-full bg-[#0E0E10] text-[#E0E0E0] overflow-hidden">
    
    <!-- Activity Bar (Vertical Bar with Hamburger Menu) -->
    <div class="w-14 h-full bg-[#09090B] border-r border-[#222222] flex flex-col items-center py-4 gap-6 flex-shrink-0 z-20">
      
      <!-- Hamburger Toggle -->
      <button @click="isSidebarOpen = !isSidebarOpen" class="text-zinc-400 hover:text-white transition-colors p-1.5 rounded hover:bg-white/5" title="Menu">
        <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-menu"><line x1="4" x2="20" y1="12" y2="12"/><line x1="4" x2="20" y1="6" y2="6"/><line x1="4" x2="20" y1="18" y2="18"/></svg>
      </button>

      <!-- Global Navigation Icons -->
      <div class="flex flex-col gap-4 mt-2">
        <router-link to="/dashboard" class="text-zinc-500 hover:text-emerald-400 p-2 rounded-lg hover:bg-white/5 transition-all" title="Sensus Home" active-class="text-emerald-400 bg-emerald-500/10">
          <span class="i-ph-house-duotone text-xl block"></span>
        </router-link>
        <router-link to="/chat" class="text-zinc-500 hover:text-purple-400 p-2 rounded-lg hover:bg-white/5 transition-all" title="Sovereign Chat" active-class="text-purple-400 bg-purple-500/10">
          <span class="i-ph-chats-teardrop-duotone text-xl block"></span>
        </router-link>
        <router-link to="/projects" class="text-zinc-500 hover:text-cyan-400 p-2 rounded-lg hover:bg-white/5 transition-all" title="Virtual Hub" active-class="text-cyan-400 bg-cyan-500/10">
          <span class="i-ph-folders-duotone text-xl block"></span>
        </router-link>
        <router-link to="/vault" class="text-zinc-500 hover:text-white p-2 rounded-lg hover:bg-white/5 transition-all" title="Explore Vault" active-class="text-white bg-white/10">
          <span class="i-ph-books-duotone text-xl block"></span>
        </router-link>
      </div>
      
      <!-- Bottom Icons -->
      <div class="mt-auto flex flex-col gap-4 mb-2">
        <button class="text-zinc-500 hover:text-white p-2 rounded-lg hover:bg-white/5 transition-all" title="Settings">
          <span class="i-ph-gear-duotone text-xl block"></span>
        </button>
      </div>

    </div>

    <!-- Main Collapsible Sidebar -->
    <SidebarTree v-show="isSidebarOpen" class="w-64 border-r border-[#222222] bg-[#121214] flex-shrink-0 transition-all" />
    
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
const isSidebarOpen = ref(true)

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
