<script lang="ts">
    import { page } from '$app/state';
    import { goto } from '$app/navigation';
    import { onMount, onDestroy } from 'svelte';
    import { trainerState, exportTrainerConfig } from '$lib/trainer.svelte';

    let isSubmitting = $state(false);
    let pollingInterval: any;

    onMount(() => {
        fetchTrainerStats();
        pollingInterval = setInterval(fetchTrainerStats, 10000);
        return () => clearInterval(pollingInterval);
    });

    async function fetchTrainerStats() {
        try {
            const res = await fetch('http://localhost:38001/v1/trainer/stats');
            if (res.ok) {
                const data = await res.json();
                trainerState.knowledgeGapPercentage = data.knowledge_gap_percentage || 0;
                trainerState.sourcesScanned = data.sources_scanned || 0;
                trainerState.sourcesScannedDelta = data.sources_scanned_delta || 0;
                if (data.recently_acquired) {
                    trainerState.recentlyAcquiredKnowledge = data.recently_acquired;
                }
                
                // Telemetry
                trainerState.isTraining = data.unsloth?.is_training || false;
                if(data.unsloth) {
                    trainerState.vramUsageGb = data.unsloth.vram_usage_gb || 0;
                    trainerState.epochCurrent = data.unsloth.epoch_current || 0;
                    trainerState.epochTotal = data.unsloth.epoch_total || 5;
                    trainerState.trainingSpeedTokensSec = data.unsloth.tokens_per_sec || 0;
                    trainerState.lastCheckpoint = data.unsloth.last_checkpoint || 'Idle';
                }
            }
        } catch(e) {
            console.error("Failed to fetch Live Trainer Telemetry from Axum:", e);
        }
    }

    async function sendUnslothControl(action: 'play' | 'pause' | 'stop') {
        try {
            await fetch('http://localhost:38001/v1/trainer/control', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action })
            });
            await fetchTrainerStats(); // Force refresh UI
        } catch(e) {
            console.error(`Unsloth RPC failed: ${action}`, e);
        }
    }

    async function runFineTuning() {
        if(isSubmitting) return;
        isSubmitting = true;
        try {
            await fetch('http://localhost:38001/v1/trainer/finetune', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    base_model: 'Llama-3-8B-Instruct-v0.1',
                    dataset_name: 'sovereign-hq-rag-dataset-v1',
                    learning_rate: trainerState.learningRate,
                    lora_rank: trainerState.loraRank,
                    batch_size: trainerState.batchSize,
                    internet_to_rag: trainerState.internetToRagActive,
                    strict_grounding: trainerState.strictGrounding,
                    top_k: trainerState.contextDepthTopK
                })
            });
            goto('/model-trainer/unsloth');
        } catch(e) {
            console.error(e);
            isSubmitting = false;
        }
    }
</script>

