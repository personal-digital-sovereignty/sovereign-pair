<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || `http://${typeof window !== 'undefined' ? window.location.hostname : 'localhost'}:8000`
const RUST_CORE_URL = import.meta.env.VITE_RUST_CORE_URL || `http://${typeof window !== 'undefined' ? window.location.hostname : 'localhost'}:38001`

const getAuthHeaders = (): Record<string, string> => {
   const token = localStorage.getItem('sovereign_token')
   return token ? { 'Authorization': `Bearer ${token}` } : {}
}


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

const ollamaClusters = ref<{id: string, name: string, url: string}[]>([])
const activeClusterId = ref('')
const isFetchingClusters = ref(false)
const isManagingClusters = ref(false)
const newClusterName = ref('')
const newClusterUrl = ref('')

const loadClusters = async () => {
    isFetchingClusters.value = true
    try {
        const res = await fetch(`${RUST_CORE_URL}/v1/settings/ollama_clusters`, { headers: getAuthHeaders() })
        if (res.ok) {
            const data = await res.json()
            ollamaClusters.value = data.clusters || []
            activeClusterId.value = data.active_cluster_id || ''
        }
    } catch (e) {
        console.warn("Could not fetch clusters", e)
    } finally {
        isFetchingClusters.value = false
    }
}

const onClusterChange = async () => {
    try {
        await fetch(`${RUST_CORE_URL}/v1/settings/ollama_clusters`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
            body: JSON.stringify({
                clusters: ollamaClusters.value,
                active_cluster_id: activeClusterId.value
            })
        })
        systemSettings.value.llm_model = ''
        await fetchLocalModels()
    } catch (e) {
        console.error("Erro ao alternar cluster", e)
    }
}

const editClusterId = ref('')

const editCluster = (c: any) => {
    editClusterId.value = c.id;
    newClusterName.value = c.name;
    newClusterUrl.value = c.url;
}

const cancelEdit = () => {
    newClusterName.value = '';
    newClusterUrl.value = '';
    editClusterId.value = '';
}

const addCluster = async () => {
    if (!newClusterName.value.trim() || !newClusterUrl.value.trim()) return;
    const id = editClusterId.value || newClusterName.value.trim().toLowerCase().replace(/\s+/g, '-');
    
    const existingIdx = ollamaClusters.value.findIndex(c => c.id === id);
    if (existingIdx >= 0) {
        const c = ollamaClusters.value[existingIdx];
        if (c) {
            c.name = newClusterName.value.trim();
            c.url = newClusterUrl.value.trim();
        }
    } else {
        ollamaClusters.value.push({
            id,
            name: newClusterName.value.trim(),
            url: newClusterUrl.value.trim()
        });
    }
    
    // Save to backend
    try {
        await fetch(`${RUST_CORE_URL}/v1/settings/ollama_clusters`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
            body: JSON.stringify({ 
                clusters: ollamaClusters.value,
                active_cluster_id: activeClusterId.value 
            })
        });
        newClusterName.value = '';
        newClusterUrl.value = '';
        editClusterId.value = '';
    } catch(e) { console.error(e) }
}

const removeCluster = async (id: string) => {
    ollamaClusters.value = ollamaClusters.value.filter(c => c.id !== id);
    if (activeClusterId.value === id) {
       activeClusterId.value = 'local';
    }
    
    // Save to backend
    try {
        await fetch(`${RUST_CORE_URL}/v1/settings/ollama_clusters`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
            body: JSON.stringify({ 
                clusters: ollamaClusters.value,
                active_cluster_id: activeClusterId.value 
            })
        });
        await onClusterChange();
    } catch(e) { console.error(e) }
}

