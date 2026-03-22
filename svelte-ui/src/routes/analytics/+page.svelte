<script lang="ts">
    import { CircleDollarSign, Timer, Gauge, AlertTriangle, TrendingUp, CheckCircle2, Zap, ShieldAlert, Network, AlertCircle, FileText, DownloadCloud, RefreshCw, ShieldCheck } from 'lucide-svelte';
    import { telemetryState } from '$lib/telemetry.svelte';

    const tailwindPalette = [
        { bg: 'bg-blue-500', bgHover: 'group-hover:bg-blue-600', text: 'text-blue-600' },
        { bg: 'bg-indigo-400', bgHover: 'group-hover:bg-indigo-500', text: 'text-indigo-600' },
        { bg: 'bg-teal-400', bgHover: 'group-hover:bg-teal-500', text: 'text-teal-600' },
        { bg: 'bg-rose-400', bgHover: 'group-hover:bg-rose-500', text: 'text-rose-600' },
        { bg: 'bg-amber-400', bgHover: 'group-hover:bg-amber-500', text: 'text-amber-600' },
        { bg: 'bg-emerald-500', bgHover: 'group-hover:bg-emerald-600', text: 'text-emerald-600' }
    ];

    let totalTokens = $derived(Object.values(telemetryState.modelsUsage).reduce((a, b) => a + b, 0));
    
    let modelSplits = $derived(Object.entries(telemetryState.modelsUsage).map(([name, tokens], idx) => {
        let palette = tailwindPalette[idx % tailwindPalette.length];
        return {
            name,
            tokens,
            percent: totalTokens > 0 ? (tokens / totalTokens) * 100 : 0,
            palette
        };
    }).sort((a,b) => b.tokens - a.tokens));
</script>

