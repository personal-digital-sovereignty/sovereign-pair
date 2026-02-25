<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import MarkdownIt from 'markdown-it'

// Inicializar parser de markdown
const md = new MarkdownIt({
  html: true,
  breaks: true,
  linkify: true
})

interface Message {
  id: number
  role: 'user' | 'assistant'
  content: string
  isStreaming?: boolean
  thumbs_up?: boolean
  thumbs_down?: boolean
}

interface ChatSession {
  id: number
  title: string
}

const inputMessage = ref('')
const currentSessionId = ref<number | null>(null)
const sessions = ref<ChatSession[]>([])

const isConfigModalOpen = ref(false)
const isLoadingConfig = ref(false)
const systemSettings = ref({
  llm_provider: 'ollama',
  llm_model: 'llama3',
  temperature: 0.1,
  system_prompt: ''
})

const localModels = ref<string[]>([])
const isFetchingModels = ref(false)

const fetchLocalModels = async () => {
  if (systemSettings.value.llm_provider !== 'ollama') return
  isFetchingModels.value = true
  try {
    const res = await fetch('http://127.0.0.1:8000/v1/ollama/models')
    if (res.ok) {
      const data = await res.json()
      localModels.value = data.models || []
    }
  } catch (error) {
    console.error('Falha ao obter modelos locais', error)
  } finally {
    isFetchingModels.value = false
  }
}

watch(() => systemSettings.value.llm_provider, (newVal) => {
  if (newVal === 'ollama') {
    fetchLocalModels()
  }
})

const messages = ref<Message[]>([
  { id: 1, role: 'assistant', content: 'Olá! Sou seu Sovereign Pair RAG. Estou conectado ao modelo local protegido em seus diretórios.\n\nComo posso ajudar hoje?' }
])
const isThinking = ref(false)
const chatContainer = ref<HTMLElement | null>(null)

// Recuperar Sessões do Backend
const loadSessions = async () => {
  try {
    const res = await fetch('http://localhost:8000/v1/sessions')
    if (res.ok) {
      sessions.value = await res.json()
    }
  } catch (e) {
    console.error("Erro ao carregar histórico", e)
    messages.value = []
  }
}

const fetchConfig = async () => {
  isLoadingConfig.value = true
  try {
    const res = await fetch('http://127.0.0.1:8000/v1/config')
    if (res.ok) {
      systemSettings.value = await res.json()
      if (systemSettings.value.llm_provider === 'ollama') {
         fetchLocalModels()
      }
    }
  } catch (error) {
    console.error('Falha ao obter configurações do servidor', error)
  } finally {
    isLoadingConfig.value = false
  }
}

const saveConfig = async () => {
  isLoadingConfig.value = true
  try {
    const res = await fetch('http://127.0.0.1:8000/v1/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(systemSettings.value)
    })
    if (res.ok) {
      systemSettings.value = await res.json()
      isConfigModalOpen.value = false
    }
  } catch (error) {
    console.error('Falha ao salvar configurações', error)
  } finally {
    isLoadingConfig.value = false
  }
}

const openConfigModal = () => {
  isConfigModalOpen.value = true
  fetchConfig()
}

onMounted(() => {
  loadSessions()
  fetchConfig()
})

const scrollToBottom = async () => {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

// Conectar ao backend FastAPI usando SSE
const sendMessage = async () => {
  if (!inputMessage.value.trim() || isThinking.value) return

  const userText = inputMessage.value
  inputMessage.value = ''
  
  messages.value.push({
    id: Date.now(),
    role: 'user',
    content: userText
  })
  scrollToBottom()

  isThinking.value = true
  
  const assistantMsgId = Date.now() + 1
  messages.value.push({
    id: assistantMsgId,
    role: 'assistant',
    content: '',
    isStreaming: true
  })
  scrollToBottom()

  try {
    const response = await fetch('http://localhost:8000/v1/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: userText,
        stream: true,
        session_id: currentSessionId.value
      })
    })

    if (!response.body) throw new Error("Sem resposta do corpo")

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let assistantMsgIndex = messages.value.findIndex(m => m.id === assistantMsgId)

    while (true) {
      const { value, done } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value, { stream: true })
      // SSE tokens vem como "data: {json}\n\n"
      const lines = chunk.split('\n')
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const dataStr = line.slice(6).trim()
          if (dataStr === '[DONE]') {
             fetchSessions() // Recarrega o menu da sidebar no final da conversa
             continue
          }
          
          try {
            const data = JSON.parse(dataStr)
            if (data.session_id_established && currentSessionId.value === null) {
               currentSessionId.value = data.session_id_established
            }
            if (data.message_id) {
               messages.value[assistantMsgIndex].id = data.message_id
            }
            
            const textDelta = data.content || data.token
            if (textDelta) {
              messages.value[assistantMsgIndex].content += textDelta
              scrollToBottom()
            }
          } catch (e) {
            console.error("Erro no parse SSE JSON", e, dataStr)
          }
        }
      }
    }
    
    messages.value[assistantMsgIndex].isStreaming = false

  } catch (error) {
    console.error("Ocorreu um erro ao buscar:", error)
    const assistantMsgIndex = messages.value.findIndex(m => m.id === assistantMsgId)
    messages.value[assistantMsgIndex].content += '\n\n**Erro**: Não foi possível comunicar com o servidor. Garanta que a API FastAPI (`uvicorn src.api.main:app`) está em execução.'
    messages.value[assistantMsgIndex].isStreaming = false
  } finally {
    isThinking.value = false
  }
}

