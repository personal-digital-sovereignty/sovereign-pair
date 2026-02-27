<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import MarkdownIt from 'markdown-it'
import DOMPurify from 'dompurify'
import Setup from './views/Setup.vue'
import Login from './views/Login.vue'

// Custom directive to securely render HTML, bypassing the need for unsafe `v-html`
const vSafeHtml = {
  mounted(el: HTMLElement, binding: import('vue').DirectiveBinding) {
    el.innerHTML = DOMPurify.sanitize(binding.value)
  },
  updated(el: HTMLElement, binding: import('vue').DirectiveBinding) {
    el.innerHTML = DOMPurify.sanitize(binding.value)
  }
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const authPhase = ref('loading')

const getAuthHeaders = (): Record<string, string> => {
   const token = localStorage.getItem('sovereign_token')
   return token ? { 'Authorization': `Bearer ${token}` } : {}
}

const checkAuthStatus = async () => {
  try {
    const res = await fetch(`${API_BASE_URL}/v1/auth/status`)
    const data = await res.json()
    if (!data.is_setup) {
      authPhase.value = 'setup'
    } else {
      const token = localStorage.getItem('sovereign_token')
      if (!token) {
        authPhase.value = 'login'
      } else {
        authPhase.value = 'authenticated'
        loadSessions()
        fetchConfig()
      }
    }
  } catch(e) {
    console.error("Auth Server offline", e)
  }
}

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
  folder_name?: string | null
  tags?: string[]
}

const searchQuery = ref('')
const sessionToDelete = ref<number | null>(null)
const editingTagsInput = ref('')

const inputMessage = ref('')
const currentSessionId = ref<number | null>(null)
const sessions = ref<ChatSession[]>([])

const expandedFolders = ref<Record<string, boolean>>({})

const toggleFolder = (folderName: string) => {
  expandedFolders.value[folderName] = !expandedFolders.value[folderName]
}

const groupedSessions = computed(() => {
  const groups: Record<string, ChatSession[]> = { '': [] }
  const query = searchQuery.value.toLowerCase().trim()

  sessions.value.forEach(s => {
    if (query) {
      const titleMatch = s.title.toLowerCase().includes(query)
      const tagsMatch = s.tags && s.tags.some(t => t.toLowerCase().includes(query))
      if (!titleMatch && !tagsMatch) return
    }

    const f = s.folder_name || ''
    if (!groups[f]) {
      groups[f] = []
      if (expandedFolders.value[f] === undefined) {
         expandedFolders.value[f] = true
      }
    }
    groups[f].push(s)
  })
  return groups
})

const isEditSessionModalOpen = ref(false)
const editingSession = ref({ id: 0, title: '', folder_name: '', tags: [] as string[] })

const openEditSessionModal = (session: ChatSession | undefined) => {
  if (!session) return;
  editingSession.value = {
    id: session.id,
    title: session.title,
    folder_name: session.folder_name || '',
    tags: session.tags ? [...session.tags] : []
  }
  editingTagsInput.value = ''
  isEditSessionModalOpen.value = true
}

const addTag = () => {
  const tag = editingTagsInput.value.trim()
  if (tag && !editingSession.value.tags.includes(tag)) {
    editingSession.value.tags.push(tag)
  }
  editingTagsInput.value = ''
}

const removeTag = (index: number) => {
  editingSession.value.tags.splice(index, 1)
}

const deleteSessionConfirmed = async () => {
  if (!sessionToDelete.value) return
  
  try {
    const res = await fetch(`${API_BASE_URL}/v1/sessions/${sessionToDelete.value}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    })
    
    if (res.ok) {
      if (currentSessionId.value === sessionToDelete.value) {
        currentSessionId.value = null
        messages.value = [{ id: 1, role: 'assistant', content: 'Nova conversa iniciada. Como posso ajudar?' }]
      }
      await loadSessions()
    }
  } catch (e) {
    console.error("Falha ao deletar sessão", e)
  } finally {
    sessionToDelete.value = null
  }
}

const saveSessionEdit = async () => {
  try {
    // Adiciona qualquer tag pendente no input antes de salvar
    if (editingTagsInput.value.trim()) {
      addTag()
    }
    const res = await fetch(`${API_BASE_URL}/v1/sessions/${editingSession.value.id}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders()
      },
      body: JSON.stringify({
        title: editingSession.value.title,
        folder_name: editingSession.value.folder_name,
        tags: editingSession.value.tags
      })
    })
    if (res.ok) {
      isEditSessionModalOpen.value = false
      await loadSessions()
    }
  } catch (e) {
    console.error("Falha ao atualizar sessão", e)
  }
}

const activeSession = computed(() => {
  return sessions.value.find(s => s.id === currentSessionId.value)
})

const isConfigModalOpen = ref(false)
const isLoadingConfig = ref(false)
const systemSettings = ref({
  llm_provider: 'ollama',
  llm_model: 'llama3',
  temperature: 0.1,
  system_prompt: '',
  theme: 'dark',
  persona: 'default',
  formality: 'neutral',
  persona_graphic_style: 'emoji',
  nickname: '',
  occupation: '',
  about_user: '',
  language: 'Português do Brasil',
  geolocation: ''
})

