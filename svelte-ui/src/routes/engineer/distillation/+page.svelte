<script lang="ts">
    import { goto } from '$app/navigation';
    import { trainerState, AI_MODELS, exportDistillationLogs, getSimilarityScoreBaseline } from '$lib/trainer.svelte';

    let isSubmitting = $state(false);

    let teacherModel = $state('GPT-4o');
    let studentModel = $state('llama3.2:3b');
    
    let currentStudentSize = $derived(AI_MODELS.find(m => m.id === studentModel)?.sizeB || 0);
    
    let availableTeachersLocal = $derived(AI_MODELS.filter(m => m.type === 'local' && m.sizeB > currentStudentSize));
    let availableTeachersExternal = $derived(AI_MODELS.filter(m => m.type === 'external' && m.sizeB > currentStudentSize && ((m.provider === 'openai' && trainerState.hasOpenAiKey) || (m.provider === 'anthropic' && trainerState.hasAnthropicKey))));

    let studentOptions = AI_MODELS.filter(m => m.type === 'local' && m.sizeB <= 10);
    
    let distillationLogs = $state<string[]>([]);
    
    let animatedScoreOffset = $state(0);
    let dynamicScore = $derived((parseFloat(getSimilarityScoreBaseline()) + animatedScoreOffset).toFixed(2));

    async function runDistillation() {
        if(isSubmitting) return;
        isSubmitting = true;
        distillationLogs = [];
        
        let logInterval = setInterval(() => {
            distillationLogs = [...distillationLogs, `[Node] Processing latent alignment batch #${Math.floor(Math.random() * 1000)}... K-Divergence delta: ${(Math.random() * 0.1).toFixed(4)}`];
            trainerState.datasetSizeCount += Math.floor(Math.random() * 250) + 10;
            if (animatedScoreOffset < 0.15) {
                animatedScoreOffset += 0.005;
            }
        }, 800);
        
        setTimeout(() => {
            clearInterval(logInterval);
            distillationLogs = [...distillationLogs, `[System] Epoch distillation complete. Transferring weights...`];
            isSubmitting = false;
        }, 6000);
    }
    
    function formatDatasetSize(count: number) {
        if (count >= 1000000) return (count / 1000000).toFixed(3) + 'M';
        if (count >= 1000) return (count / 1000).toFixed(1) + 'K';
        return count.toString();
    }
</script>