// Carregar Histórico Antigo
const loadSession = async (id: number) => {
  try {
    const res = await fetch(`http://localhost:8000/v1/sessions/${id}`)
    if (res.ok) {
      const data = await res.json()
      currentSessionId.value = data.id
      messages.value = data.messages.map((m: any) => ({
        id: m.id,
        role: m.role,
        content: m.content,
        thumbs_up: m.thumbs_up,
        thumbs_down: m.thumbs_down
      }))
      setTimeout(scrollToBottom, 50)
    }
  } catch (e) {
    console.error("Falha ao abrir histórico via ID", e)
  }
}

// Enviar Feedback
const submitFeedback = async (msg: Message, type: 'up' | 'down') => {
  if (msg.role !== 'assistant' || !msg.id || msg.isStreaming) return
  
  // Optimistic UI Update
  const originalUp = msg.thumbs_up
  const originalDown = msg.thumbs_down
  
  if (type === 'up') {
    msg.thumbs_up = !msg.thumbs_up
    msg.thumbs_down = false
  } else {
    msg.thumbs_down = !msg.thumbs_down
    msg.thumbs_up = false
  }
  
  try {
    const res = await fetch('http://localhost:8000/v1/feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message_id: msg.id,
        thumbs_up: msg.thumbs_up || false,
        thumbs_down: msg.thumbs_down || false
      })
    })
    if (!res.ok) throw new Error("Falha ao salvar feedback")
  } catch (e) {
    console.error("Erro no feedback:", e)
    // Reverter no erro
    msg.thumbs_up = originalUp
    msg.thumbs_down = originalDown
  }
}

// Manual File Upload Logic (Paperclip Button)
const fileUploadInput = ref<HTMLInputElement | null>(null)

const triggerFileUpload = () => {
  fileUploadInput.value?.click()
}

const handleFileSelect = async (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    const file = target.files[0]
    await uploadFile(file)
    target.value = '' // reset input so same file can be uploaded again if needed
  }
}

// Drag & Drop File Upload Logic
const isDragging = ref(false)
const uploadStatus = ref<{ show: boolean, message: string, type: 'success' | 'error' | 'info' }>({ show: false, message: '', type: 'info' })
const conflictFile = ref<{ file: File, message: string } | null>(null)

const handleDragOver = (e: DragEvent) => {
  e.preventDefault()
  if (!isDragging.value) isDragging.value = true
}

const handleDragLeave = (e: DragEvent) => {
  e.preventDefault()
  // Verifica se o cursor realmente saiu do container principal para evitar flickering
  if (!e.relatedTarget || (e.relatedTarget as HTMLElement).nodeName === 'HTML') {
    isDragging.value = false
  }
}

const handleDrop = async (e: DragEvent) => {
  e.preventDefault()
  isDragging.value = false
  
  if (e.dataTransfer?.files && e.dataTransfer.files.length > 0) {
    const file = e.dataTransfer.files[0] // Fase 7 foca em 1 arquivo por drag
    await uploadFile(file)
  }
}

const showToast = (message: string, type: 'success' | 'error' | 'info' = 'info') => {
  uploadStatus.value = { show: true, message, type }
  setTimeout(() => uploadStatus.value.show = false, 4000)
}

