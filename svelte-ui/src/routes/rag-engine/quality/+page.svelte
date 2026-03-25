<script lang="ts">
    import { onMount, onDestroy } from 'svelte';

    interface KnowledgeGap {
        id: string;
        query: string;
        frequency: number;
        context: string;
        sentiment: string;
        status?: string;
        resolution_content?: string;
    }

    interface RadarMetrics {
        global_score: number;
        faithfulness: number;
        precision: number;
    }

    let gaps = $state<KnowledgeGap[]>([]);
    let currentTab = $state<'pending' | 'resolved'>('pending');
    let expandedGapId = $state<string | null>(null);
    let radar = $state<RadarMetrics>({ global_score: 0, faithfulness: 0, precision: 0 });
    let is_loading = $state(true);

    let filteredGaps = $derived(gaps.filter(g => currentTab === 'pending' ? (g.status === 'pending' || !g.status) : g.status === 'resolved'));

    async function fetchData() {
        try {
            const [resGaps, resRadar] = await Promise.all([
                fetch('http://localhost:38001/v1/rag-engine/gaps'),
                fetch('http://localhost:38001/v1/rag-engine/radar')
            ]);
            
            if(resRadar.ok) radar = await resRadar.json();
            if(resGaps.ok) gaps = await resGaps.json();
        } catch(e) {
            console.error("Failed to load RAG Quality Data", e);
        } finally {
            is_loading = false;
        }
    }

    onMount(() => {
        fetchData();
        const interval = setInterval(fetchData, 10000); // 10s mesh loop polling
        return () => clearInterval(interval);
    });

    const getSentimentColor = (sentiment: string) => {
        if(sentiment === 'Frustrated' || sentiment === 'Angry') return 'text-rose-500';
        if(sentiment === 'Neutral') return 'text-slate-400';
        return 'text-blue-500';
    };
    
    const getSentimentIcon = (sentiment: string) => {
        if(sentiment === 'Frustrated' || sentiment === 'Angry') return 'sentiment_dissatisfied';
        if(sentiment === 'Frustrated' || sentiment === 'Angry') return 'sentiment_dissatisfied';
        if(sentiment === 'Neutral') return 'sentiment_neutral';
        return 'sentiment_satisfied';
    };

    async function handleInjectContent(gap: KnowledgeGap) {
        const content = prompt(`Inject raw context for the unresolved query:\n"${gap.query}"\n\nPaste plaintext below. It will be vectorized instantly.`);
        if (!content) return;
        
        // Rapid optimistic UI update (Move to solved tab)
        const previousState = [...gaps];
        gaps = gaps.map(g => g.id === gap.id ? { ...g, status: 'resolved', resolution_content: content } : g);

        try {
            const safeGapId = "Gap_" + gap.id.substring(0, 8);
            const fileName = `${safeGapId}.md`;
            
            // 1. Escreve diretamente no O.S (Vault Master Markdown Root)
            const mdPayload = `# Knowledge Resolution: ${safeGapId}\n\n**Unresolved User Query:**\n${gap.query}\n\n**Operator Context Injection:**\n${content}`;
            await fetch(`http://localhost:38001/v1/vault/document/${encodeURIComponent(fileName)}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ workspace_id: 1, content: mdPayload })
            });

            // 2. Registra o Dual-Truth Soft Delete na Memória SQLite
            await fetch(`http://localhost:38001/v1/rag-engine/gaps/${gap.id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ resolution_content: content })
            });
            
        } catch(e) {
            console.error("Failed to inject context into the vault", e);
            gaps = previousState; // Revert UI optimism on error
            alert("Falha Cíbrida ao salvar documento .md e sincronizar o SQLite.");
        }
    }

    async function handleHardDelete(gap: KnowledgeGap) {
        if(!confirm("Tem certeza que deseja aniquilar este log permanentemente? (O arquivo físico .md não será apagado do Vault)")) return;
        
        const previousState = [...gaps];
        gaps = gaps.filter(g => g.id !== gap.id);

        try {
            await fetch(`http://localhost:38001/v1/rag-engine/gaps/${gap.id}`, { method: 'DELETE' });
        } catch(e) {
            console.error("Failed to Hard Delete gap", e);
            gaps = previousState;
        }
    }
</script>

