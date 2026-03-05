<template>
  <div class="flex flex-col gap-1 bg-surface-900 border border-surface-700/60 shadow-2xl rounded-xl p-1.5 backdrop-blur-xl w-64 max-h-[300px] overflow-y-auto custom-scrollbar animate-in fade-in slide-in-from-top-2">
    <div class="text-[10px] font-bold text-surface-500 uppercase tracking-widest mb-1 px-2 pt-1.5 flex items-center justify-between sticky top-0 bg-surface-900 z-10 pb-1 border-b border-surface-800">
       <span class="flex items-center gap-1.5">
         <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20"/><path d="m2 12 20 0"/></svg>
         Sensus Blocks
       </span>
       <span class="text-[9px] opacity-70 px-1 border border-surface-700/50 rounded bg-surface-800/50 text-surface-400 font-mono tracking-tighter cursor-default" title="Teclas: ↑ ↓ Enter">↵</span>
    </div>
    
    <template v-if="items.length > 0">
      <button
        class="flex items-center gap-3 px-2 py-2 rounded-lg text-left w-full transition-all group outline-none"
        :class="{ 'bg-primary-500/10 text-primary-400 border border-primary-500/20 shadow-sm': index === selectedIndex, 'text-surface-300 hover:bg-surface-800 hover:text-white border border-transparent': index !== selectedIndex }"
        v-for="(item, index) in items"
        :key="index"
        @click="selectItem(index)"
        @mouseenter="selectedIndex = index"
      >
        <!-- SAST FIX: Avoid direct v-html to prevent Cross-Site Scripting (XSS). Safely rendering SVG icon. -->
        <component :is="{ template: item.icon }" class="w-7 h-7 flex items-center justify-center bg-surface-800 rounded-md border border-surface-700/50 group-hover:border-primary-500/30 group-hover:bg-primary-500/10 transition-colors shadow-sm shrink-0"></component>
        <div class="flex flex-col truncate">
           <span class="text-[13px] font-semibold tracking-wide leading-tight group-hover:text-primary-400 transition-colors" :class="{ 'text-primary-400': index === selectedIndex }">{{ item.title }}</span>
           <span class="text-[10px] text-surface-500 truncate mt-0.5 leading-none transition-colors group-hover:text-surface-400" :class="{ 'text-primary-500/70': index === selectedIndex }">{{ item.description }}</span>
        </div>
      </button>
    </template>
    
    <div class="p-4 text-center text-xs text-surface-500 italic flex flex-col items-center gap-2" v-else>
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="opacity-50"><line x1="18" x2="6" y1="6" y2="18"/><line x1="6" x2="18" y1="6" y2="18"/></svg>
      Nenhum bloco encontrado
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps({
  items: {
    type: Array as () => any[],
    required: true,
  },
  command: {
    type: Function,
    required: true,
  },
})

const selectedIndex = ref(0)

watch(() => props.items, () => {
  selectedIndex.value = 0
})

const onKeyDown = ({ event }: { event: KeyboardEvent }) => {
  if (event.key === 'ArrowUp') {
    upHandler()
    return true
  }
  if (event.key === 'ArrowDown') {
    downHandler()
    return true
  }
  if (event.key === 'Enter') {
    enterHandler()
    return true
  }
  return false
}

const upHandler = () => {
  selectedIndex.value = ((selectedIndex.value + props.items.length) - 1) % props.items.length
}

const downHandler = () => {
  selectedIndex.value = (selectedIndex.value + 1) % props.items.length
}

const enterHandler = () => {
  selectItem(selectedIndex.value)
}

const selectItem = (index: number) => {
  const item = props.items[index]
  if (item) {
    props.command(item)
  }
}

defineExpose({
  onKeyDown
})
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: var(--color-surface-700);
  border-radius: 10px;
}
</style>
