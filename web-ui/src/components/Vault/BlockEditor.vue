<template>
  <div class="h-full bg-[#0E0E10] text-zinc-200 flex flex-col items-center justify-center" v-if="isLoading">
     <div class="animate-pulse flex items-center gap-2">
        <div class="w-4 h-4 rounded-full bg-emerald-500/50"></div> Carregando Documento Neural...
     </div>
  </div>
  
  <div v-else-if="fetchError" class="h-full flex items-center justify-center text-red-400">
     {{ fetchError }}
  </div>

  <div v-else class="h-full bg-[#0E0E10] text-zinc-200 relative">
    <!-- Discreet Spellcheck Notification -->
    <div v-if="showSpellcheckPrompt" class="absolute top-4 right-8 z-50 bg-[#1A1A1D] border border-[#333] rounded-lg shadow-2xl p-4 max-w-xs animate-in slide-in-from-top-4 fade-in duration-300">
      <div class="flex items-start gap-3">
        <div class="mt-0.5 text-emerald-500">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 14 4-4"/><path d="M3.34 19a10 10 0 1 1 17.32 0"/></svg>
        </div>
        <div class="flex-1">
          <h4 class="text-sm font-medium text-white mb-1">Dicionário Ortográfico</h4>
          <p class="text-xs text-zinc-400 leading-relaxed mb-3">
            O corretor do navegador está desativado para evitar falsos positivos no Markdown. Deseja reativar o dicionário Pt-BR?
          </p>
          <div class="flex items-center gap-2">
            <button @click="setSpellcheck(true)" class="text-xs bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20 px-3 py-1.5 rounded transition-colors font-medium">
              Ativar Corretor
            </button>
            <button @click="setSpellcheck(false)" class="text-xs text-zinc-400 hover:text-white px-3 py-1.5 rounded transition-colors">
              Ignorar
            </button>
          </div>
        </div>
        <button @click="showSpellcheckPrompt = false" class="text-zinc-500 hover:text-white">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
        </button>
      </div>
    </div>

    <div class="max-w-4xl mx-auto px-8 py-12 h-full flex flex-col">
      <!-- Meta/Header -->
      <div class="mb-8 border-b border-[#222] pb-6 relative group">
        <input 
          type="text" 
          v-model="docData.name"
          class="bg-transparent text-4xl font-bold tracking-tight text-white w-full outline-none placeholder:text-zinc-600 focus:border-b focus:border-emerald-500/30 transition-colors"
          placeholder="New Document Title"
          disabled
        />
        <div class="mt-4 flex flex-wrap gap-4 text-xs text-zinc-500 items-center">
           <span class="max-w-[50%] flex items-center" :title="docData.path">
             <span class="truncate" dir="rtl">&lrm;{{ docData.path }}</span>
           </span>
           <span class="flex items-center gap-1">
               <!-- Auto Save Status Indicator -->
               <div :class="['w-1.5 h-1.5 rounded-full transition-colors', isSaving ? 'bg-amber-400 animate-pulse' : 'bg-zinc-600']"></div> 
               {{ isSaving ? 'Salvando...' : 'Auto-Saved a alguns segundos' }}
           </span>
           <span v-if="docData.has_vector" class="flex items-center gap-1.5 ml-2 text-emerald-500/80 bg-emerald-500/10 px-1.5 py-0.5 rounded text-[10px] font-medium border border-emerald-500/20" title="Indexado para IA">
               <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-zap"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
               <span v-if="docData.vector_id" class="font-mono opacity-80 uppercase">{{ docData.vector_id.substring(0, 8) }}</span>
               <span v-else>Vectorized</span>
           </span>
        </div>
        
        <!-- Tags -->
        <div class="mt-3 flex gap-2" v-if="docData.tags && docData.tags.length > 0">
           <span v-for="tag in docData.tags" :key="tag" class="px-2 py-0.5 bg-zinc-800 text-zinc-400 text-[11px] rounded uppercase font-medium tracking-wide border border-zinc-700">
             #{{ tag }}
           </span>
        </div>
      </div>
      
      <!-- TipTap Bubble Menu (Floating Formatter) -->
      <bubble-menu 
        v-if="editor" 
        :editor="editor" 
        :tippy-options="{ duration: 150 }"
        class="flex items-center gap-1 bg-[#222225] border border-[#333] shadow-2xl rounded-lg px-2 py-1.5 backdrop-blur-md"
      >
        <button @click="editor.chain().focus().toggleBold().run()" :class="{ 'text-emerald-400 bg-zinc-800': editor.isActive('bold'), 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800': !editor.isActive('bold') }" class="p-1.5 rounded transition-colors" title="Negrito (Cmd+B)">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 12a4 4 0 0 0 0-8H6v8"/><path d="M15 20a4 4 0 0 0 0-8H6v8Z"/></svg>
        </button>
        <button @click="editor.chain().focus().toggleItalic().run()" :class="{ 'text-emerald-400 bg-zinc-800': editor.isActive('italic'), 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800': !editor.isActive('italic') }" class="p-1.5 rounded transition-colors" title="Itálico (Cmd+I)">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="19" x2="10" y1="4" y2="4"/><line x1="14" x2="5" y1="20" y2="20"/><line x1="15" x2="9" y1="4" y2="20"/></svg>
        </button>
        <button @click="editor.chain().focus().toggleStrike().run()" :class="{ 'text-emerald-400 bg-zinc-800': editor.isActive('strike'), 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800': !editor.isActive('strike') }" class="p-1.5 rounded transition-colors" title="Tachado">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M16 4H9a3 3 0 0 0-2.83 4"/><path d="M14 12a4 4 0 0 1 0 8H6"/><line x1="4" x2="20" y1="12" y2="12"/></svg>
        </button>
        <div class="h-4 w-px bg-zinc-700 mx-1"></div>
        <button @click="editor.chain().focus().toggleCode().run()" :class="{ 'text-violet-400 bg-zinc-800': editor.isActive('code'), 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800': !editor.isActive('code') }" class="p-1.5 rounded transition-colors" title="Código Inline">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
        </button>
        <button @click="editor.chain().focus().toggleBlockquote().run()" :class="{ 'text-emerald-400 bg-zinc-800': editor.isActive('blockquote'), 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800': !editor.isActive('blockquote') }" class="p-1.5 rounded transition-colors" title="Citação">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21c3 0 7-1 7-8V5c0-1.25-.756-2.017-2-2H4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2s-1 .008-1 1.031V20c0 1 0 1 1 1z"/><path d="M15 21c3 0 7-1 7-8V5c0-1.25-.757-2.017-2-2h-4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2h.75c0 2.25.25 4-2.75 4v3c0 1 0 1 1 1z"/></svg>
        </button>
        <div class="h-4 w-px bg-zinc-700 mx-1"></div>
        <!-- Typography -->
        <button @click="editor.chain().focus().toggleHeading({ level: 1 }).run()" :class="{ 'text-emerald-400 bg-zinc-800': editor.isActive('heading', { level: 1 }), 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800': !editor.isActive('heading', { level: 1 }) }" class="p-1.5 rounded transition-colors font-bold text-xs" title="Título 1">H1</button>
        <button @click="editor.chain().focus().toggleHeading({ level: 2 }).run()" :class="{ 'text-emerald-400 bg-zinc-800': editor.isActive('heading', { level: 2 }), 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800': !editor.isActive('heading', { level: 2 }) }" class="p-1.5 rounded transition-colors font-bold text-xs" title="Título 2">H2</button>
        <button @click="editor.chain().focus().toggleHeading({ level: 3 }).run()" :class="{ 'text-emerald-400 bg-zinc-800': editor.isActive('heading', { level: 3 }), 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800': !editor.isActive('heading', { level: 3 }) }" class="p-1.5 rounded transition-colors font-bold text-xs" title="Título 3">H3</button>
      </bubble-menu>

      <!-- TipTap Floating Menu (Block Inserter) -->
      <floating-menu 
        v-if="editor" 
        :editor="editor" 
        :tippy-options="{ duration: 150, placement: 'left' }"
        class="flex flex-col gap-1 bg-[#1A1A1D] border border-[#333] shadow-2xl rounded-lg p-1.5 backdrop-blur-md w-48"
      >
        <div class="text-[10px] font-bold text-zinc-500 uppercase tracking-wider mb-1 px-2 pt-1 flex items-center justify-between">
           <span>Inserir Bloco</span>
           <span class="text-[8px] opacity-50 px-1 border border-zinc-700 rounded bg-zinc-800">Markdown</span>
        </div>
        
        <!-- Headings -->
        <div class="grid grid-cols-3 gap-1 px-1 mb-1">
          <button @click="editor.chain().focus().toggleHeading({ level: 1 }).run()" class="flex justify-center items-center py-1.5 rounded text-xs font-bold text-emerald-500 hover:text-white hover:bg-emerald-500/20 transition-colors">H1</button>
          <button @click="editor.chain().focus().toggleHeading({ level: 2 }).run()" class="flex justify-center items-center py-1.5 rounded text-xs font-bold text-emerald-500 hover:text-white hover:bg-emerald-500/20 transition-colors">H2</button>
          <button @click="editor.chain().focus().toggleHeading({ level: 3 }).run()" class="flex justify-center items-center py-1.5 rounded text-xs font-bold text-emerald-500 hover:text-white hover:bg-emerald-500/20 transition-colors">H3</button>
        </div>

        <div class="h-px bg-zinc-700/50 my-1 mx-1"></div>

        <!-- Lists & Structure -->
        <button @click="editor.chain().focus().toggleBulletList().run()" class="flex items-center gap-2 px-2 py-1.5 rounded text-sm text-zinc-400 hover:text-white hover:bg-zinc-800 transition-colors text-left w-full">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" class="text-zinc-500 w-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="8" x2="21" y1="6" y2="6"/><line x1="8" x2="21" y1="12" y2="12"/><line x1="8" x2="21" y1="18" y2="18"/><line x1="3" x2="3.01" y1="6" y2="6"/><line x1="3" x2="3.01" y1="12" y2="12"/><line x1="3" x2="3.01" y1="18" y2="18"/></svg> Lista
        </button>
        <button @click="editor.chain().focus().toggleOrderedList().run()" class="flex items-center gap-2 px-2 py-1.5 rounded text-sm text-zinc-400 hover:text-white hover:bg-zinc-800 transition-colors text-left w-full">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" class="text-zinc-500 w-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="10" x2="21" y1="6" y2="6"/><line x1="10" x2="21" y1="12" y2="12"/><line x1="10" x2="21" y1="18" y2="18"/><path d="M4 6h1v4"/><path d="M4 10h2"/><path d="M6 18H4c0-1 2-2 2-3s-1-1.5-2-1"/></svg> Numerada
        </button>
        <button @click="editor.chain().focus().toggleTaskList().run()" class="flex items-center gap-2 px-2 py-1.5 rounded text-sm text-zinc-400 hover:text-white hover:bg-zinc-800 transition-colors text-left w-full">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" class="text-zinc-500 w-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 11 3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg> Tarefas (To-Do)
        </button>
        <button @click="editor.chain().focus().toggleBlockquote().run()" class="flex items-center gap-2 px-2 py-1.5 rounded text-sm text-zinc-400 hover:text-white hover:bg-zinc-800 transition-colors text-left w-full">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" class="text-zinc-500 w-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21c3 0 7-1 7-8V5c0-1.25-.756-2.017-2-2H4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2s-1 .008-1 1.031V20c0 1 0 1 1 1z"/><path d="M15 21c3 0 7-1 7-8V5c0-1.25-.757-2.017-2-2h-4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2h.75c0 2.25.25 4-2.75 4v3c0 1 0 1 1 1z"/></svg> Citação
        </button>
        <button @click="editor.chain().focus().toggleCodeBlock().run()" class="flex items-center gap-2 px-2 py-1.5 rounded text-sm text-zinc-400 hover:text-white hover:bg-zinc-800 transition-colors text-left w-full">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" class="text-zinc-500 w-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg> Bloco de Código
        </button>
        <button @click="editor.chain().focus().setHorizontalRule().run()" class="flex items-center gap-2 px-2 py-1.5 rounded text-sm text-zinc-400 hover:text-white hover:bg-zinc-800 transition-colors text-left w-full">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" class="text-zinc-500 w-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" x2="19" y1="12" y2="12"/></svg> Divisor Horizontal
        </button>

        <div class="h-px bg-zinc-700/50 my-1 mx-1"></div>

        <!-- Tables -->
        <button @click="editor.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run()" class="flex items-center gap-2 px-2 py-1.5 rounded text-sm text-zinc-400 hover:text-white hover:bg-zinc-800 transition-colors text-left w-full">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-4 text-emerald-500"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M3 9h18"/><path d="M3 15h18"/><path d="M9 3v18"/><path d="M15 3v18"/></svg> Tabela (3x3)
        </button>

        <div class="h-px bg-zinc-700/50 my-1 mx-1"></div>
        
        <!-- Extensões -->
        <button @click="insertPresentationBlock" class="flex items-center gap-2 px-2 py-1.5 rounded text-sm text-indigo-400 hover:text-indigo-300 hover:bg-indigo-500/10 transition-colors text-left w-full font-medium">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-4"><rect width="20" height="14" x="2" y="3" rx="2"/><line x1="8" x2="16" y1="21" y2="21"/><line x1="12" x2="12" y1="17" y2="21"/></svg> Slide (16:9)
        </button>
      </floating-menu>

      <!-- TipTap Editor -->
      <editor-content :editor="editor" class="prose prose-invert prose-emerald max-w-none focus:outline-none" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { useEditor, EditorContent } from '@tiptap/vue-3'
