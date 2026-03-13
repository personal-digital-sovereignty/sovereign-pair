<template>
  <div class="h-full flex flex-col bg-surface-50 dark:bg-surface-900 border border-surface-200 dark:border-surface-700/50 rounded-xl overflow-hidden font-mono text-xs">
    <div class="flex items-center justify-between px-3 py-2 bg-surface-100/80 dark:bg-surface-800/80 border-b border-surface-200 dark:border-surface-700/50">
      <div class="flex items-center gap-2">
        <span class="w-2 h-2 rounded-full" :class="isConnecting ? 'bg-amber-400 animate-pulse' : 'bg-emerald-400'"></span>
        <span class="font-semibold text-surface-900 dark:text-surface-200 uppercase tracking-widest">Sovereign Event Stream</span>
      </div>
      <button @click="clearLogs" class="text-surface-500 hover:text-surface-900 dark:hover:text-white transition-colors" title="Limpar Logs">
        <span class="i-ph-trash"></span>
      </button>
    </div>
    <div class="flex-1 overflow-y-auto p-2 flex flex-col gap-0.5 custom-scroll" ref="logsContainer">
      <div v-if="logs.length === 0" class="text-surface-600 italic text-center py-4">
        Aguardando eventos do Synesis Core...
      </div>
      <div v-for="(log, idx) in logs" :key="idx" class="flex items-start gap-1.5 hover:bg-surface-200/50 dark:hover:bg-surface-800/30 px-1 py-0.5 rounded transition-colors text-[10px] leading-tight overflow-hidden">
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

// Conectando ao Verdadeiro Core Cíbrido (Rust Node)
let eventSource: EventSource | null = null

const connectToSSE = () => {
    // Endereço físico do Sovereign Core
    eventSource = new EventSource('http://127.0.0.1:8001/v1/logs')
    
    eventSource.onopen = () => {
        isConnecting.value = false
        addLog('info', 'Link Asíncrono Live estabelecido com The Sentinel (Core Rust).')
    }

    eventSource.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data)
            // Usa o timestamp nativo do Browser se o Rust não mandar a crônica cravada
            const level = data.level ? data.level.toLowerCase() : 'info'
            addLog(level as any, data.message)
        } catch (e) {
            console.error("The Nurse perdeu um pacote: ", e)
        }
    }

    eventSource.onerror = () => {
        if (!isConnecting.value) {
            addLog('warn', 'Sovereign Core Inacessível. Varredura cíbrida comprometida. Tentando reconexão O.S...')
            isConnecting.value = true
        }
    }
}

onMounted(() => {
    // Iniciando Handshake VUE-RUST
    connectToSSE()
})

onUnmounted(() => {
  if (eventSource) {
      eventSource.close()
  }
})
</script>

<style scoped>
.custom-scroll::-webkit-scrollbar { width: 4px; }
.custom-scroll::-webkit-scrollbar-track { background: transparent; }
.custom-scroll::-webkit-scrollbar-thumb { background-color: rgba(255,255,255,0.1); border-radius: 4px; }
</style>
