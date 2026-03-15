<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import MarkdownIt from 'markdown-it'
import DOMPurify from 'dompurify'

// Custom directive to securely render HTML, bypassing the need for unsafe `v-html`
const vSafeHtml = {
  mounted(el: HTMLElement, binding: import('vue').DirectiveBinding) {
    el.innerHTML = DOMPurify.sanitize(binding.value, { ADD_TAGS: ['svg', 'path', 'circle', 'line', 'g', 'rect', 'span', 'div'] })
  },
  updated(el: HTMLElement, binding: import('vue').DirectiveBinding) {
    el.innerHTML = DOMPurify.sanitize(binding.value, { ADD_TAGS: ['svg', 'path', 'circle', 'line', 'g', 'rect', 'span', 'div'] })
  }
}

const formatMessageIcons = (content: string) => {
  // Converte blocos Markdown de "thinking" para tags HTML elegantes (Details/Summary)
  // Expressão Regular captura o bloco inteiro: ```thinking\n ... \n```
  let formatted = content.replace(/```thinking\n([\s\S]*?)\n```/g, (_, innerText) => {
     return `<details class="cognitive-details group my-4 rounded-xl border border-primary-500/20 bg-surface-800/50 shadow-lg overflow-hidden transition-all duration-300">
        <summary class="flex justify-between items-center cursor-pointer p-3 bg-surface-800 hover:bg-surface-700/80 transition-colors select-none list-none text-xs font-semibold tracking-wider uppercase text-primary-400">
           <div class="flex items-center gap-2">
               <svg class="w-4 h-4 animate-pulse text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path></svg>
               <span>Processo Cognitivo do Engine</span>
           </div>
           <svg class="w-4 h-4 text-surface-400 group-open:rotate-180 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
        </summary>
        <div class="p-4 pt-3 border-t border-surface-700/50 text-[13px] leading-relaxed text-surface-300 font-mono opacity-80 whitespace-pre-wrap">${innerText}</div>
     </details>`;
  });
  return formatted;
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || `http://${typeof window !== 'undefined' ? window.location.hostname : 'localhost'}:8000`
const RUST_CORE_URL = import.meta.env.VITE_RUST_CORE_URL || `http://${typeof window !== 'undefined' ? window.location.hostname : 'localhost'}:8001`

const getAuthHeaders = (): Record<string, string> => {
   const token = localStorage.getItem('sovereign_token')
   return token ? { 'Authorization': `Bearer ${token}` } : {}
}

// Inicializar parser de markdown
const md = new MarkdownIt({
  html: true,
  breaks: true,
  linkify: true
})

interface ActionMeta {
  action: string
  status: 'running' | 'done' | 'error' | 'warning'
  provider?: string
  message?: string
  error?: string
}

interface ToolCall {
  index: number
  id: string
  type: string
  function: { name: string, arguments: string }
  result?: any
  status: 'running' | 'done' | 'error'
}

interface Message {
  id: number
  role: 'user' | 'assistant' | 'tool'
  content: string
  isStreaming?: boolean
  thumbs_up?: boolean
  thumbs_down?: boolean
  actions?: ActionMeta[]
  tool_calls?: ToolCall[]
  tool_call_id?: string
  name?: string
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
    const res = await fetch(`${RUST_CORE_URL}/v1/sessions/${sessionToDelete.value}`, {
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
    const res = await fetch(`${RUST_CORE_URL}/v1/sessions/${editingSession.value.id}`, {
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


const messages = ref<Message[]>([
  { id: 0, role: 'assistant', content: 'Olá! Sou seu Sovereign Pair RAG. Estou conectado ao modelo local protegido em seus diretórios.\n\nComo posso ajudar hoje?' }
])
import { systemState } from '../stores/system'

const isThinking = computed({
  get: () => systemState.isThinking,
  set: (val) => systemState.isThinking = val
})
const chatContainer = ref<HTMLElement | null>(null)
const currentAbortController = ref<AbortController | null>(null)

const cancelGeneration = () => {
  if (currentAbortController.value) {
    currentAbortController.value.abort("User Cancelled")
    currentAbortController.value = null
  }
}

// Recuperar Sessões do Backend
const loadSessions = async () => {
  try {
    const res = await fetch(`${RUST_CORE_URL}/v1/sessions`, {
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

const teleportReady = ref(false)

onMounted(() => {
  teleportReady.value = true
  loadSessions()
})

const scrollToBottom = async () => {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

// Conectar ao backend FastAPI usando SSE
const sendMessage = async (invokeSource: boolean | Event = false) => {
  const isRecursiveToolCall = typeof invokeSource === 'boolean' ? invokeSource : false;

  if (!isRecursiveToolCall) {
    if (!inputMessage.value.trim() || isThinking.value) return

    const userText = inputMessage.value
    inputMessage.value = ''
    
    messages.value.push({
      id: Date.now(),
      role: 'user',
      content: userText
    })
    scrollToBottom()
  }

  isThinking.value = true
  
  const assistantMsgId = Date.now() + 1
  messages.value.push({
    id: assistantMsgId,
    role: 'assistant',
    content: '',
    isStreaming: true,
    tool_calls: []
  })
  scrollToBottom()

  // Telemetry Reset
  tokenMetrics.value = {
     tokenCount: 0,
     startTime: performance.now(),
     tokensPerSecond: 0,
     isActive: true
  }

  try {
    currentAbortController.value = new AbortController()

    // 🚀 BYPASS CÍBRIDO: Redirecionar Inferência para o Core Rust (Fase 25)
    // Deixamos a 8000 para histórico (Python), mas o tráfego RAG quente flui pela 8001 (Rust)
    const HOST = typeof window !== 'undefined' ? window.location.hostname : 'localhost'
    
    // Convertemos o Histórico Atual da UI para a estrutura estrita OpenAI Role/Content/ToolCalls
    const rustMessages = messages.value
        .filter(m => (m.content || m.tool_calls || m.role === 'tool') && !m.isStreaming && !(m as any).isError)
        .map(m => {
           let msg: any = { role: m.role }
           if (m.content) msg.content = m.content
           if (m.tool_calls && m.tool_calls.length > 0) {
               msg.tool_calls = m.tool_calls.map(tc => ({ id: tc.id, type: tc.type, function: { name: tc.function.name, arguments: tc.function.arguments } }))
           }
           if (m.tool_call_id) msg.tool_call_id = m.tool_call_id
           if (m.name) msg.name = m.name
           return msg
        })

    const lastUserMsgContent = messages.value.filter(m => m.role === 'user').pop()?.content || '';
    const isSpecialCommand = lastUserMsgContent.trim().startsWith('/web') || lastUserMsgContent.trim().startsWith('/sys');
    
    // Se for comando /web ou /sys, bypassamos pro Python. Se não, RAG puro no Rust:
    const TARGET_URL = isSpecialCommand 
      ? `http://${HOST}:8000/v1/chat` 
      : `http://${HOST}:8001/v1/chat/completions`

    const payloadBody = isSpecialCommand 
      ? JSON.stringify({
          message: lastUserMsgContent,
          session_id: currentSessionId.value,
          stream: true
      })
      : JSON.stringify({
        model: 'gpt-4o', // Alias proxy para forçar o backend Rust Cíbrido a buscar a configuração em SQLite
        messages: rustMessages,
        tools: [
          {
            type: "function",
            function: {
              name: "read_vault_file",
              description: "Lê o conteúdo de um arquivo restrito do Cofre (Vault). Use para extrair e entender arquivos brutos no disco baseado no nome/path.",
              parameters: {
                type: "object",
                properties: {
                  workspace_id: { type: "string", description: "O ID Absoluto (Numero) retornado no Workspace Tree Context." },
                  relative_path: { type: "string", description: "O caminho local exato do arquivo requisitado para leitura. (ex: 'src/main.rs')" }
                },
                required: ["workspace_id", "relative_path"]
              }
            }
          },
          {
            type: "function",
            function: {
               name: "create_kanban_task",
               description: "Registra nativamente uma nova tarefa no O.S Task Board.",
               parameters: {
                 type: "object",
                 properties: {
                   project_id: { type: "string", description: "ID Numérico do Projeto alvo que receberá a Task." },
                   title: { type: "string", description: "Título curto da Task a ser cumprida." },
                   description: { type: "string", description: "Briefing contextual em rich text ou markdown da tarefa técnica." },
                   priority: { type: "string", enum: ["Low", "Med", "High"], description: "Prioridade Sistêmica" }
                 },
                 required: ["project_id", "title"]
               }
            }
          }
        ],
        stream: true
      })

    const response = await fetch(TARGET_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders()
      },
      body: payloadBody,
      signal: currentAbortController.value.signal
    })

    if (!response.ok) {
        let errText = '';
        try { errText = await response.text() } catch(e) {}
        
        let assistantMsgIndex = messages.value.findIndex(m => m.id === assistantMsgId)
        if (assistantMsgIndex !== -1) {
             messages.value.splice(assistantMsgIndex, 1);
        }
        
        messages.value.push({
           id: Date.now(),
           role: 'assistant',
           content: `⚠️ **Falha Crítica Cíbrida (Cognitive Engine Inalcançável)**\nO motor LLM recusou a inferência (HTTP ${response.status}).\n\n\`\`\`text\n${errText}\n\`\`\`\n> *A sua mensagem permaneceu no histórico para que você possa tentar novamente após alinhar os nós!*`,
           isStreaming: false,
           isError: true
        } as any);
        scrollToBottom();
        return;
    }

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
             continue
          }
          
          try {
            const data = JSON.parse(dataStr)
            
            // 🦀 RUST SSE PARSER (OpenAI Format)
            let textDelta = null
            
            // Suporte para o Formato OpenAI injetado pelo sovereign-core Rust
            if (data.choices && data.choices.length > 0 && data.choices[0].delta) {
                 textDelta = data.choices[0].delta.content
                 
                 // Intercept Agentic Function Calls (Tool Calls)
                 if (data.choices[0].delta.tool_calls) {
                     const assistantMsg = messages.value[assistantMsgIndex]
                     if (assistantMsg) {
                         if (!assistantMsg.tool_calls) assistantMsg.tool_calls = []
                         
                         for (const tCall of data.choices[0].delta.tool_calls) {
                             let existing = assistantMsg.tool_calls.find(tc => tc.index === tCall.index)
                             if (!existing) {
                                 // Inicializa a call! A ID pode vir apenas no primeiro chunk!
                                 existing = { index: tCall.index, id: tCall.id || `call_${Date.now()}_${tCall.index}`, type: "function", function: { name: tCall.function?.name || "", arguments: "" }, result: null, status: 'running' }
                                 assistantMsg.tool_calls.push(existing)
                             }
                             if (tCall.function?.name && !existing.function.name) {
                                  existing.function.name = tCall.function.name;
                             }
                             if (tCall.function?.arguments) {
                                 existing.function.arguments += tCall.function.arguments
                             }
                         }
                         scrollToBottom()
                     }
                 }
                 
                 // Handle Finish Reason Stop do Rust
                 if (data.choices[0].finish_reason === 'stop') {
                     continue
                 }
                 
                 if (data.choices[0].finish_reason === 'tool_calls') {
                     // Flag that streaming is done for tools
                 }
            } else if (data.content || data.token) {
                 // Formato Legado LlamaIndex (Fallback)
                 textDelta = data.content || data.token
            }
            
            // Tratamento das Actions Cíbridas Legadas Python (Bypass)
            if (data.action) {
               const assistantMsg = messages.value[assistantMsgIndex]
               if (assistantMsg) {
                   if (!assistantMsg.actions) {
                       assistantMsg.actions = []
                   }
                   const msgActions = assistantMsg.actions
                   const existingIdx = msgActions.findIndex((a: any) => a.action === data.action)
                   if (existingIdx >= 0) {
                       msgActions[existingIdx] = data
                   } else {
                       msgActions.push(data)
                   }
                   scrollToBottom()
               }
               continue
            }

            if (textDelta && messages.value[assistantMsgIndex]) {
              messages.value[assistantMsgIndex].content += textDelta
              
              // Telemetry Update
              if (tokenMetrics.value && typeof tokenMetrics.value.tokenCount === 'number') {
                  tokenMetrics.value.tokenCount++
                  const elapsedMs = performance.now() - (tokenMetrics.value.startTime || 0)
                  if (elapsedMs > 100) {
                     tokenMetrics.value.tokensPerSecond = Math.round((tokenMetrics.value.tokenCount / elapsedMs) * 1000)
                  }
              }
              
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
      const assistantMsg = messages.value[assistantMsgIndex]

      // Sync final generated text with SQLite database via Python API
      // This is crucial for enabling the Thumbs Up/Down feedback mechanisms on Assistant messages
      if (assistantMsg.content) {
          fetch(`${API_BASE_URL}/v1/chat/sync_message`, {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
                  ...getAuthHeaders()
              },
              body: JSON.stringify({
                  message_id: assistantMsg.id,
                  session_id: currentSessionId.value,
                  content: assistantMsg.content
              })
          })
          .then(res => res.json())
          .then(data => {
              if (data && data.message_id) {
                  // Substitui o ID temporário (Date.now()) pelo ID Real Numérico gerado sequencialmente pelo SGBD.
                  // Isso religará a capacidade dos componentes de Feedback (Like/Dislike) funcionarem!
                  assistantMsg.id = data.message_id;
              }
          })
          .catch(e => console.error("Silently failed to sync AI response to database:", e))
      }
      
      // Execute Pending Agentic Tool Calls
      if (assistantMsg.tool_calls && assistantMsg.tool_calls.length > 0) {
          for (const tc of assistantMsg.tool_calls) {
              try {
                  let args: any = {}
                  try { args = JSON.parse(tc.function.arguments) } catch (e) {
                      console.warn("Tool Arguments Parse Fail (Misto)", tc.function.arguments)
                      // Fallback LLM output fix? (Not handled yet)
                  }
                  
                  let toolResult = null
                  const RUST_CORE_URL_TOOLS = 'http://127.0.0.1:8001'
                  
                  if (tc.function.name === 'read_vault_file') {
                      const res = await fetch(`${RUST_CORE_URL_TOOLS}/v1/tools/read_vault_file`, {
                          method: 'POST',
                          headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
                          body: JSON.stringify(args)
                      })
                      toolResult = await res.json()
                  } else if (tc.function.name === 'create_kanban_task') {
                      const res = await fetch(`${RUST_CORE_URL_TOOLS}/v1/tools/create_kanban_task`, {
                          method: 'POST',
                          headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
                          body: JSON.stringify(args)
                      })
                      toolResult = await res.json()
                  } else {
                      toolResult = { error: `Ferramenta '${tc.function.name}' não reconhecida pelo Cíbrido` }
                  }
                  
                  tc.status = toolResult.error ? 'error' : 'done'
                  tc.result = toolResult
                  
                  // Append tool message to feed back to LLM context
                  messages.value.push({
                      id: Date.now() + Math.random(),
                      role: 'tool',
                      content: JSON.stringify(toolResult),
                      tool_call_id: tc.id,
                      name: tc.function.name
                  })
              } catch (e: any) {
                  tc.status = 'error'
                  messages.value.push({
                      id: Date.now() + Math.random(),
                      role: 'tool',
                      content: JSON.stringify({ error: String(e) }),
                      tool_call_id: tc.id,
                      name: tc.function.name
                  })
              }
          }
          scrollToBottom()
          // Automatically trigger the LLM to complete its thought based on tool results!
          await sendMessage(true) // Recursive Auto-Drive!
      }
    }

  } catch (error: any) {
    if (error.name === 'AbortError' || error === 'User Cancelled') {
       console.log("Geração Cancelada pelo Usuário")
       const assistantMsgIndex = messages.value.findIndex(m => m.id === assistantMsgId)
       if (assistantMsgIndex !== -1 && messages.value[assistantMsgIndex]) {
           messages.value[assistantMsgIndex].content += '\n\n*(Geração Interrompida)*'
           messages.value[assistantMsgIndex].isStreaming = false
       }
       return
    }

    console.error("Ocorreu um erro ao buscar:", error)
    if (assistantMsgId !== undefined) {
      const assistantMsgIndex = messages.value.findIndex(m => m.id === assistantMsgId)
      if (assistantMsgIndex !== -1 && messages.value[assistantMsgIndex]) {
        if (!messages.value[assistantMsgIndex].content) {
            messages.value[assistantMsgIndex].content = '\n\n**Erro Cíbrido**: Não foi possível comunicar com o servidor. Garanta que The Mom (`sovereign-core`) está ativa.'
        } else {
            messages.value[assistantMsgIndex].content += '\n\n*(Conexão rompida no Stream)*'
        }
        messages.value[assistantMsgIndex].isStreaming = false
      }
    }
  } finally {
    isThinking.value = false
    currentAbortController.value = null
    tokenMetrics.value.isActive = false // Congela a métrica visual final
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
    const res = await fetch(`${RUST_CORE_URL}/v1/sessions/${id}`, {
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
        session_id: currentSessionId.value,
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

// Copiar para a área de transferência
const copyToClipboard = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text)
    showToast('Texto copiado para a área de transferência!', 'success')
  } catch (err) {
    showToast('Falha ao copiar texto.', 'error')
    console.error('Failed to copy text: ', err)
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

// Telemetry State
const tokenMetrics = ref({
   tokenCount: 0,
   startTime: 0,
   tokensPerSecond: 0,
   isActive: false
})
</script>

<template>
  <div class="flex flex-col w-full h-full bg-surface-900 text-surface-200 overflow-hidden font-sans relative">
    
    <!-- Sidebar / Navigation Teleported to App.vue -->
    <Teleport to="#sidebar-context-area" v-if="teleportReady">
      <div class="flex flex-col h-full w-full overflow-hidden shrink-0">
        <div class="p-4 flex items-center justify-between border-b border-surface-700">
          <div class="text-[10px] uppercase font-bold text-surface-500 tracking-wider">Histórico de Chat</div>
          <button @click="() => { currentSessionId = null; messages = [{ id: 1, role: 'assistant', content: 'Nova conversa iniciada. Como posso ajudar?' }]; }" class="p-1.5 text-surface-400 hover:text-primary-400 hover:bg-surface-700/50 rounded-md transition-colors" title="Nova Conversa">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
          </button>
        </div>
        
        <div class="p-3">
          <div class="relative">
            <input 
              v-model="searchQuery" 
              type="text" 
              placeholder="Buscar chats ou tags..." 
              class="w-full bg-surface-800 border border-surface-700 rounded-md py-1.5 pl-8 pr-3 text-xs text-surface-300 focus:outline-none focus:border-surface-500 transition-all placeholder-surface-500"
            />
            <svg class="w-3.5 h-3.5 text-surface-500 absolute left-2.5 top-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
          </div>
        </div>

        <div class="flex-1 overflow-y-auto px-3 pb-3 space-y-1 custom-scrollbar">
          <!-- Pastas com nome -->
          <div v-for="(sessList, folderName) in groupedSessions" :key="'folder-'+folderName">
             <template v-if="folderName !== '' && sessList.length > 0">
                 <button @click="toggleFolder(folderName as string)" class="w-full flex items-center justify-between px-2 py-1.5 text-[10px] font-bold text-surface-500 hover:text-surface-300 transition-colors uppercase tracking-wider mb-1 mt-2">
                   <div class="flex items-center gap-1.5">
                     <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"></path></svg>
                     {{ folderName }}
                   </div>
                   <svg :class="{'rotate-180': expandedFolders[folderName as string]}" class="w-3 h-3 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
                 </button>
                 
                 <div v-show="expandedFolders[folderName as string]" class="space-y-0.5 pl-2 ml-1.5 border-l border-[#333]">
                    <div 
                      v-for="session in sessList" 
                      :key="session.id"
                      class="group flex items-center gap-1"
                    >
                      <button
                        @click="loadSession(session.id)"
                        :class="['w-full text-left px-2 py-1.5 rounded-md text-xs transition-colors flex items-center justify-between', 
                                 currentSessionId === session.id 
                                  ? 'bg-primary-500/10 text-primary-400 font-medium' 
                                  : 'text-surface-400 hover:bg-surface-700/50']"
                      >
                        <span class="truncate block flex-1 pr-2">{{ session.title }}</span>
                        <div @click.stop="sessionToDelete = session.id" class="p-1 text-surface-500 hover:text-rose-400 opacity-0 group-hover:opacity-100 transition-all shrink-0" title="Deletar">
                          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                        </div>
                      </button>
                    </div>
                 </div>
             </template>
          </div>
          
          <!-- Sessões Raiz -->
          <div class="space-y-0.5 mt-2">
             <div 
                v-for="session in groupedSessions['']" 
                :key="session.id"
                class="group flex items-center gap-1"
              >
                <button
                  @click="loadSession(session.id)"
                  :class="['w-full text-left px-2 py-1.5 rounded-md text-xs transition-colors flex items-center justify-between', 
                           currentSessionId === session.id 
                            ? 'bg-primary-500/10 text-primary-400 font-medium' 
                            : 'text-surface-400 hover:bg-surface-700/50']"
                >
                  <div class="flex items-center gap-1.5 min-w-0 pr-1 truncate flex-1">
                    <svg class="w-3.5 h-3.5 shrink-0" :class="currentSessionId === session.id ? 'text-primary-400' : 'text-surface-600'" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path></svg>
                    <span class="truncate">{{ session.title }}</span>
                  </div>
                  <div @click.stop="sessionToDelete = session.id" class="p-1 text-surface-500 hover:text-rose-400 opacity-0 group-hover:opacity-100 transition-all shrink-0" title="Deletar">
                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                  </div>
                </button>
              </div>
          </div>
          <div v-if="sessions.length === 0" class="text-xs text-zinc-600 italic px-3 py-4 flex flex-col items-center gap-2 text-center">
            <svg class="w-8 h-8 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path></svg>
            Nenhuma conversa
          </div>
        </div>
      </div>
    </Teleport>

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
          <h2 class="font-medium text-surface-200 truncate max-w-[200px] md:max-w-md">
             {{ activeSession ? activeSession.title : 'Sovereign Pair' }}
          </h2>
           <button v-if="activeSession" @click="openEditSessionModal(activeSession as any)" class="p-1.5 text-surface-400 hover:text-primary-400 hover:bg-surface-700 rounded-md transition-colors" title="Editar Sessão">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path></svg>
          </button>
        </div>
        
        <!-- Right Status Indicators -->
        <div class="flex items-center gap-3">
          <!-- Telemetry Badge -->
          <div v-show="tokenMetrics.tokenCount > 0" class="flex items-center gap-2 border border-surface-700/60 bg-surface-900/50 rounded flex-shrink-0 px-2 py-0.5" title="Telemetria de Geração (Tokens/segundo) e Consumo">
             <svg class="w-3 h-3 text-sky-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
             <span class="text-[10px] text-sky-400 font-mono tracking-wider font-bold">{{ tokenMetrics.tokensPerSecond }} t/s</span>
             <span class="text-[10px] text-surface-500">|</span>
             <span class="text-[10px] text-surface-400 font-mono tracking-wider">{{ tokenMetrics.tokenCount }} T</span>
          </div>
          
          <div class="flex items-center gap-2 px-2 py-1 rounded-md transition-colors group" :title="isThinking ? 'Inferência Ativa' : 'Motor Pronto'">
            <span class="flex h-2 w-2 relative">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75" :class="isThinking ? 'bg-amber-400' : 'bg-emerald-400'"></span>
              <span class="relative inline-flex rounded-full h-2 w-2" :class="isThinking ? 'bg-amber-500' : 'bg-emerald-500'"></span>
            </span>
            <span class="text-xs font-medium text-slate-400">{{ isThinking ? 'Processando...' : 'Motor Pronto' }}</span>
          </div>
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
            <div v-if="msg.role === 'assistant'" class="w-8 h-8 md:w-10 md:h-10 rounded-full flex items-center justify-center relative">
              <!-- Orbit / Border (faint outer ring) -->
              <div class="absolute inset-0 rounded-full border border-current opacity-20 text-primary-500"></div>
              
              <!-- Pulsing animation from center to orbit while streaming (thinking) -->
              <div v-if="msg.isStreaming" class="absolute inset-0 rounded-full animate-ping opacity-30 bg-primary-500"></div>
              
              <!-- Center Dot (100% filled, solid) -->
              <div class="w-3.5 h-3.5 md:w-4 md:h-4 rounded-full bg-primary-500"></div>
            </div>
            <div v-else class="w-8 h-8 md:w-10 md:h-10 rounded-full bg-surface-700 flex items-center justify-center p-2 text-surface-300">
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
              :class="msg.role === 'user' ? 'bg-surface-700 text-surface-100 rounded-tr-sm' : 'bg-transparent prose w-full max-w-none'"
            >
              <template v-if="msg.role === 'user'">
                {{ msg.content }}
              </template>
              <template v-else>
                <!-- Container de React-Badges de Ação (Engine Info, Timeout, Warnings) -->
                <div v-if="msg.actions && msg.actions.length > 0" class="mb-3 flex flex-col gap-2">
                   <div v-for="(act, idx) in msg.actions" :key="idx" 
                        class="flex flex-row items-center gap-2.5 px-3 py-2 text-[11px] font-mono tracking-wider uppercase rounded-lg border w-fit shadow-md transition-all" 
                        :class="act.status === 'running' ? 'bg-sky-500/10 border-sky-500/20 text-sky-400' : (act.status === 'error' ? 'bg-rose-500/10 border-rose-500/30 text-rose-400 font-bold' : (act.status === 'warning' ? 'bg-amber-500/10 border-amber-500/30 text-amber-400 font-bold' : 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'))">
                      
                      <svg v-if="act.status === 'running'" class="w-4 h-4 animate-spin shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"></path></svg>
                      <svg v-else-if="act.status === 'error'" class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                      <svg v-else-if="act.status === 'warning'" class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                      <svg v-else class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>

                      <div class="flex flex-col">
                         <span>{{ act.action === 'web_search' ? 'Scanner Web (DuckDuckGo)' : (act.action === 'sys_rag' ? 'Motor O.S (Source Code)' : act.action) }}</span>
                         <span v-if="act.status === 'running'" class="text-[9.5px] opacity-70 normal-case">Capturando contexto externo...</span>
                         <span v-else-if="act.status === 'error'" class="text-[9.5px] opacity-90 normal-case font-medium whitespace-pre-wrap">{{ act.error || 'Falha Crítica do Engine' }}</span>
                         <span v-else-if="act.status === 'warning'" class="text-[9.5px] opacity-90 normal-case font-medium">{{ act.message || 'Sistema disparou um aviso' }}</span>
                         <span v-else class="text-[9.5px] opacity-70 normal-case">{{ act.message || 'Dados engolidos com sucesso' }}</span>
                      </div>
                   </div>
                </div>

                <div v-if="msg.content" v-safe-html="md.render(formatMessageIcons(msg.content))" class="prose-h1:text-xl prose-h2:text-text-lg prose-p:my-2 prose-pre:bg-surface-800 prose-pre:border prose-pre:border-surface-700 prose-pre:rounded-lg prose-pre:shadow-xl prose-a:text-primary-400 prose-a:no-underline hover:prose-a:underline prose-code:text-primary-300 prose-code:bg-primary-500/10 prose-code:px-1 prose-code:rounded"></div>
                <span v-if="msg.isStreaming" class="w-2 h-4 bg-primary-400 inline-block animate-pulse ml-1 vertical-align-middle mt-1 rounded-sm shadow-[0_0_8px_var(--primary)]"></span>
              </template>
            </div>
            
            <!-- Botões para mensagens do usuário -->
            <div v-if="msg.role === 'user'" class="mt-2 flex items-center justify-end gap-3 px-2 text-surface-500 opacity-0 group-hover:opacity-100 transition-opacity">
              <button @click="editMessage(msg)" title="Recuperar texto para editar" class="hover:text-amber-400">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path></svg>
              </button>
              <button @click="resendMessage(msg)" title="Reenviar exata mensagem" class="hover:text-primary-400">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
              </button>
            </div>

            <!-- Botões para mensagens da assistente -->
            <div v-if="msg.role === 'assistant'" class="mt-2 flex items-center gap-3 px-2 text-surface-500 opacity-0 group-hover:opacity-100 transition-opacity">
              <button @click="copyToClipboard(msg.content)" class="hover:text-primary-400" title="Copiar texto nativamente">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>
              </button>
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
          <button @click="triggerFileUpload" class="absolute left-3 p-2 text-surface-400 hover:text-primary-400 transition-colors" title="Anexar Arquivo">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"></path></svg>
          </button>
          
          <textarea
            v-model="inputMessage"
            @keydown.enter.prevent="sendMessage"
            placeholder="Mensagem para Sovereign Pair..."
            class="w-full bg-transparent text-surface-200 pl-12 pr-14 py-4 max-h-48 rounded-2xl focus:outline-none resize-none placeholder-surface-500"
            rows="1"
          ></textarea>
          
          <button 
            v-if="!isThinking"
            @click="sendMessage"
            :disabled="!inputMessage.trim() || isThinking"
            class="absolute right-3 p-2 rounded-xl transition-all flex items-center justify-center bg-primary-500 text-white hover:bg-primary-400 disabled:bg-surface-700 disabled:text-surface-500"
            title="Enviar"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path></svg>
          </button>
          
          <button 
            v-else
            @click="cancelGeneration"
            title="Parar Geração"
            class="absolute right-3 p-2 rounded-xl transition-all flex items-center justify-center bg-rose-500 text-white hover:bg-rose-400 shadow-[0_0_15px_rgba(244,63,94,0.3)] animate-pulse"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><rect class="opacity-75" x="6" y="6" width="12" height="12" rx="2" fill="currentColor"></rect></svg>
          </button>
        </div>
        <p class="text-center text-[11px] text-slate-500 mt-3 hidden md:block">
          Sovereign Pair AI pode cometer erros. Considere verificar informações com as fontes anexadas.
        </p>
      </div>
    </main>
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
    
    <!-- Edit Session Modal -->
    <div v-if="isEditSessionModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div class="bg-surface-100 dark:bg-surface-900 border border-surface-300 dark:border-surface-700/50 rounded-2xl shadow-2xl w-full max-w-sm overflow-hidden flex flex-col">
        <div class="px-6 py-4 border-b border-surface-300 dark:border-surface-700/50 flex justify-between items-center bg-surface-200 dark:bg-surface-800/50">
          <h3 class="text-lg font-medium text-surface-900 dark:text-surface-100">Editar Sessão</h3>
          <button @click="isEditSessionModalOpen = false" class="text-surface-500 hover:text-surface-900 dark:hover:text-white transition-colors">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
          </button>
        </div>
        <div class="p-6 space-y-4">
          <div class="space-y-2">
            <label class="block text-sm font-medium text-surface-600 dark:text-surface-400">Título</label>
            <input v-model="editingSession.title" type="text" class="w-full bg-surface-50 dark:bg-surface-800 border border-surface-300 dark:border-surface-700 text-surface-900 dark:text-surface-100 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block p-2.5 outline-none transition-all">
          </div>
          <div class="space-y-2">
            <label class="block text-sm font-medium text-surface-600 dark:text-surface-400">Pasta (Opcional)</label>
            <input v-model="editingSession.folder_name" list="session-folders-list" type="text" placeholder="Selecione ou digite o nome da pasta" class="w-full bg-surface-50 dark:bg-surface-800 border border-surface-300 dark:border-surface-700 text-surface-900 dark:text-surface-100 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block p-2.5 outline-none transition-all">
            <datalist id="session-folders-list">
               <template v-for="(_val, folderName) in expandedFolders" :key="folderName">
                  <option v-if="folderName !== ''" :value="folderName"></option>
               </template>
            </datalist>
          </div>

          <div class="space-y-2 pt-2 border-t border-surface-300 dark:border-surface-700/50">
            <label class="block text-sm font-medium text-surface-600 dark:text-surface-400">Tags / Categorias (Pressione Enter para adicionar)</label>
            <div class="flex flex-wrap gap-2 mb-2">
              <span v-for="(tag, idx) in editingSession.tags" :key="idx" class="px-2 py-1 bg-surface-200 dark:bg-surface-700 border border-surface-300 dark:border-surface-600 text-xs text-surface-800 dark:text-surface-300 rounded-md flex items-center gap-1">
                #{{ tag }}
                <button @click="removeTag(idx)" class="hover:text-rose-500 dark:hover:text-rose-400 ml-1 transition-colors">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                </button>
              </span>
              <span v-if="editingSession.tags.length === 0" class="text-xs text-surface-400 dark:text-surface-500 italic block">Nenhuma tag...</span>
            </div>
            <input 
              v-model="editingTagsInput"
              @keydown.enter.prevent="addTag"
              type="text" 
              placeholder="Ex: python, pesquisa, ideia... (Aperte Enter)" 
              class="w-full bg-surface-50 dark:bg-surface-800 border border-surface-300 dark:border-surface-700 text-surface-900 dark:text-surface-100 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block p-2.5 outline-none transition-all"
            >
          </div>
        </div>
        <div class="px-6 py-4 border-t border-surface-300 dark:border-surface-700/50 bg-surface-100 dark:bg-surface-800/30 flex justify-end gap-3">
          <button @click="isEditSessionModalOpen = false" class="px-4 py-2 text-sm text-surface-600 dark:text-surface-300 hover:text-surface-900 dark:hover:text-white transition-colors">Cancelar</button>
          <button @click="saveSessionEdit" class="px-5 py-2 text-sm bg-primary-500 hover:bg-primary-400 text-white rounded-lg font-medium transition-colors shadow-lg shadow-primary-500/30">Salvar</button>
        </div>
      </div>
    </div>
</template>

<style scoped>
/* Remove default arrow from Details/Summary in Webkit/Firefox */
.cognitive-details > summary::-webkit-details-marker {
  display: none;
}
.cognitive-details > summary {
  list-style: none;
}
.cognitive-details[open] summary {
  background-color: rgba(var(--surface-700), 0.5); /* Se houver var custom; se não vai herdar tw fallback */
}
</style>