const personaOptions = [
  { id: 'default', icon: '🧠', name: 'Assistente Padrão (Default)', prompt: 'Foco em respostas analíticas, pragmáticas e diretas. Traga conhecimento fundamentado sem enrolação.' },
  { id: 'developer', icon: '💻', name: 'Desenvolvedor Sênior', prompt: 'Aja como um Arquiteto de Software sênior. Foco em código limpo (Clean Code), design patterns, otimização de performance e explicações técnicas concisas e precisas.' },
  { id: 'marketing', icon: '📈', name: 'Mestre do Marketing', prompt: 'Você é um especialista em Marketing Digital. Use copywriting persuasivo focado em conversão, métricas, SEO e lançamento de produtos. Adote um tom empolgante.' },
  { id: 'admin', icon: '👔', name: 'Gestor & Admin', prompt: 'Aja como um administrador de empresas e gerente de projetos sênior. Foco em organização corporativa, planilhas estruturadas, relatórios processuais e finanças limpas.' },
  { id: 'professor', icon: '🎓', name: 'Professor Acadêmico', prompt: 'Você é um mentor acadêmico compassivo e sagaz. Explique conceitos complexos com metáforas didáticas, passo a passo, fomentando o raciocínio sem dar apenas a resposta pronta imediata.' },
  { id: 'career', icon: '💼', name: 'Mentor de Carreira', prompt: 'Você é um Headhunter experiente. Foco na evolução profissional do usuário, melhoria de propostas de valor (currículos e portfólios) e dicas cirúrgicas de networking e entrevistas.' },
  { id: 'productivity', icon: '⚡', name: 'Hacker de Rendimento', prompt: 'Comporte-se como um executor fanático por otimização de tempo. Foco rígido na geração de checklists diretos, métodos ágeis (Kanban/Scrum) e atalhos de produtividade extrema.' },
  { id: 'creative', icon: '💡', name: 'Brainstormer Criativo', prompt: 'Seja extremamente imaginativo e fora-da-caixa. Seu objetivo é ajudar a encontrar soluções inovadoras para problemas normais, usando um tom entusiasmado e proativo. Proponha cenários alternativos abundantes.' }
]

const selectPersona = (p: typeof personaOptions[0]) => {
  systemSettings.value.persona = p.id
  systemSettings.value.system_prompt = p.prompt
}

const localModels = ref<string[]>([])
const isFetchingModels = ref(false)

const fetchLocalModels = async () => {
  if (systemSettings.value.llm_provider !== 'ollama') return
  isFetchingModels.value = true
  try {
    const res = await fetch(`${API_BASE_URL}/v1/ollama/models`, {
        headers: getAuthHeaders()
    })
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
  { id: 0, role: 'assistant', content: 'Olá! Sou seu Sovereign Pair RAG. Estou conectado ao modelo local protegido em seus diretórios.\n\nComo posso ajudar hoje?' }
])
const isThinking = ref(false)
const chatContainer = ref<HTMLElement | null>(null)

