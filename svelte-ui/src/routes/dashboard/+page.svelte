<script lang="ts">
    import { Activity, Cpu, Network, Zap, Timer, CheckCircle2, AlertTriangle, AlertCircle, Power, ShieldCheck, Database, FolderSync, FileText, Tags, Briefcase, CheckSquare, Layers, BookOpen } from 'lucide-svelte';
    import { globalState } from '$lib/state.svelte';
    import { projectState, fetchProjects } from '$lib/projects.svelte';
    import { telemetryState, connectTelemetry, disconnectTelemetry } from '$lib/telemetry.svelte';
    import { onMount } from 'svelte';

    import { onDestroy } from 'svelte';

    let hallucinations: any[] = $state([]);

    let groupedHallucinations = $derived.by(() => {
        const groups: Record<string, any> = {};
        for (const h of hallucinations) {
            if (!groups[h.model_name]) {
                groups[h.model_name] = {
                    model_name: h.model_name,
                    lies_detected: 0,
                    queries_processed: 0,
                    incidents: []
                };
            }
            groups[h.model_name].lies_detected += (h.lies_detected || 1);
            groups[h.model_name].queries_processed += (h.queries_processed || 1);
            groups[h.model_name].incidents.push(h);
        }
        return Object.values(groups).sort((a: any, b: any) => b.lies_detected - a.lies_detected);
    });

    let isModalOpen = $state(false);
    let selectedModel = $state<any>(null);

    function openModal(model: any) {
        selectedModel = model;
        isModalOpen = true;
    }

    function closeModal() {
        isModalOpen = false;
        selectedModel = null;
    }

    async function fetchHallucinations() {
        try {
            const res = await fetch('http://127.0.0.1:38001/v1/analytics/hallucinations');
            if (res.ok) {
                hallucinations = await res.json();
            }
        } catch(e) { console.error(e); }
    }

    onMount(() => {
        if (projectState.projects.length === 0) fetchProjects();
        connectTelemetry();
        fetchHallucinations();
    });

    onDestroy(() => {
        disconnectTelemetry();
    });

    let activeProjects = $derived(projectState.projects.filter(p => !p.is_archived).length);
    let totalTasks = $derived(projectState.projects.filter(p => !p.is_archived).reduce((acc, p) => acc + p.tasks.length, 0));
    let completedTasks = $derived(projectState.projects.filter(p => !p.is_archived).reduce((acc, p) => acc + p.tasks.filter(t => ['done', 'completed', 'concluído', 'concluido'].includes(t.status.toLowerCase())).length, 0));
    let progressPercent = $derived(totalTasks === 0 ? 0 : Math.round((completedTasks / totalTasks) * 100));

    let ramGB = $derived((telemetryState.ramUsageMB / 1024).toFixed(1));
    let ramTotalGB = $derived(telemetryState.ramTotalGB.toFixed(1));
    let ramPercent = $derived(((telemetryState.ramUsageMB / 1024) / telemetryState.ramTotalGB) * 100);

    let overallCpu = $derived(telemetryState.cpuCores.length > 0 ? (telemetryState.cpuCores.reduce((a, b) => a + b, 0) / telemetryState.cpuCores.length).toFixed(1) : "0.0");
    let rxFormatted = $derived(formatBytes(telemetryState.ioRxBytes));
    let txFormatted = $derived(formatBytes(telemetryState.ioTxBytes));

    const coreColors = ['bg-blue-500', 'bg-indigo-500', 'bg-purple-500', 'bg-pink-500', 'bg-rose-500', 'bg-orange-500', 'bg-amber-500', 'bg-yellow-500', 'bg-emerald-500', 'bg-teal-500'];

    function formatBytes(bytes: number, decimals = 1) {
        if (!+bytes) return '0 B';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
    }
</script>

