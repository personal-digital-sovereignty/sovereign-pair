<script lang="ts">
  import { settingsState, saveSettings } from '$lib/settings.svelte';
  import { Settings, ChevronDown, ChevronsUpDown, X, Plus, Trash2 } from 'lucide-svelte';
  import { onMount } from 'svelte';
  
  let activeTab = $state('Engine'); // Engine, Persona, Guardrails, Profile
  let availableModels = $state<{name: string}[]>([]);

  onMount(async () => {
      try {
          const res = await fetch('http://localhost:38001/v1/settings/models');
          if (res.ok) {
              const data = await res.json();
              if (data.models) availableModels = data.models;
          }
      } catch(e) { console.error("Could not fetch models", e); }
  });
  
  function closeModal() {
      settingsState.isOpen = false;
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
<div class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-[2px]">
    <!-- Engine Settings Modal -->
    <div class="w-full max-w-2xl bg-[#ffffff] rounded-xl shadow-2xl border border-slate-200 flex flex-col max-h-[85vh] overflow-hidden">
        <!-- Modal Header -->
        <div class="px-8 py-6 flex items-center justify-between bg-slate-50/50">
            <div class="flex items-center gap-3">
                <div class="p-2 bg-indigo-50 rounded-lg">
                    <Settings class="w-6 h-6 text-indigo-700" />
                </div>
                <div>
                    <h2 class="text-xl font-bold text-slate-800 tracking-tight">Engine Settings</h2>
                    <p class="text-sm text-slate-500">Configure core RAG retrieval, Persona, and Security</p>
                </div>
            </div>
            <button onclick={closeModal} class="p-2 hover:bg-slate-200 rounded-full transition-colors">
                <X class="w-5 h-5 text-slate-500" />
            </button>
        </div>

        <!-- Tabs -->
        <div class="flex px-8 border-b border-slate-200 bg-slate-50/50">
            {#each ['Engine', 'Persona', 'Profile', 'Guardrails'] as tab}
                <button 
                    class="px-6 py-3 text-sm font-bold border-b-2 transition-colors {activeTab === tab ? 'border-indigo-700 text-indigo-800' : 'border-transparent text-slate-500 hover:text-slate-800'}"
                    onclick={() => activeTab = tab}
                >
                    {tab}
                </button>
            {/each}
        </div>

        <!-- Modal Content -->
        <div class="flex-1 overflow-y-auto p-8 space-y-10 custom-scrollbar">
            
            {#if activeTab === 'Engine'}
                <!-- Provider & Model Selection -->
                <section class="grid grid-cols-2 gap-6">
                    <div class="space-y-2">
                        <label class="text-xs font-semibold uppercase tracking-wider text-slate-500 flex items-center gap-2">
                            Provider
                        </label>
                        <div class="relative">
                            <button class="w-full flex items-center justify-between px-4 py-3 bg-slate-50 rounded-xl border border-slate-200 text-slate-800 text-sm font-medium">
                                <span class="flex items-center gap-2">
                                    <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
                                    {settingsState.provider}
                                </span>
                                <ChevronDown class="w-5 h-5 text-slate-400" />
                            </button>
                        </div>
                    </div>
                    <div class="space-y-2">
                        <label class="text-xs font-semibold uppercase tracking-wider text-slate-500 flex items-center gap-2">
                            Model Name
                        </label>
                        <div class="relative">
                            <select bind:value={settingsState.modelName} class="w-full px-4 py-3 pr-10 bg-white rounded-xl border border-indigo-200 text-slate-800 text-sm font-medium shadow-sm appearance-none outline-none focus:ring-2 focus:ring-indigo-500/20 cursor-pointer">
                                <option value={settingsState.modelName}>{settingsState.modelName}</option>
                                {#each availableModels as m}
                                    <option value={m.name}>{m.name}</option>
                                {/each}
                            </select>
                            <ChevronsUpDown class="w-5 h-5 text-indigo-700 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none" />
                        </div>
                    </div>
                </section>
                <!-- Temperature (Slider) -->
                <section class="space-y-4">
                    <div class="flex justify-between items-end">
                        <div class="space-y-1">
                            <label class="text-xs font-semibold uppercase tracking-wider text-slate-500">Temperature (Creativity)</label>
                            <p class="text-xs text-slate-500">Controls randomness: Lower is more focused and deterministic.</p>
                        </div>
                        <span class="text-sm font-mono font-bold text-indigo-800 bg-indigo-100 px-2 py-0.5 rounded">{settingsState.temperature.toFixed(1)}</span>
                    </div>
                    <div class="relative h-6 flex items-center px-1 pt-2">
                        <input type="range" bind:value={settingsState.temperature} min="0" max="2" step="0.1" class="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-indigo-700" />
                    </div>
                    <div class="flex justify-between text-[10px] text-slate-400 uppercase font-bold tracking-tighter">
                        <span>Precise</span>
                        <span>Balanced</span>
                        <span>Creative</span>
                    </div>
                </section>
            {/if}

            {#if activeTab === 'Persona'}
                <!-- AI Personality -->
                <section class="space-y-4">
                    <div class="space-y-2">
                        <label class="text-xs font-semibold uppercase tracking-wider text-slate-500 flex items-center justify-between">
                            <span>Personality Name</span>
                            <select 
                                onchange={(e) => applyPreset(e.target.value)}
                                class="bg-transparent border-none text-xs text-indigo-600 font-bold p-0 cursor-pointer outline-none hover:text-indigo-800 transition-colors"
                            >
                                <option value="" disabled selected>Load Preset...</option>
                                {#each PERSONA_PRESETS as p}
                                    <option value={p.name}>{p.name}</option>
                                {/each}
                            </select>
                        </label>
                        <input bind:value={settingsState.personalityName} class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500/20 outline-none" type="text" />
                    </div>
                    <div class="space-y-2">
                        <label class="text-xs font-semibold uppercase tracking-wider text-slate-500">System Instructions</label>
                        <textarea bind:value={settingsState.systemInstructions} class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm leading-relaxed focus:ring-2 focus:ring-indigo-500/20 resize-y outline-none" rows="4"></textarea>
                    </div>
                    <!-- Additional Prompts -->
                    <div class="space-y-3 pt-2">
                        <label class="text-xs font-semibold uppercase tracking-wider text-slate-500">Additional Context Prompts</label>
                        {#each settingsState.additionalPrompts as prompt, i}
                            <input bind:value={settingsState.additionalPrompts[i]} placeholder="E.g. Sempre responda em português do Brasil..." class="w-full px-4 py-2.5 bg-white border border-slate-200 rounded-lg text-sm outline-none focus:ring-1 focus:ring-indigo-500" type="text" />
                        {/each}
                    </div>
                </section>
                <!-- Behavior & Formality -->
                <section class="flex items-center justify-between p-4 bg-slate-50 rounded-xl border border-slate-100">
                    <div class="space-y-0.5">
                        <h4 class="text-sm font-bold text-slate-800">Behavior &amp; Formality</h4>
                        <p class="text-xs text-slate-500">Adjust the tone of voice for generated responses.</p>
                    </div>
                    <div class="flex p-1 bg-slate-200 rounded-full">
                        <button onclick={() => settingsState.formality = 'Formal'} class="px-5 py-1.5 text-xs font-bold rounded-full transition-all {settingsState.formality === 'Formal' ? 'bg-white text-indigo-700 shadow-sm' : 'text-slate-500 hover:text-slate-800'}">Formal</button>
                        <button onclick={() => settingsState.formality = 'Casual'} class="px-5 py-1.5 text-xs font-bold rounded-full transition-all {settingsState.formality === 'Casual' ? 'bg-white text-indigo-700 shadow-sm' : 'text-slate-500 hover:text-slate-800'}">Casual</button>
                    </div>
                </section>
            {/if}

            {#if activeTab === 'Profile'}
                <section class="space-y-6">
                    <div class="grid grid-cols-2 gap-6">
                        <div class="space-y-2">
                            <label class="text-xs font-semibold uppercase tracking-wider text-slate-500">Nickname / User Name</label>
                            <input bind:value={settingsState.userName} class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500/20 outline-none" type="text" />
                        </div>
                        <div class="space-y-2">
                            <label class="text-xs font-semibold uppercase tracking-wider text-slate-500">Profession / Role</label>
                            <input bind:value={settingsState.userProfession} class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500/20 outline-none" type="text" />
                        </div>
                    </div>
                    
                    <div class="space-y-2 pt-2 border-t border-slate-100">
                        <label class="text-xs font-semibold tracking-wide text-indigo-700">Como você deseja chamar a sua IA?</label>
                        <input bind:value={settingsState.aiName} placeholder="Ex: Sophy, Jarvis, Sovereign..." class="w-full px-4 py-3 bg-white border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500/20 outline-none font-bold text-slate-700" type="text" />
                    </div>

                    <div class="space-y-4 pt-4 border-t border-slate-100">
                        <label class="text-xs font-semibold uppercase tracking-wider text-slate-500">Appearance (Theme Selection)</label>
                        <div class="grid grid-cols-2 gap-4">
                            <!-- Light Mode -->
                            <button onclick={() => settingsState.theme = 'Light Mode'} class="text-left relative group border-2 {settingsState.theme === 'Light Mode' ? 'border-indigo-600' : 'border-slate-200'} rounded-xl p-3 bg-slate-50 transition-all hover:shadow-md">
                                <div class="flex items-center justify-between mb-3">
                                    <span class="text-xs font-bold text-slate-800">Light Mode</span>
                                    <div class="w-4 h-4 rounded-full border-4 {settingsState.theme === 'Light Mode' ? 'border-indigo-600 bg-white' : 'border-slate-300'}"></div>
                                </div>
                                <div class="space-y-2 opacity-70">
                                    <div class="h-2 w-full bg-slate-200 rounded"></div>
                                    <div class="h-2 w-2/3 bg-slate-200 rounded"></div>
                                </div>
                            </button>
                            <!-- Dark Mode -->
                            <button onclick={() => settingsState.theme = 'Dark Mode'} class="text-left relative group border-2 {settingsState.theme === 'Dark Mode' ? 'border-indigo-500/50' : 'border-slate-700/30'} rounded-xl p-3 bg-slate-800 transition-all">
                                <div class="flex items-center justify-between mb-3">
                                    <span class="text-xs font-bold text-slate-200">Dark Mode <span class="text-[9px] text-slate-400 opacity-80">(WIP)</span></span>
                                    <div class="w-4 h-4 rounded-full border-4 {settingsState.theme === 'Dark Mode' ? 'border-indigo-500 bg-slate-800' : 'border-slate-600'}"></div>
                                </div>
                                <div class="space-y-2 opacity-50">
                                    <div class="h-2 w-full bg-slate-600 rounded"></div>
                                    <div class="h-2 w-2/3 bg-slate-600 rounded"></div>
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
                            <label class="text-xs font-semibold uppercase tracking-wider text-slate-500">Active Security Filters</label>
                            <p class="text-xs text-slate-500">Regular expressions and keywords blocked locally by the Rust DevSecOps pipeline.</p>
                        </div>
                        <button onclick={() => settingsState.guardrails.push({type: 'keyword', value: '', description: ''})} class="flex items-center gap-1 px-3 py-1.5 bg-emerald-50 text-emerald-700 hover:bg-emerald-100 rounded-lg text-xs font-bold transition-colors">
                            <Plus class="w-4 h-4" /> Add Rule
                        </button>
                    </div>
                    <div class="space-y-3">
                        {#each settingsState.guardrails as rule, i}
                        <div class="flex items-start gap-3 p-3 bg-slate-50 border border-slate-200 rounded-xl relative group">
                            <select bind:value={rule.type} class="bg-white border border-slate-200 text-xs font-bold text-slate-700 rounded-lg px-2 py-2 outline-none focus:ring-2 focus:ring-indigo-500/20">
                                <option value="regex">Regex</option>
                                <option value="keyword">Keyword</option>
                            </select>
                            <div class="flex-1 space-y-2">
                                <input bind:value={rule.value} class="w-full bg-white border border-slate-200 text-sm font-mono text-slate-800 rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-indigo-500/20" placeholder="Pattern or keyword..." />
                                <input bind:value={rule.description} class="w-full bg-transparent border-none text-xs text-slate-500 p-0 outline-none placeholder:text-slate-400" placeholder="Description (e.g. Credit Card Format)..." />
                            </div>
                            <button onclick={() => settingsState.guardrails.splice(i, 1)} class="p-2 text-rose-400 hover:bg-rose-100 rounded-lg transition-colors">
                                <Trash2 class="w-5 h-5" />
                            </button>
                        </div>
                        {/each}
                    </div>
                </section>
            {/if}

        </div>

        <!-- Modal Footer -->
        <div class="px-8 py-5 bg-slate-50/50 border-t border-slate-200 flex justify-end gap-3 shrink-0">
            <button onclick={closeModal} class="px-6 py-2.5 text-sm font-bold text-slate-600 hover:bg-slate-200 rounded-lg transition-colors">
                Discard Changes
            </button>
            <button onclick={saveSettings} class="px-8 py-2.5 text-sm font-bold text-white bg-gradient-to-br from-indigo-700 to-indigo-800 rounded-lg shadow-lg hover:brightness-110 active:scale-[0.98] transition-all">
                Save Engine Config
            </button>
        </div>
    </div>
</div>
{/if}