<div class="p-8 h-full">
    <!-- Header Section (Identical to Distillation) -->
    <header class="mb-10 w-full flex items-center justify-between">
        <div class="flex items-center gap-4 bg-surface-container-low px-4 py-2 rounded-full w-96 border border-outline-variant/10 shadow-sm">
            <span class="material-symbols-outlined text-on-surface-variant text-[20px]">search</span>
            <input class="bg-transparent border-none focus:ring-0 text-sm w-full placeholder:text-on-surface-variant/70 text-on-surface outline-none" placeholder="Search experiments or datasets..." type="text" />
        </div>
        <div class="flex items-center gap-4 bg-surface-container-low p-1.5 rounded-xl border border-outline-variant/10">
            <button class="px-4 py-2 bg-surface-container-lowest text-primary font-bold text-xs rounded-lg shadow-sm">Fine-Tuning</button>
            <a href="/model-trainer/distillation" class="px-4 py-2 text-on-surface-variant font-medium text-xs rounded-lg hover:bg-surface-container-high transition-colors">Distillation</a>
            <a href="/model-trainer/reflection" class="px-4 py-2 text-on-surface-variant font-medium text-xs rounded-lg hover:bg-surface-container-high transition-colors">Reflection Lab</a>
            <a href="/model-trainer/rag-pipeline" class="px-4 py-2 text-on-surface-variant font-medium text-xs rounded-lg hover:bg-surface-container-high transition-colors">RAG Pipeline</a>
            <a href="/model-trainer/unsloth" class="px-4 py-2 text-on-surface-variant font-medium text-xs rounded-lg hover:bg-surface-container-high transition-colors">Unsloth Monitor</a>
        </div>
    </header>

    <div class="w-full flex-1">
        <!-- Title Section -->
        <section class="flex justify-between items-end mb-10">
            <div>
                <p class="text-primary font-semibold text-sm tracking-wide mb-1 uppercase">Model Trainer</p>
                <h1 class="font-extrabold text-3xl tracking-tight text-on-surface">Fine-Tuning Engine</h1>
            </div>
            <div class="flex gap-3">
                <button onclick={exportTrainerConfig} class="px-5 py-2.5 rounded-xl border border-outline-variant/30 text-on-surface-variant font-bold text-xs hover:bg-surface-container-high transition-colors cursor-pointer active:scale-95">
                    Export Configuration
                </button>
                <button disabled={isSubmitting} onclick={runFineTuning} class="px-5 py-2.5 rounded-xl bg-gradient-to-br from-[#001360] to-[#002395] text-white font-bold text-xs shadow-md shadow-primary/20 active:scale-95 transition-transform flex items-center gap-2 cursor-pointer disabled:opacity-50">
                    <span class="material-symbols-outlined text-[18px]">play_arrow</span>
                    {isSubmitting ? 'Iniciando...' : 'Start Fine-Tuning'}
                </button>
            </div>
        </section>

    <!-- Grid Layout -->
    <div class="grid grid-cols-1 xl:grid-cols-12 gap-8 items-start">
        
        <!-- Section 1 & 2: Main Left Column -->
        <div class="xl:col-span-7 space-y-8">
            
            <!-- Deep Research Agent WAG Section -->
            <section class="bg-surface-container-lowest rounded-3xl p-8 relative overflow-hidden border border-outline-variant/10 shadow-sm">
                <div class="flex justify-between items-start relative z-10 mb-10">
                    <div class="flex gap-4">
                        <div class="w-12 h-12 rounded-xl bg-primary-fixed flex items-center justify-center">
                            <span class="material-symbols-outlined text-primary text-[24px]">travel_explore</span>
                        </div>
                        <div>
                            <h2 class="text-xl font-bold text-on-surface ">Deep Research Agent</h2>
                            <div class="flex items-center gap-2 mt-1">
                                <span class="w-2 h-2 rounded-full bg-on-tertiary-container shadow-[0_0_8px_rgba(79,175,110,0.6)]"></span>
                                <p class="text-xs text-on-surface-variant font-medium">Status: Web-Augmented Generation (WAG) Active</p>
                            </div>
                        </div>
                    </div>
                    <div class="flex items-center gap-3 px-4 py-2 bg-surface-container-low rounded-xl">
                        <span class="text-[10px] font-bold text-on-surface-variant uppercase tracking-tighter">Internet-to-RAG</span>
                        <button onclick={() => trainerState.internetToRagActive = !trainerState.internetToRagActive} class="w-10 h-5 {trainerState.internetToRagActive ? 'bg-primary' : 'bg-surface-variant'} rounded-full relative transition-colors cursor-pointer">
                            <div class="absolute top-1 w-3 h-3 bg-white rounded-full transition-all {trainerState.internetToRagActive ? 'right-1' : 'left-1'}"></div>
                        </button>
                    </div>
                </div>

                <div class="grid grid-cols-3 gap-4 mb-8">
                    <div class="p-4 bg-surface-container-low rounded-xl">
                        <p class="text-[10px] text-on-surface-variant font-bold uppercase mb-2">Knowledge Gap</p>
                        <p class="text-lg font-bold text-on-surface">{trainerState.knowledgeGapPercentage.toFixed(1)}%</p>
                        <div class="w-full h-1 bg-surface-container-highest mt-3 rounded-full overflow-hidden">
                            <div class="h-full bg-primary transition-all duration-500" style="width: {trainerState.knowledgeGapPercentage}%"></div>
                        </div>
                    </div>
                    <div class="p-4 bg-surface-container-low rounded-xl">
                        <p class="text-[10px] text-on-surface-variant font-bold uppercase mb-2">Sources Scanned</p>
                        <p class="text-lg font-bold text-on-surface">{trainerState.sourcesScanned.toLocaleString()}</p>
                        <p class="text-[10px] text-on-tertiary-container font-bold mt-1">+{trainerState.sourcesScannedDelta} in last hour</p>
                    </div>
                    <div class="p-4 bg-surface-container-low rounded-xl">
                        <p class="text-[10px] text-on-surface-variant font-bold uppercase mb-2">Vault Sync</p>
                        <p class="text-lg font-bold text-on-surface">Encrypted</p>
                        <span class="text-[10px] {trainerState.sourcesScanned > 0 ? 'bg-tertiary-fixed text-on-tertiary-fixed' : 'bg-surface-variant text-on-surface-variant'} px-2 py-0.5 rounded-full mt-2 font-bold inline-block">{trainerState.sourcesScanned > 0 ? 'Verified' : 'Idle'}</span>
                    </div>
                </div>

                <div>
                    <h3 class="text-sm font-bold text-on-surface mb-4 ">Recently Acquired Knowledge</h3>
                    <div class="space-y-3">
                        {#if trainerState.recentlyAcquiredKnowledge.length === 0}
                            <div class="text-xs text-on-surface-variant font-medium text-center py-4 bg-surface-container-lowest rounded-lg border border-outline-variant/10">No recent Vault injections documented in the system yet.</div>
                        {/if}
                        {#each trainerState.recentlyAcquiredKnowledge as item}
                            <div class="flex items-center justify-between p-3 bg-surface hover:bg-surface-container-high rounded-lg transition-colors group cursor-pointer border border-transparent hover:border-outline-variant/20">
                                <div class="flex items-center gap-3">
                                    <span class="material-symbols-outlined text-on-surface-variant group-hover:text-primary transition-colors text-[20px]">{item.type === 'description' ? 'description' : 'article'}</span>
                                    <span class="text-xs font-medium text-on-surface">{item.title}</span>
                                </div>
                                <span class="text-[10px] text-on-surface-variant font-medium">{item.timeAgo}</span>
                            </div>
                        {/each}
                    </div>
                </div>
            </section>

            <!-- Unsloth Monitor Mini Section -->
            <section class="bg-surface-container-lowest rounded-3xl p-8 border border-outline-variant/10 shadow-sm">
                <div class="flex justify-between items-center mb-8">
                    <div class="flex items-center gap-4">
                        <div class="w-10 h-10 rounded-xl bg-tertiary-fixed-dim flex items-center justify-center">
                            <span class="material-symbols-outlined text-tertiary text-[20px]">terminal</span>
                        </div>
                        <h2 class="text-xl font-bold text-on-surface ">Unsloth Monitor <span class="text-on-surface-variant font-medium text-sm ml-2">3B/8B Optimizations</span></h2>
                    </div>
                    <div class="flex gap-2 bg-surface-container-low p-1 rounded-lg">
                        <button class="px-3 py-1 bg-surface-container-lowest shadow-sm rounded-md text-[10px] font-bold text-on-surface">Local</button>
                        <button class="px-3 py-1 text-on-surface-variant rounded-md text-[10px] font-bold">Remote</button>
                    </div>
                </div>

                <div class="grid grid-cols-2 gap-8 mb-8">
                    <div class="space-y-4">
                        <div class="flex justify-between items-end">
                            <p class="text-xs font-bold text-on-surface-variant uppercase tracking-widest">VRAM Usage</p>
                            <p class="text-lg font-bold font-mono text-on-surface">{trainerState.vramUsageGb.toFixed(1)} GB <span class="text-xs font-medium text-on-surface-variant">/ {trainerState.vramTotalGb} GB</span></p>
                        </div>
                        <div class="h-10 w-full bg-surface-container-high rounded-lg overflow-hidden flex gap-1 p-1">
                            <div class="h-full bg-primary rounded-md transition-all duration-1000" style="width: {Math.min(100, (trainerState.vramUsageGb / trainerState.vramTotalGb) * 100)}%"></div>
                            <div class="h-full bg-surface-variant rounded-md flex-1"></div>
                        </div>
                    </div>
                    <div class="space-y-4">
                        <div class="flex justify-between items-end">
                            <p class="text-xs font-bold text-on-surface-variant uppercase tracking-widest">Epoch Progress</p>
                            <p class="text-lg font-bold font-mono text-on-surface">{trainerState.epochCurrent} / {trainerState.epochTotal} <span class="text-xs font-medium text-on-surface-variant">({trainerState.epochTotal > 0 ? Math.round((trainerState.epochCurrent / trainerState.epochTotal) * 100) : 0}%)</span></p>
                        </div>
                        <div class="h-10 w-full bg-surface-container-high rounded-lg overflow-hidden p-1">
                            <div class="h-full bg-gradient-to-r from-primary to-primary-container rounded-md relative transition-all duration-1000" style="width: {trainerState.epochTotal > 0 ? (trainerState.epochCurrent / trainerState.epochTotal) * 100 : 0}%">
                                {#if trainerState.isTraining}
                                <div class="absolute inset-0 bg-white/10 flex items-center justify-end px-2">
                                    <div class="w-1 h-4 bg-white/40 rounded-full animate-pulse"></div>
                                </div>
                                {/if}
                            </div>
                        </div>
                    </div>
                </div>

                <div class="flex items-center gap-4 bg-surface-container-low p-4 rounded-xl border border-outline-variant/10">
                    <div class="flex gap-2 shrink-0">
                        <button onclick={() => sendUnslothControl('play')} class="w-10 h-10 rounded-full {trainerState.isTraining ? 'bg-primary text-white shadow-md shadow-primary/20 hover:scale-105' : 'bg-surface-container-lowest text-on-surface-variant border border-outline-variant/30 hover:bg-primary hover:text-white'} flex items-center justify-center transition-all active:scale-95 cursor-pointer">
                            <span class="material-symbols-outlined text-[20px]" style={trainerState.isTraining ? "font-variation-settings: 'FILL' 1;" : ""}>play_arrow</span>
                        </button>
                        <button onclick={() => sendUnslothControl('pause')} class="w-10 h-10 rounded-full {!trainerState.isTraining && trainerState.epochCurrent > 0 ? 'bg-surface-variant text-on-surface shadow-inner' : 'bg-surface-container-lowest text-on-surface-variant border border-outline-variant/30 hover:bg-surface-container-high'} flex items-center justify-center transition-colors cursor-pointer">
                            <span class="material-symbols-outlined text-[20px]">pause</span>
                        </button>
                        <button onclick={() => sendUnslothControl('stop')} class="w-10 h-10 rounded-full bg-surface-container-lowest text-error border border-error/20 flex items-center justify-center hover:bg-error-container hover:text-error transition-colors cursor-pointer">
                            <span class="material-symbols-outlined text-[20px]">stop</span>
                        </button>
                    </div>
                    <div class="h-8 w-[1px] bg-outline-variant/30 mx-2"></div>
                    <div class="flex-1 font-mono text-[11px] text-on-surface-variant leading-relaxed">
                        <p>[SYSTEM] {trainerState.lastCheckpoint}</p>
                        {#if trainerState.isTraining}
                            <p class="text-on-tertiary-container font-medium animate-pulse">[INFO] Training speed: {trainerState.trainingSpeedTokensSec.toFixed(1)} tokens/sec</p>
                        {:else}
                            <p class="text-on-surface-variant/50 font-medium">[INFO] Engine Sleeping...</p>
                        {/if}
                    </div>
                    <a href="/model-trainer/unsloth" class="p-2 text-on-surface-variant hover:bg-surface-container-high rounded-lg transition-colors ml-auto tooltip" title="Open Full Monitor">
                        <span class="material-symbols-outlined text-[20px]">open_in_new</span>
                    </a>
                </div>
            </section>
        </div>

        <!-- Section 3: Right Sidebar Column -->
        <div class="xl:col-span-5 space-y-8">
            
            <!-- Alignment Metrics -->
            <!-- Unsloth Native Configuration -->
            <section class="bg-surface-container-lowest rounded-3xl p-8 border border-outline-variant/10 shadow-sm">
                <div class="flex items-center gap-3 mb-8">
                    <span class="material-symbols-outlined text-secondary text-[24px]">memory</span>
                    <h2 class="text-sm font-bold text-on-surface uppercase tracking-widest ">Unsloth LoRA Engine</h2>
                </div>
                
                <div class="space-y-8">
                    <div>
                        <div class="flex justify-between items-center mb-3">
                            <span class="text-xs font-bold text-on-surface-variant uppercase tracking-widest">LoRA Rank (r)</span>
                            <span class="px-2 py-1 bg-primary/10 text-primary font-extrabold text-xs rounded-lg">{trainerState.loraRank}</span>
                        </div>
                        <input type="range" class="w-full accent-primary h-1.5 bg-surface-variant rounded-full appearance-none outline-none" min="8" max="128" step="8" bind:value={trainerState.loraRank} />
                        <div class="flex justify-between text-[10px] text-on-surface-variant mt-2 font-mono">
                            <span>r=8 (Fast)</span>
                            <span>r=128 (Detailed)</span>
                        </div>
                    </div>

                    <div class="w-full h-[1px] bg-outline-variant/20"></div>

                    <div>
                        <div class="flex justify-between items-center mb-3">
                            <span class="text-xs font-bold text-on-surface-variant uppercase tracking-widest">Batch Size</span>
                            <span class="px-2 py-1 bg-secondary/10 text-secondary font-extrabold text-xs rounded-lg">{trainerState.batchSize}</span>
                        </div>
                        <input type="range" class="w-full accent-secondary h-1.5 bg-surface-variant rounded-full appearance-none outline-none" min="1" max="32" step="1" bind:value={trainerState.batchSize} />
                        <div class="flex justify-between text-[10px] text-on-surface-variant mt-2 font-mono">
                            <span>1 (Slow / Precise)</span>
                            <span>32 (High VRAM)</span>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Perfection Controls & Reflection Lab -->
            <section class="bg-surface-container-lowest rounded-3xl p-8 border border-outline-variant/10 shadow-sm">
                <h2 class="text-sm font-bold text-on-surface uppercase tracking-widest mb-6 ">Perfection Controls</h2>
                
                <div class="space-y-8">
                    <!-- Hallucination Switch -->
                    <div class="flex items-center justify-between p-4 bg-surface-container-low rounded-xl border border-outline-variant/10">
                        <div class="flex items-center gap-3">
                            <div class="w-10 h-10 rounded-xl bg-error-container/40 flex items-center justify-center text-error">
                                <span class="material-symbols-outlined text-[20px]">security</span>
                            </div>
                            <div>
                                <p class="text-xs font-bold text-on-surface">Strict Grounding AI</p>
                                <p class="text-[10px] text-on-surface-variant mt-0.5">Force factual matching in RAG</p>
                            </div>
                        </div>
                        <button onclick={() => trainerState.strictGrounding = !trainerState.strictGrounding} title="Toggle Strict Grounding AI" class="w-12 h-6 {trainerState.strictGrounding ? 'bg-primary ring-4 ring-primary-fixed' : 'bg-surface-variant'} rounded-full relative cursor-pointer transition-colors">
                            <div class="absolute top-1.5 w-3 h-3 bg-white rounded-full shadow-sm transition-all {trainerState.strictGrounding ? 'right-1' : 'left-1'}"></div>
                        </button>
                    </div>
                    
                    <!-- Sliders -->
                    <div class="space-y-6 px-1">
                        <div class="space-y-3">
                            <div class="flex justify-between text-[10px] font-bold uppercase tracking-widest">
                                <span class="text-on-surface-variant">Embedding Alignment</span>
                                <span class="text-primary font-mono bg-primary-fixed/50 px-2 py-0.5 rounded text-[10px]">{trainerState.embeddingAlignmentAlpha / 100} Alpha</span>
                            </div>
                            <input class="w-full h-1.5 bg-surface-variant rounded-full appearance-none accent-primary cursor-pointer hover:accent-primary-container transition-colors" type="range" min="0" max="100" bind:value={trainerState.embeddingAlignmentAlpha} />
                        </div>
                        
                        <div class="space-y-3">
                            <div class="flex justify-between text-[10px] font-bold uppercase tracking-widest">
                                <span class="text-on-surface-variant">Context Depth (Top-K)</span>
                                <span class="text-primary font-mono bg-primary-fixed/50 px-2 py-0.5 rounded text-[10px]">k = {trainerState.contextDepthTopK}</span>
                            </div>
                            <input class="w-full h-1.5 bg-surface-variant rounded-full appearance-none accent-primary cursor-pointer hover:accent-primary-container transition-colors" type="range" min="1" max="128" bind:value={trainerState.contextDepthTopK} />
                        </div>
                    </div>
                </div>

                <!-- Reflection Lab Mini -->
                <div class="mt-8 pt-6 border-t border-outline-variant/20">
                    <h3 class="text-xs font-bold text-on-surface mb-4 uppercase tracking-widest ">Reflection Lab</h3>
                    <div class="bg-surface p-5 rounded-2xl mb-4 border border-outline-variant/10">
                        <div class="flex justify-between items-center mb-6">
                            <div class="flex items-center gap-2">
                                <span class="material-symbols-outlined text-[16px] text-on-surface-variant">psychology</span>
                                <p class="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest">Internal Monologue</p>
                            </div>
                            <button onclick={() => trainerState.internalMonologue = !trainerState.internalMonologue} title="Toggle Internal Monologue" class="w-8 h-4 {trainerState.internalMonologue ? 'bg-tertiary shadow-[0_0_8px_rgba(79,175,110,0.4)]' : 'bg-outline-variant'} rounded-full relative cursor-pointer transition-colors">
                                <div class="absolute top-0.5 w-3 h-3 bg-white rounded-full transition-all {trainerState.internalMonologue ? 'right-1' : 'left-1'}"></div>
                            </button>
                        </div>
                        
                        <div class="flex items-end justify-between">
                            <div>
                                <!-- Use inverse gap to simulate truth grounded reflection success rate -->
                                <p class="text-3xl font-extrabold text-on-tertiary-container leading-none ">{Math.max(0, 100 - trainerState.knowledgeGapPercentage).toFixed(1)}%</p>
                                <p class="text-[10px] text-on-surface-variant font-bold mt-2 uppercase tracking-tight">Self-Correction Rate</p>
                            </div>
                            
                            <!-- Mini Bar Chart -->
                            <div class="flex items-end gap-1.5 h-12">
                                <div class="w-2 h-4 bg-tertiary-fixed-dim rounded-t-sm hover:h-6 transition-all duration-300"></div>
                                <div class="w-2 h-7 bg-tertiary-fixed-dim rounded-t-sm hover:h-8 transition-all duration-300"></div>
                                <div class="w-2 h-10 bg-tertiary-fixed-dim rounded-t-sm hover:h-11 transition-all duration-300"></div>
                                <div class="w-2 h-8 bg-tertiary-fixed-dim rounded-t-sm hover:h-9 transition-all duration-300"></div>
                                <div class="w-2 h-12 bg-on-tertiary-container rounded-t-sm shadow-[0_0_8px_rgba(79,175,110,0.4)]"></div>
                            </div>
                        </div>
                    </div>
                    
                    <a href="/model-trainer/reflection" class="block w-full py-3 bg-surface-container-high text-on-surface-variant text-[11px] font-bold rounded-xl hover:bg-surface-container-highest transition-colors uppercase tracking-widest text-center border border-outline-variant/10">
                        Visualize Reasoning Chain
                    </a>
                </div>
            </section>
        </div>
    </div>
</div>

<style>
    .material-symbols-outlined {
        font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
    }
    
    input[type=range] {
        -webkit-appearance: none;
        appearance: none;
        width: 100%;
        background: transparent;
    }
    input[type=range]::-webkit-slider-thumb {
        -webkit-appearance: none;
        appearance: none;
        height: 18px;
        width: 18px;
        border-radius: 50%;
        background: var(--color-primary);
        cursor: pointer;
        margin-top: -6px;
        box-shadow: 0 0 10px rgba(0, 19, 96, 0.3);
    }
    input[type=range]::-moz-range-track {
        width: 100%;
        height: 6px;
        cursor: pointer;
        background: var(--color-surface-variant);
        border-radius: 3px;
    }
    input[type=range]::-webkit-slider-thumb:hover {
        background: var(--color-primary-container);
        transform: scale(1.1);
    }
    input[type=range]::-webkit-slider-runnable-track {
        width: 100%;
        height: 6px;
        cursor: pointer;
        background: var(--color-surface-variant);
        border-radius: 3px;
    }
</style>
    </div>
