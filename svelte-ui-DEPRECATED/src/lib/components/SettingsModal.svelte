<script lang="ts">
import { API_BASE_URL } from '$lib/env_config';

  import { settingsState, saveSettings, openRouterState, loadOpenRouterSettings, saveOpenRouterSettings, qwenState, loadQwenSettings, saveQwenSettings, nvidiaState, loadNvidiaSettings, saveNvidiaSettings } from '$lib/settings.svelte';
  import { Settings, ChevronDown, ChevronsUpDown, X, Plus, Trash2, Database, Globe, ShieldCheck, Cloud, Sparkles, Cpu } from 'lucide-svelte';
  import { onMount } from 'svelte';
  
  let activeTab = $state('Workspaces'); // Engine, Workspaces, Persona, Guardrails, Profile
  let availableModels = $state<{name: string}[]>([]);
  
  // Workspaces state
  let workspaces = $state<{id: number, name: string, path: string}[]>([]);
  let isLoadingWs = $state(false);
  let newWsName = $state('');
  let newWsPath = $state('');
  let isAddingWs = $state(false);

  // SearxNG state
  let searxngNodes = $state<string[]>([]);
  let newSearxngNode = $state('');
  let isLoadingSearxng = $state(false);

  onMount(async () => {
      try {
          const res = await fetch(`${API_BASE_URL}/v1/system/available_models`);
          if (res.ok) {
              const data = await res.json();
              if (data.models) availableModels = data.models;
          }
      } catch(e) { console.error("Could not fetch models", e); }
      
      loadWorkspaces();
      loadSearxng();
      loadOpenRouterSettings();
      loadQwenSettings();
      loadNvidiaSettings();
  });
  
  async function loadWorkspaces() {
      isLoadingWs = true;
      try {
          const res = await fetch(`${API_BASE_URL}/v1/workspaces`);
          if (res.ok) {
              workspaces = await res.json();
          }
      } catch(e) { console.error("Could not fetch workspaces", e); }
      isLoadingWs = false;
  }

  async function addWorkspace() {
      if (!newWsName || !newWsPath) return;
      isAddingWs = true;
      try {
          const res = await fetch(`${API_BASE_URL}/v1/workspaces`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ name: newWsName, path: newWsPath })
          });
          if (res.ok) {
              newWsName = '';
              newWsPath = '';
              await loadWorkspaces();
          } else {
              const data = await res.json();
              alert(data.message || "Error adding workspace");
          }
      } catch(e) { console.error("Error adding workspace", e); }
      isAddingWs = false;
  }

  async function deleteWorkspace(id: number) {
      if(!confirm("Are you sure? This will unmap the directory from the Sovereign Engine!")) return;
      try {
          const res = await fetch(`${API_BASE_URL}/v1/workspaces/${id}`, { method: 'DELETE' });
          if (res.ok) {
              workspaces = workspaces.filter(w => w.id !== id);
          }
      } catch(e) { console.error("Error deleting workspace", e); }
  }
  
  function closeModal() {
      settingsState.isOpen = false;
  }

  async function loadSearxng() {
      isLoadingSearxng = true;
      try {
          const res = await fetch(`${API_BASE_URL}/v1/settings/searxng`);
          if (res.ok) searxngNodes = await res.json();
      } catch(e) { console.error("Could not fetch searxng nodes", e); }
      isLoadingSearxng = false;
  }

  async function addSearxngNode() {
      if (!newSearxngNode) return;
      if (!newSearxngNode.startsWith('http')) newSearxngNode = 'https://' + newSearxngNode;
      searxngNodes.push(newSearxngNode);
      newSearxngNode = '';
      await saveSearxng();
  }

  async function removeSearxngNode(index: number) {
      searxngNodes.splice(index, 1);
      await saveSearxng();
  }
  
  async function saveSearxng() {
      try {
          await fetch(`${API_BASE_URL}/v1/settings/searxng`, {
              method: 'POST', body: JSON.stringify(searxngNodes), headers: {'Content-Type': 'application/json'}
          });
      } catch(e) { console.error(e); }
  }

  const PERSONA_PRESETS = [
      { name: 'Sovereign Architect', text: 'Você é o Arquiteto mestre do Cíbrido. Analise toda a estrutura e responda com foco em engenharia, arquitetura de software e escalabilidade.' },
      { name: 'Sovereign Coder', text: 'Você é um Especialista em Código (Rust, Svelte, TS). Forneça snippets eficientes, limpos e siga as rigorosas práticas do DevSecOps e Clean Code.' },
      { name: 'Sovereign Nurse', text: 'Você atua como Analista de Segurança / Cibersegurança (Red Team). Foco em encontrar vulnerabilidades, propor hardening, garantir DLP e segurança defensiva.' },
      { name: 'Sovereign Accountant', text: 'Analista Financeiro e de Negócios. Foco absoluto em números, cálculos, projeções, planilhas e economia de recursos Cloud/Token.' },
      { name: 'Sovereign Mom', text: 'Assistente Executiva Pessoal. Amigável, calorosa, hiper-organizada. Foco exclusivo em resumos, checklists, bem-estar e produtividade diária.' },
      { name: 'Sovereign Doctor', text: 'Pesquisador Chefe. Foco metodológico. Ao responder, utilize linguagem científica, buscas extensas em papers e forneça detalhes acadêmicos profundos.' },
      { name: 'Sovereign Oracle', text: 'Criativo mestre. Copywriter avançado especializado em UX/UI, design de narrativa, persuasão e comunicação não-violenta.' },
      { name: 'Sovereign Operator', text: 'DevOps & SRE Specialist. Foco absoluto em Infraestrutura como Código, Docker, Kubernetes, CI/CD, métricas de rede e estabilidade nativa.' },
      { name: 'Blank Canvas', text: 'Você é um assistente LLM genérico. Responda de forma direta e concisa o que lhe for solicitado, sem impor personalidades.' }
  ];

  function applyPreset(presetName: string) {
      const p = PERSONA_PRESETS.find(x => x.name === presetName);
      if (p) {
          settingsState.personalityName = p.name;
          settingsState.systemInstructions = p.text;
      }
  }