<div class="flex flex-col h-full w-full bg-white rounded-2xl border border-slate-200 shadow-[0_2px_12px_rgba(0,0,0,0.03)] overflow-hidden">
    <!-- Sovereign Standard Sub-Header -->
    <header class="h-20 border-b border-slate-100 bg-white flex items-center px-6 shrink-0 justify-between z-10 w-full">
        <div class="flex items-center gap-4">
            <div class="bg-blue-600/10 p-2.5 rounded-xl border border-blue-100/50">
                <Network class="w-6 h-6 text-blue-600" />
            </div>
            <div class="flex flex-col">
                <div class="flex items-center gap-2">
                    <h1 class="text-lg font-bold tracking-tight text-slate-800">Nexus Command Center</h1>
                    <span class="px-2 py-0.5 bg-emerald-100/50 text-emerald-700 text-[9px] uppercase tracking-widest font-bold rounded-full border border-emerald-200/50">PROD</span>
                </div>
                <span class="text-xs text-slate-500 font-medium">Intelligence-led oversight of global RAG operations and multi-model routing.</span>
            </div>
        </div>
        
        <div class="flex items-center gap-4">
            <button class="flex items-center gap-2 px-4 py-2 bg-white border border-slate-200 rounded-xl text-xs font-bold uppercase tracking-wider text-slate-500 hover:bg-slate-50 hover:text-slate-700 transition-colors cursor-pointer shadow-sm">
                <DownloadCloud class="w-4 h-4" /> Export Report
            </button>
            <button class="flex items-center gap-2 px-5 py-2 bg-gradient-to-br from-blue-600 to-indigo-700 text-white rounded-xl text-xs font-bold uppercase tracking-wider shadow-[0_4px_14px_rgba(79,70,229,0.3)] hover:shadow-[0_6px_20px_rgba(79,70,229,0.4)] hover:-translate-y-0.5 transition-all cursor-pointer">
                <RefreshCw class="w-4 h-4" /> Global Refresh
            </button>
        </div>
    </header>

    <!-- Scrollable Content Viewport -->
    <div class="flex-1 overflow-y-auto custom-scrollbar p-6 bg-slate-50/50">
        <div class="max-w-7xl mx-auto space-y-8">

    <!-- Row 1: Vital Signs -->
    <div class="grid grid-cols-1 md:grid-cols-2 border border-slate-200/50 bg-white/50 backdrop-blur p-2 rounded-3xl lg:grid-cols-4 gap-4 shrink-0 shadow-sm">
        <!-- Total Cost -->
        <div class="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm hover:border-blue-200 transition-all flex flex-col group">
            <div class="flex justify-between items-start mb-4">
                <span class="text-xs font-bold text-slate-400 uppercase tracking-widest group-hover:text-blue-500 transition-colors">Total Cost</span>
                <div class="p-2 bg-blue-50 rounded-lg">
                  <CircleDollarSign class="text-blue-600 w-5 h-5" />
                </div>
            </div>
            <div class="text-3xl font-extrabold text-slate-800 mb-1 leading-none">US$ {telemetryState.estimatedCost.toFixed(4)}</div>
            <div class="flex items-center gap-1.5 text-xs font-bold text-rose-500 mt-4">
                <TrendingUp class="w-4 h-4" /> 5% vs last 24h
            </div>
        </div>

        <!-- Latency -->
        <div class="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm hover:border-indigo-200 transition-all flex flex-col group">
            <div class="flex justify-between items-start mb-4">
                <span class="text-xs font-bold text-slate-400 uppercase tracking-widest group-hover:text-indigo-500 transition-colors">Avg Latency</span>
                <div class="p-2 bg-indigo-50 rounded-lg">
                  <Timer class="text-indigo-600 w-5 h-5" />
                </div>
            </div>
            <div class="text-3xl font-extrabold text-slate-800 mb-1 leading-none">{telemetryState.avgLatencyMs} <span class="text-lg text-slate-400 font-medium">ms</span></div>
            <div class="flex items-center gap-1.5 text-xs font-bold text-emerald-500 mt-4">
                <CheckCircle2 class="w-4 h-4" /> Rapid • Healthy
            </div>
        </div>

        <!-- Throughput -->
        <div class="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm hover:border-teal-200 transition-all flex flex-col group">
            <div class="flex justify-between items-start mb-4">
                <span class="text-xs font-bold text-slate-400 uppercase tracking-widest group-hover:text-teal-500 transition-colors">Throughput</span>
                <div class="p-2 bg-teal-50 rounded-lg">
                  <Gauge class="text-teal-600 w-5 h-5" />
                </div>
            </div>
            <div class="text-3xl font-extrabold text-slate-800 mb-1 leading-none">{telemetryState.tokensPerSecond} <span class="text-lg text-slate-400 font-medium">t/s</span></div>
            <div class="flex items-center gap-1.5 text-xs font-bold text-emerald-500 mt-4">
                <Zap class="w-4 h-4" /> Peak Performance
            </div>
        </div>

        <!-- Security Alerts -->
        <div class="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm hover:border-rose-200 transition-all flex flex-col group">
            <div class="flex justify-between items-start mb-4">
                <span class="text-xs font-bold text-slate-400 uppercase tracking-widest group-hover:text-rose-500 transition-colors">Security Alerts</span>
                <div class="p-2 bg-rose-50 rounded-lg">
                  <AlertTriangle class="text-rose-600 w-5 h-5" />
                </div>
            </div>
            <div class="text-3xl font-extrabold text-rose-600 mb-1 leading-none">{telemetryState.firewallBlocks}</div>
            <div class="flex items-center gap-1.5 text-xs font-bold text-rose-600 mt-4">
                <AlertCircle class="w-4 h-4" /> Requires Attention
            </div>
        </div>
    </div>

    <!-- Row 2: Traffic & Economics -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 shrink-0">
        <!-- Live Traffic (Mocked Chart) -->
        <div class="lg:col-span-2 bg-white p-8 rounded-3xl border border-slate-200 shadow-sm flex flex-col">
            <div class="flex justify-between items-center mb-8">
                <div>
                    <h2 class="text-xl font-bold text-slate-800">Live Traffic by Model</h2>
                    <p class="text-xs text-slate-500 font-medium mt-1">Real-time token request volume per architecture</p>
                </div>
                <div class="flex flex-wrap gap-4">
                    {#each modelSplits as split}
                    <div class="flex items-center gap-2 text-xs font-bold text-slate-600">
                        <span class="w-3 h-3 rounded-full {split.palette.bg} shadow-sm"></span> {split.name}
                    </div>
                    {/each}
                    {#if modelSplits.length === 0}
                    <div class="flex items-center gap-2 text-xs font-bold text-slate-400">
                        <span class="w-3 h-3 rounded-full bg-slate-300 shadow-sm"></span> Awaiting Data
                    </div>
                    {/if}
                </div>
            </div>
            
            <!-- Simulated Bar Chart -->
            <div class="h-64 relative flex items-end gap-1 mt-auto shrink-0 border-b border-slate-100 pb-2">
                {#each [ 
                    [60, 30, 10], [65, 25, 10], [55, 35, 10], [70, 20, 10], [50, 40, 10], [60, 25, 15], [63, 27, 10], [58, 30, 12] 
                ] as split}
                <div class="flex-1 flex flex-col justify-end gap-0.5 group cursor-crosshair">
                    {#if modelSplits.length > 0}
                        {#each modelSplits as model, idx}
                        <!-- Pseudo timeseries distribution mirroring aggregate percent exactly -->
                        <div class="w-full {model.palette.bg}/80 {model.palette.bgHover} transition-colors {idx === 0 ? 'rounded-t-sm' : ''} {idx === modelSplits.length - 1 ? 'rounded-b-sm' : ''}" style="height: {model.percent * split[0] / 60}%;"></div>
                        {/each}
                    {:else}
                        <div class="w-full bg-slate-200/50 rounded-sm" style="height: {split[0]}%;"></div>
                    {/if}
                </div>
                {/each}
            </div>
            <div class="flex justify-between mt-3 text-[10px] text-slate-400 font-bold uppercase tracking-widest px-1">
                <span>12:00</span><span>13:00</span><span>14:00</span><span>15:00</span><span>16:00</span><span>17:00</span><span>18:00</span><span>19:00</span>
            </div>
        </div>

        <!-- Costs & Savings -->
        <div class="bg-white p-8 rounded-3xl border border-slate-200 shadow-sm flex flex-col">
            <h2 class="text-xl font-bold text-slate-800 mb-6">Usage Economics</h2>
            <div class="space-y-6">
                {#each modelSplits as split}
                <div>
                    <div class="flex justify-between text-xs font-bold mb-2 text-slate-700">
                        <span>{split.name}</span>
                        <span class="text-slate-500">{split.percent.toFixed(1)}% Volume</span>
                    </div>
                    <div class="h-2.5 bg-slate-100 rounded-full overflow-hidden">
                        <div class="h-full {split.palette.bg} rounded-full shadow-[inset_0_-1px_2px_rgba(0,0,0,0.1)]" style="width: {split.percent}%"></div>
                    </div>
                </div>
                {/each}
                {#if modelSplits.length === 0}
                <div class="flex flex-col items-center justify-center py-6 text-slate-400">
                    <Network class="w-8 h-8 mb-2 opacity-50" />
                    <p class="text-xs font-medium text-center">Awaiting intelligence routing to compile economics.</p>
                </div>
                {/if}
            </div>
            <div class="mt-auto pt-8 border-t border-slate-100">
                <div class="flex items-center gap-5">
                    <div class="w-16 h-16 rounded-full border-[5px] border-emerald-100 flex items-center justify-center bg-white shadow-inner">
                        <span class="text-lg font-black text-emerald-600">34%</span>
                    </div>
                    <div>
                        <h3 class="text-sm font-bold text-slate-800 mb-1">Semantic Cache Hit</h3>
                        <p class="text-[11px] text-emerald-600 font-bold tracking-wide uppercase">Est. savings: $124.20/day</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Row 3: Security & Knowledge -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 pb-20 shrink-0">
        <!-- Firewall & Guardrails -->
        <div class="bg-slate-900 p-8 rounded-3xl shadow-xl border border-slate-800 relative overflow-hidden">
            <!-- Grid Pattern Background -->
            <div class="absolute inset-0 opacity-10" style="background-image: linear-gradient(#475569 1px, transparent 1px), linear-gradient(90deg, #475569 1px, transparent 1px); background-size: 20px 20px;"></div>
            
            <div class="flex justify-between items-center mb-8 relative z-10">
                <div class="flex items-center gap-3">
                    <ShieldAlert class="text-emerald-400 w-6 h-6" />
                    <h2 class="text-xl font-bold text-white tracking-wide">Firewall & Guardrails</h2>
                </div>
                <span class="px-2.5 py-1 bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 text-[10px] uppercase font-black tracking-widest rounded-md animate-pulse">
                    LIVE MONITOR
                </span>
            </div>
            <div class="space-y-3 relative z-10">
                <div class="flex items-start gap-4 p-4 bg-slate-800/50 backdrop-blur rounded-xl border border-slate-700/50 hover:border-slate-600 transition-colors">
                    <div class="mt-1 w-2.5 h-2.5 rounded-full bg-rose-500 shrink-0 shadow-[0_0_8px_rgba(244,63,94,0.6)]"></div>
                    <div>
                        <p class="text-xs font-mono text-slate-200 font-bold tracking-tight mb-1.5">SEC Prompt Injection BLOCKED</p>
                        <p class="text-[10px] text-slate-400 leading-relaxed">Request ID: 894-X-92 | Model: GPT-4o<br/>Source: External IP 192.x.x.x</p>
                    </div>
                    <span class="ml-auto text-[10px] font-mono text-slate-500">2m ago</span>
                </div>
                <div class="flex items-start gap-4 p-4 bg-slate-800/50 backdrop-blur rounded-xl border border-slate-700/50 hover:border-slate-600 transition-colors">
                    <div class="mt-1 w-2.5 h-2.5 rounded-full bg-emerald-400 shrink-0 shadow-[0_0_8px_rgba(52,211,153,0.6)]"></div>
                    <div>
                        <p class="text-xs font-mono text-slate-200 font-bold tracking-tight mb-1.5">PII Detected CPF MASKED</p>
                        <p class="text-[10px] text-slate-400 leading-relaxed">Output Filter Active | Compliance: GDPR/LGPD<br/>Masked: [***.842.***-**]</p>
                    </div>
                    <span class="ml-auto text-[10px] font-mono text-slate-500">14m ago</span>
                </div>
                <div class="flex items-start gap-4 p-4 bg-slate-800/50 backdrop-blur rounded-xl border border-slate-700/50 opacity-60 hover:opacity-100 transition-opacity">
                    <div class="mt-1 w-2.5 h-2.5 rounded-full bg-emerald-400 shrink-0"></div>
                    <div>
                        <p class="text-xs font-mono text-slate-200 font-bold tracking-tight mb-1.5">Toxicity Check PASSED</p>
                        <p class="text-[10px] text-slate-400 leading-relaxed">Score: 0.002 | Policy: Enterprise-Strict</p>
                    </div>
                    <span class="ml-auto text-[10px] font-mono text-slate-500">21m ago</span>
                </div>
            </div>
        </div>

        <!-- RAG Knowledge Radar -->
        <div class="bg-white p-8 rounded-3xl border border-slate-200 shadow-sm">
            <div class="flex justify-between items-center mb-8">
                <div class="flex items-center gap-3">
                    <div class="p-2 bg-indigo-50 text-indigo-600 rounded-lg">
                        <Network class="w-5 h-5" />
                    </div>
                    <h2 class="text-xl font-bold text-slate-800">RAG Knowledge Radar</h2>
                </div>
                <button class="text-indigo-600 text-xs font-bold hover:text-indigo-800 hover:underline transition-all uppercase tracking-wider">Full Audit</button>
            </div>
            <div class="grid grid-cols-2 gap-10">
                <div>
                    <h3 class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-4 flex items-center gap-2">
                        <AlertCircle class="w-3 h-3 text-rose-500" /> Content Gaps
                    </h3>
                    <div class="space-y-3">
                        <div class="p-3 bg-rose-50 border border-rose-100 rounded-xl flex items-center justify-between group cursor-pointer">
                            <span class="text-xs font-bold text-rose-700 group-hover:text-rose-900 transition-colors">Home office policy</span>
                            <AlertTriangle class="text-rose-500 w-3.5 h-3.5" />
                        </div>
                        <div class="p-3 bg-slate-50 border border-slate-100 rounded-xl flex items-center justify-between group cursor-pointer hover:bg-slate-100">
                            <span class="text-xs font-semibold text-slate-600 group-hover:text-slate-800 transition-colors">ERP reset protocol</span>
                            <FileText class="text-slate-400 w-3.5 h-3.5" />
                        </div>
                    </div>
                </div>
                <div>
                    <h3 class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-4 flex items-center gap-2">
                        <TrendingUp class="w-3 h-3 text-indigo-500" /> Top Topics
                    </h3>
                    <div class="space-y-5">
                        <div>
                            <div class="flex justify-between text-xs font-bold mb-1.5 text-slate-700">
                                <span>Deploy Pipelines</span>
                                <span class="text-indigo-600">32%</span>
                            </div>
                            <div class="h-1.5 bg-slate-100 rounded-full">
                                <div class="h-full bg-indigo-500 w-[32%] rounded-full"></div>
                            </div>
                        </div>
                        <div>
                            <div class="flex justify-between text-xs font-bold mb-1.5 text-slate-700">
                                <span>Docker Bugs</span>
                                <span class="text-indigo-600">15%</span>
                            </div>
                            <div class="h-1.5 bg-slate-100 rounded-full">
                                <div class="h-full bg-indigo-500 w-[15%] rounded-full"></div>
                            </div>
                        </div>
                        <div>
                            <div class="flex justify-between text-xs font-bold mb-1.5 text-slate-700">
                                <span>Auth Setup</span>
                                <span class="text-indigo-600">12%</span>
                            </div>
                            <div class="h-1.5 bg-slate-100 rounded-full">
                                <div class="h-full bg-indigo-500 w-[12%] rounded-full"></div>
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