<header class="h-20 border-b border-slate-200/60 bg-white flex items-center px-6 shrink-0 justify-between mb-8 rounded-2xl shadow-sm border">
    <div class="flex items-center gap-4">
        <div class="bg-emerald-600/10 p-2.5 rounded-xl border border-emerald-100/50">
            <svg class="w-6 h-6 text-emerald-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20V10"/><path d="M18 20V4"/><path d="M6 20v-4"/></svg>
        </div>
        <div class="flex flex-col">
            <div class="flex items-center gap-2">
                <h1 class="text-lg font-bold tracking-tight text-slate-800">Quality & Alignment</h1>
                <span class="px-2 py-0.5 bg-indigo-100/50 text-indigo-700 text-[9px] uppercase tracking-widest font-bold rounded-full border border-indigo-200/50">REPORT</span>
            </div>
            <span class="text-xs text-slate-500 font-medium">Monitor RAG performance, detect hallucination patterns, and bridge organizational knowledge gaps.</span>
        </div>
    </div>
    
    <div class="flex items-center gap-3">
        <div class="bg-indigo-50 px-4 py-2 rounded-xl flex items-center gap-2 border border-indigo-100/50">
            <div class="w-2 h-2 rounded-full bg-indigo-500 animate-pulse"></div>
            <span class="text-xs font-bold text-indigo-700">System Optimal</span>
        </div>
        <button onclick={() => window.print()} class="bg-white shadow-sm border border-slate-200 px-4 py-2 rounded-xl text-xs font-bold text-slate-700 flex items-center gap-2 hover:bg-slate-50 transition-colors">
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" x2="12" y1="15" y2="3"></line></svg>
            Export PDF
        </button>
    </div>
</header>

