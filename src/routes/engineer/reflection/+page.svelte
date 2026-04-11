<script lang="ts">
    import { onMount } from 'svelte';
    import { trainerState, exportReflectionLogs, getSelfCorrectRatio } from '$lib/trainer.svelte';

    let isReflecting = $state(false);
    
    // Dataset JSON state
    let validationStatus = $state<{valid: boolean | null, msg: string}>({valid: null, msg: "UTF-8 • JSON"});
    let reflectionDatasetJson = $state(`{
  "step_id": "reflection_v4_092",
  "input_query": "Summarize the quarterly risk report for EMEA.",
  "chain_of_thought": [
    {
      "thought": "Identify primary risk factors mentioned in page 4-12.",
      "self_critique": "Initial scan missed political instability in section 3.",
      "correction": "Rerouting attention to geopolitical headers."
    },
    {
      "thought": "Synthesize fiscal impact vs operational impact.",
      "confidence_score": 0.982
    }
  ],
  "output_buffer": "The EMEA region shows a 12% rise in political risk due to shifts in border policies..."
}`);

    let liveStreamLogs = $state<any[]>([]);

    function validateDataset() {
        try {
            JSON.parse(reflectionDatasetJson);
            validationStatus = { valid: true, msg: "Syntax OK" };
            setTimeout(() => validationStatus.msg = "UTF-8 • JSON", 3000);
        } catch(e: any) {
            validationStatus = { valid: false, msg: e.message };
        }
    }

    function applyToTraining() {
        validateDataset();
        if(validationStatus.valid) {
            alert("Payload Injected to Rust Axiom via Local IPC!");
        }
    }

    async function launchSimulation() {
        if (isReflecting) return;
        isReflecting = true;
        
        const simInterval = setInterval(() => {
            const randomType = Math.random() > 0.5 ? 'correction' : 'completion';
            liveStreamLogs = [{
                type: randomType,
                title: randomType === 'correction' ? "Successful Self-Correction" : "Complex Chain Completion",
                icon: randomType === 'correction' ? "verified" : "psychology",
                color: randomType === 'correction' ? "text-on-tertiary-container bg-tertiary-container/10" : "text-primary bg-primary-container/10",
                desc: randomType === 'correction' ? "Model identified hallucinated figure and corrected to verified data source." : "Deep reasoning loop completed. 12 intermediate steps verified by AI Auditor.",
                time: "Just now"
            }, ...liveStreamLogs].slice(0, 5);
        }, 1500);

        setTimeout(() => { 
            clearInterval(simInterval);
            isReflecting = false; 
        }, 10000);
    }
</script>