import { BubbleMenu, FloatingMenu } from '@tiptap/vue-3/menus'
import StarterKit from '@tiptap/starter-kit'
import TaskList from '@tiptap/extension-task-list'
import TaskItem from '@tiptap/extension-task-item'
import { Table } from '@tiptap/extension-table'
import TableRow from '@tiptap/extension-table-row'
import TableHeader from '@tiptap/extension-table-header'
import TableCell from '@tiptap/extension-table-cell'
import { Markdown } from 'tiptap-markdown'
import { VaultSyntaxHighlighter } from './decorators'
import { PresentationBlock } from './extensions/PresentationBlock'

const props = defineProps({
  fileId: { type: String, required: true }
})

const emit = defineEmits(['editor-stats'])

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const isLoading = ref(true)
const fetchError = ref<string | null>(null)
const isSaving = ref(false)
let saveTimeout: ReturnType<typeof setTimeout> | null = null

// Spellcheck Preference Logic
const showSpellcheckPrompt = ref(false)
const spellcheckEnabled = ref(false)

const docData = ref<any>({})

const editor = useEditor({
  content: '', 
  extensions: [
    StarterKit,
    Markdown.configure({
        // Extract raw markdown instead of HTML
    }),
    TaskList,
    TaskItem.configure({
      nested: true,
    }),
    Table.configure({
      resizable: true,
    }),
    TableRow,
    TableHeader,
    TableCell,
    VaultSyntaxHighlighter,
    PresentationBlock,
  ],
  editorProps: {
    attributes: {
      class: 'focus:outline-none min-h-[500px] text-lg leading-relaxed text-zinc-300',
      spellcheck: spellcheckEnabled.value ? 'true' : 'false',
    },
  },
  onUpdate: ({ editor }) => {
    // Convert current TipTap Editor State into pure Markdown
    // @ts-expect-error extension typings inject this dynamically
    const markdownContent = editor.storage.markdown.getMarkdown() 
    debounceSave(markdownContent)
    computeEditorStats(markdownContent)
  }
})

