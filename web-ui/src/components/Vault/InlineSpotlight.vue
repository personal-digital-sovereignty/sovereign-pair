<template>
  <div class="h-full w-80 bg-surface-900 border-l border-surface-800 flex flex-col shrink-0 shadow-[-10px_0_30px_rgba(0,0,0,0.5)] z-20 transition-all duration-300 relative" :class="isOpen ? 'translate-x-0' : 'translate-x-full absolute right-0'">
     
     <!-- Header -->
     <header class="h-14 border-b border-surface-800 flex items-center px-4 justify-between bg-surface-900/80 backdrop-blur-md shrink-0">
        <div class="flex items-center gap-2">
           <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" class="text-emerald-500" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
           <h3 class="font-bold text-sm text-slate-200 tracking-wide">The Doctor</h3>
        </div>
        <button @click="$emit('close')" class="p-1.5 text-slate-400 hover:text-white hover:bg-surface-800 rounded-md transition-colors" title="Fechar Spotlight">
           <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>
     </header>

     <!-- Context Anchor Banner -->
     <div v-if="activeTabName" class="px-3 py-2 bg-emerald-500/10 border-b border-emerald-500/20 text-xs text-emerald-400 flex items-center gap-2 shrink-0">
        <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/></svg>
        <span class="truncate pr-2">Contexto ativo: <b>{{ activeTabName }}</b></span>
     </div>

     <!-- Empty State / Welcome -->
     <div v-if="messages.length === 0" class="flex-1 flex flex-col items-center justify-center p-6 text-center text-slate-500 space-y-4">
        <div class="w-12 h-12 rounded-full border border-emerald-500/30 bg-emerald-500/10 flex items-center justify-center text-emerald-500 shadow-[0_0_15px_rgba(16,185,129,0.2)]">
           <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a10 10 0 1 0 10 10H12V2z"/><path d="M12 12 2.1 7.1"/><path d="m12 12 9.9 4.9"/></svg>
        </div>
        <div>
           <p class="text-sm font-medium text-slate-300 mb-1">Spotlight Assistant</p>
           <p class="text-xs leading-relaxed">Faça perguntas profundas, peça revisões ou reescritas exclusivamente sobre o texto que você está editando.</p>
        </div>
        <div class="bg-surface-800 border border-surface-700 rounded-lg p-3 text-left w-full">
           <p class="text-[10px] font-bold text-surface-400 uppercase tracking-wider mb-2">Dica de Produtividade</p>
           <p class="text-xs text-slate-400">Grife um texto no Editor e clique em <b>"Consultar Sovereign"</b> no Menu Flutuante para analisar fatias específicas.</p>
        </div>
     </div>

     <!-- Chat Log -->
     <div v-else ref="chatLog" class="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
        <div v-for="(msg, idx) in messages" :key="idx" class="flex flex-col gap-1" :class="msg.role === 'user' ? 'items-end' : 'items-start'">
           <div class="text-[10px] font-semibold tracking-wider uppercase text-surface-500 px-1">
              {{ msg.role === 'user' ? 'Você' : 'The Doctor' }}
           </div>
           <div :class="msg.role === 'user' ? 'bg-surface-700 text-slate-200 rounded-xl rounded-tr-sm' : 'bg-transparent text-slate-300 prose prose-sm prose-invert'" class="px-3 py-2.5 max-w-[90%] text-[13px] leading-relaxed relative">
              <template v-if="msg.role === 'user'">{{ msg.content }}</template>
              <template v-else>
                 <div v-safe-html="md.render(msg.content)"></div>
                 <span v-if="isThinking && idx === messages.length - 1" class="w-1.5 h-3 bg-emerald-400 inline-block animate-pulse ml-1 align-middle"></span>
              </template>
           </div>
        </div>
     </div>

     <!-- Input Area -->
     <div class="p-3 border-t border-surface-800 shrink-0 bg-surface-900/80 backdrop-blur-md">
        <div class="relative flex items-end bg-surface-800 border border-surface-700 rounded-xl focus-within:border-emerald-500/50 focus-within:ring-1 focus-within:ring-emerald-500/50 shadow-inner overflow-hidden transition-all">
           <textarea 
               v-model="inputQuery"
               @keydown.enter.prevent="sendQuery"
               class="w-full bg-transparent text-slate-200 text-sm px-3 py-3 max-h-32 min-h-[44px] resize-none outline-none custom-scrollbar placeholder-surface-500"
               placeholder="Perguntar ao The Doctor..."
               rows="1"
           ></textarea>
           <button @click="sendQuery" :disabled="!inputQuery.trim() || isThinking" class="p-2.5 text-emerald-500 hover:bg-surface-700 transition-colors shrink-0 disabled:opacity-50 disabled:hover:bg-transparent">
              <svg v-if="!isThinking" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/></svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="animate-spin"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
           </button>
        </div>
        <!-- Context Pills -->
        <div class="flex gap-2 mt-2" v-if="contextPills.length > 0">
           <div v-for="(pill, i) in contextPills" :key="i" class="px-2 py-0.5 rounded bg-surface-700 border border-surface-600 flex items-center gap-1 max-w-full">
               <span class="text-[10px] text-slate-300 truncate tracking-wide">"{{ pill.text }}"</span>
               <button @click="removePill(i)" class="text-surface-400 hover:text-rose-400 p-0.5 transition-colors">
                  <svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
               </button>
           </div>
        </div>
     </div>

  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
