<script lang="ts">
    import { CircleDollarSign, Timer, Gauge, AlertTriangle, TrendingUp, CheckCircle2, Zap, ShieldAlert, Network, AlertCircle, FileText, DownloadCloud, RefreshCw, ShieldCheck, Database } from 'lucide-svelte';
    import { telemetryState } from '$lib/telemetry.svelte';

    const tailwindPalette = [
        { bg: 'bg-blue-500', bgHover: 'group-hover:bg-blue-600', text: 'text-blue-600' },
        { bg: 'bg-indigo-400', bgHover: 'group-hover:bg-indigo-500', text: 'text-indigo-600' },
        { bg: 'bg-teal-400', bgHover: 'group-hover:bg-teal-500', text: 'text-teal-600' },
        { bg: 'bg-rose-400', bgHover: 'group-hover:bg-rose-500', text: 'text-rose-600' },
        { bg: 'bg-amber-400', bgHover: 'group-hover:bg-amber-500', text: 'text-amber-600' },
        { bg: 'bg-emerald-500', bgHover: 'group-hover:bg-emerald-600', text: 'text-emerald-600' }
    ];

    let validModels = $derived(telemetryState.historicalModels.filter(m => m.model_name && m.model_name.trim() !== '' && m.model_name !== '-'));
    let historicalTotalTokens = $derived(validModels.reduce((acc, m) => acc + (parseInt(m.total_tokens) || 0), 0));
    
    // Cloud Economy Real-time Math
    let lifetimeSavings = $derived((historicalTotalTokens / 1000) * telemetryState.avgCloudCostPer1k);
    let earliestDate = $derived(validModels.length > 0 ? validModels.reduce((acc, m) => {
        if (!m.first_used_at) return acc;
        let d = new Date(m.first_used_at.replace(' ', 'T') + 'Z');
        return d < acc ? d : acc;
    }, new Date()) : new Date());
    let activeDays = $derived(Math.max(1, (new Date().getTime() - earliestDate.getTime()) / (1000 * 60 * 60 * 24)));
    let dailySavings = $derived(lifetimeSavings / activeDays);
    let weeklySavings = $derived(dailySavings * 7);
    let historicalModelSplits = $derived(validModels.map((m, idx) => {
        let palette = tailwindPalette[idx % tailwindPalette.length];
        let tokens = parseInt(m.total_tokens) || 0;
        return {
            name: m.model_name,
            tokens: tokens,
            percent: historicalTotalTokens > 0 ? (tokens / historicalTotalTokens) * 100 : 0,
            palette,
            durationMs: parseInt(m.total_duration_ms) || 0,
            firstUsed: m.first_used_at,
            lastUsed: m.last_used_at
        };
    }).sort((a,b) => b.tokens - a.tokens));

    function formatDuration(ms: number) {
        if (!ms) return "0s";
        let seconds = Math.floor(ms / 1000);
        let minutes = Math.floor(seconds / 60);
        let hours = Math.floor(minutes / 60);
        let days = Math.floor(hours / 24);
        
        if (days > 0) return `${days}d ${hours % 24}h`;
        if (hours > 0) return `${hours}h ${minutes % 60}m`;
        if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
        return `${seconds}s`;
    }

    function formatTimeAgo(dateStr: string) {
        if (!dateStr) return "Never";
        // SQLite returns 'YYYY-MM-DD HH:MM:SS', so we replace space with T for valid ISO parsing
        const date = new Date(dateStr.replace(' ', 'T') + 'Z'); 
        const now = new Date();
        const diffMs = now.getTime() - date.getTime();
        if (isNaN(diffMs)) return dateStr.split(' ')[0] || "Unknown";
        
        const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
        if (diffDays === 0) return "Today";
        if (diffDays === 1) return "Yesterday";
        if (diffDays > 30) return `${Math.floor(diffDays/30)} months ago`;
        return `${diffDays} days ago`;
    }
</script>

