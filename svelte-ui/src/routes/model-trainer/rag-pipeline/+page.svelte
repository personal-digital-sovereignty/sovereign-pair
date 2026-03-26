<script lang="ts">
    import { trainerState } from '$lib/trainer.svelte';
    
    let flowStep = $state(0);
    let sseClient: EventSource | null = null;
    
    async function launchDeepResearch() {
        if (!trainerState.deepResearchPrompt.trim() || trainerState.isDeepResearchActive) return;
        
        trainerState.isDeepResearchActive = true;
        trainerState.deepResearchScrapedSources = 0;
        flowStep = 0;
        
        // Spawn Real SSE Connection to Sovereign Engine
        if (sseClient) {
            sseClient.close();
        }
        sseClient = new EventSource('http://localhost:38001/v1/trainer/unsloth-monitor');
        
        sseClient.onmessage = (event) => {
            const data = event.data;
            if (data.includes('[STEP 0]')) {
                flowStep = 0;
            } else if (data.includes('[STEP 1]')) {
                flowStep = 1;
            } else if (data.includes('[STEP 2]')) {
                flowStep = 2;
            } else if (data.includes('[STEP 3]')) {
                flowStep = 3;
            } else if (data.includes('[STEP 4]')) {
                flowStep = 4;
                trainerState.isDeepResearchActive = false;
                if (sseClient) sseClient.close();
            } else if (data.includes('[SCRAPED: ')) {
                // Parse amount e.g. [SCRAPED: 3]
                const match = data.match(/\[SCRAPED: (\d+)\]/);
                if (match && match[1]) {
                    trainerState.deepResearchScrapedSources += parseInt(match[1], 10);
                }
            } else if (data.includes('DEEP_RESEARCH') && data.includes('ABORTED')) {
                trainerState.isDeepResearchActive = false;
                if (sseClient) sseClient.close();
            }
        };

        try {
            await fetch('http://localhost:38001/v1/trainer/deep-research', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    directive: trainerState.deepResearchPrompt,
                    strict_hallucination: trainerState.deepResearchStrictHallucination,
                    grounding_focus: trainerState.deepResearchGroundingFocus,
                    query_expansion: trainerState.deepResearchQueryExpansion,
                    model: trainerState.deepResearchModel
                })
            });
        } catch (e) {
            console.error("🚀 Fatal: Sensus Deep Research Invocation Failed", e);
            trainerState.isDeepResearchActive = false;
            if (sseClient) sseClient.close();
        }
    }

    async function cancelDeepResearch() {
        if (!trainerState.isDeepResearchActive) return;
        
        trainerState.isDeepResearchActive = false;
        if (sseClient) {
            sseClient.close();
            sseClient = null;
        }

        try {
            await fetch('http://localhost:38001/v1/trainer/deep-research/cancel', {
                method: 'POST'
            });
        } catch (e) {
            console.error("Failed to abort deep research process.", e);
        }
    }
</script>

