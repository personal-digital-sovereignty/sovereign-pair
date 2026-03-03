<template>
  <div class="space-y-0.5 mt-0.5">
    <div v-for="node in nodes" :key="node.path">
      
      <!-- FOLDER -->
      <div v-if="node.type === 'dir'">
        <div 
          @click="toggleFolder(node.path)"
          @contextmenu.prevent="onContextMenu($event, node)"
          class="flex items-center gap-1.5 py-1 px-1.5 hover:bg-zinc-800 cursor-pointer text-zinc-400 group transition-colors rounded select-none"
        >
          <!-- Chevron -->
          <svg v-if="!isOpen(node.path)" xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="opacity-50 group-hover:opacity-100"><path d="m9 18 6-6-6-6"/></svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="opacity-50 group-hover:opacity-100"><path d="m6 9 6 6 6-6"/></svg>
          
          <!-- Folder Icon -->
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="opacity-70 group-hover:text-emerald-400"><path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z"/></svg>
          
          <span class="text-[11px] font-bold tracking-wide">{{ node.name }}</span>
        </div>
        
        <!-- Recursion -->
        <div v-show="isOpen(node.path)" class="pl-2.5 border-l border-zinc-800/50 ml-3.5 mt-0.5">
           <SidebarTreeNode :nodes="node.children" @show-context-menu="forwardContextMenu" />
        </div>
      </div>

      <!-- FILE -->
      <div v-else>
         <div 
            @click="openFile(node)"
            @dblclick="openGlobalToc(node)"
            @contextmenu.prevent="onContextMenu($event, node)"
            class="py-1.5 px-2 rounded hover:bg-zinc-800 cursor-pointer text-zinc-300 flex items-center gap-2 group transition-colors select-none"
          >
            <!-- File Text Icon -->
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" class="opacity-50 group-hover:opacity-100 group-hover:text-amber-300" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/></svg>
            <span class="truncate">{{ node.name }}</span>
            <div v-if="node.has_vector" class="ml-auto w-1.5 h-1.5 rounded-full bg-emerald-500/50 group-hover:bg-emerald-400" title="Vetorizado"></div>
            <div v-else class="ml-auto w-1.5 h-1.5 rounded-full bg-amber-500/50 group-hover:bg-amber-400 animate-pulse" title="Sem Vetor"></div>
         </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps<{ nodes: any[] }>()
const emit = defineEmits(['show-context-menu'])
const router = useRouter()

const getPersistedState = () => {
  try {
    return JSON.parse(localStorage.getItem('sensus-vault-folders') || '{}')
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
  return localState.value[path] === true
}

const openGlobalToc = (file: any) => {
   window.dispatchEvent(new CustomEvent('sensus-open-toc-modal', { detail: { file } }))
}

const openFile = (file: any) => {
    const query: any = { name: file.name, path: file.path }
    if (file.id) {
        query.file = file.id
    }
    router.push({ path: '/vault', query })
}

const onContextMenu = (event: MouseEvent, node: any) => {
    emit('show-context-menu', { event, node })
}

const forwardContextMenu = (payload: any) => {
    emit('show-context-menu', payload)
}
</script>
