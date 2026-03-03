<template>
  <div class="flex h-screen w-full bg-[#0E0E10] text-[#E0E0E0] overflow-hidden">
    
    <!-- Main Editor Area -->
    <main class="flex-1 flex flex-col h-full bg-[#0E0E10]">
      <!-- Tab Bar -->
      <div v-if="tabs.length > 0" class="flex items-center overflow-x-auto bg-[#121214] border-b border-[#222] hide-scrollbar select-none">
        <div 
          v-for="tab in tabs" 
          :key="tab.id"
          @click="activeTabId = tab.id"
          class="group flex items-center gap-2 px-4 py-2 text-sm border-r border-[#222] cursor-pointer cursor-default whitespace-nowrap min-w-[120px] max-w-[200px]"
          :class="[activeTabId === tab.id ? 'bg-[#1E1E20] text-emerald-400 border-t-2 border-t-emerald-500' : 'text-zinc-400 hover:bg-[#1A1A1C] border-t-2 border-t-transparent']"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-file-text opacity-75 flex-shrink-0"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/></svg>
          <span class="truncate flex-1" :title="tab.name">{{ tab.name }}</span>
          <button @click.stop="closeTab(tab.id)" class="opacity-0 group-hover:opacity-100 hover:text-red-400 hover:bg-zinc-800 p-0.5 rounded transition-all">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" class="lucide lucide-x" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
          </button>
        </div>
      </div>

      <!-- Editor Canvas -->
      <div class="flex-1 overflow-y-auto relative bg-[#0E0E10]">
        <BlockEditor 
           v-if="activeTabId" 
           :fileId="activeTabId" 
           :key="activeTabId" 
           :viewMode="activeTabObject?.viewMode || 'visual'"
           @editor-stats="handleEditorStats" 
           @update-view-mode="handleUpdateViewMode"
        />
        <div v-else class="absolute inset-0 flex flex-col items-center justify-center text-zinc-500">
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-book-dashed opacity-20 mb-4"><path d="M20 22h-2"/><path d="M20 15v2"/><path d="M20 8v2"/><path d="M20 2v2"/><path d="M15 2h2"/><path d="M8 2h2"/><path d="M2 2h2"/><path d="M2 9v2"/><path d="M2 16v2"/><path d="M2 22h2"/><path d="M15 22h2"/><path d="m14 16-4-4"/><path d="m14 10-4 4"/></svg>
          <p class="text-lg font-light tracking-wide">Sensus Vault</p>
          <p class="text-sm mt-2 opacity-60">Selecione uma nota ou use <kbd class="px-1.5 py-0.5 bg-zinc-800 rounded font-mono text-xs mx-1">Cmd+K</kbd> para buscar rapidamente.</p>
        </div>
      </div>

      <!-- Contextual Status Bar (Mini-Copilot) -->
      <div v-if="activeTabId" class="flex-shrink-0 h-7 bg-[#121214] border-t border-[#222] flex items-center justify-between px-3 text-[11px] font-medium text-zinc-500 tracking-wide select-none">
        
        <!-- Left Side: Path & Status -->
        <div class="flex items-center gap-4">
          <div class="flex items-center gap-1.5 text-zinc-400 group cursor-pointer hover:text-zinc-200 transition-colors" title="Caminho do Arquivo">
            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="opacity-70 group-hover:opacity-100"><path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/></svg>
            <span class="truncate max-w-[300px]">{{ editorStats.path }}</span>
          </div>
        </div>

        <!-- Right Side: Metrics & Analytics -->
        <div class="flex items-center gap-4">
          <div class="flex items-center gap-1.5" title="Contador de Palavras">
            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="opacity-70"><path d="M17 6.1H3"/><path d="M21 12.1H3"/><path d="M15.1 18H3"/></svg>
            <span>{{ editorStats.words }} palavras</span>
          </div>
          
          <div class="flex items-center gap-1.5" title="Conexões Bidirecionais (Wikilinks)">
            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" class="lucide lucide-link-2 opacity-70" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 17H7A5 5 0 0 1 7 7h2"/><path d="M15 7h2a5 5 0 1 1 0 10h-2"/><line x1="8" x2="16" y1="12" y2="12"/></svg>
            <span>{{ editorStats.links }} links</span>
          </div>
          
          <div class="flex items-center gap-1 text-emerald-500/80 cursor-default" title="Status de Validação Neural">
            <div class="w-1.5 h-1.5 rounded-full bg-emerald-500 mr-0.5"></div>
            Online
          </div>
        </div>
        
      </div>
    </main>
    
    <SophiBar @select-file="handleSelectFile" />

    <!-- Table of Contents Modal -->
    <TocModal 
      :isOpen="isTocOpen"
      :title="tocActiveTitle"
      :items="tocItems"
      @close="isTocOpen = false"
      @navigate="handleTocNavigate"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BlockEditor from '../components/Vault/BlockEditor.vue'
