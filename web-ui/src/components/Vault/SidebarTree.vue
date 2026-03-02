<template>
  <div class="h-full flex flex-col text-sm pt-4">
    <!-- Header -->
    <div class="px-4 pb-4 border-b border-[#222]">
      <div class="flex items-center gap-2 mb-2 text-zinc-100 font-semibold tracking-wide">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-book-open opacity-75"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>
        Sensus Vault
      </div>
      <div class="text-xs text-zinc-500 flex items-center gap-1">
        <div class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></div>
        Watching SharedBrain
      </div>
    </div>

    <!-- Dynamic File Tree -->
    <div class="flex-1 overflow-y-auto pt-2 px-2 space-y-4">
      
      <!-- Loading State -->
      <div v-if="isLoading" class="text-xs text-zinc-500 text-center py-4 animate-pulse">
        Carregando arquivos neurais...
      </div>

      <!-- Folders -->
      <div v-for="(files, folderName) in vaultTree" :key="folderName" v-else>
         <div v-if="folderName" class="text-[10px] uppercase font-bold text-zinc-600 mb-1 px-2 tracking-wider mt-2">
            {{ folderName }}
         </div>
         <div class="space-y-0.5">
           <div 
              v-for="file in files" 
              :key="file.id"
              @click="openFile(file)"
              @dblclick="openGlobalToc(file)"
              class="py-1.5 px-2 rounded hover:bg-zinc-800 cursor-pointer text-zinc-300 flex items-center gap-2 group transition-colors"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" class="opacity-50 group-hover:opacity-100 group-hover:text-emerald-400" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/></svg>
              <span class="truncate">{{ file.name }}</span>
              <!-- Bubble indicador se já foi vetorizado pelo Pai -->
              <div v-if="file.has_vector" class="ml-auto w-1.5 h-1.5 rounded-full bg-emerald-500/50 group-hover:bg-emerald-400" title="Vetorizado"></div>
              <div v-else class="ml-auto w-1.5 h-1.5 rounded-full bg-amber-500/50 group-hover:bg-amber-400 animate-pulse" title="Sem Vetor"></div>
           </div>
         </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const isLoading = ref(true)
const vaultTree = ref<Record<string, any[]>>({})

const openGlobalToc = (file: any) => {
   window.dispatchEvent(new CustomEvent('sensus-open-toc-modal', { detail: { file } }))
}

const openFile = (file: any) => {
    router.push({ path: '/vault', query: { file: file.id, name: file.name } })
}

const loadVaultTree = async () => {
  try {
    const token = localStorage.getItem('sovereign_token')
    const res = await fetch(`${API_BASE_URL}/v1/vault/tree`, {
      headers: token ? { 'Authorization': `Bearer ${token}` } : {}
    })
    if (res.ok) {
        vaultTree.value = await res.json()
    }
  } catch (error) {
    console.error("Failed to load Sensus Vault Tree", error)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadVaultTree()
})
</script>
