<template>
  <div class="h-full overflow-hidden w-full bg-surface-900 text-surface-200 flex flex-col">
    <!-- Header Controls -->
    <header class="flex-shrink-0 flex items-center justify-between px-6 py-4 border-b border-surface-700 bg-surface-800/80 backdrop-blur z-10">
      <div>
        <h1 class="text-2xl font-light tracking-tight text-white flex items-center gap-3">
          Centro de Comando Temporal
        </h1>
        <p class="text-[11px] text-surface-400 font-mono tracking-widest mt-1 uppercase">Sovereign Cognitive Hub</p>
      </div>

      <!-- Navigation Tabs -->
      <div class="flex items-center bg-surface-900 border border-surface-700/50 rounded-lg p-1 gap-1">
        <button v-for="tab in availableTabs" :key="tab.id"
                @click="activeTab = tab.id"
                :class="[activeTab === tab.id ? 'bg-surface-700 text-white shadow-sm' : 'text-surface-400 hover:text-surface-200 hover:bg-surface-800', tab.id === 'graph' ? 'text-primary-400' : '']"
                class="px-4 py-1.5 rounded-md text-xs font-medium transition-all flex items-center gap-2">
            <span :class="tab.icon"></span>
            {{ tab.label }}
        </button>
      </div>
    </header>

    <!-- Main Content Area -->
    <main class="flex-1 overflow-hidden relative">
        
       <!-- GRAPH VIEW -->
       <div v-show="activeTab === 'graph'" class="absolute inset-0 w-full h-full p-4">
           <CognitiveGraph 
                ref="graphComponent"
                @node-click="openInVault" 
                class="w-full h-full rounded-2xl border border-surface-700/60 shadow-2xl" 
           />
       </div>

       <!-- AGENDA VIEWS -->
       <div v-show="activeTab !== 'graph'" class="absolute inset-0 w-full h-full overflow-y-auto p-6">
           <div class="max-w-5xl mx-auto flex flex-col gap-6 relative">
               
               <div v-if="isLoadingAgenda" class="flex flex-col items-center justify-center py-20 text-surface-500">
                  <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" class="animate-spin text-surface-600 mb-4" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
                  Carregando malha temporal...
               </div>

               <template v-else>
                   <!-- Header Dynamic based on Tab -->
                   <div class="flex items-center justify-between mb-2">
                       <h2 class="text-lg font-medium text-surface-200 flex items-center gap-2">
                           <span class="i-ph-calendar-check-duotone text-xl text-primary-400"></span>
                           Resumo Funcional: {{ tabLabels[activeTab] }}
                       </h2>
                       <div v-if="agenda[activeTab]" class="text-xs font-mono text-surface-500 bg-surface-800 px-2 py-1 rounded">
                           {{ agenda[activeTab]?.docs?.length || 0 }} Notas · {{ agenda[activeTab]?.tasks?.length || 0 }} Pendências
                       </div>
                   </div>

                   <!-- Grid: Left (Notes) / Right (Tasks & Pomodoro) -->
                   <div v-if="agenda[activeTab]" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                       
                       <!-- Modificações -->
                       <section class="bg-surface-800/50 border border-surface-700/50 rounded-xl p-5 backdrop-blur-sm flex flex-col">
                           <h3 class="text-sm font-semibold text-surface-300 mb-3 flex items-center gap-2">
                               Fluxo de Conhecimento (Notas Modificadas)
                           </h3>
                           
                           <div v-if="!agenda[activeTab]?.docs?.length" class="flex-1 flex flex-col items-center justify-center py-6 text-surface-500 border border-dashed border-surface-700 rounded-lg bg-surface-900/40">
                               <p class="text-xs">Nenhum registro nesta janela de tempo.</p>
                           </div>
                           
                           <div v-else class="space-y-2">
                               <div v-for="doc in agenda[activeTab]?.docs" :key="doc.path" 
                                    @click="openInVault(doc)"
                                    class="group flex flex-col p-3 rounded-lg bg-surface-900/50 border border-surface-700/30 hover:bg-surface-700/50 hover:border-primary-500/30 cursor-pointer transition-all">
                                   <div class="flex items-center justify-between">
                                       <div class="flex items-center gap-2">
                                           <span class="i-ph-file-text-duotone text-surface-500 group-hover:text-primary-400 text-base transition-colors"></span>
                                           <h4 class="text-sm font-medium text-surface-200 group-hover:text-white truncate max-w-[200px]">{{ doc.name }}</h4>
                                       </div>
                                       <span class="text-[10px] text-surface-500 font-mono">{{ formatTime(doc.dt) }}</span>
                                   </div>
                                   <p class="text-[10px] text-surface-600 mt-1 truncate">{{ doc.path }}</p>
                               </div>
                           </div>
                       </section>

                       <!-- Lado Direito: Pomodoro + Tarefas -->
                       <div class="flex flex-col gap-6">
                           
                           <!-- Widget Pomodoro (Exclusivo pro Hoje ou Persistente?) -->
                           <!-- Vamos deixar em todas as abas pra utilidade geral, focado na Task -->
                           <PomodoroWidget 
                              :targetTask="pomodoroTarget" 
                              @task-cleared="pomodoroTarget = null" 
                           />

                           <!-- Tarefas Pendentes Restritas à Data -->
                           <section class="bg-surface-800/50 border border-surface-700/50 rounded-xl p-5 backdrop-blur-sm flex flex-col flex-1">
                               <h3 class="text-sm font-semibold text-amber-400/90 mb-3 flex items-center gap-2">
                                   Ações Requeridas (Vault Tasks)
                               </h3>

                           <div v-if="!agenda[activeTab]?.tasks?.length" class="flex-1 flex flex-col items-center justify-center py-6 text-surface-500 border border-dashed border-surface-700 rounded-lg bg-surface-900/40">
                               <p class="text-xs">Missão cumprida! Nenhuma pendência aberta.</p>
                           </div>

                           <div v-else class="space-y-1.5 overflow-y-auto max-h-[500px] custom-scroll">
                               <div v-for="(task, idx) in agenda[activeTab]?.tasks" :key="idx" 
                                    class="flex items-start gap-3 p-2.5 rounded-lg bg-surface-900/30 hover:bg-surface-700/30 cursor-pointer group transition-colors">
                                   <input type="checkbox" class="mt-0.5 rounded bg-surface-900 border-surface-600 text-primary-500 focus:ring-primary-500 focus:ring-offset-surface-900 cursor-pointer" />
                                   <div class="flex-1">
                                       <p class="text-sm text-surface-300 leading-snug">{{ task.text }}</p>
                                       <div class="mt-2 flex items-center gap-2">
                                          <p class="text-[10px] text-surface-500 font-mono group-hover:text-amber-400/80 transition-colors cursor-pointer" @click.stop="openInVault(task)">
                                              Extraído de: {{ task.file_name }}
                                          </p>
                                          <button @click.stop="focusOnTask(task.text)" class="opacity-0 group-hover:opacity-100 px-2 py-0.5 rounded bg-primary-500/20 text-primary-400 text-[9px] uppercase tracking-wider hover:bg-primary-500 hover:text-white transition-all">
                                              Focar Nisso
                                          </button>
                                       </div>
                                   </div>
                               </div>
                           </div>
                       </section>
                       
                       </div><!-- Fim Lado Direito -->

                   </div>
               </template>
           </div>
       </div>

    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import CognitiveGraph from '../components/Vault/CognitiveGraph.vue'
