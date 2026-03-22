<script lang="ts">
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
                    <div class="flex items-center gap-4 mb-10 pb-6 border-b border-outline-variant/10">
                        <div class="p-3 bg-primary-fixed/50 rounded-2xl shadow-inner">
                            <span class="material-symbols-outlined text-primary text-[28px]" style="font-variation-settings: 'FILL' 1;">verified</span>
                        </div>
                        <h3 class=" text-xl font-bold text-on-surface">Perfection Engine</h3>
                    </div>
                    
                    <div class="space-y-10">
                        <!-- Slider: Top-K Value -->
                        <div class="space-y-5 px-1">
                            <div class="flex justify-between items-center">
                                <label class="text-sm font-bold text-on-surface">Top-K Retrieval Value</label>
                                <span class="bg-primary/5 text-primary text-xs px-3 py-1 rounded-md font-mono font-bold border border-primary/10">K = 5</span>
                            </div>
                            <input class="w-full h-1.5 bg-surface-variant rounded-full appearance-none cursor-pointer accent-primary hover:accent-primary-container transition-colors" max="50" min="1" type="range" value={5} />
                            <div class="flex justify-between text-[10px] font-bold text-on-surface-variant uppercase tracking-widest mt-2">
                                <span>Precision focus</span>
                                <span>Recall focus</span>
                            </div>
                        </div>

                        <!-- Slider: Embedding Quality -->
                        <div class="space-y-5 px-1 pt-4">
                            <div class="flex justify-between items-center">
                                <label class="text-sm font-bold text-on-surface">Embedding Quality Threshold</label>
                                <span class="bg-tertiary-container/10 text-on-tertiary-container text-xs px-3 py-1 rounded-md font-mono font-bold border border-tertiary-container/20">0.96</span>
                            </div>
                            <input class="w-full h-1.5 bg-surface-variant rounded-full appearance-none cursor-pointer accent-on-tertiary-container hover:accent-tertiary-container transition-colors" max="100" min="0" type="range" value={96} />
                            <p class="text-[11px] text-on-surface-variant leading-relaxed font-medium mt-2">Higher thresholds ensure vector similarity but may increase retrieval misses in sparse datasets.</p>
                        </div>

                        <!-- Toggles Grid -->
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 pt-8">
                            <!-- Toggle 1 -->
                            <div class="flex items-center justify-between p-5 bg-surface-container-low rounded-2xl group border border-outline-variant/5 hover:border-outline-variant/20 transition-colors">
                                <div class="flex flex-col">
                                    <span class="text-[13px] font-bold text-on-surface">Cross-Encoder Re-rank</span>
                                    <span class="text-[10px] text-on-surface-variant mt-0.5">Deep semantic validation</span>
                                </div>
                                <button class="w-12 h-6 bg-primary rounded-full relative cursor-pointer ring-4 ring-primary-fixed/50 transition-colors">
                                    <span class="absolute right-1 top-1 w-4 h-4 bg-white rounded-full shadow-sm"></span>
                                </button>
                            </div>
                            
                            <!-- Toggle 2 -->
                            <div class="flex items-center justify-between p-5 bg-surface-container-low rounded-2xl group border border-outline-variant/5 hover:border-outline-variant/20 transition-colors">
                                <div class="flex flex-col">
                                    <span class="text-[13px] font-bold text-on-surface">Strict Hallucination</span>
                                    <span class="text-[10px] text-on-surface-variant mt-0.5">Entity verification layer</span>
                                </div>
                                <button class="w-12 h-6 bg-primary rounded-full relative cursor-pointer ring-4 ring-primary-fixed/50 transition-colors">
                                    <span class="absolute right-1 top-1 w-4 h-4 bg-white rounded-full shadow-sm"></span>
                                </button>
                            </div>
                            
                            <!-- Toggle 3 -->
                            <div class="flex items-center justify-between p-5 bg-surface-container-low rounded-2xl group border border-outline-variant/5 hover:border-outline-variant/20 transition-colors">
                                <div class="flex flex-col">
                                    <span class="text-[13px] font-bold text-on-surface">Grounding Focus</span>
                                    <span class="text-[10px] text-on-surface-variant mt-0.5">Source-only attribution</span>
                                </div>
                                <button class="w-12 h-6 bg-surface-variant rounded-full relative cursor-pointer hover:bg-outline-variant transition-colors border border-outline-variant/30">
                                    <span class="absolute left-1 top-1 w-4 h-4 bg-white rounded-full shadow-sm"></span>
                                </button>
                            </div>
                            
                            <!-- Toggle 4 -->
                            <div class="flex items-center justify-between p-5 bg-surface-container-low rounded-2xl group border border-outline-variant/5 hover:border-outline-variant/20 transition-colors">
                                <div class="flex flex-col">
                                    <span class="text-[13px] font-bold text-on-surface">Query Expansion</span>
                                    <span class="text-[10px] text-on-surface-variant mt-0.5">Multi-hop decomposition</span>
                                </div>
                                <button class="w-12 h-6 bg-surface-variant rounded-full relative cursor-pointer hover:bg-outline-variant transition-colors border border-outline-variant/30">
                                    <span class="absolute left-1 top-1 w-4 h-4 bg-white rounded-full shadow-sm"></span>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Right Column: Visualizer / Metadata -->
            <div class="col-span-12 xl:col-span-5 space-y-6 flex flex-col">
                <!-- Status Card -->
                <div class="bg-gradient-to-br from-[#001360] to-[#002395] text-white p-8 rounded-3xl relative overflow-hidden h-fit shadow-lg shadow-primary/10 border border-primary/20">
                    <div class="relative z-10">
                        <div class="flex justify-between items-start mb-8">
                            <span class="text-[10px] font-extrabold tracking-[0.25em] uppercase text-white/60">Engine Status</span>
                            <div class="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center backdrop-blur-sm">
                                <span class="material-symbols-outlined text-white/90">speed</span>
                            </div>
                        </div>
                        <h4 class=" text-5xl font-extrabold mb-2 leading-none">99.8%</h4>
                        <p class="text-xs font-bold text-white/70 mb-8 uppercase tracking-widest">Retrieval Accuracy Index</p>
                        
                        <div class="space-y-4">
                            <div class="flex justify-between text-[11px] border-b border-white/10 pb-3 font-mono">
                                <span class="text-white/60 uppercase tracking-widest">Latency</span>
                                <span class="font-bold text-white">142ms</span>
                            </div>
                            <div class="flex justify-between text-[11px] border-b border-white/10 pb-3 font-mono">
                                <span class="text-white/60 uppercase tracking-widest">Throughput</span>
                                <span class="font-bold text-white">1.2k req/min</span>
                            </div>
                            <div class="flex justify-between text-[11px] font-mono">
                                <span class="text-white/60 uppercase tracking-widest">Resources</span>
                                <span class="font-bold text-white">Optimized</span>
                            </div>
                        </div>
                    </div>
                    <!-- Abstract Design Background -->
                    <div class="absolute -right-20 -bottom-20 w-64 h-64 rounded-full bg-primary-fixed blur-[60px] opacity-30"></div>
                </div>

                <!-- Pipeline Visualization Placeholder -->
                <div class="bg-surface-container-lowest p-8 rounded-3xl border border-outline-variant/10 shadow-sm flex-1">
                    <h5 class="text-[10px] font-extrabold text-on-surface-variant uppercase tracking-widest mb-8 ">Execution Flow Graph</h5>
                    
                    <div class="space-y-5 px-2">
                        <div class="flex items-center gap-4">
                            <div class="w-3 h-3 rounded-full bg-primary shadow-[0_0_10px_rgba(0,19,96,0.5)] ring-4 ring-primary/20 shrink-0"></div>
                            <div class="w-10 border-t-2 border-dashed border-outline-variant/40 shrink-0"></div>
                            <div class="px-4 py-2 bg-surface text-[11px] font-extrabold rounded-xl shadow-sm uppercase tracking-widest text-[#444653] border border-outline-variant/10 w-full">Query Vectorization</div>
                        </div>
                        
                        <div class="flex items-center gap-4">
                            <div class="w-3 h-3 rounded-full bg-primary ring-4 ring-primary/20 shrink-0"></div>
                            <div class="w-10 border-t-2 border-dashed border-outline-variant/40 shrink-0"></div>
                            <div class="px-4 py-2 bg-surface text-[11px] font-extrabold rounded-xl shadow-sm uppercase tracking-widest text-[#444653] border border-outline-variant/10 w-full flex justify-between">
                                <span>Retrieval Matrix</span>
                                <span class="text-primary bg-primary/10 px-2 rounded">K=5</span>
                            </div>
                        </div>
                        
                        <div class="flex items-center gap-4">
                            <div class="w-3 h-3 rounded-full bg-on-tertiary-container shadow-[0_0_10px_rgba(79,175,110,0.5)] ring-4 ring-on-tertiary-container/20 shrink-0"></div>
                            <div class="w-10 border-t-2 border-dashed border-outline-variant/40 shrink-0"></div>
                            <div class="px-4 py-2 bg-[#f6fcf8] text-[11px] font-extrabold rounded-xl shadow-sm uppercase tracking-widest text-on-tertiary-container border border-on-tertiary-container/30 w-full flex items-center gap-2">
                                <span class="material-symbols-outlined text-[14px]">security</span>
                                Hallucination Filter
                            </div>
                        </div>
                        
                        <div class="flex items-center gap-4">
                            <div class="w-3 h-3 rounded-full bg-secondary ring-4 ring-secondary/20 shrink-0"></div>
                            <div class="w-10 border-t-2 border-dashed border-outline-variant/40 shrink-0"></div>
                            <div class="px-4 py-2 bg-surface text-[11px] font-extrabold rounded-xl shadow-sm uppercase tracking-widest text-[#444653] border border-outline-variant/10 w-full">Context Injector</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Action Footer -->
        <div class="flex justify-end gap-4 border-t border-outline-variant/10 pt-8 pb-4">
            <button class="px-8 py-3 bg-white text-on-surface-variant text-xs font-bold uppercase tracking-widest rounded-xl shadow-sm border border-outline-variant/20 hover:bg-surface-container-low transition-colors active:scale-95">
                Discard
            </button>
            <button class="px-10 py-3 bg-gradient-to-br from-[#001360] to-[#002395] text-white text-xs font-bold uppercase tracking-widest rounded-xl shadow-md shadow-primary/20 hover:shadow-lg active:scale-95 transition-all">
                Update Pipeline Conf
            </button>
        </div>
    </div>

    <!-- Contextual "Grounding" Alert Glassmorphism -->
    <div class="absolute bottom-8 left-1/2 -translate-x-1/2 bg-white/80 backdrop-blur-xl border border-white/60 px-6 py-4 rounded-2xl shadow-[0_10px_40px_rgba(0,0,0,0.1)] flex items-center gap-5 z-50 animate-in slide-in-from-bottom-5 duration-500">
        <div class="w-12 h-12 rounded-full bg-tertiary-container/10 flex items-center justify-center shrink-0 border border-tertiary-container/20">
            <span class="material-symbols-outlined text-on-tertiary-container text-[24px]">auto_awesome</span>
        </div>
        <div>
            <p class="text-[13px] font-extrabold text-on-surface tracking-tight mb-0.5 ">Grounding Engine Active</p>
            <p class="text-[11px] text-on-surface-variant font-medium">Model will exclusively utilize the internal Sovereign DB for responses.</p>
        </div>
        <button class="ml-4 pl-4 border-l border-outline-variant/20 text-on-surface-variant hover:text-error transition-colors flex shrink-0">
            <span class="material-symbols-outlined text-[20px]">close</span>
        </button>
    </div>
</div>

<style>
    .material-symbols-outlined {
        font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
    }
    
    input[type=range] {
        -webkit-appearance: none;
        width: 100%;
        background: transparent;
    }
    input[type=range]::-webkit-slider-thumb {
        -webkit-appearance: none;
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
    
    /* Dedicated specific coloring for the second slider */
    input[type=range].accent-on-tertiary-container::-webkit-slider-thumb {
        background: var(--color-on-tertiary-container);
        box-shadow: 0 0 10px rgba(79, 175, 110, 0.4);
    }
    input[type=range].accent-on-tertiary-container::-webkit-slider-thumb:hover {
        background: var(--color-tertiary-fixed-dim);
    }

    input[type=range]::-webkit-slider-runnable-track {
        width: 100%;
        height: 6px;
        cursor: pointer;
        background: var(--color-surface-variant);
        border-radius: 3px;
    }
</style>
