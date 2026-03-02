<template>
  <div class="p-8 h-full overflow-y-auto w-full bg-[#111111] text-zinc-100 flex flex-col gap-6">
    <header class="flex flex-col gap-1 pb-4 border-b border-white/5">
      <h1 class="text-3xl font-light tracking-tight text-white flex items-center gap-3">
        <div class="px-2 py-1 bg-white/5 border border-white/10 rounded-md shadow-[inset_0_1px_0_rgba(255,255,255,0.1)]">
            <span class="text-cyan-400">🗂️</span>
        </div>
        Virtual Projects Hub
      </h1>
      <p class="text-sm text-zinc-500 font-mono tracking-wider ml-1">WORKFLOW & TEMPLATE ORCHESTRATION</p>
    </header>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      
      <!-- Projetos Ativos -->
      <div class="lg:col-span-2 flex flex-col gap-6">
        <section class="bg-[#151518] border border-white/5 rounded-xl p-5 shadow-2xl backdrop-blur-sm">
            <div class="flex items-center justify-between mb-4">
                <h2 class="text-lg font-medium text-cyan-400 flex items-center gap-2">
                    <span class="i-ph-folder-star-duotone text-xl"></span>
                    Agrupamentos Lógicos (Tags)
                </h2>
                <button class="bg-white/5 hover:bg-white/10 text-xs px-3 py-1.5 rounded-md border border-white/10 transition-colors flex items-center gap-1">
                    <span class="i-ph-plus-bold"></span> Novo Virtual Hub
                </button>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <!-- Project Card Mock -->
                <div class="group flex flex-col p-4 rounded-lg bg-black/20 border border-white/5 hover:border-cyan-500/30 transition-all cursor-pointer relative overflow-hidden">
                    <div class="absolute top-0 right-0 w-32 h-32 bg-cyan-500/5 rounded-full blur-2xl -translate-y-1/2 translate-x-1/2 pointer-events-none"></div>
                    <div class="flex items-center justify-between mb-2">
                        <h3 class="font-medium text-zinc-200 group-hover:text-white">Project Sensus</h3>
                        <span class="text-[10px] font-mono bg-cyan-500/10 text-cyan-400 px-2 rounded-full border border-cyan-500/20">8 Docs</span>
                    </div>
                    <p class="text-xs text-zinc-500 mb-3 line-clamp-2">Migração para arquitetura híbrida BGE-M3 e novo motor The Accountant.</p>
                    <div class="flex -space-x-2">
                        <div class="w-6 h-6 rounded-full bg-zinc-800 border-2 border-[#151518] flex items-center justify-center text-[10px] font-bold">JL</div>
                    </div>
                </div>

                <div class="group flex flex-col p-4 rounded-lg bg-black/20 border border-white/5 hover:border-cyan-500/30 transition-all cursor-pointer">
                    <div class="flex items-center justify-between mb-2">
                        <h3 class="font-medium text-zinc-200 group-hover:text-white">Finanças 2026</h3>
                        <span class="text-[10px] font-mono bg-cyan-500/10 text-cyan-400 px-2 rounded-full border border-cyan-500/20">3 Docs</span>
                    </div>
                    <p class="text-xs text-zinc-500 mb-3 line-clamp-2">Orçamentos e infraestruturas Oracle Cloud.</p>
                </div>
            </div>
        </section>
      </div>

      <!-- Templates (DoR / Specs) -->
      <div class="flex flex-col gap-6">
        <section class="bg-[#151518] border border-white/5 rounded-xl p-5 shadow-2xl backdrop-blur-sm flex-1 flex flex-col">
          <h2 class="text-lg font-medium text-purple-400 mb-4 flex items-center gap-2">
              <span class="i-ph-magic-wand-duotone text-xl"></span>
              Templates (DoR)
          </h2>
          
          <div class="space-y-3">
              <button class="w-full text-left p-3 flex flex-col gap-1 rounded-lg bg-white/5 border border-white/5 hover:bg-white/10 hover:border-purple-500/30 transition-all">
                  <strong class="text-sm font-medium text-zinc-200">Definição de Pronto (DoR)</strong>
                  <span class="text-xs text-zinc-500">Cria um Markdown estruturado para especificar novas features.</span>
              </button>

              <button class="w-full text-left p-3 flex flex-col gap-1 rounded-lg bg-white/5 border border-white/5 hover:bg-white/10 hover:border-purple-500/30 transition-all">
                  <strong class="text-sm font-medium text-zinc-200">Reunião Diária (Log)</strong>
                  <span class="text-xs text-zinc-500">Ata de reunião com meta-dados para o motor de busca.</span>
              </button>
              
              <button class="w-full text-left p-3 flex flex-col gap-1 rounded-lg bg-black text-center border border-dashed border-white/20 hover:border-white/40 transition-all text-zinc-400 hover:text-white">
                  <span class="text-sm font-medium flex items-center justify-center gap-2">
                      <span class="i-ph-plus"></span> Criar Novo Template
                  </span>
              </button>
          </div>
        </section>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
// Logic for handling template instantiation will be added in the upcoming execution phase
</script>