import PomodoroWidget from '../components/Dashboard/PomodoroWidget.vue'

const router = useRouter()
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const availableTabs = [
    { id: 'today', label: 'Hoje', icon: 'i-ph-calendar-star-duotone' },
    { id: 'this_week', label: 'Nesta Semana', icon: 'i-ph-calendar-blank-duotone' },
    { id: 'last_week', label: 'Semana Passada', icon: 'i-ph-clock-counter-clockwise-duotone' },
    { id: 'this_month', label: 'Este Mês', icon: 'i-ph-calendar-duotone' },
    { id: 'this_year', label: 'Panorama Anual', icon: 'i-ph-binoculars-duotone' },
    { id: 'graph', label: 'Grafo Cognitivo', icon: 'i-ph-graph-duotone' }
]

const tabLabels: Record<string, string> = {
    'today': 'Foco Diário',
    'this_week': 'Produtividade da Semana',
    'last_week': 'Retrospectiva Semanal',
    'this_month': 'Agregado do Mês',
    'this_year': 'Panorama e Metas Anuais'
}

const activeTab = ref('today')
const isLoadingAgenda = ref(true)
const graphComponent = ref<any>(null)

watch(activeTab, (newVal: string) => {
    if (newVal === 'graph') {
        // Dispatch explicit window resize to force ForceGraph to measure the now-visible DOM
        setTimeout(() => {
            window.dispatchEvent(new Event('resize'))
            // E chama função handler filho pra acionar grafos se a ref for injetada no componente
            if (graphComponent.value && graphComponent.value.handleResize) {
                graphComponent.value.handleResize()
            }
        }, 100)
    }
})

// -- Pomodoro State Integration --
const pomodoroTarget = ref<string | null>(null)

const focusOnTask = (taskText: string) => {
    // Scroll To Top to see the timer
    const mainContainer = document.querySelector('main > div > div.max-w-5xl')
    if(mainContainer) mainContainer.scrollIntoView({ behavior: 'smooth' })
    
    pomodoroTarget.value = taskText
}

interface AgendaBucket {
    docs: any[]
    tasks: any[]
}

const agenda = ref<Record<string, AgendaBucket>>({})

const fetchAgenda = async () => {
    isLoadingAgenda.value = true
    try {
        const token = localStorage.getItem('sovereign_token') || ''
        const headers = { 'Authorization': `Bearer ${token}` }
        
        const res = await fetch(`${API_BASE_URL}/v1/vault/agenda`, { headers })
        if (res.ok) {
            agenda.value = await res.json()
        }
    } catch(e) {
        console.error("Erro ao puxar dados da Agenda Temporal:", e)
    } finally {
        isLoadingAgenda.value = false
    }
}

const formatTime = (isoString: string) => {
    if (!isoString) return ''
    const d = new Date(isoString)
    return d.toLocaleDateString('pt-BR', {day: '2-digit', month: 'short'}) + ' ' + d.toLocaleTimeString('pt-BR', {hour: '2-digit', minute:'2-digit'})
}

const openInVault = (doc: any) => {
    // Navigate straight to vault with query param
    router.push({ path: '/vault', query: { file: doc.path } })
}

onMounted(() => {
    fetchAgenda()
})
</script>

<style scoped>
.custom-scroll::-webkit-scrollbar {
  width: 6px;
}
.custom-scroll::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scroll::-webkit-scrollbar-thumb {
  background-color: rgba(255,255,255,0.1);
  border-radius: 10px;
}
.custom-scroll:hover::-webkit-scrollbar-thumb {
  background-color: rgba(255,255,255,0.2);
}
</style>