</script>

{#if settingsState.isOpen}
<div class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 dark:bg-slate-900/80 backdrop-blur-[2px]">
    <!-- Engine Settings Modal -->
    <div class="w-full max-w-2xl bg-[#ffffff] dark:bg-[#12192b] rounded-xl shadow-2xl dark:shadow-[0_24px_48px_-12px_rgba(0,0,0,0.5)] border border-slate-200 dark:border-[#424859]/20 flex flex-col max-h-[85vh] overflow-hidden transition-colors">
        <!-- Modal Header -->
        <div class="px-8 py-6 flex items-center justify-between bg-slate-50/50 dark:bg-[#0c1324] border-b border-transparent dark:border-[#424859]/20 transition-colors">
            <div class="flex items-center gap-3">
                <div class="p-2 bg-indigo-50 dark:bg-indigo-500/10 rounded-lg">
                    <Settings class="w-6 h-6 text-indigo-700 dark:text-[#74b0ff]" />
                </div>
                <div>
                    <h2 class="text-xl font-bold text-slate-800 dark:text-slate-200 tracking-tight">Engine Settings</h2>
                    <p class="text-sm text-slate-500 dark:text-slate-400">Configure core RAG retrieval, Persona, and Security</p>
                </div>
            </div>
            <button onclick={closeModal} class="p-2 hover:bg-slate-200 dark:hover:bg-slate-800 rounded-full transition-colors cursor-pointer text-slate-500 dark:text-slate-400">
                <X class="w-5 h-5" />
            </button>
        </div>

        <!-- Tabs -->
        <div class="flex px-8 border-b border-slate-200 dark:border-[#424859]/20 bg-slate-50/50 dark:bg-[#0c1324] transition-colors overflow-x-auto no-scrollbar">
            {#each ['Workspaces', 'Engine', 'Cloud Mesh', 'Alibaba Qwen', 'NVIDIA NIM', 'Persona', 'Profile', 'Guardrails'] as tab}
                <button 
                    class="px-6 py-3 text-sm font-bold border-b-2 transition-colors cursor-pointer {activeTab === tab ? 'border-indigo-700 dark:border-[#74b0ff] text-indigo-800 dark:text-[#74b0ff]' : 'border-transparent text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200'}"
                    onclick={() => activeTab = tab}
                >
                    {tab}
                </button>
            {/each}
        </div>

        <!-- Modal Content -->
        <div class="flex-1 overflow-y-auto p-8 space-y-10 custom-scrollbar dark:bg-[#12192b]">
            
            {#if activeTab === 'Workspaces'}
                <section class="space-y-6">
                    <div class="flex items-center justify-between">
                        <div>
                            <h3 class="text-sm font-bold text-slate-800 dark:text-slate-200">Global Knowledge Workspaces</h3>
                            <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">Sovereign Core will index, vectorise, and monitor all directories listed below.</p>
                        </div>
                    </div>
                    
                    <!-- Form to add new workspace -->
                    <div class="flex items-end gap-4 p-4 bg-slate-50 dark:bg-[#0c1324] border border-slate-100 dark:border-[#424859]/20 rounded-xl">
                        <div class="flex-1 space-y-1">
                            <label for="nicknameInput" class="text-[10px] font-bold uppercase tracking-widest text-slate-500 dark:text-slate-400">Nickname</label>
                            <input id="nicknameInput" bind:value={newWsName} class="w-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-[#424859]/50 rounded-lg px-3 py-2 text-sm outline-none focus:border-indigo-500 dark:focus:border-[#74b0ff] dark:text-slate-200" placeholder="e.g. Legal Docs" />
                        </div>
                        <div class="flex-[2] space-y-1">
                            <label for="osPathInput" class="text-[10px] font-bold uppercase tracking-widest text-slate-500 dark:text-slate-400">Absolute OS Path</label>
                            <input id="osPathInput" bind:value={newWsPath} class="w-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-[#424859]/50 rounded-lg px-3 py-2 text-sm outline-none focus:border-indigo-500 dark:focus:border-[#74b0ff] dark:text-slate-200 font-mono" placeholder="/home/user/Documents/Legal" />
                        </div>
                        <button onclick={addWorkspace} disabled={!newWsName || !newWsPath || isAddingWs} class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 dark:bg-indigo-500/20 dark:hover:bg-indigo-500/30 text-white dark:text-[#74b0ff] font-bold text-sm rounded-lg transition-colors flex items-center shadow-sm disabled:opacity-50 cursor-pointer">
                            {#if isAddingWs} <span class="animate-pulse">Adding...</span> {:else} <Plus class="w-4 h-4 mr-1"/> Add {/if}
                        </button>
                    </div>

                    <!-- List of current workspaces -->
                    <div class="space-y-3">
                        {#if isLoadingWs}
                            <div class="py-4 text-center text-xs text-slate-400 dark:text-slate-500">Loading workspaces...</div>
                        {:else if workspaces.length === 0}
                            <div class="py-6 text-center text-xs font-semibold text-slate-400 dark:text-slate-500 bg-slate-50 dark:bg-[#0c1324] rounded-xl border border-slate-100 dark:border-[#424859]/20 border-dashed">
                                No workspaces defined. RAG Engine is dormant.
                            </div>
                        {:else}
                            {#each workspaces as ws}
                                <div class="flex items-center justify-between p-4 bg-white dark:bg-[#0c1324] border border-slate-200 dark:border-[#424859]/20 rounded-xl shadow-sm group hover:border-indigo-200 dark:hover:border-indigo-500/50 transition-colors">
                                    <div class="flex items-start gap-4">
                                        <div class="mt-0.5 w-10 h-10 rounded-xl bg-indigo-50 dark:bg-indigo-500/10 border border-indigo-100 dark:border-indigo-500/20 flex items-center justify-center">
                                            <Database class="w-4 h-4 text-indigo-500 dark:text-[#74b0ff]"/>
                                        </div>
                                        <div>
                                            <p class="text-sm font-bold text-slate-800 dark:text-slate-200">{ws.name}</p>
                                            <p class="text-[11px] text-slate-500 dark:text-slate-400 font-mono mt-0.5 select-all">{ws.path}</p>
                                        </div>
                                    </div>
                                    <button onclick={() => deleteWorkspace(ws.id)} class="p-2 text-slate-400 dark:text-slate-500 hover:text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-500/10 dark:hover:text-rose-400 rounded-lg transition-colors opacity-0 group-hover:opacity-100 cursor-pointer" title="Unmap Workspace">
                                        <Trash2 class="w-4 h-4" />
                                    </button>
                                </div>
                            {/each}
                        {/if}
                    </div>
                </section>
            {/if}

            {#if activeTab === 'Engine'}
                <!-- Provider & Model Selection -->
                <section class="grid grid-cols-2 gap-6">
                    <div class="space-y-2">
                        <label for="providerBtn" class="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 flex items-center gap-2">
                            Provider
                        </label>
                        <div class="relative">
                            <button id="providerBtn" class="w-full flex items-center justify-between px-4 py-3 bg-slate-50 dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-[#424859]/50 text-slate-800 dark:text-slate-200 text-sm font-medium">
                                <span class="flex items-center gap-2">
                                    <span class="w-2 h-2 rounded-full bg-emerald-500 dark:bg-emerald-400"></span>
                                    {settingsState.provider}
                                </span>
                                <ChevronDown class="w-5 h-5 text-slate-400 dark:text-slate-500" />
                            </button>
                        </div>
                    </div>
                    <div class="space-y-2">
                        <label for="modelSelect" class="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 flex items-center gap-2">
                            Model Name
                        </label>
                        <div class="relative">
                            <select id="modelSelect" bind:value={settingsState.modelName} class="w-full px-4 py-3 pr-10 bg-white dark:bg-slate-800 rounded-xl border border-indigo-200 dark:border-[#424859]/50 text-slate-800 dark:text-slate-200 text-sm font-medium shadow-sm appearance-none outline-none focus:ring-2 focus:ring-indigo-500/20 dark:focus:border-[#74b0ff] cursor-pointer">
                                {#if availableModels.length === 0}
                                    <option value={settingsState.modelName}>{settingsState.modelName}</option>
                                {/if}
                                {#each availableModels.filter(m => !m.name.includes('embed') && !m.name.includes('bge-') && !m.name.includes('nomic')) as m}
                                    <option value={m.name}>{m.name}</option>
                                {/each}
                            </select>
                            <ChevronsUpDown class="w-5 h-5 text-indigo-700 dark:text-[#74b0ff] absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none" />
                        </div>
                    </div>
                </section>
                <!-- Temperature (Slider) -->
                <section class="space-y-4">
                    <div class="flex justify-between items-end">
                        <div class="space-y-1">
                            <label for="tempInput" class="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Temperature (Creativity)</label>
                            <p class="text-xs text-slate-500 dark:text-slate-500">Controls randomness: Lower is more focused and deterministic.</p>
                        </div>
                        <span class="text-sm font-mono font-bold text-indigo-800 dark:text-[#74b0ff] bg-indigo-100 dark:bg-indigo-500/10 border border-transparent dark:border-indigo-500/30 px-2 py-0.5 rounded">{settingsState.temperature.toFixed(1)}</span>
                    </div>
                    <div class="relative h-6 flex items-center px-1 pt-2">
                        <input id="tempInput" type="range" bind:value={settingsState.temperature} min="0" max="2" step="0.1" class="w-full h-1.5 bg-slate-200 dark:bg-[#424859]/50 rounded-lg appearance-none cursor-pointer accent-indigo-700 dark:accent-[#74b0ff]" />
                    </div>
                    <div class="flex justify-between text-[10px] text-slate-400 dark:text-slate-500 uppercase font-bold tracking-tighter">
                        <span>Precise</span>
                        <span>Balanced</span>
                        <span>Creative</span>
                    </div>
                </section>
                
                <!-- SearxNG Deep Research Configuration -->
                <section class="space-y-4 pt-6 border-t border-slate-100 dark:border-[#424859]/20">
                    <div class="space-y-1">
                        <div class="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Deep Research (WAG) SearxNG Network</div>
                        <p class="text-xs text-slate-500 dark:text-slate-500 max-w-lg leading-relaxed">The Sovereign mesh utilizes these public P2P nodes to execute web scraping anonymously when search engines block direct traffic.</p>
                    </div>
                    
                    <div class="flex items-end gap-3 bg-slate-50 dark:bg-[#0c1324] border border-slate-100 dark:border-[#424859]/20 p-4 rounded-xl">
                        <div class="flex-1 space-y-1">
                            <label for="searxngInput" class="text-[10px] font-bold uppercase tracking-widest text-slate-500 dark:text-slate-400">Instance Domain / IP</label>
                            <input id="searxngInput" bind:value={newSearxngNode} 
                                onkeypress={(e) => e.key === 'Enter' && addSearxngNode()}
                                class="w-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-[#424859]/50 rounded-lg px-3 py-2 text-sm outline-none focus:border-indigo-500 dark:focus:border-[#74b0ff] focus:ring-2 focus:ring-indigo-500/20 font-mono transition-shadow placeholder:text-slate-300 dark:placeholder:text-slate-600 dark:text-slate-200" 
                                placeholder="https://paulgo.io" />
                        </div>
                        <button onclick={addSearxngNode} disabled={!newSearxngNode} class="px-5 py-2.5 bg-slate-800 dark:bg-slate-700 hover:bg-slate-900 dark:hover:bg-slate-600 border border-slate-800 dark:border-slate-600 text-white font-bold text-sm rounded-lg shadow-sm transition-colors flex items-center shrink-0 disabled:opacity-50 cursor-pointer">
                            <Plus class="w-4 h-4 mr-1.5"/> Add Node
                        </button>
                    </div>

                    {#if isLoadingSearxng}
                        <div class="py-2 text-left text-[11px] text-slate-400 dark:text-slate-500 font-bold animate-pulse uppercase tracking-wider">Scanning Internal SQLite DB...</div>
                    {:else if searxngNodes.length === 0}
                        <div class="py-3 px-4 text-xs font-semibold text-rose-500 dark:text-rose-400 bg-rose-50/50 dark:bg-rose-500/10 rounded-xl border border-rose-100 dark:border-rose-500/20 border-dashed">
                            Empty Table! The sovereign agent will fallback to <span class="underline">Hardcoded Default Engines</span>.
                        </div>
                    {:else}
                        <div class="flex flex-wrap gap-2">
                            {#each searxngNodes as node, i}
                                <div class="flex items-center gap-2 bg-indigo-50/50 dark:bg-indigo-500/10 border border-indigo-100 dark:border-indigo-500/20 pl-3 pr-1 py-1 rounded-lg hover:border-indigo-300 dark:hover:border-indigo-500/50 transition-colors">
                                    <span class="text-[13px] font-medium text-indigo-700 dark:text-[#74b0ff] font-mono select-all truncate max-w-[200px]">{node}</span>
                                    <button onclick={() => removeSearxngNode(i)} class="p-1.5 hover:bg-rose-100 dark:hover:bg-rose-500/20 rounded-md text-slate-400 dark:text-slate-500 hover:text-rose-600 dark:hover:text-rose-400 transition-colors cursor-pointer" title="Remove SearxNG Engine">
                                        <X class="w-3.5 h-3.5" />
                                    </button>
                                </div>
                            {/each}
                        </div>
                    {/if}
                </section>
            {/if}

            {#if activeTab === 'Cloud Mesh'}
                <section class="space-y-8">
                    <div class="flex items-center justify-between p-6 bg-indigo-50 dark:bg-indigo-500/5 border border-indigo-100 dark:border-indigo-500/20 rounded-2xl">
                        <div class="space-y-1">
                            <div class="flex items-center gap-2">
                                <Globe class="w-5 h-5 text-indigo-600 dark:text-[#74b0ff]" />
                                <h3 class="text-sm font-bold text-slate-800 dark:text-slate-200">OpenRouter Private Mesh</h3>
                            </div>
                            <p class="text-xs text-slate-500 dark:text-slate-400 max-w-sm">Enable this to route commercial models (GPT, Claude) through OpenRouter when local fallback is not desired.</p>
                        </div>
                        <label class="relative inline-flex items-center cursor-pointer">
                            <input type="checkbox" bind:checked={openRouterState.enabled} class="sr-only peer">
                            <div class="w-11 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer dark:bg-slate-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-indigo-600"></div>
                        </label>
                    </div>

                    <div class="space-y-6 {openRouterState.enabled ? 'opacity-100' : 'opacity-40 pointer-events-none transition-opacity'}">
                        <div class="space-y-2">
                            <label for="orApiKeyInput" class="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 flex items-center gap-2">
                                <ShieldCheck class="w-4 h-4" /> OpenRouter API Key
                            </label>
                            <div class="relative">
                                <input 
                                    id="orApiKeyInput"
                                    type="password" 
                                    bind:value={openRouterState.api_key} 
                                    class="w-full px-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-[#424859]/50 dark:text-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500/20 outline-none font-mono" 
                                    placeholder="sk-or-v1-..." 
                                />
                                <div class="absolute right-4 top-1/2 -translate-y-1/2 text-[10px] font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-widest bg-emerald-50 dark:bg-emerald-500/10 px-2 py-1 rounded">KMS Encrypted</div>
                            </div>
                            <p class="text-[10px] text-slate-400 dark:text-slate-500">Sua chave será criptografada via AES-256-GCM pelo Sovereign KMS antes de tocar o disco.</p>
                        </div>

                        <div class="space-y-2">
                            <label for="orModelInput" class="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Default Cloud Model</label>
                            <input 
                                id="orModelInput"
                                bind:value={openRouterState.default_model} 
                                class="w-full px-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-[#424859]/50 dark:text-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500/20 outline-none font-mono" 
                                placeholder="openai/gpt-4o-mini" 
                            />
                            <p class="text-[10px] text-slate-400 dark:text-slate-500">Ex: `anthropic/claude-3.5-sonnet`, `google/gemini-pro-1.5`, etc.</p>
                        </div>
                    </div>
                </section>
            {/if}

            {#if activeTab === 'Alibaba Qwen'}
                <section class="space-y-8">
                    <div class="flex items-center justify-between p-6 bg-orange-50 dark:bg-orange-500/5 border border-orange-100 dark:border-orange-500/20 rounded-2xl">
                        <div class="space-y-1">
                            <div class="flex items-center gap-2">
                                <Sparkles class="w-5 h-5 text-orange-600 dark:text-orange-400" />
                                <h3 class="text-sm font-bold text-slate-800 dark:text-slate-200">Alibaba Qwen (DashScope)</h3>
                            </div>
                            <p class="text-xs text-slate-500 dark:text-slate-400 max-w-sm">Use o poder dos modelos Qwen da Alibaba Cloud via API DashScope nativa.</p>
                        </div>
                        <label class="relative inline-flex items-center cursor-pointer">
                            <input type="checkbox" bind:checked={qwenState.enabled} class="sr-only peer">
                            <div class="w-11 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer dark:bg-slate-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-orange-600"></div>
                        </label>
                    </div>

                    <div class="space-y-6 {qwenState.enabled ? 'opacity-100' : 'opacity-40 pointer-events-none transition-opacity'}">
                        <div class="space-y-2">
                            <label for="qwenApiKeyInput" class="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 flex items-center gap-2">
                                <ShieldCheck class="w-4 h-4" /> DashScope API Key
                            </label>
                            <div class="relative">
                                <input 
                                    id="qwenApiKeyInput"
                                    type="password" 
                                    bind:value={qwenState.api_key} 
                                    class="w-full px-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-[#424859]/50 dark:text-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-orange-500/20 outline-none font-mono" 
                                    placeholder="sk-..." 
                                />
                                <div class="absolute right-4 top-1/2 -translate-y-1/2 text-[10px] font-bold text-orange-600 dark:text-orange-400 uppercase tracking-widest bg-orange-50 dark:bg-orange-500/10 px-2 py-1 rounded">KMS Protected</div>
                            </div>
                            <p class="text-[10px] text-slate-400 dark:text-slate-500">Chave protegida pelo Sovereign KMS (AES-256-GCM).</p>
                        </div>

                        <div class="space-y-2">
                            <label for="qwenModelInput" class="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Default Qwen Model</label>
                            <input 
                                id="qwenModelInput"
                                bind:value={qwenState.default_model} 
                                class="w-full px-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-[#424859]/50 dark:text-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-orange-500/20 outline-none font-mono" 
                                placeholder="qwen-plus" 
                            />
                            <p class="text-[10px] text-slate-400 dark:text-slate-500">Ex: `qwen-turbo`, `qwen-plus`, `qwen-max`, `qwen-long`.</p>
                        </div>
                    </div>
                    
                    <div class="p-4 bg-slate-50 dark:bg-[#0c1324] border border-slate-100 dark:border-[#424859]/20 rounded-xl">
                        <p class="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed italic">
                            * Note: Para usar estes modelos no chat, prefixe o nome do modelo com `qwen/` (ex: `qwen/qwen-max`) ou ative a opção "Alibaba Qwen" acima.
                        </p>
                    </div>
                </section>
            {/if}

            {#if activeTab === 'NVIDIA NIM'}
                <section class="space-y-8">
                    <div class="flex items-center justify-between p-6 bg-green-50 dark:bg-green-500/5 border border-green-100 dark:border-green-500/20 rounded-2xl">
                        <div class="space-y-1">
                            <div class="flex items-center gap-2">
                                <Cpu class="w-5 h-5 text-green-600 dark:text-green-400" />
                                <h3 class="text-sm font-bold text-slate-800 dark:text-slate-200">NVIDIA NIM (Accelerated Inference)</h3>
                            </div>
                            <p class="text-xs text-slate-500 dark:text-slate-400 max-w-sm">Acesse modelos de estado da arte otimizados pela NVIDIA via NIM API.</p>
                        </div>
                        <label class="relative inline-flex items-center cursor-pointer">
                            <input type="checkbox" bind:checked={nvidiaState.enabled} class="sr-only peer">
                            <div class="w-11 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer dark:bg-slate-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-green-600"></div>
                        </label>
                    </div>

                    <div class="space-y-6 {nvidiaState.enabled ? 'opacity-100' : 'opacity-40 pointer-events-none transition-opacity'}">
                        <div class="space-y-2">
                            <label for="nvidiaApiKeyInput" class="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 flex items-center gap-2">
                                <ShieldCheck class="w-4 h-4" /> NVIDIA API Key
                            </label>
                            <div class="relative">
                                <input 
                                    id="nvidiaApiKeyInput"
                                    type="password" 
                                    bind:value={nvidiaState.api_key} 
                                    class="w-full px-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-[#424859]/50 dark:text-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-green-500/20 outline-none font-mono" 
                                    placeholder="nvapi-..." 
                                />
                                <div class="absolute right-4 top-1/2 -translate-y-1/2 text-[10px] font-bold text-green-600 dark:text-green-400 uppercase tracking-widest bg-green-50 dark:bg-green-500/10 px-2 py-1 rounded">KMS Protected</div>
                            </div>
                            <p class="text-[10px] text-slate-400 dark:text-slate-500">Chave protegida pelo Sovereign KMS (AES-256-GCM).</p>
                        </div>

                        <div class="space-y-2">
                            <label for="nvidiaModelInput" class="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Default NIM Model</label>
                            <input 
                                id="nvidiaModelInput"
                                bind:value={nvidiaState.default_model} 
                                class="w-full px-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-[#424859]/50 dark:text-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-green-500/20 outline-none font-mono" 
                                placeholder="meta/llama-3.1-405b-instruct" 
                            />
                            <p class="text-[10px] text-slate-400 dark:text-slate-500">Ex: `meta/llama-3.1-405b-instruct`, `nvidia/llama-3.1-nemotron-70b-instruct`.</p>
                        </div>
                    </div>
                    
                    <div class="p-4 bg-slate-50 dark:bg-[#0c1324] border border-slate-100 dark:border-[#424859]/20 rounded-xl">
                        <p class="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed italic">
                            * Note: Para usar estes modelos no chat, prefixe o nome do modelo com `nvidia/` (ex: `nvidia/meta/llama-3.1-405b-instruct`).
                        </p>
                    </div>
                </section>
            {/if}

            {#if activeTab === 'Persona'}
                <!-- AI Personality -->
                <section class="space-y-4">
                    <div class="space-y-2">
                        <label for="personalityInput" class="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 flex items-center justify-between">
                            <span>Personality Name</span>
                            <select 
                                onchange={(e) => applyPreset((e.target as HTMLSelectElement).value)}
                                class="bg-transparent border-none text-xs text-indigo-600 dark:text-[#74b0ff] font-bold p-0 cursor-pointer outline-none hover:text-indigo-800 dark:hover:text-indigo-300 transition-colors"
                            >
                                <option value="" disabled selected>Load Preset...</option>
                                {#each PERSONA_PRESETS as p}
                                    <option value={p.name} class="text-slate-800">{p.name}</option>
                                {/each}
                            </select>
                        </label>
                        <input id="personalityInput" bind:value={settingsState.personalityName} class="w-full px-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-[#424859]/50 dark:text-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500/20 outline-none" type="text" />
                    </div>
                    <div class="space-y-2">
                        <label for="instructionsInput" class="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">System Instructions</label>
                        <textarea id="instructionsInput" bind:value={settingsState.systemInstructions} class="w-full px-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-[#424859]/50 dark:text-slate-200 rounded-xl text-sm leading-relaxed focus:ring-2 focus:ring-indigo-500/20 resize-y outline-none" rows="4"></textarea>
                    </div>
                    <!-- Additional Prompts -->
                    <div class="space-y-3 pt-2">
                        <label class="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Additional Context Prompts</label>
                        {#each settingsState.additionalPrompts as prompt, i}
                            <input bind:value={settingsState.additionalPrompts[i]} placeholder="E.g. Sempre responda em português do Brasil..." class="w-full px-4 py-2.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-[#424859]/50 dark:text-slate-200 rounded-lg text-sm outline-none focus:ring-1 focus:ring-indigo-500 dark:focus:ring-[#74b0ff]" type="text" />
                        {/each}
                    </div>
                </section>
                <!-- Behavior & Formality -->
                <section class="flex items-center justify-between p-4 bg-slate-50 dark:bg-[#0c1324] rounded-xl border border-slate-100 dark:border-[#424859]/20">
                    <div class="space-y-0.5">
                        <h4 class="text-sm font-bold text-slate-800 dark:text-slate-200">Behavior &amp; Formality</h4>
                        <p class="text-xs text-slate-500 dark:text-slate-400">Adjust the tone of voice for generated responses.</p>
                    </div>
                    <div class="flex p-1 bg-slate-200 dark:bg-slate-800 rounded-full">
                        <button onclick={() => settingsState.formality = 'Formal'} class="px-5 py-1.5 text-xs font-bold rounded-full transition-all cursor-pointer {settingsState.formality === 'Formal' ? 'bg-white dark:bg-slate-600 text-indigo-700 dark:text-white shadow-sm' : 'text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200'}">Formal</button>
                        <button onclick={() => settingsState.formality = 'Casual'} class="px-5 py-1.5 text-xs font-bold rounded-full transition-all cursor-pointer {settingsState.formality === 'Casual' ? 'bg-white dark:bg-slate-600 text-indigo-700 dark:text-white shadow-sm' : 'text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200'}">Casual</button>
                    </div>
                </section>
            {/if}

            {#if activeTab === 'Profile'}
                <section class="space-y-6">
                    <div class="grid grid-cols-2 gap-6">
                        <div class="space-y-2">
                            <label for="userNameInput" class="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Nickname / User Name</label>
                            <input id="userNameInput" bind:value={settingsState.userName} class="w-full px-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-[#424859]/50 dark:text-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500/20 outline-none" type="text" />
                        </div>
                        <div class="space-y-2">
                            <label for="userProfessionInput" class="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Profession / Role</label>
                            <input id="userProfessionInput" bind:value={settingsState.userProfession} class="w-full px-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-[#424859]/50 dark:text-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500/20 outline-none" type="text" />
                        </div>
                    </div>
                    
                    <div class="space-y-2 pt-2 border-t border-slate-100 dark:border-[#424859]/20">
                        <label for="aiNameInput" class="text-xs font-semibold tracking-wide text-indigo-700 dark:text-[#74b0ff]">Como você deseja chamar a sua IA?</label>
                        <input id="aiNameInput" bind:value={settingsState.aiName} placeholder="Ex: Sophy, Jarvis, Sovereign..." class="w-full px-4 py-3 bg-white dark:bg-slate-800 border border-slate-200 dark:border-[#424859]/50 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500/20 outline-none font-bold text-slate-700 dark:text-slate-200" type="text" />
                    </div>

                    <div class="space-y-4 pt-4 border-t border-slate-100 dark:border-[#424859]/20">
                        <div class="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Appearance (Theme Selection)</div>
                        <div class="grid grid-cols-2 gap-4">
                            <!-- Light Mode -->
                            <button onclick={() => settingsState.theme = 'Light Mode'} class="text-left relative cursor-pointer group border-2 {settingsState.theme === 'Light Mode' ? 'border-indigo-600 dark:border-[#74b0ff]' : 'border-slate-200 dark:border-[#424859]/50'} rounded-xl p-3 bg-slate-50 dark:bg-slate-800 transition-all hover:shadow-md">
                                <div class="flex items-center justify-between mb-3">
                                    <span class="text-xs font-bold text-slate-800 dark:text-slate-200">Light Mode</span>
                                    <div class="w-4 h-4 rounded-full border-4 {settingsState.theme === 'Light Mode' ? 'border-indigo-600 dark:border-[#74b0ff] bg-white ' : 'border-slate-300 dark:border-slate-500'}"></div>
                                </div>
                                <div class="space-y-2 opacity-70">
                                    <div class="h-2 w-full bg-slate-200 dark:bg-slate-600 rounded"></div>
                                    <div class="h-2 w-2/3 bg-slate-200 dark:bg-slate-600 rounded"></div>
                                </div>
                            </button>
                            <!-- Dark Mode -->
                            <button onclick={() => settingsState.theme = 'Dark Mode'} class="text-left relative cursor-pointer group border-2 {settingsState.theme === 'Dark Mode' ? 'border-indigo-500/50 dark:border-[#74b0ff]' : 'border-slate-700/30 dark:border-[#424859]/50'} rounded-xl p-3 bg-slate-800 dark:bg-[#080e1d] transition-all">
                                <div class="flex items-center justify-between mb-3">
                                    <span class="text-xs font-bold text-slate-200">Dark Mode <span class="text-[9px] text-slate-400 shadow-sm opacity-80">(Neural)</span></span>
                                    <div class="w-4 h-4 rounded-full border-4 {settingsState.theme === 'Dark Mode' ? 'border-indigo-500 dark:border-[#74b0ff] bg-slate-800' : 'border-slate-600 dark:border-[#424859]/50'}"></div>
                                </div>
                                <div class="space-y-2 opacity-50">
                                    <div class="h-2 w-full bg-slate-600 dark:bg-[#1d253b] rounded"></div>
                                    <div class="h-2 w-2/3 bg-slate-600 dark:bg-[#1d253b] rounded"></div>
                                </div>
                            </button>
                        </div>
                    </div>
                </section>
            {/if}
            
            {#if activeTab === 'Guardrails'}
                <section class="space-y-4">
                    <div class="flex items-center justify-between">
                        <div class="space-y-1">
                            <div class="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Active Security Filters</div>
                            <p class="text-xs text-slate-500 dark:text-slate-400">Regular expressions and keywords blocked locally by the Rust DevSecOps pipeline.</p>
                        </div>
                        <button onclick={() => settingsState.guardrails.push({type: 'keyword', value: '', description: ''})} class="flex items-center gap-1 px-3 py-1.5 bg-emerald-50 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 hover:bg-emerald-100 dark:hover:bg-emerald-500/20 rounded-lg text-xs font-bold transition-colors cursor-pointer">
                            <Plus class="w-4 h-4" /> Add Rule
                        </button>
                    </div>
                    <div class="space-y-3">
                        {#each settingsState.guardrails as rule, i}
                        <div class="flex items-start gap-3 p-3 bg-slate-50 dark:bg-[#0c1324] border border-slate-200 dark:border-[#424859]/20 rounded-xl relative group">
                            <select bind:value={rule.type} class="bg-white dark:bg-[#1d253b] border border-slate-200 dark:border-[#424859]/30 text-xs font-bold text-slate-700 dark:text-slate-300 rounded-lg px-2 py-2 outline-none focus:ring-2 focus:ring-indigo-500/20">
                                <option value="regex">Regex</option>
                                <option value="keyword">Keyword</option>
                            </select>
                            <div class="flex-1 space-y-2">
                                <input bind:value={rule.value} class="w-full bg-white dark:bg-[#1d253b] border border-slate-200 dark:border-[#424859]/30 text-sm font-mono text-slate-800 dark:text-slate-200 rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-indigo-500/20 dark:focus:border-[#74b0ff]" placeholder="Pattern or keyword..." />
                                <input bind:value={rule.description} class="w-full bg-transparent border-none text-xs text-slate-500 dark:text-slate-400 p-0 outline-none placeholder:text-slate-400 dark:placeholder:text-slate-600" placeholder="Description (e.g. Credit Card Format)..." />
                            </div>
                            <button onclick={() => settingsState.guardrails.splice(i, 1)} class="p-2 text-rose-400 hover:bg-rose-100 dark:hover:bg-rose-500/10 rounded-lg transition-colors cursor-pointer">
                                <Trash2 class="w-5 h-5" />
                            </button>
                        </div>
                        {/each}
                    </div>
                </section>
            {/if}

        </div>

        <!-- Modal Footer -->
        <div class="px-8 py-5 bg-slate-50/50 dark:bg-[#0c1324] border-t border-slate-200 dark:border-[#424859]/20 flex justify-end gap-3 shrink-0 transition-colors">
            <button onclick={closeModal} class="px-6 py-2.5 text-sm font-bold text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-800 hover:text-slate-800 dark:hover:text-slate-200 rounded-lg transition-colors cursor-pointer">
                Discard Changes
            </button>
            <button onclick={async () => { await saveSettings(); await saveOpenRouterSettings(); await saveQwenSettings(); await saveNvidiaSettings(); }} class="px-8 py-2.5 text-sm font-bold text-white bg-gradient-to-br from-indigo-700 to-indigo-800 dark:from-indigo-600 dark:to-indigo-500 rounded-lg shadow-lg hover:brightness-110 active:scale-[0.98] transition-all cursor-pointer">
                Save Engine Config
            </button>
        </div>
    </div>
</div>
{/if}
