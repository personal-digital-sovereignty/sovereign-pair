<template>
  <div class="h-full overflow-hidden w-full bg-surface-50 dark:bg-surface-900 text-surface-900 dark:text-surface-200 flex flex-col">
    <header class="flex-shrink-0 flex items-center justify-between px-6 py-4 border-b border-surface-200 dark:border-surface-700 bg-surface-100/80 dark:bg-surface-800/80 backdrop-blur z-10">
      <div>
        <h1 class="text-2xl font-light tracking-tight flex items-center gap-3 text-surface-900 dark:text-white">
          Sovereign Masterplan (God Mode)
        </h1>
        <p class="text-[11px] text-surface-400 font-mono tracking-widest mt-1 uppercase flex items-center gap-2">
           Terminal Cíbrido Integrado & Observabilidade de LLMs
        </p>
      </div>
      
      <Teleport to="#sidebar-context-area" v-if="isMounted">
        <div class="p-3 w-full h-full flex flex-col gap-2 mt-4">
          <div class="px-2 py-1.5 rounded-lg cursor-pointer transition-all flex items-center gap-2"
               @click="activeTab = 'overview'"
               :class="activeTab === 'overview' ? 'bg-surface-200 dark:bg-[#1C1C1E] border border-black/10 dark:border-white/10 shadow-[inset_3px_0_0_0_#10b981] text-surface-900 dark:text-white' : 'text-zinc-500 hover:text-surface-900 dark:hover:text-white transition-colors'">
            <i class="i-lucide-layout-dashboard text-sm"></i>
            <span class="text-sm font-medium">Overview</span>
          </div>
          <div class="px-2 py-1.5 rounded-lg cursor-pointer transition-all flex items-center gap-2"
               @click="activeTab = 'graph'"
               :class="activeTab === 'graph' ? 'bg-surface-200 dark:bg-[#1C1C1E] border border-black/10 dark:border-white/10 shadow-[inset_3px_0_0_0_#10b981] text-surface-900 dark:text-white' : 'text-zinc-500 hover:text-surface-900 dark:hover:text-white transition-colors'">
            <i class="i-lucide-network text-sm"></i>
            <span class="text-sm font-medium">Cognitive Graph</span>
          </div>
          <div class="px-2 py-1.5 rounded-lg cursor-pointer transition-all flex items-center gap-2 mt-4"
               @click="activeTab = 'blue-collar'"
               :class="activeTab === 'blue-collar' ? 'bg-surface-200 dark:bg-[#1C1C1E] border border-black/10 dark:border-white/10 shadow-[inset_3px_0_0_0_#f97316] text-surface-900 dark:text-white' : 'text-zinc-500 hover:text-orange-500/80 transition-colors'">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"></path></svg>
            <span class="text-sm font-medium">Blue Collar OCI</span>
          </div>
        </div>
      </Teleport>
    </header>

    <!-- Main Content Area: Widescreen LLMOps Nexus -->
    <main class="flex-1 overflow-hidden relative">
        <div class="absolute inset-0 w-full h-full overflow-y-auto p-6 bg-surface-50/90 dark:bg-surface-900/90 custom-scroll">
            <template v-if="activeTab === 'overview'">
              <div class="w-full flex flex-col gap-6 relative min-h-[calc(100vh-140px)]">
                  
                  <!-- O.S Terminal Integrado (The Hacker's CLI) -->
                  <HackerCommandLine class="shrink-0 z-20" />
                  
                  <!-- Tri-Core Trackers (Telemetria, Cronos, RAG) -->
                  <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 shrink-0 min-h-[220px]">
                      <div class="bg-surface-100/80 dark:bg-surface-900/80 border border-surface-200 dark:border-surface-700/50 rounded-xl overflow-hidden relative p-4 flex flex-col justify-center shadow-xl">
                          <TokenMetricsTracker />
                      </div>
                      <CronosTimeMap class="h-full shadow-xl" />
                      <RagPipelineTracker class="h-full shadow-xl" />
                  </div>
                  
                  <!-- Sovereign Event Stream -->
                  <div class="flex-1 min-h-[300px] h-full bg-surface-100/80 dark:bg-surface-900/80 border border-surface-200 dark:border-surface-700/50 rounded-xl overflow-hidden flex flex-col p-4 custom-scroll shadow-xl">
                      <RealtimeLogs />
                  </div>
              </div>
            </template>
            <template v-else-if="activeTab === 'graph'">
              <div class="w-full h-[calc(100vh-140px)] bg-surface-100/80 dark:bg-surface-900/80 border border-surface-200 dark:border-surface-700/50 rounded-xl overflow-hidden shadow-xl">
                 <CognitiveGraph />
              </div>
            </template>
            <template v-else-if="activeTab === 'blue-collar'">
              <div class="w-full h-[calc(100vh-140px)] bg-surface-100/80 dark:bg-surface-900/80 border border-surface-200 dark:border-surface-700/50 rounded-xl overflow-hidden shadow-xl">
                 <BlueCollarManager />
              </div>
            </template>
        </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import RealtimeLogs from '../components/Dashboard/RealtimeLogs.vue'
import TokenMetricsTracker from '../components/Dashboard/TokenMetricsTracker.vue'
import HackerCommandLine from '../components/Dashboard/HackerCommandLine.vue'
import RagPipelineTracker from '../components/Dashboard/RagPipelineTracker.vue'
import CronosTimeMap from '../components/Dashboard/CronosTimeMap.vue'
import CognitiveGraph from '../components/Vault/CognitiveGraph.vue'
import BlueCollarManager from '../components/Dashboard/BlueCollarManager.vue'

const isMounted = ref(false)
const activeTab = ref('overview')

onMounted(() => {
  isMounted.value = true
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
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}
.custom-scroll::-webkit-scrollbar-thumb:hover {
  background-color: rgba(255, 255, 255, 0.2);
}
</style>
