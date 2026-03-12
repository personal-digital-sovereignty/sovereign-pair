<template>
  <section class="bg-surface-900/80 border border-amber-500/20 rounded-xl p-5 shadow-xl relative overflow-hidden flex flex-col h-full group">
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
        <div class="bg-[#0a0a0a] border border-surface-800 rounded-lg p-3 flex items-center justify-between hover:border-red-500/30 transition-colors cursor-pointer" title="Ver Arquivos em Quarentena">
            <div>
                <p class="text-[10px] text-surface-500 uppercase tracking-wider mb-1">Knowledge Gaps (RAG)</p>
                <div class="flex items-end gap-2">
                    <span class="text-2xl font-light text-red-400 leading-none">{{ gapsCount }}</span>
                    <span class="text-[10px] pb-1 text-surface-400">Arquivos Bloqueados</span>
                </div>
            </div>
            <span class="i-ph-shield-warning-duotone text-3xl text-red-500/20"></span>
        </div>

        <!-- Kanban Tasks For Today -->
        <div class="bg-[#0a0a0a] border border-surface-800 rounded-lg p-3 flex flex-col hover:border-emerald-500/30 transition-colors cursor-pointer" title="Abrir Kanban de Hoje">
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
import { ref, onMounted } from 'vue'

const gapsCount = ref(1) // Mock de Knowledge Gap / Quarantine
const tasksToday = ref(3) // Mock Extraído do Kanban
const progress = ref(33) // Mock: 1 de 3 completado

onMounted(() => {
    // Simular oscilações ativas no Hub Cibernético
    setTimeout(() => {
        gapsCount.value = 2 // Novo arquivo caiu na quarentena
    }, 45000)
})
</script>
