<template>
  <div class="h-full overflow-hidden w-full bg-surface-900 text-surface-200 flex flex-col">
    <!-- Header Controls -->
    <header class="flex-shrink-0 flex items-center justify-between px-6 py-4 border-b border-surface-700 bg-surface-800/80 backdrop-blur z-10">
      <div>
        <h1 class="text-2xl font-light tracking-tight flex items-center gap-3 text-white">
          Sovereign Masterplan (God Mode)
        </h1>
        <p class="text-[11px] text-surface-400 font-mono tracking-widest mt-1 uppercase flex items-center gap-2">
           Terminal Cíbrido Integrado & Observabilidade de LLMs
        </p>
      </div>
    </header>

    <!-- Main Content Area: Widescreen LLMOps Nexus -->
    <main class="flex-1 overflow-hidden relative">
        <div class="absolute inset-0 w-full h-full overflow-y-auto p-6 bg-surface-900/90 custom-scroll">
            <div class="w-full flex flex-col gap-6 relative min-h-[calc(100vh-140px)]">
                
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
    </main>
  </div>
</template>

<script setup lang="ts">
import RealtimeLogs from '../components/Dashboard/RealtimeLogs.vue'
import TokenMetricsTracker from '../components/dashboard/TokenMetricsTracker.vue'
import HackerCommandLine from '../components/Dashboard/HackerCommandLine.vue'
import RagPipelineTracker from '../components/Dashboard/RagPipelineTracker.vue'
import CronosTimeMap from '../components/Dashboard/CronosTimeMap.vue'
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