import SophiBar from '../components/Vault/SophiBar.vue'
import TocModal from '../components/Vault/TocModal.vue'

interface Tab {
  id: string
  name: string
  viewMode?: 'visual' | 'source' | 'split'
}

const tabs = ref<Tab[]>([])
const activeTabId = ref<string | null>(null)

const activeTabObject = computed(() => tabs.value.find(t => t.id === activeTabId.value))

const handleUpdateViewMode = (mode: 'visual' | 'source' | 'split') => {
  const tab = tabs.value.find(t => t.id === activeTabId.value)
  if (tab) tab.viewMode = mode
}

// Status Bar State
const editorStats = ref({ words: 0, links: 0, path: 'Carregando...' })

const handleEditorStats = (stats: { words: number, links: number, path: string }) => {
  editorStats.value = stats
}

const handleSelectFile = (file: { id: string | null, name?: string, path?: string }) => {
  // Se o Sidebar/Sophi enviar nome, usa ele, senão faz um fallback pegando do basename doc
  let fallbackName = file.name
  const tabId = file.id || file.path // Fallback for OS files without database ID
  
  if (!tabId) return // Cannot open a tab without an identifier
  
  if (!fallbackName) {
      const parts = tabId.split('/')
      const lastPart = parts.length > 0 ? parts[parts.length - 1] : undefined
      fallbackName = lastPart || 'Untitled.md'
  }

  // Checa se já ta aberto
  const existingTabIndex = tabs.value.findIndex(t => t.id === tabId)
  if (existingTabIndex >= 0) {
    activeTabId.value = tabId
  } else {
    // Abre nova tab
    tabs.value.push({ id: tabId, name: fallbackName, viewMode: 'visual' })
    activeTabId.value = tabId
  }
}

// Router Watcher for Global Sidebar Integration
const route = useRoute()
const router = useRouter()

const processRouteQuery = () => {
    if (route.query.file || route.query.path) {
        let fileId = route.query.file as string | null
        if (fileId === 'undefined') fileId = null
        
        handleSelectFile({
            id: fileId,
            name: route.query.name as string | undefined,
            path: route.query.path as string | undefined
        })
        // Clear query to avoid re-triggering on local tab switch
        router.replace({ path: '/vault' })
    }
}

watch(() => route.query.file, () => {
    processRouteQuery()
})

onMounted(() => {
    processRouteQuery()
    window.addEventListener('sensus-toc-ready', handleTocReady)
    window.addEventListener('sensus-open-toc-modal', handleOpenTocModal)
})

const closeTab = (tabId: string) => {
  const index = tabs.value.findIndex(t => t.id === tabId)
  if (index === -1) return

  tabs.value.splice(index, 1)

  // Arruma tab ativa se fechou a atual
  if (activeTabId.value === tabId) {
    if (tabs.value.length > 0) {
      // Vai pra tab anterior
      const previousIndex = Math.max(0, index - 1)
      activeTabId.value = tabs.value[previousIndex]?.id || null
    } else {
      activeTabId.value = null
    }
  }
}

// ==========================================
// Table of Contents (Active Outline) Logic
// ==========================================
const isTocOpen = ref(false)
const tocActiveTitle = ref<string | null>(null)
const tocItems = ref<Array<{level: number, text: string, id: string}>>([])

const handleTocReady = (e: Event) => {
   const customEvent = e as CustomEvent
   tocItems.value = customEvent.detail?.items || []
}

const handleOpenTocModal = (e: Event) => {
   const customEvent = e as CustomEvent
   const file = customEvent.detail?.file
   if (file) {
       tocActiveTitle.value = file.name || 'Sumário'
       isTocOpen.value = true
       window.dispatchEvent(new CustomEvent('sensus-request-toc'))
   }
}

onBeforeUnmount(() => {
   window.removeEventListener('sensus-toc-ready', handleTocReady)
   window.removeEventListener('sensus-open-toc-modal', handleOpenTocModal)
})

const handleTocNavigate = (item: {level: number, text: string}) => {
   // Fechar modal
   isTocOpen.value = false
   
   // Emitir um evento nativo para que o componente BlockEditor filho pegue
   // ou fazer um dispatch de DOM, pois o TipTap mora numa sub-árvore
   const event = new CustomEvent('sensus-toc-navigate', { detail: { text: item.text } })
   window.dispatchEvent(event)
}

</script>

<style scoped>
.hide-scrollbar::-webkit-scrollbar {
  display: none;
}
.hide-scrollbar {
  -ms-overflow-style: none; /* IE and Edge */
  scrollbar-width: none; /* Firefox */
}
</style>