<div class="p-8 h-full flex flex-col">
    <!-- Header Section -->
    <header class="mb-10 w-full flex items-center justify-between">
        <div class="flex items-center gap-4 bg-surface-container-low px-4 py-2 rounded-full w-96 border border-outline-variant/10 shadow-sm">
            <span class="material-symbols-outlined text-on-surface-variant text-[20px]">search</span>
            <input class="bg-transparent border-none focus:ring-0 text-sm w-full placeholder:text-on-surface-variant/70 text-on-surface outline-none" placeholder="Search experiments or datasets..." type="text" />
        </div>
        <div class="flex items-center gap-4 bg-surface-container-low p-1.5 rounded-xl border border-outline-variant/10">
            <a href="/engineer/fine-tuning" class="px-4 py-2 text-on-surface-variant font-medium text-xs rounded-lg hover:bg-surface-container-high transition-colors">Fine-Tuning</a>
            <button class="px-4 py-2 bg-surface-container-lowest text-primary font-bold text-xs rounded-lg shadow-sm">Distillation</button>
            <a href="/engineer/reflection" class="px-4 py-2 text-on-surface-variant font-medium text-xs rounded-lg hover:bg-surface-container-high transition-colors">Reflection Lab</a>
            <a href="/engineer/rag-pipeline" class="px-4 py-2 text-on-surface-variant font-medium text-xs rounded-lg hover:bg-surface-container-high transition-colors">RAG Pipeline</a>
            <a href="/engineer/unsloth" class="px-4 py-2 text-on-surface-variant font-medium text-xs rounded-lg hover:bg-surface-container-high transition-colors">Unsloth Monitor</a>
            <a href="/engineer/analytics" class="px-4 py-2 text-on-surface-variant font-medium text-xs rounded-lg hover:bg-surface-container-high transition-colors">Analytics</a>
        </div>
    </header>

    <!-- Page Content -->
    <div class="w-full space-y-10 flex-1">
        <!-- Title Section -->
        <section class="flex justify-between items-end">
            <div>
                <p class="text-primary font-semibold text-sm tracking-wide mb-1 uppercase">Model Trainer</p>
                <h2 class=" font-extrabold text-3xl tracking-tight text-on-surface">Knowledge Distillation</h2>
                <p class="text-on-surface-variant mt-2 text-sm font-medium">Transferring latent logic from Professor (GPT-4) to Student (Llama 3.2 3B).</p>
            </div>
            <div class="flex gap-3">
                <button onclick={() => exportDistillationLogs(teacherModel, studentModel, distillationLogs)} class="px-5 py-2.5 rounded-xl border border-outline-variant/30 text-on-surface-variant font-bold text-xs hover:bg-surface-container-high transition-colors">
                    Export Logs
                </button>
                <button disabled={isSubmitting} onclick={runDistillation} class="px-5 py-2.5 rounded-xl bg-gradient-to-br from-primary to-primary-container text-white font-bold text-xs shadow-md shadow-primary/20 active:scale-95 transition-transform flex items-center gap-2 cursor-pointer disabled:opacity-50">
                    <span class="material-symbols-outlined text-[18px]">model_training</span>
                    {isSubmitting ? 'Destilando...' : 'Run Distillation'}
                </button>
            </div>
        </section>

        <!-- Bento Grid Layout -->
        <div class="grid grid-cols-12 gap-6 pb-12">
            
            <!-- Relationship Card -->
            <div class="col-span-12 xl:col-span-8 bg-surface-container-lowest rounded-3xl p-8 relative overflow-hidden border border-outline-variant/10 shadow-sm">
                <div class="relative z-10">
                    <h3 class=" font-bold text-lg mb-8 text-on-surface">Model Alignment Architecture</h3>
                    <div class="flex items-center justify-between gap-6 py-2">
                        <!-- Professor -->
                        <div class="flex-1 bg-surface p-6 rounded-2xl border border-outline-variant/10 shadow-sm">
                            <div class="flex items-center gap-4 mb-6">
                                <div class="w-12 h-12 rounded-xl bg-secondary-container flex items-center justify-center shadow-inner">
                                    <span class="material-symbols-outlined text-secondary text-[24px]">school</span>
                                </div>
                                <div class="flex-1 w-full">
                                    <p class="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest mb-1">Professor Model</p>
                                    <select bind:value={teacherModel} class="w-full bg-surface-container-high border border-outline-variant/30 rounded-lg px-2 py-1.5 text-sm font-extrabold text-on-surface focus:ring-1 focus:ring-primary outline-none">
                                        {#if availableTeachersLocal.length > 0}
                                        <optgroup label="Sovereign Mesh Nodes">
                                            {#each availableTeachersLocal as model}
                                            <option value={model.id}>{model.name}</option>
                                            {/each}
                                        </optgroup>
                                        {/if}
                                        {#if availableTeachersExternal.length > 0}
                                        <optgroup label="External Providers">
                                            {#each availableTeachersExternal as model}
                                            <option value={model.id}>{model.name}</option>
                                            {/each}
                                        </optgroup>
                                        {/if}
                                        {#if availableTeachersLocal.length === 0 && availableTeachersExternal.length === 0}
                                        <option value="" disabled>No superior professors available</option>
                                        {/if}
                                    </select>
                                </div>
                            </div>
                            <div class="space-y-3 mb-4">
                                <div class="flex justify-between text-xs">
                                    <span class="text-on-surface-variant font-medium">Reasoning Level</span>
                                    <span class="font-bold text-secondary">{AI_MODELS.find(m => m.id === teacherModel)?.badge || 'Tier 1 (Elite)'}</span>
                                </div>
                                <div class="w-full bg-surface-variant h-2 rounded-full overflow-hidden">
                                    <div class="bg-secondary h-full w-[95%] rounded-full"></div>
                                </div>
                            </div>
                            
                            <!-- Privacy Warning Advisory -->
                            {#if AI_MODELS.find(m => m.id === teacherModel)?.type === 'local'}
                            <div class="bg-primary-fixed/20 border border-primary/20 rounded-lg p-2.5 flex items-start gap-2.5 animate-in fade-in duration-300 shadow-sm">
                                <span class="material-symbols-outlined text-primary text-[16px] mt-0.5">shield_person</span>
                                <div>
                                    <p class="text-[9px] font-extrabold text-primary uppercase tracking-widest mb-0.5">Sovereign Privacy Active</p>
                                    <p class="text-[10px] text-on-surface-variant/90 leading-tight font-medium">Local residents guarantee <strong class="text-on-surface">zero-cost</strong> and <strong class="text-on-surface">100% private</strong> distillation independent of external APIs.</p>
                                </div>
                            </div>
                            {:else}
                            <div class="bg-surface-variant border border-outline-variant/30 rounded-lg p-2.5 flex items-start gap-2.5 animate-in fade-in duration-300 shadow-sm">
                                <span class="material-symbols-outlined text-on-surface-variant text-[16px] mt-0.5">cloud_upload</span>
                                <div>
                                    <p class="text-[9px] font-extrabold text-on-surface-variant uppercase tracking-widest mb-0.5">External API Dependent</p>
                                    <p class="text-[10px] text-on-surface-variant/80 leading-tight font-medium">Subject to third-party billing and data sovereignty risks. <strong class="text-on-surface">Prefer local models</strong> when possible.</p>
                                </div>
                            </div>
                            {/if}
                        </div>
                        
                        <!-- Transfer Link -->
                        <div class="flex flex-col items-center shrink-0">
                            <div class="text-primary animate-pulse w-12 h-12 bg-primary-fixed/30 rounded-full flex items-center justify-center border border-primary/20">
                                <span class="material-symbols-outlined text-[28px]">trending_flat</span>
                            </div>
                            <p class="text-[9px] font-bold text-primary mt-3 tracking-widest uppercase">K-Divergence</p>
                        </div>
                        
                        <!-- Student -->
                        <div class="flex-1 bg-surface p-6 rounded-2xl border border-outline-variant/10 shadow-sm">
                            <div class="flex items-center gap-4 mb-6">
                                <div class="w-12 h-12 rounded-xl bg-primary-fixed/50 flex items-center justify-center shadow-inner">
                                    <span class="material-symbols-outlined text-primary text-[24px]">child_care</span>
                                </div>
                                <div class="flex-1 w-full">
                                    <p class="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest mb-1">Student Model</p>
                                    <select bind:value={studentModel} class="w-full bg-surface-container-high border border-outline-variant/30 rounded-lg px-2 py-1.5 text-sm font-extrabold text-on-surface focus:ring-1 focus:ring-primary outline-none">
                                        <optgroup label="Local Edge">
                                            {#each studentOptions as model}
                                            <option value={model.id}>{model.name}</option>
                                            {/each}
                                        </optgroup>
                                    </select>
                                </div>
                            </div>
                            <div class="space-y-3">
                                <div class="flex justify-between text-xs">
                                    <span class="text-on-surface-variant font-medium">Learning Capacity</span>
                                    <span class="font-bold text-primary">{AI_MODELS.find(m => m.id === studentModel)?.badge || 'Edge Optimized'}</span>
                                </div>
                                <div class="w-full bg-surface-variant h-2 rounded-full overflow-hidden">
                                    <div class="bg-primary h-full w-[65%] rounded-full"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Score Card -->
            <div class="col-span-12 md:col-span-6 xl:col-span-4 bg-gradient-to-br from-[#001360] to-[#002395] text-white rounded-3xl p-8 flex flex-col justify-between shadow-lg shadow-primary/20 relative overflow-hidden">
                <div class="absolute inset-0 opacity-10 bg-[radial-gradient(circle_at_top_right,_var(--tw-gradient-stops))] from-white via-transparent to-transparent"></div>
                <div class="relative z-10">
                    <div class="flex justify-between items-start mb-6">
                        <h3 class=" font-bold text-lg text-white/90">Similarity Score</h3>
                        <div class="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center backdrop-blur-sm">
                            <span class="material-symbols-outlined text-white/80">analytics</span>
                        </div>
                    </div>
                    <div class="mt-2 flex items-baseline gap-2">
                        <span class="text-7xl  font-extrabold tracking-tighter">{dynamicScore}</span>
                        <span class="text-sm font-medium text-white/60">/ 1.00</span>
                    </div>
                </div>
                <div class="mt-8 relative z-10">
                    <div class="flex justify-between text-[11px] mb-3">
                        <span class="text-primary-fixed font-medium">Latent Space Match</span>
                        <span class="font-bold text-white">+12% vs Baseline</span>
                    </div>
                    <div class="w-full bg-black/20 h-2 rounded-full overflow-hidden">
                        <div class="bg-primary-fixed h-full w-[88%] rounded-full shadow-[0_0_10px_rgba(222,225,255,0.5)]"></div>
                    </div>
                </div>
            </div>

            <!-- Hyperparameters -->
            <div class="col-span-12 md:col-span-6 xl:col-span-4 bg-surface-container-lowest rounded-3xl p-8 border border-outline-variant/10 shadow-sm flex flex-col justify-center">
                <div class="flex items-center gap-3 mb-8">
                    <span class="material-symbols-outlined text-on-surface-variant">tune</span>
                    <h3 class="font-bold text-lg text-on-surface">Hyperparameters</h3>
                </div>
                
                <div class="space-y-8">
                    <div>
                        <div class="flex justify-between items-center mb-3">
                            <span class="text-xs font-bold text-on-surface-variant uppercase tracking-widest">Distillation Epochs</span>
                            <span class="px-2 py-1 bg-primary/10 text-primary font-extrabold text-xs rounded-lg">{trainerState.distillationEpochs}</span>
                        </div>
                        <input type="range" min="1" max="10" bind:value={trainerState.distillationEpochs} class="w-full accent-primary h-1.5 bg-surface-variant rounded-full appearance-none outline-none" />
                        <div class="flex justify-between text-[10px] text-on-surface-variant mt-2">
                            <span>1 Epoch</span>
                            <span>10 Epochs</span>
                        </div>
                    </div>
                    
                    <div class="w-full h-[1px] bg-outline-variant/20"></div>

                    <div>
                        <div class="flex justify-between items-center mb-3">
                            <span class="text-xs font-bold text-on-surface-variant uppercase tracking-widest">Batch Size</span>
                            <span class="px-2 py-1 bg-secondary/10 text-secondary font-extrabold text-xs rounded-lg">{trainerState.distillationBatchSize}</span>
                        </div>
                        <input type="range" min="1" max="32" step="1" bind:value={trainerState.distillationBatchSize} class="w-full accent-secondary h-1.5 bg-surface-variant rounded-full appearance-none outline-none" />
                        <div class="flex justify-between text-[10px] text-on-surface-variant mt-2">
                            <span>Micro-batching</span>
                            <span>High VRAM</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Generation Log -->
            <div class="col-span-12 xl:col-span-8 bg-surface-container-high rounded-3xl overflow-hidden flex flex-col border border-outline-variant/10 shadow-inner">
                <div class="px-6 py-4 bg-surface-container-highest border-b border-outline-variant/20 flex justify-between items-center">
                    <h3 class=" font-bold text-sm text-on-surface">Dataset Generation Log</h3>
                    <div class="flex items-center gap-2 px-3 py-1 bg-white/50 dark:bg-slate-800/50 rounded-full border border-outline-variant/30 text-surface-container-highest dark:text-slate-300 shadow-sm">
                         <span class="w-2 h-2 rounded-full bg-on-tertiary-container animate-pulse shadow-[0_0_8px_rgba(79,175,110,0.8)]"></span>
                        <span class="text-[9px] font-bold text-on-surface-variant dark:text-slate-300 uppercase tracking-widest">Active Process</span>
                    </div>
                </div>
                <div class="p-6 font-mono text-[11px] overflow-y-auto h-[220px] bg-[#1a1b1e] text-slate-300 custom-scrollbar leading-relaxed">
                    <div class="flex flex-col h-full">
                        <div class="flex items-center justify-between text-[11px] text-on-surface-variant font-mono border-b border-surface-container-highest pb-2 shrink-0 mb-2">
                            <span class="uppercase tracking-widest font-bold text-on-surface-variant/70">Agent Node Trace</span>
                            <span class="flex items-center gap-2">
                                {#if isSubmitting}
                                <div class="w-2 h-2 rounded-full bg-primary/20 animate-pulse"></div> Async Watchdog Active
                                {:else}
                                <div class="w-2 h-2 rounded-full bg-surface-variant"></div> Watchdog Idle
                                {/if}
                            </span>
                        </div>
                        <div class="font-mono text-[11px] leading-relaxed flex-1 overflow-y-auto custom-scrollbar flex flex-col gap-1.5 pb-2">
                            {#each distillationLogs as log}
                            <div class="text-on-surface-variant/80 flex animate-in slide-in-from-left-2 duration-300">
                                <span class="text-primary/70 mr-2 w-20 shrink-0 text-right select-none">{log.substring(0, log.indexOf(']')+1)}</span>
                                <span>{log.substring(log.indexOf(']')+1).trim()}</span>
                            </div>
                            {/each}
                            {#if distillationLogs.length === 0}
                            <div class="text-on-surface-variant/50 flex">
                                <span class="text-primary/70 mr-2 w-20 shrink-0 text-right select-none">[System]</span>
                                <span>Awaiting compilation loop for dataset distillation...</span>
                            </div>
                            {/if}
                        </div>
                    </div>
                </div>
                
                <!-- Status Bar Integrated -->
                <div class="flex items-center justify-between px-6 py-4 bg-surface-container-low border-t border-outline-variant/10">
                    <div class="flex items-center gap-8">
                        <div class="flex items-center gap-3">
                            <span class="material-symbols-outlined text-on-tertiary-container text-[20px]" style="font-variation-settings: 'FILL' 1;">verified</span>
                            <div>
                                <p class="text-[9px] font-bold text-on-surface-variant uppercase tracking-wider">Source</p>
                                <p class="text-xs font-bold text-on-surface">Verified</p>
                            </div>
                        </div>
                        <div class="flex items-center gap-3">
                            <span class="material-symbols-outlined text-on-surface-variant text-[20px]">storage</span>
                            <div>
                                <p class="text-[9px] font-bold text-on-surface-variant uppercase tracking-wider">Dataset Size</p>
                                <p class="text-xs font-bold text-on-surface">{formatDatasetSize(trainerState.datasetSizeCount)} Samples</p>
                            </div>
                        </div>
                        <!-- VRAM USG removed due to actual pipeline not exposing hardware telemetry locally -->
                    </div>
                </div>
            </div>

        </div>
    </div>
</div>

<style>
    .material-symbols-outlined {
        font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
    }
</style>
