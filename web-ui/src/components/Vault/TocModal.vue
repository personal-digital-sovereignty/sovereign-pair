<template>
  <Teleport to="body">
    <Transition name="fade-scale">
      <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <!-- Backdrop Blur -->
        <div class="absolute inset-0 bg-[#0E0E10]/80 backdrop-blur-sm" @click="close"></div>
        
        <!-- Modal Content -->
        <div class="relative w-full max-w-lg bg-[#151518] rounded-xl border border-[#2A2A2D] shadow-2xl flex flex-col max-h-[85vh] overflow-hidden transform transition-all">
          
          <!-- Header -->
          <div class="flex items-center justify-between px-5 py-4 border-b border-[#222]">
            <div class="flex items-center gap-3">
              <div class="p-1.5 bg-emerald-500/10 rounded-lg text-emerald-400">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-list-tree"><path d="M21 12h-8"/><path d="M21 6H8"/><path d="M21 18h-8"/><path d="M12 12V6h-4v6h4z"/><path d="M3 6v14h4v-4H3z"/></svg>
              </div>
              <div>
                <h3 class="text-sm font-semibold text-zinc-100 tracking-wide">Document Outline</h3>
                <p class="text-xs text-zinc-500 mt-0.5 truncate max-w-[300px]">{{ title || 'Untittled.md' }}</p>
              </div>
            </div>
            
            <button @click="close" class="p-1.5 text-zinc-500 hover:text-red-400 hover:bg-zinc-800 rounded transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-x"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
            </button>
          </div>

          <!-- Body / TOC List -->
          <div class="flex-1 overflow-y-auto p-3 custom-scrollbar">
            <div v-if="loading" class="flex flex-col items-center justify-center py-12 gap-3 text-zinc-500">
              <svg class="animate-spin h-6 w-6 text-emerald-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
              <span class="text-xs tracking-wider">Parsing Neural Structure...</span>
            </div>
            
            <div v-else-if="items.length === 0" class="flex flex-col items-center justify-center py-12 text-zinc-500 text-center px-4">
              <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none" class="mb-3 opacity-20" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" x2="8" y1="13" y2="13"/><line x1="16" x2="8" y1="17" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
              <p class="text-sm font-medium text-zinc-400">Sem estrutura</p>
              <p class="text-xs mt-1 max-w-[250px] opacity-70">Nenhum cabeçalho (H1, H2, H3) foi encontrado neste documento.</p>
            </div>
            
            <div v-else class="space-y-1">
              <button
                v-for="(item, index) in items" 
                :key="index"
                @click="navigate(item)"
                class="w-full text-left px-3 py-2 rounded-md hover:bg-zinc-800/80 transition-all group flex items-start gap-2 focus:outline-none focus:bg-zinc-800"
                :style="{ paddingLeft: `${(item.level - 1) * 1.5 + 0.75}rem` }"
              >
                <span class="text-[10px] font-mono font-bold text-zinc-600 mt-0.5 group-hover:text-emerald-500 transition-colors w-6 flex-shrink-0">
                  H{{ item.level }}
                </span>
                <span class="text-sm text-zinc-300 group-hover:text-zinc-100 flex-1 truncate">
                  {{ item.text }}
                </span>
              </button>
            </div>
          </div>
          
          <!-- Footer Indicator -->
          <div class="bg-[#121214] px-5 py-3 border-t border-[#222] flex justify-between items-center select-none text-zinc-500">
             <div class="text-[10px] font-medium tracking-wide flex items-center gap-1.5">
               <div class="w-1.5 h-1.5 rounded-full bg-emerald-500"></div>
               {{ items.length }} NÓS MAPEADOS
             </div>
             <div class="text-[10px] font-mono opacity-50">
                Pressione ESC para sair
             </div>
          </div>
          
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'

interface TocItem {
  level: number;
  text: string;
}

const props = defineProps<{
  isOpen: boolean;
  title: string | null;
  items: TocItem[];
  loading?: boolean;
}>()

const emit = defineEmits(['close', 'navigate'])

const close = () => {
  emit('close')
}

const navigate = (item: TocItem) => {
  emit('navigate', item)
}

// Global Keyboard Handler for ESC
const handleKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Escape' && props.isOpen) {
    close()
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.fade-scale-enter-active,
.fade-scale-leave-active {
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}
.fade-scale-enter-from,
.fade-scale-leave-to {
  opacity: 0;
  transform: scale(0.98);
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #333;
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #444;
}
</style>
