<template>
  <div class="h-full flex flex-col bg-[#0f1012] border border-[#1a1c21] rounded-xl overflow-hidden shadow-[0_4px_16px_rgba(0,0,0,0.4)]">
    <!-- Header -->
    <div class="flex items-center justify-between px-4 py-3 border-b border-[#1a1c21] bg-[#141518]/80 backdrop-blur-sm">
      <div class="flex items-center gap-2">
         <div class="w-2 h-2 rounded-full bg-sky-500 shadow-[0_0_8px_rgba(14,165,233,0.6)]"></div>
         <h3 class="text-[12px] font-bold tracking-widest text-[#6c7585] uppercase">Telemetry Center</h3>
      </div>
      <div class="flex items-center gap-2">
         <span class="text-[10px] text-zinc-500 font-medium bg-black/30 px-2 py-0.5 rounded-sm border border-white/5 uppercase">Global</span>
      </div>
    </div>

    <!-- Content / Grid -->
    <div class="flex-1 p-5 grid grid-cols-2 gap-4">
       
       <!-- 1. Tokens Box -->
       <div class="flex flex-col items-center justify-center p-4 bg-zinc-900/40 border border-zinc-800/60 rounded-xl relative overflow-hidden group">
          <div class="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-sky-500/30 to-transparent"></div>
          <svg class="w-6 h-6 text-sky-500/50 mb-2 group-hover:text-sky-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
          <div class="text-[10px] uppercase font-bold text-zinc-500 tracking-wider mb-1">Total Gerado</div>
          <div class="text-3xl font-light text-zinc-200 tracking-tight flex items-baseline gap-1">
             {{ totalTokens.toLocaleString() }}
             <span class="text-xs text-zinc-500 font-bold">TOKENS</span>
          </div>
       </div>

       <!-- 2. Cost Analysis -->
       <div class="flex flex-col items-center justify-center p-4 bg-zinc-900/40 border border-emerald-900/30 rounded-xl relative overflow-hidden group">
          <div class="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-emerald-500/30 to-transparent"></div>
          <svg class="w-6 h-6 text-emerald-500/50 mb-2 group-hover:text-emerald-400 transition-colors lucide lucide-banknote" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="12" x="2" y="6" rx="2"/><circle cx="12" cy="12" r="2"/><path d="M6 12h.01M18 12h.01"/></svg>
          <div class="text-[10px] uppercase font-bold text-emerald-600 tracking-wider mb-1">Economia Estimada</div>
          <div class="text-3xl font-light text-emerald-400 tracking-tight flex items-baseline gap-1">
             ${{ estimatedSavings.toFixed(4) }}
             <span class="text-xs text-emerald-600 font-bold">USD</span>
          </div>
       </div>
       
       <!-- 3. T/s Average -->
       <div class="col-span-2 flex items-center justify-between p-4 bg-zinc-900/30 border border-zinc-800/50 rounded-xl mt-1">
          <div class="flex items-center gap-3">
             <div class="w-8 h-8 rounded-full bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v4"/><path d="M12 18v4"/><path d="M4.93 4.93l2.83 2.83"/><path d="M16.24 16.24l2.83 2.83"/><path d="M2 12h4"/><path d="M18 12h4"/><path d="M4.93 19.07l2.83-2.83"/><path d="M16.24 7.76l2.83-2.83"/></svg>
             </div>
             <div>
                <div class="text-[10px] uppercase font-bold text-zinc-500 tracking-wider">Desempenho da Frota Neural</div>
                <div class="text-xs text-zinc-400 font-mono mt-0.5">Local Ryzen Runtime</div>
             </div>
          </div>
          <div class="text-2xl font-bold text-zinc-300 font-mono tracking-tight">
             {{ averageTPS }} <span class="text-sm font-normal text-zinc-500">t/s</span>
          </div>
       </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const totalTokens = ref(0)
const estimatedSavings = ref(0.0)
const averageTPS = ref(0)

// O custo é estimado na API do Llama-3-70B/GPT-4o padrão (Aprox $0.015 / 1K output tokens)
const COST_PER_1K = 0.0150 
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const fetchTelemetry = async () => {
   try {
      const res = await fetch(`${API_BASE_URL}/v1/analytics/telemetry`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('sovereign_token')}` }
      })
      if (res.ok) {
          const data = await res.json()
          totalTokens.value = data.total_tokens || 12450 // Mocked default until Backend implemented
          averageTPS.value = data.avg_tps || 45
          estimatedSavings.value = (totalTokens.value / 1000) * COST_PER_1K
      } else {
         // Mock Mode for now
         totalTokens.value = 45912
         averageTPS.value = 52
         estimatedSavings.value = (totalTokens.value / 1000) * COST_PER_1K
      }
   } catch(e) {
      // Mock Data if API not ready
      totalTokens.value = 89431
      averageTPS.value = 65
      estimatedSavings.value = (totalTokens.value / 1000) * COST_PER_1K
   }
}

onMounted(() => {
   fetchTelemetry()
   // setInterval(fetchTelemetry, 30000) 
})
</script>
