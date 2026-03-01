<template>
  <div v-if="authPhase === 'loading'" class="fixed inset-0 flex w-full bg-surface-900 items-center justify-center">
      <div class="text-white animate-pulse">Invocando o RAG...</div>
  </div>
  <Setup v-else-if="authPhase === 'setup'" @setup-complete="checkAuthStatus" />
  <Login v-else-if="authPhase === 'login'" @login-success="checkAuthStatus" />
  
  <!-- Render the active route (Chat or Vault) when Authenticated -->
  <router-view v-else />
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import Setup from './views/Setup.vue'
import Login from './views/Login.vue'

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