<div class="p-8 h-full flex flex-col relative">
    <!-- Header Section -->
    <header class="mb-10 w-full flex items-center justify-between">
        <div class="flex items-center gap-4 bg-surface-container-low px-4 py-2 rounded-full w-[400px] border border-outline-variant/10 shadow-sm relative">
            <span class="material-symbols-outlined text-on-surface-variant text-[20px] absolute left-4">search</span>
            <input class="bg-transparent border-none focus:ring-0 text-sm w-full pl-8 placeholder:text-on-surface-variant/70 text-on-surface outline-none" placeholder="Search pipeline nodes..." type="text" />
        </div>
        <div class="flex items-center gap-4 bg-surface-container-low p-1.5 rounded-xl border border-outline-variant/10">
            <a href="/model-trainer/fine-tuning" class="px-4 py-2 text-on-surface-variant font-medium text-xs rounded-lg hover:bg-surface-container-high transition-colors">Fine-Tuning</a>
            <a href="/model-trainer/distillation" class="px-4 py-2 text-on-surface-variant font-medium text-xs rounded-lg hover:bg-surface-container-high transition-colors">Distillation</a>
            <a href="/model-trainer/reflection" class="px-4 py-2 text-on-surface-variant font-medium text-xs rounded-lg hover:bg-surface-container-high transition-colors">Reflection Lab</a>
            <button class="px-4 py-2 bg-surface-container-lowest text-primary font-bold text-xs rounded-lg shadow-sm">RAG Pipeline</button>
            <a href="/model-trainer/unsloth" class="px-4 py-2 text-on-surface-variant font-medium text-xs rounded-lg hover:bg-surface-container-high transition-colors">Unsloth Monitor</a>
        </div>
    </header>

    <!-- Main Canvas -->
    <div class="w-full space-y-10 flex-1">
        <!-- Header & Breadcrumbs -->
        <div class="flex justify-between items-end mb-10">
            <div>
                <nav class="flex items-center gap-2 text-[11px] font-bold text-on-surface-variant tracking-wider uppercase mb-2">
                    <span>Deployments</span>
                    <span class="material-symbols-outlined text-[14px]">chevron_right</span>
                    <span class="text-primary font-extrabold">Pipeline Config</span>
                </nav>
                <h2 class=" text-3xl font-extrabold text-on-surface tracking-tight">RAG Pipeline Orchestrator</h2>
            </div>
            <div class="flex items-center gap-3">
                <div class="flex items-center gap-2 px-4 py-2 bg-tertiary-container/10 text-on-tertiary-fixed-variant rounded-full border border-tertiary-container/20">
                    <span class="relative flex h-2 w-2">
                        <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-on-tertiary-container opacity-75"></span>
                        <span class="relative inline-flex rounded-full h-2 w-2 bg-on-tertiary-container"></span>
                    </span>
                    <span class="text-[12px] font-bold tracking-tight">Optimized for Low-Latency</span>
                </div>
            </div>
        </div>

        <!-- Bento Grid Layout -->
        <div class="grid grid-cols-12 gap-6 pb-12">
            <!-- Left Column: Perfection Controls -->
            <div class="col-span-12 xl:col-span-7 space-y-6">
                <div class="bg-surface-container-lowest p-8 rounded-3xl shadow-sm border border-outline-variant/10">
                    <div class="flex items-center gap-4 mb-8 pb-6 border-b border-outline-variant/10">
                        <div class="p-3 bg-primary-fixed/50 rounded-2xl shadow-inner">
                            <span class="material-symbols-outlined text-primary text-[28px]" style="font-variation-settings: 'FILL' 1;">travel_explore</span>
                        </div>
                        <div>
                            <h3 class=" text-xl font-bold text-on-surface">Deep Research Protocol</h3>
                            <p class="text-[11px] font-medium text-on-surface-variant mt-1">Sovereign pipelines will autonomously scrape, verify, and distill global knowledge into the RAG Vault.</p>
                        </div>
                    </div>
                    
                    <div class="space-y-8">
                        <!-- Generative Input Area -->
                        <div class="space-y-3">
                            <div class="flex justify-between items-center">
                                <label for="deep-research-prompt" class="text-xs font-bold text-on-surface-variant uppercase tracking-widest">Research Directive</label>
                                <div class="flex items-center gap-3">
                                    <select bind:value={trainerState.deepResearchModel} disabled={trainerState.isDeepResearchActive} class="bg-surface-container border border-outline-variant/30 text-[11px] text-on-surface font-bold rounded-lg px-2 py-1 outline-none focus:ring-1 focus:ring-primary shadow-sm disabled:opacity-50">
                                        <option value="llama3.2:latest">Llama 3.2 3B (Fast Triage)</option>
                                        <option value="qwen2.5:14b">Qwen 2.5 14B (Heavy Analytics)</option>
                                    </select>
                                    {#if trainerState.isDeepResearchActive}
                                    <span class="bg-tertiary-container/20 text-on-tertiary-container text-xs px-3 py-1 rounded-md font-mono font-bold border border-tertiary-container/30 animate-pulse flex items-center gap-2">
                                        <div class="w-2 h-2 rounded-full bg-on-tertiary-container"></div> Executing
                                    </span>
                                    {/if}
                                </div>
                            </div>
                            <textarea 
                                id="deep-research-prompt"
                                bind:value={trainerState.deepResearchPrompt}
                                disabled={trainerState.isDeepResearchActive}
                                placeholder='e.g. "Analise o histórico de preço das ações da Petrobras e verifique quais períodos do ano suas ações mais sofrem quedas. Traga um percentil anual justificando os motivadores..."'
                                class="w-full h-44 bg-surface-container-high border border-outline-variant/30 rounded-2xl p-5 text-sm font-medium text-on-surface placeholder:text-on-surface-variant/40 focus:ring-2 focus:ring-primary focus:border-transparent outline-none resize-none disabled:opacity-50 transition-all custom-scrollbar"
                            ></textarea>
                            <p class="text-[10px] text-on-surface-variant/70 leading-relaxed font-medium">Use highly specific prompts. The engine will decompose multi-hop questions and compile the results into a definitive Markdown artifact within your selected Workspace.</p>
                        </div>

                        <!-- Toggles Grid: Research Modifiers -->
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4">
                            <!-- Toggle 1: Cross-Encoder -->
                            <div class="flex items-center justify-between p-5 bg-surface-container-low rounded-2xl group border border-outline-variant/5 hover:border-outline-variant/20 transition-colors">
                                <div class="flex flex-col">
                                    <span class="text-[13px] font-bold text-on-surface">Cross-Encoder Re-rank</span>
                                    <span class="text-[10px] text-on-surface-variant mt-0.5">Deep semantic validation</span>
                                </div>
                                <button aria-label="Toggle Cross-Encoder Re-rank" disabled={trainerState.isDeepResearchActive} onclick={() => trainerState.deepResearchCrossEncoder = !trainerState.deepResearchCrossEncoder} class="w-12 h-6 rounded-full relative cursor-pointer border transition-colors disabled:opacity-50 {trainerState.deepResearchCrossEncoder ? 'bg-primary ring-4 ring-primary-fixed/50 border-transparent' : 'bg-surface-variant hover:bg-outline-variant border-outline-variant/30'}">
                                    <span class="absolute top-1 w-4 h-4 bg-white rounded-full shadow-sm transition-all {trainerState.deepResearchCrossEncoder ? 'right-1' : 'left-1'}"></span>
                                </button>
                            </div>
                            
                            <!-- Toggle 2: Strict Hallucination -->
                            <div class="flex items-center justify-between p-5 bg-surface-container-low rounded-2xl group border border-outline-variant/5 hover:border-outline-variant/20 transition-colors">
                                <div class="flex flex-col">
                                    <span class="text-[13px] font-bold text-on-surface">Strict Hallucination</span>
                                    <span class="text-[10px] text-on-surface-variant mt-0.5">Entity verification layer</span>
                                </div>
                                <button aria-label="Toggle Strict Hallucination" disabled={trainerState.isDeepResearchActive} onclick={() => trainerState.deepResearchStrictHallucination = !trainerState.deepResearchStrictHallucination} class="w-12 h-6 rounded-full relative cursor-pointer border transition-colors disabled:opacity-50 {trainerState.deepResearchStrictHallucination ? 'bg-primary ring-4 ring-primary-fixed/50 border-transparent' : 'bg-surface-variant hover:bg-outline-variant border-outline-variant/30'}">
                                    <span class="absolute top-1 w-4 h-4 bg-white rounded-full shadow-sm transition-all {trainerState.deepResearchStrictHallucination ? 'right-1' : 'left-1'}"></span>
                                </button>
                            </div>
                            
                            <!-- Toggle 3: Grounding Focus -->
                            <div class="flex items-center justify-between p-5 bg-surface-container-low rounded-2xl group border border-outline-variant/5 hover:border-outline-variant/20 transition-colors">
                                <div class="flex flex-col">
                                    <span class="text-[13px] font-bold text-on-surface">Grounding Focus</span>
                                    <span class="text-[10px] text-on-surface-variant mt-0.5">Source-only attribution</span>
                                </div>
                                <button aria-label="Toggle Grounding Focus" disabled={trainerState.isDeepResearchActive} onclick={() => trainerState.deepResearchGroundingFocus = !trainerState.deepResearchGroundingFocus} class="w-12 h-6 rounded-full relative cursor-pointer border transition-colors disabled:opacity-50 {trainerState.deepResearchGroundingFocus ? 'bg-primary ring-4 ring-primary-fixed/50 border-transparent' : 'bg-surface-variant hover:bg-outline-variant border-outline-variant/30'}">
                                    <span class="absolute top-1 w-4 h-4 bg-white rounded-full shadow-sm transition-all {trainerState.deepResearchGroundingFocus ? 'right-1' : 'left-1'}"></span>
                                </button>
                            </div>
                            
                            <!-- Toggle 4: Query Expansion -->
                            <div class="flex items-center justify-between p-5 bg-surface-container-low rounded-2xl group border border-outline-variant/5 hover:border-outline-variant/20 transition-colors">
                                <div class="flex flex-col">
                                    <span class="text-[13px] font-bold text-on-surface">Query Expansion</span>
                                    <span class="text-[10px] text-on-surface-variant mt-0.5">Multi-hop decomposition</span>
                                </div>
                                <button aria-label="Toggle Query Expansion" disabled={trainerState.isDeepResearchActive} onclick={() => trainerState.deepResearchQueryExpansion = !trainerState.deepResearchQueryExpansion} class="w-12 h-6 rounded-full relative cursor-pointer border transition-colors disabled:opacity-50 {trainerState.deepResearchQueryExpansion ? 'bg-primary ring-4 ring-primary-fixed/50 border-transparent' : 'bg-surface-variant hover:bg-outline-variant border-outline-variant/30'}">
                                    <span class="absolute top-1 w-4 h-4 bg-white rounded-full shadow-sm transition-all {trainerState.deepResearchQueryExpansion ? 'right-1' : 'left-1'}"></span>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Right Column: Visualizer / Metadata -->
            <div class="col-span-12 xl:col-span-5 space-y-6 flex flex-col">
                <!-- Status Card -->
                <div class="bg-gradient-to-br from-[#001360] to-[#002395] text-white p-8 rounded-3xl relative overflow-hidden h-fit shadow-lg shadow-primary/10 border border-primary/20 transition-all duration-500 {trainerState.isDeepResearchActive ? 'ring-2 ring-primary ring-offset-2 ring-offset-surface' : ''}">
                    <div class="relative z-10">
                        <div class="flex justify-between items-start mb-8">
                            <span class="text-[10px] font-extrabold tracking-[0.25em] uppercase text-white/60">Engine Status</span>
                            <div class="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center backdrop-blur-sm">
                                {#if trainerState.isDeepResearchActive}
                                <span class="material-symbols-outlined text-white/90 animate-spin">autorenew</span>
                                {:else}
                                <span class="material-symbols-outlined text-white/90">speed</span>
                                {/if}
                            </div>
                        </div>
                        <h4 class=" text-5xl font-extrabold mb-2 leading-none font-mono">{trainerState.isDeepResearchActive ? trainerState.deepResearchScrapedSources : (flowStep === 4 && trainerState.deepResearchScrapedSources > 0) ? trainerState.deepResearchScrapedSources : 'Idle'}</h4>
                        <p class="text-xs font-bold text-white/70 mb-8 uppercase tracking-widest">{trainerState.isDeepResearchActive || flowStep === 4 ? 'Sources Scraped' : 'Awaiting Protocol'}</p>
                        
                        <div class="space-y-4">
                            <div class="flex justify-between text-[11px] border-b border-white/10 pb-3 font-mono">
                                <span class="text-white/60 uppercase tracking-widest">Latency</span>
                                <span class="font-bold text-white">{trainerState.isDeepResearchActive ? `${Math.floor(Math.random()*40)+10}ms` : '--'}</span>
                            </div>
                            <div class="flex justify-between text-[11px] border-b border-white/10 pb-3 font-mono">
                                <span class="text-white/60 uppercase tracking-widest">Active Threads</span>
                                <span class="font-bold text-white">{trainerState.isDeepResearchActive ? '64 (Max)' : '0'}</span>
                            </div>
                            <div class="flex justify-between text-[11px] font-mono">
                                <span class="text-white/60 uppercase tracking-widest">Engine Load</span>
                                <span class="font-bold text-white">{trainerState.isDeepResearchActive ? '100% (Turbine)' : 'Standby'}</span>
                            </div>
                        </div>
                    </div>
                    <!-- Abstract Design Background -->
                    <div class="absolute -right-20 -bottom-20 w-64 h-64 rounded-full bg-primary-fixed blur-[60px] opacity-30 {trainerState.isDeepResearchActive ? 'animate-pulse scale-150' : ''}"></div>
                </div>

                <!-- Pipeline Visualization Placeholder -->
                <div class="bg-surface-container-lowest p-8 rounded-3xl border border-outline-variant/10 shadow-sm flex-1">
                    <h5 class="text-[10px] font-extrabold text-on-surface-variant uppercase tracking-widest mb-8 ">Execution Flow Graph</h5>
                    
                    <div class="space-y-5 px-2">
                        <!-- Step 1 -->
                        <div class="flex items-center gap-4 transition-all duration-300 {trainerState.isDeepResearchActive && flowStep >= 0 || flowStep === 4 ? 'opacity-100 scale-100' : 'opacity-40 grayscale scale-95'}">
                            <div class="w-4 h-4 rounded-full bg-primary shadow-[0_0_10px_rgba(0,19,96,0.5)] ring-4 ring-primary/20 shrink-0 {trainerState.isDeepResearchActive && flowStep === 0 ? 'animate-pulse' : ''} flex items-center justify-center {flowStep > 0 || flowStep === 4 ? 'bg-secondary' : ''}">
                                {#if flowStep > 0 || flowStep === 4}
                                <span class="material-symbols-outlined text-white text-[10px] font-bold">check</span>
                                {/if}
                            </div>
                            <div class="w-10 border-t-2 border-dashed border-outline-variant/40 shrink-0 {flowStep > 0 || flowStep === 4 ? 'border-secondary' : ''}"></div>
                            <div class="px-4 py-2 bg-surface text-[11px] font-extrabold rounded-xl shadow-sm uppercase tracking-widest text-[#444653] border border-outline-variant/10 w-full flex items-center justify-between">
                                Query Vectorization
                                {#if trainerState.isDeepResearchActive && flowStep === 0} <span class="w-2 h-2 rounded-full bg-primary animate-pulse"></span> {/if}
                            </div>
                        </div>
                        
                        <!-- Step 2 -->
                        <div class="flex items-center gap-4 transition-all duration-300 {trainerState.isDeepResearchActive && flowStep >= 1 || flowStep === 4 ? 'opacity-100 scale-100' : 'opacity-40 grayscale scale-95'}">
                            <div class="w-4 h-4 rounded-full bg-primary ring-4 ring-primary/20 shrink-0 {trainerState.isDeepResearchActive && flowStep === 1 ? 'animate-pulse' : ''} flex items-center justify-center {flowStep > 1 || flowStep === 4 ? 'bg-secondary' : ''}">
                                {#if flowStep > 1 || flowStep === 4}
                                <span class="material-symbols-outlined text-white text-[10px] font-bold">check</span>
                                {/if}
                            </div>
                            <div class="w-10 border-t-2 border-dashed border-outline-variant/40 shrink-0 {flowStep > 1 || flowStep === 4 ? 'border-secondary' : ''}"></div>
                            <div class="px-4 py-2 bg-surface text-[11px] font-extrabold rounded-xl shadow-sm uppercase tracking-widest text-[#444653] border border-outline-variant/10 w-full flex justify-between items-center">
                                <span>Web Matrix Scraper</span>
                                {#if trainerState.isDeepResearchActive && flowStep === 1}
                                <span class="text-primary bg-primary/10 px-2 py-0.5 rounded font-mono animate-pulse">{trainerState.deepResearchScrapedSources} docs</span>
                                {/if}
                            </div>
                        </div>
                        
                        <!-- Step 3 -->
                        <div class="flex items-center gap-4 transition-all duration-300 {trainerState.isDeepResearchActive && flowStep >= 2 || flowStep === 4 ? 'opacity-100 scale-100' : 'opacity-40 grayscale scale-95'}">
                            <div class="w-4 h-4 rounded-full bg-on-tertiary-container shadow-[0_0_10px_rgba(79,175,110,0.5)] ring-4 ring-on-tertiary-container/20 shrink-0 {trainerState.isDeepResearchActive && flowStep === 2 ? 'animate-pulse' : ''} flex items-center justify-center {flowStep > 2 || flowStep === 4 ? 'bg-secondary' : ''}">
                                {#if flowStep > 2 || flowStep === 4}
                                <span class="material-symbols-outlined text-white text-[10px] font-bold">check</span>
                                {/if}
                            </div>
                            <div class="w-10 border-t-2 border-dashed border-outline-variant/40 shrink-0 {flowStep > 2 || flowStep === 4 ? 'border-secondary' : ''}"></div>
                            <div class="px-4 py-2 bg-[#f6fcf8] text-[11px] font-extrabold rounded-xl shadow-sm uppercase tracking-widest text-on-tertiary-container border border-on-tertiary-container/30 w-full flex items-center gap-2 justify-between">
                                <span class="flex items-center gap-2"><span class="material-symbols-outlined text-[14px]">security</span> Hallucination Filter</span>
                                {#if trainerState.isDeepResearchActive && flowStep === 2} <span class="w-2 h-2 rounded-full bg-on-tertiary-container animate-pulse"></span> {/if}
                            </div>
                        </div>
                        
                        <!-- Step 4 -->
                        <div class="flex items-center gap-4 transition-all duration-300 {trainerState.isDeepResearchActive && flowStep >= 3 || flowStep === 4 ? 'opacity-100 scale-100' : 'opacity-40 grayscale scale-95'}">
                            <div class="w-4 h-4 rounded-full bg-secondary ring-4 ring-secondary/20 shrink-0 {trainerState.isDeepResearchActive && flowStep === 3 ? 'animate-pulse' : ''} flex items-center justify-center {flowStep === 4 ? 'bg-secondary' : ''}">
                                {#if flowStep === 4}
                                <span class="material-symbols-outlined text-white text-[10px] font-bold">check</span>
                                {/if}
                            </div>
                            <div class="w-10 border-t-2 border-dashed border-outline-variant/40 shrink-0"></div>
                            <div class="px-4 py-2 bg-surface text-[11px] font-extrabold rounded-xl shadow-sm uppercase tracking-widest text-[#444653] border border-outline-variant/10 w-full flex items-center justify-between">
                                Vault Context Injector
                                {#if trainerState.isDeepResearchActive && flowStep === 3} <span class="w-2 h-2 rounded-full bg-secondary animate-pulse"></span> {/if}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Action Footer -->
        <div class="flex justify-end gap-4 border-t border-outline-variant/10 pt-8 pb-4">
            <button onclick={cancelDeepResearch} disabled={!trainerState.isDeepResearchActive} class="cursor-pointer px-8 py-3 bg-white text-on-surface-variant text-xs font-bold uppercase tracking-widest rounded-xl shadow-sm border border-outline-variant/20 hover:bg-surface-container-low transition-colors active:scale-95 disabled:opacity-50">
                Cancel Crawler
            </button>
            <button onclick={launchDeepResearch} disabled={trainerState.isDeepResearchActive || !trainerState.deepResearchPrompt.trim()} class="cursor-pointer px-10 py-3 bg-gradient-to-br flex items-center gap-3 from-[#001360] to-[#002395] text-white text-xs font-bold uppercase tracking-widest rounded-xl shadow-md shadow-primary/20 hover:shadow-lg active:scale-95 transition-all disabled:opacity-50 disabled:grayscale">
                {#if trainerState.isDeepResearchActive}
                    <span class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                    Executing Analysis...
                {:else}
                    <span class="material-symbols-outlined text-[18px]">travel_explore</span>
                    Launch Deep Research
                {/if}
            </button>
        </div>
    </div>

    <!-- Contextual "Grounding" Alert Glassmorphism -->
    {#if trainerState.deepResearchGroundingFocus}
    <div class="absolute bottom-8 left-1/2 -translate-x-1/2 bg-white/80 backdrop-blur-xl border border-white/60 px-6 py-4 rounded-2xl shadow-[0_10px_40px_rgba(0,0,0,0.1)] flex items-center gap-5 z-50 animate-in slide-in-from-bottom-5 duration-500">
        <div class="w-12 h-12 rounded-full bg-tertiary-container/10 flex items-center justify-center shrink-0 border border-tertiary-container/20">
            <span class="material-symbols-outlined text-on-tertiary-container text-[24px]">database</span>
        </div>
        <div>
            <p class="text-[13px] font-extrabold text-on-surface tracking-tight mb-0.5 ">Grounding Engine Active</p>
            <p class="text-[11px] text-on-surface-variant font-medium">Model will exclusively utilize the internal Sovereign DB for responses.</p>
        </div>
        <button aria-label="Dismiss Grounding Alert" onclick={() => trainerState.deepResearchGroundingFocus = false} class="ml-4 pl-4 border-l border-outline-variant/20 text-on-surface-variant hover:text-error transition-colors flex shrink-0">
            <span class="material-symbols-outlined text-[20px]">close</span>
        </button>
    </div>
    {/if}
</div>

<style>
    .material-symbols-outlined {
        font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
    }
</style>
