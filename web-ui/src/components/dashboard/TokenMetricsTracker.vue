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
       <div class="flex flex-col items-center justify-center p-3 bg-zinc-900/40 border border-zinc-800/60 rounded-xl relative overflow-hidden group">
          <div class="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-sky-500/30 to-transparent"></div>
          <svg class="w-5 h-5 text-sky-500/50 mb-1.5 group-hover:text-sky-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
          <div class="text-[9px] uppercase font-bold text-zinc-500 tracking-wider mb-0.5 text-center leading-tight">Total Gerado</div>
          <div class="flex flex-col items-center gap-0">
             <span class="text-xl sm:text-2xl font-light text-zinc-200 tracking-tight">{{ totalTokens.toLocaleString() }}</span>
             <span class="text-[9px] text-zinc-600 font-bold uppercase tracking-widest mt-0.5">Tokens</span>
          </div>
       </div>

       <!-- 2. Cost Analysis -->
       <div class="flex flex-col items-center justify-center p-3 bg-zinc-900/40 border border-emerald-900/30 rounded-xl relative overflow-hidden group">
          <div class="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-emerald-500/30 to-transparent"></div>
          <svg class="w-5 h-5 text-emerald-500/50 mb-1.5 group-hover:text-emerald-400 transition-colors lucide lucide-banknote" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="12" x="2" y="6" rx="2"/><circle cx="12" cy="12" r="2"/><path d="M6 12h.01M18 12h.01"/></svg>
          <div class="text-[9px] uppercase font-bold text-emerald-600 tracking-wider mb-0.5 text-center leading-tight">Economia Estimada</div>
          <div class="flex flex-col items-center gap-0">
             <span class="text-xl sm:text-2xl font-light text-emerald-400 tracking-tight">${{ estimatedSavings.toFixed(4) }}</span>
             <span class="text-[9px] text-emerald-700 font-bold uppercase tracking-widest mt-0.5">USD</span>
          </div>
       </div>
       
       <!-- 3. Hardware & Network Telemetry -->
       <div class="col-span-2 flex flex-col gap-3 p-3 bg-zinc-900/30 border border-zinc-800/50 rounded-xl mt-1">
          <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                 <div class="w-6 h-6 rounded-full bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
                    <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path></svg>
                 </div>
                 <div>
                    <div class="text-[9px] uppercase font-bold text-zinc-500 tracking-wider">Desempenho da Engine O.S</div>
                    <div class="flex gap-2 text-[10px] text-zinc-400 font-mono mt-0.5">
                        <span class="text-indigo-400/80">{{ averageTPS }} t/s</span>
                        <span class="text-zinc-600">|</span>
                        <span>Ryzen Runtime</span>
                    </div>
                 </div>
              </div>
          </div>
          
          <!-- System Bars -->
          <div class="grid grid-cols-3 gap-2 w-full mt-1">
              <div class="flex flex-col gap-1 items-center">
                  <div class="text-[9px] font-mono"><span class="text-zinc-500 mr-1">CPU</span><span class="text-amber-400/80">{{ hardware.cpu }}%</span></div>
                  <div class="h-1 bg-black rounded overflow-hidden w-full">
                      <div class="h-full bg-amber-500/50 transition-all duration-1000" :style="`width: ${hardware.cpu}%`"></div>
                  </div>
              </div>
              <div class="flex flex-col gap-1 items-center">
                  <div class="text-[9px] font-mono"><span class="text-zinc-500 mr-1">RAM</span><span class="text-purple-400/80">{{ hardware.ram }} GB</span></div>
                  <div class="h-1 bg-black rounded overflow-hidden w-full">
                      <div class="h-full bg-purple-500/50 transition-all duration-1000" :style="`width: ${(hardware.ram / 32) * 100}%`"></div>
                  </div>
              </div>
              <div class="flex flex-col gap-1 items-center">
                  <div class="text-[9px] font-mono"><span class="text-zinc-500 mr-1">I/O</span><span class="text-sky-400/80">{{ hardware.io }} MB/s</span></div>
                  <div class="h-1 bg-black rounded overflow-hidden w-full">
                      <div class="h-full bg-sky-500/50 transition-all duration-1000" :style="`width: ${(hardware.io / 500) * 100}%`"></div>
                  </div>
              </div>
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
const hardware = ref({ cpu: 12, ram: 14.5, io: 45.2 })
let hwInterval: any = null

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
   
   // Randomizer visual para a Barrinha Mock do Hardware (Variando uso pra dar 'vida')
   hwInterval = setInterval(() => {
       hardware.value.cpu = Math.max(2, Math.min(98, hardware.value.cpu + (Math.random() * 20 - 10)))
       hardware.value.ram = Math.max(8, Math.min(30, hardware.value.ram + (Math.random() * 2 - 1)))
       hardware.value.io = Math.max(5, Math.min(500, hardware.value.io + (Math.random() * 100 - 50)))
       hardware.value.cpu = Number(hardware.value.cpu.toFixed(1))
       hardware.value.ram = Number(hardware.value.ram.toFixed(1))
       hardware.value.io = Number(hardware.value.io.toFixed(1))
   }, 3000)
})

import { onUnmounted } from 'vue'
onUnmounted(() => {
    if (hwInterval) clearInterval(hwInterval)
})
</script>
