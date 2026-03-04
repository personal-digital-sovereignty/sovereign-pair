<template>
  <div class="bg-surface-800/80 border border-surface-700/50 rounded-xl p-5 backdrop-blur-sm flex flex-col relative overflow-hidden group">
    
    <!-- Header Opcional do Alvo (Task em Foco) -->
    <div v-if="activeTask" class="absolute top-0 left-0 w-full bg-primary-900/40 border-b border-primary-500/30 px-3 py-1.5 flex items-center justify-between z-10">
       <div class="flex items-center gap-2 overflow-hidden">
          <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" class="text-primary-400 flex-shrink-0" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>
          <span class="text-[10px] text-primary-200 font-medium truncate uppercase tracking-widest">Alvo: {{ activeTask }}</span>
       </div>
       <button @click="clearTask" class="text-primary-400 hover:text-white transition-colors" title="Limpar Alvo">
         <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
       </button>
    </div>

    <div :class="['flex flex-col items-center justify-center transition-all', activeTask ? 'pt-6' : '']">
      
      <!-- Seletor de Modos -->
      <div class="flex items-center gap-1 bg-surface-900/50 p-1 rounded-lg mb-4 border border-surface-700/50">
        <button 
          v-for="m in modes" 
          :key="m.id"
          @click="setMode(m.id)"
          :class="[
            'px-3 py-1 text-[11px] font-medium rounded-md transition-all',
            mode === m.id 
              ? 'bg-surface-700 text-white shadow-sm' 
              : 'text-surface-400 hover:text-surface-200 hover:bg-surface-800/80'
          ]"
        >
          {{ m.label }}
        </button>
      </div>

      <!-- Relógio (Timer) -->
      <div class="relative flex items-center justify-center mb-6">
        <!-- SVG Ring Progress -->
        <svg class="w-32 h-32 transform -rotate-90">
          <circle 
            class="text-surface-700/40" 
            stroke-width="4" 
            stroke="currentColor" 
            fill="transparent" 
            r="58" cx="64" cy="64"
          />
          <circle 
            :class="ringColor" 
            stroke-width="4" 
            :stroke-dasharray="circumference" 
            :stroke-dashoffset="dashOffset"
            stroke-linecap="round" 
            stroke="currentColor" 
            fill="transparent" 
            r="58" cx="64" cy="64"
            class="transition-all duration-1000 ease-linear"
          />
        </svg>
        
        <!-- Texto do Tempo -->
        <div class="absolute inset-0 flex flex-col items-center justify-center">
          <span class="text-3xl font-light tabular-nums tracking-tight truncate text-white" style="font-feature-settings: 'tnum';">
            {{ formattedTime }}
          </span>
          <span v-if="isRunning" class="text-[10px] text-emerald-400 font-mono mt-1 uppercase tracking-widest animate-pulse">
            Sovereign Focus
          </span>
        </div>
      </div>

      <!-- Controles Main -->
      <div class="flex items-center gap-4">
        <!-- Botão Play/Pause -->
        <button 
          @click="toggleTimer"
          class="w-12 h-12 rounded-full border border-surface-600 flex items-center justify-center transition-all focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 focus:ring-offset-surface-800"
          :class="isRunning ? 'bg-surface-700 text-amber-400 hover:bg-surface-600' : 'bg-primary-600 text-white hover:bg-primary-500 border-primary-500 shadow-lg shadow-primary-900/20'"
        >
          <svg v-if="!isRunning" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor" stroke="none"><polygon points="5 3 19 12 5 21 5 3"/></svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor" stroke="none"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>
        </button>

        <!-- Botão Reset -->
        <button 
          @click="resetTimer"
          class="w-10 h-10 rounded-full bg-surface-800 border border-surface-700 text-surface-400 flex items-center justify-center hover:bg-surface-700 hover:text-white transition-all focus:outline-none"
          title="Reiniciar Ciclo"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" class="lucide lucide-rotate-ccw" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg>
        </button>
      </div>
      
    </div>
    
    <!-- Audio Element Invisível para Notificação Clássica -->
    <audio ref="bellAudio" src="https://assets.mixkit.co/active_storage/sfx/2860/2860-preview.mp3" preload="auto"></audio>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'

const props = defineProps<{
    targetTask?: string | null
}>()

const emit = defineEmits(['task-cleared', 'cycle-complete'])

// -- Configs de Tempo (Minutos) --
const modes = [
    { id: 'focus', label: 'Pomodoro', minutes: 25 },
    { id: 'short_break', label: 'Pausa Curta', minutes: 5 },
    { id: 'long_break', label: 'Pausa Longa', minutes: 15 }
]

const mode = ref('focus')
const timeLeft = ref(25 * 60) // em segundos
const isRunning = ref(false)
const activeTask = ref<string | null>(null)
let timerInterval: number | null = null

// -- Setup de Referências --
const bellAudio = ref<HTMLAudioElement | null>(null)

// -- Computed Vars Relógio --
const formattedTime = computed(() => {
    const mins = Math.floor(timeLeft.value / 60)
    const secs = timeLeft.value % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
})

const totalTimeForCurrentMode = computed(() => {
    const m = modes.find(x => x.id === mode.value)
    return (m ? m.minutes : 25) * 60
})

