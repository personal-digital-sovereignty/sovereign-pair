<template>
  <div class="w-full bg-surface-50 dark:bg-surface-900/80 border border-surface-200 dark:border-surface-700/50 rounded-xl overflow-hidden flex flex-col min-h-0">
    <!-- Header O.S -->
    <div class="px-3 py-2 border-b border-surface-200 dark:border-surface-700/50 bg-surface-100 dark:bg-[#0a0a0a] flex items-center justify-between">
      <h3 class="text-[11px] font-mono tracking-widest text-surface-400 uppercase flex items-center gap-2">
        <span class="i-ph-brain-duotone text-emerald-500 text-sm"></span> 
        RAG Ingestion Queue
      </h3>
      <span v-if="activeJobs > 0" class="flex h-2 w-2">
        <span class="animate-ping absolute inline-flex h-2 w-2 rounded-full bg-emerald-400 opacity-75"></span>
        <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
      </span>
      <span v-else class="text-[9px] text-surface-600 font-mono tracking-widest uppercase">IDLE</span>
    </div>

    <!-- Job List Container -->
    <div class="flex-1 overflow-y-auto custom-scroll p-3 flex flex-col gap-3 min-h-[140px]">
      <div v-if="jobs.length === 0" class="flex-1 flex flex-col items-center justify-center text-surface-600 border border-dashed border-surface-800 rounded-lg">
         <span class="i-ph-file-zip-duotone text-2xl mb-1 opacity-50"></span>
         <p class="text-[9px] font-mono uppercase tracking-widest">Aguardando Blobs</p>
      </div>

      <!-- Item Tracker -->
      <div v-for="job in jobs" :key="job.id" class="flex flex-col gap-2 p-2.5 rounded-lg border border-surface-200 dark:border-surface-800 bg-surface-100 dark:bg-[#0d0d0d] transition-colors relative overflow-hidden group">
        <!-- Barra Lateral Dinamica -->
        <div class="absolute left-0 top-0 bottom-0 w-[2px]" :class="getStatusColor(job.status)"></div>

        <!-- Info Header -->
        <div class="flex items-center justify-between pl-2">
           <div class="flex items-center gap-2 truncate">
               <span class="i-ph-file-pdf-duotone text-red-400 text-xs shrink-0" v-if="job.filename.endsWith('.pdf')"></span>
               <span class="i-ph-file-code-duotone text-primary-400 text-xs shrink-0" v-else-if="job.filename.endsWith('.md') || job.filename.endsWith('.txt')"></span>
               <span class="i-ph-file-duotone text-surface-400 text-xs shrink-0" v-else></span>
               <p class="text-[10px] text-surface-300 font-medium truncate" :title="job.filename">{{ job.filename }}</p>
           </div>
           <span class="text-[9px] font-mono tracking-widest shrink-0 uppercase" :class="getTextStatusColor(job.status)">
               {{ getProgressPercent(job.currentStep) }}%
           </span>
        </div>

        <!-- Steps Progress Tracker (Brutalista) -->
        <div class="flex items-center pl-2 gap-1 mt-1">
          <div v-for="(step, idx) in stepsDef" :key="idx" class="flex-1 flex flex-col gap-1 relative group/step cursor-help" :title="step.label">
             <div class="h-1 rounded-sm overflow-hidden bg-surface-800">
                <div class="h-full transition-all duration-500" 
                     :class="getStepBgColor(job.currentStep, idx)"
                     :style="{ width: getStepFill(job.currentStep, idx) }">
                </div>
             </div>
             <!-- Minúscula indicação Ocular ao passar o mouse -->
             <span class="absolute -bottom-4 text-[7px] font-mono uppercase tracking-widest whitespace-nowrap opacity-0 group-hover/step:opacity-100 transition-opacity z-10" :class="getTextStatusColor(job.status)">
                 {{ step.label }}
             </span>
          </div>
        </div>
        
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

const stepsDef = [
    { label: 'O.C.R / Parse', weight: 20 },
    { label: 'Doc Chunking', weight: 30 },
    { label: 'Embedding Vector', weight: 40 },
    { label: 'SQLite Store', weight: 10 }
]

type JobStatus = 'queued' | 'processing' | 'completed' | 'failed'

interface IngestionJob {
    id: string
    filename: string
    status: JobStatus
    currentStep: number // 0 a 3 (índice em stepsDef) ou 4 (Completo)
    progress_ms: number // simulador interno
}

const jobs = ref<IngestionJob[]>([])

const activeJobs = computed(() => jobs.value.filter(j => j.status === 'processing').length)

const getStatusColor = (status: JobStatus) => {
    switch(status) {
        case 'processing': return 'bg-amber-500'
        case 'completed': return 'bg-emerald-500'
        case 'failed': return 'bg-red-500'
        default: return 'bg-surface-700'
    }
}

const getTextStatusColor = (status: JobStatus) => {
    switch(status) {
        case 'processing': return 'text-amber-400'
        case 'completed': return 'text-emerald-500'
        case 'failed': return 'text-red-400'
        default: return 'text-surface-500'
    }
}

const getProgressPercent = (currentStep: number) => {
    if (currentStep >= 4) return 100
    let fill = 0
    for(let i = 0; i < currentStep; i++) {
        if (stepsDef[i]) fill += stepsDef[i]?.weight || 0
    }
    // Adiciona uma casqinha "processando" ao passo atual 
    if (currentStep < 4 && stepsDef[currentStep]) {
        fill += Math.floor(stepsDef[currentStep].weight / 2)
    }
    return fill
}

const getStepFill = (currentStep: number, boxIndex: number) => {
    if (currentStep > boxIndex) return '100%'
    if (currentStep === boxIndex) return '50%' // Simula animação contínua internamente
    return '0%'
}

const getStepBgColor = (currentStep: number, boxIndex: number) => {
    if (currentStep > boxIndex) return 'bg-emerald-500'
    if (currentStep === boxIndex) return 'bg-amber-400 animate-pulse'
    return 'bg-transparent'
}

// ==========================================
// RAG VAULT SYNC ENGINE: SSE NATIVE OBSERVER
// ==========================================
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || `http://${typeof window !== 'undefined' ? window.location.hostname : 'localhost'}:8001`
let eventSource: EventSource | null = null

const startSseConnection = () => {
    eventSource = new EventSource(`${API_BASE_URL}/v1/vault/sync/status`)

    eventSource.onopen = () => {
        // Tracker conectado à Máquina Física
    }

    eventSource.onmessage = (event) => {
        try {
            const data: IngestionJob = JSON.parse(event.data)
            const existingJobIndex = jobs.value.findIndex(j => j.id === data.id)
            
            if (existingJobIndex >= 0) {
                // Atualiza progresso da barra em tempo-real (Processamento In Loco)
                jobs.value[existingJobIndex] = { ...jobs.value[existingJobIndex], ...data }
            } else {
                // Push no novo trabalho de Indexação
                jobs.value.unshift(data)
                
                // Manter UI fluída c/ Garbage Collector de Jobs Ativos (Histórico)
                if (jobs.value.length > 5) jobs.value.pop()
            }
        } catch (err) {
            console.error("Masterplan Rag Tracker falhou no Sync Decode", err)
        }
    }

    eventSource.onerror = () => {
        // Reconexão Invisivel
    }
}

onMounted(() => {
    startSseConnection()
})

onUnmounted(() => {
    if (eventSource) eventSource.close()
})
</script>
