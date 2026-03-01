<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="isOpen" class="fixed inset-0 z-[100] flex items-start justify-center pt-[15vh] px-4 sm:px-0">
        <!-- Backdrop -->
        <div class="fixed inset-0 bg-[#000000cc] backdrop-blur-sm transition-opacity" @click="close"></div>

        <!-- Command Palette -->
        <div 
          class="relative w-full max-w-2xl bg-[#121214] border border-[#2A2A2F] rounded-xl shadow-2xl overflow-hidden animate-in zoom-in-95 duration-200"
          role="dialog"
          aria-modal="true"
        >
          <!-- Search Header -->
          <div class="flex items-center px-4 border-b border-[#2A2A2F]">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-emerald-500 mr-3"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
            <input 
              ref="searchInput"
              type="text"
              v-model="query"
              class="w-full h-14 bg-transparent text-lg text-white placeholder-zinc-500 outline-none"
              placeholder="Pergunte à Sophi ou busque no Vault..."
              @keydown.down.prevent="selectNext"
              @keydown.up.prevent="selectPrev"
              @keydown.enter.prevent="handleEnter"
              @keydown.esc.prevent="close"
            />
            <div class="flex items-center gap-1 text-[10px] text-zinc-500 ml-2 border border-zinc-700 rounded px-1.5 py-0.5 bg-zinc-800/50">
               ESC
            </div>
          </div>

          <!-- Content / Results -->
          <div class="max-h-[60vh] overflow-y-auto p-2" v-if="results.length > 0">
            <div class="text-[10px] font-bold tracking-wider text-zinc-500 uppercase px-3 py-2">
               Base de Conhecimento
            </div>
            
            <button
              v-for="(res, index) in results"
              :key="res.id"
              class="w-full text-left px-3 py-3 rounded-lg flex flex-col gap-1 transition-colors"
              :class="selectedIndex === index ? 'bg-emerald-500/10' : 'hover:bg-zinc-800/50'"
              @click="selectResult(res)"
              @mouseenter="selectedIndex = index"
            >
              <div class="flex items-center justify-between">
                <span class="text-zinc-200 font-medium truncate flex-1" :class="{'text-emerald-400': selectedIndex === index}">
                   {{ res.name }}
                </span>
                <span v-if="res.has_vector" class="text-xs text-emerald-500/80 bg-emerald-500/10 px-1.5 py-0.5 rounded flex items-center gap-1">
                   <svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
                   Vector
                </span>
              </div>
              <p class="text-xs text-zinc-400 truncate w-full">{{ res.summary }}</p>
              
              <div class="flex gap-1 mt-1" v-if="res.tags && res.tags.length > 0">
                 <span v-for="tag in res.tags.slice(0, 3)" :key="tag" class="text-[10px] text-zinc-500">
                   #{{ tag }}
                 </span>
              </div>
            </button>
          </div>
          
          <div class="p-8 text-center text-zinc-500 text-sm" v-else-if="query.length > 0 && !isLoading">
             Nenhum neurônio corresponde à sua busca.
          </div>
          <div class="p-8 text-center" v-else-if="isLoading">
             <div class="w-5 h-5 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
          </div>
          <div class="p-6 text-center text-zinc-500 text-sm flex flex-col items-center justify-center gap-2" v-else>
             <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="opacity-30 mb-2"><path d="M4 22h14a2 2 0 0 0 2-2V7l-5-5H6a2 2 0 0 0-2 2v4"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M3 15h6"/><path d="M3 18h6"/><path d="M14 15h-3l-2 2v-4"/></svg>
             Busque por qualquer nota, tag ou conteúdo semântico.
          </div>

          <!-- Footer -->
          <div class="px-4 py-2 border-t border-[#2A2A2F] bg-[#0E0E10] flex items-center justify-between text-xs text-zinc-500">
             <div class="flex items-center gap-4">
                 <span class="flex items-center gap-1"><kbd class="bg-zinc-800 border border-zinc-700 rounded px-1.5 font-sans">↑</kbd> <kbd class="bg-zinc-800 border border-zinc-700 rounded px-1.5 font-sans">↓</kbd> Navegar</span>
                 <span class="flex items-center gap-1"><kbd class="bg-zinc-800 border border-zinc-700 rounded px-1.5 font-sans">↵</kbd> Abrir</span>
             </div>
             <div>Sophi Spotlight Search</div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'

const emit = defineEmits(['select-file'])

const isOpen = ref(false)
const query = ref('')
const results = ref<any[]>([])
const selectedIndex = ref(0)
const isLoading = ref(false)
const searchInput = ref<HTMLInputElement | null>(null)
let debounceTimeout: ReturnType<typeof setTimeout> | null = null

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const open = () => {
  isOpen.value = true
  query.value = ''
  results.value = []
  selectedIndex.value = 0
  nextTick(() => {
    if (searchInput.value) searchInput.value.focus()
  })
}

const close = () => {
  isOpen.value = false
}

const toggle = () => {
  if (isOpen.value) close()
  else open()
}

// Escuta Ctrl+K / Cmd+K globalmente
const handleGlobalKeydown = (e: KeyboardEvent) => {
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
    e.preventDefault()
    toggle()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleGlobalKeydown)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleGlobalKeydown)
})

const performSearch = async (val: string) => {
    if (!val.trim()) {
        results.value = []
        return
    }
    isLoading.value = true
    try {
        const token = localStorage.getItem('sovereign_token')
        const headers: Record<string, string> = {}
        if (token) headers['Authorization'] = `Bearer ${token}`

        const res = await fetch(`${API_BASE_URL}/v1/vault/search?q=${encodeURIComponent(val)}`, { headers })
        if (res.ok) {
            results.value = await res.json()
            selectedIndex.value = 0 // Reset selection
        }
    } catch(err) {
        console.error("Spotlight Error:", err)
    } finally {
        isLoading.value = false
    }
}

watch(query, (newVal) => {
    if (debounceTimeout) clearTimeout(debounceTimeout)
    debounceTimeout = setTimeout(() => {
        performSearch(newVal)
    }, 250)
})

const selectNext = () => {
  if (results.value.length === 0) return
  selectedIndex.value = (selectedIndex.value + 1) % results.value.length
}

const selectPrev = () => {
  if (results.value.length === 0) return
  selectedIndex.value = (selectedIndex.value - 1 + results.value.length) % results.value.length
}

const selectResult = (res: any) => {
  emit('select-file', { id: res.id })
  close()
}

const handleEnter = () => {
  if (results.value.length > 0 && results.value[selectedIndex.value]) {
    selectResult(results.value[selectedIndex.value])
  }
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