// Progresso do Anel (0 a 1)
const progress = computed(() => {
    return 1 - (timeLeft.value / totalTimeForCurrentMode.value)
})

// Math de Circunferência de SVG
const radius = 58
const circumference = 2 * Math.PI * radius
const dashOffset = computed(() => circumference * (1 - progress.value))

const ringColor = computed(() => {
    if (mode.value === 'focus') return 'text-primary-500'
    if (mode.value === 'short_break') return 'text-emerald-500'
    return 'text-blue-500'
})

// -- Update Title Bar Document --
const updateDocumentTitle = () => {
    if (isRunning.value) {
        document.title = `(${formattedTime.value}) ${activeTask.value || 'Foco'} - Sovereign Pair`
    } else {
        document.title = 'Sovereign Pair'
    }
}

// -- Sincronizador de Props --
watch(() => props.targetTask, (newVal) => {
    if (newVal) {
        activeTask.value = newVal
        // Força modo Focus se ganhar uma nova task e não estiver rodando
        if (!isRunning.value && mode.value !== 'focus') {
           setMode('focus')
        }
    }
}, { immediate: true })

watch(timeLeft, () => {
   updateDocumentTitle()
   saveState()
})

watch([mode, isRunning, activeTask], () => {
   saveState()
})

// -- Lógica Central --
const setMode = (modeId: string) => {
    mode.value = modeId
    const m = modes.find(x => x.id === modeId)
    timeLeft.value = (m ? m.minutes : 25) * 60
    pause()
}

const toggleTimer = () => {
    if (isRunning.value) pause()
    else play()
}

const play = () => {
    if (timeLeft.value <= 0) resetTimer()
    
    isRunning.value = true
    timerInterval = window.setInterval(() => {
        if (timeLeft.value > 0) {
            timeLeft.value--
        } else {
            completeCycle()
        }
    }, 1000)
    saveState()
}

const pause = () => {
    isRunning.value = false
    if (timerInterval) clearInterval(timerInterval)
    updateDocumentTitle() // Limpa o title
    saveState()
}

const resetTimer = () => {
    pause()
    setMode(mode.value) // Reseta pro valor total do modo atual
}

const clearTask = () => {
    activeTask.value = null
    emit('task-cleared')
}

// Quando o timer zera
const completeCycle = () => {
    pause()
    timeLeft.value = 0 // Trava em zero visualmente por um instante
    
    // Tocar Som
    if (bellAudio.value) {
        bellAudio.value.currentTime = 0
        bellAudio.value.play().catch(e => console.log('Audio autoplay blocked', e))
    }
    
    // Notificação Nativa do O.S se permitido
    if ("Notification" in window && Notification.permission === "granted") {
         const title = mode.value === 'focus' ? 'Sessão de Foco Concluída!' : 'Pausa Finalizada'
         const body = activeTask.value 
               ? `Excelente trabalho focando em: ${activeTask.value}`
               : 'Hora de trocar de modo e se preparar para o próximo ciclo.'
               
         new Notification(title, {
            body: body,
            icon: '/icon.png' // Icone base do souverign
         })
    }
    
    emit('cycle-complete', { mode: mode.value, task: activeTask.value })
    
    // Auto-swap de Padrão Simples: Focus -> Short Break -> Focus
    if (mode.value === 'focus') {
       setMode('short_break')
    } else {
       setMode('focus')
    }
}

// -- Persistência do Estado (LocalStorage) --
// Permite que o usuário feche as abas (Dash -> Vault) e o relógio não perca onde estava
const STORAGE_KEY = 'sovereign_pomodoro_state'

const saveState = () => {
    const state = {
        mode: mode.value,
        timeLeft: timeLeft.value,
        isRunning: isRunning.value,
        activeTask: activeTask.value,
        lastTick: Date.now() // Pra compensar o tempo fechado
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
}

const restoreState = () => {
    const rawState = localStorage.getItem(STORAGE_KEY)
    if (rawState) {
        try {
            const state = JSON.parse(rawState)
            mode.value = state.mode || 'focus'
            activeTask.value = state.activeTask || null
            
            // Compensação de tempo fora da tela
            if (state.isRunning) {
                const now = Date.now()
                const diffSecs = Math.floor((now - state.lastTick) / 1000)
                const newTime = state.timeLeft - diffSecs
                
                if (newTime <= 0) {
                     // Passou do limite enquanto tava fechado
                     timeLeft.value = 0
                     isRunning.value = false // Não dispara o complete/audio offline pra não assustar no reload, apenas deixa pronto
                } else {
                     timeLeft.value = newTime
                     play() // Retoma automático
                }
            } else {
                timeLeft.value = state.timeLeft
                isRunning.value = false
            }
        } catch(e) { /* Silently ignore broken local storge */ }
    }
}

// -- Lyfecycle --
onMounted(() => {
    restoreState()
    
    // Pede permissão da Notificação do SO
    if ("Notification" in window && Notification.permission !== "granted" && Notification.permission !== "denied") {
        Notification.requestPermission()
    }
})

onUnmounted(() => {
    if (timerInterval) clearInterval(timerInterval)
    document.title = 'Sovereign Pair' // Limpa rastros
})
</script>
