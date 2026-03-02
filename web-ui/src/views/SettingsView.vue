<script setup lang="ts">
import { ref, onMounted } from 'vue'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const getAuthHeaders = (): Record<string, string> => {
   const token = localStorage.getItem('sovereign_token')
   return token ? { 'Authorization': `Bearer ${token}` } : {}
}

const isConfigModalOpen = ref(true) // Always open in this view
const isLoadingConfig = ref(false)
const isTokenVisible = ref(false)
const authTokenForDisplay = ref(localStorage.getItem('sovereign_token') || 'Não configurado')

const localModels = ref<string[]>([])
const isFetchingModels = ref(false)
const modelToPull = ref('')
const isPulling = ref(false)
const pullStatus = ref('')
const pullProgress = ref(0)
const pullCompleted = ref(0)
const pullTotal = ref(0)

const personaOptions = ref([
  { id: 'custom', name: 'Personalizado', prompt: 'Seu próprio prompt...', color: 'text-slate-400 bg-slate-500' },
  { id: 'analytical', name: 'Analista de Dados', prompt: 'Você é um bot analítico e preciso...', color: 'text-sky-400 bg-sky-500' },
  { id: 'creative', name: 'Escritor Criativo', prompt: 'Você é focado em ideias e expansão literária...', color: 'text-fuchsia-400 bg-fuchsia-500' },
  { id: 'coder', name: 'Engenheiro de Software', prompt: 'Foco total em código limpo, python e Vue...', color: 'text-emerald-400 bg-emerald-500' },
  { id: 'mentor', name: 'Mentor Sênior', prompt: 'Você guia com perguntas socráticas...', color: 'text-amber-400 bg-amber-500' }
])

const systemSettings = ref({
  llm_provider: 'ollama',
  llm_model: 'llama3.2',
  temperature: 0.7,
  system_prompt: 'Você é Sovereign Pair, uma Inteligência Artificial local focada em privacidade e agência digital.',
  ai_name: 'Sovereign Pair',
  nickname: '',
  occupation: '',
  about_user: '',
  language: 'Português do Brasil',
  geolocation: '',
  formality: 'neutral',
  theme: 'slate',
  persona: 'custom'
})

const getPersonaColorClass = (id: string) => {
  const p = personaOptions.value.find(o => o.id === id)
  return p ? p.color : 'text-slate-400 bg-slate-500'
}

const selectPersona = (p: { id: string, prompt: string }) => {
  systemSettings.value.persona = p.id
  systemSettings.value.system_prompt = p.prompt
}

const loadConfig = async () => {
  try {
    const res = await fetch(`${API_BASE_URL}/v1/settings`, {
      headers: getAuthHeaders()
    })
    if (res.ok) {
      const data = await res.json()
      systemSettings.value = { ...systemSettings.value, ...data }
      if (systemSettings.value.theme) {
         document.documentElement.setAttribute('data-theme', systemSettings.value.theme)
      }
    }
    
    if (systemSettings.value.llm_provider === 'ollama') {
       fetchLocalModels()
    }
  } catch (err) {
    console.error("Failed to load settings:", err)
  }
}

const saveConfig = async () => {
  isLoadingConfig.value = true
  try {
    await fetch(`${API_BASE_URL}/v1/settings`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders()
      },
      body: JSON.stringify(systemSettings.value)
    })
    
    // Apply theme
    document.documentElement.setAttribute('data-theme', systemSettings.value.theme)
    
  } catch (err) {
    console.error("Failed to save settings:", err)
  } finally {
    isLoadingConfig.value = false
  }
}

const fetchLocalModels = async () => {
  isFetchingModels.value = true
  try {
    const res = await fetch(`${API_BASE_URL}/v1/llm/models`, {
      headers: getAuthHeaders()
    })
    if (res.ok) {
      const data = await res.json()
      localModels.value = data.models || []
    }
  } catch (e) {
    console.warn("Could not fetch local models", e)
  } finally {
    isFetchingModels.value = false
  }
}

