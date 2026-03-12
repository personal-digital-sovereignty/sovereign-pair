<template>
  <div class="flex flex-col text-sm pt-4 relative w-full" style="min-height: 200px;" @click="closeContextMenu">
    <!-- Header -->
    <div class="px-4 pb-4 border-b border-[#222] cursor-context-menu hover:bg-zinc-800/30 transition-colors" @contextmenu.prevent="handleRootContextMenu($event, true)">
      <div class="flex items-center justify-between mb-2">
        <div class="flex items-center gap-2 text-zinc-100 font-semibold tracking-wide">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-book-open opacity-75"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>
          Sensus Vault
        </div>
        <button @click.stop="loadVaultTree" title="Atualizar Vault Nativamente" class="p-1 hover:bg-zinc-700/50 rounded-md text-zinc-400 hover:text-emerald-400 transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" :class="{'animate-spin': isLoading}"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg>
        </button>
      </div>
      <div class="text-xs text-zinc-500 flex items-center gap-1">
        <div class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></div>
        Watching SharedBrain
      </div>
    </div>

    <!-- Dynamic File Tree -->
    <div class="flex-1 w-full overflow-y-auto pt-2 px-2 space-y-4 pb-12">
      
      <!-- Loading State -->
      <div v-if="isLoading" class="text-xs text-zinc-500 text-center py-4 animate-pulse">
        Carregando OS Directory...
      </div>

      <!-- Recursive Tree Component -->
      <div v-else @contextmenu.prevent="handleRootContextMenu">
         <SidebarTreeNode :nodes="vaultTree" @show-context-menu="handleContextMenu" />
      </div>

    </div>

    <!-- Context Menu Overlay -->
    <div 
      v-if="contextMenu.visible" 
      :style="{ top: contextMenu.y + 'px', left: contextMenu.x + 'px' }"
      class="fixed z-[9999] w-48 bg-zinc-900 border border-zinc-700/50 shadow-xl rounded-md py-1 text-xs text-zinc-300"
      @click.stop
    >
      <div class="px-3 py-1.5 text-[10px] uppercase font-bold text-zinc-500 border-b border-zinc-800/50 mb-1 tracking-wider truncate">
        {{ contextMenu.node ? contextMenu.node.name : 'Sensus Vault' }}
      </div>
      <button @click="createNewFolder" class="w-full text-left px-3 py-1.5 hover:bg-zinc-800 hover:text-white transition-colors flex items-center gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5v14"/><path d="M5 12h14"/></svg> Nova Pasta
      </button>
      <button @click="createNewFile" class="w-full text-left px-3 py-1.5 hover:bg-zinc-800 hover:text-white transition-colors flex items-center gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/></svg> Novo Arquivo
      </button>
      <template v-if="contextMenu.node">
        <div class="my-1 border-t border-zinc-800/50"></div>
        <button @click="renameItem" class="w-full text-left px-3 py-1.5 hover:bg-zinc-800 hover:text-white transition-colors flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg> Renomear
        </button>
        <button @click="deleteItem" class="w-full text-left px-3 py-1.5 hover:bg-red-900/40 hover:text-red-400 text-red-500 transition-colors flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg> Deletar
        </button>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import SidebarTreeNode from './SidebarTreeNode.vue'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const isLoading = ref(true)
const vaultTree = ref<any[]>([])

// --- Context Menu State ---
const contextMenu = ref({
  visible: false,
  x: 0,
  y: 0,
  node: null as any
})

const closeContextMenu = () => {
  contextMenu.value.visible = false
}

const handleContextMenu = (payload: { event: MouseEvent, node: any }) => {
  contextMenu.value = {
    visible: true,
    x: payload.event.clientX,
    y: payload.event.clientY,
    node: payload.node
  }
}

const handleRootContextMenu = (event: MouseEvent, forceRoot: boolean = false) => {
  // Se for forceRoot (clique no header) ou no vazio da sidebar, assume root
  if (forceRoot || event.target === event.currentTarget) {
    contextMenu.value = {
      visible: true,
      x: event.clientX,
      y: event.clientY,
      node: null // null indica Raiz da Vault
    }
  }
}

onMounted(() => {
  window.addEventListener('click', closeContextMenu)
  window.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeContextMenu() })
  loadVaultTree()
})

onUnmounted(() => {
  window.removeEventListener('click', closeContextMenu)
})

