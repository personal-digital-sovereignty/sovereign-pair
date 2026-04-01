<script lang="ts">
    import { onMount, onDestroy } from 'svelte';

    // Types matching our exact Rust schema
    interface RoutingRule {
        id: string;
        name: string;
        target_model: string;
        latency_badge: string;
        icon: string;
        is_active: boolean;
        order_index: number;
    }

    interface RemoteModel {
        id: string;
        name: string;
        provider: string;
        icon_url: string | null;
        latency_ms: number;
        cost_per_1k: number;
        success_rate: number;
        status: string;
    }

    let rules = $state<RoutingRule[]>([]);
    let models = $state<RemoteModel[]>([]);
    let is_loading = $state(true);
    let routing_active = $state(true);

    let isNewRuleModalOpen = $state(false);
    let isNewModelModalOpen = $state(false);

    let newRule = $state({name: '', target_model: '', latency_badge: '', icon: 'api'});
    let newModel = $state({name: '', provider: '', latency_ms: 100, cost_per_1k: 0.0});

    async function deleteRule(id: string) {
        if(!confirm("Tem certeza que deseja remover esta regra de roteamento?")) return;
        await fetch(`http://localhost:38001/v1/engineer/rag/rules/${id}`, { method: 'DELETE' });
        fetchData();
    }

    async function deleteModel(id: string) {
        if(!confirm("Tem certeza que deseja remover este modelo remoto da arquitetura?")) return;
        await fetch(`http://localhost:38001/v1/engineer/rag/models/${id}`, { method: 'DELETE' });
        fetchData();
    }

    async function saveRule() {
        await fetch(`http://localhost:38001/v1/engineer/rag/rules`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(newRule)
        });
        isNewRuleModalOpen = false;
        fetchData();
    }

    async function saveModel() {
        await fetch(`http://localhost:38001/v1/engineer/rag/models`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(newModel)
        });
        isNewModelModalOpen = false;
        fetchData();
    }

    async function fetchData() {
        try {
            const resRules = await fetch('http://localhost:38001/v1/engineer/rag/rules');
            if(resRules.ok) rules = await resRules.json();

            const resModels = await fetch('http://localhost:38001/v1/engineer/rag/models');
            if(resModels.ok) models = await resModels.json();
        } catch(e) {
            console.error("Failed to load RAG engine data", e);
        } finally {
            is_loading = false;
        }
    }

    onMount(() => {
        fetchData();
        // Setup rapid polling to mimic real-time resilience telemetry
        const interval = setInterval(fetchData, 5000);
        return () => clearInterval(interval);
    });
</script>

<!-- Header Section -->
<header class="h-20 border-b border-slate-200/60 dark:border-slate-800/60 bg-white dark:bg-[#12192b] flex items-center px-6 shrink-0 justify-between mb-8 rounded-2xl shadow-sm border transition-colors">
    <div class="flex items-center gap-4">
        <div class="bg-indigo-600/10 p-2.5 rounded-xl border border-indigo-100/50">
            <svg class="w-6 h-6 text-indigo-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="4.5" r="2.5"/><path d="m10.2 6.3-3.9 3.9"/><circle cx="4.5" cy="12" r="2.5"/><path d="M7 12h10"/><circle cx="19.5" cy="12" r="2.5"/><path d="m13.8 17.7 3.9-3.9"/><circle cx="12" cy="19.5" r="2.5"/></svg>
        </div>
        <div class="flex flex-col">
            <div class="flex items-center gap-2">
                <h1 class="text-lg font-bold tracking-tight text-slate-800">Model Router & Resilience</h1>
                <span class="px-2 py-0.5 bg-emerald-100/50 text-emerald-700 text-[9px] uppercase tracking-widest font-bold rounded-full border border-emerald-200/50">ACTIVE</span>
            </div>
            <span class="text-xs text-slate-500 font-medium">Gerencie o tráfego de IA com roteamento inteligente entre modelos locais e em nuvem para otimizar custo e latência.</span>
        </div>
    </div>
