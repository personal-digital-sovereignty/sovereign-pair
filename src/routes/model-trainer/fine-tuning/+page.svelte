<script lang="ts">
    import { page } from '$app/state';
    import { goto } from '$app/navigation';

    let isSubmitting = false;

    async function runFineTuning() {
        if(isSubmitting) return;
        isSubmitting = true;
        try {
            await fetch('http://localhost:38001/v1/trainer/finetuning', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    base_model: 'Llama-3-8B-Instruct-v0.1',
                    dataset_name: 'sovereign-hq-rag-dataset-v1',
                    learning_rate: 0.0002
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
                <button class="px-5 py-2.5 rounded-xl border border-outline-variant/30 text-on-surface-variant font-bold text-xs hover:bg-surface-container-high transition-colors">
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
                        <div class="w-10 h-5 bg-primary rounded-full relative">
                            <div class="absolute right-1 top-1 w-3 h-3 bg-white rounded-full"></div>
                        </div>
                    </div>
                </div>

                <div class="grid grid-cols-3 gap-4 mb-8">
                    <div class="p-4 bg-surface-container-low rounded-xl">
                        <p class="text-[10px] text-on-surface-variant font-bold uppercase mb-2">Knowledge Gap</p>
                        <p class="text-lg font-bold text-on-surface">14.2%</p>
                        <div class="w-full h-1 bg-surface-container-highest mt-3 rounded-full overflow-hidden">
                            <div class="w-2/3 h-full bg-primary"></div>
                        </div>
                    </div>
                    <div class="p-4 bg-surface-container-low rounded-xl">
                        <p class="text-[10px] text-on-surface-variant font-bold uppercase mb-2">Sources Scanned</p>
                        <p class="text-lg font-bold text-on-surface">1,402</p>
                        <p class="text-[10px] text-on-tertiary-container font-bold mt-1">+12 in last hour</p>
                    </div>
                    <div class="p-4 bg-surface-container-low rounded-xl">
                        <p class="text-[10px] text-on-surface-variant font-bold uppercase mb-2">Vault Sync</p>
                        <p class="text-lg font-bold text-on-surface">Encrypted</p>
                        <span class="text-[10px] bg-tertiary-fixed text-on-tertiary-fixed px-2 py-0.5 rounded-full mt-2 font-bold inline-block">Verified</span>
                    </div>
                </div>

                <div>
                    <h3 class="text-sm font-bold text-on-surface mb-4 ">Recently Acquired Knowledge</h3>
                    <div class="space-y-3">
                        <div class="flex items-center justify-between p-3 bg-surface hover:bg-surface-container-high rounded-lg transition-colors group cursor-pointer border border-transparent hover:border-outline-variant/20">
                            <div class="flex items-center gap-3">
                                <span class="material-symbols-outlined text-on-surface-variant group-hover:text-primary transition-colors text-[20px]">article</span>
                                <span class="text-xs font-medium text-on-surface">Quantum entanglement in room-temp semiconductors...</span>
                            </div>
                            <span class="text-[10px] text-on-surface-variant font-medium">2m ago</span>
                        </div>
                        <div class="flex items-center justify-between p-3 bg-surface hover:bg-surface-container-high rounded-lg transition-colors group cursor-pointer border border-transparent hover:border-outline-variant/20">
                            <div class="flex items-center gap-3">
                                <span class="material-symbols-outlined text-on-surface-variant group-hover:text-primary transition-colors text-[20px]">description</span>
                                <span class="text-xs font-medium text-on-surface">Technical documentation for Llama 3.2-1B quantization</span>
                            </div>
                            <span class="text-[10px] text-on-surface-variant font-medium">15m ago</span>
                        </div>
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
                            <p class="text-lg font-bold font-mono text-on-surface">14.2 GB <span class="text-xs font-medium text-on-surface-variant">/ 24 GB</span></p>
                        </div>
                        <div class="h-10 w-full bg-surface-container-high rounded-lg overflow-hidden flex gap-1 p-1">
                            <div class="h-full bg-primary rounded-md w-3/5 transition-all"></div>
                            <div class="h-full bg-primary-fixed rounded-md w-1/5 transition-all"></div>
                            <div class="h-full bg-surface-variant rounded-md flex-1"></div>
                        </div>
                    </div>
                    <div class="space-y-4">
                        <div class="flex justify-between items-end">
                            <p class="text-xs font-bold text-on-surface-variant uppercase tracking-widest">Epoch Progress</p>
                            <p class="text-lg font-bold font-mono text-on-surface">2 / 5 <span class="text-xs font-medium text-on-surface-variant">(44%)</span></p>
                        </div>
                        <div class="h-10 w-full bg-surface-container-high rounded-lg overflow-hidden p-1">
                            <div class="h-full bg-gradient-to-r from-primary to-primary-container rounded-md w-[44%] relative">
                                <div class="absolute inset-0 bg-white/10 flex items-center justify-end px-2">
                                    <div class="w-1 h-4 bg-white/40 rounded-full animate-pulse"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="flex items-center gap-4 bg-surface-container-low p-4 rounded-xl border border-outline-variant/10">
                    <div class="flex gap-2 shrink-0">
                        <button class="w-10 h-10 rounded-full bg-primary text-white flex items-center justify-center hover:scale-105 transition-transform active:scale-95 shadow-md shadow-primary/20">
                            <span class="material-symbols-outlined text-[20px]" style="font-variation-settings: 'FILL' 1;">play_arrow</span>
                        </button>
                        <button class="w-10 h-10 rounded-full bg-surface-container-lowest text-on-surface-variant border border-outline-variant/30 flex items-center justify-center hover:bg-surface-container-high transition-colors">
                            <span class="material-symbols-outlined text-[20px]">pause</span>
                        </button>
                        <button class="w-10 h-10 rounded-full bg-surface-container-lowest text-error border border-error/20 flex items-center justify-center hover:bg-error-container text-error transition-colors">
                            <span class="material-symbols-outlined text-[20px]">stop</span>
                        </button>
                    </div>
                    <div class="h-8 w-[1px] bg-outline-variant/30 mx-2"></div>
                    <div class="flex-1 font-mono text-[11px] text-on-surface-variant leading-relaxed">
                        <p>[SYSTEM] Weights saved at step 1400</p>
                        <p class="text-on-tertiary-container font-medium">[INFO] Training speed: 42.1 tokens/sec</p>
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
            <section class="bg-surface-container-lowest rounded-3xl p-8 border border-outline-variant/10 shadow-sm">
                <h2 class="text-sm font-bold text-on-surface uppercase tracking-widest mb-6 ">Distillation: Alignment</h2>
                <div class="flex items-center justify-between mb-8">
                    <div class="text-center w-20">
                        <div class="w-14 h-14 rounded-2xl bg-secondary-container flex items-center justify-center mx-auto mb-3 shadow-[0_4px_12px_rgba(209,226,243,0.5)]">
                            <span class="material-symbols-outlined text-secondary text-[24px]">school</span>
                        </div>
                        <p class="text-[11px] font-extrabold text-on-surface">GPT-4</p>
                        <p class="text-[9px] text-on-surface-variant font-medium uppercase tracking-wider mt-0.5">Teacher</p>
                    </div>
                    <div class="flex-1 px-4 relative">
                        <div class="h-[2px] w-full bg-surface-container-high rounded-full overflow-hidden">
                            <div class="h-full bg-gradient-to-r from-secondary-container to-primary-fixed w-[88%]"></div>
                        </div>
                        <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-surface-container-lowest border-2 border-primary w-12 h-12 rounded-full flex flex-col items-center justify-center shadow-sm">
                            <p class="text-xs font-extrabold text-primary leading-none">0.88</p>
                            <p class="text-[6px] text-primary uppercase font-bold mt-1 tracking-widest">Similar</p>
                        </div>
                    </div>
                    <div class="text-center w-20">
                        <div class="w-14 h-14 rounded-2xl bg-primary-fixed flex items-center justify-center mx-auto mb-3 shadow-[0_4px_12px_rgba(222,225,255,0.5)]">
                            <span class="material-symbols-outlined text-primary text-[24px]">person_search</span>
                        </div>
                        <p class="text-[11px] font-extrabold text-on-surface">Llama 3.2</p>
                        <p class="text-[9px] text-on-surface-variant font-medium uppercase tracking-wider mt-0.5">Student</p>
                    </div>
                </div>
                <div class="space-y-3 bg-surface-container-low p-4 rounded-xl border border-outline-variant/10">
                    <div class="flex justify-between items-center text-xs">
                        <span class="text-on-surface-variant font-medium text-[11px]">CoT Samples Quality</span>
                        <span class="font-bold text-on-tertiary-container text-[11px]">High (Excellent)</span>
                    </div>
                    <div class="h-2 w-full bg-surface-variant rounded-full overflow-hidden">
                        <div class="h-full bg-on-tertiary-container w-[92%] rounded-full"></div>
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
                        <button title="Toggle Strict Grounding AI" class="w-12 h-6 bg-primary rounded-full relative cursor-pointer ring-4 ring-primary-fixed transition-colors">
                            <div class="absolute right-1 top-1.5 w-3 h-3 bg-white rounded-full shadow-sm"></div>
                        </button>
                    </div>
                    
                    <!-- Sliders -->
                    <div class="space-y-6 px-1">
                        <div class="space-y-3">
                            <div class="flex justify-between text-[10px] font-bold uppercase tracking-widest">
                                <span class="text-on-surface-variant">Embedding Alignment</span>
                                <span class="text-primary font-mono bg-primary-fixed/50 px-2 py-0.5 rounded text-[10px]">0.96 Alpha</span>
                            </div>
                            <input class="w-full h-1.5 bg-surface-variant rounded-full appearance-none accent-primary cursor-pointer hover:accent-primary-container transition-colors" type="range" value="96" />
                        </div>
                        
                        <div class="space-y-3">
                            <div class="flex justify-between text-[10px] font-bold uppercase tracking-widest">
                                <span class="text-on-surface-variant">Context Depth (Top-K)</span>
                                <span class="text-primary font-mono bg-primary-fixed/50 px-2 py-0.5 rounded text-[10px]">k = 12</span>
                            </div>
                            <input class="w-full h-1.5 bg-surface-variant rounded-full appearance-none accent-primary cursor-pointer hover:accent-primary-container transition-colors" type="range" value="40" min="0" max="100" />
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
                            <button title="Toggle Internal Monologue" class="w-8 h-4 bg-outline-variant rounded-full relative">
                                <div class="absolute left-1 top-0.5 w-3 h-3 bg-white rounded-full"></div>
                            </button>
                        </div>
                        
                        <div class="flex items-end justify-between">
                            <div>
                                <p class="text-3xl font-extrabold text-on-tertiary-container leading-none ">94.2%</p>
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
    input[type=range]::-webkit-slider-runnable-track {
        width: 100%;
        height: 6px;
        cursor: pointer;
        background: var(--color-surface-variant);
        border-radius: 3px;
    }
</style>
    </div>