const pullModel = async () => {
  if (!modelToPull.value.trim()) return;
  
  isPulling.value = true;
  pullStatus.value = 'Iniciando download...';
  pullProgress.value = 0;
  pullCompleted.value = 0;
  pullTotal.value = 0;
  
  try {
    const response = await fetch(`${API_BASE_URL}/v1/llm/pull`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders()
      },
      body: JSON.stringify({ model: modelToPull.value.trim() })
    });

    if (!response.ok) throw new Error('Falha ao iniciar download');
    if (!response.body) throw new Error('Sem corpo na resposta');

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n').filter(line => line.trim());
      
      for (const line of lines) {
         try {
           const data = JSON.parse(line);
           pullStatus.value = data.status || 'Fazendo download...';
           
           if (data.total) pullTotal.value = data.total;
           if (data.completed) pullCompleted.value = data.completed;
           
           if (data.total && data.completed) {
              pullProgress.value = Math.round((data.completed / data.total) * 100);
           }
         } catch(e) {
           // Skip bad json
         }
      }
    }
    
    pullStatus.value = 'Download finalizado!';
    await fetchLocalModels(); // Refresh list
    systemSettings.value.llm_model = modelToPull.value.trim();
    modelToPull.value = '';
    
    setTimeout(() => {
      isPulling.value = false;
    }, 3000);

  } catch (err) {
    console.error(err);
    pullStatus.value = 'Erro ao baixar modelo.';
    setTimeout(() => { isPulling.value = false; }, 3000);
  }
}

onMounted(() => {
  loadConfig()
})
</script>

