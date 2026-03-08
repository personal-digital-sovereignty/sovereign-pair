<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
    <div class="bg-zinc-900 border border-white/10 rounded-xl shadow-2xl w-full max-w-2xl flex flex-col overflow-hidden">
      
      <!-- Header -->
      <div class="p-4 border-b border-white/10 bg-white/[0.02] flex items-center justify-between">
        <h2 class="text-xl font-medium text-white flex items-center gap-2">
          <i class="i-lucide-git-compare text-yellow-500"></i>
          Sync Conflict Detected
        </h2>
        <button @click="close" class="text-zinc-500 hover:text-white transition-colors">
          <i class="i-lucide-x text-xl"></i>
        </button>
      </div>
      
      <!-- Body -->
      <div class="p-6">
        <p class="text-zinc-300 text-sm mb-6 leading-relaxed">
          O arquivo Markdown físico <strong>({{ entityTitle }}.md)</strong> foi modificado externamente (provavelmente no VSCode, Obsidian ou por um Agente). 
          O banco de dados do UI Hub está desatualizado. Quem deve vencer este impasse?
        </p>

        <div class="grid grid-cols-2 gap-4">
          <!-- Option A: Markdown Wins -->
          <div class="bg-black/50 border border-emerald-500/30 rounded-lg p-4 flex flex-col gap-2 relative overflow-hidden group">
            <div class="absolute inset-0 bg-emerald-500/5 opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <div class="flex items-center gap-2 text-emerald-400 font-medium mb-1 z-10">
              <i class="i-lucide-file-text"></i> Markdown File Wins
            </div>
            <p class="text-xs text-zinc-400 z-10 flex-1">
              Força o banco de dados (SQLite) a absorver todas as mudanças feitas no arquivo físico, perdendo o estado atual do Kanban.
            </p>
            <div class="text-[10px] font-mono text-zinc-500 z-10 pt-2 border-t border-white/5">
              Modified: {{ formatTime(fileMtime) }}
            </div>
            <button @click="resolve('MARKDOWN_WINS')" class="mt-3 relative z-10 w-full py-2 bg-emerald-600/20 hover:bg-emerald-600/40 text-emerald-400 border border-emerald-500/30 rounded font-medium text-sm transition-colors">
              Accept Physical File
            </button>
          </div>

          <!-- Option B: SQLite Wins -->
          <div class="bg-black/50 border border-blue-500/30 rounded-lg p-4 flex flex-col gap-2 relative overflow-hidden group">
            <div class="absolute inset-0 bg-blue-500/5 opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <div class="flex items-center gap-2 text-blue-400 font-medium mb-1 z-10">
              <i class="i-lucide-database"></i> Database Wins
            </div>
            <p class="text-xs text-zinc-400 z-10 flex-1">
              Ignora completamente o arquivo modificado e sobrescreve o Markdown com o estado engavetado atual neste exato Kanban.
            </p>
            <div class="text-[10px] font-mono text-zinc-500 z-10 pt-2 border-t border-white/5">
              Last Synced: {{ formatTime(dbUpdate) }}
            </div>
            <button @click="resolve('DB_WINS')" class="mt-3 relative z-10 w-full py-2 bg-blue-600/20 hover:bg-blue-600/40 text-blue-400 border border-blue-500/30 rounded font-medium text-sm transition-colors">
              Trust Dashboard DB
            </button>
          </div>
        </div>
      </div>
      
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  isOpen: boolean
  entityTitle: string
  fileMtime: string
  dbUpdate: string
}>()

const emit = defineEmits(['close', 'resolve'])

const close = () => {
  emit('close')
}

const resolve = (strategy: 'MARKDOWN_WINS' | 'DB_WINS') => {
  emit('resolve', strategy)
  close()
}

const formatTime = (isoStr: string) => {
  if (!isoStr) return 'Unknown'
  return new Intl.DateTimeFormat('en-US', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(isoStr))
}
</script>