// Recuperar Sessões do Backend
const loadSessions = async () => {
  try {
    const res = await fetch(`${API_BASE_URL}/v1/sessions`, {
        headers: getAuthHeaders()
    })
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
    const res = await fetch(`${API_BASE_URL}/v1/config`, {
        headers: getAuthHeaders()
    })
    if (res.ok) {
      systemSettings.value = await res.json()
      if (systemSettings.value.llm_provider === 'ollama') {
         fetchLocalModels()
      }
      applyTheme(systemSettings.value.theme)
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
    const res = await fetch(`${API_BASE_URL}/v1/config`, {
      method: 'POST',
      headers: { 
          'Content-Type': 'application/json',
          ...getAuthHeaders()
      },
      body: JSON.stringify(systemSettings.value)
    })
    if (res.ok) {
      systemSettings.value = await res.json()
      isConfigModalOpen.value = false
      applyTheme(systemSettings.value.theme)
    }
  } catch (error) {
    console.error('Falha ao salvar configurações', error)
  } finally {
    isLoadingConfig.value = false
  }
}

const applyTheme = (themeName: string) => {
  const root = document.documentElement;
  root.classList.remove('theme-slate', 'theme-ocean', 'theme-forest', 'theme-hacker', 'theme-rose', 'theme-amber', 'theme-purple', 'theme-light');
  
  if (themeName === 'light') {
    root.classList.add('theme-light');
  } else if (themeName && themeName !== 'dark') {
    root.classList.add(`theme-${themeName}`);
  } else {
    root.classList.add('theme-slate');
  }
}

watch(() => systemSettings.value.theme, (newVal) => {
  applyTheme(newVal)
})

const isTokenVisible = ref(false)
const authTokenForDisplay = ref('')

const openConfigModal = () => {
  isConfigModalOpen.value = true
  isTokenVisible.value = false
  authTokenForDisplay.value = localStorage.getItem('sovereign_token') || ''
  fetchConfig()
}

const sidebarWidth = ref(288) // w-72 = 18rem = 288px
const isDraggingSidebar = ref(false)
const isSidebarOpen = ref(true)

const startDragSidebar = () => {
  isDraggingSidebar.value = true
  document.body.style.cursor = 'col-resize'
  document.addEventListener('mousemove', dragSidebar)
  document.addEventListener('mouseup', stopDragSidebar)
}

const dragSidebar = (e: MouseEvent) => {
  if (!isDraggingSidebar.value) return
  let newWidth = e.clientX
  if (newWidth < 200) newWidth = 200
  if (newWidth > 600) newWidth = 600
  sidebarWidth.value = newWidth
}

const stopDragSidebar = () => {
  isDraggingSidebar.value = false
  document.body.style.cursor = ''
  document.removeEventListener('mousemove', dragSidebar)
  document.removeEventListener('mouseup', stopDragSidebar)
  localStorage.setItem('sidebar_width', sidebarWidth.value.toString())
}

onMounted(() => {
  checkAuthStatus()
  const savedWidth = localStorage.getItem('sidebar_width')
  if (savedWidth) {
    sidebarWidth.value = parseInt(savedWidth)
  }
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
    const response = await fetch(`${API_BASE_URL}/v1/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders()
      },
      body: JSON.stringify({
        message: userText,
        stream: true,
        session_id: currentSessionId.value,
        provider: systemSettings.value.llm_provider,
        model: systemSettings.value.llm_model
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
             loadSessions() // Recarrega o menu da sidebar no final da conversa
             continue
          }
          
          try {
            const data = JSON.parse(dataStr)
            if (data.session_id_established && currentSessionId.value === null) {
               currentSessionId.value = data.session_id_established
            }
            if (data.message_id) {
               if (messages.value[assistantMsgIndex]) {
                 messages.value[assistantMsgIndex].id = data.message_id
               }
            }
            
            const textDelta = data.content || data.token
            if (textDelta && messages.value[assistantMsgIndex]) {
              messages.value[assistantMsgIndex].content += textDelta
              scrollToBottom()
            }
          } catch (e) {
            console.error("Erro no parse SSE JSON", e, dataStr)
          }
        }
      }
    }
    
    if (assistantMsgIndex !== -1 && messages.value[assistantMsgIndex]) {
      messages.value[assistantMsgIndex].isStreaming = false
    }

  } catch (error) {
    console.error("Ocorreu um erro ao buscar:", error)
    if (assistantMsgId !== undefined) {
      const assistantMsgIndex = messages.value.findIndex(m => m.id === assistantMsgId)
      if (assistantMsgIndex !== -1 && messages.value[assistantMsgIndex]) {
        messages.value[assistantMsgIndex].content += '\n\n**Erro**: Não foi possível comunicar com o servidor. Garanta que a API FastAPI (`uvicorn src.api.main:app`) está em execução.'
        messages.value[assistantMsgIndex].isStreaming = false
      }
    }
  } finally {
    isThinking.value = false
  }
}

// Lógica para Edição e Reenvio
const editMessage = (msg: Message) => {
  inputMessage.value = msg.content
  nextTick(() => {
    document.querySelector('textarea')?.focus()
  })
}

const resendMessage = (msg: Message) => {
  inputMessage.value = msg.content
  sendMessage()
}

// Carregar Histórico Antigo
const loadSession = async (id: number) => {
  try {
    const res = await fetch(`${API_BASE_URL}/v1/sessions/${id}`, {
        headers: getAuthHeaders()
    })
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
  if (msg.role !== 'assistant' || !msg.id || msg.id === 0 || msg.isStreaming) return
  
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
    const res = await fetch(`${API_BASE_URL}/v1/feedback`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        ...getAuthHeaders()
      },
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
    if (file) await uploadFile(file)
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
    if (file) await uploadFile(file)
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
    const res = await fetch(`${API_BASE_URL}/v1/upload`, {
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
  <div v-if="authPhase === 'loading'" class="flex h-screen w-full bg-surface-900 items-center justify-center">
      <div class="text-white animate-pulse">Invocando o RAG...</div>
  </div>
  <Setup v-else-if="authPhase === 'setup'" @setup-complete="checkAuthStatus" />
  <Login v-else-if="authPhase === 'login'" @login-success="checkAuthStatus" />
  
  <div v-else class="flex h-screen w-full bg-surface-900 text-slate-200 overflow-hidden font-sans">
    
    <!-- Slim Navigation Bar (Gemini Style) -->
    <nav class="w-14 shrink-0 bg-surface-950 border-r border-slate-800 flex flex-col items-center py-4 z-20">
      <button @click="isSidebarOpen = !isSidebarOpen" class="p-2 text-slate-400 hover:text-slate-100 hover:bg-surface-800 rounded-lg transition-colors mb-6" title="Menu principal">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
      </button>

      <button @click="() => { currentSessionId = null; messages = [{ id: 1, role: 'assistant', content: 'Nova conversa iniciada. Como posso ajudar?' }]; }" class="p-2 text-slate-400 hover:text-sky-400 hover:bg-surface-800 rounded-lg transition-colors" title="Nova Conversa">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
      </button>

      <div class="flex-1"></div>

      <button @click="openConfigModal" class="p-2 text-slate-400 hover:text-slate-100 hover:bg-surface-800 rounded-lg transition-colors mb-2" title="Engine Settings">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
      </button>
    </nav>

    <!-- Sidebar / Navigation -->
    <aside 
      v-show="isSidebarOpen"
      class="bg-surface-800 border-r border-slate-700/50 flex flex-col shrink-0 relative"
      :class="{'transition-all duration-300': !isDraggingSidebar}"
      :style="{ width: sidebarWidth + 'px' }"
    >
      <div class="p-4 flex items-center gap-3 border-b border-slate-700/50 shine-effect">
        <div class="w-8 h-8 rounded bg-gradient-to-tr from-primary-600 to-primary-400 flex items-center justify-center shadow-lg shadow-primary-500/20">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"></path></svg>
        </div>
        <div>
          <h1 class="font-bold text-slate-100 tracking-tight">Sovereign Pair</h1>
          <p class="text-xs text-sky-400 font-medium">Local-first RAG Engine</p>
        </div>
      </div>
      
      <div class="flex-1 overflow-y-auto p-3 space-y-1">
        <!-- Removed Nova Conversa from here to Slim Navbar -->

        <div class="mb-3">
          <div class="relative">
            <input 
              v-model="searchQuery" 
              type="text" 
              placeholder="Buscar chats ou #tags..." 
              class="w-full bg-surface-900 border border-slate-700/50 rounded-md py-1.5 pl-8 pr-3 text-xs text-slate-200 focus:outline-none focus:border-sky-500/50 transition-all placeholder-slate-500"
            />
            <svg class="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
          </div>
        </div>

        <div class="text-[10px] uppercase font-bold text-slate-500 mb-2 px-2 tracking-wider">Histórico de Sessões</div>
        
        <div class="space-y-4">
          <!-- Pastas com nome -->
          <div v-for="(sessList, folderName) in groupedSessions" :key="'folder-'+folderName">
             <template v-if="folderName !== '' && sessList.length > 0">
                 <button @click="toggleFolder(folderName as string)" class="w-full flex items-center justify-between px-2 py-1.5 text-xs font-semibold text-slate-400 hover:text-slate-200 transition-colors uppercase tracking-wider mb-1">
                   <div class="flex items-center gap-2">
                     <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"></path></svg>
                     {{ folderName }}
                   </div>
                   <svg :class="{'rotate-180': expandedFolders[folderName as string]}" class="w-3 h-3 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
                 </button>
                 
                 <div v-show="expandedFolders[folderName as string]" class="space-y-1 pl-3 border-l-2 border-slate-700/50 ml-3 mb-2">
                    <div 
                      v-for="session in sessList" 
                      :key="session.id"
                      class="group flex items-center gap-1"
                    >
                      <button
                        @click="loadSession(session.id)"
                        :class="['w-full text-left px-3 py-1.5 rounded-md text-sm transition-colors border flex items-center justify-between', 
                                 currentSessionId === session.id 
                                  ? 'bg-surface-700 text-sky-300 border-sky-500/50 shadow-[0_0_10px_rgba(14,165,233,0.1)]' 
                                  : 'bg-transparent text-slate-400 hover:bg-surface-700/50 border-transparent']"
                      >
                        <span class="truncate block flex-1 pr-2">{{ session.title }}</span>
                        <div @click.stop="sessionToDelete = session.id" class="p-1 text-slate-500 hover:text-rose-400 opacity-0 group-hover:opacity-100 transition-all rounded hover:bg-surface-600 shrink-0" title="Deletar">
                          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                        </div>
                      </button>
                    </div>
                 </div>
             </template>
          </div>
          
          <!-- Sessões Raiz -->
          <div class="space-y-1">
             <div 
                v-for="session in groupedSessions['']" 
                :key="session.id"
                class="group flex items-center gap-1"
              >
                <button
                  @click="loadSession(session.id)"
                  :class="['w-full text-left px-3 py-2 rounded-md text-sm transition-colors flex flex-col gap-1 border', 
                           currentSessionId === session.id 
                            ? 'bg-surface-700 text-sky-300 border-sky-500/50 shadow-[0_0_10px_rgba(14,165,233,0.1)]' 
                            : 'bg-surface-700/30 text-slate-300 hover:bg-surface-700/80 border-slate-700/50']"
                >
                  <div class="flex items-center gap-2 w-full justify-between">
                     <div class="flex items-center gap-2 min-w-0 pr-1 truncate flex-1">
                       <svg class="w-4 h-4 shrink-0" :class="currentSessionId === session.id ? 'text-sky-400' : 'text-slate-500'" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path></svg>
                       <span class="truncate">{{ session.title }}</span>
                     </div>
                     <div @click.stop="sessionToDelete = session.id" class="p-1 text-slate-500 hover:text-rose-400 opacity-0 group-hover:opacity-100 transition-all rounded hover:bg-surface-600 shrink-0" title="Deletar">
                       <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                     </div>
                  </div>
                </button>
              </div>
          </div>
        </div>
        
        <div v-if="sessions.length === 0" class="text-xs text-slate-500 italic px-3 py-2 text-center">
          Nenhuma conversa salva
        </div>
      </div>
      
      <!-- Removed Engine Settings from here to Slim Navbar -->
      <!-- Resizer Handle -->
      <div 
        class="absolute right-0 top-0 bottom-0 w-1.5 cursor-col-resize hover:bg-sky-500/50 z-10 transition-colors translate-x-1/2"
        :class="{'bg-sky-500': isDraggingSidebar}"
        @mousedown="startDragSidebar"
      ></div>
    </aside>

    <!-- Main Chat Area -->
    <main 
      class="flex-1 flex flex-col h-full bg-surface-900 shadow-[-10px_0_30px_rgba(0,0,0,0.5)] z-10 relative"
      @dragover.prevent="handleDragOver" 
      @dragleave.prevent="handleDragLeave" 
      @drop.prevent="handleDrop"
    >
      
      <!-- Drag Overlay -->
      <div v-if="isDragging" class="absolute inset-x-2 inset-y-2 z-50 bg-surface-900/90 backdrop-blur-md border-2 border-dashed border-primary-500 rounded-xl flex items-center justify-center transition-all">
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
        <div class="bg-surface-800 border border-surface-700 p-6 rounded-2xl max-w-md w-full shadow-2xl animate-scale-in">
          <div class="flex items-center gap-3 mb-4 text-amber-400">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
            <h3 class="text-lg font-bold text-slate-100">Colisão de Arquivo</h3>
          </div>
          <p class="text-slate-300 text-sm mb-6 leading-relaxed">{{ conflictFile.message }}</p>
          <div class="flex gap-3 justify-end flex-wrap mt-2">
             <button @click="resolveConflict('cancel')" class="px-3 py-2 rounded-lg bg-surface-700 text-slate-300 hover:bg-surface-600 transition-colors text-sm font-medium">Cancelar</button>
             <button @click="resolveConflict('rename')" class="px-3 py-2 rounded-lg bg-emerald-500/20 border border-emerald-500/50 text-emerald-300 hover:bg-emerald-500/30 transition-colors text-sm font-medium shadow-[0_0_15px_rgba(16,185,129,0.2)]">Renomear Novo</button>
             <button @click="resolveConflict('overwrite')" class="px-3 py-2 rounded-lg bg-amber-500/20 border border-amber-500/50 text-amber-300 hover:bg-amber-500/30 transition-colors text-sm font-medium shadow-[0_0_15px_rgba(245,158,11,0.2)]">Sobrescrever Vetores</button>
          </div>
        </div>
      </div>
      
      <!-- Top header for mobile / status -->
      <header class="h-14 border-b border-surface-800 flex items-center px-4 justify-between shrink-0 bg-surface-900/80 backdrop-blur-md">
        <div class="flex items-center gap-3">
          <h2 class="font-medium text-slate-300 truncate max-w-[200px] md:max-w-md">
             {{ activeSession ? activeSession.title : 'Sovereign Pair' }}
          </h2>
          <button v-if="activeSession" @click="openEditSessionModal(activeSession as any)" class="p-1.5 text-slate-400 hover:text-sky-400 hover:bg-surface-700 rounded-md transition-colors" title="Editar Sessão">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path></svg>
          </button>
        </div>
        <button @click="openConfigModal" class="flex items-center gap-2 px-2 py-1 rounded-md hover:bg-surface-700/50 transition-colors cursor-pointer group" title="Abrir Configurações do Motor">
          <span class="flex h-2 w-2 relative">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <span class="text-xs font-medium text-slate-400 group-hover:text-sky-300 transition-colors">Motor Pronto</span>
        </button>
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
            <div v-if="msg.role === 'assistant'" class="w-8 h-8 md:w-10 md:h-10 rounded-full flex items-center justify-center shadow-lg transition-all" :class="systemSettings.persona_graphic_style === 'dots' ? 'bg-primary-500/10 border border-primary-500/20' : 'bg-gradient-to-br from-primary-600 to-primary-400 shadow-primary-500/20 p-1.5'">
              <span v-if="systemSettings.persona_graphic_style === 'emoji'" class="text-xl md:text-2xl leading-none drop-shadow-sm">{{ personaOptions.find(p => p.id === systemSettings.persona)?.icon || '🧠' }}</span>
              <svg v-else-if="systemSettings.persona_graphic_style === 'vector'" class="w-5 h-5 md:w-6 md:h-6 text-white drop-shadow-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="11.5" r="11" class="opacity-40" stroke="currentColor" fill="none" />
                <path d="M12 4.5l-3 3v4l3 3 3-3v-4l-3-3zM9 7.5H5.5l1 3 2.5 2M15 7.5h3.5l-1 3-2.5 2M12 4.5V2M12 14.5v5M9 12.5l-2.5 3M15 12.5l2.5 3" />
                <circle cx="12" cy="4.5" r="1.5" fill="currentColor" stroke="none"/><circle cx="9" cy="7.5" r="1.5" fill="currentColor" stroke="none"/><circle cx="15" cy="7.5" r="1.5" fill="currentColor" stroke="none"/><circle cx="9" cy="12.5" r="1.5" fill="currentColor" stroke="none"/><circle cx="15" cy="12.5" r="1.5" fill="currentColor" stroke="none"/><circle cx="12" cy="14.5" r="1.5" fill="currentColor" stroke="none"/>
                <circle cx="5.5" cy="7.5" r="1" fill="currentColor" stroke="none"/><circle cx="18.5" cy="7.5" r="1" fill="currentColor" stroke="none"/><circle cx="6.5" cy="10.5" r="1" fill="currentColor" stroke="none"/><circle cx="17.5" cy="10.5" r="1" fill="currentColor" stroke="none"/><circle cx="6.5" cy="15.5" r="1" fill="currentColor" stroke="none"/><circle cx="17.5" cy="15.5" r="1" fill="currentColor" stroke="none"/><circle cx="12" cy="19.5" r="1" fill="currentColor" stroke="none"/>
              </svg>
              <div v-else class="w-2 h-2 md:w-3 md:h-3 rounded-full bg-primary-500 shadow-[0_0_8px_rgba(var(--color-primary-500),0.7)]"></div>
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
              :class="msg.role === 'user' ? 'bg-surface-700 text-slate-100 rounded-tr-sm' : 'bg-transparent prose prose-invert w-full max-w-none'"
            >
              <template v-if="msg.role === 'user'">
                {{ msg.content }}
              </template>
              <template v-else>
                <div v-safe-html="md.render(msg.content)"></div>
                <span v-if="msg.isStreaming" class="w-2 h-4 bg-sky-400 inline-block animate-pulse ml-1 vertical-align-middle"></span>
              </template>
            </div>
            
            <!-- Botões para mensagens do usuário -->
            <div v-if="msg.role === 'user'" class="mt-2 flex items-center justify-end gap-3 px-2 text-slate-500 opacity-0 group-hover:opacity-100 transition-opacity">
              <button @click="editMessage(msg)" title="Recuperar texto para editar" class="hover:text-amber-400">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path></svg>
              </button>
              <button @click="resendMessage(msg)" title="Reenviar exata mensagem" class="hover:text-sky-400">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
              </button>
            </div>

            <!-- Botões para mensagens da assistente -->
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
        <div class="relative flex items-center bg-surface-800 rounded-2xl border border-surface-700 shadow-xl focus-within:ring-1 focus-within:ring-primary-500/50 focus-within:border-primary-500/50 transition-all">
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
        <div class="bg-surface-900 border border-surface-700/50 rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden flex flex-col max-h-[90vh]">
          
          <!-- Header -->
          <div class="px-6 py-4 border-b border-surface-700/50 flex justify-between items-center bg-surface-800/50">
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
                <select v-model="systemSettings.llm_provider" class="w-full bg-surface-800 border border-surface-700 text-slate-200 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block p-2.5 outline-none transition-all">
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
                  <select v-else v-model="systemSettings.llm_model" class="w-full bg-surface-800 border border-surface-700 text-slate-200 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block p-2.5 outline-none transition-all">
                    <option v-for="mod in localModels" :key="mod" :value="mod">{{ mod }}</option>
                    <option v-if="localModels.length === 0" value="llama3.2" disabled>Nenhum modelo encontrado</option>
                  </select>
                </template>
                <template v-else>
                  <input v-model="systemSettings.llm_model" type="text" class="w-full bg-surface-800 border border-surface-700 text-slate-200 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block p-2.5 outline-none transition-all" placeholder="ex: llama3, gpt-4o">
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

            <div class="space-y-4">
              <label class="block text-sm font-medium text-slate-400 mb-2">Comportamento da IA (Persona)</label>
              
              <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2 mb-3">
                <button 
                  v-for="p in personaOptions" 
                  :key="p.id"
                  @click="selectPersona(p)"
                  class="flex items-start gap-2 p-2.5 rounded-lg border transition-all text-left group"
                  :class="systemSettings.persona === p.id ? 'bg-primary-500/10 border-primary-500 text-primary-300 ring-1 ring-primary-500/50' : 'bg-surface-800 border-surface-700 text-slate-400 hover:border-surface-600 hover:text-slate-300'"
                >
                  <svg v-if="systemSettings.persona_graphic_style === 'vector'" class="w-7 h-7 shrink-0 text-primary-400 opacity-90 transition-all group-hover:scale-105" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="11.5" r="11" class="opacity-40" stroke="currentColor" fill="none" />
                    <path d="M12 4.5l-3 3v4l3 3 3-3v-4l-3-3zM9 7.5H5.5l1 3 2.5 2M15 7.5h3.5l-1 3-2.5 2M12 4.5V2M12 14.5v5M9 12.5l-2.5 3M15 12.5l2.5 3" />
                    <circle cx="12" cy="4.5" r="1.5" fill="currentColor" stroke="none"/>
                    <circle cx="9" cy="7.5" r="1.5" fill="currentColor" stroke="none"/>
                    <circle cx="15" cy="7.5" r="1.5" fill="currentColor" stroke="none"/>
                    <circle cx="9" cy="12.5" r="1.5" fill="currentColor" stroke="none"/>
                    <circle cx="15" cy="12.5" r="1.5" fill="currentColor" stroke="none"/>
                    <circle cx="12" cy="14.5" r="1.5" fill="currentColor" stroke="none"/>
                    <circle cx="5.5" cy="7.5" r="1" fill="currentColor" stroke="none"/>
                    <circle cx="18.5" cy="7.5" r="1" fill="currentColor" stroke="none"/>
                    <circle cx="6.5" cy="10.5" r="1" fill="currentColor" stroke="none"/>
                    <circle cx="17.5" cy="10.5" r="1" fill="currentColor" stroke="none"/>
                    <circle cx="6.5" cy="15.5" r="1" fill="currentColor" stroke="none"/>
                    <circle cx="17.5" cy="15.5" r="1" fill="currentColor" stroke="none"/>
                    <circle cx="12" cy="19.5" r="1" fill="currentColor" stroke="none"/>
                  </svg>
                  <div v-else-if="systemSettings.persona_graphic_style === 'dots'" class="w-2.5 h-2.5 shrink-0 rounded-full bg-primary-500 shadow-sm mt-1 shadow-primary-500/50"></div>
                  <span v-else class="text-xl shrink-0 mt-0.5">{{ p.icon }}</span>
                  <div class="flex flex-col min-w-0">
                     <span class="text-xs font-semibold leading-tight truncate group-hover:text-primary-300">{{ p.name }}</span>
                     <span class="text-[9px] text-slate-500 line-clamp-2 mt-1 leading-tight">{{ p.prompt }}</span>
                  </div>
                </button>
              </div>

              <textarea 
                v-model="systemSettings.system_prompt" 
                rows="4" 
                @input="systemSettings.persona = 'custom'"
                class="w-full bg-surface-800 border border-surface-700 text-slate-200 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block p-3 outline-none transition-all resize-none font-mono text-[13px] leading-relaxed" 
                placeholder="Como o assistente deve se comportar..."></textarea>
                
                <div class="space-y-2 mt-4">
                  <label class="block text-sm font-medium text-slate-400">Tratamento e Formalidade</label>
                  <div class="flex p-1 bg-surface-800 rounded-lg border border-surface-700 max-w-sm">
                    <button @click="systemSettings.formality = 'feminine'" :class="systemSettings.formality === 'feminine' ? 'bg-primary-500/20 text-primary-400 font-medium shadow-sm' : 'text-slate-400 hover:text-slate-300'" class="flex-1 py-2 text-xs rounded-md transition-colors">Assistente ♀️</button>
                    <button @click="systemSettings.formality = 'neutral'" :class="systemSettings.formality === 'neutral' ? 'bg-primary-500/20 text-primary-400 font-medium shadow-sm' : 'text-slate-400 hover:text-slate-300'" class="flex-1 py-2 text-xs rounded-md transition-colors">Neutro 🤖</button>
                    <button @click="systemSettings.formality = 'masculine'" :class="systemSettings.formality === 'masculine' ? 'bg-primary-500/20 text-primary-400 font-medium shadow-sm' : 'text-slate-400 hover:text-slate-300'" class="flex-1 py-2 text-xs rounded-md transition-colors">Assistente ♂️</button>
                  </div>
                </div>

                <div class="space-y-4 pt-4 border-t border-surface-700/50">
                  <div class="space-y-2">
                    <label class="block text-sm font-medium text-slate-400">Nome / Como te chamar?</label>
                    <input v-model="systemSettings.nickname" type="text" class="w-full bg-surface-800 border border-surface-700 text-slate-200 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block p-2.5 outline-none transition-all" placeholder="Seu apelido/nome preferido">
                  </div>
                  <div class="space-y-2">
                    <label class="block text-sm font-medium text-slate-400">Ocupação / Atuação</label>
                    <input v-model="systemSettings.occupation" type="text" class="w-full bg-surface-800 border border-surface-700 text-slate-200 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block p-2.5 outline-none transition-all" placeholder="Ex: Dev Backend Pleno">
                  </div>
                  <div class="space-y-2">
                    <label class="block text-sm font-medium text-slate-400">Mais sobre você</label>
                    <textarea v-model="systemSettings.about_user" class="w-full bg-surface-800 border border-surface-700 text-slate-200 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block p-2.5 outline-none transition-all resize-y min-h-[80px]" placeholder="Gosto de explicações curtas em bullet points..."></textarea>
                  </div>
                  <div class="grid grid-cols-2 gap-4">
                    <div class="space-y-2">
                      <label class="block text-sm font-medium text-slate-400">Idioma da IA</label>
                      <select v-model="systemSettings.language" class="w-full bg-surface-800 border border-surface-700 text-slate-200 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block p-2.5 outline-none transition-all">
                        <option value="Português do Brasil">Português do Brasil</option>
                        <option value="Português (Carioca)">🇧🇷 Português (Carioca)</option>
                        <option value="Português (Paulistano)">🇧🇷 Português (Paulistano)</option>
                        <option value="Português (Mineiro)">🇧🇷 Português (Mineiro)</option>
                        <option value="Português (Nordestino)">🇧🇷 Português (Nordestino)</option>
                        <option value="Português de Portugal">🇵🇹 Português de Portugal</option>
                        <option value="Inglês (EUA)">🇺🇸 Inglês Americano</option>
                        <option value="Espanhol">🇪🇸 Espanhol</option>
                      </select>
                    </div>
                    <div class="space-y-2">
                      <label class="block text-sm font-medium text-slate-400">Geolocalização</label>
                      <input v-model="systemSettings.geolocation" type="text" class="w-full bg-surface-800 border border-surface-700 text-slate-200 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block p-2.5 outline-none transition-all" placeholder="ex: SP, Brasil" title="Permite contexto local para clima ou cultura">
                    </div>
                  </div>
                </div>
              </div>
            
            <!-- Graphic Style -->
            <div class="space-y-3 mt-4">
              <label class="block text-sm font-medium text-slate-400">Estilo Visual das Personas</label>
              <div class="flex p-1 bg-surface-800 rounded-lg border border-surface-700 w-full max-w-sm">
                <button @click="systemSettings.persona_graphic_style = 'emoji'" :class="systemSettings.persona_graphic_style === 'emoji' ? 'bg-primary-500/20 text-primary-400 font-medium shadow-sm' : 'text-slate-400 hover:text-surface-300'" class="flex-1 py-1.5 text-xs rounded-md transition-colors flex items-center justify-center gap-1.5"><span>🧠</span> Emojis</button>
                <button @click="systemSettings.persona_graphic_style = 'vector'" :class="systemSettings.persona_graphic_style === 'vector' ? 'bg-primary-500/20 text-primary-400 font-medium shadow-sm' : 'text-slate-400 hover:text-surface-300'" class="flex-1 py-1.5 text-xs rounded-md transition-colors flex items-center justify-center gap-1.5">
                  <svg class="w-4 h-4 shrink-0 transition-all opacity-80" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="11.5" r="11" class="opacity-40" stroke="currentColor" fill="none" />
                    <path d="M12 4.5l-3 3v4l3 3 3-3v-4l-3-3zM9 7.5H5.5l1 3 2.5 2M15 7.5h3.5l-1 3-2.5 2M12 4.5V2M12 14.5v5M9 12.5l-2.5 3M15 12.5l2.5 3" />
                    <circle cx="12" cy="4.5" r="1.5" fill="currentColor" stroke="none"/>
                    <circle cx="9" cy="7.5" r="1.5" fill="currentColor" stroke="none"/>
                    <circle cx="15" cy="7.5" r="1.5" fill="currentColor" stroke="none"/>
                    <circle cx="9" cy="12.5" r="1.5" fill="currentColor" stroke="none"/>
                    <circle cx="15" cy="12.5" r="1.5" fill="currentColor" stroke="none"/>
                    <circle cx="12" cy="14.5" r="1.5" fill="currentColor" stroke="none"/>
                  </svg> Cérebro Virtual
                </button>
                <button @click="systemSettings.persona_graphic_style = 'dots'" :class="systemSettings.persona_graphic_style === 'dots' ? 'bg-primary-500/20 text-primary-400 font-medium shadow-sm' : 'text-slate-400 hover:text-surface-300'" class="flex-1 py-1.5 text-xs rounded-md transition-colors flex items-center justify-center gap-1.5">
                  <div class="w-1.5 h-1.5 rounded-full bg-current"></div> Minimal
                </button>
              </div>
            </div>

            <!-- Theme selector -->
            <div class="space-y-3">
              <label class="block text-sm font-medium text-slate-400">Aparência da Interface</label>
              <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
                <button 
                  v-for="themeOp in [
                    { id: 'slate', name: 'Slate', color: 'bg-slate-800', border: 'border-slate-600' },
                    { id: 'ocean', name: 'Ocean', color: 'bg-cyan-900', border: 'border-cyan-700' },
                    { id: 'forest', name: 'Forest', color: 'bg-emerald-900', border: 'border-emerald-700' },
                    { id: 'hacker', name: 'Hacker', color: 'bg-black', border: 'border-green-500' },
                    { id: 'rose', name: 'Rose', color: 'bg-rose-900', border: 'border-rose-700' },
                    { id: 'amber', name: 'Amber', color: 'bg-orange-900', border: 'border-orange-700' },
                    { id: 'purple', name: 'Purple', color: 'bg-purple-900', border: 'border-purple-700' },
                    { id: 'light', name: 'Light', color: 'bg-white', border: 'border-slate-300' }
                  ]" 
                  :key="themeOp.id"
                  @click="systemSettings.theme = themeOp.id"
                  class="flex items-center justify-center p-2 rounded-xl border-2 transition-all relative overflow-hidden group"
                  :class="systemSettings.theme === themeOp.id ? 'border-primary-500 ring-2 ring-primary-500/20' : 'border-surface-700 hover:border-surface-600'"
                >
                  <div class="flex items-center gap-2 relative z-10 w-full justify-center">
                    <div class="w-4 h-4 rounded-full border shadow-sm shrink-0" :class="[themeOp.color, themeOp.border]"></div>
                    <span class="text-xs font-medium text-slate-300 truncate group-hover:text-white transition-colors">{{ themeOp.name }}</span>
                  </div>
                  <div class="absolute inset-x-0 bottom-0 h-1/2 opacity-10 pointer-events-none" :class="themeOp.color"></div>
                </button>
              </div>
            </div>

            <!-- Auth Token Viewer -->
            <div class="space-y-2 border-t border-slate-700/50 pt-4">
              <label class="block text-sm font-medium text-slate-400">Sovereign Token (API Key)</label>
              <div class="relative flex items-center bg-surface-800 border border-surface-700 rounded-lg overflow-hidden transition-all focus-within:ring-1 focus-within:ring-primary-500 focus-within:border-primary-500">
                <input 
                  :type="isTokenVisible ? 'text' : 'password'" 
                  readonly
                  :value="authTokenForDisplay"
                  class="w-full bg-transparent text-slate-200 text-sm block p-2.5 outline-none font-mono" 
                >
                <button 
                  @click="isTokenVisible = !isTokenVisible" 
                  class="px-3 text-slate-400 hover:text-sky-400 transition-colors"
                  :title="isTokenVisible ? 'Ocultar Token' : 'Mostrar Token'"
                >
                  <svg v-if="!isTokenVisible" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path></svg>
                  <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"></path></svg>
                </button>
              </div>
              <p class="text-[11px] text-slate-500">Cole este token nas configurações do seu plugin Sovereign Pair no Obsidian.</p>
            </div>

          </div>

          <!-- Footer -->
          <div class="px-6 py-4 border-t border-surface-700/50 bg-surface-800/30 flex justify-end gap-3">
            <button @click="isConfigModalOpen = false" class="px-4 py-2 text-sm text-slate-300 hover:text-white transition-colors">Cancelar</button>
            <button @click="saveConfig" :disabled="isLoadingConfig" class="px-5 py-2 text-sm bg-primary-500 hover:bg-primary-400 text-white rounded-lg font-medium transition-colors shadow-lg shadow-primary-500/30 disabled:opacity-50 flex items-center gap-2">
              <svg v-if="isLoadingConfig" class="w-4 h-4 animate-spin flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
              {{ isLoadingConfig ? 'Salvando...' : 'Salvar no Banco' }}
            </button>
          </div>
          
        </div>
      </div>

      <!-- Edit Session Modal -->
      <div v-if="isEditSessionModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
        <div class="bg-surface-900 border border-surface-700/50 rounded-2xl shadow-2xl w-full max-w-sm overflow-hidden flex flex-col">
          <div class="px-6 py-4 border-b border-surface-700/50 flex justify-between items-center bg-surface-800/50">
            <h3 class="text-lg font-medium text-slate-200">Editar Sessão</h3>
            <button @click="isEditSessionModalOpen = false" class="text-slate-400 hover:text-white transition-colors">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
            </button>
          </div>
          <div class="p-6 space-y-4">
            <div class="space-y-2">
              <label class="block text-sm font-medium text-slate-400">Título</label>
              <input v-model="editingSession.title" type="text" class="w-full bg-surface-800 border border-surface-700 text-slate-200 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block p-2.5 outline-none transition-all">
            </div>
            <div class="space-y-2">
              <label class="block text-sm font-medium text-slate-400">Pasta (Opcional)</label>
              <input v-model="editingSession.folder_name" type="text" placeholder="Nome da pasta" class="w-full bg-surface-800 border border-surface-700 text-slate-200 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block p-2.5 outline-none transition-all">
            </div>

            <div class="space-y-2 pt-2 border-t border-surface-700/50">
              <label class="block text-sm font-medium text-slate-400">Tags / Categorias (Pressione Enter para adicionar)</label>
              <div class="flex flex-wrap gap-2 mb-2">
                <span v-for="(tag, idx) in editingSession.tags" :key="idx" class="px-2 py-1 bg-surface-700 border border-surface-600 text-xs text-slate-300 rounded-md flex items-center gap-1">
                  #{{ tag }}
                  <button @click="removeTag(idx)" class="hover:text-rose-400 ml-1 transition-colors">
                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                  </button>
                </span>
                <span v-if="editingSession.tags.length === 0" class="text-xs text-slate-500 italic block">Nenhuma tag...</span>
              </div>
              <input 
                v-model="editingTagsInput"
                @keydown.enter.prevent="addTag"
                type="text" 
                placeholder="Ex: python, pesquisa, ideia... (Aperte Enter)" 
                class="w-full bg-surface-800 border border-surface-700 text-slate-200 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block p-2.5 outline-none transition-all"
              >
            </div>
          </div>
          <div class="px-6 py-4 border-t border-surface-700/50 bg-surface-800/30 flex justify-end gap-3">
            <button @click="isEditSessionModalOpen = false" class="px-4 py-2 text-sm text-slate-300 hover:text-white transition-colors">Cancelar</button>
            <button @click="saveSessionEdit" class="px-5 py-2 text-sm bg-primary-500 hover:bg-primary-400 text-white rounded-lg font-medium transition-colors shadow-lg shadow-primary-500/30">Salvar</button>
          </div>
        </div>
      </div>

    <!-- Confirm Delete Modal -->
      <div v-if="sessionToDelete !== null" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
        <div class="bg-surface-900 border border-rose-900/50 rounded-2xl shadow-2xl w-full max-w-sm overflow-hidden flex flex-col animate-scale-in">
          <div class="px-6 py-4 border-b border-surface-700/50 flex items-center gap-3 bg-rose-500/10">
            <svg class="w-6 h-6 text-rose-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
            <h3 class="text-lg font-medium text-rose-500">Excluir Sessão</h3>
          </div>
          <div class="p-6">
            <p class="text-slate-300 text-sm">Tem certeza que deseja apagar esta sessão e todo o seu histórico de mensagens permanentemente?</p>
            <p class="text-rose-400 text-xs mt-2 font-medium">Esta ação não pode ser desfeita.</p>
          </div>
          <div class="px-6 py-4 border-t border-surface-700/50 bg-surface-800/30 flex justify-end gap-3">
            <button @click="sessionToDelete = null" class="px-4 py-2 text-sm text-slate-300 hover:text-white transition-colors">Cancelar</button>
            <button @click="deleteSessionConfirmed" class="px-5 py-2 text-sm bg-rose-600 hover:bg-rose-500 text-white rounded-lg font-medium transition-colors shadow-lg shadow-rose-900/50">Sim, excluir</button>
          </div>
        </div>
      </div>

    </main>
  </div>
</template>

<style scoped>
/* Optional: Adding some custom gradient animations if needed */
</style>
