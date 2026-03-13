<template>
  <div class="space-y-0.5 mt-0.5">
    <div v-for="node in nodes" :key="node.path">
      
      <!-- FOLDER -->
      <div v-if="node.type === 'dir' || node.is_dir">
        <div 
        <div class="flex items-center gap-1.5 flex-1 min-w-0" @click="toggleFolder(node.path)" @contextmenu.prevent="onContextMenu($event, node)">
          <!-- Chevron -->
          <svg v-if="!isOpen(node.path)" xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="opacity-50 group-hover:opacity-100 shrink-0"><path d="m9 18 6-6-6-6"/></svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="opacity-50 group-hover:opacity-100 shrink-0"><path d="m6 9 6 6 6-6"/></svg>
          
          <!-- Folder Icon -->
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="opacity-70 group-hover:text-emerald-400 shrink-0"><path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z"/></svg>
          
          <span class="text-[11px] font-bold tracking-wide truncate">{{ node.name }}</span>
        </div>
        
        <!-- Hover Actions -->
        <div class="opacity-0 group-hover:opacity-100 flex items-center gap-1.5 shrink-0 transition-opacity">
          <button @click.stop="onAction('rename', node)" class="p-0.5 hover:text-white" title="Renomear">
            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>
          </button>
          <button @click.stop="onAction('move', node)" class="p-0.5 hover:text-white" title="Mover">
             <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 9 2 6l3-3"/><path d="M9 5h10a2 2 0 0 1 2 2v10"/><path d="M19 15l3 3-3 3"/><path d="M15 19H5a2 2 0 0 1-2-2V7"/></svg>
          </button>
          <button @click.stop="onAction('delete', node)" class="p-0.5 hover:text-red-400 text-red-500" title="Deletar">
            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
          </button>
        </div>
        
        <!-- Recursion -->
        <div v-show="isOpen(node.path)" class="pl-2.5 border-l border-zinc-800/50 ml-3.5 mt-0.5">
           <SidebarTreeNode :nodes="node.children" :workspaceId="workspaceId" @show-context-menu="forwardContextMenu" />
        </div>
      </div>

      <!-- FILE -->
      <div v-else>
         <div class="py-1.5 px-2 rounded hover:bg-zinc-800 cursor-pointer text-zinc-300 flex items-center justify-between group transition-colors select-none">
            <div class="flex items-center gap-2 flex-1 min-w-0" @click="openFile(node)" @dblclick="openGlobalToc(node)" @contextmenu.prevent="onContextMenu($event, node)">
               <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" class="opacity-50 group-hover:opacity-100 group-hover:text-amber-300 shrink-0" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/></svg>
               <span class="truncate">{{ node.name }}</span>
            </div>
            
            <div class="flex items-center shrink-0">
              <div class="opacity-0 group-hover:opacity-100 flex items-center gap-1.5 mr-2 transition-opacity">
                <button @click.stop="onAction('rename', node)" class="p-0.5 hover:text-white" title="Renomear">
                  <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>
                </button>
                <button @click.stop="onAction('move', node)" class="p-0.5 hover:text-white" title="Mover">
                   <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 9 2 6l3-3"/><path d="M9 5h10a2 2 0 0 1 2 2v10"/><path d="M19 15l3 3-3 3"/><path d="M15 19H5a2 2 0 0 1-2-2V7"/></svg>
                </button>
                <button @click.stop="onAction('delete', node)" class="p-0.5 hover:text-red-400 text-red-500" title="Deletar">
                  <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
                </button>
              </div>
              <div v-if="node.has_vector" class="w-1.5 h-1.5 rounded-full bg-emerald-500/50 group-hover:bg-emerald-400" title="Vetorizado"></div>
              <div v-else class="w-1.5 h-1.5 rounded-full bg-amber-500/50 group-hover:bg-amber-400 animate-pulse" title="Sem Vetor"></div>
            </div>
         </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

defineOptions({ name: 'SidebarTreeNode' })

const props = defineProps<{ nodes: any[], workspaceId: number }>()
const emit = defineEmits(['show-context-menu', 'node-action'])
const router = useRouter()

const getPersistedState = () => {
  try {
    const raw = localStorage.getItem('sensus-vault-folders')
    if (!raw || raw === 'null') return {}
    return JSON.parse(raw) || {}
  } catch {
    return {}
  }
}

const savePersistedState = (state: Record<string, boolean>) => {
  localStorage.setItem('sensus-vault-folders', JSON.stringify(state))
}

const toggleFolder = (path: string) => {
  const state = getPersistedState()
  state[path] = !state[path]
  savePersistedState(state)
  localState.value = { ...state }
}

const localState = ref<Record<string, boolean>>(getPersistedState())

const isOpen = (path: string) => {
  return localState.value && localState.value[path] === true
}

const openGlobalToc = (file: any) => {
   window.dispatchEvent(new CustomEvent('sensus-open-toc-modal', { detail: { file } }))
}

const openFile = (file: any) => {
    const query: any = { name: file.name || file.filename, path: file.path, workspace_id: props.workspaceId }
    if (file.id) {
        query.file = file.id
    }
    router.push({ path: '/vault', query })
}

const onContextMenu = (event: MouseEvent, node: any) => {
    emit('show-context-menu', { event, node, workspaceId: props.workspaceId })
}

const forwardContextMenu = (payload: any) => {
    emit('show-context-menu', payload)
    if (payload.action) emit('node-action', payload)
}

const onAction = (action: string, node: any) => {
    emit('node-action', { action, node, workspaceId: props.workspaceId })
}
</script>