import MarkdownIt from 'markdown-it'
import DOMPurify from 'dompurify'

const props = defineProps<{
  isOpen: boolean
  activeTabName: string | null
  activeDocumentContent: string // Passamos o Markdown bruto completo do Editor para ser o contexto
}>()

const emit = defineEmits(['close'])

const vSafeHtml = {
  mounted(el: HTMLElement, binding: import('vue').DirectiveBinding) {
    el.innerHTML = DOMPurify.sanitize(binding.value)
  },
  updated(el: HTMLElement, binding: import('vue').DirectiveBinding) {
    el.innerHTML = DOMPurify.sanitize(binding.value)
  }
}

const md = new MarkdownIt({ html: false, breaks: true, linkify: true })

const inputQuery = ref('')
const isThinking = ref(false)
const chatLog = ref<HTMLElement | null>(null)
const messages = ref<{role: 'user'|'assistant', content: string}[]>([])

// Text Selection Pills (Grifar texto no editor envia para cá)
const contextPills = ref<{text: string}[]>([])

const addContextPill = (text: string) => {
   if (text.trim().length > 0) {
      // Limpar anterior e manter apenas 1 pill de seleção para focar a pergunta
      contextPills.value = [{ text: text.length > 40 ? text.substring(0, 40) + '...' : text }]
      // A string completa será enviada no Request. Aqui guardamos a "pill" só como UX
      selectedTargetRaw.value = text
   }
   if (!props.isOpen) {
       // Se o drawer estiver fechado, não dá pra abrir sem emiter evento pro parent, 
       // então o Vue parent de VaultView.vue precisa saber
       // Disparado no evento de window (abaixo)
   }
}

const removePill = (idx: number) => {
   contextPills.value.splice(idx, 1)
   selectedTargetRaw.value = null
}

const selectedTargetRaw = ref<string | null>(null)

// Global event listener to catch text selected from TipTap Bubble Menu
const handleSpotlightInject = (e: Event) => {
    const customEvent = e as CustomEvent
    if (customEvent.detail && customEvent.detail.text) {
        addContextPill(customEvent.detail.text)
        inputQuery.value = ''
        // Auto-focus input
        setTimeout(() => document.querySelector('textarea')?.focus(), 300)
    }
}

window.addEventListener('sensus-spotlight-inject', handleSpotlightInject)

const scrollToBottom = () => {
   if (chatLog.value) {
      chatLog.value.scrollTop = chatLog.value.scrollHeight
   }
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const getAuthHeaders = (): Record<string, string> => {
   const token = localStorage.getItem('sovereign_token')
   return token ? { 'Authorization': `Bearer ${token}` } : {}
}

const sendQuery = async () => {
   if (!inputQuery.value.trim() || isThinking.value) return

   let finalQuery = inputQuery.value.trim()
   // Se o usuário tem um pedaço de texto pinado, empacotamos ele na pergunta.
   if (selectedTargetRaw.value) {
       finalQuery = `Referente ao trecho: "${selectedTargetRaw.value}"\n\nMinha pergunta: ${finalQuery}`
       // Consumimos a pill
       contextPills.value = []
       selectedTargetRaw.value = null
   }

   messages.value.push({ role: 'user', content: finalQuery })
   inputQuery.value = ''
   isThinking.value = true
   messages.value.push({ role: 'assistant', content: '' })
   nextTick(scrollToBottom)

   try {
       const res = await fetch(`${API_BASE_URL}/v1/chat`, {
           method: 'POST',
           headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
           // Forced context bypasses normal SLM retrieval and injects active doc directly
           body: JSON.stringify({
               query: finalQuery,
               options: {
                   forced_local_context: props.activeDocumentContent // Pass the entire markdown
               }
           })
       })

       if (!res.ok) throw new Error("Spotlight Chat falhou")

       if (res.body) {
           const reader = res.body.getReader()
           const decoder = new TextDecoder('utf-8')
           const assistantIndex = messages.value.length - 1

           while (true) {
               const { value, done } = await reader.read()
               if (done) break
               
               const chunk = decoder.decode(value, { stream: true })
               const lines = chunk.split('\n')
               
               for (const line of lines) {
                   if (line.startsWith('data: ')) {
                       const data = line.slice(6)
                       if (data === '[DONE]') break
                       try {
                           const parsed = JSON.parse(data)
                           if (parsed && parsed.content && messages.value[assistantIndex]) {
                               messages.value[assistantIndex].content += parsed.content
                               scrollToBottom()
                           }
                       } catch (e) {
                           // partial chunk handling if needed
                       }
                   }
               }
           }
       }

   } catch (e) {
       console.error("Spotlight Chat Error:", e)
       if (messages.value.length > 0) {
           const lastMsg = messages.value[messages.value.length - 1]
           if (lastMsg) {
               lastMsg.content = "_Falha de conexão com a interface do The Doctor._"
           }
       }
   } finally {
       isThinking.value = false
   }
}

</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}
</style>
