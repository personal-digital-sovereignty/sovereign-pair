<template>
  <div class="w-full bg-[#050505] border border-surface-700/50 rounded-xl overflow-hidden shadow-[0_0_20px_rgba(0,0,0,0.5)] relative group">
    <!-- Efeito Glitch/Glow Superior -->
    <div class="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-emerald-500/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-1000"></div>
    
    <div class="flex items-center p-3 relative z-10">
      <!-- Decorator Bracket -->
      <div class="flex items-center justify-center shrink-0 w-8 text-emerald-500/80 font-mono text-lg font-bold">
        >
      </div>
      
      <!-- O Prompt Input Mestre -->
      <input 
        ref="cmdInput"
        v-model="commandText"
        @keyup.enter="dispatchCommand"
        type="text" 
        class="flex-1 bg-transparent border-none text-emerald-400 font-mono tracking-wider focus:ring-0 placeholder-surface-600/50 text-sm py-1"
        placeholder="_ execute sub-rotinas / flush / wakeup..."
        autocomplete="off"
        spellcheck="false"
      />
      
      <!-- Right Status Flag -->
      <div v-if="isProcessing" class="shrink-0 flex items-center gap-2 pr-2">
         <span class="i-ph-circle-notch-duotone animate-spin text-emerald-500"></span>
         <span class="text-[10px] uppercase font-mono text-emerald-500/70 tracking-widest">EXECUTING</span>
      </div>
      <div v-else class="shrink-0 flex items-center gap-2 pr-2 opacity-50">
         <span class="px-1.5 py-0.5 rounded text-[9px] uppercase font-bold tracking-widest font-mono border border-surface-700 text-surface-400">System Ready</span>
      </div>
    </div>
    
    <!-- Output Console (Expandido via Toggle) -->
    <div v-if="commandLog.length > 0" class="border-t border-surface-800/80 bg-[#0a0a0a] p-3 max-h-32 overflow-y-auto custom-scroll">
      <div v-for="(log, idx) in commandLog" :key="idx" class="font-mono text-[11px] mb-1.5 flex gap-2" :class="getLogColor(log.type)">
        <span class="opacity-50 select-none">[{{ log.timestamp }}]</span>
        <span>{{ log.text }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const commandText = ref('')
const isProcessing = ref(false)
const commandLog = ref<{timestamp: string, text: string, type: 'info' | 'error' | 'success'}[]>([])
const cmdInput = ref<HTMLInputElement | null>(null)

// Formatador de Relógio Brutalista
const getClock = () => {
    const d = new Date()
    return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}:${d.getSeconds().toString().padStart(2, '0')}`
}

const addLog = (text: string, type: 'info' | 'error' | 'success' = 'info') => {
    commandLog.value.unshift({ timestamp: getClock(), text, type })
    if (commandLog.value.length > 20) commandLog.value.pop()
}

const getLogColor = (type: string) => {
    if (type === 'error') return 'text-red-400'
    if (type === 'success') return 'text-emerald-400'
    return 'text-surface-400'
}

type CommandHandler = (args: string[]) => Promise<void> | void;
const registry: Record<string, CommandHandler> = {}

// REGISTRO DE COMANDOS (PÓS-BRAINSTORM)
registry['/flush-cache'] = async () => {
    addLog('Liberando L3 Semantic Cache e Node Vectors...', 'info')
    // Simular chamada API
    await new Promise(r => setTimeout(r, 600))
    addLog('Cache purged com sucesso. Memória liberada: 450MB.', 'success')
}

registry['/wake'] = async (args) => {
    const target = args[0] || 'The Doctor'
    addLog(`Enviando sinal de Wake-On-LAN para o Nódulo da Cloud [${target}]...`, 'info')
    await new Promise(r => setTimeout(r, 800))
    addLog(`${target} respondeu com handshake válido (24ms).`, 'success')
}

registry['/clear'] = () => {
    commandLog.value = []
}

registry['/help'] = () => {
    addLog('Comandos Disponíveis: /flush-cache, /wake [node], /clear', 'info')
}

const dispatchCommand = async () => {
    const raw = commandText.value.trim()
    if (!raw) return
    
    commandText.value = ''
    addLog(`> ${raw}`, 'info')
    
    // Parseia args (ex: /wake The Doctor -> cmd="/wake", args=["The", "Doctor"])
    const parts = raw.split(' ')
    const cmd = parts[0]?.toLowerCase() || ""
    const args = parts.slice(1)
    
    if (registry[cmd]) {
        isProcessing.value = true
        try {
            await registry[cmd](args)
        } catch (e: any) {
            addLog(`Falha na sub-rotina: ${e.message || String(e)}`, 'error')
        } finally {
            isProcessing.value = false
        }
    } else {
        addLog(`Comando não reconhecido: ${cmd}. Digite /help.`, 'error')
    }
}

// Focar no Terminal automaticamente se o usuário pressionar '/' no teclado enquanto estiver no Dashboard.
onMounted(() => {
    window.addEventListener('keydown', (e) => {
        // Se não estivermos digitando em outros inputs
        if (e.key === '/' && document.activeElement?.tagName !== 'INPUT' && document.activeElement?.tagName !== 'TEXTAREA') {
            e.preventDefault()
            if (cmdInput.value) {
                cmdInput.value.focus()
            }
            commandText.value = '/'
        }
    })
})
</script>
