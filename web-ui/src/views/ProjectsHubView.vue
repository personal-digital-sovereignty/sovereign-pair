<template>
  <div class="p-8 h-full w-full bg-[#111111] text-zinc-100 flex flex-col gap-6 overflow-hidden">
    <header class="flex flex-col gap-1 pb-4 border-b border-white/5 flex-shrink-0">
      <h1 class="text-3xl font-light tracking-tight text-white flex items-center gap-3">
        <div class="px-2 py-1 bg-white/5 border border-white/10 rounded-md shadow-[inset_0_1px_0_rgba(255,255,255,0.1)]">
            <span class="text-cyan-400">⚡</span>
        </div>
        Sovereign "Plan & Execute" Hub
      </h1>
      <p class="text-sm text-zinc-500 font-mono tracking-wider ml-1">ORQUESTRAÇÃO DESACOPLADA DE CONHECIMENTO & EXECUÇÃO</p>
    </header>

    <div class="flex-1 min-h-0 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 overflow-hidden">
      
      <!-- 1. PROJETOS (High Level Plans) -->
      <section class="bg-[#151518] border border-white/5 rounded-xl p-4 flex flex-col overflow-hidden">
          <div class="flex items-center justify-between mb-4 shrink-0">
              <h2 class="text-base font-medium text-purple-400 flex items-center gap-2">
                  <span class="i-ph-folders-duotone text-lg"></span> Projetos (The Plan)
              </h2>
              <button class="bg-white/5 hover:bg-white/10 px-2 py-1 rounded border border-white/10 text-xs text-white">+</button>
          </div>
          <div class="flex-1 overflow-y-auto custom-scroll pr-2 space-y-3">
              <div v-for="i in 3" :key="'p'+i" class="p-3 bg-white/5 border border-white/5 rounded-lg hover:border-purple-500/30 cursor-pointer transition-all">
                  <h3 class="font-medium text-sm text-zinc-200">Migração Infraestrutura Oracle</h3>
                  <div class="flex items-center gap-2 mt-2">
                      <div class="flex-1 bg-black rounded-full h-1.5"><div class="bg-purple-500 h-1.5 rounded-full w-[60%]"></div></div>
                      <span class="text-[10px] text-zinc-500 font-mono">60%</span>
                  </div>
              </div>
          </div>
      </section>

      <!-- 2. TASK LISTS (Execution Steps) -->
      <section class="bg-[#151518] border border-white/5 rounded-xl p-4 flex flex-col overflow-hidden">
          <div class="flex items-center justify-between mb-4 shrink-0">
              <h2 class="text-base font-medium text-amber-500 flex items-center gap-2">
                  <span class="i-ph-check-square-offset-duotone text-lg"></span> Tarefas (The Execute)
              </h2>
              <button class="bg-white/5 hover:bg-white/10 px-2 py-1 rounded border border-white/10 text-xs text-white">+</button>
          </div>
          <div class="flex-1 overflow-y-auto custom-scroll pr-2 space-y-2">
              <div v-for="i in 5" :key="'t'+i" class="p-2.5 bg-black/40 border border-white/5 rounded-lg flex items-start gap-3 hover:bg-surface-800 transition-colors group">
                  <input type="checkbox" class="mt-0.5 rounded bg-surface-900 border-surface-600 text-amber-500 focus:ring-amber-500 cursor-pointer" />
                  <div>
                      <p class="text-sm text-zinc-300 leading-snug">Configurar regras de firewall no Tailscale root node</p>
                      <span class="text-[10px] text-zinc-500 font-mono uppercase bg-white/5 px-1 py-0.5 rounded mt-1 inline-block border border-white/5">Task List</span>
                  </div>
              </div>
          </div>
      </section>

      <!-- 3. NOTES (Knowledge Base / Specs) -->
      <section class="bg-[#151518] border border-white/5 rounded-xl p-4 flex flex-col overflow-hidden">
          <div class="flex items-center justify-between mb-4 shrink-0">
              <h2 class="text-base font-medium text-cyan-400 flex items-center gap-2">
                  <span class="i-ph-file-text-duotone text-lg"></span> Notas & Specs
              </h2>
              <button class="bg-white/5 hover:bg-white/10 px-2 py-1 rounded border border-white/10 text-xs text-white">+</button>
          </div>
          <div class="flex-1 overflow-y-auto custom-scroll pr-2 space-y-3">
              <div class="grid grid-cols-1 gap-2">
                  <div v-for="tag in tags" :key="tag.name" class="p-3 bg-cyan-900/10 border border-cyan-500/20 rounded-lg hover:bg-cyan-900/20 cursor-pointer flex items-center justify-between transition-colors">
                      <span class="text-sm font-medium text-zinc-300">#{{ tag.name }}</span>
                      <span class="text-[10px] bg-cyan-500/20 text-cyan-400 px-2 py-0.5 rounded-full">{{ tag.count }} docs</span>
                  </div>
              </div>
          </div>
      </section>

      <!-- 4. FILES (Raw Contexts) -->
      <section class="bg-[#151518] border border-white/5 rounded-xl p-4 flex flex-col overflow-hidden">
          <div class="flex items-center justify-between mb-4 shrink-0">
              <h2 class="text-base font-medium text-emerald-400 flex items-center gap-2">
                  <span class="i-ph-files-duotone text-lg"></span> Arquivos Físicos
              </h2>
              <button class="bg-white/5 hover:bg-white/10 px-2 py-1 rounded border border-white/10 text-xs text-white">+</button>
          </div>
          <div class="flex-1 overflow-y-auto custom-scroll pr-2 space-y-2">
              <div v-for="i in 4" :key="'f'+i" class="p-2.5 bg-black/30 border border-white/5 rounded-lg flex items-center gap-3 cursor-pointer hover:bg-white/5 transition-colors">
                  <div class="p-1.5 bg-red-500/10 text-red-500 rounded"><span class="i-ph-file-pdf-duotone text-lg"></span></div>
                  <div class="min-w-0">
                      <p class="text-sm text-zinc-300 truncate font-medium">AWS_Architecture_Diagram.pdf</p>
                      <p class="text-[10px] text-zinc-500 font-mono pt-0.5">2.4 MB • Raw Doc</p>
                  </div>
              </div>
          </div>
      </section>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'

interface TagInfo {
  name: string
  count: number
}

const tags = ref<TagInfo[]>([])

const fetchHubData = async () => {
  const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  const token = localStorage.getItem('sovereign_token')
  const headers = token ? { Authorization: `Bearer ${token}` } : {}
  
  try {
    const tagsRes = await axios.get(`${baseURL}/v1/vault/tags`, { headers })
    tags.value = tagsRes.data.tags || []
  } catch (error) {
    console.warn("Failed to fetch tags. Populating with mock data for UI visual.")
    tags.value = [
      { name: 'architecture', count: 12 },
      { name: 'research', count: 4 },
      { name: 'meeting-notes', count: 8 }
    ]
  }
}

onMounted(() => {
  fetchHubData()
})
</script>

<style scoped>
.custom-scroll::-webkit-scrollbar { width: 4px; }
.custom-scroll::-webkit-scrollbar-track { background: transparent; }
.custom-scroll::-webkit-scrollbar-thumb { background-color: rgba(255,255,255,0.1); border-radius: 4px; }
.custom-scroll:hover::-webkit-scrollbar-thumb { background-color: rgba(255,255,255,0.2); }
</style>