const computeEditorStats = (markdown: string) => {
    // Basic word count splitting by whitespace
    const words = markdown.trim().split(/\s+/).filter(w => w.length > 0)
    
    // TipTap Markdown ext often escapes literal consecutive brackets as \[\[
    const unescapedMarkdown = markdown.replace(/\\/g, '')
    const links = (unescapedMarkdown.match(/\[\[.*?\]\]/g) || []).length
    
    emit('editor-stats', {
        words: words.length,
        links: links,
        path: docData.value?.path || 'N/A'
    })
}

const insertPresentationBlock = () => {
    if (editor.value) {
        // @ts-expect-error Custom TipTap command not typed in ChainedCommands
        editor.value.chain().focus().setPresentationBlock().run()
    }
}

const fetchDocument = async () => {
    isLoading.value = true
    fetchError.value = null
    try {
        const token = localStorage.getItem('sovereign_token')
        const headers: Record<string, string> = {}
        if (token) headers['Authorization'] = `Bearer ${token}`

        const res = await fetch(`${API_BASE_URL}/v1/vault/document/${props.fileId}`, { headers })
        if (!res.ok) throw new Error("Documento não encontrado no Vault")
        
        docData.value = await res.json()
        
        // Atualiza o TipTap com o Markdown puro e diz pra não emitir update para evitar loop de savar inicial
        if (editor.value) {
           editor.value.commands.setContent(docData.value.content, { emitUpdate: false }) 
           computeEditorStats(docData.value.content)
        }
        
    } catch(err: any) {
        fetchError.value = err.message
    } finally {
        isLoading.value = false
    }
}

