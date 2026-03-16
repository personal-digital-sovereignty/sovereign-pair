<script setup lang="ts">
import { ref, onMounted } from "vue";

const searchQuery = ref("");
const messages = ref<{role: string, content: string}[]>([]);
const isProcessing = ref(false);
const inputField = ref<HTMLInputElement | null>(null);

function closeWindow() {
  // Can be hooked to Tauri window.hide() when needed
  searchQuery.value = "";
  messages.value = [];
}

async function performSearch() {
  if (!searchQuery.value.trim()) return;
  
  messages.value.push({ role: 'user', content: searchQuery.value });
  searchQuery.value = "";
  isProcessing.value = true;
  
  try {
    const HOST = '127.0.0.1';
    const TARGET_URL = `http://${HOST}:8001/v1/chat/completions`;
    
    // Convert to OpenAI format
    const rustMessages = messages.value.map(m => ({
        role: m.role,
        content: m.content
    }));

    const response = await fetch(TARGET_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: 'gpt-4o', // Proxy alias
        messages: rustMessages,
        stream: true
      })
    });

    if (!response.ok) {
        messages.value.push({ role: 'assistant', content: `⚠️ O Sovereign Pair Backend recusou a conexão (HTTP ${response.status}). Verifique se The Mom está rodando no porto 8001.` });
        isProcessing.value = false;
        return;
    }

    if (!response.body) throw new Error("No response body");

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    // Crie o card vazio do assistente para iniciar o stream
    messages.value.push({ role: 'assistant', content: '' });
    const assistantMsgIndex = messages.value.length - 1;

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value, { stream: true });
      const lines = chunk.split('\n');
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const dataStr = line.slice(6).trim();
          if (dataStr === '[DONE]') continue;
          
          try {
            const data = JSON.parse(dataStr);
            let textDelta = null;
            
            if (data.choices && data.choices.length > 0 && data.choices[0].delta) {
                 textDelta = data.choices[0].delta.content;
            } else if (data.content || data.token) {
                 textDelta = data.content || data.token; // Fallback
            }
            
            if (textDelta) {
              messages.value[assistantMsgIndex].content += textDelta;
              // Auto-scroll minimalista para o bottom
              const chatArea = document.querySelector('.chat-area');
              if (chatArea) chatArea.scrollTop = chatArea.scrollHeight;
            }
          } catch (e) {
            console.error("SSE JSON Parse Error", e);
          }
        }
      }
    }
  } catch (error) {
    console.error(error);
    messages.value.push({ role: 'assistant', content: `❌ Erro de Conexão: Não foi possível alcançar a RAG API no localhost:8001. O Motor está desligado.` });
  } finally {
    isProcessing.value = false;
  }
}

onMounted(() => {
  inputField.value?.focus();
  // Listen for ESC to hide window
  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      // Future window.hide() call
      closeWindow();
    }
  });
});
</script>

