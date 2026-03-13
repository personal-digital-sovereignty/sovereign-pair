<template>
  <div class="flex flex-col text-sm pt-4 relative w-full" style="min-height: 200px;" @click="closeContextMenu">
    <!-- Header -->
    <div class="px-4 pb-4 border-b border-surface-700">
      <div class="flex items-center justify-between mb-2">
        <div class="flex items-center gap-2 text-surface-200 font-semibold tracking-wide" title="Sovereign Multi-Drive O.S">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-database opacity-75"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5V19A9 3 0 0 0 21 19V5"/><path d="M3 12A9 3 0 0 0 21 12"/></svg>
          Sensus Drives
        </div>
        <div class="flex gap-2">
          <!-- Mount O.S Drive -->
          <button @click="showMountModal = true" title="Atrelar Novo Diretório (Host OS)" class="p-1 hover:bg-surface-700/50 rounded-md text-surface-400 hover:text-primary-400 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
          </button>
          <!-- Refresh Geral -->
          <button @click.stop="loadAllWorkspaces" title="Atualizar Discos Nativamente" class="p-1 hover:bg-surface-700/50 rounded-md text-surface-400 hover:text-primary-400 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" :class="{'animate-spin': isLoading}"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg>
          </button>
        </div>
      </div>
      <div class="text-[10px] text-surface-500 flex items-center gap-1 uppercase tracking-widest font-bold">
        <div class="w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.8)] animate-pulse"></div>
        Multi-Workspace Tracking
      </div>
    </div>

    <!-- Dynamic File Tree -->
    <div class="flex-1 w-full overflow-y-auto pt-2 px-2 space-y-4 pb-12">
      
      <!-- Loading State -->
      <div v-if="isLoading" class="text-xs text-surface-500 text-center py-4 animate-pulse">
        Carregando OS Directory...
      </div>

      <!-- Global Tree Loop -->
      <div v-else class="space-y-6">
         <!-- Cada Workspace Atua como uma Raíz Virtual Independente no Frontend -->
         <div v-for="ws in workspacesTrees" :key="ws.workspace_id" class="workspace-block">
            <!-- Título do Drive Falso, p/ Clique de Context Menu e Expand -->
             <div class="flex items-center justify-between px-2 py-1.5 cursor-context-menu hover:bg-surface-700/50 rounded-md group text-surface-500 uppercase text-[10px] font-bold tracking-widest" @contextmenu.prevent="handleRootContextMenu($event, ws.workspace_id)">
                 <div class="flex items-center gap-2">
                     <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-primary-500"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>
                     {{ ws.name }}
                 </div>
                 
                 <!-- Guilhotina de Drive (Desatrelar) -->
                 <!-- Só exibimos se o Workspace Não For a Raiz Nativa O.S Primordial (id > 1 ou todos, deixarei p/ todos com Warning) -->
                 <button @click.stop="removeWorkspace(ws.workspace_id, ws.name)" title="Destruir Integração Cíbrida (Desatrelar Drive)" class="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-900/50 text-red-500 rounded transition-all">
                     <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" class="lucide lucide-trash-2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/><line x1="10" x2="10" y1="11" y2="17"/><line x1="14" x2="14" y1="11" y2="17"/></svg>
                 </button>
            </div>
            <!-- Filhos do Drive -->
            <SidebarTreeNode :nodes="ws.tree" :workspaceId="ws.workspace_id" @show-context-menu="handleContextMenu" />
         </div>
      </div>

    </div>

    <!-- Mount OS Modal -->
    <div v-if="showMountModal" class="fixed inset-0 z-[99999] flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
        <div class="bg-surface-900 border border-surface-700/50 rounded-xl shadow-2xl w-full max-w-md p-6 relative">
            <h3 class="text-lg font-bold text-surface-100 mb-2 flex items-center gap-2"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-primary-400"><path d="M5 12h14"/><path d="M12 5v14"/></svg> Mount O.S Directory</h3>
            <p class="text-sm text-surface-400 mb-6">Insira um caminho absoluto válido do seu sistema Hospedeiro para indexar um novo Drive Cíbrido.</p>
            
            <div class="space-y-4">
                <div>
                    <label class="block text-xs uppercase text-surface-500 font-bold tracking-widest mb-1.5">Drive Label Name</label>
                    <input v-model="newDriveName" type="text" placeholder="Ex: Personal Docs" class="w-full bg-surface-900 border border-surface-700 text-surface-200 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block p-2.5 outline-none transition-all">
                </div>
                <div>
                    <label class="block text-xs uppercase text-surface-500 font-bold tracking-widest mb-1.5">OS Absolute Path</label>
                    <input v-model="newDrivePath" type="text" placeholder="Ex: /home/user/Documents" class="w-full bg-surface-900 border border-surface-700 text-surface-200 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block p-2.5 outline-none transition-all font-mono">
                </div>
            </div>

            <div class="flex items-center justify-end gap-3 mt-8">
                <button @click="showMountModal = false" class="px-4 py-2 text-sm font-medium text-surface-400 hover:text-surface-100 transition-colors">Cancelar</button>
                <button @click="mountOsDrive" :disabled="!newDrivePath || isLoading" class="px-4 py-2 text-sm font-bold text-white bg-primary-600 hover:bg-primary-500 rounded-lg transition-colors ring-1 ring-primary-400/30 disabled:opacity-50 flex items-center gap-2">
                   <svg v-if="isLoadingMount" class="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                   Atrelar Drive
                </button>
            </div>
        </div>
    </div>

    <!-- Context Menu Overlay -->
    <div 
      v-if="contextMenu.visible" 
      :style="{ top: contextMenu.y + 'px', left: contextMenu.x + 'px' }"
      class="fixed z-[9999] w-48 bg-surface-900 border border-surface-700/50 shadow-xl rounded-md py-1 text-xs text-surface-300"
      @click.stop
    >
      <div class="px-3 py-1.5 text-[10px] uppercase font-bold text-surface-500 border-b border-surface-800 mb-1 tracking-wider truncate">
        {{ contextMenu.node ? contextMenu.node.name : 'Sensus Vault' }}
      </div>
      <button @click="createNewFolder" class="w-full text-left px-3 py-1.5 hover:bg-surface-800 hover:text-surface-100 transition-colors flex items-center gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5v14"/><path d="M5 12h14"/></svg> Nova Pasta
      </button>
      <button @click="createNewFile" class="w-full text-left px-3 py-1.5 hover:bg-surface-800 hover:text-surface-100 transition-colors flex items-center gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/></svg> Novo Arquivo
      </button>
      <template v-if="contextMenu.node">
        <div class="my-1 border-t border-surface-800"></div>
        <button @click="renameItem" class="w-full text-left px-3 py-1.5 hover:bg-surface-800 hover:text-surface-100 transition-colors flex items-center gap-2">
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

