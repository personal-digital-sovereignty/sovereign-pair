<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
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
}

const inputMessage = ref('')
const messages = ref<Message[]>([
  { id: 1, role: 'assistant', content: 'Olá! Sou seu Sovereign Pair RAG. Estou conectado ao modelo local protegido em seus diretórios.\n\nComo posso ajudar hoje?' }
])
const isThinking = ref(false)
const chatContainer = ref<HTMLElement | null>(null)

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
        stream: true
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
          if (dataStr === '[DONE]') continue
          
          try {
            const data = JSON.parse(dataStr)
            if (data.token) {
              messages.value[assistantMsgIndex].content += data.token
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
        <div class="text-xs uppercase font-semibold text-slate-500 mb-2 px-2 mt-2 tracking-wider">Histórico</div>
        <button class="w-full text-left px-3 py-2 rounded-md bg-[#334155]/50 text-slate-200 text-sm hover:bg-[#334155] transition-colors flex items-center gap-2 border border-slate-600/30">
          <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path></svg>
          Sessão Atual
        </button>
      </div>
      
      <div class="p-4 border-t border-slate-700/50">
        <button class="flex items-center gap-2 text-sm text-slate-400 hover:text-slate-200 transition-colors w-full p-2 rounded hover:bg-[#334155]/50">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
          Configurações do LLM
        </button>
      </div>
    </aside>

    <!-- Main Chat Area -->
    <main class="flex-1 flex flex-col h-full bg-[#0f172a] shadow-[-10px_0_30px_rgba(0,0,0,0.5)] z-10">
      
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
              <button class="hover:text-slate-300"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg></button>
              <button class="hover:text-emerald-400"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.514"></path></svg></button>
            </div>
          </div>
        </div>
      </div>

      <!-- Input Area -->
      <div class="px-4 pb-6 pt-2 shrink-0 max-w-4xl w-full mx-auto">
        <div class="relative flex items-center bg-[#1e293b] rounded-2xl border border-slate-700 shadow-xl focus-within:ring-1 focus-within:ring-sky-500/50 focus-within:border-sky-500/50 transition-all">
          <textarea
            v-model="inputMessage"
            @keydown.enter.prevent="sendMessage"
            placeholder="Mensagem para Sovereign Pair..."
            class="w-full bg-transparent text-slate-200 pl-5 pr-14 py-4 max-h-48 rounded-2xl focus:outline-none resize-none placeholder-slate-500"
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

    </main>
  </div>
</template>

<style scoped>
/* Optional: Adding some custom gradient animations if needed */
</style>
