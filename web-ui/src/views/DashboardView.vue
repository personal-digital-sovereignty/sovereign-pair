<template>
  <div class="p-8 h-full overflow-y-auto w-full bg-[#111111] text-zinc-100 flex flex-col gap-6">
    <header class="flex flex-col gap-1 pb-4 border-b border-white/5">
      <h1 class="text-3xl font-light tracking-tight text-white flex items-center gap-3">
        <div class="px-2 py-1 bg-white/5 border border-white/10 rounded-md shadow-[inset_0_1px_0_rgba(255,255,255,0.1)]">
            <span class="text-emerald-400">⚡</span>
        </div>
        Sensus Dashboard
      </h1>
      <p class="text-sm text-zinc-500 font-mono tracking-wider ml-1">COGNITIVE HUB & ACTIVITY STREAM</p>
    </header>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      
      <!-- Esquerda: Calendário e Atividades (Col span 2) -->
      <div class="lg:col-span-2 flex flex-col gap-6">
        
        <!-- Bloco de Autonomia / Atividade Recente -->
        <section class="bg-[#151518] border border-white/5 rounded-xl p-5 shadow-2xl backdrop-blur-sm relative overflow-hidden">
            <div class="absolute top-0 right-0 w-64 h-64 bg-emerald-500/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 pointer-events-none"></div>
            <h2 class="text-lg font-medium text-emerald-400 mb-4 flex items-center gap-2">
                <span class="i-ph-clock-counter-clockwise-duotone text-xl"></span>
                Atividades Recentes
            </h2>
            
            <div class="flex flex-col gap-3 relative z-10">
                <div v-if="recentDocs.length === 0" class="flex flex-col items-center justify-center py-10 text-zinc-500 border border-dashed border-white/10 rounded-lg bg-black/20">
                    <span class="i-ph-ghost-duotone text-4xl mb-2 opacity-50"></span>
                    <p class="text-sm">Nenhum documento modificado recentemente.</p>
                </div>
                
                <div v-else class="space-y-2">
                    <div v-for="doc in recentDocs" :key="doc.path" 
                         @click="openInVault(doc)"
                         class="group flex items-center justify-between p-3 rounded-lg bg-white/5 border border-white/5 hover:bg-white/10 hover:border-emerald-500/30 cursor-pointer transition-all">
                        <div class="flex items-center gap-3">
                            <span class="i-ph-file-text-duotone text-zinc-400 group-hover:text-emerald-400 text-lg transition-colors"></span>
                            <div>
                                <h3 class="text-sm font-medium text-zinc-200 group-hover:text-white">{{ doc.name }}</h3>
                                <p class="text-xs text-zinc-500">{{ doc.path }}</p>
                            </div>
                        </div>
                        <span class="text-xs text-zinc-500 font-mono bg-black/30 px-2 py-1 rounded">{{ doc.timeAgo }}</span>
                    </div>
                </div>
            </div>
        </section>

      </div>

      <!-- Direita: Tasks e Insights (Col span 1) -->
      <div class="flex flex-col gap-6">
          
        <!-- Bloco de Tasks -->
        <section class="bg-[#151518] border border-white/5 rounded-xl p-5 shadow-2xl backdrop-blur-sm flex-1 flex flex-col">
          <div class="flex items-center justify-between mb-4">
              <h2 class="text-lg font-medium text-amber-400 flex items-center gap-2">
                  <span class="i-ph-check-circle-duotone text-xl"></span>
                  Pendências (Vault Tasks)
              </h2>
              <span class="bg-amber-500/10 text-amber-500 text-xs px-2 py-0.5 rounded-full border border-amber-500/20">{{ pendingTasks.length }}</span>
          </div>

          <div class="flex-1 overflow-y-auto min-h-[300px] border border-white/5 rounded-lg bg-black/20 p-2">
             <div v-if="pendingTasks.length === 0" class="h-full flex flex-col items-center justify-center text-zinc-500">
                <span class="i-ph-check-fat-duotone text-3xl mb-2 text-emerald-500/50"></span>
                <p class="text-sm text-center">Tudo limpo!<br> O sistema não encontrou marcadores `[ ]` pendentes.</p>
             </div>
             <div v-else class="space-y-1">
                 <div v-for="(task, idx) in pendingTasks" :key="idx" 
                      class="flex items-start gap-2 p-2 rounded hover:bg-white/5 cursor-pointer leading-tight">
                      <input type="checkbox" class="mt-0.5 rounded bg-black/50 border-white/20 text-emerald-500 focus:ring-emerald-500 focus:ring-offset-black accent-emerald-500 cursor-pointer" />
                      <div>
                          <p class="text-sm text-zinc-300">{{ task.text }}</p>
                          <p class="text-[10px] text-zinc-500 font-mono mt-1 hover:text-amber-400" @click="openInVault({ path: task.file })">{{ task.file }}</p>
                      </div>
                 </div>
             </div>
          </div>
        </section>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

interface RecentDoc {
    name: string
    path: string
    timeAgo: string
}

interface VaultTask {
    text: string
    file: string
}

const recentDocs = ref<RecentDoc[]>([])
const pendingTasks = ref<VaultTask[]>([])

const fetchDashboardData = async () => {
    try {
        const token = localStorage.getItem('sovereign_token') || ''
        const headers = { 'Authorization': `Bearer ${token}` }
        
        const [recentRes, tasksRes] = await Promise.all([
            fetch(`${API_BASE_URL}/v1/vault/recent`, { headers }),
            fetch(`${API_BASE_URL}/v1/vault/tasks`, { headers })
        ])
        
        if (recentRes.ok) {
            const data = await recentRes.json()
            recentDocs.value = data.map((d: any) => ({
                name: d.name,
                path: d.path,
                timeAgo: new Date(d.updated_at).toLocaleDateString('pt-BR', {day: '2-digit', month: 'short'}) + ' ' + new Date(d.updated_at).toLocaleTimeString('pt-BR', {hour: '2-digit', minute:'2-digit'})
            }))
        }
        
        if (tasksRes.ok) {
            pendingTasks.value = await tasksRes.json()
        }
    } catch(e) {
        console.error("Erro ao puxar dados do Dashboard:", e)
    }
}

const openInVault = (doc: any) => {
    // Redireciona para o Vault e manda abrir o arquivo (Pode exigir query param ou state store)
    router.push({ path: '/vault', query: { file: doc.path } })
}

onMounted(() => {
    fetchDashboardData()
})
</script>