const RUST_CORE_URL = import.meta.env.VITE_RUST_CORE_URL || `http://${typeof window !== 'undefined' ? window.location.hostname : 'localhost'}:8001`
const isLoading = ref(true)

// O Estado UI Mestre de Workspaces Array (Não mais FileRoot única)
const workspacesTrees = ref<Array<{ workspace_id: number, name: string, path: string, tree: any[] }>>([])

// Context Menu Tracking Adaptado
const contextMenu = ref({
  visible: false,
  x: 0,
  y: 0,
  node: null as any,
  workspaceId: null as number | null
})

// Modals
const showMountModal = ref(false)
const newDriveName = ref('')
const newDrivePath = ref('')
const isLoadingMount = ref(false)

const closeContextMenu = () => {
  contextMenu.value.visible = false
}

const handleContextMenu = (payload: { event: MouseEvent, node: any, workspaceId: number }) => {
  contextMenu.value = {
    visible: true,
    x: payload.event.clientX,
    y: payload.event.clientY,
    node: payload.node,
    workspaceId: payload.workspaceId
  }
}

const handleRootContextMenu = (event: MouseEvent, targetWorkspaceId: number) => {
    contextMenu.value = {
      visible: true,
      x: event.clientX,
      y: event.clientY,
      node: null, // null indica Raiz
      workspaceId: targetWorkspaceId
    }
}

onMounted(() => {
  window.addEventListener('click', closeContextMenu)
  window.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeContextMenu() })
  loadAllWorkspaces()
})

onUnmounted(() => {
  window.removeEventListener('click', closeContextMenu)
})

const getHeaders = (): Record<string, string> => {
  const token = localStorage.getItem('sovereign_token')
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (token) headers['Authorization'] = `Bearer ${token}`
  return headers
}

// --- CRUD Operations (RUST NATIVE PORT 8001) ---
const getTargetParentPath = () => {
  if (!contextMenu.value.node) return "" // Root of Workspace
  if (contextMenu.value.node.type === 'dir' || contextMenu.value.node.is_dir) return contextMenu.value.node.id // Id em rust node é o path relativo ao root!
  return contextMenu.value.node.id.replace(`/${contextMenu.value.node.filename}`, '')
}

const mountOsDrive = async () => {
    if (!newDriveName.value || !newDrivePath.value) return;
    isLoadingMount.value = true;
    try {
        const res = await fetch(`${RUST_CORE_URL}/v1/workspaces`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify({ name: newDriveName.value, path: newDrivePath.value })
        })
        if (res.ok) {
            showMountModal.value = false;
            newDriveName.value = '';
            newDrivePath.value = '';
            await loadAllWorkspaces();
        } else {
            const err = await res.json()
            alert(`Falha Cíbrida ao Atrelar Drive O.S: ${err.message || 'Desconhecida'}`)
        }
    } catch (e) {
        alert("Erro fatal na comunicação com o Motor Rust (8001).")
    } finally {
        isLoadingMount.value = false;
    }
}

