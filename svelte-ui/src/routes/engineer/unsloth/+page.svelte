<script lang="ts">
    import { onMount } from 'svelte';
    import { trainerState, fetchTrainerStats, sendUnslothControl } from '$lib/trainer.svelte';

    let logs = $state<string[]>([]);
    let eventSource: EventSource;
    let logContainer: HTMLElement;
    let pollingInterval: any;

    onMount(() => {
        // Start Global Polling
        fetchTrainerStats();
        pollingInterval = setInterval(fetchTrainerStats, 10000);

        eventSource = new EventSource('http://localhost:38001/v1/engineer/trainer/unsloth-monitor');
        
        eventSource.onmessage = (event) => {
            logs.push(event.data);
            if (logContainer) {
                setTimeout(() => logContainer.scrollTop = logContainer.scrollHeight, 50);
            }
        };

        return () => {
            clearInterval(pollingInterval);
            if (eventSource) eventSource.close();
        };
    });
</script>

<div class="p-8 h-full flex flex-col relative w-full">
    <!-- Header Section -->
    <header class="mb-10 w-full flex items-center justify-between">
        <div class="flex items-center gap-4">
            <h2 class=" font-bold text-xl text-[#191c1d] tracking-tight">Unsloth Monitor</h2>
            <div class="h-4 w-[1px] bg-outline-variant"></div>
            <div class="flex bg-surface-container-high rounded-full p-1 text-[12px] font-semibold">
                <button class="px-4 py-1 rounded-full bg-white text-primary shadow-sm font-bold">Local Compute</button>
                <button class="px-4 py-1 rounded-full text-on-surface-variant hover:text-on-surface transition-colors">Remote Cluster</button>
            </div>
        </div>
        <div class="flex items-center gap-4 bg-surface-container-low p-1.5 rounded-xl border border-outline-variant/10">
            <a href="/engineer/fine-tuning" class="px-4 py-2 text-on-surface-variant font-medium text-xs rounded-lg hover:bg-surface-container-high transition-colors">Fine-Tuning</a>
            <a href="/engineer/distillation" class="px-4 py-2 text-on-surface-variant font-medium text-xs rounded-lg hover:bg-surface-container-high transition-colors">Distillation</a>
            <a href="/engineer/reflection" class="px-4 py-2 text-on-surface-variant font-medium text-xs rounded-lg hover:bg-surface-container-high transition-colors">Reflection Lab</a>
            <a href="/engineer/rag-pipeline" class="px-4 py-2 text-on-surface-variant font-medium text-xs rounded-lg hover:bg-surface-container-high transition-colors">RAG Pipeline</a>
            <button class="px-4 py-2 bg-surface-container-lowest text-primary font-bold text-xs rounded-lg shadow-sm">Unsloth Monitor</button>
            <a href="/engineer/analytics" class="px-4 py-2 text-on-surface-variant font-medium text-xs rounded-lg hover:bg-surface-container-high transition-colors">Analytics</a>
        </div>
    </header>

    <!-- Bento Grid Content -->
    <div class="grid grid-cols-12 gap-6 w-full flex-1 mb-8">
        
        <!-- Training Controls & Hardware Quick Stats (Left Col) -->
        <div class="col-span-12 xl:col-span-4 flex flex-col gap-6">
            <div class="bg-surface-container-lowest p-6 rounded-3xl shadow-sm border border-outline-variant/10 h-fit">
                <h3 class=" text-on-surface-variant text-[11px] font-extrabold uppercase tracking-widest mb-6">Control Center</h3>
                <div class="flex flex-col gap-3">
                    <button onclick={() => sendUnslothControl('play')} class="bg-gradient-to-br from-[#001360] to-[#002395] text-white w-full py-3.5 rounded-xl font-bold flex items-center justify-center gap-2 active:scale-[0.98] transition-all shadow-md shadow-primary/20">
                        <span class="material-symbols-outlined text-[20px]">play_arrow</span>
                        Start Training
                    </button>
                    <div class="grid grid-cols-2 gap-3">
                        <button onclick={() => sendUnslothControl('pause')} class="bg-surface-container-low border border-outline-variant/10 text-on-surface-variant py-3 rounded-xl font-bold text-sm flex items-center justify-center gap-2 hover:bg-surface-container-highest transition-all">
                            <span class="material-symbols-outlined text-[18px]">pause</span>
                            Pause
                        </button>
                        <button onclick={() => sendUnslothControl('stop')} class="bg-primary-container/10 border border-primary-container/20 text-primary py-3 rounded-xl font-bold text-sm flex items-center justify-center gap-2 hover:bg-primary-container/20 transition-all">
                            <span class="material-symbols-outlined text-[18px]">stop</span>
                            Stop / Merge
                        </button>
                    </div>
                </div>
            </div>

            <!-- Hardware Quick Stats -->
            <div class="bg-surface-container-lowest p-6 rounded-3xl border border-outline-variant/10 shadow-sm flex-1">
                <div class="flex items-center justify-between mb-8">
                    <h3 class=" text-on-surface-variant text-[11px] font-extrabold uppercase tracking-widest">Active Resource</h3>
                    <span class="text-[10px] bg-tertiary-container/10 text-on-tertiary-fixed-variant px-2.5 py-1 rounded-md font-bold border border-tertiary-container/20">Local Sovereign Compute</span>
                </div>
                
                <div class="space-y-6">
                    <div>
                        <div class="flex justify-between text-[13px] mb-2">
                            <span class="font-bold text-on-surface">VRAM / Memory Allocation</span>
                            <span class="text-primary font-bold">{trainerState.isTraining ? `${trainerState.vramUsageGb} GB / ${trainerState.vramTotalGb} GB` : 'Waiting telemetry...'}</span>
                        </div>
                        <div class="h-2.5 bg-surface-variant rounded-full overflow-hidden">
                            <div class="h-full bg-gradient-to-r from-primary to-primary-container transition-all duration-1000" style="width: {trainerState.isTraining ? Math.min((trainerState.vramUsageGb / trainerState.vramTotalGb) * 100, 100) : 0}%"></div>
                        </div>
                    </div>
                    <div>
                        <div class="flex justify-between text-[13px] mb-2">
                            <span class="font-bold text-on-surface">Compute Load</span>
                            <span class="text-[#50606f] font-bold">{trainerState.isTraining ? 'Active Processing' : 'Idle'}</span>
                        </div>
                        <div class="h-2.5 bg-surface-variant rounded-full overflow-hidden">
                            <div class="h-full bg-[linear-gradient(45deg,var(--tw-gradient-stops))] from-tertiary to-tertiary-container transition-all duration-1000 animate-[progress-stripe_2s_linear_infinite]" style="width: {trainerState.isTraining ? '80%' : '0%'}"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Epoch Progress & Telemetry (Right Col) -->
        <div class="col-span-12 xl:col-span-8 flex flex-col gap-6">
            <div class="bg-surface-container-lowest p-8 rounded-3xl shadow-sm border border-outline-variant/10 relative overflow-hidden">
                <div class="flex justify-between items-start mb-10 pb-6 border-b border-outline-variant/10">
                    <div>
                        <h2 class=" text-3xl font-extrabold text-[#191c1d]">Fine-Tuning Execution</h2>
                        <p class="text-on-surface-variant text-sm mt-1.5 font-mono font-medium">Llama-3-8B-Instruct-v0.1 • LoRA Adapter: alpha_v2</p>
                    </div>
                    <div class="text-right">
                        <div class="text-3xl font-extrabold text-primary">Epoch {trainerState.epochCurrent}/{trainerState.epochTotal}</div>
                        <p class="text-[11px] text-on-surface-variant font-bold uppercase tracking-widest mt-1">Est. Completion: Calculating...</p>
                    </div>
                </div>
                
                <!-- Progress Bar Visual -->
                <div class="mb-10">
                    <div class="flex justify-between text-[11px] font-extrabold uppercase tracking-widest text-on-surface-variant mb-3">
                        <span>Total Progress</span>
                        <span class="text-primary">{Math.min((trainerState.epochCurrent / trainerState.epochTotal) * 100, 100).toFixed(1)}%</span>
                    </div>
                    <div class="h-4 bg-surface-variant rounded-full p-0.5">
                        <div class="h-full bg-gradient-to-r from-primary to-primary-fixed-dim rounded-full relative overflow-hidden shadow-[0_0_10px_rgba(0,19,96,0.3)] transition-all duration-1000" style="width: {Math.min((trainerState.epochCurrent / trainerState.epochTotal) * 100, 100)}%">
                            {#if trainerState.isTraining}
                            <div class="absolute top-0 left-0 right-0 bottom-0 bg-[linear-gradient(45deg,rgba(255,255,255,0.15)_25%,transparent_25%,transparent_50%,rgba(255,255,255,0.15)_50%,rgba(255,255,255,0.15)_75%,transparent_75%,transparent)] bg-[length:1rem_1rem] animate-[progress-stripe_1s_linear_infinite]"></div>
                            {/if}
                        </div>
                    </div>
                </div>

                <!-- Mini Stats Row -->
                <div class="grid grid-cols-4 gap-4">
                    <div class="p-5 bg-surface-container-low rounded-2xl border border-outline-variant/10 relative overflow-hidden group">
                        <div class="absolute -right-4 -bottom-4 w-16 h-16 bg-on-tertiary-container/10 rounded-full blur-xl transition-all group-hover:scale-150 group-hover:bg-on-tertiary-container/30"></div>
                        <p class="text-[10px] text-on-surface-variant font-extrabold uppercase tracking-widest mb-1.5 line-clamp-1">Current Loss</p>
                        <p class="text-2xl font-extrabold text-[#191c1d] transition-all">{trainerState.loss}</p>
                        <p class="text-[11px] text-on-tertiary-container font-extrabold mt-1 uppercase tracking-tight flex items-center gap-1">
                            <span class="material-symbols-outlined text-[14px]">arrow_downward</span>
                            Converging
                        </p>
                    </div>
                    <div class="p-5 bg-surface-container-low rounded-2xl border border-outline-variant/10 relative overflow-hidden">
                        <p class="text-[10px] text-on-surface-variant font-extrabold uppercase tracking-widest mb-1.5 line-clamp-1">Grad Norm</p>
                        <p class="text-2xl font-extrabold text-[#191c1d] transition-all">{trainerState.gradNorm}</p>
                        <p class="text-[11px] text-on-secondary-container font-extrabold mt-1 uppercase tracking-tight flex items-center gap-1">
                            Stable
                        </p>
                    </div>
                    <div class="p-5 bg-surface-container-low rounded-2xl border border-outline-variant/10 relative overflow-hidden">
                        <p class="text-[10px] text-on-surface-variant font-extrabold uppercase tracking-widest mb-1.5 line-clamp-1">Learning Rate</p>
                        <p class="text-2xl font-extrabold text-[#191c1d] transition-all">{trainerState.learningRateLabel}</p>
                        <p class="text-[11px] text-on-surface-variant font-bold mt-1 uppercase tracking-tight flex items-center gap-1">
                            Linear Decay
                        </p>
                    </div>
                    <div class="p-5 bg-surface-container-low rounded-2xl border border-outline-variant/10 relative overflow-hidden group">
                        <div class="absolute -right-4 -bottom-4 w-16 h-16 bg-primary/5 rounded-full blur-xl transition-all group-hover:scale-150 group-hover:bg-primary/20"></div>
                        <p class="text-[10px] text-on-surface-variant font-extrabold uppercase tracking-widest mb-1.5 line-clamp-1">Step Time</p>
                        <p class="text-2xl font-extrabold text-[#191c1d] transition-all">{trainerState.stepTime}</p>
                        <p class="text-[11px] text-primary font-extrabold mt-1 uppercase tracking-tight flex items-center gap-1">
                            Optimized
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Detailed Monitor Logs & Charts (Bottom Half) -->
    <div class="grid grid-cols-12 gap-6 w-full flex-1">
        
        <!-- Training Log Console -->
        <div class="col-span-12 xl:col-span-7 flex flex-col min-h-[450px]">
            <div class="bg-[#1e1e2d] rounded-3xl overflow-hidden shadow-xl shadow-black/10 border border-outline-variant/20 flex flex-col h-full">
                <!-- Mac-like Header -->
                <div class="bg-[#2d2d3f] px-6 py-4 border-b border-[#414158] flex items-center justify-between shrink-0">
                    <div class="flex items-center gap-4">
                        <div class="flex gap-2">
                            <div class="w-3.5 h-3.5 rounded-full bg-[#ff5f56] border border-[#e0443e]"></div>
                            <div class="w-3.5 h-3.5 rounded-full bg-[#ffbd2e] border border-[#dea123]"></div>
                            <div class="w-3.5 h-3.5 rounded-full bg-[#27c93f] border border-[#1aab29]"></div>
                        </div>
                        <span class="text-xs font-mono text-[#a9b1d6] font-medium tracking-wide">unsloth_daemon_v0.4.log</span>
                    </div>
                    <button class="text-[#a9b1d6] hover:text-white transition-colors bg-[#414158]/50 p-1.5 rounded-lg">
                        <span class="material-symbols-outlined text-[18px]">download</span>
                    </button>
                </div>
                
                <!-- Terminal Output -->
                <div bind:this={logContainer} class="flex-1 overflow-y-auto p-6 font-mono text-[13px] leading-loose custom-scrollbar bg-[#1a1b26] space-y-1.5 shadow-inner">
                    {#each logs as log}
                        <p class="text-[#565f89]"><span class="text-[#7aa2f7] font-bold">LOG</span> {log}</p>
                    {/each}
                    {#if logs.length === 0}
                        <p class="text-slate-500 animate-pulse">Awaiting Unsloth Engine connection...</p>
                    {/if}
                    {#if trainerState.isTraining}
                    <p class="text-slate-200 animate-pulse flex items-center gap-2 mt-4">
                        <span class="text-[#565f89]">[Live]</span> <span class="text-[#7aa2f7] font-bold">SYSTEM</span> Processing
                        <span class="flex gap-1">
                            <span class="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce"></span>
                            <span class="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style="animation-delay: 150ms"></span>
                            <span class="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style="animation-delay: 300ms"></span>
                        </span>
                    </p>
                    {/if}
                </div>
            </div>
        </div>

        <!-- VRAM Chart & Visualization -->
        <div class="col-span-12 xl:col-span-5 flex flex-col min-h-[450px]">
            <div class="bg-surface-container-lowest p-8 rounded-3xl shadow-sm border border-outline-variant/10 h-full flex flex-col">
                <div class="flex items-center justify-between mb-8 shrink-0">
                    <h3 class=" text-on-surface-variant text-[11px] font-extrabold uppercase tracking-widest">VRAM Telemetry</h3>
                    <div class="flex items-center gap-2 bg-primary/5 px-3 py-1.5 rounded-lg border border-primary/10">
                        <span class="w-2.5 h-2.5 rounded-full bg-primary animate-pulse"></span>
                        <span class="text-[10px] font-bold text-primary uppercase tracking-wider">Live Logging</span>
                    </div>
                </div>
                
                <div class="relative flex-1 flex items-end gap-1.5 px-4 bg-surface-container-low rounded-2xl border border-outline-variant/5 mb-8 py-6">
                    <!-- Simple SVG Visualization for VRAM Trend -->
                    <div class="absolute inset-0 flex items-center justify-center opacity-5 pointer-events-none">
                        <span class="material-symbols-outlined text-[150px]">memory</span>
                    </div>
                    
                    <!-- Histogram Bars -->
                    {#each trainerState.vramHistory as val, i}
                        <div class="flex-1 rounded-t-sm transition-all duration-700 relative group"
                             class:bg-primary={trainerState.isTraining}
                             class:opacity-10={!trainerState.isTraining || trainerState.vramHistory.length - 1 !== i}
                             class:opacity-100={trainerState.isTraining && trainerState.vramHistory.length - 1 === i}
                             class:bg-[linear-gradient(to_top,var(--tw-gradient-stops))]={trainerState.isTraining && trainerState.vramHistory.length - 1 === i}
                             class:from-primary={trainerState.isTraining && trainerState.vramHistory.length - 1 === i}
                             class:to-primary-container={trainerState.isTraining && trainerState.vramHistory.length - 1 === i}
                             class:shadow-[0_0_15px_rgba(0,19,96,0.3)]={trainerState.isTraining && trainerState.vramHistory.length - 1 === i}
                             class:bg-primary-container={!trainerState.isTraining}
                             style="height: {Math.max((val / trainerState.vramTotalGb) * 100, 5)}%">
                             {#if trainerState.isTraining && trainerState.vramHistory.length - 1 === i}
                                <div class="absolute -top-10 left-1/2 -translate-x-1/2 bg-inverse-surface text-inverse-on-surface text-[10px] font-bold px-2 py-1.5 rounded-lg whitespace-nowrap shadow-xl opacity-0 transition-opacity group-hover:opacity-100 border border-white/10 z-10 pointer-events-none">Peak {val.toFixed(1)}GB</div>
                                <div class="absolute inset-0 bg-white/20 opacity-0 group-hover:opacity-100 transition-opacity"></div>
                             {/if}
                        </div>
                    {/each}
                    
                    <!-- Baseline Grid -->
                    <div class="absolute bottom-6 left-0 right-0 border-b border-dashed border-outline-variant/40"></div>
                    <div class="absolute bottom-[30%] left-0 right-0 border-b border-dashed border-outline-variant/40"></div>
                    <div class="absolute bottom-[60%] left-0 right-0 border-b border-dashed border-outline-variant/40"></div>
                </div>
                
                <div class="pt-6 border-t border-outline-variant/10 shrink-0">
                    <div class="grid grid-cols-2 gap-6">
                        <div class="flex items-center gap-4 p-4 rounded-xl border border-outline-variant/5 bg-surface-container-lowest">
                            <div class="w-10 h-10 bg-primary/10 rounded-xl flex items-center justify-center text-primary">
                                <span class="material-symbols-outlined text-[20px]">speed</span>
                            </div>
                            <div>
                                <p class="text-[9px] text-on-surface-variant font-extrabold uppercase tracking-widest mb-0.5">Memory BW</p>
                                <p class="text-sm font-bold ">{trainerState.memoryBw}</p>
                            </div>
                        </div>
                        <div class="flex items-center gap-4 p-4 rounded-xl border border-outline-variant/5 bg-surface-container-lowest">
                            <div class="w-10 h-10 bg-[#ba1a1a]/10 rounded-xl flex items-center justify-center text-[#ba1a1a]">
                                <span class="material-symbols-outlined text-[20px]">thermostat</span>
                            </div>
                            <div>
                                <p class="text-[9px] text-on-surface-variant font-extrabold uppercase tracking-widest mb-0.5">Temperature</p>
                                <p class="text-sm font-bold ">{trainerState.temperatureC}°C</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Footer Meta -->
    <footer class="mt-4 pb-8 flex justify-between items-center text-[11px] text-on-surface-variant font-bold uppercase tracking-widest">
        <div class="flex gap-8">
            <span class="flex items-center gap-2"><span class="w-2.5 h-2.5 rounded-full bg-on-tertiary-container shadow-[0_0_8px_rgba(79,175,110,0.6)]"></span> System Online</span>
            <span class="flex items-center gap-2"><span class="w-2.5 h-2.5 rounded-full bg-on-tertiary-container shadow-[0_0_8px_rgba(79,175,110,0.6)]"></span> Unsloth Kernel Active</span>
            <span class="font-mono text-[10px] tracking-normal bg-surface-variant/50 px-2 py-0.5 rounded text-on-surface">Session ID: trainer_7742_ax9</span>
        </div>

    </footer>
</div>

<style>
    .material-symbols-outlined {
        font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
    }
    
    @keyframes progress-stripe {
        0% { background-position: 1rem 0; }
        100% { background-position: 0 0; }
    }
</style>