const uploadFile = async (file: File, forceOverwrite = false, forceRename = false) => {
  const formData = new FormData()
  formData.append('file', file)
  if (forceOverwrite) formData.append('force_overwrite', 'true')
  if (forceRename) formData.append('rename_if_exists', 'true')
  
  showToast(`Iniciando processamento de: ${file.name}...`, 'info')
  
  try {
    const res = await fetch('http://localhost:8000/v1/upload', {
      method: 'POST',
      body: formData
    })
    const data = await res.json()
    
    if (res.ok && data.status === 'success') {
      showToast(data.message || 'Arquivo absorvido com sucesso pela Inteligência!', 'success')
      conflictFile.value = null
    } else if (data.status === 'conflict') {
      conflictFile.value = { file, message: data.message }
      uploadStatus.value.show = false
    } else {
      showToast('Erro interno ao extrair RAG Document.', 'error')
    }
  } catch (e) {
    console.error("Upload error", e)
    showToast('Falha na comunicação de arquivo com o servidor.', 'error')
  }
}

const resolveConflict = (action: 'cancel' | 'overwrite' | 'rename') => {
  if (conflictFile.value) {
     if (action === 'overwrite') {
         uploadFile(conflictFile.value.file, true, false)
     } else if (action === 'rename') {
         uploadFile(conflictFile.value.file, false, true)
     }
  }
  conflictFile.value = null
}
</script>

