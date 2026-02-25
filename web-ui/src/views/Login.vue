<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-gray-900 bg-opacity-90 backdrop-blur-md">
    <div class="w-full max-w-md bg-gray-800 rounded-xl shadow-2xl p-8 border border-gray-700">
      
      <div class="text-center mb-6">
        <h2 class="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-emerald-400 to-blue-400">
          Identidade Local
        </h2>
        <p class="text-gray-400 text-sm mt-1">Insira a credencial mestra do Sovereign Pair.</p>
      </div>

      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-400 mb-1">Senha (Master Auth)</label>
          <input 
            v-model="password" 
            @keyup.enter="doLogin"
            type="password" 
            class="w-full bg-gray-900 border border-gray-600 rounded-lg p-3 text-white focus:ring-2 focus:ring-blue-500 outline-none transition" 
            placeholder="Sua senha secreta inviolável..."
          >
        </div>
      </div>

      <div class="mt-6 flex justify-end">
        <button 
          @click="doLogin" 
          :disabled="isSubmitting || !password" 
          class="w-full bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition disabled:opacity-50 flex justify-center"
        >
          <span v-if="isSubmitting">Conectando...</span>
          <span v-else>Desbloquear Acesso</span>
        </button>
      </div>
      
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const emit = defineEmits(['login-success'])

const password = ref('')
const isSubmitting = ref(false)

const doLogin = async () => {
  if (!password.value) return
  isSubmitting.value = true
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  
  try {
    const res = await fetch(`${API_BASE_URL}/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password: password.value })
    })
    
    if (res.ok) {
      const data = await res.json()
      localStorage.setItem('sovereign_token', data.access_token)
      emit('login-success')
    } else {
      alert('Acesso Negado: Senha inválida.')
    }
  } catch(e) {
    alert('Erro de conexão ao Servidor Soberano.')
    console.error(e)
  } finally {
    isSubmitting.value = false
  }
}
</script>