<template>
  <div class="flex-1 flex flex-col h-full bg-[#0E0E10] overflow-hidden text-[#E0E0E0]">
     <div class="px-6 py-5 flex justify-between items-center bg-[#18181B] border-b border-[#222222] shrink-0">
        <h3 class="text-xl font-semibold text-slate-100 flex items-center gap-3">
          <div class="p-2 bg-emerald-500/10 rounded-lg text-emerald-400">
            <span class="i-ph-gear-duotone text-[24px]"></span>
          </div>
          Configurações da Engine
        </h3>
        <div class="flex items-center gap-4">
          <button @click="saveConfig" :disabled="isLoadingConfig" class="px-6 py-2.5 text-sm bg-emerald-500 hover:bg-emerald-400 text-white rounded-lg font-medium transition-colors shadow-lg shadow-emerald-500/30 disabled:opacity-50 flex items-center gap-2">
            <svg v-if="isLoadingConfig" class="w-4 h-4 animate-spin flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
            {{ isLoadingConfig ? 'Salvando...' : 'Salvar Alterações' }}
          </button>
        </div>
      </div>
      
      <!-- Body -->
      <div class="p-6 md:p-10 flex-1 overflow-y-auto w-full max-w-5xl mx-auto space-y-10 pb-20">
        
        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-2">
            <label class="block text-sm font-medium text-slate-400">Provedor LLM</label>
            <select v-model="systemSettings.llm_provider" class="w-full bg-[#18181B] border border-[#222222] text-[#E0E0E0] text-sm rounded-lg focus:ring-emerald-500 focus:border-emerald-500 block p-2.5 outline-none transition-all">
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
              <select v-else v-model="systemSettings.llm_model" class="w-full bg-[#18181B] border border-[#222222] text-[#E0E0E0] text-sm rounded-lg focus:ring-emerald-500 focus:border-emerald-500 block p-2.5 outline-none transition-all">
                <option v-for="mod in localModels" :key="mod" :value="mod">{{ mod }}</option>
                <option v-if="localModels.length === 0" value="llama3.2" disabled>Nenhum modelo encontrado</option>
              </select>
              <div class="mt-2 flex gap-2">
                <input v-model="modelToPull" type="text" placeholder="Baixar nova extração (ex: phi3:mini)" class="flex-1 bg-[#121214] border border-[#222222] text-[#E0E0E0] rounded px-2.5 py-1.5 text-sm outline-none focus:border-emerald-500 transition-colors">
                <button v-if="!isPulling" @click="pullModel" class="bg-emerald-500/20 text-emerald-400 border border-emerald-500/50 hover:bg-emerald-500/30 px-4 py-1.5 rounded text-sm font-medium transition-colors">
                  Baixar
                </button>
              </div>
              <!-- Progress Bar for Download -->
              <div v-if="isPulling" class="mt-2 text-xs space-y-1 bg-[#121214] p-2 rounded border border-[#222222]">
                 <div class="flex justify-between text-slate-400 font-medium">
                    <span>{{ pullStatus }}</span>
                    <span v-if="pullProgress > 0" class="text-emerald-400">{{ pullProgress }}%</span>
                 </div>
                 <div class="w-full bg-[#0E0E10] rounded-full h-1.5">
                    <div class="bg-emerald-500 h-1.5 rounded-full transition-all duration-300 ease-out" :style="{ width: `${pullProgress}%` }"></div>
                 </div>
                 <div v-if="pullTotal > 0" class="text-[10px] text-slate-500 tracking-wider">
                    {{ (pullCompleted / 1e9).toFixed(2) }} GB / {{ (pullTotal / 1e9).toFixed(2) }} GB
                 </div>
              </div>
            </template>
            <template v-else>
              <input v-model="systemSettings.llm_model" type="text" class="w-full bg-[#18181B] border border-[#222222] text-[#E0E0E0] text-sm rounded-lg focus:ring-emerald-500 focus:border-emerald-500 block p-2.5 outline-none transition-all" placeholder="ex: llama3, gpt-4o">
            </template>
          </div>
        </div>

        <div class="space-y-2">
          <div class="flex justify-between">
            <label class="block text-sm font-medium text-slate-400">Temperatura (Criatividade)</label>
            <span class="text-xs text-emerald-400 font-mono">{{ systemSettings.temperature.toFixed(2) }}</span>
          </div>
          <input v-model.number="systemSettings.temperature" type="range" min="0" max="2" step="0.1" class="w-full h-2 bg-[#222222] rounded-lg appearance-none cursor-pointer accent-emerald-500">
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
              :class="systemSettings.persona === p.id ? 'bg-emerald-500/10 border-emerald-500 text-emerald-300 ring-1 ring-emerald-500/50' : 'bg-[#18181B] border-[#222222] text-slate-400 hover:border-emerald-500/50 hover:text-slate-300'"
            >
              <!-- Dynamic Color Dot for Persona Selection Menu -->
              <div class="relative w-4 h-4 shrink-0 flex items-center justify-center mt-1">
                <div class="absolute inset-0 rounded-full border border-current opacity-20" :class="getPersonaColorClass(p.id)?.split(' ')[0] || ''"></div>
                <div class="w-2 h-2 rounded-full" :class="getPersonaColorClass(p.id)?.split(' ')[1] || ''"></div>
              </div>
              <div class="flex flex-col min-w-0">
                 <span class="text-xs font-semibold leading-tight truncate group-hover:text-emerald-300">{{ p.name }}</span>
                 <span class="text-[9px] text-slate-500 line-clamp-2 mt-1 leading-tight">{{ p.prompt }}</span>
              </div>
            </button>
          </div>

          <textarea 
            v-model="systemSettings.system_prompt" 
            rows="4" 
            @input="systemSettings.persona = 'custom'"
            class="w-full bg-[#18181B] border border-[#222222] text-[#E0E0E0] text-sm rounded-lg focus:ring-emerald-500 focus:border-emerald-500 block p-3 outline-none transition-all resize-none font-mono text-[13px] leading-relaxed" 
            placeholder="Como o assistente deve se comportar..."></textarea>
            
            <div class="space-y-2 mt-4">
              <label class="block text-sm font-medium text-slate-400">Tratamento e Formalidade</label>
              <div class="flex p-1 bg-[#18181B] rounded-lg border border-[#222222] max-w-sm">
                <button @click="systemSettings.formality = 'feminine'" :class="systemSettings.formality === 'feminine' ? 'bg-emerald-500/20 text-emerald-400 font-medium shadow-sm' : 'text-slate-400 hover:text-slate-300'" class="flex-1 py-2 text-xs rounded-md transition-colors">Assistente ♀️</button>
                <button @click="systemSettings.formality = 'neutral'" :class="systemSettings.formality === 'neutral' ? 'bg-emerald-500/20 text-emerald-400 font-medium shadow-sm' : 'text-slate-400 hover:text-slate-300'" class="flex-1 py-2 text-xs rounded-md transition-colors">Neutro 🤖</button>
                <button @click="systemSettings.formality = 'masculine'" :class="systemSettings.formality === 'masculine' ? 'bg-emerald-500/20 text-emerald-400 font-medium shadow-sm' : 'text-slate-400 hover:text-slate-300'" class="flex-1 py-2 text-xs rounded-md transition-colors">Assistente ♂️</button>
              </div>
            </div>

            <div class="space-y-4 pt-4 border-t border-[#222222]">
              <div class="space-y-2">
                <label class="block text-sm font-medium text-slate-400">Batismo da Inteligência Artificial</label>
                <input v-model="systemSettings.ai_name" type="text" class="w-full bg-[#18181B] border border-[#222222] text-[#E0E0E0] text-sm rounded-lg focus:ring-emerald-500 focus:border-emerald-500 block p-2.5 outline-none transition-all" placeholder="Nome para a IA (Ex: Jarvis, Friday)">
                <p class="text-[10px] text-slate-500">O sobrenome oficial permanecerá como <i>Sovereign Pair</i> corporativamente.</p>
              </div>
              <div class="space-y-2">
                <label class="block text-sm font-medium text-slate-400">Seu Nome / Como te chamar?</label>
                <input v-model="systemSettings.nickname" type="text" class="w-full bg-[#18181B] border border-[#222222] text-[#E0E0E0] text-sm rounded-lg focus:ring-emerald-500 focus:border-emerald-500 block p-2.5 outline-none transition-all" placeholder="Seu apelido/nome preferido">
              </div>
              <div class="space-y-2">
                <label class="block text-sm font-medium text-slate-400">Ocupação / Atuação</label>
                <input v-model="systemSettings.occupation" type="text" class="w-full bg-[#18181B] border border-[#222222] text-[#E0E0E0] text-sm rounded-lg focus:ring-emerald-500 focus:border-emerald-500 block p-2.5 outline-none transition-all" placeholder="Ex: Dev Backend Pleno">
              </div>
              <div class="space-y-2">
                <label class="block text-sm font-medium text-slate-400">Mais sobre você</label>
                <textarea v-model="systemSettings.about_user" class="w-full bg-[#18181B] border border-[#222222] text-[#E0E0E0] text-sm rounded-lg focus:ring-emerald-500 focus:border-emerald-500 block p-2.5 outline-none transition-all resize-y min-h-[80px]" placeholder="Gosto de explicações curtas em bullet points..."></textarea>
              </div>
              <div class="grid grid-cols-2 gap-4">
                <div class="space-y-2">
                  <label class="block text-sm font-medium text-slate-400">Idioma da IA</label>
                  <select v-model="systemSettings.language" class="w-full bg-[#18181B] border border-[#222222] text-[#E0E0E0] text-sm rounded-lg focus:ring-emerald-500 focus:border-emerald-500 block p-2.5 outline-none transition-all">
                    <option value="Português do Brasil">Português do Brasil</option>
                    <option value="Português (Carioca)">🇧🇷 Português (Carioca)</option>
                    <option value="Português (Paulistano)">��🇷 Português (Paulistano)</option>
                    <option value="Português (Mineiro)">🇧🇷 Português (Mineiro)</option>
                    <option value="Português (Nordestino)">🇧🇷 Português (Nordestino)</option>
                    <option value="Português de Portugal">🇵🇹 Português de Portugal</option>
                    <option value="Inglês (EUA)">🇺🇸 Inglês Americano</option>
                    <option value="Espanhol">🇪🇸 Espanhol</option>
                  </select>
                </div>
                <div class="space-y-2">
                  <label class="block text-sm font-medium text-slate-400">Geolocalização</label>
                  <input v-model="systemSettings.geolocation" type="text" class="w-full bg-[#18181B] border border-[#222222] text-[#E0E0E0] text-sm rounded-lg focus:ring-emerald-500 focus:border-emerald-500 block p-2.5 outline-none transition-all" placeholder="ex: SP, Brasil" title="Permite contexto local para clima ou cultura">
                </div>
              </div>
            </div>
          </div>

        <!-- Auth Token Viewer -->
        <div class="space-y-2 border-t border-[#222222] pt-4">
          <label class="block text-sm font-medium text-slate-400">Sovereign Token (API Key)</label>
          <div class="relative flex items-center bg-[#18181B] border border-[#222222] rounded-lg overflow-hidden transition-all focus-within:ring-1 focus-within:ring-emerald-500 focus-within:border-emerald-500">
            <input 
              :type="isTokenVisible ? 'text' : 'password'" 
              readonly
              :value="authTokenForDisplay"
              class="w-full bg-transparent text-[#E0E0E0] text-sm block p-2.5 outline-none font-mono" 
            >
            <button 
              @click="isTokenVisible = !isTokenVisible" 
              class="px-3 text-slate-400 hover:text-emerald-400 transition-colors"
              :title="isTokenVisible ? 'Ocultar Token' : 'Mostrar Token'"
            >
              <svg v-if="!isTokenVisible" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path></svg>
              <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"></path></svg>
            </button>
          </div>
          <p class="text-[11px] text-slate-500">Cole este token nas configurações do seu plugin Sovereign Pair no Obsidian.</p>
        </div>

      </div>
  </div>
</template>
