<template>
  <section class="bg-surface-800 border-surface-700 border rounded-xl p-5 shadow-[0_4px_20px_rgba(0,0,0,0.15)] relative overflow-hidden flex flex-col h-full group">
    <!-- Decorative accent -->
    <div class="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-amber-500 to-orange-600 opacity-80 group-hover:opacity-100 transition-opacity"></div>
    
    <div class="flex items-center justify-between mb-4 pl-2">
        <h2 class="text-sm font-medium text-amber-500 flex items-center gap-2">
            <span class="i-ph-hourglass-high-duotone text-lg animate-pulse"></span> 
            Cronos Time-Map
        </h2>
        <p class="text-[9px] text-surface-400 font-mono tracking-widest uppercase">System Deadlines</p>
    </div>
    
    <div class="flex-1 flex flex-col gap-4 pl-2 font-mono">
        <!-- RAG Gaps / Quarantine -->
        <div class="bg-surface-900 border border-surface-700 rounded-lg p-3 flex flex-col hover:border-red-500/30 transition-colors cursor-pointer" title="Ver Arquivos em Quarentena">
            <div class="flex items-center justify-between">
                <div>
                    <p class="text-[10px] text-surface-500 uppercase tracking-wider mb-1">Knowledge Gaps (RAG)</p>
                    <div class="flex items-end gap-2">
                        <span class="text-2xl font-light text-red-400 leading-none">{{ gapsCount }}</span>
                        <span class="text-[10px] pb-1 text-surface-400">Arquivos Bloqueados</span>
                    </div>
                </div>
                <span class="i-ph-shield-warning-duotone text-3xl text-red-500/20"></span>
            </div>
            
            <!-- Lista real de arquivos Quarentenados / Bloqueados -->
            <div v-if="gapsList.length > 0" class="mt-3 flex flex-col gap-2 border-t border-surface-800 pt-3">
                <div v-for="gap in gapsList" :key="gap.id" class="flex flex-col gap-1 w-full bg-surface-950/50 p-2 border border-surface-800/60 rounded">
                   <div class="flex items-center gap-1.5 pb-1 border-b border-surface-800 overflow-hidden">
                       <span class="w-2 h-2 rounded-full bg-red-500/50 shrink-0"></span>
                       <span class="text-[10px] text-red-400/80 font-mono truncate" :title="gap.file_path">{{ gap.file_path.split('/').pop() }}</span>
                   </div>
                   <span class="text-[9px] text-surface-400 leading-tight mt-1" :title="gap.reason">{{ gap.reason }}</span>
                </div>
            </div>
        </div>

        <!-- Kanban Tasks For Today -->
        <div class="bg-surface-900 border border-surface-700 rounded-lg p-3 flex flex-col hover:border-emerald-500/30 transition-colors cursor-pointer" title="Abrir Kanban de Hoje">
            <div class="flex items-center justify-between mb-2">
                <p class="text-[10px] text-surface-500 uppercase tracking-wider">Missões de Hoje</p>
                <span class="text-[10px] px-1.5 py-0.5 rounded uppercase font-bold tracking-widest bg-emerald-500/10 text-emerald-500">
                    {{ tasksToday }} TASKS
                </span>
            </div>
            <div class="h-1.5 w-full bg-surface-800 rounded-full overflow-hidden">
                <div class="h-full bg-emerald-500 transition-all" :style="{ width: progress + '%' }"></div>
            </div>
            <p class="text-[9px] text-surface-500 mt-2 tracking-widest text-right">{{ progress }}% completado</p>
        </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const gapsCount = ref(0)
const gapsList = ref<Array<any>>([])
const tasksToday = ref(0) 
const progress = ref(0)

const handleCronosUpdate = (event: Event) => {
    const detail = (event as CustomEvent).detail
    if (detail) {
        gapsCount.value = detail.gaps || 0
        gapsList.value = detail.gaps_list || []
        tasksToday.value = detail.tasks_today || 0
        progress.value = detail.progress || 0
    }
}

onMounted(() => {
    window.addEventListener('cronos-telemetry-update', handleCronosUpdate)
})

onUnmounted(() => {
    window.removeEventListener('cronos-telemetry-update', handleCronosUpdate)
})
</script>
