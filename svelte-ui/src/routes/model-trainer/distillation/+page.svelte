<script lang="ts">
    import { goto } from '$app/navigation';

    let isSubmitting = false;

    async function runDistillation() {
        if(isSubmitting) return;
        isSubmitting = true;
        try {
            await fetch('http://localhost:38001/v1/trainer/distillation', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    teacher_model: 'GPT-4 (Omni)',
                    student_model: 'Llama-3.2-3B',
                    epochs: 3,
                    batch_size: 4
                })
            });
            goto('/model-trainer/unsloth');
        } catch(e) {
            console.error(e);
            isSubmitting = false;
        }
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
            <a href="/model-trainer/fine-tuning" class="px-4 py-2 text-on-surface-variant font-medium text-xs rounded-lg hover:bg-surface-container-high transition-colors">Fine-Tuning</a>
            <button class="px-4 py-2 bg-surface-container-lowest text-primary font-bold text-xs rounded-lg shadow-sm">Distillation</button>
            <a href="/model-trainer/reflection" class="px-4 py-2 text-on-surface-variant font-medium text-xs rounded-lg hover:bg-surface-container-high transition-colors">Reflection Lab</a>
            <a href="/model-trainer/rag-pipeline" class="px-4 py-2 text-on-surface-variant font-medium text-xs rounded-lg hover:bg-surface-container-high transition-colors">RAG Pipeline</a>
            <a href="/model-trainer/unsloth" class="px-4 py-2 text-on-surface-variant font-medium text-xs rounded-lg hover:bg-surface-container-high transition-colors">Unsloth Monitor</a>
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
                <button class="px-5 py-2.5 rounded-xl border border-outline-variant/30 text-on-surface-variant font-bold text-xs hover:bg-surface-container-high transition-colors">
                    Export Logs
                </button>
                <button disabled={isSubmitting} onclick={runDistillation} class="px-5 py-2.5 rounded-xl bg-gradient-to-br from-primary to-primary-container text-white font-bold text-xs shadow-md shadow-primary/20 active:scale-95 transition-transform flex items-center gap-2 cursor-pointer disabled:opacity-50">
                    <span class="material-symbols-outlined text-[18px]">model_training</span>
                    {isSubmitting ? 'Iniciando...' : 'Run Distillation'}
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
                                <div>
                                    <p class="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest mb-0.5">Professor Model</p>
                                    <h4 class=" font-extrabold text-on-surface text-lg">GPT-4 (Omni)</h4>
                                </div>
                            </div>
                            <div class="space-y-3">
                                <div class="flex justify-between text-xs">
                                    <span class="text-on-surface-variant font-medium">Reasoning Level</span>
                                    <span class="font-bold text-secondary">Tier 1 (Elite)</span>
                                </div>
                                <div class="w-full bg-surface-variant h-2 rounded-full overflow-hidden">
                                    <div class="bg-secondary h-full w-[95%] rounded-full"></div>
                                </div>
                            </div>
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
                                <div>
                                    <p class="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest mb-0.5">Student Model</p>
                                    <h4 class=" font-extrabold text-on-surface text-lg">Llama 3.2 3B</h4>
                                </div>
                            </div>
                            <div class="space-y-3">
                                <div class="flex justify-between text-xs">
                                    <span class="text-on-surface-variant font-medium">Learning Capacity</span>
                                    <span class="font-bold text-primary">Edge Optimized</span>
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
                        <span class="text-7xl  font-extrabold tracking-tighter">0.88</span>
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

            <!-- Quality Metrics -->
            <div class="col-span-12 md:col-span-6 xl:col-span-4 bg-surface-container-lowest rounded-3xl p-8 border border-outline-variant/10 shadow-sm">
                <h3 class=" font-bold text-lg mb-8 text-on-surface">CoT Quality Metrics</h3>
                <div class="space-y-8">
                    <div class="flex items-center gap-5">
                        <div class="w-14 h-14 rounded-full border-4 border-on-tertiary-container/30 border-t-on-tertiary-container flex items-center justify-center shrink-0">
                            <span class="text-sm font-bold text-on-tertiary-container">94%</span>
                        </div>
                        <div>
                            <h4 class="text-[13px] font-bold text-on-surface mb-0.5">Logic Fidelity</h4>
                            <p class="text-[11px] text-on-surface-variant leading-tight">Step-by-step reasoning accuracy match</p>
                        </div>
                    </div>
                    <div class="w-full h-[1px] bg-slate-100"></div>
                    <div class="flex items-center gap-5">
                        <div class="w-14 h-14 rounded-full border-4 border-primary/20 border-t-primary flex items-center justify-center shrink-0">
                            <span class="text-sm font-bold text-primary">82%</span>
                        </div>
                        <div>
                            <h4 class="text-[13px] font-bold text-on-surface mb-0.5">Syntactic Nuance</h4>
                            <p class="text-[11px] text-on-surface-variant leading-tight">Tone and structural mimicry scoring</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Generation Log -->
            <div class="col-span-12 xl:col-span-8 bg-surface-container-high rounded-3xl overflow-hidden flex flex-col border border-outline-variant/10 shadow-inner">
                <div class="px-6 py-4 bg-surface-container-highest border-b border-outline-variant/20 flex justify-between items-center">
                    <h3 class=" font-bold text-sm text-on-surface">Dataset Generation Log</h3>
                    <div class="flex items-center gap-2 px-3 py-1 bg-white/50 rounded-full border border-outline-variant/30 text-surface-container-highest shadow-sm">
                         <span class="w-2 h-2 rounded-full bg-on-tertiary-container animate-pulse shadow-[0_0_8px_rgba(79,175,110,0.8)]"></span>
                        <span class="text-[9px] font-bold text-on-surface-variant uppercase tracking-widest">Active Process</span>
                    </div>
                </div>
                <div class="p-6 font-mono text-[11px] overflow-y-auto h-[220px] bg-[#1a1b1e] text-slate-300 custom-scrollbar leading-relaxed">
                    <div class="space-y-1.5">
                        <p class="text-slate-500">[14:22:01] Initializing prompt template: "Scientific Reasoning v4"</p>
                        <p class="text-slate-500">[14:22:05] Professor generating 500 CoT samples...</p>
                        <p><span class="text-[#4faf6e] font-bold mr-2">SUCCESS</span> Prompt 0x44: "Explain Quantum Entanglement to a CEO"</p>
                        <p class="ml-6 text-slate-500 border-l border-slate-700 pl-2">-> logic_steps: 14 | tokens: 842 | entropy: 0.12</p>
                        <p><span class="text-[#4faf6e] font-bold mr-2">SUCCESS</span> Prompt 0x45: "Derivative strategy for market volatility"</p>
                        <p class="ml-6 text-slate-500 border-l border-slate-700 pl-2">-> logic_steps: 09 | tokens: 512 | entropy: 0.08</p>
                        <p class="text-[#8094ff] font-bold mt-3 mb-2">[14:23:44] Injecting latent constraints into Student weights...</p>
                        <p><span class="text-[#ffdad6] font-bold mr-2 bg-[#ba1a1a]/20 px-1 rounded">WARNING</span> Cluster 0x09 showed higher divergence (0.22)</p>
                        <p><span class="text-[#4faf6e] font-bold mr-2">SUCCESS</span> Prompt 0x46: "Summarize legal risk in tech acquisitions"</p>
                        <p class="ml-6 text-slate-500 border-l border-slate-700 pl-2">-> logic_steps: 11 | tokens: 620 | entropy: 0.05</p>
                        <div class="flex items-center gap-2 mt-3">
                            <div class="animate-pulse bg-slate-700 h-3 w-48 rounded"></div>
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
                                <p class="text-xs font-bold text-on-surface">1.2M Samples</p>
                            </div>
                        </div>
                        <div class="flex items-center gap-3">
                            <span class="material-symbols-outlined text-on-surface-variant text-[20px]">memory</span>
                            <div>
                                <p class="text-[9px] font-bold text-on-surface-variant uppercase tracking-wider">VRAM Usg</p>
                                <p class="text-xs font-bold text-on-surface">12.4 / 40 GB</p>
                            </div>
                        </div>
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
