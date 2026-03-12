<template>
  <div class="h-full flex flex-col bg-[#0f0f12] border border-surface-700/50 rounded-xl overflow-hidden font-mono text-xs">
    <div class="flex items-center justify-between px-3 py-2 bg-surface-800/80 border-b border-surface-700/50">
      <div class="flex items-center gap-2">
        <span class="w-2 h-2 rounded-full" :class="isConnecting ? 'bg-amber-400 animate-pulse' : 'bg-emerald-400'"></span>
        <span class="font-semibold text-surface-200 uppercase tracking-widest">Sovereign Event Stream</span>
      </div>
      <button @click="clearLogs" class="text-surface-500 hover:text-white transition-colors" title="Limpar Logs">
        <span class="i-ph-trash"></span>
      </button>
    </div>
    <div class="flex-1 overflow-y-auto p-2 flex flex-col gap-0.5 custom-scroll" ref="logsContainer">
      <div v-if="logs.length === 0" class="text-surface-600 italic text-center py-4">
        Aguardando eventos do Synesis Core...
      </div>
      <div v-for="(log, idx) in logs" :key="idx" class="flex items-start gap-1.5 hover:bg-surface-800/30 px-1 py-0.5 rounded transition-colors text-[10px] leading-tight overflow-hidden">
        <span class="text-surface-500 shrink-0 select-none">[{{ formatTime(log.timestamp) }}]</span>
        <span :class="getLogColor(log.level)" class="shrink-0 uppercase font-bold w-10 select-none">{{ log.level }}</span>
        <span class="text-surface-300 flex-1 truncate" :title="log.message">{{ log.message }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'

interface LogEntry {
  timestamp: Date
  level: 'info' | 'warn' | 'error' | 'agent' | 'rag'
  message: string
}

const logs = ref<LogEntry[]>([])
const isConnecting = ref(true)
const logsContainer = ref<HTMLElement | null>(null)
let mockInterval: any = null

const formatTime = (d: Date) => {
  return d.toLocaleTimeString('pt-BR', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

const getLogColor = (level: string) => {
  switch(level) {
    case 'info': return 'text-blue-400'
    case 'warn': return 'text-amber-400'
    case 'error': return 'text-red-400'
    case 'agent': return 'text-purple-400'
    case 'rag': return 'text-emerald-400'
    default: return 'text-surface-400'
  }
}

const addLog = (level: LogEntry['level'], message: string) => {
  logs.value.push({ timestamp: new Date(), level, message })
  if (logs.value.length > 200) logs.value.shift()
  
  nextTick(() => {
    if (logsContainer.value) {
      logsContainer.value.scrollTop = logsContainer.value.scrollHeight
    }
  })
}

const clearLogs = () => {
  logs.value = []
}

// TODO: Connect to actual /v1/logs SSE endpoint
// For now we simulate background activity to show the concept
onMounted(() => {
  setTimeout(() => {
    isConnecting.value = false
    addLog('info', 'Conexão segura restabelecida com Sovereign Core.')
    addLog('info', 'Guardrails do The Sentinel: ACTIVE.')
  }, 1000)

  // Simulation of background tasks
  mockInterval = setInterval(() => {
    const events = [
      { level: 'rag', msg: 'The Dad (Oracle) roteando RAG query para Vector DB...' },
      { level: 'agent', msg: 'The Coder detectou modificações na pasta src/' },
      { level: 'info', msg: 'Sincronização assíncrona efetuada com sucesso.' },
      { level: 'rag', msg: 'Hyrbid Search retornou 3 contextos relevantes.' },
      { level: 'warn', msg: 'Pico de temperatura detectado na nuvem Cibrid.' }
    ]
    if (Math.random() > 0.7) {
      const ev = events[Math.floor(Math.random() * events.length)]
      if (ev) addLog(ev.level as any, ev.msg)
    }
  }, 4500)
})

onUnmounted(() => {
  if (mockInterval) clearInterval(mockInterval)
})
</script>

<style scoped>
.custom-scroll::-webkit-scrollbar { width: 4px; }
.custom-scroll::-webkit-scrollbar-track { background: transparent; }
.custom-scroll::-webkit-scrollbar-thumb { background-color: rgba(255,255,255,0.1); border-radius: 4px; }
</style>