<div class="p-8 h-full flex flex-col">

    <!-- Main Canvas -->
    <div class="w-full space-y-10 flex-1">
        <!-- Header & Breadcrumbs -->
        <div class="flex justify-between items-end">
            <div>
                <nav class="flex text-[11px] uppercase tracking-widest font-bold text-on-surface-variant mb-4 gap-2">
                    <span>Model Trainer</span>
                    <span>/</span>
                    <span class="text-primary font-extrabold">Reflection Lab</span>
                </nav>
                <h2 class="text-3xl font-extrabold text-on-surface tracking-tight mb-2 ">Reflection Lab</h2>
                <p class="text-on-surface-variant max-w-2xl text-sm font-medium">
                    Optimize Chain of Thought (CoT) pathways and self-correction mechanisms.
                    Evaluate how the model audits its own reasoning steps before final synthesis.
                </p>
            </div>
            <div class="flex gap-3">
                <button onclick={() => exportReflectionLogs(liveStreamLogs)} class="px-5 py-2.5 rounded-xl border border-outline-variant/30 text-on-surface font-bold text-xs hover:bg-surface-container-low transition-colors">
                    Export Logs
                </button>
                <button onclick={launchSimulation} disabled={isReflecting} class="px-5 py-2.5 rounded-xl bg-gradient-to-br from-[#001360] to-[#002395] text-white font-bold text-xs shadow-md shadow-primary/20 active:scale-95 transition-transform flex items-center gap-2 disabled:opacity-50">
                    <span class="material-symbols-outlined text-[18px]">science</span>
                    {isReflecting ? 'Simulating...' : 'Launch Simulation'}
                </button>
            </div>
        </div>

        <!-- Bento Grid Layout -->
        <div class="grid grid-cols-12 gap-6 pb-12">
            
            <!-- Reflection AI & Tuning Panel -->
            <div class="col-span-12 xl:col-span-4 flex flex-col gap-6">
                <!-- Tuning Controls -->
                <div class="bg-surface-container-lowest p-8 rounded-3xl shadow-sm border border-outline-variant/10">
                    <div class="flex items-center justify-between mb-8">
                        <h3 class="text-lg font-bold flex items-center gap-2 ">
                            <span class="material-symbols-outlined text-primary text-[24px]" style="font-variation-settings: 'FILL' 1;">tune</span>
                            Reflection Controls
                        </h3>
                        <span class="px-2 py-1 bg-tertiary-container/10 text-on-tertiary-container text-[10px] font-extrabold uppercase tracking-widest rounded-md border border-tertiary-container/20">System Active</span>
                    </div>
                    
                    <div class="space-y-8">
                        <div class="flex items-center justify-between p-4 bg-surface-container-low rounded-xl border border-outline-variant/10">
                            <div>
                                <p class="text-xs font-bold text-on-surface">Think-Before-Response</p>
                                <p class="text-[10px] text-on-surface-variant mt-0.5">Force 500ms latent reasoning loop</p>
                            </div>
                            <button aria-label="Toggle Think Before Response" onclick={() => trainerState.internalMonologue = !trainerState.internalMonologue} class="w-12 h-6 {trainerState.internalMonologue ? 'bg-primary ring-4 ring-primary-fixed/50' : 'bg-surface-variant'} rounded-full relative transition-colors cursor-pointer outline-none">
                                <span class="absolute {trainerState.internalMonologue ? 'right-1' : 'left-1'} top-1 w-4 h-4 bg-white rounded-full shadow-sm transition-all"></span>
                            </button>
                        </div>
                        
                        <div class="space-y-4 px-1">
                            <div class="flex justify-between items-center text-[10px] font-bold uppercase tracking-wider text-on-surface-variant">
                                <span>Reasoning Depth</span>
                                <span class="text-primary font-mono bg-primary-fixed/30 px-2 py-0.5 rounded">Level {Math.floor(trainerState.reasoningDepth / 10)}</span>
                            </div>
                            <input class="w-full h-1.5 bg-surface-variant rounded-full appearance-none accent-primary cursor-pointer hover:accent-primary-container transition-colors" type="range" bind:value={trainerState.reasoningDepth} />
                        </div>
                        
                        <div class="space-y-4 px-1">
                            <div class="flex justify-between items-center text-[10px] font-bold uppercase tracking-wider text-on-surface-variant">
                                <span>Audit Intensity</span>
                                <span class="text-primary font-mono bg-primary-fixed/30 px-2 py-0.5 rounded">High ({(trainerState.auditIntensity / 100).toFixed(2)})</span>
                            </div>
                            <input class="w-full h-1.5 bg-surface-variant rounded-full appearance-none accent-primary cursor-pointer hover:accent-primary-container transition-colors" type="range" bind:value={trainerState.auditIntensity} />
                        </div>
                    </div>
                </div>

                <!-- Stats Cards -->
                <div class="grid grid-cols-2 gap-4">
                    <div class="bg-surface-container-lowest p-6 rounded-3xl border border-outline-variant/10 shadow-sm">
                        <p class="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-2">Reasoning Chain</p>
                        <p class="text-2xl font-extrabold text-primary ">Stable</p>
                        <div class="mt-4 flex items-center gap-1.5 text-[10px] text-on-tertiary-container font-extrabold uppercase tracking-tight">
                            <span class="material-symbols-outlined text-[16px]">trending_up</span>
                            <span>+4.2% Consist.</span>
                        </div>
                    </div>
                    <div class="bg-surface-container-lowest p-6 rounded-3xl border border-outline-variant/10 shadow-sm relative overflow-hidden">
                        <div class="absolute -right-4 -bottom-4 w-16 h-16 bg-primary/5 rounded-full blur-xl"></div>
                        <p class="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-2">Self-Correct</p>
                        <p class="text-2xl font-extrabold text-primary pr-2">{getSelfCorrectRatio()}%</p>
                        <div class="mt-4 flex items-center gap-1.5 text-[10px] text-on-tertiary-container font-extrabold uppercase tracking-tight">
                            <span class="material-symbols-outlined text-[16px]">check_circle</span>
                            <span>Optimal Rate</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Main Workspace: Reasoning Chain Analysis -->
            <div class="col-span-12 xl:col-span-8 flex flex-col gap-6">
                <!-- Dataset Editor / JSON Preview -->
                <div class="bg-[#1a1c1d] text-inverse-on-surface rounded-3xl overflow-hidden flex flex-col border border-outline-variant/20 shadow-lg shadow-black/10 flex-1 min-h-[400px]">
                    
                    <div class="flex items-center justify-between px-6 py-4 bg-[#232527] border-b border-[#35383a]">
                        <div class="flex items-center gap-3">
                            <span class="material-symbols-outlined text-primary-fixed-dim text-[20px]">data_object</span>
                            <h3 class="font-bold text-sm text-slate-200">Reflection Dataset Editor — <span class="text-primary-fixed-dim font-mono text-[13px]">Sample_Reasoning_Step.json</span></h3>
                        </div>
                        <div class="flex gap-2">
                            <div class="w-3 h-3 rounded-full bg-error/80 border border-error shadow-inner"></div>
                            <div class="w-3 h-3 rounded-full bg-[#e8c33c] border border-[#d6af20] shadow-inner"></div>
                            <div class="w-3 h-3 rounded-full bg-primary-fixed border border-primary-fixed shadow-inner"></div>
                        </div>
                    </div>
                    
                    <div class="flex-1 overflow-hidden p-6 font-mono text-[13px] leading-loose custom-scrollbar flex">