<template>
  <main class="spotlight-container" data-tauri-drag-region>
    <!-- Header / Input Area -->
    <div class="search-header" data-tauri-drag-region>
      <div class="agent-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="var(--accent)" viewBox="0 0 256 256">
          <path d="M216.59,103c-2.73-30-24.16-56.34-53.11-65.41A67.92,67.92,0,0,0,128,24a67.92,67.92,0,0,0-35.48,13.57C63.57,46.64,42.14,73,39.41,103,22.06,112.55,10,132.89,10,152a46.06,46.06,0,0,0,46,46h24A14,14,0,0,0,94,184V168a14,14,0,0,1,14-14h13.25A51.3,51.3,0,0,1,128,152a51.3,51.3,0,0,1,6.75,2h13.25A14,14,0,0,1,162,168v16a14,14,0,0,0,14,14h24a46.06,46.06,0,0,0,46-46C246,132.89,233.94,112.55,216.59,103ZM220.26,177.16A34,34,0,0,1,196,186H176v-18a26,26,0,0,0-26-26H134a64.44,64.44,0,0,0-12-1.12,64.44,64.44,0,0,0-12,1.12H94a26,26,0,0,0-26,26v18H48a34,34,0,0,1-24.26-8.84A33.56,33.56,0,0,1,22.18,144c1.17-15.06,12.72-27.42,26.6-28.52a6,6,0,0,0,5.22-6A100,100,0,0,1,60.89,75a6,6,0,0,0-1.78-8A56,56,0,0,1,128,36a56,56,0,0,1,68.89,31,6,6,0,0,0-1.78,8,100,100,0,0,1,6.89,34.52,6,6,0,0,0,5.22,6c13.88,1.1,25.43,13.46,26.6,28.52A33.56,33.56,0,0,1,220.26,177.16Z"></path>
        </svg>
      </div>
      <input 
        ref="inputField"
        v-model="searchQuery"
        type="text" 
        placeholder="Pergunte ao Sovereign Pair..." 
        @keydown.enter="performSearch"
        autofocus
      />
      <div class="kdb-hint" v-if="!searchQuery && messages.length === 0">↵</div>
    </div>
    
    <!-- Results / Chat -->
    <div class="chat-area" v-if="messages.length > 0">
      <div 
        v-for="(msg, index) in messages" 
        :key="index" 
        :class="['message', msg.role]"
      >
        <span class="avatar">{{ msg.role === 'user' ? 'U' : 'AI' }}</span>
        <div class="content">{{ msg.content }}</div>
      </div>
      
      <div v-if="isProcessing" class="typing-indicator">
        <span class="dot"></span><span class="dot"></span><span class="dot"></span>
      </div>
    </div>
    
    <!-- Footer Context Hints -->
    <div class="footer" data-tauri-drag-region v-if="messages.length === 0">
      <div class="shortcut"><span>Esc</span> Ocultar</div>
      <div class="shortcut"><span>@mom</span> Contexto Geral</div>
      <div class="shortcut"><span>@dev</span> Contexto Código</div>
    </div>
  </main>
</template>

<style scoped>
.spotlight-container {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.search-header {
  padding: 20px 24px;
  display: flex;
  align-items: center;
  border-bottom: 1px solid var(--border-light);
}

.agent-icon {
  font-size: 28px;
  margin-right: 16px;
  filter: drop-shadow(0 0 12px var(--accent-glow));
}

input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  font-size: 22px;
  font-weight: 400;
  color: var(--text-main);
  font-family: inherit;
}

input::placeholder {
  color: var(--text-muted);
}

.kdb-hint {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  padding: 4px 10px;
  font-size: 14px;
  color: var(--text-muted);
  box-shadow: 0 2px 0 rgba(0,0,0,0.2) inset;
}

/* Chat Area */
.chat-area {
  padding: 20px 24px;
  max-height: 380px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.chat-area::-webkit-scrollbar {
  width: 6px;
}
.chat-area::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 6px;
}

.message {
  display: flex;
  gap: 14px;
  align-items: flex-start;
  animation: fade-in 0.3s ease;
}

@keyframes fade-in {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.avatar {
  min-width: 32px;
  height: 32px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
  color: #fff;
}

.user .avatar {
  background: linear-gradient(135deg, #4b5563, #374151);
}
.assistant .avatar {
  background: linear-gradient(135deg, var(--accent), #9d80ff);
  box-shadow: 0 0 12px var(--accent-glow);
}

.content {
  background: rgba(255, 255, 255, 0.04);
  padding: 14px 18px;
  border-radius: 12px;
  font-size: 15px;
  line-height: 1.5;
  color: var(--text-main);
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.user .content {
  border-top-left-radius: 4px;
}
.assistant .content {
  border-top-left-radius: 4px;
  background: rgba(107, 76, 255, 0.08);
  border-color: rgba(107, 76, 255, 0.25);
}

.footer {
  padding: 14px 24px;
  background: rgba(0, 0, 0, 0.25);
  display: flex;
  gap: 20px;
  font-size: 13px;
  color: var(--text-muted);
}

.shortcut span {
  display: inline-block;
  background: rgba(255, 255, 255, 0.1);
  padding: 2px 8px;
  border-radius: 4px;
  margin-right: 6px;
  font-family: monospace;
  font-weight: 600;
  color: #ccc;
}

/* Typing Indicator */
.typing-indicator {
  display: flex;
  gap: 6px;
  padding: 12px 16px 12px 50px;
}

.dot {
  width: 6px;
  height: 6px;
  background: var(--text-muted);
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}
.dot:nth-child(1) { animation-delay: -0.32s; }
.dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}
</style>