const debounceSave = (content: string) => {
    isSaving.value = true
    if (saveTimeout) clearTimeout(saveTimeout)
    saveTimeout = setTimeout(async () => {
        try {
            const token = localStorage.getItem('sovereign_token')
            const headers: Record<string, string> = { "Content-Type": "application/json" }
            if (token) headers['Authorization'] = `Bearer ${token}`
            
            const res = await fetch(`${API_BASE_URL}/v1/vault/document/${props.fileId}`, {
                method: "PUT",
                headers,
                body: JSON.stringify({ content })
            })
            
            if (!res.ok) console.error("Auto-save falhou. Status:", res.status)
        } catch(e) {
            console.error("Auto-save Exception", e)
        } finally {
            isSaving.value = false
        }
    }, 1200) // Debounce delay 1.2s após parar de digitar
}

// Em caso de troca de documento com o mesmo componente Editor montado
watch(() => props.fileId, (newId) => {
    if (newId) fetchDocument()
})

const checkSpellcheckPreference = () => {
    const pref = localStorage.getItem('sensus_spellcheck')
    if (pref === null) {
        showSpellcheckPrompt.value = true
        spellcheckEnabled.value = false // Default off
    } else {
        showSpellcheckPrompt.value = false
        spellcheckEnabled.value = pref === 'true'
        updateEditorSpellcheck()
    }
}

