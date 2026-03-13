<script setup lang="ts">
import { ref, onMounted } from 'vue'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || `http://${typeof window !== 'undefined' ? window.location.hostname : 'localhost'}:8000`

interface BlueCollarTask {
  id: string
  topic: string
  frequency: string
  is_active: boolean
  last_run_at: string | null
  next_run_at: string | null
  status: string
  last_log: string | null
}

const tasks = ref<BlueCollarTask[]>([])
const newTopic = ref('')
const newFrequency = ref('manual')
const isSubmitting = ref(false)

const fetchTasks = async () => {
  try {
    const token = localStorage.getItem('sovereign_token')
    const headers: Record<string, string> = {}
    if (token) headers['Authorization'] = `Bearer ${token}`
    
    const res = await fetch(`${API_BASE_URL}/v1/blue-collar`, { headers })
    if (res.ok) {
      tasks.value = await res.json()
    }
  } catch (error) {
    console.error("Erro ao carregar Missões Blue Collar:", error)
  }
}

const createTask = async () => {
  if (!newTopic.value.trim()) return
  isSubmitting.value = true
  
  try {
    const token = localStorage.getItem('sovereign_token')
    const headers: Record<string, string> = { 'Content-Type': 'application/json' }
    if (token) headers['Authorization'] = `Bearer ${token}`
    
    const payload = {
       topic: newTopic.value,
       frequency: newFrequency.value
    }
    
    const res = await fetch(`${API_BASE_URL}/v1/blue-collar`, {
      method: 'POST',
      headers,
      body: JSON.stringify(payload)
    })
    
    if (res.ok) {
        newTopic.value = ''
        await fetchTasks()
    }
  } catch (error) {
      console.error("Erro ao criar missão:", error)
  } finally {
      isSubmitting.value = false
  }
}

const runTask = async (id: string) => {
   try {
    const token = localStorage.getItem('sovereign_token')
    const headers: Record<string, string> = {}
    if (token) headers['Authorization'] = `Bearer ${token}`
    
    const taskIdx = tasks.value.findIndex(t => t.id === id)
    if (taskIdx >= 0) {
      const t = tasks.value[taskIdx]
      if (t) t.status = 'running'
    }
    
    await fetch(`${API_BASE_URL}/v1/blue-collar/${id}/run`, {
      method: 'POST',
      headers
    })
    
    // Atualiza a lista pra refletir o novo log/status após alguns segundos (emulação)
    setTimeout(fetchTasks, 6000)
    
  } catch (error) {
    console.error("Erro ao forçar execução da missão:", error)
  }
}

const deleteTask = async (id: string) => {
   try {
    const token = localStorage.getItem('sovereign_token')
    const headers: Record<string, string> = {}
    if (token) headers['Authorization'] = `Bearer ${token}`
    
    const res = await fetch(`${API_BASE_URL}/v1/blue-collar/${id}`, {
      method: 'DELETE',
      headers
    })
    
    if (res.ok) {
       tasks.value = tasks.value.filter(t => t.id !== id)
    }
  } catch (error) {
    console.error("Erro ao deletar missão:", error)
  }
}

onMounted(() => {
    fetchTasks()
})
</script>