<textarea bind:value={reflectionDatasetJson} class="w-full h-full bg-transparent border-none focus:outline-none focus:ring-0 resize-none text-[#a9b1d6] font-mono leading-relaxed" spellcheck="false"></textarea>
                    </div>
                    
                    <div class="px-6 py-4 bg-[#232527] border-t border-[#35383a] flex justify-between items-center text-[10px] text-outline-variant font-mono">
                        <span class={validationStatus.valid === false ? 'text-error font-bold' : validationStatus.valid === true ? 'text-primary' : ''}>{validationStatus.msg}</span>
                        <div class="flex gap-6 font-sans">
                            <button onclick={validateDataset} class="hover:text-white transition-colors uppercase font-bold tracking-widest text-[#94A3B8] flex items-center gap-2">
                                <span class="material-symbols-outlined text-[16px]">fact_check</span>
                                Validate Schema
                            </button>
                            <button onclick={applyToTraining} class="text-primary-fixed-dim hover:text-white transition-colors uppercase font-bold tracking-widest flex items-center gap-2">
                                <span class="material-symbols-outlined text-[16px]">publish</span>
                                Apply to Training
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Recent Reflection Logs -->
                <div class="bg-surface-container-lowest rounded-3xl shadow-sm border border-outline-variant/10">
                    <div class="px-6 py-5 border-b border-outline-variant/10 flex justify-between items-center">
                        <h3 class="font-bold text-sm text-on-surface ">Live Reflection Stream</h3>
                        <div class="w-16 h-1 bg-surface-variant rounded-full overflow-hidden">
                            <div class="w-1/3 h-full bg-primary animate-pulse rounded-full mx-auto"></div>
                        </div>
                    </div>
                    <div class="divide-y divide-outline-variant/5">
                        {#each liveStreamLogs as log}
                        <div class="p-5 flex items-start gap-4 hover:bg-surface-container-low transition-colors group cursor-pointer animate-in fade-in slide-in-from-top-4 duration-500">
                            <div class="w-10 h-10 rounded-xl {log.color} flex items-center justify-center shrink-0 group-hover:bg-opacity-80 transition-colors">
                                <span class="material-symbols-outlined text-[20px]">{log.icon}</span>
                            </div>
                            <div class="flex-1 mt-0.5">
                                <div class="flex justify-between mb-1.5">
                                    <span class="text-xs font-bold text-on-surface">{log.title}</span>
                                    <span class="text-[10px] text-on-surface-variant font-bold uppercase tracking-widest">{log.time}</span>
                                </div>
                                <p class="text-[12px] text-on-surface-variant leading-relaxed">{log.desc}</p>
                            </div>
                        </div>
                        {/each}
                        {#if liveStreamLogs.length === 0}
                            <div class="flex justify-center flex-col items-center py-10 opacity-50">
                                <span class="material-symbols-outlined text-[42px] mb-2 text-on-surface-variant">hourglass_empty</span>
                                <p class="text-xs text-on-surface-variant uppercase tracking-widest font-bold">Waiting for simulation triggers...</p>
                            </div>
                        {/if}
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
    input[type=range]::-moz-range-track {
        width: 100%;
        height: 6px;
        cursor: pointer;
        background: var(--color-surface-variant);
        border-radius: 3px;
    }
</style>