const removeWorkspace = async (id: number, name: string) => {
    const confirmation = window.confirm(`ATENÇÃO CÍBRIDA!\nVocê está prestes a desatrelar o Disco: [ ${name} ].\n\nIsso removerá a pasta do Sensus Hub e Acionará a Guilhotina Vetorial (Erradicando Fantasmas O.S) do Cerebro Local. O processo pode levar alguns segundos.\n\nDeseja prosseguir com a Decapitação?`)
    if (!confirmation) return;

    isLoading.value = true;
    try {
        const res = await fetch(`${RUST_CORE_URL}/v1/workspaces/${id}`, {
            method: 'DELETE',
            headers: getHeaders()
        })
        
        if (res.ok) {
            console.log("💥 [UI] O.S Workspace Removido com Sucesso. Guilhotina Vectorial Iniciada no Backend.");
            await loadAllWorkspaces(); // Reload Interface Cíbrida
        } else {
            const err = await res.json()
            alert(`Falha Cíbrida ao Desatrelar Workspace: ${err.message || 'Desconhecida'}`)
        }
    } catch (e) {
        alert("Erro fatal na comunicação com o Motor Rust (8001).")
    } finally {
        isLoading.value = false;
    }
}

const createNewFolder = async () => {
  const name = prompt("Nome da Nova Pasta:")
  if (!name || contextMenu.value.workspaceId === null) return closeContextMenu()
  
  const parentPath = getTargetParentPath()
  try {
    const res = await fetch(`${RUST_CORE_URL}/v1/vault/fs/create`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ workspace_id: contextMenu.value.workspaceId, type: 'folder', name, path: parentPath })
    })
    
    if (res.ok) await loadAllWorkspaces()
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
  if (!name || contextMenu.value.workspaceId === null) return closeContextMenu()
  if (!name.endsWith('.md')) name += '.md'
  
  const parentPath = getTargetParentPath()
  try {
    const res = await fetch(`${RUST_CORE_URL}/v1/vault/fs/create`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ workspace_id: contextMenu.value.workspaceId, type: 'file', name, path: parentPath })
    })
    
    if (res.ok) await loadAllWorkspaces()
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
  if (!contextMenu.value.node || contextMenu.value.workspaceId === null) return
  const currentName = contextMenu.value.node.filename
  let newName = prompt("Renomear para:", currentName)
  if (!newName || newName === currentName) return closeContextMenu()
  
  if (!contextMenu.value.node.is_dir && !newName.endsWith('.md')) {
      newName += '.md'
  }

  try {
    const res = await fetch(`${RUST_CORE_URL}/v1/vault/fs/rename`, {
      method: 'PUT',
      headers: getHeaders(),
      body: JSON.stringify({ workspace_id: contextMenu.value.workspaceId, path: contextMenu.value.node.id, new_name: newName })
    })
    
    if (res.ok) await loadAllWorkspaces()
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
  if (!contextMenu.value.node || contextMenu.value.workspaceId === null) return
  if (!confirm(`Tem certeza que deseja apagar permanentemente '${contextMenu.value.node.filename}'?`)) return closeContextMenu()
  
  try {
    const res = await fetch(`${RUST_CORE_URL}/v1/vault/fs/delete`, {
      method: 'DELETE',
      headers: getHeaders(),
      body: JSON.stringify({ workspace_id: contextMenu.value.workspaceId, path: contextMenu.value.node.id })
    })
    
    if (res.ok) await loadAllWorkspaces()
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

// --- The Sovereign Multi-Drive Fetcher ---
const loadAllWorkspaces = async () => {
  isLoading.value = true
  try {
    // 1. Descarrega os Registros O.S do SQLite Configurado
    const resWs = await fetch(`${RUST_CORE_URL}/v1/workspaces`, { headers: getHeaders() })
    if (!resWs.ok) throw new Error("Falha ao comunicar com os Registros Globais do Cíbrido")
    
    const dbRows = await resWs.json()
    const treesAggregated = []

    // 2. Itera puramente cada Espaço de Trabalho pedindo sua árvore nativa 100% Rust Std::FS
    for (const ws of dbRows) {
        try {
           const resTree = await fetch(`${RUST_CORE_URL}/v1/workspaces/${ws.id}/tree`, { headers: getHeaders() })
           if (resTree.ok) {
               const rootJson = await resTree.json()
               treesAggregated.push({
                   workspace_id: ws.id,
                   name: ws.name,
                   path: ws.path,
                   tree: rootJson
               })
           }
        } catch (e) {
            console.error(`Falha Escaneando o Drive Físico ${ws.name}`, e)
        }
    }

    workspacesTrees.value = treesAggregated
  } catch (error) {
    console.error("[Workspace API] Network fetch falhou de forma bruta:", error)
    workspacesTrees.value = []
  } finally {
    isLoading.value = false
  }
}
</script>