<template>
  <div class="h-full flex flex-col p-6 bg-surface-50 dark:bg-surface-900 overflow-y-auto custom-scroll">
     
     <div class="flex items-center gap-4 mb-8">
        <div class="w-12 h-12 rounded-xl bg-orange-500/10 border border-orange-500/20 flex flex-col items-center justify-center text-orange-500 shadow-[0_0_15px_rgba(249,115,22,0.15)]">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"></path></svg>
        </div>
        <div>
            <h2 class="text-2xl font-light text-surface-900 dark:text-white">Blue Collar Worker</h2>
            <p class="text-sm text-surface-500 mt-1 uppercase tracking-widest font-mono">Trabalhador Braçal Autônomo na Oracle OCI</p>
        </div>
     </div>

     <!-- Painel de Ingestão / Cadastro de Agente -->
     <div class="bg-surface-100 dark:bg-surface-800/60 border border-surface-200 dark:border-surface-700/50 rounded-2xl p-6 mb-8 shadow-xl">
         <h3 class="text-xs tracking-widest uppercase font-bold text-surface-400 mb-4 flex items-center gap-2">
            <svg class="w-4 h-4 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
            Delegar Missão de Scraper
         </h3>
         
         <div class="flex flex-col md:flex-row gap-4 items-end">
            <div class="flex-1 w-full">
                <label class="block text-xs text-surface-500 mb-2">Tópico de Pesquisa (Contexto-Alvo)</label>
                <input v-model="newTopic" @keyup.enter="createTask" type="text" placeholder="Ex: Últimos papers sobre Multi-Agent LLMs" class="w-full bg-surface-50 dark:bg-surface-900 border border-surface-300 dark:border-surface-700 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-primary-500 transition-colors shadow-inner" />
            </div>
            <div class="w-full md:w-48">
                <label class="block text-xs text-surface-500 mb-2">Ciclo de Ingestão</label>
                <select v-model="newFrequency" class="w-full bg-surface-50 dark:bg-surface-900 border border-surface-300 dark:border-surface-700 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-primary-500 transition-colors appearance-none shadow-inner">
                    <option value="manual">Disparo Manual</option>
                    <option value="hourly">Pesquisa Horária</option>
                    <option value="daily">Pesquisa Diária</option>
                </select>
            </div>
            <button @click="createTask" :disabled="isSubmitting || !newTopic.trim()" class="h-[46px] px-8 bg-orange-500 hover:bg-orange-400 disabled:bg-surface-700 disabled:text-surface-500 text-white rounded-xl shadow-[0_0_15px_rgba(249,115,22,0.2)] font-medium transition-all flex items-center gap-2">
                <span v-if="!isSubmitting">Delegar</span>
                <svg v-else class="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
            </button>
         </div>
     </div>

     <!-- Missões Ativas -->
     <h3 class="text-xs tracking-widest uppercase font-bold text-surface-400 mb-4 border-b border-surface-200 dark:border-surface-700/50 pb-2">
        Missões de Vigilância ({{ tasks.length }})
     </h3>
     
     <div v-if="tasks.length === 0" class="text-center py-12 text-surface-500 border border-dashed border-surface-300 dark:border-surface-700 rounded-2xl bg-surface-100/30 dark:bg-surface-800/30">
        Nenhuma missão delegada ao Blue Collar.
     </div>

     <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
         <div v-for="task in tasks" :key="task.id" class="bg-surface-100 dark:bg-surface-800/40 border border-surface-200 dark:border-surface-700/50 rounded-2xl p-5 hover:border-surface-300 dark:hover:border-surface-600 transition-all flex flex-col group relative overflow-hidden">
             
             <!-- Animated Gradient Background for 'running' status -->
             <div v-if="task.status === 'running'" class="absolute inset-0 bg-gradient-to-r from-transparent via-orange-500/5 to-transparent animate-[shimmer_2s_infinite] -z-0"></div>

             <div class="flex justify-between items-start mb-3 z-10">
                 <div class="flex items-center gap-3">
                     <span class="flex h-2.5 w-2.5 relative">
                        <span v-if="task.status === 'running'" class="animate-ping absolute inline-flex h-full w-full rounded-full bg-orange-400 opacity-75"></span>
                        <span class="relative inline-flex rounded-full h-2.5 w-2.5" :class="task.status === 'running' ? 'bg-orange-500' : (task.status === 'error' ? 'bg-rose-500' : 'bg-surface-500')"></span>
                     </span>
                     <h4 class="font-medium text-surface-900 dark:text-slate-200 text-sm line-clamp-1 title-font">{{ task.topic }}</h4>
                 </div>
                 <div class="flex gap-2">
                     <span class="px-2 py-1 text-[10px] font-mono tracking-wider uppercase rounded-md border" :class="task.frequency === 'manual' ? 'border-surface-600 text-surface-400 bg-surface-800/50' : 'border-sky-500/30 text-sky-400 bg-sky-500/10'">
                        {{ task.frequency }}
                     </span>
                     <button @click="deleteTask(task.id)" class="text-surface-500 hover:text-rose-400 transition-colors opacity-0 group-hover:opacity-100" title="Apagar Missão">
                         <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                     </button>
                 </div>
             </div>
             
             <div class="text-[11px] text-surface-500 font-mono bg-surface-50 dark:bg-surface-900/50 p-3 rounded-lg border border-surface-200 dark:border-surface-700 line-clamp-2 h-12 z-10 flex-1 flex items-center">
                 > {{ task.last_log || 'Aguardando inicialização do OCI...' }}
             </div>
             
             <div class="mt-4 flex justify-between items-center z-10">
                 <div class="text-[10px] text-surface-500 font-mono tracking-widest uppercase">
                    Última Checagem: {{ task.last_run_at ? new Date(task.last_run_at).toLocaleString() : 'Nunca' }}
                 </div>
                 <button @click="runTask(task.id)" :disabled="task.status === 'running'" class="flex items-center gap-2 text-xs font-medium text-orange-500 hover:text-orange-400 disabled:text-surface-600 transition-colors">
                     <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                     {{ task.status === 'running' ? 'Minerando...' : 'Forçar Scraper Agora' }}
                 </button>
             </div>
         </div>
     </div>
  </div>
</template>

<style scoped>
@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}
.title-font {
    font-family: ui-sans-serif, system-ui, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji";
}
</style>
