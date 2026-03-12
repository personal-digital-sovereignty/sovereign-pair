<template>
  <div class="h-full overflow-hidden w-full bg-surface-900 text-surface-200 flex flex-col">
    <!-- Header Controls -->
    <header class="flex-shrink-0 flex items-center justify-between px-6 py-4 border-b border-surface-700 bg-surface-800/80 backdrop-blur z-10">
      <div>
        <h1 class="text-2xl font-light tracking-tight flex items-center gap-3 transition-colors" :class="sensusMode === 'enterprise' ? 'text-amber-400' : 'text-white'">
          {{ sensusMode === 'enterprise' ? 'Enterprise Command Center' : 'Centro de Comando Temporal' }}
        </h1>
        <p class="text-[11px] text-surface-400 font-mono tracking-widest mt-1 uppercase flex items-center gap-2">
           <span v-if="false" class="px-1.5 py-0.5 bg-amber-500/20 text-amber-400 border border-amber-500/30 rounded text-[9px] font-bold">B2B ACTIVE</span>
           Sovereign Cognitive Hub
        </p>
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
                   <!-- Header Dynamic based on Tab (Omitido na Quarentena) -->
                   <div v-if="activeTab !== 'quarantine'" class="flex items-center justify-between mb-2">
                       <h2 class="text-lg font-medium text-surface-200 flex items-center gap-2">
                           <span class="i-ph-calendar-check-duotone text-xl text-primary-400"></span>
                           Resumo Funcional: {{ tabLabels[activeTab] }}
                       </h2>
                       <div v-if="agenda[activeTab]" class="text-xs font-mono text-surface-500 bg-surface-800 px-2 py-1 rounded">
                           {{ agenda[activeTab]?.docs?.length || 0 }} Notas · {{ agenda[activeTab]?.tasks?.length || 0 }} Pendências
                       </div>
                   </div>

                   <!-- Grid: Left (Notes) / Right (Tasks & Pomodoro) (Somente Agenda Regular) -->
                   <div v-if="activeTab !== 'quarantine' && agenda[activeTab]" class="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
                       
                       <!-- Modificações -->
                       <section class="bg-surface-800/50 border border-surface-700/50 rounded-xl p-5 backdrop-blur-sm flex flex-col">
                           <h3 class="text-sm font-semibold text-surface-300 mb-3 flex items-center gap-2">
                               Fluxo de Conhecimento (Notas Modificadas)
                           </h3>
                           
                           <div v-if="!agenda[activeTab]?.docs?.length" class="h-32 flex flex-col items-center justify-center text-surface-500 border border-dashed border-surface-700 rounded-lg bg-surface-900/40">
                               <p class="text-xs">Nenhum registro nesta janela de tempo.</p>
                           </div>
                           
                           <div v-else class="space-y-2 max-h-[450px] overflow-y-auto custom-scroll pr-1">
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
                              v-if="sensusMode !== 'enterprise'"
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

                           <div v-else class="space-y-1.5 overflow-y-auto max-h-[500px] custom-scroll pr-1">
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

       <!-- THE GOD MODE COCKPIT (PHASE 27: FULL-WIDTH MASTERPLAN) -->
        <div v-show="activeTab === 'cockpit'" class="absolute inset-0 w-full h-full overflow-y-auto p-6 bg-surface-900/90 custom-scroll">
            <div class="w-full flex flex-col gap-6 relative min-h-full">
                
                <!-- O.S Terminal Integrado (The Hacker's CLI) -->
                <HackerCommandLine class="shrink-0 z-20" />
                
                <!-- Tri-Core Trackers (Telemetria, Cronos, RAG) -->
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 shrink-0 min-h-[220px]">
                    <div class="bg-surface-900/80 border border-surface-700/50 rounded-xl overflow-hidden relative p-4 flex flex-col justify-center shadow-xl">
                        <TokenMetricsTracker />
                    </div>
                    
                    <CronosTimeMap class="h-full shadow-xl" />
                    <RagPipelineTracker class="h-full shadow-xl" />
                </div>
                
                <!-- Sovereign Event Stream -->
                <div class="flex-1 min-h-[300px] h-full bg-surface-900/80 border border-surface-700/50 rounded-xl overflow-hidden flex flex-col p-4 custom-scroll shadow-xl">
                    <RealtimeLogs />
                </div>

            </div>
        </div>

        <!-- QUARANTINE (THE SENTINEL) VIEW -->
       <div v-show="activeTab === 'quarantine'" class="absolute inset-0 w-full h-full overflow-y-auto p-6">
           <div class="max-w-5xl mx-auto flex flex-col gap-6 relative">
               <div class="flex items-center justify-between mb-2">
                   <h2 class="text-lg font-medium text-red-400 flex items-center gap-2">
                       <span class="i-ph-shield-warning-duotone text-xl"></span>
                       The Sentinel (Logs de Quarentena)
                   </h2>
                   <button @click="fetchQuarantineLogs" class="text-xs flex items-center gap-1 text-surface-400 hover:text-white transition-colors bg-surface-800 px-3 py-1.5 rounded-md border border-surface-700">
                       <span class="i-ph-arrows-clockwise-duotone"></span> Atualizar
                   </button>
               </div>
               
               <div v-if="isLoadingQuarantine" class="flex flex-col items-center justify-center py-20 text-surface-500">
                  <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" class="animate-spin text-surface-600 mb-4" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
                  Consultando Firewall Ciborque...
               </div>
               
               <div v-else-if="!quarantineLogs || quarantineLogs.length === 0" class="flex-1 flex flex-col items-center justify-center py-16 text-emerald-500/80 border border-dashed border-emerald-900/30 rounded-xl bg-emerald-900/10">
                   <span class="i-ph-shield-check-duotone text-5xl mb-4 text-emerald-500/50"></span>
                   <p class="text-sm font-medium">Bastião Seguro.</p>
                   <p class="text-xs text-emerald-500/60 mt-1">Nenhum documento detectado com Prompt Injection ou scripts maliciosos.</p>
               </div>
               
               <div v-else class="grid grid-cols-1 gap-4 max-h-[600px] overflow-y-auto custom-scroll pr-2">
                   <div v-for="log in quarantineLogs" :key="log.id" class="bg-surface-800/80 border border-red-900/50 rounded-xl p-5 backdrop-blur-sm flex flex-col md:flex-row gap-6 relative overflow-hidden group">
                       <!-- Alert Strip -->
                       <div class="absolute left-0 top-0 bottom-0 w-1 bg-red-500/50"></div>
                       
                       <div class="flex-1 min-w-0">
                           <div class="flex items-start justify-between gap-4 mb-3">
                               <div>
                                   <div class="flex items-center gap-2 mb-1">
                                       <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-red-500/20 text-red-400 border border-red-500/30">
                                           Ameaça Bloqueada
                                       </span>
                                       <span class="text-xs text-surface-500 font-mono">{{ formatTime(log.created_at) }}</span>
                                   </div>
                                   <h3 class="text-base font-medium text-white break-all flex items-center gap-2">
                                       <span class="i-ph-file-pdf-duotone text-red-400 text-lg flex-shrink-0"></span>
                                       {{ log.file_name }}
                                   </h3>
                                   <p class="text-[11px] text-surface-500 font-mono truncate mt-1" :title="log.file_path">{{ log.file_path }}</p>
                               </div>
                           </div>
                           
                           <div class="bg-surface-900/50 rounded border border-surface-700 p-3 mb-4">
                               <p class="text-sm text-red-300 font-medium mb-1 flex items-center gap-1.5">
                                   <span class="i-ph-warning-circle-duotone"></span> Veredito do SLM:
                               </p>
                               <p class="text-xs text-surface-300">{{ log.reason }}</p>
                           </div>
                           
                           <div class="relative">
                               <p class="text-[10px] uppercase tracking-wider text-surface-500 font-bold mb-1 ml-1">Snippet Ofensivo Extraído</p>
                               <pre class="text-[11px] text-surface-400 bg-[#0d0d0d] p-3 rounded-lg border border-surface-800 overflow-x-auto font-mono max-h-32">{{ log.content_snippet }}</pre>
                           </div>
                       </div>
                       
                       <div class="flex flex-row md:flex-col gap-2 justify-center items-center md:items-stretch md:w-48 shrink-0 border-t md:border-t-0 md:border-l border-surface-700/50 pt-4 md:pt-0 md:pl-6">
                           <button @click="deleteQuarantineLog(log.id)" :disabled="actionLoading === log.id" class="flex-1 md:flex-none flex items-center justify-center gap-2 px-4 py-2 bg-red-500/10 hover:bg-red-500/20 text-red-500 hover:text-red-400 border border-red-500/20 rounded-lg text-xs font-semibold transition-all disabled:opacity-50">
                               <span v-if="actionLoading === log.id" class="i-ph-spinner-gap animate-spin"></span>
                               <span v-else class="i-ph-trash-duotone"></span>
                               Destruir Arquivo
                           </button>
                           <button @click="releaseQuarantineLog(log.id)" :disabled="actionLoading === log.id" class="flex-1 md:flex-none flex items-center justify-center gap-2 px-4 py-2 bg-surface-800 hover:bg-surface-700 text-surface-300 hover:text-white border border-surface-600 rounded-lg text-xs font-medium transition-all disabled:opacity-50" title="Bypassar Sentinel e enviar ao RAG">
                               <span v-if="actionLoading === log.id" class="i-ph-spinner-gap animate-spin"></span>
                               <span v-else class="i-ph-check-circle-duotone"></span>
                               Absolver Risco
                           </button>
                       </div>
                   </div>
               </div>
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
import RealtimeLogs from '../components/Dashboard/RealtimeLogs.vue'
import TokenMetricsTracker from '../components/dashboard/TokenMetricsTracker.vue'
import HackerCommandLine from '../components/Dashboard/HackerCommandLine.vue'
import RagPipelineTracker from '../components/Dashboard/RagPipelineTracker.vue'
import CronosTimeMap from '../components/Dashboard/CronosTimeMap.vue'

// O "User Mode" simula a visão B2B (Enterprise) x B2C (Personal)
const router = useRouter()
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const availableTabs = [
    { id: 'cockpit', label: 'Command Hub', icon: 'i-ph-rocket-launch-duotone' },
    { id: 'today', label: 'Hoje', icon: 'i-ph-calendar-star-duotone' },
    { id: 'this_week', label: 'Nesta Semana', icon: 'i-ph-calendar-blank-duotone' },
    { id: 'last_week', label: 'Semana Passada', icon: 'i-ph-clock-counter-clockwise-duotone' },
    { id: 'this_month', label: 'Este Mês', icon: 'i-ph-calendar-duotone' },
    { id: 'this_year', label: 'Panorama Anual', icon: 'i-ph-binoculars-duotone' },
    { id: 'graph', label: 'Grafo Cognitivo', icon: 'i-ph-graph-duotone' },
    { id: 'quarantine', label: 'The Sentinel', icon: 'i-ph-shield-warning-duotone' }
]

const tabLabels: Record<string, string> = {
    'cockpit': 'God Mode',
    'today': 'Foco Diário',
    'this_week': 'Produtividade da Semana',
    'last_week': 'Retrospectiva Semanal',
    'this_month': 'Agregado do Mês',
    'this_year': 'Panorama e Metas Anuais',
    'quarantine': 'Quarentena'
}

const activeTab = ref('cockpit')
const isLoadingAgenda = ref(true)
const graphComponent = ref<any>(null)

// --- COCKPIT LOGIC ---
const isLoadingQuarantine = ref(false)
const actionLoading = ref<number | null>(null)

const fetchQuarantineLogs = async () => {
    isLoadingQuarantine.value = true
    try {
        const token = localStorage.getItem('sovereign_token') || ''
        const headers = { 'Authorization': `Bearer ${token}` }
        const res = await fetch(`${API_BASE_URL}/v1/quarantine`, { headers })
        if (res.ok) {
            quarantineLogs.value = await res.json()
        }
    } catch(e) {
        console.error("Erro ao puxar quarentena:", e)
    } finally {
        isLoadingQuarantine.value = false
    }
}

const deleteQuarantineLog = async (logId: number) => {
    if (!confirm("Isso apagará fisicamente o PDF malicioso do seu disco. Confirma?")) return
    actionLoading.value = logId
    try {
        const token = localStorage.getItem('sovereign_token') || ''
        const headers = { 'Authorization': `Bearer ${token}` }
        const res = await fetch(`${API_BASE_URL}/v1/quarantine/${logId}`, { method: 'DELETE', headers })
        if (res.ok) {
            quarantineLogs.value = quarantineLogs.value.filter(l => l.id !== logId)
        }
    } catch(e) {
        console.error("Erro ao deletar quarentena:", e)
    } finally {
        actionLoading.value = null
    }
}

const releaseQuarantineLog = async (logId: number) => {
    if (!confirm("Aviso: Você está assumindo o risco e bypassando o Guardrail local. O documento irá trafegar (desidratado) para os LLMs através de RAG. Confirma?")) return
    actionLoading.value = logId
    try {
        const token = localStorage.getItem('sovereign_token') || ''
        const headers = { 'Authorization': `Bearer ${token}` }
        const res = await fetch(`${API_BASE_URL}/v1/quarantine/${logId}/release`, { method: 'POST', headers })
        if (res.ok) {
            quarantineLogs.value = quarantineLogs.value.filter(l => l.id !== logId)
            alert("Documento validado. Ele foi injetado na Base Relacional e será vetorizado pelo Guardião (The Dad) silenciosamente.")
        } else {
            const data = await res.json()
            alert(data.detail || "Erro inesperado ao liberar")
        }
    } catch(e) {
        console.error("Erro ao liberar arquio:", e)
    } finally {
        actionLoading.value = null
    }
}

onMounted(() => {
    fetchSystemMode()
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
