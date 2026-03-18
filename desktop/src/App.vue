<script setup lang="ts">
import { ref, onMounted } from "vue";
import QrcodeVue from 'qrcode.vue';
import { invoke } from "@tauri-apps/api/core";

const showPairingModal = ref(false);
const pairAlias = ref("");
const pairToken = ref("");
const pairUrl = ref("");

async function openPairingModal() {
    try {
        const res = await fetch(`http://127.0.0.1:${activePort.value}/v1/network/pair`);
        if (res.ok) {
            const data = await res.json();
            if (data.alias && data.token) {
                pairAlias.value = data.alias;
                pairToken.value = data.token;
                pairUrl.value = `http://${data.alias}:${activePort.value}/?token=${data.token}`;
                showPairingModal.value = true;
            }
        }
    } catch (e) {
        console.error("Modo Offline: não foi possível parear via mDNS.", e);
    }
}

async function triggerStudioMode() {
    await invoke("open_studio_mode", { port: activePort.value });
}

const searchQuery = ref("");
const messages = ref<{role: string, content: string}[]>([]);
const isProcessing = ref(false);
const inputField = ref<HTMLInputElement | null>(null);
const activePort = ref<number>(38001); // Começa na 38001 e escala dinamicamente

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
    const TARGET_URL = `http://${HOST}:${activePort.value}/v1/chat/completions`;
    
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
        messages.value.push({ role: 'assistant', content: `⚠️ O Sovereign Pair Backend recusou a conexão (HTTP ${response.status}). Verifique se The Mom está rodando no porto 38001.` });
        isProcessing.value = false;
        return;
    }

    if (!response.body) throw new Error("No response body");

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    // Crie o card vazio do assistente para iniciar o stream
    messages.value.push({ role: 'assistant', content: '' });
    const assistantMsgIndex = messages.value.length - 1;

    let buffer = '';

    while (true) {
      const { value, done } = await reader.read();
      if (done) {
        // Flushing final do buffer caso decodificador segure algo
        if (buffer.trim()) {
           // O que restou aqui que não terminou em \n provavelmente é lixo ou final, mas é bom prevenir
        }
        break;
      }

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      
      // A última linha pode estar cortada ao meio num pacote TCP. 
      // Então removemos do array de linhas prontas e jogamos de volta no buffer para a próxima iteração.
      buffer = lines.pop() || '';
      
      for (const line of lines) {
        if (line.trim() === '') continue;
        
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
            console.error("SSE JSON Parse Error no pedaço:", dataStr, e);
          }
        }
      }
    }
  } catch (error) {
    console.error(error);
    messages.value.push({ role: 'assistant', content: `❌ Erro de Conexão: Não foi possível alcançar a RAG API no localhost:38001. O Motor está desligado.` });
  } finally {
    isProcessing.value = false;
  }
}

onMounted(async () => {
  inputField.value?.focus();
  
  // Realiza varredura silenciosa da API Rust (Sidecar) para descobrir em qual porta subiu (38001 até 38010)
  for (let port = 38001; port <= 38010; port++) {
      try {
          const res = await fetch(`http://127.0.0.1:${port}/v1/models`, {
              method: 'GET',
              headers: { 'Accept': 'application/json' }
          });
          if (res.ok) {
              activePort.value = port;
              console.log(`[Sovereign Core] Estabeleceu Uplink na porta: ${port}`);
              break;
          }
      } catch (e) {
          // Ignora erros de "Connection Refused" enquanto engole as portas
      }
  }

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
        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" class="shrink-0" style="color: #10b981;">
          <circle cx="12" cy="12" r="4.5" fill="currentColor"/>
          <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.5" stroke-opacity="0.3"/>
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
      <div class="shortcut popup-btn" @click="triggerStudioMode" title="Abre a Interface Completa Web"><span>💻</span> Studio RAG</div>
      <div class="shortcut popup-btn" @click="openPairingModal" title="Distribui o RAG na Rede Wi-Fi"><span>📡</span> Parear LAN</div>
      <div class="shortcut"><span>Esc</span> Ocultar</div>
    </div>
    
    <!-- Pairing Modal (QR Code) -->
    <div class="modal-overlay" v-if="showPairingModal" @click.self="showPairingModal = false">
        <div class="modal-content">
            <h3>Pareamento Seguro (Rede Local)</h3>
            <p>Acesse a Inteligência Artificial diretamente pelo navegador do seu celular ou de outro computador na mesma rede Wi-Fi.</p>
            
            <div class="qr-box">
                <qrcode-vue :value="pairUrl" :size="180" level="M" />
            </div>
            
            <div class="alias-box">
                <code>{{ pairUrl.split('?')[0] }}</code>
                <p class="token-hint">Acesso restrito via Token Autenticado.</p>
            </div>
            
            <button class="close-btn" @click="showPairingModal = false">Fechar</button>
        </div>
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
  max-height: 450px;
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

.popup-btn {
  cursor: pointer;
  transition: all 0.2s ease;
}
.popup-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  border-radius: 4px;
}
.popup-btn:hover span {
  color: #10b981;
}

/* Modal Styling */
.modal-overlay {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  animation: fade-in 0.2s ease-out;
}

.modal-content {
  background: #1a1a1e;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 24px;
  width: 90%;
  max-width: 320px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  box-shadow: 0 10px 40px rgba(0,0,0,0.5);
}

.modal-content h3 {
  margin: 0 0 10px;
  font-size: 18px;
  color: #fff;
}

.modal-content p {
  font-size: 13px;
  color: #aaa;
  margin: 0 0 20px;
  line-height: 1.4;
}

.qr-box {
  background: #fff;
  padding: 12px;
  border-radius: 12px;
  margin-bottom: 20px;
}

.alias-box {
  background: rgba(0, 0, 0, 0.3);
  padding: 10px;
  border-radius: 8px;
  width: 100%;
  margin-bottom: 20px;
}

.alias-box code {
  color: #10b981;
  font-size: 14px;
  font-family: monospace;
  font-weight: 600;
}

.token-hint {
  margin: 6px 0 0 !important;
  font-size: 11px !important;
  color: #666 !important;
}

.close-btn {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: #fff;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  width: 100%;
  transition: background 0.2s;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.15);
}
</style>