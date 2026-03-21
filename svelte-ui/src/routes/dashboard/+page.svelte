<script lang="ts">
    import { Activity, Cpu, Network, Zap, Timer, CheckCircle2, AlertTriangle, AlertCircle, Power, ShieldCheck, Database } from 'lucide-svelte';
</script>

<div class="p-6 max-w-[1600px] mx-auto space-y-6 h-full overflow-y-auto custom-scrollbar">
    <!-- Headline & Kill Switch Section -->
    <div class="flex justify-between items-end shrink-0">
        <div>
            <h1 class="text-3xl font-extrabold text-slate-800 tracking-tight mb-2">Hardware Telemetry</h1>
            <p class="text-slate-500 max-w-lg text-sm">System-wide monitor for physical resources and real-time intelligence routing overview.</p>
        </div>
        <div class="flex gap-3">
            <button class="flex items-center gap-2 px-6 py-2.5 bg-rose-600 text-white rounded-xl text-xs font-black uppercase tracking-widest shadow-[0_4px_14px_rgba(225,29,72,0.3)] hover:bg-rose-700 hover:shadow-[0_6px_20px_rgba(225,29,72,0.4)] transition-all cursor-pointer group">
                <Power class="w-4 h-4 group-hover:animate-pulse" /> System Kill Switch
            </button>
        </div>
    </div>

    <!-- KDE-Style Wide System Monitor -->
    <div class="bg-[#1e293b] rounded-3xl border border-slate-700 p-6 shadow-xl flex flex-col gap-6">
        <!-- CPU Matrix -->
        <div>
            <div class="flex justify-between items-center mb-2">
                <div class="flex items-center gap-2">
                    <Cpu class="w-4 h-4 text-slate-400" />
                    <span class="text-xs font-bold text-slate-300 uppercase tracking-widest">CPU Matrix & Core Usage</span>
                </div>
                <span class="text-xs font-mono text-slate-400">14.2% OVERALL</span>
            </div>
            <div class="h-12 bg-slate-900 rounded-lg border border-slate-800 relative overflow-hidden">
                <!-- Master CPU Mock Line -->
                <div class="absolute bottom-0 w-full h-[60%] opacity-50 bg-gradient-to-t from-blue-500/20 to-transparent"></div>
                <svg class="absolute bottom-0 w-full h-full preserve-3d" preserveAspectRatio="none" viewBox="0 0 100 100">
                    <path d="M0,100 L0,90 L10,88 L20,85 L30,90 L40,75 L45,40 L50,85 L60,88 L70,92 L80,90 L90,85 L100,88 L100,100 Z" fill="none" stroke="#3b82f6" stroke-width="1.5" vector-effect="non-scaling-stroke"/>
                </svg>
            </div>
            <div class="flex flex-wrap gap-x-6 gap-y-2 mt-3 px-1">
                <div class="flex items-center gap-2 text-[10px] font-mono"><span class="w-1.5 h-1.5 bg-blue-500 rounded"></span> <span class="text-slate-400">Core 1</span> <span class="text-slate-300">12.0%</span></div>
                <div class="flex items-center gap-2 text-[10px] font-mono"><span class="w-1.5 h-1.5 bg-indigo-500 rounded"></span> <span class="text-slate-400">Core 2</span> <span class="text-slate-300">8.4%</span></div>
                <div class="flex items-center gap-2 text-[10px] font-mono"><span class="w-1.5 h-1.5 bg-purple-500 rounded"></span> <span class="text-slate-400">Core 3</span> <span class="text-slate-300">4.1%</span></div>
                <div class="flex items-center gap-2 text-[10px] font-mono"><span class="w-1.5 h-1.5 bg-pink-500 rounded"></span> <span class="text-slate-400">Core 4</span> <span class="text-slate-300">9.9%</span></div>
                <div class="flex items-center gap-2 text-[10px] font-mono"><span class="w-1.5 h-1.5 bg-rose-500 rounded"></span> <span class="text-slate-400">Core 5</span> <span class="text-slate-300">64.2%</span></div>
                <div class="flex items-center gap-2 text-[10px] font-mono"><span class="w-1.5 h-1.5 bg-orange-500 rounded"></span> <span class="text-slate-400">Core 6</span> <span class="text-slate-300">11.3%</span></div>
                <div class="flex items-center gap-2 text-[10px] font-mono"><span class="w-1.5 h-1.5 bg-amber-500 rounded"></span> <span class="text-slate-400">Core 7</span> <span class="text-slate-300">5.0%</span></div>
                <div class="flex items-center gap-2 text-[10px] font-mono"><span class="w-1.5 h-1.5 bg-yellow-500 rounded"></span> <span class="text-slate-400">Core 8</span> <span class="text-slate-300">2.1%</span></div>
            </div>
        </div>

        <!-- GPU & Memory -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
                <div class="flex justify-between items-center mb-2">
                    <div class="flex items-center gap-2">
                        <Activity class="w-4 h-4 text-slate-400" />
                        <span class="text-xs font-bold text-slate-300 uppercase tracking-widest">GPU Compute</span>
                    </div>
                    <span class="text-[10px] font-mono text-emerald-400">RTX 4090 Active</span>
                </div>
                <div class="h-12 bg-slate-900 rounded-lg border border-slate-800 relative overflow-hidden">
                    <div class="absolute bottom-0 w-full h-[40%] opacity-30 bg-gradient-to-t from-emerald-500/20 to-transparent"></div>
                    <svg class="absolute bottom-0 w-full h-full preserve-3d" preserveAspectRatio="none" viewBox="0 0 100 100">
                        <path d="M0,100 L0,95 L20,95 L30,97 L40,94 L50,95 L60,95 L70,85 L80,90 L90,95 L100,92 L100,100 Z" fill="none" stroke="#10b981" stroke-width="1.5" vector-effect="non-scaling-stroke"/>
                    </svg>
                </div>
                <div class="flex justify-between text-[10px] font-mono mt-1 px-1">
                    <span class="text-slate-400">Temp: <span class="text-emerald-400">64ºC</span></span>
                    <span class="text-slate-400">Load: <span class="text-emerald-400">82.4%</span></span>
                </div>
            </div>
            <div>
                <div class="flex justify-between items-center mb-2">
                    <div class="flex items-center gap-2">
                        <Database class="w-4 h-4 text-slate-400" />
                        <span class="text-xs font-bold text-slate-300 uppercase tracking-widest">Memory Allocation</span>
                    </div>
                    <span class="text-xs font-mono text-slate-400">18.4 GiB / 32.0 GiB</span>
                </div>
                <div class="h-12 bg-slate-900 rounded-lg border border-slate-800 flex flex-col justify-end p-1 gap-0.5">
                    <div class="w-[80%] h-2.5 bg-blue-500/50 rounded-sm overflow-hidden"><div class="w-full h-full bg-blue-500 relative"><div class="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTAgMjBMMjAgMEgxMEwwIDEwWiIgZmlsbD0icmdiYSgyNTUsMjU1LDI1NSwwLjEpIi8+PC9zdmc+')] opacity-30"></div></div></div>
                    <div class="w-[55%] h-2.5 bg-emerald-500/50 rounded-sm overflow-hidden"><div class="w-full h-full bg-emerald-500 relative"></div></div>
                    <div class="w-[15%] h-2.5 bg-rose-500/50 rounded-sm overflow-hidden"><div class="w-full h-full bg-rose-500 relative"></div></div>
                </div>
                <div class="flex gap-4 text-[10px] font-mono mt-1 px-1">
                    <span class="text-slate-400"><span class="text-blue-500">■</span> Used</span>
                    <span class="text-slate-400"><span class="text-emerald-500">■</span> Cache</span>
                    <span class="text-slate-400"><span class="text-rose-500">■</span> Swap</span>
                </div>
            </div>
        </div>

        <!-- Network IO -->
        <div>
            <div class="flex justify-between items-center mb-2">
                <div class="flex items-center gap-2">
                    <Network class="w-4 h-4 text-slate-400" />
                    <span class="text-xs font-bold text-slate-300 uppercase tracking-widest">Network I/O</span>
                </div>
                <span class="text-xs font-mono text-slate-400">Localhost Mesh</span>
            </div>
            <div class="h-10 bg-slate-900 rounded-lg border border-slate-800 relative overflow-hidden">
                <svg class="absolute bottom-0 w-full h-full preserve-3d" preserveAspectRatio="none" viewBox="0 0 100 100">
                    <!-- Download (Blue) -->
                    <path d="M0,100 L10,100 L15,80 L20,100 L30,100 L35,90 L40,100 L60,100 L65,70 L70,100 L80,100 L85,60 L90,100 L100,100 Z" fill="rgba(59,130,246,0.1)" stroke="#3b82f6" stroke-width="1.5" vector-effect="non-scaling-stroke"/>
                    <!-- Upload (Orange/Red) -->
                    <path d="M0,100 L5,100 L10,85 L15,100 L40,100 L45,95 L50,100 L75,100 L80,80 L85,100 L95,100 L100,100 Z" fill="none" stroke="#f97316" stroke-width="1.5" vector-effect="non-scaling-stroke"/>
                </svg>
            </div>
            <div class="flex gap-6 text-[10px] font-mono mt-1 px-1">
                <span class="text-slate-400">↓ Download: <span class="text-blue-400">680.0 B/s</span></span>
                <span class="text-slate-400">↑ Upload: <span class="text-orange-400">12.5 KB/s</span></span>
            </div>
        </div>
    </div>

    <!-- Sovereign Intelligence Indicators (Recycled from Analytics) -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 shrink-0">
        <!-- Latency -->
        <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col group">
            <div class="flex justify-between items-start mb-4">
                <span class="text-xs font-bold text-slate-400 uppercase tracking-widest">LLM Routing Latency</span>
                <div class="p-1.5 bg-indigo-50 rounded-lg">
                  <Timer class="text-indigo-600 w-4 h-4" />
                </div>
            </div>
            <div class="text-2xl font-extrabold text-slate-800 mb-1 leading-none">450 <span class="text-sm text-slate-400 font-medium">ms</span></div>
            <div class="flex items-center gap-1.5 text-xs font-bold text-emerald-500 mt-2">
                <CheckCircle2 class="w-3.5 h-3.5" /> Healthy
            </div>
        </div>

        <!-- Throughput -->
        <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col group">
            <div class="flex justify-between items-start mb-4">
                <span class="text-xs font-bold text-slate-400 uppercase tracking-widest">Inference Speed</span>
                <div class="p-1.5 bg-teal-50 rounded-lg">
                  <Zap class="text-teal-600 w-4 h-4" />
                </div>
            </div>
            <div class="text-2xl font-extrabold text-slate-800 mb-1 leading-none">1250 <span class="text-sm text-slate-400 font-medium">tokens/s</span></div>
            <div class="flex items-center gap-1.5 text-xs font-bold text-emerald-500 mt-2">
                <Zap class="w-3.5 h-3.5" /> Peak Output
            </div>
        </div>

        <!-- Security Alerts -->
        <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col group">
            <div class="flex justify-between items-start mb-4">
                <span class="text-xs font-bold text-slate-400 uppercase tracking-widest">Firewall Blocks</span>
                <div class="p-1.5 bg-rose-50 rounded-lg">
                  <AlertTriangle class="text-rose-600 w-4 h-4" />
                </div>
            </div>
            <div class="text-2xl font-extrabold text-slate-800 mb-1 leading-none">12</div>
            <div class="flex items-center gap-1.5 text-xs font-bold text-slate-500 mt-2">
                <ShieldCheck class="w-3.5 h-3.5 text-slate-400" /> Secured by Guardrails
            </div>
        </div>
    </div>
</div>
