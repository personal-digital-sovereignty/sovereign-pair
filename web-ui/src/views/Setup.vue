<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-gray-900 bg-opacity-90 backdrop-blur-md">
    <div class="w-full max-w-2xl bg-gray-800 rounded-xl shadow-2xl overflow-hidden text-gray-100">
      
      <!-- Stepper Header -->
      <div class="bg-gray-700 p-6 border-b border-gray-600 flex justify-between items-center">
        <div>
          <h2 class="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-emerald-400">
            Sovereign Pair Setup
          </h2>
          <p class="text-gray-400 text-sm mt-1">Soberania cognitiva local. Fase de autenticação primária.</p>
        </div>
        <div class="text-xs font-mono bg-gray-800 px-3 py-1 rounded text-emerald-400 border border-emerald-500/30">
          Passo {{ step }} / 2
        </div>
      </div>

      <!-- Step 1: Identidade e Modelos -->
      <div v-if="step === 1" class="p-8 space-y-6">
        <p class="text-gray-300">Olá. Parece que é a sua primeira vez acessando a Interface Web do RAG em modelo Cloud/Standalone. Vamos configurar sua identidade básica para o backend.</p>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-400 mb-1">Como você se chama? (Nome do Usuário Pai)</label>
            <input v-model="form.owner_name" type="text" class="w-full bg-gray-900 border border-gray-600 rounded-lg p-3 text-white focus:ring-2 focus:ring-blue-500 outline-none transition" placeholder="Ex: Jeferson">
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-400 mb-1">E como devo me chamar? (Nome da sua IA Assistente)</label>
            <input v-model="form.sovereign_name" type="text" class="w-full bg-gray-900 border border-gray-600 rounded-lg p-3 text-white focus:ring-2 focus:ring-emerald-500 outline-none transition" placeholder="Ex: Sovereign Pair">
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-400 mb-1">Defina uma Senha de Master Login (B2C Security)</label>
            <input v-model="form.password" type="password" class="w-full bg-gray-900 border border-gray-600 rounded-lg p-3 text-white focus:ring-2 focus:ring-purple-500 outline-none transition" placeholder="Sua senha secreta inviolável...">
          </div>
        </div>

        <div class="flex justify-end pt-4">
          <button @click="nextStep" :disabled="!isStep1Valid" class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition disabled:opacity-50">
            Avançar →
          </button>
        </div>
      </div>

      <!-- Step 2: Finalização e Deploy -->
      <div v-if="step === 2" class="p-8 space-y-6 text-center">
        <div class="mb-4 text-emerald-400">
          <svg class="w-16 h-16 mx-auto animate-bounce" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path></svg>
        </div>
        <h3 class="text-xl font-bold text-white">Pronto para a Ascenção Local!</h3>
        <p class="text-gray-400 text-sm mx-auto max-w-md">Ao finalizar, seus dados de Identidade serão gravados via Mega-CLI para o Mega Backend (Proteção JWT). O ambiente será devidamente protegido.</p>
        
        <div class="bg-gray-900 p-4 rounded-lg text-left inline-block mt-4 mb-2 min-w-xs border border-gray-700 overflow-hidden shadow-inner">
          <p class="text-gray-400 font-mono text-xs mb-1">Resumo Executivo:</p>
          <ul class="text-sm font-mono text-gray-300 space-y-1">
            <li><span class="text-blue-400">Owner:</span> {{ form.owner_name }}</li>
            <li><span class="text-emerald-400">IA:</span> {{ form.sovereign_name }}</li>
            <li><span class="text-purple-400">Proteção:</span> Ativada (JWT Hashing)</li>
          </ul>
        </div>
        
        <div class="flex justify-between pt-4 mt-6">
          <button @click="step = 1" class="text-gray-400 hover:text-white px-4 py-2 transition">← Voltar</button>
          <button @click="submitSetup" :disabled="isSubmitting" class="bg-gradient-to-r from-emerald-500 to-blue-500 hover:from-emerald-400 hover:to-blue-400 text-white px-8 py-2 rounded-lg font-bold shadow-lg transform transition active:scale-95 disabled:opacity-50 flex items-center gap-2">
            <svg v-if="isSubmitting" class="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span v-else>Finalizar & Destrancar Interface</span>
          </button>
        </div>
      </div>
      
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const emit = defineEmits(['setup-complete'])

const step = ref(1)
const isSubmitting = ref(false)

const form = ref({
  owner_name: 'Jeferson',
  sovereign_name: 'Sovereign Pair',
  password: ''
})

const isStep1Valid = computed(() => {
  return form.value.owner_name.trim().length > 0 && 
         form.value.sovereign_name.trim().length > 0 && 
         form.value.password.trim().length >= 4
})

const nextStep = () => {
  if (isStep1Valid.value) step.value = 2
}

const submitSetup = async () => {
  isSubmitting.value = true
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || `http://${typeof window !== 'undefined' ? window.location.hostname : 'localhost'}:8000`
  
  try {
    const res = await fetch(`${API_BASE_URL}/v1/auth/setup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form.value)
    })
    
    if (res.ok) {
      const data = await res.json()
      // Salva o JWT retornado no localStorage persistemente!
      localStorage.setItem('sovereign_token', data.access_token)
      
      // Manda sinal pro Root do App (App.vue) para desmontar esta Wizard Screen
      emit('setup-complete')
    } else {
      alert('Erro ao realizar o Setup. O Backend já foi inicializado anteriormente.')
    }
  } catch(e) {
    alert('Erro de rede ao conectar à API para Setup Inicial.')
    console.error(e)
  } finally {
    isSubmitting.value = false
  }
}
</script>