const personaOptions = ref([
  { id: 'custom', name: 'Personalizado', prompt: 'Seu próprio prompt...', color: 'text-surface-400 bg-surface-500' },
  { id: 'analytical', name: 'Analista de Dados', prompt: 'Você é um bot analítico e preciso. Foco em números, probabilidades e tabelas de dados.', color: 'text-primary-400 bg-primary-500' },
  { id: 'creative', name: 'Escritor Criativo', prompt: 'Você é focado em ideias, expansão literária e inovação. Pense fora da caixa.', color: 'text-primary-400 bg-primary-500' },
  { id: 'coder', name: 'Engenheiro de Software', prompt: 'Foco total em código limpo, documentação técnica, Python, Vue e clean architecture.', color: 'text-primary-400 bg-primary-500' },
  { id: 'mentor', name: 'Mentor Sênior', prompt: 'Você guia com perguntas socráticas, provocando raciocínio em vez de dar respostas prontas.', color: 'text-primary-400 bg-primary-500' },
  { id: 'assessor', name: 'Assessor Executivo', prompt: 'Você é um executivo C-Level assistente. Respostas diretas, executivas, em bullet-points estratégicos.', color: 'text-primary-400 bg-primary-500' },
  { id: 'philosophical', name: 'Filósofo Contemporâneo', prompt: 'Você discorre sobre os impactos éticos, existenciais e morais. Use analogias densas e perspectivas históricas.', color: 'text-primary-400 bg-primary-500' },
  { id: 'cyberpunk', name: 'Hacker Cyberpunk', prompt: 'Você responde como um netrunner de 2077. Direto, sarcástico, focado na "machine" e gírias de cyberpunk.', color: 'text-primary-400 bg-primary-500' },
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
  theme: 'dark',
  persona: 'custom',
  openai_api_key: '',
  anthropic_api_key: '',
  gemini_api_key: '',
  oci_sandbox_ip: '',
  oci_sandbox_user: 'ubuntu',
  oci_sandbox_key: '',
  custom_ollama_url: '',
  default_intake_vault: '',
  workspaces: [] as string[],
  sensus_mode: 'standard',
  enterprise_license_key: ''
})

const activeTab = ref('identity') // 'identity' | 'workspaces'

const newWorkspacePath = ref('')
const addWorkspace = async () => {
   if (newWorkspacePath.value.trim() && !systemSettings.value.workspaces.includes(newWorkspacePath.value.trim())) {
      systemSettings.value.workspaces.push(newWorkspacePath.value.trim())
      newWorkspacePath.value = ''
      await saveConfig()
   }
}