<div class="p-8 h-full">
    <!-- Header Section (Identical to Distillation) -->
    <header class="mb-10 w-full flex items-center justify-between">
        <div class="flex items-center gap-4 bg-surface-container-low px-4 py-2 rounded-full w-96 border border-outline-variant/10 shadow-sm">
            <span class="material-symbols-outlined text-on-surface-variant text-[20px]">search</span>
            <input class="bg-transparent border-none focus:ring-0 text-sm w-full placeholder:text-on-surface-variant/70 text-on-surface outline-none" placeholder="Search analytics or metrics..." type="text" />
        </div>
        <div class="flex items-center gap-4 bg-surface-container-low p-1.5 rounded-xl border border-outline-variant/10">
            <a href="/engineer/fine-tuning" class="px-4 py-2 text-slate-500 dark:text-slate-400 font-medium text-xs rounded-lg hover:bg-slate-100 dark:hover:bg-[#1d253b] transition-colors">Fine-Tuning</a>
            <a href="/engineer/distillation" class="px-4 py-2 text-slate-500 dark:text-slate-400 font-medium text-xs rounded-lg hover:bg-slate-100 dark:hover:bg-[#1d253b] transition-colors">Distillation</a>
            <a href="/engineer/reflection" class="px-4 py-2 text-slate-500 dark:text-slate-400 font-medium text-xs rounded-lg hover:bg-slate-100 dark:hover:bg-[#1d253b] transition-colors">Reflection Lab</a>
            <a href="/engineer/rag-pipeline" class="px-4 py-2 text-slate-500 dark:text-slate-400 font-medium text-xs rounded-lg hover:bg-slate-100 dark:hover:bg-[#1d253b] transition-colors">RAG Pipeline</a>
            <a href="/engineer/unsloth" class="px-4 py-2 text-slate-500 dark:text-slate-400 font-medium text-xs rounded-lg hover:bg-slate-100 dark:hover:bg-[#1d253b] transition-colors">Unsloth Monitor</a>
            <button class="px-4 py-2 bg-blue-600 dark:bg-[#74b0ff]/20 text-white dark:text-[#74b0ff] font-bold text-xs rounded-lg shadow-sm">Analytics</button>
        </div>
    </header>

    <div class="w-full flex-1">
        <!-- Title Section -->
        <section class="flex justify-between items-end mb-10">
            <div>
                <p class="text-primary dark:text-blue-400 font-semibold text-sm tracking-wide mb-1 uppercase">Model Trainer</p>
                <div class="flex items-center gap-2">
                    <h1 class="font-extrabold text-3xl tracking-tight text-on-surface dark:text-white">Nexus Command Center</h1>
                    <span class="px-2 py-0.5 bg-emerald-100/50 dark:bg-emerald-900/40 text-emerald-700 dark:text-emerald-400 text-[9px] uppercase tracking-widest font-bold rounded-full border border-emerald-200/50 dark:border-emerald-800/50 relative -top-2">PROD</span>
                </div>
            </div>
            <div class="flex gap-3">
                <button class="px-5 py-2.5 rounded-xl border border-outline-variant/30 dark:border-slate-700 text-on-surface-variant dark:text-slate-300 font-bold text-xs hover:bg-surface-container-high dark:hover:bg-slate-800 transition-colors cursor-pointer active:scale-95 flex items-center gap-2">
                    <DownloadCloud class="w-4 h-4" /> Export Report
                </button>
                <button class="px-5 py-2.5 rounded-xl bg-gradient-to-br from-[#001360] to-[#002395] dark:from-blue-600 dark:to-blue-800 text-white font-bold text-xs shadow-md shadow-primary/20 dark:shadow-none active:scale-95 transition-transform flex items-center gap-2 cursor-pointer">
                    <RefreshCw class="w-4 h-4" /> Global Refresh
                </button>
            </div>
        </section>

        <!-- Fluid Analytics Layout -->
        <div class="space-y-8">

    <!-- Row 1: Vital Signs -->
    <div class="grid grid-cols-1 md:grid-cols-2 border border-slate-200/50 dark:border-slate-800/50 bg-white/50 dark:bg-[#12192b]/50 backdrop-blur p-2 rounded-3xl lg:grid-cols-5 gap-4 shrink-0 shadow-sm">
        <!-- Total Savings -->
        <div class="bg-white dark:bg-[#0c1324] p-6 rounded-2xl border border-slate-100 dark:border-slate-800/50 shadow-sm hover:border-emerald-200 dark:hover:border-emerald-900/50 transition-all flex flex-col group">
            <div class="flex justify-between items-start mb-4">
                <span class="text-xs font-bold text-slate-400 uppercase tracking-widest group-hover:text-emerald-500 transition-colors">Total Savings</span>
                <div class="p-2 bg-emerald-50 dark:bg-emerald-900/30 rounded-lg">
                  <CircleDollarSign class="text-emerald-600 dark:text-emerald-400 w-5 h-5" />
                </div>
            </div>
            <div class="text-3xl font-extrabold text-slate-800 dark:text-slate-200 mb-1 leading-none">US$ {telemetryState.estimatedCost.toFixed(4)}</div>
            <div class="flex items-center gap-1.5 text-xs font-bold text-emerald-500 mt-4">
                <TrendingUp class="w-4 h-4" /> Sovereign Cloud Economy
            </div>
        </div>

        <!-- Latency -->
        <div class="bg-white dark:bg-[#0c1324] p-6 rounded-2xl border border-slate-100 dark:border-slate-800/50 shadow-sm hover:border-indigo-200 dark:hover:border-indigo-900/50 transition-all flex flex-col group">
            <div class="flex justify-between items-start mb-4">
                <span class="text-xs font-bold text-slate-400 uppercase tracking-widest group-hover:text-indigo-500 transition-colors">Avg Latency</span>
                <div class="p-2 bg-indigo-50 dark:bg-indigo-900/30 rounded-lg">
                  <Timer class="text-indigo-600 dark:text-indigo-400 w-5 h-5" />
                </div>
            </div>
            <div class="text-3xl font-extrabold text-slate-800 dark:text-slate-200 mb-1 leading-none">{telemetryState.avgLatencyMs} <span class="text-lg text-slate-400 font-medium">ms</span></div>
            <div class="flex items-center gap-1.5 text-xs font-bold text-emerald-500 mt-4">
                <CheckCircle2 class="w-4 h-4" /> Rapid • Healthy
            </div>
        </div>

        <!-- Throughput -->
        <div class="bg-white dark:bg-[#0c1324] p-6 rounded-2xl border border-slate-100 dark:border-slate-800/50 shadow-sm hover:border-teal-200 dark:hover:border-teal-900/50 transition-all flex flex-col group">
            <div class="flex justify-between items-start mb-4">
                <span class="text-xs font-bold text-slate-400 uppercase tracking-widest group-hover:text-teal-500 transition-colors">Throughput</span>
                <div class="p-2 bg-teal-50 dark:bg-teal-900/30 rounded-lg">
                  <Gauge class="text-teal-600 dark:text-teal-400 w-5 h-5" />
                </div>
            </div>
            <div class="text-3xl font-extrabold text-slate-800 dark:text-slate-200 mb-1 leading-none">{telemetryState.tokensPerSecond} <span class="text-lg text-slate-400 font-medium">t/s</span></div>
            <div class="flex items-center gap-1.5 text-xs font-bold text-emerald-500 mt-4">
                <Zap class="w-4 h-4" /> Peak Performance
            </div>
        </div>

        <!-- Security Alerts -->
        <div class="bg-white dark:bg-[#0c1324] p-6 rounded-2xl border border-slate-100 dark:border-slate-800/50 shadow-sm hover:border-rose-200 dark:hover:border-rose-900/50 transition-all flex flex-col group">
            <div class="flex justify-between items-start mb-4">
                <span class="text-xs font-bold text-slate-400 uppercase tracking-widest group-hover:text-rose-500 transition-colors">Security Alerts</span>
                <div class="p-2 bg-rose-50 dark:bg-rose-900/30 rounded-lg">
                  <AlertTriangle class="text-rose-600 dark:text-rose-400 w-5 h-5" />
                </div>
            </div>
            <div class="text-3xl font-extrabold text-rose-600 mb-1 leading-none">{telemetryState.firewallBlocks}</div>
            <div class="flex items-center gap-1.5 text-xs font-bold text-rose-600 mt-4">
                <AlertCircle class="w-4 h-4" /> Requires Attention
            </div>
        </div>

        <!-- Trackers Blocked -->
        <div class="bg-white dark:bg-[#0c1324] p-6 rounded-2xl border border-slate-100 dark:border-slate-800/50 shadow-sm hover:border-violet-200 dark:hover:border-violet-900/50 transition-all flex flex-col group relative overflow-hidden">
            <div class="absolute -right-4 -top-4 w-24 h-24 bg-violet-50 rounded-full blur-2xl opacity-50 group-hover:scale-150 transition-transform duration-700 pointer-events-none"></div>
            <div class="flex justify-between items-start mb-4 relative z-10">
                <span class="text-xs font-bold text-slate-400 uppercase tracking-widest group-hover:text-violet-500 transition-colors">Ads Blocked</span>
                <div class="p-2 bg-violet-50 dark:bg-violet-900/30 rounded-lg">
                  <ShieldCheck class="text-violet-600 dark:text-violet-400 w-5 h-5" />
                </div>
            </div>
            <div class="text-3xl font-extrabold text-slate-800 dark:text-slate-200 mb-1 leading-none relative z-10">{telemetryState.trackersBlocked}</div>
            <div class="flex items-center gap-1.5 text-xs font-bold text-violet-500 mt-4 relative z-10">
                <ShieldCheck class="w-4 h-4" /> Sovereign Pi-Hole
            </div>
        </div>
    </div>

    <!-- Row 2: Traffic & Economics -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 shrink-0 h-[450px]">
        
        <!-- Live Traffic (Now Real Persistence) -->
        <div class="lg:col-span-2 bg-white dark:bg-[#12192b] p-8 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col h-full min-h-0 overflow-hidden">
            <div class="flex justify-between items-center mb-6 shrink-0">
                <div>
                    <h2 class="text-xl font-bold text-slate-800 dark:text-slate-200">Historical Intelligence Fleet</h2>
                    <p class="text-xs text-slate-500 dark:text-slate-400 font-medium mt-1">Total token volume and uptime metrics for all recorded AI models</p>
                </div>
            </div>
            
            <div class="flex-1 overflow-y-auto pr-2 space-y-3 custom-scrollbar">
                {#each historicalModelSplits as model}
                <div class="flex items-center justify-between p-4 bg-slate-50 dark:bg-[#0c1324] border border-slate-100 dark:border-slate-800 rounded-2xl hover:border-slate-200 dark:hover:border-slate-700 transition-colors">
                    <div class="flex items-center gap-4">
                        <div class="w-10 h-10 rounded-full {model.palette.bg} bg-opacity-20 flex items-center justify-center border border-{model.palette.bg.replace('bg-', 'border-')} shadow-sm">
                            <Network class="w-5 h-5 {model.palette.text}" />
                        </div>
                        <div>
                            <h3 class="text-sm font-bold text-slate-800 dark:text-slate-200 flex items-center gap-2">
                                {model.name}
                                {#if telemetryState.modelsUsage[model.name]}
                                    <span class="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.8)] animate-pulse" title="Model Currently Active in Matrix"></span>
                                {/if}
                            </h3>
                            <p class="text-[11px] font-medium text-slate-500 dark:text-slate-400 mt-0.5">
                                First Boot: <span class="font-bold text-slate-600 dark:text-slate-300">{formatTimeAgo(model.firstUsed)}</span>
                            </p>
                        </div>
                    </div>
                    
                    <div class="flex items-center gap-8 text-right">
                        <div>
                            <p class="text-[10px] uppercase font-black tracking-widest text-slate-400 dark:text-slate-500 mb-1">Time Active</p>
                            <p class="text-xs font-bold text-slate-700 dark:text-slate-300">{formatDuration(model.durationMs)}</p>
                        </div>
                        <div class="min-w-[100px]">
                            <p class="text-[10px] uppercase font-black tracking-widest text-slate-400 dark:text-slate-500 mb-1">Tokens Burnt</p>
                            <p class="text-xs font-extrabold text-slate-800 dark:text-slate-100">{model.tokens.toLocaleString()}</p>
                        </div>
                    </div>
                </div>
                {/each}
                {#if historicalModelSplits.length === 0}
                <div class="h-full flex flex-col items-center justify-center text-slate-400 dark:text-slate-500 py-10">
                    <Database class="w-10 h-10 mb-3 opacity-20" />
                    <p class="text-sm font-bold">No Neural Fleet Data</p>
                    <p class="text-xs font-medium mt-1">Awaiting first generation cycle to record metrics.</p>
                </div>
                {/if}
            </div>
        </div>

        <!-- Costs & Savings -->
        <div class="bg-white dark:bg-[#12192b] p-8 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col h-full min-h-0 overflow-hidden">
            <h2 class="text-xl font-bold text-slate-800 dark:text-slate-200 mb-6 shrink-0">Usage Economics</h2>
            <div class="space-y-6 overflow-y-auto custom-scrollbar flex-1 pr-2 mb-4">
                {#each historicalModelSplits as split}
                <div>
                    <div class="flex justify-between text-xs font-bold mb-2 text-slate-700 dark:text-slate-300">
                        <span>{split.name}</span>
                        <span class="text-slate-500 dark:text-slate-400">{split.percent.toFixed(1)}% Volume</span>
                    </div>
                    <div class="h-2.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                        <div class="h-full {split.palette.bg} rounded-full shadow-[inset_0_-1px_2px_rgba(0,0,0,0.1)]" style="width: {split.percent}%"></div>
                    </div>
                </div>
                {/each}
                {#if historicalModelSplits.length === 0}
                <div class="flex flex-col items-center justify-center py-6 text-slate-400 dark:text-slate-500">
                    <Network class="w-8 h-8 mb-2 opacity-50" />
                    <p class="text-xs font-medium text-center">Awaiting intelligence routing to compile economics.</p>
                </div>
                {/if}
            </div>
            <div class="mt-auto pt-5 border-t border-slate-100 dark:border-slate-800 shrink-0">
                <div class="flex items-center gap-5">
                    <div class="w-14 h-14 rounded-full border-[4px] border-emerald-100 dark:border-emerald-900/50 flex flex-col items-center justify-center bg-emerald-50 dark:bg-emerald-900/20 shadow-inner shrink-0">
                        <span class="text-[9px] font-bold text-emerald-600 dark:text-emerald-400 -mb-0.5">LIFETIME</span>
                        <span class="text-[10px] font-black tracking-widest text-emerald-700 dark:text-emerald-300">$$$</span>
                    </div>
                    <div class="flex-1 min-w-0">
                        <div class="flex items-end justify-between mb-0.5">
                            <h3 class="text-sm font-bold text-slate-800 dark:text-slate-200 truncate">Total Economy Extracted</h3>
                            <span class="text-xs font-extrabold text-emerald-600 dark:text-emerald-400">US$ {lifetimeSavings.toFixed(2)}</span>
                        </div>
                        <div class="flex items-center justify-between text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest">
                            <span title="Economia Estimada por Dia">Day: <span class="text-slate-600 dark:text-slate-300">US$ {dailySavings.toFixed(2)}</span></span>
                            <span title="Economia Estimada por Semana">Week: <span class="text-slate-600 dark:text-slate-300">US$ {weeklySavings.toFixed(2)}</span></span>
                            <span title="Economia Estimada por Mês">Month: <span class="text-slate-600 dark:text-slate-300">US$ {(dailySavings * 30).toFixed(2)}</span></span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Row 3: Security & Knowledge -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 pb-20 shrink-0 h-[450px]">
        <!-- Firewall & Guardrails -->
        <div class="bg-slate-900 p-8 rounded-3xl shadow-xl border border-slate-800 relative overflow-hidden flex flex-col h-full min-h-0">
            <!-- Grid Pattern Background -->
            <div class="absolute inset-0 opacity-10" style="background-image: linear-gradient(#475569 1px, transparent 1px), linear-gradient(90deg, #475569 1px, transparent 1px); background-size: 20px 20px;"></div>
            
            <div class="flex justify-between items-center mb-6 shrink-0 relative z-10">
                <div class="flex items-center gap-3">
                    <ShieldAlert class="text-emerald-400 w-6 h-6" />
                    <h2 class="text-xl font-bold text-white tracking-wide">Firewall & Guardrails</h2>
                </div>
                <span class="px-2.5 py-1 bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 text-[10px] uppercase font-black tracking-widest rounded-md animate-pulse">
                    LIVE MONITOR
                </span>
            </div>
            <div class="space-y-4 relative z-10 overflow-y-auto custom-scrollbar pr-2 flex-1 pb-4">
                {#each telemetryState.securityLogs as log}
                <div class="flex items-start gap-4 p-4 bg-slate-800/50 backdrop-blur rounded-xl border border-slate-700/50 hover:border-slate-600 transition-colors">
                    <div class="mt-1 w-2.5 h-2.5 rounded-full {log.severity === 'Critical' ? 'bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.6)]' : 'bg-amber-400 shadow-[0_0_8px_rgba(251,191,36,0.6)]'} shrink-0"></div>
                    <div class="flex-1 min-w-0">
                        <p class="text-xs font-mono text-slate-200 font-bold tracking-tight mb-1.5 break-words">{log.event_type} {log.blocked ? 'BLOCKED' : 'PASSED'}</p>
                        <p class="text-[10px] text-slate-400 leading-relaxed font-mono break-words">{log.message}<br/>Source: {log.source}</p>
                    </div>
                    <span class="ml-auto text-[10px] font-mono text-slate-500 shrink-0 whitespace-nowrap pl-2">{log.created_at}</span>
                </div>
                {/each}
                {#if telemetryState.securityLogs.length === 0}
                <div class="flex items-start gap-4 p-4 bg-slate-800/50 backdrop-blur rounded-xl border border-slate-700/50 opacity-60">
                    <div class="mt-1 w-2.5 h-2.5 rounded-full bg-emerald-400 shrink-0 shadow-[0_0_8px_rgba(52,211,153,0.4)]"></div>
                    <div>
                        <p class="text-xs font-mono text-slate-200 font-bold tracking-tight mb-1.5">Sovereign Guardrails PASSED</p>
                        <p class="text-[10px] text-slate-400 leading-relaxed font-mono">Nenhuma ameaça identificada.<br/>Policy: Enterprise-Strict</p>
                    </div>
                </div>
                {/if}
            </div>
        </div>

        <!-- RAG Knowledge Radar -->
        <div class="bg-white dark:bg-[#12192b] p-8 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col h-full min-h-0 overflow-hidden">
            <div class="flex justify-between items-center mb-6 shrink-0">
                <div class="flex items-center gap-3">
                    <div class="p-2 bg-indigo-50 dark:bg-indigo-900/40 text-indigo-600 dark:text-indigo-400 rounded-lg">
                        <Network class="w-5 h-5" />
                    </div>
                    <h2 class="text-xl font-bold text-slate-800 dark:text-slate-200">RAG Knowledge Radar</h2>
                </div>
                <a href="/engineer/quality" class="text-indigo-600 dark:text-indigo-400 text-xs font-bold hover:text-indigo-800 dark:hover:text-indigo-300 hover:underline transition-all uppercase tracking-wider shrink-0">Full Audit</a>
            </div>
            <div class="grid grid-cols-2 gap-10 overflow-y-auto custom-scrollbar pr-2 flex-1 pb-4">
                <div>
                    <h3 class="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-4 flex items-center gap-2">
                        <AlertCircle class="w-3 h-3 text-rose-500" /> Content Gaps
                    </h3>
                    <div class="space-y-4">
                        {#each telemetryState.contentGaps as gap}
                        <div class="p-3 bg-rose-50 dark:bg-rose-900/20 border border-rose-100 dark:border-rose-900/50 rounded-xl flex flex-col gap-2 cursor-pointer group hover:bg-rose-100 dark:hover:bg-rose-900/40 transition-colors">
                            <div class="flex items-center justify-between">
                                <span class="text-xs font-bold text-rose-700 dark:text-rose-400 group-hover:text-rose-900 dark:group-hover:text-rose-300 transition-colors pr-2 break-words leading-tight">{gap.query}</span>
                                <AlertTriangle class="text-rose-500 w-3.5 h-3.5 shrink-0" />
                            </div>
                            <span class="text-[10px] text-rose-600/80 dark:text-rose-500 font-bold uppercase tracking-wider mt-1">Freq: {gap.frequency}x • {gap.status}</span>
                        </div>
                        {/each}
                        {#if telemetryState.contentGaps.length === 0}
                        <p class="text-xs text-slate-400 dark:text-slate-500 font-medium p-3 bg-slate-50 dark:bg-slate-800/50 rounded-xl border border-slate-100 dark:border-slate-800">No content gaps recorded.</p>
                        {/if}
                    </div>
                </div>
                <div>
                    <h3 class="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-4 flex items-center gap-2">
                        <TrendingUp class="w-3 h-3 text-indigo-500" /> Top Topics
                    </h3>
                    <div class="space-y-5">
                        {#each telemetryState.topTopics as topic}
                        <div>
                            <div class="flex justify-between text-xs font-bold mb-1.5 text-slate-700 dark:text-slate-300">
                                <span class="capitalize">{topic.topic}</span>
                                <span class="text-indigo-600 dark:text-indigo-400">{topic.count}</span>
                            </div>
                            <div class="h-1.5 bg-slate-100 dark:bg-slate-800 rounded-full">
                                <div class="h-full bg-indigo-500 rounded-full shadow-[inset_0_-1px_2px_rgba(0,0,0,0.1)]" style="width: {Math.max(10, Math.min(100, topic.count * 15))}%"></div>
                            </div>
                        </div>
                        {/each}
                        {#if telemetryState.topTopics.length === 0}
                        <p class="text-xs text-slate-400 dark:text-slate-500 font-medium p-3 bg-slate-50 dark:bg-slate-800/50 rounded-xl border border-slate-100 dark:border-slate-800">No topic clusters extracted yet.</p>
                        {/if}
                    </div>
                </div>
            </div>
            </div>
        </div>
    </div>
</div>
</div>