</header>

<!-- Top Grid: Routing Rules & Real-time Monitor -->
<div class="grid grid-cols-12 gap-8 mb-8 font-inter">
    
    <!-- Section 1: Regras de Roteamento -->
    <section class="col-span-12 lg:col-span-7 bg-white dark:bg-[#12192b] shadow-sm rounded-2xl p-8 border border-slate-100 dark:border-slate-800/50 transition-colors">
        <div class="flex justify-between items-center mb-6">
            <div>
                <h3 class="text-xl font-bold text-indigo-900 font-manrope">Regras de Roteamento</h3>
                <p class="text-sm text-slate-500">Defina a lógica de distribuição baseada em complexidade</p>
            </div>
            
            <label class="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" bind:checked={routing_active} class="sr-only peer">
                <div class="w-11 h-6 bg-slate-300 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                <span class="ms-3 text-sm font-medium text-on-surface">Ativo</span>
            </label>
        </div>

        <div class="space-y-4">
            {#if is_loading}
                <div class="animate-pulse w-full h-20 bg-surface-variant rounded-xl"></div>
                <div class="animate-pulse w-full h-20 bg-surface-variant rounded-xl"></div>
            {:else}
                {#each rules as rule}
                <!-- Rule Card -->
                <div class="bg-surface-container-lowest p-5 rounded-xl flex items-center justify-between group hover:shadow-sm transition-all border border-outline-variant/10">
                    <div class="flex items-center gap-4">
                        <div class="p-3 bg-primary-container/10 text-primary rounded-lg">
                            <svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="10" rx="2"/><circle cx="12" cy="5" r="2"/><path d="M12 7v4"/><line x1="8" y1="16" x2="8.01" y2="16"/><line x1="16" y1="16" x2="16.01" y2="16"/></svg>
                        </div>
                        <div>
                            <p class="font-bold text-on-surface">{rule.name}</p>
                            <p class="text-xs text-on-surface-variant">{rule.target_model}</p>
                        </div>
                    </div>
                    <div class="flex items-center gap-3">
                        <span class="text-xs font-semibold px-2 py-1 bg-primary-fixed text-on-primary-fixed-variant rounded uppercase tracking-wider mr-2">{rule.latency_badge}</span>
                        <button aria-label="Edit" class="text-indigo-400 hover:text-indigo-600 transition-colors cursor-pointer px-1 py-1 rounded hover:bg-indigo-50" onclick={() => alert('Edição em breve')} title="Editar Regra">
                            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
                        </button>
                        <button aria-label="Delete" class="text-rose-400 hover:text-rose-600 transition-colors cursor-pointer px-1 py-1 rounded hover:bg-rose-50" onclick={() => deleteRule(rule.id)} title="Remover Regra">
                            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"></path><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"></path><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>
                        </button>
                        <svg class="w-5 h-5 text-slate-400 cursor-grab active:cursor-grabbing ml-1" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="12" r="1"></circle><circle cx="9" cy="5" r="1"></circle><circle cx="9" cy="19" r="1"></circle><circle cx="15" cy="12" r="1"></circle><circle cx="15" cy="5" r="1"></circle><circle cx="15" cy="19" r="1"></circle></svg>
                    </div>
                </div>
                {/each}
            {/if}

            <button onclick={() => isNewRuleModalOpen = true} class="w-full py-3 border-2 border-dashed border-outline-variant rounded-xl text-on-surface-variant text-sm font-medium hover:bg-white transition-colors cursor-pointer">
                + Adicionar Nova Regra de Lógica
            </button>
        </div>
    </section>

    <!-- Section 2: Monitor de Auto-Fallback -->
    <section class="col-span-12 lg:col-span-5 bg-gradient-to-b from-white dark:from-[#12192b] to-slate-50/50 dark:to-[#0c1324]/50 shadow-sm rounded-2xl p-8 border border-slate-100 dark:border-slate-800/50 transition-colors">
        <h3 class="text-xl font-bold text-indigo-900 mb-6 font-manrope">Monitor de Auto-Fallback</h3>
        
        <!-- Fallback Alert Card -->
        <div class="bg-gradient-to-r from-slate-50 to-slate-100/50 border border-slate-200/60 p-5 rounded-xl mb-6 flex items-start gap-4 shadow-sm">
            <svg class="w-6 h-6 text-slate-400 mt-0.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
            <div>
                <p class="text-sm font-bold text-slate-700">All Systems Stable</p>
                <p class="text-xs text-slate-500 mt-0.5">No automatic fallback actions detected in the last 24 hours.</p>
            </div>
        </div>

        <!-- Health Status List -->
        <div class="space-y-4">
            {#each models as model}
            <div class="flex items-center justify-between p-3 bg-white dark:bg-[#0c1324] rounded-lg border border-transparent dark:border-slate-800/50 transition-colors">
                <div class="flex items-center gap-3">
                    {#if model.status === 'Operational'}
                        <div class="w-2 h-2 rounded-full bg-on-tertiary-container shadow-[0_0_8px_rgba(79,175,110,0.6)]"></div>
                    {:else}
                        <div class="w-2 h-2 rounded-full bg-error shadow-[0_0_8px_rgba(186,26,26,0.6)] animate-pulse"></div>
                    {/if}
                    <span class="text-sm font-medium">{model.name}</span>
                </div>
                {#if model.status === 'Operational'}
                    <span class="text-xs text-on-surface-variant">Operational</span>
                {:else}
                    <span class="text-xs text-error font-semibold">{model.status}</span>
                {/if}
            </div>
            {/each}
        </div>

        <!-- Traffic Visualizer -->
        <div class="mt-8 pt-6 border-t border-slate-200/60">
            <p class="text-[10px] font-bold text-slate-400 mb-4 uppercase tracking-widest">Tráfego em Tempo Real</p>
            <div class="flex items-end gap-2 h-16 opacity-30 grayscale">
                <div class="w-full bg-slate-200 h-[10%] rounded pointer-events-none transition-all duration-500"></div>
                <div class="w-full bg-slate-200 h-[20%] rounded pointer-events-none transition-all duration-500"></div>
                <div class="w-full bg-slate-200 h-[15%] rounded pointer-events-none transition-all duration-500"></div>
                <div class="w-full bg-slate-200 h-[5%] rounded pointer-events-none transition-all duration-500"></div>
                <div class="w-full bg-slate-200 h-[10%] rounded pointer-events-none transition-all duration-500"></div>
                <div class="w-full bg-slate-200 h-[25%] rounded pointer-events-none transition-all duration-500"></div>
                <div class="w-full bg-slate-200 h-[10%] rounded pointer-events-none transition-all duration-500"></div>
            </div>
        </div>
    </section>
</div>

<!-- Section 3: Gestão de Modelos Remotos -->
<section class="bg-white dark:bg-[#12192b] border border-slate-100 dark:border-slate-800/50 rounded-2xl p-8 shadow-sm font-inter transition-colors">
    <div class="flex justify-between items-end mb-8">
        <div>
            <h3 class="text-2xl font-bold text-slate-800 font-manrope">Gestão de Modelos Remotos</h3>
            <p class="text-slate-500 text-sm mt-1">Controle custos, performance e disponibilidade de endpoints externos.</p>
        </div>
        <button onclick={() => isNewModelModalOpen = true} class="bg-indigo-50 text-indigo-700 px-5 py-2.5 rounded-xl font-bold text-sm flex items-center gap-2 hover:bg-indigo-100 hover:text-indigo-800 transition-all border border-indigo-100/50 cursor-pointer">
            Novo Modelo / API Key
        </button>
    </div>
    
    <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
            <thead>
                <tr class="border-b border-outline-variant/30">
                    <th class="pb-4 font-manrope font-bold text-sm text-on-surface-variant">MODELO</th>
                    <th class="pb-4 font-manrope font-bold text-sm text-on-surface-variant text-center">LATÊNCIA</th>
                    <th class="pb-4 font-manrope font-bold text-sm text-on-surface-variant text-center">CUSTO / 1K TOKENS</th>
                    <th class="pb-4 font-manrope font-bold text-sm text-on-surface-variant text-center">TAXA SUCESSO</th>
                    <th class="pb-4 font-manrope font-bold text-sm text-on-surface-variant text-right">STATUS</th>
                </tr>
            </thead>
            <tbody class="divide-y divide-outline-variant/10">
                {#if is_loading}
                    <tr><td colspan="5" class="py-10 text-center text-slate-400">Scanning mesh edges...</td></tr>
                {:else}
                    {#each models as model}
                    <tr class="group hover:bg-surface-container-low/50 transition-colors">
                        <td class="py-5">
                            <div class="flex items-center gap-3">
                                {#if model.icon_url}
                                    <img src={model.icon_url} alt="{model.name} logo" class="w-8 h-8 rounded bg-slate-100 object-contain" />
                                {:else}
                                    <div class="w-8 h-8 rounded bg-primary text-white flex items-center justify-center font-bold text-[10px]">
                                        {model.name.substring(0, 2).toUpperCase()}
                                    </div>
                                {/if}
                                <div>
                                    <p class="font-bold text-on-surface">{model.name}</p>
                                    <p class="text-xs text-on-surface-variant">{model.provider}</p>
                                </div>
                            </div>
                        </td>
                        <td class="py-5 text-center">
                            <span class="font-body text-sm font-medium">
                                {model.latency_ms >= 1000 ? (model.latency_ms / 1000).toFixed(1) + 's' : model.latency_ms + 'ms'}
                            </span>
                        </td>
                        <td class="py-5 text-center text-sm">
                            <span class="font-bold">${model.cost_per_1k.toFixed(3)}</span>
                        </td>
                        <td class="py-5 text-center">
                            <div class="w-24 bg-surface-container h-1.5 rounded-full mx-auto overflow-hidden">
                                <div class="bg-on-tertiary-container h-full" style="width: {model.success_rate * 100}%"></div>
                            </div>
                            <span class="text-[10px] font-bold text-on-tertiary-fixed-variant">{(model.success_rate * 100).toFixed(1)}%</span>
                        </td>
                        <td class="py-5 text-right">
                            <span class="px-3 py-1 bg-tertiary-container/20 text-on-tertiary-fixed-variant rounded-full text-xs font-bold uppercase mr-2">
                                {model.status}
                            </span>
                            <button aria-label="Edit" class="text-indigo-400 hover:text-indigo-600 transition-colors cursor-pointer px-2 py-2 rounded hover:bg-indigo-50 align-middle" onclick={() => alert('Edição em breve')} title="Editar Modelo">
                                <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
                            </button>
                            <button aria-label="Delete" class="text-rose-400 hover:text-rose-600 transition-colors cursor-pointer px-2 py-2 rounded hover:bg-rose-50 align-middle" onclick={() => deleteModel(model.id)} title="Remover Modelo">
                                <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"></path><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"></path><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>
                            </button>
                        </td>
                    </tr>
                    {/each}
                {/if}
            </tbody>
        </table>
    </div>
</section>



<!-- Modals -->
{#if isNewRuleModalOpen}
<div class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm">
    <div class="bg-white dark:bg-[#12192b] rounded-2xl p-8 w-full max-w-lg shadow-2xl relative font-inter border border-slate-100 dark:border-slate-700">
        <h3 class="text-2xl font-bold text-indigo-950 mb-6 font-manrope">Nova Regra de Lógica</h3>
        
        <div class="space-y-4">
            <div>
                <label for="ruleName" class="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-1.5">Intenção / Gatilho</label>
                <input id="ruleName" bind:value={newRule.name} type="text" placeholder="Ex: Financeiro / Planilhas" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-indigo-500/20 outline-none font-medium text-slate-700">
            </div>
            <div>
                <label for="ruleTarget" class="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-1.5">Modelo Alvo (Target)</label>
                <input id="ruleTarget" bind:value={newRule.target_model} type="text" placeholder="Ex: Llama-3-70B (Local GPU)" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-indigo-500/20 outline-none font-medium text-slate-700">
            </div>
            <div class="grid grid-cols-2 gap-4">
                <div>
                    <label for="ruleBadge" class="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-1.5">Badge de Promessa</label>
                    <input id="ruleBadge" bind:value={newRule.latency_badge} type="text" placeholder="Ex: Alta Inteligência" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-indigo-500/20 outline-none font-medium text-slate-700">
                </div>
                <div>
                    <label for="ruleIcon" class="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-1.5">Ícone Material</label>
                    <input id="ruleIcon" bind:value={newRule.icon} type="text" placeholder="Ex: database" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-indigo-500/20 outline-none font-medium material-symbols-outlined text-slate-700">
                </div>
            </div>
        </div>

        <div class="mt-8 flex justify-end gap-3">
            <button onclick={() => isNewRuleModalOpen = false} class="px-6 py-2.5 rounded-xl font-bold text-slate-500 hover:bg-slate-100 transition-colors cursor-pointer">Cancelar</button>
            <button onclick={saveRule} class="px-8 py-2.5 rounded-xl font-bold text-white bg-indigo-600 hover:bg-indigo-700 transition-colors shadow-lg shadow-indigo-600/30 cursor-pointer">Criar Regra</button>
        </div>
    </div>
</div>
{/if}

{#if isNewModelModalOpen}
<div class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm">
    <div class="bg-white dark:bg-[#12192b] rounded-2xl p-8 w-full max-w-lg shadow-2xl relative font-inter border border-slate-100 dark:border-slate-700">
        <h3 class="text-2xl font-bold text-indigo-950 mb-6 font-manrope">Acoplar Novo Modelo API</h3>
        
        <div class="space-y-4">
            <div>
                <label for="modelName" class="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-1.5">Nome do Modelo</label>
                <input id="modelName" bind:value={newModel.name} type="text" placeholder="Ex: Claude 3.5 Sonnet" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-indigo-500/20 outline-none font-medium text-slate-700">
            </div>
            <div>
                <label for="modelProvider" class="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-1.5">Provedor / API Route</label>
                <input id="modelProvider" bind:value={newModel.provider} type="text" placeholder="Ex: Anthropic REST API" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-indigo-500/20 outline-none font-medium text-slate-700">
            </div>
            <div class="grid grid-cols-2 gap-4">
                <div>
                    <label for="modelLatency" class="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-1.5">Latência Esperada (ms)</label>
                    <input id="modelLatency" bind:value={newModel.latency_ms} type="number" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-indigo-500/20 outline-none font-medium text-amber-600 font-mono">
                </div>
                <div>
                    <label for="modelCost" class="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-1.5">Custo p/ 1k Tokens ($)</label>
                    <input id="modelCost" bind:value={newModel.cost_per_1k} type="number" step="0.001" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-indigo-500/20 outline-none font-medium text-emerald-600 font-mono">
                </div>
            </div>
        </div>

        <div class="mt-8 flex justify-end gap-3">
            <button onclick={() => isNewModelModalOpen = false} class="px-6 py-2.5 rounded-xl font-bold text-slate-500 hover:bg-slate-100 transition-colors cursor-pointer">Cancelar</button>
            <button onclick={saveModel} class="px-8 py-2.5 rounded-xl font-bold text-white bg-indigo-600 hover:bg-indigo-700 transition-colors shadow-lg shadow-indigo-600/30 cursor-pointer">Acoplar Modelo</button>
        </div>
    </div>
</div>
{/if}