<div class="grid grid-cols-12 gap-6 font-inter">
    <!-- Hallucination Radar (LLM-as-a-Judge) -->
    <div class="col-span-12 lg:col-span-5 bg-gradient-to-br from-slate-900 to-slate-800 rounded-3xl p-8 flex flex-col relative overflow-hidden group shadow-lg">
        <div class="relative z-10">
            <div class="flex justify-between items-start mb-10">
                <div>
                    <h3 class="font-manrope font-bold text-xl text-white">Hallucination Radar</h3>
                    <p class="text-xs text-slate-400 mt-1">Grounded Confidence Index</p>
                </div>
                <div class="w-12 h-12 rounded-2xl bg-white/10 flex items-center justify-center backdrop-blur-md"></div>
            </div>
            
            <div class="flex flex-col items-center justify-center py-4">
                <div class="relative w-48 h-48 flex items-center justify-center">
                    <svg class="w-full h-full -rotate-90">
                        <circle class="text-white/10" cx="96" cy="96" fill="transparent" r="88" stroke="currentColor" stroke-width="8"></circle>
                        <circle class="text-indigo-400 transition-all duration-1000 ease-in-out" cx="96" cy="96" fill="transparent" r="88" stroke="currentColor" stroke-dasharray="553" stroke-dashoffset={553 - (553 * radar.global_score) / 100} stroke-linecap="round" stroke-width="12"></circle>
                    </svg>
                    <div class="absolute inset-0 flex flex-col items-center justify-center">
                        <span class="text-5xl font-manrope font-extrabold text-white">
                            {#if is_loading}<span class="animate-pulse opacity-50">...</span>{:else}{radar.global_score}{/if}
                        </span>
                        <span class="text-[10px] uppercase font-bold text-slate-400 tracking-widest mt-1">Score</span>
                    </div>
                </div>
                
                <div class="mt-8 grid grid-cols-2 gap-8 w-full">
                    <div class="text-center bg-white/5 rounded-2xl py-3 backdrop-blur-sm">
                        <div class="text-2xl font-bold text-emerald-400">
                            {#if is_loading}<span class="animate-pulse">--</span>{:else}{radar.faithfulness}%{/if}
                        </div>
                        <div class="text-[10px] text-slate-300 font-medium uppercase tracking-wider mt-1">Faithfulness</div>
                    </div>
                    <div class="text-center bg-white/5 rounded-2xl py-3 backdrop-blur-sm">
                        <div class="text-2xl font-bold {radar.precision > 80 ? 'text-indigo-300' : 'text-amber-300'}">
                            {#if is_loading}<span class="animate-pulse">--</span>{:else}{radar.precision}%{/if}
                        </div>
                        <div class="text-[10px] text-slate-300 font-medium uppercase tracking-wider mt-1">Precision</div>
                    </div>
                </div>
            </div>
        </div>
        <div class="absolute -right-16 -bottom-16 w-64 h-64 bg-indigo-500/20 rounded-full blur-3xl opacity-50 group-hover:scale-110 transition-transform duration-700"></div>
    </div>

    <!-- Intent Clustering (Heatmap/Trends) -->
    <div class="col-span-12 lg:col-span-7 bg-white rounded-3xl p-8 border border-slate-100 shadow-sm relative overflow-hidden">
        <div class="flex justify-between items-start mb-8 relative z-10">
            <div>
                <h3 class="font-manrope font-bold text-xl text-slate-800">Intent Clustering</h3>
                <p class="text-xs text-slate-500 mt-1">Query density & real-time shifts</p>
            </div>
            <div class="flex gap-2">
                <span class="px-3 py-1 bg-rose-100 text-rose-700 border border-rose-200 text-[10px] font-bold rounded-full flex items-center justify-center gap-1"><div class="w-1.5 h-1.5 bg-rose-500 rounded-full animate-pulse"></div>LIVE</span>
                <span class="px-3 py-1 bg-slate-100 text-slate-600 text-[10px] font-bold rounded-full">Last 24h</span>
            </div>
        </div>

        <!-- Bubble/Clustering Visualization - Empty State -->
        <div class="h-64 relative bg-slate-50/50 rounded-2xl border border-slate-100/50 overflow-hidden flex flex-col items-center justify-center">
            <svg class="w-12 h-12 text-slate-300 mb-2" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 8v4l3 3"/></svg>
            <span class="text-sm font-semibold text-slate-400">Awaiting Search Density</span>
            <span class="text-xs text-slate-400 text-center max-w-[200px] mt-1">Sensus Sync will aggregate intent groupings here as queries flow in.</span>
        </div>

        <div class="mt-6 flex items-center justify-between relative z-10">
            <div class="flex items-center gap-4">
                <span class="text-[10px] font-bold uppercase tracking-widest text-slate-400">Data Feed Offline</span>
            </div>
            <a class="text-indigo-600 text-xs font-bold hover:text-indigo-800 transition-colors" href="#">Full Heatmap &rarr;</a>
        </div>
    </div>

    <!-- Knowledge Gaps -->
    <div class="col-span-12 bg-white rounded-3xl p-8 border border-slate-100 shadow-sm mt-2">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
            <div>
                <h3 class="font-manrope font-bold text-2xl text-slate-800">Knowledge Gaps</h3>
                <p class="text-sm text-slate-500 mt-1">Missing source documentation identified automatically from user queries.</p>
            </div>
            <div class="flex items-center gap-3">
                <div class="flex items-center gap-1 bg-slate-50 p-1.5 rounded-xl border border-slate-200">
                    <button onclick={() => currentTab = 'pending'} class="px-4 py-1.5 text-xs font-bold rounded-lg transition-colors {currentTab === 'pending' ? 'bg-white shadow-sm text-slate-800 border border-slate-200/50' : 'text-slate-500 hover:text-slate-700'}">Pendentes</button>
                    <button onclick={() => currentTab = 'resolved'} class="px-4 py-1.5 text-xs font-bold rounded-lg transition-colors {currentTab === 'resolved' ? 'bg-white shadow-sm text-slate-800 border border-slate-200/50' : 'text-slate-500 hover:text-slate-700'}">Resolvidos</button>
                </div>
                <select class="appearance-none bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-xs font-bold text-slate-600 focus:ring-2 focus:ring-indigo-100 outline-none cursor-pointer">
                    <option>High Priority</option>
                    <option>Most Recent</option>
                    <option>Volume</option>
                </select>
            </div>
        </div>

        <div class="overflow-x-auto no-scrollbar">
            <table class="w-full text-left">
                <thead>
                    <tr class="text-[10px] uppercase font-bold tracking-widest text-slate-400 border-b border-slate-100">
                        <th class="pb-4 px-3 w-[40%]">Unresolved Query</th>
                        <th class="pb-4 px-3 text-center">Frequency</th>
                        {#if currentTab === 'pending'}
                            <th class="pb-4 px-3">Context Field</th>
                            <th class="pb-4 px-3">Sentiment Effect</th>
                            <th class="pb-4 px-3 text-right">Rapid Action</th>
                        {:else}
                            <th class="pb-4 px-3 w-[30%]">Resolution Vault</th>
                            <th class="pb-4 px-3 text-right">Purge Log</th>
                        {/if}
                    </tr>
                </thead>
                <tbody class="text-sm">
                    {#if is_loading}
                        <tr><td colspan="5" class="py-12 text-center text-slate-400 font-medium">Scanning index blocks...</td></tr>
                    {:else if filteredGaps.length === 0}
                        <tr><td colspan="5" class="py-12 text-center text-slate-400 font-medium">{currentTab === 'pending' ? 'All hallucination gaps resolved. System optimal.' : 'No resolved logs recorded yet.'}</td></tr>
                    {:else}
                        {#each filteredGaps as gap}
                            <tr class="group hover:bg-slate-50 transition-colors border-b border-slate-50 last:border-0">
                                <td class="py-5 px-3">
                                    <span class="font-bold text-slate-800 group-hover:text-indigo-700 transition-colors">"{gap.query}"</span>
                                </td>
                                <td class="py-5 px-3 text-center">
                                    {#if gap.frequency > 100}
                                        <span class="px-2.5 py-1 rounded bg-rose-100 text-rose-700 text-[10px] font-bold border border-rose-200">{gap.frequency} hits</span>
                                    {:else if gap.frequency > 50}
                                        <span class="px-2.5 py-1 rounded bg-amber-100 text-amber-700 text-[10px] font-bold border border-amber-200">{gap.frequency} hits</span>
                                    {:else}
                                        <span class="px-2.5 py-1 rounded bg-slate-100 text-slate-600 text-[10px] font-bold border border-slate-200">{gap.frequency} hits</span>
                                    {/if}
                                </td>
                                {#if currentTab === 'pending'}
                                    <td class="py-5 px-3 text-slate-500 font-medium">{gap.context}</td>
                                    <td class="py-5 px-3">
                                        <div class="flex items-center gap-1.5 {getSentimentColor(gap.sentiment)}">
                                            <span class="material-symbols-outlined text-lg" style="font-variation-settings: 'FILL' 1;">{getSentimentIcon(gap.sentiment)}</span>
                                            <span class="text-xs font-bold">{gap.sentiment}</span>
                                        </div>
                                    </td>
                                    <td class="py-5 px-3 text-right">
                                        <button onclick={() => handleInjectContent(gap)} class="text-indigo-600 bg-indigo-50 hover:bg-indigo-100 border border-indigo-100 font-bold text-xs px-3 py-1.5 rounded-lg flex items-center justify-end gap-1 ml-auto transition-colors">
                                            Inject Content <span class="material-symbols-outlined text-[16px]">add</span>
                                        </button>
                                    </td>
                                {:else}
                                    <td class="py-5 px-3">
                                        {#if expandedGapId === gap.id}
                                            <button 
                                                onclick={() => expandedGapId = null} 
                                                class="text-xs text-slate-700 bg-slate-100 border border-slate-200 p-3 rounded-xl max-w-xl text-left hover:bg-slate-200 transition-colors cursor-pointer leading-relaxed"
                                            >
                                                {gap.resolution_content}
                                            </button>
                                        {:else}
                                            <button 
                                                onclick={() => expandedGapId = gap.id}
                                                class="text-xs text-slate-500 line-clamp-2 max-w-sm text-left hover:text-indigo-600 transition-colors cursor-pointer" 
                                                title="Clique para ler a resolução completa"
                                            >
                                                {gap.resolution_content}
                                            </button>
                                        {/if}
                                    </td>
                                    <td class="py-5 px-3 text-right">
                                        <button onclick={() => handleHardDelete(gap)} class="text-rose-500 bg-rose-50 hover:bg-rose-100 border border-rose-100 font-bold text-xs p-1.5 rounded-lg flex items-center justify-center ml-auto transition-colors" title="Purge logic permanently">
                                            <span class="material-symbols-outlined text-[16px]">delete</span>
                                        </button>
                                    </td>
                                {/if}
                            </tr>
                        {/each}

                    {/if}
                </tbody>
            </table>
        </div>
    </div>
</div>