const setSpellcheck = (enable: boolean) => {
    spellcheckEnabled.value = enable
    localStorage.setItem('sensus_spellcheck', enable.toString())
    showSpellcheckPrompt.value = false
    updateEditorSpellcheck()
}

const updateEditorSpellcheck = () => {
    if (editor.value) {
        editor.value.setOptions({
            editorProps: {
                ...editor.value.options.editorProps,
                attributes: {
                    ...editor.value.options.editorProps?.attributes,
                    spellcheck: spellcheckEnabled.value ? 'true' : 'false',
                    class: 'focus:outline-none min-h-[500px] text-lg leading-relaxed text-zinc-300',
                }
            }
        })
    }
}

onMounted(() => {
    fetchDocument()
    checkSpellcheckPreference()
})

onBeforeUnmount(() => {
    if (saveTimeout) clearTimeout(saveTimeout)
})
</script>

<style>
/* Estilos essenciais do TipTap */
.tiptap p.is-editor-empty:first-child::before {
  color: #52525b;
  content: attr(data-placeholder);
  float: left;
  height: 0;
  pointer-events: none;
}
.tiptap ul[data-type="taskList"] {
  list-style: none;
  padding: 0;
}
.tiptap li[data-type="taskItem"] {
  display: flex;
  align-items: flex-start;
  margin-bottom: 0.5rem;
}
.tiptap li[data-type="taskItem"] > label {
  margin-right: 0.5rem;
  user-select: none;
}
</style>