const getHeaders = (): Record<string, string> => {
  const token = localStorage.getItem('sovereign_token')
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  return headers
}

// --- CRUD Operations ---
const getTargetParentPath = () => {
  if (!contextMenu.value.node) return "" // Root
  if (contextMenu.value.node.type === 'dir') return contextMenu.value.node.path
  // se for arquivo, o parent path seria o dirname. Mas o backend `routes.py` usa `RAW_DOCS_DIR` como root se o path for em branco?
  // O ideal era enviar o path do parent. Vamos mandar a string exata tirando o nome do arquivo.
  return contextMenu.value.node.path.replace(`/${contextMenu.value.node.name}`, '')
}

const createNewFolder = async () => {
  const name = prompt("Nome da Nova Pasta:")
  if (!name) return closeContextMenu()
  
  const parentPath = getTargetParentPath()
  try {
    const res = await fetch(`${API_BASE_URL}/v1/vault/fs/create`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ type: 'folder', name, path: parentPath })
    })
    
    if (res.ok) await loadVaultTree()
    else {
        const errorData = await res.json()
        alert(`Erro ao criar pasta: ${errorData.detail}`)
    }
  } catch (e) {
    console.error(e)
  } finally {
    closeContextMenu()
  }
}

const createNewFile = async () => {
  let name = prompt("Nome do Novo Arquivo (sem .md):")
  if (!name) return closeContextMenu()
  if (!name.endsWith('.md')) name += '.md'
  
  const parentPath = getTargetParentPath()
  try {
    const res = await fetch(`${API_BASE_URL}/v1/vault/fs/create`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ type: 'file', name, path: parentPath })
    })
    
    if (res.ok) await loadVaultTree()
    else {
        const errorData = await res.json()
        alert(`Erro ao criar arquivo: ${errorData.detail}`)
    }
  } catch (e) {
    console.error(e)
  } finally {
    closeContextMenu()
  }
}

const renameItem = async () => {
  if (!contextMenu.value.node) return
  const currentName = contextMenu.value.node.name
  let newName = prompt("Renomear para:", currentName)
  if (!newName || newName === currentName) return closeContextMenu()
  
  // Garantir a extensão
  if (contextMenu.value.node.type === 'file' && !newName.endsWith('.md')) {
      newName += '.md'
  }

  try {
    const res = await fetch(`${API_BASE_URL}/v1/vault/fs/rename`, {
      method: 'PUT',
      headers: getHeaders(),
      body: JSON.stringify({ path: contextMenu.value.node.path, new_name: newName })
    })
    
    if (res.ok) await loadVaultTree()
    else {
        const errorData = await res.json()
        alert(`Erro ao renomear: ${errorData.detail}`)
    }
  } catch (e) {
    console.error(e)
  } finally {
    closeContextMenu()
  }
}

const deleteItem = async () => {
  if (!contextMenu.value.node) return
  if (!confirm(`Tem certeza que deseja apagar permanentemente '${contextMenu.value.node.name}'?`)) return closeContextMenu()
  
  try {
    const res = await fetch(`${API_BASE_URL}/v1/vault/fs/delete`, {
      method: 'DELETE',
      headers: getHeaders(),
      body: JSON.stringify({ path: contextMenu.value.node.path })
    })
    
    if (res.ok) await loadVaultTree()
    else {
        const errorData = await res.json()
        alert(`Erro ao deletar: ${errorData.detail}`)
    }
  } catch (e) {
    console.error(e)
  } finally {
    closeContextMenu()
  }
}

// --- Init ---
const loadVaultTree = async () => {
  isLoading.value = true
  try {
    const res = await fetch(`${API_BASE_URL}/v1/vault/tree`, {
      method: 'GET',
      headers: getHeaders()
    })
    
    if (res.ok) {
        const text = await res.text()
        try {
            const data = JSON.parse(text)
            // Force vue reactivity by re-assigning a new array object
            vaultTree.value = Array.isArray(data) ? [...data] : []
        } catch (parseErr) {
            console.error("[Vault API] Failed to parse:", parseErr)
            vaultTree.value = []
        }
    } else {
        vaultTree.value = []
    }
  } catch (error) {
    console.error("[Vault API] Network fetch failed:", error)
    vaultTree.value = []
  } finally {
    isLoading.value = false
  }
}
</script>