<div class="flex flex-col h-full w-full bg-white dark:bg-[#12192b] rounded-2xl border border-slate-200 dark:border-[#424859]/20 shadow-[0_2px_12px_rgba(0,0,0,0.03)] dark:shadow-[0_24px_48px_-12px_rgba(0,0,0,0.5)] overflow-hidden">
    <!-- Sovereign Standard Sub-Header -->
    <header class="h-20 border-b border-slate-100 dark:border-[#424859]/20 bg-white dark:bg-[#12192b] flex items-center px-6 shrink-0 justify-between z-10 w-full">
        <div class="flex items-center gap-4">
            <div class="bg-indigo-600/10 dark:bg-[#74b0ff]/10 p-2.5 rounded-xl border border-indigo-100/50 dark:border-[#74b0ff]/20">
                <Activity class="w-6 h-6 text-indigo-600 dark:text-[#74b0ff]" />
            </div>
            <div class="flex flex-col">
                <div class="flex items-center gap-2">
                    <h1 class="text-lg font-bold tracking-tight text-slate-800 dark:text-slate-200">Hardware Telemetry</h1>
                    <span class="px-2 py-0.5 bg-blue-100/50 dark:bg-[#74b0ff]/10 text-blue-700 dark:text-[#74b0ff] text-[9px] uppercase tracking-widest font-bold rounded-full border border-blue-200/50 dark:border-[#74b0ff]/20">System Wide</span>
                </div>
                <span class="text-xs text-slate-500 dark:text-slate-400 font-medium">Real-time physical resource monitor & intelligence routing overview.</span>
            </div>
        </div>
        
        <div class="flex items-center gap-6">
            <div class="flex flex-col items-end">
                <span class="text-[10px] font-bold text-slate-400 uppercase tracking-widest leading-none mb-1.5">Local Cibrid Core</span>
                <div class="flex items-center gap-1.5">
                    <div class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.6)]"></div>
                    <span class="text-xs font-semibold text-emerald-600 dark:text-emerald-400">Online</span>
                </div>
            </div>
            <div class="h-8 w-px bg-slate-200/80 dark:bg-[#424859]/30"></div>
            
            <div class="flex items-center gap-2">
                <!-- User Manual Button -->
                <button onclick={() => globalState.isManualOpen = true} class="flex items-center gap-2 px-4 py-2 bg-white dark:bg-[#12192b] border border-emerald-200 dark:border-emerald-500/30 text-emerald-700 dark:text-emerald-400 rounded-xl text-xs font-black uppercase tracking-widest shadow-sm hover:bg-emerald-50 dark:hover:bg-emerald-500/10 hover:border-emerald-300 dark:hover:border-emerald-500/50 hover:text-emerald-800 dark:hover:text-emerald-300 transition-all cursor-pointer" title="📖 LER O MANUAL
                Entenda a arquitetura Cíbrida e os Comandos">
                    <BookOpen class="w-4 h-4" /> Manual
                </button>

                <!-- Kill Switch Button -->
                <button class="flex items-center gap-2 px-4 py-2 bg-white dark:bg-[#12192b] border border-rose-200 dark:border-rose-500/30 text-rose-600 dark:text-rose-400 rounded-xl text-xs font-black uppercase tracking-widest shadow-sm hover:bg-rose-50 dark:hover:bg-rose-500/10 hover:border-rose-300 dark:hover:border-rose-500/50 hover:text-rose-700 dark:hover:text-rose-300 transition-all cursor-pointer group" title="🔥 STOP TODOS OS MODELOS
    • Corta imediatamente a inferência LLM
    • Mantém o banco de dados online
    • Salva estado atual na memória">
                    <Power class="w-4 h-4 group-hover:animate-pulse" /> Kill Switch
                </button>
            </div>
        </div>
    </header>

    <!-- Scrollable Content Viewport -->
    <div class="flex-1 overflow-y-auto custom-scrollbar p-6 bg-slate-50/50 dark:bg-[#080e1d]">
        <div class="max-w-[1600px] mx-auto space-y-6">

    <!-- KDE-Style Wide System Monitor -->
    <div class="bg-white dark:bg-[#12192b] rounded-3xl border border-slate-200 dark:border-[#424859]/20 p-6 shadow-sm flex flex-col gap-6" title="💻 MONITORAMENTO HOST