<template>
  <div class="flex h-screen w-full bg-[#0f172a] text-slate-200 overflow-hidden font-sans">
    
    <!-- Sidebar / Navigation -->
    <aside class="w-72 bg-[#1e293b] border-r border-slate-700/50 flex flex-col transition-all duration-300 transform hidden md:flex">
      <div class="p-4 flex items-center gap-3 border-b border-slate-700/50 shine-effect">
        <div class="w-8 h-8 rounded bg-gradient-to-tr from-[#0ea5e9] to-[#38bdf8] flex items-center justify-center shadow-lg shadow-sky-500/20">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"></path></svg>
        </div>
        <div>
          <h1 class="font-bold text-slate-100 tracking-tight">Sovereign Pair</h1>
          <p class="text-xs text-sky-400 font-medium">Local-first RAG Engine</p>
        </div>
      </div>
      
      <div class="flex-1 overflow-y-auto p-3 space-y-1">
        
        <button 
          @click="() => { currentSessionId = null; messages = [{ id: 1, role: 'assistant', content: 'Nova conversa iniciada. Como posso ajudar?' }]; }"
          class="w-full text-left px-3 py-2 rounded-md bg-emerald-500/20 text-emerald-400 text-sm hover:bg-emerald-500/30 transition-colors flex items-center gap-2 border border-emerald-500/30 font-medium mb-4">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
          Nova Conversa
        </button>

        <div class="text-[10px] uppercase font-bold text-slate-500 mb-2 px-2 tracking-wider">Histórico de Sessões</div>
        
        <button 
          v-for="session in sessions" 
          :key="session.id"
          @click="loadSession(session.id)"
          :class="['w-full text-left px-3 py-2 rounded-md text-sm transition-colors flex items-center gap-2 border', 
                   currentSessionId === session.id 
                    ? 'bg-[#334155] text-sky-300 border-sky-500/50 shadow-[0_0_10px_rgba(14,165,233,0.1)]' 
                    : 'bg-[#334155]/30 text-slate-300 hover:bg-[#334155]/80 border-slate-700/50']"
        >
          <svg class="w-4 h-4 shrink-0" :class="currentSessionId === session.id ? 'text-sky-400' : 'text-slate-500'" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path></svg>
          <span class="truncate">{{ session.title }}</span>
        </button>
        
        <div v-if="sessions.length === 0" class="text-xs text-slate-500 italic px-3 py-2 text-center">
          Nenhuma conversa salva
        </div>
      </div>
      
      <div class="p-4 border-t border-slate-700/50">
        <button 
          @click="openConfigModal"
          class="flex items-center justify-center gap-2 text-sm text-slate-300 hover:text-white transition-colors w-full p-2 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-600/50 shadow-sm"
        >
          <svg class="w-4 h-4 text-sky-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
          <span class="font-medium">Engine Settings</span>
        </button>
      </div>
    </aside>

    <!-- Main Chat Area -->
    <main 
      class="flex-1 flex flex-col h-full bg-[#0f172a] shadow-[-10px_0_30px_rgba(0,0,0,0.5)] z-10 relative"
      @dragover.prevent="handleDragOver" 
      @dragleave.prevent="handleDragLeave" 
      @drop.prevent="handleDrop"
    >
      
      <!-- Drag Overlay -->
      <div v-if="isDragging" class="absolute inset-x-2 inset-y-2 z-50 bg-[#0f172a]/90 backdrop-blur-md border-2 border-dashed border-sky-500 rounded-xl flex items-center justify-center transition-all">
        <div class="text-center pointer-events-none">
          <svg class="w-16 h-16 text-sky-400 mx-auto mb-4 animate-bounce" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path></svg>
          <h2 class="text-2xl font-bold text-slate-100">Solte o arquivo para Ingestão RAG</h2>
          <p class="text-slate-400 mt-2">PDF, Markdown ou TXT serão lidos e vetorizados instantaneamente.</p>
        </div>
      </div>

      <!-- Toast Notification -->
      <div v-if="uploadStatus.show" class="absolute top-6 right-6 z-50 px-4 py-3 rounded-lg shadow-2xl flex items-center gap-3 transition-all transform animate-fade-in-down" :class="uploadStatus.type === 'success' ? 'bg-emerald-500/20 border border-emerald-500/50 text-emerald-100' : (uploadStatus.type === 'error' ? 'bg-rose-500/20 border border-rose-500/50 text-rose-100' : 'bg-sky-500/20 border border-sky-500/50 text-sky-100')">
        <svg v-if="uploadStatus.type === 'success'" class="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
        <svg v-else-if="uploadStatus.type === 'error'" class="w-5 h-5 text-rose-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        <svg v-else class="w-5 h-5 text-sky-400 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
        <p class="text-sm font-medium">{{ uploadStatus.message }}</p>
      </div>

      <!-- Conflict Modal -->
      <div v-if="conflictFile" class="absolute inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center">
        <div class="bg-[#1e293b] border border-slate-700 p-6 rounded-2xl max-w-md w-full shadow-2xl animate-scale-in">
          <div class="flex items-center gap-3 mb-4 text-amber-400">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
            <h3 class="text-lg font-bold text-slate-100">Colisão de Arquivo</h3>
          </div>
          <p class="text-slate-300 text-sm mb-6 leading-relaxed">{{ conflictFile.message }}</p>
          <div class="flex gap-3 justify-end flex-wrap mt-2">
             <button @click="resolveConflict('cancel')" class="px-3 py-2 rounded-lg bg-[#334155] text-slate-300 hover:bg-slate-600 transition-colors text-sm font-medium">Cancelar</button>
             <button @click="resolveConflict('rename')" class="px-3 py-2 rounded-lg bg-emerald-500/20 border border-emerald-500/50 text-emerald-300 hover:bg-emerald-500/30 transition-colors text-sm font-medium shadow-[0_0_15px_rgba(16,185,129,0.2)]">Renomear Novo</button>
             <button @click="resolveConflict('overwrite')" class="px-3 py-2 rounded-lg bg-amber-500/20 border border-amber-500/50 text-amber-300 hover:bg-amber-500/30 transition-colors text-sm font-medium shadow-[0_0_15px_rgba(245,158,11,0.2)]">Sobrescrever Vetores</button>
          </div>
        </div>
      </div>
      
      <!-- Top header for mobile / status -->
      <header class="h-14 border-b border-slate-800 flex items-center px-4 justify-between shrink-0 bg-[#0f172a]/80 backdrop-blur-md">
        <h2 class="font-medium text-slate-300 md:hidden">Sovereign Pair</h2>
        <div class="flex items-center gap-2">
          <span class="flex h-2 w-2">
            <span class="animate-ping absolute inline-flex h-2 w-2 rounded-full bg-emerald-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <span class="text-xs font-medium text-slate-400">Motor Pronto</span>
        </div>
      </header>

      <!-- Chat Messages Scrollable Box -->
      <div 
        ref="chatContainer"
        class="flex-1 overflow-y-auto p-4 md:p-8 space-y-8 scroll-smooth"
      >
        <div 
          v-for="msg in messages" 
          :key="msg.id"
          class="flex w-full max-w-4xl mx-auto gap-4 md:gap-6 group"
          :class="msg.role === 'user' ? 'flex-row-reverse' : ''"
        >
          <!-- Avatar -->
          <div class="shrink-0 flex items-start justify-center mt-1">
            <div v-if="msg.role === 'assistant'" class="w-8 h-8 md:w-10 md:h-10 rounded-full bg-gradient-to-br from-[#0284c7] to-[#0ea5e9] flex items-center justify-center p-1.5 shadow-lg shadow-primary-500/20">
              <img src="/favicon.png" alt="AI Icon" class="w-full h-full object-contain filter brightness-0 invert" v-if="true" />
            </div>
            <div v-else class="w-8 h-8 md:w-10 md:h-10 rounded-full bg-slate-700 flex items-center justify-center p-2 text-slate-300">
              <svg class="w-full h-full" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>
            </div>
          </div>

          <!-- Message Box -->
          <div 
            class="flex flex-col max-w-[85%]"
            :class="msg.role === 'user' ? 'items-end' : 'items-start'"
          >
            <div 
              class="px-5 py-4 rounded-2xl shadow-sm text-[15px] leading-relaxed relative"
              :class="msg.role === 'user' ? 'bg-[#334155] text-slate-100 rounded-tr-sm' : 'bg-transparent prose prose-invert w-full max-w-none'"
            >
              <template v-if="msg.role === 'user'">
                {{ msg.content }}
              </template>
              <template v-else>
                <div v-html="md.render(msg.content)"></div>
                <span v-if="msg.isStreaming" class="w-2 h-4 bg-sky-400 inline-block animate-pulse ml-1 vertical-align-middle"></span>
              </template>
            </div>
            <div v-if="msg.role === 'assistant'" class="mt-2 flex items-center gap-3 px-2 text-slate-500 opacity-0 group-hover:opacity-100 transition-opacity">
              <button @click="submitFeedback(msg, 'up')" :class="msg.thumbs_up ? 'text-emerald-400' : 'hover:text-emerald-400'"><svg class="w-4 h-4" :fill="msg.thumbs_up ? 'currentColor' : 'none'" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.514"></path></svg></button>
              <button @click="submitFeedback(msg, 'down')" :class="msg.thumbs_down ? 'text-rose-400' : 'hover:text-rose-400'"><svg class="w-4 h-4" :fill="msg.thumbs_down ? 'currentColor' : 'none'" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14H5.236a2 2 0 01-1.789-2.894l3.5-7A2 2 0 018.736 3h4.018a2 2 0 01.485.06l3.76.94m-7 10v5a2 2 0 002 2h.096c.5 0 .905-.405.905-.904 0-.715.211-1.413.608-2.008L17 13V4m-7 10h2m5-10h2a2 2 0 012 2v6a2 2 0 01-2 2h-2.514"></path></svg></button>
            </div>
          </div>
        </div>
      </div>

      <!-- Input Area -->
      <div class="px-4 pb-6 pt-2 shrink-0 max-w-4xl w-full mx-auto">
        <input type="file" ref="fileUploadInput" class="hidden" @change="handleFileSelect" accept=".txt,.md,.pdf,.csv">
        <div class="relative flex items-center bg-[#1e293b] rounded-2xl border border-slate-700 shadow-xl focus-within:ring-1 focus-within:ring-sky-500/50 focus-within:border-sky-500/50 transition-all">
          <button @click="triggerFileUpload" class="absolute left-3 p-2 text-slate-400 hover:text-sky-400 transition-colors" title="Anexar Arquivo">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"></path></svg>
          </button>
          
          <textarea
            v-model="inputMessage"
            @keydown.enter.prevent="sendMessage"
            placeholder="Mensagem para Sovereign Pair..."
            class="w-full bg-transparent text-slate-200 pl-12 pr-14 py-4 max-h-48 rounded-2xl focus:outline-none resize-none placeholder-slate-500"
            rows="1"
          ></textarea>
          
          <button 
            @click="sendMessage"
            :disabled="!inputMessage.trim() || isThinking"
            class="absolute right-3 p-2 rounded-xl transition-all flex items-center justify-center bg-sky-500 text-white hover:bg-sky-400 disabled:bg-slate-700 disabled:text-slate-500"
          >
            <svg v-if="!isThinking" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path></svg>
            <svg v-else class="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
          </button>
        </div>
        <p class="text-center text-[11px] text-slate-500 mt-3 hidden md:block">
          Sovereign Pair AI pode cometer erros. Considere verificar informações com as fontes anexadas.
        </p>
      </div>

      <!-- Config Modal -->
      <div v-if="isConfigModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
        <div class="bg-slate-900 border border-slate-700/50 rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden flex flex-col max-h-[90vh]">
          
          <!-- Header -->
          <div class="px-6 py-4 border-b border-slate-700/50 flex justify-between items-center bg-slate-800/50">
            <h3 class="text-lg font-medium text-slate-200 flex items-center gap-2">
              <svg class="w-5 h-5 text-sky-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
              Engine Settings
            </h3>
            <button @click="isConfigModalOpen = false" class="text-slate-400 hover:text-white transition-colors">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
            </button>
          </div>
          
          <!-- Body -->
          <div class="px-6 py-6 overflow-y-auto space-y-6">
            
            <div class="grid grid-cols-2 gap-4">
              <div class="space-y-2">
                <label class="block text-sm font-medium text-slate-400">Provedor LLM</label>
                <select v-model="systemSettings.llm_provider" class="w-full bg-slate-800 border border-slate-700 text-slate-200 text-sm rounded-lg focus:ring-sky-500 focus:border-sky-500 block p-2.5 outline-none transition-all">
                  <option value="ollama">Ollama (Local)</option>
                  <option value="openai">OpenAI</option>
                  <option value="groq">Groq</option>
                  <option value="anthropic">Anthropic</option>
                  <option value="gemini">Gemini</option>
                </select>
              </div>
              <div class="space-y-2">
                <label class="block text-sm font-medium text-slate-400">Nome do Modelo</label>
                <template v-if="systemSettings.llm_provider === 'ollama'">
                  <div v-if="isFetchingModels" class="text-xs text-sky-400 flex items-center gap-2 p-2">
                    <svg class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
                    Buscando locais...
                  </div>
                  <select v-else v-model="systemSettings.llm_model" class="w-full bg-slate-800 border border-slate-700 text-slate-200 text-sm rounded-lg focus:ring-sky-500 focus:border-sky-500 block p-2.5 outline-none transition-all">
                    <option v-for="mod in localModels" :key="mod" :value="mod">{{ mod }}</option>
                    <option v-if="localModels.length === 0" value="llama3.2" disabled>Nenhum modelo encontrado</option>
                  </select>
                </template>
                <template v-else>
                  <input v-model="systemSettings.llm_model" type="text" class="w-full bg-slate-800 border border-slate-700 text-slate-200 text-sm rounded-lg focus:ring-sky-500 focus:border-sky-500 block p-2.5 outline-none transition-all" placeholder="ex: llama3, gpt-4o">
                </template>
              </div>
            </div>

            <div class="space-y-2">
              <div class="flex justify-between">
                <label class="block text-sm font-medium text-slate-400">Temperatura (Criatividade)</label>
                <span class="text-xs text-sky-400 font-mono">{{ systemSettings.temperature.toFixed(2) }}</span>
              </div>
              <input v-model.number="systemSettings.temperature" type="range" min="0" max="2" step="0.1" class="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-sky-500">
              <div class="flex justify-between text-[10px] text-slate-500 px-1">
                <span>Analítico (0)</span>
                <span>Balanceado (1)</span>
                <span>Caótico (2)</span>
              </div>
            </div>

            <div class="space-y-2">
              <label class="block text-sm font-medium text-slate-400">Persona (System Prompt)</label>
              <textarea v-model="systemSettings.system_prompt" rows="5" class="w-full bg-slate-800 border border-slate-700 text-slate-200 text-sm rounded-lg focus:ring-sky-500 focus:border-sky-500 block p-3 outline-none transition-all resize-none font-mono text-[13px] leading-relaxed" placeholder="Como o assistente deve se comportar..."></textarea>
              <p class="text-xs text-slate-500">Defina estritamente o papel, tom e comportamento. Será aplicado em novas interações.</p>
            </div>

          </div>

          <!-- Footer -->
          <div class="px-6 py-4 border-t border-slate-700/50 bg-slate-800/30 flex justify-end gap-3">
            <button @click="isConfigModalOpen = false" class="px-4 py-2 text-sm text-slate-300 hover:text-white transition-colors">Cancelar</button>
            <button @click="saveConfig" :disabled="isLoadingConfig" class="px-5 py-2 text-sm bg-sky-500 hover:bg-sky-400 text-white rounded-lg font-medium transition-colors shadow-[0_0_15px_rgba(14,165,233,0.3)] disabled:opacity-50 flex items-center gap-2">
              <svg v-if="isLoadingConfig" class="w-4 h-4 animate-spin flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
              {{ isLoadingConfig ? 'Salvando...' : 'Salvar no Banco' }}
            </button>
          </div>
          
        </div>
      </div>

    </main>
  </div>
</template>

<style scoped>
/* Optional: Adding some custom gradient animations if needed */
</style>