const removeWorkspace = async (index: number) => {
   systemSettings.value.workspaces.splice(index, 1)
   await saveConfig()
}

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
    const res = await fetch(`${RUST_CORE_URL}/v1/settings`, {
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
    
    // Atualiza Tema O.S Definitivo via Storage
    localStorage.setItem('sensus_theme', systemSettings.value.theme)
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
    const res = await fetch(`${API_BASE_URL}/v1/ollama/models`, {
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
    const response = await fetch(`${API_BASE_URL}/v1/ollama/pull`, {
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

const onProviderChange = () => {
   const p = systemSettings.value.llm_provider
   if (p === 'openai') systemSettings.value.llm_model = 'gpt-4o'
   else if (p === 'anthropic') systemSettings.value.llm_model = 'claude-3-5-sonnet-20240620'
   else if (p === 'gemini') systemSettings.value.llm_model = 'gemini-1.5-pro'
   else if (p === 'groq') systemSettings.value.llm_model = 'llama3-70b-8192'
   else if (p === 'ollama') {
       systemSettings.value.llm_model = 'llama3.2'
       fetchLocalModels()
   }
}

const proxyEnabled = ref(false)
const isMounted = ref(false)

onMounted(() => {
  const saved = localStorage.getItem('sensus_opencode_proxy_enabled')
  if (saved) proxyEnabled.value = saved === 'true'

  loadConfig()
  loadClusters()
  isMounted.value = true
})

watch(proxyEnabled, (val) => {
   localStorage.setItem('sensus_opencode_proxy_enabled', String(val))
})

watch(() => systemSettings.value.theme, (newTheme) => {
   // Instant visual feedback for Theme O.S without saving yet
   if (newTheme) {
      document.documentElement.setAttribute('data-theme', newTheme)
   }
})
</script>

<template>
  <div class="flex-1 flex flex-col h-full bg-surface-900 border-l border-surface-700 overflow-hidden text-surface-200">
     <!-- Header -->
     <div class="px-6 h-14 flex justify-between items-center bg-surface-900 border-b border-surface-700 shrink-0">
        <h3 class="text-lg font-semibold text-surface-200 flex items-center gap-3">
          Configurações da Engine
        </h3>
        <div class="flex items-center gap-4">
          <button @click="saveConfig" :disabled="isLoadingConfig" class="px-5 py-1.5 text-xs bg-primary-600 hover:bg-primary-500 text-white rounded font-medium transition-colors shadow-lg shadow-primary-500/20 disabled:opacity-50 flex items-center gap-2">
            <svg v-if="isLoadingConfig" class="w-4 h-4 animate-spin flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
            {{ isLoadingConfig ? 'Salvando...' : 'Salvar Alterações' }}
          </button>
        </div>
      </div>
      
      <div class="flex flex-1 h-full overflow-hidden">
        
        <!-- Sidebar Interna movida via Teleport para o layout central (O.S Wrapper) -->
        <Teleport to="#sidebar-context-area" v-if="isMounted">
            <div class="w-full h-full bg-surface-800 flex flex-col pt-4 shrink-0 overflow-y-auto">
                <button @click="activeTab = 'identity'" :class="activeTab === 'identity' ? 'bg-surface-700 border-l-2 border-primary-500 text-primary-400' : 'border-l-2 border-transparent text-surface-400 hover:text-surface-200 hover:bg-surface-700/50'" class="px-6 py-3 text-sm font-medium transition-all text-left flex items-center gap-3">
                    <span class="i-ph-user-focus-duotone text-lg"></span> Identidade & Tema
                </button>
                <button @click="activeTab = 'workspaces'" :class="activeTab === 'workspaces' ? 'bg-surface-700 border-l-2 border-primary-500 text-primary-400' : 'border-l-2 border-transparent text-surface-400 hover:text-surface-200 hover:bg-surface-700/50'" class="px-6 py-3 text-sm font-medium transition-all text-left flex items-center gap-3">
                    <span class="i-ph-hard-drives-duotone text-lg"></span> Workspaces O.S.
                </button>
            </div>
        </Teleport>
      
        <!-- Content Area (Direita) -->
        <div class="flex-1 overflow-y-auto p-8 relative">
          <div class="max-w-4xl mx-auto pb-20">
        
        <!-- ================= IDENTIDADE TAB ================= -->
        <div v-show="activeTab === 'identity'" class="space-y-10">
        
        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-2">
            <label class="block text-sm font-medium text-slate-400">Provedor LLM</label>
            <select v-model="systemSettings.llm_provider" @change="onProviderChange" class="w-full bg-surface-900 border border-surface-700 text-surface-200 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block p-2.5 outline-none transition-all">
              <option value="ollama">Ollama (Multi-Cluster Local)</option>
            </select>
          </div>
          <div class="space-y-2">
            <template v-if="systemSettings.llm_provider === 'ollama'">
              <div class="mb-4 space-y-2 p-3 bg-indigo-500/10 border border-indigo-500/20 rounded-lg">
                 <label class="flex items-center justify-between text-[11px] font-semibold text-indigo-400 uppercase tracking-wide">
                    <span class="flex items-center gap-2"><span class="i-ph-hard-drives-duotone text-sm"></span> Roteamento do Motor RAG</span>
                    <span v-if="isFetchingClusters" class="i-ph-spinner-gap-duotone animate-spin text-indigo-300"></span>
                 </label>
                 <select v-model="activeClusterId" @change="onClusterChange" class="w-full bg-surface-900 border border-surface-700 text-indigo-300 text-xs rounded focus:ring-indigo-500 focus:border-primary-500 block p-2 outline-none font-medium cursor-pointer shadow-inner">
                   <option v-for="c in ollamaClusters" :key="c.id" :value="c.id">⚡ {{ c.name }}</option>
                 </select>
                 <div class="flex items-center justify-between">
                    <p class="text-[9px] text-indigo-500/70 font-medium leading-tight">Direciona as requisições LLM/Embeddings espacialmente.</p>
                    <button @click="isManagingClusters = !isManagingClusters" class="text-[10px] text-indigo-400 hover:text-indigo-300 font-medium transition-colors flex items-center gap-1">
                       <span class="i-ph-wrench-duotone"></span> Gerenciar Nós
                    </button>
                 </div>
                 
                 <!-- Inline Cluster Manager -->
                 <div v-show="isManagingClusters" class="mt-3 bg-surface-900 border border-indigo-500/20 rounded-md p-2 space-y-3">
                    <!-- List -->
                    <ul class="space-y-1.5 max-h-32 overflow-y-auto pr-1">
                       <li v-for="c in ollamaClusters" :key="c.id" class="flex items-center justify-between bg-surface-800 border border-surface-700 p-1.5 rounded" :class="activeClusterId === c.id ? 'border-indigo-500/50 outline outline-1 outline-indigo-500/30' : ''">
                          <div class="flex flex-col min-w-0">
                             <span class="text-[11px] font-semibold text-slate-300 truncate" :class="activeClusterId === c.id ? 'text-indigo-300' : ''">{{ c.name }} <span v-if="activeClusterId === c.id" class="text-[9px] text-indigo-500/70 ml-1">(Ativo)</span></span>
                             <span class="text-[9px] text-slate-500 font-mono truncate">{{ c.url }}</span>
                          </div>
                          <!-- Ações do Nó -->
                          <div v-show="c.id !== 'local'" class="flex items-center gap-1 shrink-0">
                              <button @click="editCluster(c)" class="text-indigo-400/70 hover:text-indigo-300 p-1" title="Editar Nó">
                                 <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/><path d="m15 5 4 4"/></svg>
                              </button>
                              <button @click="removeCluster(c.id)" class="text-rose-500/70 hover:text-rose-400 p-1" title="Remover Nó da Frota">
                                 <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/><line x1="10" x2="10" y1="11" y2="17"/><line x1="14" x2="14" y1="11" y2="17"/></svg>
                              </button>
                          </div>
                       </li>
                    </ul>
                    
                    <!-- Add / Edit -->
                    <div class="flex flex-col gap-1.5 pt-2 border-t border-surface-700">
                       <input v-model="newClusterName" type="text" placeholder="Nome (Ex: Oracle Pro)" class="w-full bg-surface-900 border border-surface-600 text-surface-200 rounded px-2 py-1 text-[11px] outline-none focus:border-primary-500 placeholder-slate-600">
                       <input v-model="newClusterUrl" type="url" placeholder="URL (Ex: http://100.116.x.y:11434)" class="w-full bg-surface-900 border border-surface-600 text-surface-200 rounded px-2 py-1 text-[11px] outline-none focus:border-primary-500 placeholder-slate-600 font-mono">
                       <div class="flex gap-2 mt-1">
                           <button v-if="editClusterId" @click="cancelEdit" class="w-1/3 bg-slate-500/20 text-slate-400 hover:bg-slate-500/30 border border-slate-500/30 py-1.5 rounded text-[11px] font-semibold transition-colors">
                              Cancelar
                           </button>
                           <button @click="addCluster" :disabled="!newClusterName || !newClusterUrl" class="flex-1 bg-indigo-500/20 text-indigo-400 hover:bg-indigo-500/30 border border-indigo-500/30 disabled:opacity-50 disabled:cursor-not-allowed py-1.5 rounded text-[11px] font-semibold transition-colors">
                              {{ editClusterId ? 'Salvar Edição' : 'Adicionar à Frota' }}
                           </button>
                       </div>
                    </div>
                 </div>
              </div>
            </template>
            <label class="block text-sm font-medium text-slate-400">Nome do Modelo Localizado</label>
            <template v-if="systemSettings.llm_provider === 'ollama'">
              <div v-if="isFetchingModels" class="text-xs text-sky-400 flex items-center gap-2 p-2">
                <svg class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
                Buscando locais...
              </div>
              <select v-else v-model="systemSettings.llm_model" class="w-full bg-surface-900 border border-surface-700 text-surface-200 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block p-2.5 outline-none transition-all">
                <option v-for="mod in localModels" :key="mod" :value="mod">{{ mod }}</option>
                <option v-if="localModels.length === 0" value="llama3.2" disabled>Nenhum modelo encontrado</option>
              </select>
              <div class="mt-2 flex gap-2">
                <input v-model="modelToPull" type="text" placeholder="Baixar nova extração (ex: phi3:mini)" class="flex-1 bg-surface-950 border border-surface-700 text-surface-200 rounded px-2.5 py-1.5 text-sm outline-none focus:border-primary-500 transition-colors">
                <button v-if="!isPulling" @click="pullModel" class="bg-emerald-500/20 text-emerald-400 border border-emerald-500/50 hover:bg-emerald-500/30 px-4 py-1.5 rounded text-sm font-medium transition-colors">
                  Baixar
                </button>
              </div>
              <!-- Progress Bar for Download -->
              <div v-if="isPulling" class="mt-2 text-xs space-y-1 bg-surface-950 p-2 rounded border border-surface-700">
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
          </div>
        </div>

        <div class="space-y-2">
          <div class="flex justify-between">
            <label class="block text-sm font-medium text-slate-400">Temperatura (Criatividade)</label>
            <span class="text-xs text-emerald-400 font-mono">{{ systemSettings.temperature.toFixed(2) }}</span>
          </div>
          <input v-model.number="systemSettings.temperature" type="range" min="0" max="2" step="0.1" class="w-full h-2 bg-[#222222] rounded-lg appearance-none cursor-pointer accent-primary-500">
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
              :class="systemSettings.persona === p.id ? 'bg-primary-500/10 border-primary-500 text-primary-300 ring-1 ring-primary-500/50' : 'bg-surface-800 border-surface-700 text-surface-400 hover:border-primary-500/50 hover:text-surface-300'"
            >
              <!-- Dynamic Color Dot for Persona Selection Menu -->
              <div class="relative w-4 h-4 shrink-0 flex items-center justify-center mt-1">
                <div class="absolute inset-0 rounded-full border border-current opacity-20" :class="getPersonaColorClass(p.id)?.split(' ')[0] || ''"></div>
                <div class="w-2 h-2 rounded-full" :class="getPersonaColorClass(p.id)?.split(' ')[1] || ''"></div>
              </div>
              <div class="flex flex-col min-w-0">
                 <span class="text-xs font-semibold leading-tight truncate group-hover:text-primary-300">{{ p.name }}</span>
                 <span class="text-[9px] text-surface-500 line-clamp-2 mt-1 leading-tight">{{ p.prompt }}</span>
              </div>
            </button>
          </div>

          <textarea 
            v-model="systemSettings.system_prompt" 
            rows="4" 
            @input="systemSettings.persona = 'custom'"
            class="w-full bg-surface-900 border border-surface-700 text-surface-200 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block p-3 outline-none transition-all resize-none font-mono text-[13px] leading-relaxed" 
            placeholder="Como o assistente deve se comportar..."></textarea>
            
            <div class="space-y-2 mt-4">
              <label class="block text-sm font-medium text-slate-400">Tratamento e Formalidade</label>
              <div class="flex p-1 bg-surface-900 rounded-lg border border-surface-700 max-w-sm">
                <button @click="systemSettings.formality = 'feminine'" :class="systemSettings.formality === 'feminine' ? 'bg-emerald-500/20 text-emerald-400 font-medium shadow-sm' : 'text-slate-400 hover:text-slate-300'" class="flex-1 py-2 text-xs rounded-md transition-colors">Assistente ♀️</button>
                <button @click="systemSettings.formality = 'neutral'" :class="systemSettings.formality === 'neutral' ? 'bg-emerald-500/20 text-emerald-400 font-medium shadow-sm' : 'text-slate-400 hover:text-slate-300'" class="flex-1 py-2 text-xs rounded-md transition-colors">Neutro 🤖</button>
                <button @click="systemSettings.formality = 'masculine'" :class="systemSettings.formality === 'masculine' ? 'bg-emerald-500/20 text-emerald-400 font-medium shadow-sm' : 'text-slate-400 hover:text-slate-300'" class="flex-1 py-2 text-xs rounded-md transition-colors">Assistente ♂️</button>
              </div>
            </div>

            <div class="space-y-2 mt-6">
              <label class="block text-sm font-medium text-slate-400">Tema Visual (Sovereign OS)</label>
              <div class="flex gap-3 max-w-2xl">
                <button @click="systemSettings.theme = 'dark'" :class="systemSettings.theme === 'dark' ? 'ring-2 ring-emerald-500 border-transparent shadow-lg shadow-emerald-500/20' : 'border-surface-600 hover:border-emerald-500/50'" class="flex-1 py-3 px-3 rounded-lg border bg-[#09090b] text-zinc-300 flex flex-col items-center gap-2 transition-all">
                  <div class="w-full h-10 bg-[#18181b] rounded flex items-center justify-center border border-[#27272a] shadow-inner"><div class="w-4 h-4 rounded-full bg-emerald-500 shadow-sm"></div></div>
                  <span class="text-xs font-semibold mt-1">Dark Hacker</span>
                </button>
                <button @click="systemSettings.theme = 'blue'" :class="systemSettings.theme === 'blue' ? 'ring-2 ring-sky-500 border-transparent shadow-lg shadow-sky-500/20' : 'border-surface-600 hover:border-sky-500/50'" class="flex-1 py-3 px-3 rounded-lg border bg-[#020617] text-slate-300 flex flex-col items-center gap-2 transition-all">
                  <div class="w-full h-10 bg-[#0f172a] rounded flex items-center justify-center border border-[#1e293b] shadow-inner"><div class="w-4 h-4 rounded-full bg-sky-500 shadow-sm"></div></div>
                  <span class="text-xs font-semibold mt-1">Deep Blue</span>
                </button>
                <button @click="systemSettings.theme = 'cream'" :class="systemSettings.theme === 'cream' ? 'ring-2 ring-amber-500 border-transparent shadow-lg shadow-amber-500/20' : 'border-surface-600 hover:border-amber-500/50'" class="flex-1 py-3 px-3 rounded-lg border bg-[#fefce8] text-amber-900 flex flex-col items-center gap-2 transition-all">
                  <div class="w-full h-10 bg-[#fef3c7] rounded flex items-center justify-center border border-[#fde047] shadow-inner"><div class="w-4 h-4 rounded-full bg-amber-600 shadow-sm"></div></div>
                  <span class="text-xs font-semibold mt-1">Cream Reading</span>
                </button>
                <button @click="systemSettings.theme = 'white'" :class="systemSettings.theme === 'white' ? 'ring-2 ring-slate-400 border-transparent shadow-lg shadow-slate-400/20' : 'border-surface-600 hover:border-slate-500/50'" class="flex-1 py-3 px-3 rounded-lg border bg-[#ffffff] text-slate-800 flex flex-col items-center gap-2 transition-all">
                  <div class="w-full h-10 bg-[#f8fafc] rounded flex items-center justify-center border border-[#e2e8f0] shadow-inner"><div class="w-4 h-4 rounded-full bg-slate-500 shadow-sm"></div></div>
                  <span class="text-xs font-semibold mt-1">Clean White</span>
                </button>
              </div>
            </div>

            <div class="space-y-4 pt-4 border-t border-surface-700">
              <div class="space-y-2">
                <label class="block text-sm font-medium text-slate-400">Batismo da Inteligência Artificial</label>
                <input v-model="systemSettings.ai_name" type="text" class="w-full bg-surface-900 border border-surface-700 text-surface-200 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block p-2.5 outline-none transition-all" placeholder="Nome para a IA (Ex: Jarvis, Friday)">
                <p class="text-[10px] text-slate-500">O sobrenome oficial permanecerá como <i>Sovereign Pair</i> corporativamente.</p>
              </div>
              <div class="space-y-2">
                <label class="block text-sm font-medium text-slate-400">Seu Nome / Como te chamar?</label>
                <input v-model="systemSettings.nickname" type="text" class="w-full bg-surface-900 border border-surface-700 text-surface-200 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block p-2.5 outline-none transition-all" placeholder="Seu apelido/nome preferido">
              </div>
              <div class="space-y-2">
                <label class="block text-sm font-medium text-slate-400">Ocupação / Atuação</label>
                <input v-model="systemSettings.occupation" type="text" class="w-full bg-surface-900 border border-surface-700 text-surface-200 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block p-2.5 outline-none transition-all" placeholder="Ex: Dev Backend Pleno">
              </div>
              <div class="space-y-2">
                <label class="block text-sm font-medium text-slate-400">Mais sobre você</label>
                <textarea v-model="systemSettings.about_user" class="w-full bg-surface-900 border border-surface-700 text-surface-200 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block p-2.5 outline-none transition-all resize-y min-h-[80px]" placeholder="Gosto de explicações curtas em bullet points..."></textarea>
              </div>
              <div class="grid grid-cols-2 gap-4">
                <div class="space-y-2">
                  <label class="block text-sm font-medium text-slate-400">Idioma da IA</label>
                  <select v-model="systemSettings.language" class="w-full bg-surface-900 border border-surface-700 text-surface-200 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block p-2.5 outline-none transition-all">
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
                  <input v-model="systemSettings.geolocation" type="text" class="w-full bg-surface-900 border border-surface-700 text-surface-200 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block p-2.5 outline-none transition-all" placeholder="ex: SP, Brasil" title="Permite contexto local para clima ou cultura">
                </div>
              </div>
            </div>
          </div>

        <!-- Auth Token Viewer -->
        <div class="space-y-3 p-4 bg-surface-900 border border-surface-700/50 rounded-xl mt-8">
          <label class="block text-sm font-medium text-surface-400">Sovereign Token (API Key)</label>
          <div class="relative flex items-center bg-surface-800 border border-surface-700 rounded-lg overflow-hidden transition-all focus-within:ring-1 focus-within:ring-primary-500 focus-within:border-primary-500">
            <input 
              :type="isTokenVisible ? 'text' : 'password'" 
              readonly
              :value="authTokenForDisplay"
              class="w-full bg-transparent text-surface-200 text-sm block p-2.5 outline-none font-mono" 
            >
            <button 
              @click="isTokenVisible = !isTokenVisible" 
              class="px-3 text-surface-400 hover:text-primary-400 transition-colors"
              :title="isTokenVisible ? 'Ocultar Token' : 'Mostrar Token'"
            >
              <svg v-if="!isTokenVisible" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path></svg>
              <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"></path></svg>
            </button>
          </div>
          <p class="text-[11px] text-surface-500 text-center">Utilize essa chave secreta para integrações OpenAPI em modo Local/REST.</p>
        </div>
        </div>
        
          <!-- ================= WORKSPACES (O.S. Native) TAB ================= -->
         <div v-show="activeTab === 'workspaces'" class="space-y-8">
            
            <div class="bg-indigo-500/10 border border-indigo-500/30 rounded-lg p-5 flex items-start gap-4">
               <span class="i-ph-hard-drives-duotone text-3xl text-indigo-400 shrink-0"></span>
               <div>
                  <h4 class="text-indigo-400 font-semibold text-sm mb-1">Workspaces Nativos do O.S.</h4>
                  <p class="text-xs text-indigo-300/80 leading-relaxed">
                     Você pode mapear qualquer diretório do seu computador local (ex: <code class="bg-surface-900 text-slate-300 px-1 py-0.5 rounded">/home/user/Documentos</code>). 
                     A Sovereign lerá os dados nativos destas pastas sem copiar os arquivos.
                  </p>
               </div>
            </div>

            <div class="space-y-4 max-w-3xl">
               <div class="p-4 bg-surface-900 border border-surface-700 rounded-xl space-y-3">
                  <label class="block text-sm font-semibold text-emerald-400">Bandeja de Entrada Primária (Intake Vault)</label>
                  <p class="text-xs text-slate-400 leading-relaxed">
                     Quando você fizer Upload de um novo arquivo pela interface web, arrastar uma imagem no chat, 
                     ou criar um arquivo Novo, ele será fisicamente persistido neste único caminho absoluto do seu Sistema Operacional.
                  </p>
                  <input v-model="systemSettings.default_intake_vault" type="text" placeholder="/caminho/absoluto/Vault-Principal" class="w-full bg-surface-950 border border-surface-600 text-surface-200 text-sm rounded focus:ring-primary-500 focus:border-primary-500 block p-2.5 outline-none font-mono">
               </div>

               <div class="space-y-3 pt-6 border-t border-surface-700">
                  <label class="block text-sm font-medium text-slate-300">Diretórios Indexados Adicionais (Somente Leitura Dinâmica)</label>
                  
                  <div class="flex gap-2">
                     <input v-model="newWorkspacePath" @keyup.enter="addWorkspace" type="text" placeholder="Adicionar caminho absoluto (/opt/projetos/notas)" class="flex-1 bg-surface-900 border border-surface-700 text-surface-200 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block p-2.5 outline-none font-mono">
                     <button @click="addWorkspace" class="px-4 bg-emerald-500 text-white rounded-lg hover:bg-emerald-400 font-medium text-sm transition-colors">Vincular</button>
                  </div>

                  <div v-if="systemSettings.workspaces.length === 0" class="text-xs text-slate-500 py-4 text-center border border-dashed border-surface-600 rounded-lg">
                     Nenhum diretório adicional vinculado. O Motor agirá apenas na Inbox Primária.
                  </div>
                  
                  <ul v-else class="space-y-2">
                     <li v-for="(ws, index) in systemSettings.workspaces" :key="ws" class="flex justify-between items-center p-3 bg-surface-900 border border-slate-700/50 rounded-lg group">
                        <div class="flex items-center gap-3">
                           <span class="i-ph-folder-open-duotone text-slate-400 text-xl"></span>
                           <span class="text-sm font-mono text-slate-300">{{ ws }}</span>
                        </div>
                        <button @click="removeWorkspace(index)" class="text-rose-400 hover:text-rose-300 transition-opacity bg-rose-500/10 p-1.5 rounded" title="Desvincular Diretório">
                           <span class="i-ph-trash-duotone text-lg"></span>
                        </button>
                     </li>
                  </ul>
               </div>

               <!-- OPENCODE PROXY SETTINGS INJECTION -->
               <div class="space-y-3 pt-6 border-t border-surface-700">
                  <label class="block text-sm font-semibold text-emerald-400">Integrações de API Clientes (Vercel/OpenCode)</label>
                  <p class="text-xs text-slate-400 leading-relaxed mb-2">
                     O SOVEREIGN Rust-Core (Servidor Local 38001) pode atuar como um Proxy Compatível com OpenAI. Habilite abaixo para o seu VS Code redirecionar inference via SSE local.
                  </p>
                  <div class="p-4 bg-surface-900 border border-surface-700 rounded-xl flex items-center gap-3">
                     <input type="checkbox" id="proxy-opencode" v-model="proxyEnabled" class="w-4 h-4 rounded bg-surface-950 border-primary-800 text-primary-500 focus:ring-primary-500">
                     <label for="proxy-opencode" class="text-sm font-semibold text-emerald-400 cursor-pointer">Habilitar Proxy Local OpenCode via Sovereign Pair</label>
                  </div>
               </div>

               <!-- ORACLE OCI ZERO-TRUST SANDBOX (THE CODER) -->
               <div class="space-y-4 pt-6 border-t border-surface-700">
                  <label class="block text-sm font-semibold text-emerald-400 flex items-center gap-2">
                     <span class="i-ph-cloud-check-duotone text-lg"></span> Sandboxed Cloud Execution (Oracle OCI Gateway)
                  </label>
                  <p class="text-xs text-slate-400 leading-relaxed mb-2">
                     Variáveis de pareamento do Worker Remoto. A execução de códigos validados pelo Agente "The Coder" transitará estritamente via Subprocesso OpenSSH.
                  </p>
                  <div class="grid grid-cols-2 gap-4">
                     <div class="space-y-2">
                        <label class="block text-xs font-medium text-slate-400">IP Público / Tailscale (OCI_HOST)</label>
                        <input v-model="systemSettings.oci_sandbox_ip" type="text" placeholder="ex: 129.159.179.116" class="w-full bg-surface-950 border border-surface-700 text-surface-200 text-sm rounded focus:ring-primary-500 focus:border-primary-500 block p-2 outline-none font-mono placeholder:text-surface-600">
                     </div>
                     <div class="space-y-2">
                        <label class="block text-xs font-medium text-slate-400">Usuário SSH (OCI_USER)</label>
                        <input v-model="systemSettings.oci_sandbox_user" type="text" placeholder="ex: ubuntu" class="w-full bg-surface-950 border border-surface-700 text-surface-200 text-sm rounded focus:ring-primary-500 focus:border-primary-500 block p-2 outline-none font-mono placeholder:text-surface-600">
                     </div>
                  </div>
                  <div class="space-y-2">
                     <label class="block text-xs font-medium text-slate-400">Caminho Absoluto da Chave Privada (Ed25519 / RSA)</label>
                     <input v-model="systemSettings.oci_sandbox_key" type="text" placeholder="ex: /home/jefersonlopes/.ssh/id_ed25519" class="w-full bg-surface-950 border border-surface-700 text-surface-200 text-sm rounded focus:ring-primary-500 focus:border-primary-500 block p-2 outline-none font-mono placeholder:text-surface-600 shadow-inner">
                  </div>
               </div>

            </div>
         </div>
         
         <!-- ================= SOVEREIGN LICENSING (B2B) TAB ================= -->
         <div v-show="false" class="space-y-8">
            <div class="bg-amber-500/10 border border-amber-500/30 rounded-lg p-5 flex items-start gap-4 shadow-[0_0_15px_rgba(245,158,11,0.1)]">
               <span class="i-ph-shield-check-duotone text-3xl text-amber-400 shrink-0"></span>
               <div class="flex-1">
                  <h4 class="text-amber-400 font-semibold text-sm mb-1 uppercase tracking-wider flex items-center gap-2">
                     Sovereign Pair <span class="bg-amber-500/20 text-amber-300 text-[10px] px-2 py-0.5 rounded border border-amber-500/50">Enterprise Ready</span>
                  </h4>
                  <p class="text-xs text-amber-300/80 leading-relaxed mb-4">
                     O modo <strong class="text-amber-300">Enterprise B2B</strong> ativa a poda pragmática do motor (SENSUS_MODE=enterprise),
                     desativando módulos de consumo B2C (Como o Pomodoro) e endurecendo o contrato OpenAPI para integração de dados corporativos limpos e Audit Logs focados.
                  </p>
                  
                  <div class="space-y-4">
                     <div class="space-y-2">
                        <label class="block text-sm font-medium text-slate-300">Chave Criptográfica JWT (License Key)</label>
                        <div class="relative">
                           <textarea v-model="systemSettings.enterprise_license_key"
                               class="w-full bg-surface-950 border border-surface-600 text-surface-200 text-xs rounded-lg focus:ring-amber-500 focus:border-amber-500 block p-3 outline-none font-mono resize-none h-24 shadow-inner" 
                               placeholder="eyJhbGciOiJSUzI1NiIsInR5cCI... cole o seu Token Assinado aqui">
                           </textarea>
                        </div>
                        <p class="text-[10px] text-slate-500 mt-1">
                           As chaves são emitidas e assinadas pelo Master Generator offline. A sua engine RAG as valida de forma Zero-Trust localmente em <code class="bg-surface-900 px-1 rounded border border-surface-700">/v1/license/activate</code>.
                        </p>
                     </div>
                     
                     <div class="flex items-center gap-4 py-3 px-4 bg-surface-900 border border-surface-700 rounded-lg">
                        <div class="flex-1">
                           <p class="text-sm font-medium" :class="systemSettings.sensus_mode === 'enterprise' ? 'text-amber-400' : 'text-slate-300'">
                              Status do Motor B2B Local
                           </p>
                           <p class="text-[10px] text-slate-500">Isto é apenas um reflexo visual no Banco SQLite. A poda arquitetural de rede (Amputação) só ocorre no Boot do Container FastAPI.</p>
                        </div>
                        <div class="flex p-1 bg-surface-800 border border-surface-600 rounded-md">
                           <button @click="systemSettings.sensus_mode = 'standard'" :class="systemSettings.sensus_mode === 'standard' ? 'bg-surface-700 text-surface-200 shadow' : 'text-surface-400 hover:text-surface-200'" class="px-3 py-1 text-xs rounded transition-all font-medium">Standard</button>
                           <button @click="systemSettings.sensus_mode = 'enterprise'" :class="systemSettings.sensus_mode === 'enterprise' ? 'bg-amber-600 text-white shadow ring-1 ring-amber-500' : 'text-surface-400 hover:text-surface-200'" class="px-3 py-1 text-xs rounded transition-all font-medium">Enterprise</button>
                        </div>
                     </div>
                  </div>
               </div>
            </div>
         </div>

          </div>
        </div>
      </div>
  </div>
</template>