Exibe o stress exato da máquina local rodando o Sovereign Core">
        <!-- CPU Matrix -->
        <div>
            <div class="flex justify-between items-center mb-2">
                <div class="flex items-center gap-2">
                    <Cpu class="w-4 h-4 text-slate-500 dark:text-slate-400" />
                    <span class="text-xs font-bold text-slate-600 dark:text-slate-300 uppercase tracking-widest">CPU Matrix & Core Usage</span>
                </div>
                <span class="text-xs font-mono text-slate-500 dark:text-slate-400 font-bold">{overallCpu}% OVERALL</span>
            </div>
            <div class="h-12 bg-slate-50 dark:bg-[#0c1324] rounded-lg border border-slate-100 dark:border-[#424859]/10 relative overflow-hidden">
                <!-- Master CPU Mock Line -->
                <div class="absolute bottom-0 w-full h-[60%] opacity-30 bg-gradient-to-t from-blue-500/20 dark:from-[#74b0ff]/20 to-transparent"></div>
                <svg class="absolute bottom-0 w-full h-full preserve-3d opacity-80" preserveAspectRatio="none" viewBox="0 0 100 100">
                    <path d="M0,100 L0,90 L10,88 L20,85 L30,90 L40,75 L45,40 L50,85 L60,88 L70,92 L80,90 L90,85 L100,88 L100,100 Z" fill="none" stroke="#3b82f6" stroke-width="1.5" vector-effect="non-scaling-stroke"/>
                </svg>
            </div>
            <div class="flex flex-wrap gap-x-6 gap-y-2 mt-3 px-1">
                {#each telemetryState.cpuCores as coreLoad, i}
                    <div class="flex items-center gap-2 text-[10px] font-mono"><span class="w-1.5 h-1.5 {coreColors[i % coreColors.length]} rounded"></span> <span class="text-slate-500 dark:text-slate-400">Core {i + 1}</span> <span class="text-slate-700 dark:text-slate-200 font-semibold">{coreLoad.toFixed(1)}%</span></div>
                {/each}
            </div>
        </div>

        <!-- GPU & Memory -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
                <div class="flex justify-between items-center mb-2">
                    <div class="flex items-center gap-2">
                        <Activity class="w-4 h-4 text-slate-500 dark:text-slate-400" />
                        <span class="text-xs font-bold text-slate-600 dark:text-slate-300 uppercase tracking-widest">GPU Compute</span>
                    </div>
                    <span class="text-[10px] font-mono {telemetryState.vramTotalMB > 0 ? 'text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-500/10' : 'text-slate-500 dark:text-slate-400 bg-slate-100 dark:bg-[#0c1324]'} font-bold px-2 py-0.5 rounded">
                        {telemetryState.vramTotalMB > 0 ? telemetryState.gpuName + ' (' + (telemetryState.vramTotalMB / 1024).toFixed(1) + ' GB VRAM)' : 'GPU Compute'}
                    </span>
                </div>
                <div class="h-12 bg-slate-50 dark:bg-[#0c1324] rounded-lg border border-slate-100 dark:border-[#424859]/10 relative overflow-hidden">
                    <div class="absolute bottom-0 w-full h-[40%] opacity-30 bg-gradient-to-t from-emerald-500/20 to-transparent"></div>
                    <svg class="absolute bottom-0 w-full h-full preserve-3d opacity-80" preserveAspectRatio="none" viewBox="0 0 100 100">
                        <path d="M0,100 L0,95 L20,95 L30,97 L40,94 L50,95 L60,95 L70,85 L80,90 L90,95 L100,92 L100,100 Z" fill="none" stroke="#10b981" stroke-width="1.5" vector-effect="non-scaling-stroke"/>
                    </svg>
                </div>
                <div class="flex justify-between text-[10px] font-mono mt-1 px-1">
                    <span class="text-slate-500 dark:text-slate-400">Temp: <span class="{telemetryState.gpuTemperature > 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-400 dark:text-slate-500'} font-semibold">{telemetryState.gpuTemperature > 0 ? telemetryState.gpuTemperature + 'ºC' : '--ºC'}</span></span>
                    <span class="text-slate-500 dark:text-slate-400">Load: <span class="{telemetryState.vramUsageMB > 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-400 dark:text-slate-500'} font-semibold">{telemetryState.vramUsageMB > 0 ? 'Active' : 'Idle'}</span></span>
                </div>
            </div>
            <div>
                <div class="flex justify-between items-center mb-2">
                    <div class="flex items-center gap-2">
                        <Database class="w-4 h-4 text-slate-500 dark:text-slate-400" />
                        <span class="text-xs font-bold text-slate-600 dark:text-slate-300 uppercase tracking-widest">Memory Allocation</span>
                    </div>
                    <span class="text-xs font-mono text-slate-500 dark:text-slate-400 font-bold">{ramGB} GiB / {ramTotalGB} GiB</span>
                </div>
                <div class="h-12 bg-slate-50 dark:bg-[#0c1324] rounded-lg border border-slate-100 dark:border-[#424859]/10 flex flex-col justify-end p-1 gap-0.5">
                    <div class="h-2.5 bg-blue-500/20 rounded-sm overflow-hidden" style="width: {ramPercent}%"><div class="w-full h-full bg-blue-500 relative"><div class="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTAgMjBMMjAgMEgxMEwwIDEwWiIgZmlsbD0icmdiYSgyNTUsMjU1LDI1NSwwLjEpIi8+PC9zdmc+')] opacity-20"></div></div></div>
                    <div class="w-[0%] h-2.5 bg-emerald-500/20 rounded-sm overflow-hidden"><div class="w-full h-full bg-emerald-500 relative"></div></div>
                    <div class="w-[0%] h-2.5 bg-rose-500/20 rounded-sm overflow-hidden"><div class="w-full h-full bg-rose-500 relative"></div></div>
                </div>
                <div class="flex gap-4 text-[10px] font-mono mt-1 px-1">
                    <span class="text-slate-500 dark:text-slate-400"><span class="text-blue-500 font-bold">■</span> Used</span>
                    <span class="text-slate-500 dark:text-slate-400"><span class="text-emerald-500 font-bold">■</span> Cache</span>
                    <span class="text-slate-500 dark:text-slate-400"><span class="text-rose-500 font-bold">■</span> Swap</span>
                </div>
            </div>
        </div>

        <!-- Network IO -->
        <div>
            <div class="flex justify-between items-center mb-2">
                <div class="flex items-center gap-2">
                    <Network class="w-4 h-4 text-slate-500 dark:text-slate-400" />
                    <span class="text-xs font-bold text-slate-600 dark:text-slate-300 uppercase tracking-widest">Network I/O</span>
                </div>
                <span class="text-xs font-mono text-slate-500 dark:text-slate-400 font-bold">Localhost Mesh</span>
            </div>
            <div class="h-10 bg-slate-50 dark:bg-[#0c1324] rounded-lg border border-slate-100 dark:border-[#424859]/10 relative overflow-hidden">
                <svg class="absolute bottom-0 w-full h-full preserve-3d opacity-80" preserveAspectRatio="none" viewBox="0 0 100 100">
                    <!-- Download (Blue) -->
                    <path d="M0,100 L10,100 L15,80 L20,100 L30,100 L35,90 L40,100 L60,100 L65,70 L70,100 L80,100 L85,60 L90,100 L100,100 Z" fill="rgba(59,130,246,0.05)" stroke="#3b82f6" stroke-width="1.5" vector-effect="non-scaling-stroke"/>
                    <!-- Upload (Orange/Red) -->
                    <path d="M0,100 L5,100 L10,85 L15,100 L40,100 L45,95 L50,100 L75,100 L80,80 L85,100 L95,100 L100,100 Z" fill="none" stroke="#f97316" stroke-width="1.5" vector-effect="non-scaling-stroke"/>
                </svg>
            </div>
            <div class="flex gap-6 text-[10px] font-mono mt-1 px-1">
                <span class="text-slate-500 dark:text-slate-400">↓ Download: <span class="text-blue-600 dark:text-blue-400 font-semibold">{rxFormatted}/s</span></span>
                <span class="text-slate-500 dark:text-slate-400">↑ Upload: <span class="text-orange-600 dark:text-orange-400 font-semibold">{txFormatted}/s</span></span>
            </div>
        </div>
    </div>

    <!-- Sovereign Intelligence Indicators (Recycled from Analytics) -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 shrink-0">
        <!-- Latency -->
        <div class="bg-white dark:bg-[#12192b] p-6 rounded-2xl border border-slate-200 dark:border-[#424859]/20 shadow-sm flex flex-col group hover:bg-slate-50 dark:hover:bg-[#1d253b] transition-colors duration-300">
            <div class="flex justify-between items-start mb-4">
                <span class="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest">LLM Routing Latency</span>
                <div class="p-1.5 bg-indigo-50 dark:bg-[#74b0ff]/10 rounded-lg">
                  <Timer class="text-indigo-600 dark:text-[#74b0ff] w-4 h-4" />
                </div>
            </div>
            <div class="text-2xl font-extrabold text-slate-800 dark:text-slate-200 mb-1 leading-none">{telemetryState.avgLatencyMs} <span class="text-sm text-slate-400 dark:text-slate-500 font-medium">ms</span></div>
            <div class="flex items-center gap-1.5 text-xs font-bold {telemetryState.avgLatencyMs > 0 ? 'text-emerald-500 dark:text-emerald-400' : 'text-slate-400 dark:text-slate-500'} mt-2">
                <CheckCircle2 class="w-3.5 h-3.5" /> {telemetryState.avgLatencyMs > 0 ? 'Healthy' : 'Awaiting Data'}
            </div>
        </div>

        <!-- Throughput -->
        <div class="bg-white dark:bg-[#12192b] p-6 rounded-2xl border border-slate-200 dark:border-[#424859]/20 shadow-sm flex flex-col group hover:bg-slate-50 dark:hover:bg-[#1d253b] transition-colors duration-300">
            <div class="flex justify-between items-start mb-4">
                <span class="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest">Inference Speed</span>
                <div class="p-1.5 bg-teal-50 dark:bg-teal-500/10 rounded-lg">
                  <Zap class="text-teal-600 dark:text-teal-400 w-4 h-4" />
                </div>
            </div>
            <div class="text-2xl font-extrabold text-slate-800 dark:text-slate-200 mb-1 leading-none">{telemetryState.tokensPerSecond} <span class="text-sm text-slate-400 dark:text-slate-500 font-medium">tokens/s</span></div>
            <div class="flex items-center gap-1.5 text-xs font-bold {telemetryState.tokensPerSecond > 0 ? 'text-emerald-500 dark:text-emerald-400' : 'text-slate-400 dark:text-slate-500'} mt-2">
                <Zap class="w-3.5 h-3.5" /> {telemetryState.tokensPerSecond > 0 ? 'Peak Output' : 'Idle'}
            </div>
        </div>

        <!-- Security Alerts -->
        <div class="bg-white dark:bg-[#12192b] p-6 rounded-2xl border border-slate-100 dark:border-[#424859]/20 shadow-sm hover:border-rose-200 dark:hover:border-rose-500/50 hover:bg-rose-50/30 dark:hover:bg-rose-500/10 transition-all flex flex-col group cursor-help" title="🛡️ FIREWALL BLOCKS
Bloqueios feitos por políticas de segurança. Inclui tentativas de vazamento PII ou injeções nocivas.">
            <div class="flex justify-between items-start mb-4">
                <span class="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest">Firewall Blocks</span>
                <div class="p-1.5 bg-rose-50 dark:bg-rose-500/10 rounded-lg">
                  <AlertTriangle class="text-rose-600 dark:text-rose-400 w-4 h-4" />
                </div>
            </div>
            <div class="text-2xl font-extrabold text-slate-800 dark:text-slate-200 mb-1 leading-none">{telemetryState.firewallBlocks}</div>
            <div class="flex items-center gap-1.5 text-xs font-bold text-slate-500 dark:text-slate-400 mt-2">
                <ShieldCheck class="w-3.5 h-3.5 text-emerald-500 dark:text-emerald-400" /> Secured by Guardrails
            </div>
        </div>
    </div>

    <!-- Epistemic Ledger (Hallucinations) -->
    <div class="bg-white dark:bg-[#12192b] p-6 rounded-2xl border border-slate-200 dark:border-[#424859]/20 shadow-sm shrink-0 hover:bg-slate-50 dark:hover:bg-[#1d253b] transition-colors duration-300">
        <div class="flex justify-between items-center mb-4">
            <div class="flex items-center gap-2">
                <ShieldCheck class="w-5 h-5 text-indigo-600 dark:text-[#74b0ff]" />
                <h2 class="text-sm font-bold text-slate-800 dark:text-slate-200 tracking-tight">Epistemic Ledger (Hallucinations)</h2>
            </div>
            <span class="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded-full">Quorum Tracker</span>
        </div>
        {#if hallucinations.length === 0}
            <div class="flex flex-col items-center justify-center py-6 text-slate-400 dark:text-slate-500 text-sm">
                <ShieldCheck class="w-8 h-8 opacity-20 mb-2" />
                No mathematical hallucinations recorded yet.
            </div>
        {:else}
            <div class="overflow-y-auto max-h-[300px] custom-scrollbar rounded-xl border border-slate-100 dark:border-[#424859]/20">
                <table class="w-full text-left text-xs text-slate-600 dark:text-slate-300 relative">
                    <thead class="bg-slate-50 dark:bg-[#0c1324] border-b border-slate-100 dark:border-[#424859]/20 text-[10px] uppercase font-bold text-slate-500 dark:text-slate-400 sticky top-0 z-10 shadow-sm">
                        <tr>
                            <th class="px-4 py-3">Model Engine</th>
                            <th class="px-4 py-3 text-center">Lies Detected</th>
                            <th class="px-4 py-3 text-center">Total Queries</th>
                            <th class="px-4 py-3 text-right">Incidents History</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-100/50 dark:divide-[#424859]/20">
                        {#each groupedHallucinations as h}
                            <tr class="hover:bg-slate-50/50 dark:hover:bg-[#1d253b] transition-colors">
                                <td class="px-4 py-3 font-mono font-semibold">
                                    <button class="text-indigo-600 dark:text-[#74b0ff] hover:text-indigo-800 dark:hover:text-blue-300 underline decoration-indigo-300 dark:decoration-[#74b0ff]/50 underline-offset-2 transition-colors cursor-pointer text-left" onclick={() => openModal(h)}>
                                        {h.model_name}
                                    </button>
                                </td>
                                <td class="px-4 py-3 text-center">
                                    <span class="bg-rose-100 dark:bg-rose-500/10 text-rose-700 dark:text-rose-400 px-2 py-0.5 rounded font-bold shadow-sm border border-rose-200 dark:border-rose-500/20">{h.lies_detected}</span>
                                </td>
                                <td class="px-4 py-3 text-center text-slate-500 dark:text-slate-400 font-mono font-bold">{h.queries_processed}</td>
                                <td class="px-4 py-3 text-right text-slate-400 dark:text-slate-500 font-medium">
                                    <button class="px-3 py-1 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300 rounded-md transition-colors text-[10px] font-bold uppercase tracking-widest cursor-pointer" onclick={() => openModal(h)}>
                                        View {h.incidents.length} dates
                                    </button>
                                </td>
                            </tr>
                        {/each}
                    </tbody>
                </table>
            </div>
        {/if}
    </div>

    <!-- Knowledge & Workspace Hub -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6 shrink-0">
        <!-- Vaults & Ingestion -->
        <div class="bg-white dark:bg-[#12192b] p-6 rounded-2xl border border-slate-200 dark:border-[#424859]/20 shadow-sm flex flex-col hover:bg-slate-50 dark:hover:bg-[#1d253b] transition-colors duration-300">
            <div class="flex justify-between items-start mb-4">
                <span class="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest">Active Vaults</span>
                <div class="p-1.5 bg-blue-50 dark:bg-blue-500/10 rounded-lg">
                  <FolderSync class="text-blue-600 dark:text-blue-400 w-4 h-4" />
                </div>
            </div>
            <div class="text-2xl font-extrabold text-slate-800 dark:text-slate-200 mb-1 leading-none">{telemetryState.vaultsCount} <span class="text-sm text-slate-400 dark:text-slate-500 font-medium">Vaults</span></div>
            <div class="flex items-center gap-1.5 text-xs font-bold text-blue-500 dark:text-blue-400 mt-2">
                <FileText class="w-3.5 h-3.5" /> {telemetryState.syncedFiles} Files Synced
            </div>
        </div>

        <!-- Knowledge Categories -->
        <div class="bg-white dark:bg-[#12192b] p-6 rounded-2xl border border-slate-200 dark:border-[#424859]/20 shadow-sm flex flex-col hover:bg-slate-50 dark:hover:bg-[#1d253b] transition-colors duration-300">
            <div class="flex justify-between items-start mb-4">
                <span class="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest">Categories Placed</span>
                <div class="p-1.5 bg-purple-50 dark:bg-purple-500/10 rounded-lg">
                  <Tags class="text-purple-600 dark:text-purple-400 w-4 h-4" />
                </div>
            </div>
            <div class="text-2xl font-extrabold text-slate-800 dark:text-slate-200 mb-1 leading-none">{telemetryState.vaultCategories.length} <span class="text-sm text-slate-400 dark:text-slate-500 font-medium">Categories</span></div>
            <div class="flex items-center gap-1.5 text-xs font-bold text-purple-500 dark:text-purple-400 mt-2">
                <Tags class="w-3.5 h-3.5" /> Mapped from Local Vault
            </div>
        </div>

        <!-- Active Projects -->
        <div class="bg-white dark:bg-[#12192b] p-6 rounded-2xl border border-slate-200 dark:border-[#424859]/20 shadow-sm flex flex-col hover:bg-slate-50 dark:hover:bg-[#1d253b] transition-colors duration-300">
            <div class="flex justify-between items-start mb-4">
                <span class="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest">Active Projects</span>
                <div class="p-1.5 bg-amber-50 dark:bg-amber-500/10 rounded-lg">
                  <Briefcase class="text-amber-600 dark:text-amber-400 w-4 h-4" />
                </div>
            </div>
            <div class="text-2xl font-extrabold text-slate-800 dark:text-slate-200 mb-1 leading-none">{activeProjects}</div>
            <div class="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-1.5 mt-2 mb-1">
                <div class="bg-amber-500 dark:bg-amber-400 h-1.5 rounded-full" style="width: {progressPercent}%"></div>
            </div>
            <div class="flex justify-between items-center text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase mt-1">
                <span>Progress</span>
                <span class="text-amber-600 dark:text-amber-400">{progressPercent}%</span>
            </div>
        </div>

        <!-- Pending Tasks -->
        <div class="bg-white dark:bg-[#12192b] p-6 rounded-2xl border border-slate-200 dark:border-[#424859]/20 shadow-sm flex flex-col hover:bg-slate-50 dark:hover:bg-[#1d253b] transition-colors duration-300">
            <div class="flex justify-between items-start mb-4">
                <span class="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest">Pending Tasks</span>
                <div class="p-1.5 bg-emerald-50 dark:bg-emerald-500/10 rounded-lg">
                  <CheckSquare class="text-emerald-600 dark:text-emerald-400 w-4 h-4" />
                </div>
            </div>
            <div class="text-2xl font-extrabold text-slate-800 dark:text-slate-200 mb-1 leading-none">{totalTasks - completedTasks} <span class="text-sm text-slate-400 dark:text-slate-500 font-medium">To-do</span></div>
            <div class="flex items-center gap-1.5 text-xs font-bold text-emerald-500 dark:text-emerald-400 mt-2">
                <Layers class="w-3.5 h-3.5" /> {completedTasks} Completed total
            </div>
        </div>
    </div>
    </div>
</div>
</div>

{#if isModalOpen && selectedModel}
    <div class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-4" onclick={closeModal} onkeydown={(e) => e.key === 'Escape' && closeModal()} role="presentation">
        <div class="bg-white dark:bg-[#12192b] rounded-3xl shadow-xl dark:shadow-[0_24px_48px_-12px_rgba(0,0,0,0.5)] border border-slate-200 dark:border-[#424859]/20 w-full max-w-lg overflow-hidden flex flex-col max-h-[85vh] animate-in fade-in zoom-in-95 duration-200" onclick={(e) => e.stopPropagation()} onkeydown={(e) => e.stopPropagation()} role="presentation">
            <div class="px-6 py-5 border-b border-slate-100 dark:border-[#424859]/20 flex items-center justify-between bg-slate-50/50 dark:bg-[#0c1324]">
                <div>
                    <h3 class="text-lg font-bold text-slate-800 dark:text-slate-200 tracking-tight">Incident Ledger</h3>
                    <p class="text-xs text-slate-500 dark:text-slate-400 font-mono mt-1 font-semibold">{selectedModel.model_name}</p>
                </div>
                <button class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-slate-200 dark:hover:bg-slate-800 text-slate-400 dark:text-slate-500 transition-colors cursor-pointer" onclick={closeModal} aria-label="Close Modal">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                </button>
            </div>
            <div class="p-6 overflow-y-auto custom-scrollbar flex-1">
                <div class="space-y-3">
                    {#each selectedModel.incidents as inc}
                        <div class="flex flex-col p-4 rounded-xl border border-slate-100 dark:border-[#424859]/20 bg-white dark:bg-[#12192b] hover:border-indigo-100 dark:hover:border-indigo-500/50 hover:shadow-sm dark:hover:bg-[#1d253b] transition-all text-left group">
                            <div class="flex justify-between items-center mb-2">
                                <span class="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest group-hover:text-indigo-500 dark:group-hover:text-[#74b0ff] transition-colors">Incident Timestamp</span>
                                <span class="text-xs font-mono text-slate-600 dark:text-slate-300 font-bold bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded">{inc.last_lied_at}</span>
                            </div>
                            <div class="flex gap-4">
                                <div class="text-xs text-slate-500 dark:text-slate-400"><span class="font-semibold text-rose-500 dark:text-rose-400">Lies:</span> {inc.lies_detected}</div>
                                <div class="text-xs text-slate-500 dark:text-slate-400"><span class="font-semibold text-blue-500 dark:text-blue-400">Queries:</span> {inc.queries_processed}</div>
                            </div>
                        </div>
                    {/each}
                </div>
            </div>
            <div class="px-6 py-4 bg-slate-50 dark:bg-[#0c1324] border-t border-slate-100 dark:border-[#424859]/20 flex justify-end shrink-0">
                <button class="px-4 py-2 bg-indigo-600 dark:bg-indigo-500/20 hover:bg-indigo-700 dark:hover:bg-indigo-500/30 text-white dark:text-[#74b0ff] text-xs font-bold rounded-lg shadow-sm transition-colors cursor-pointer" onclick={closeModal}>Close Details</button>
            </div>
        </div>
    </div>
{/if}
