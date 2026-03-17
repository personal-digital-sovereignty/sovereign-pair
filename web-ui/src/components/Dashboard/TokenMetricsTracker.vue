<template>
  <div class="h-full flex flex-col bg-surface-800 border border-surface-700 rounded-xl overflow-hidden shadow-[0_4px_16px_rgba(0,0,0,0.1)] dark:shadow-[0_4px_16px_rgba(0,0,0,0.4)]">
    <!-- Header -->
    <div class="flex items-center justify-between px-4 py-3 border-b border-surface-700 bg-surface-900/80 backdrop-blur-sm">
      <div class="flex items-center gap-2">
         <div class="w-2 h-2 rounded-full bg-sky-500 shadow-[0_0_8px_rgba(14,165,233,0.6)]"></div>
         <h3 class="text-[12px] font-bold tracking-widest text-surface-400 uppercase">Telemetry Center</h3>
      </div>
      <div class="flex items-center gap-2">
         <span class="text-[10px] text-surface-500 font-medium bg-surface-900/50 px-2 py-0.5 rounded-sm border border-surface-700 uppercase">Global</span>
      </div>
    </div>

    <!-- Content / Grid -->
    <div class="flex-1 p-5 grid grid-cols-2 gap-4">
       
       <!-- 1. Tokens Box -->
       <div class="flex flex-col items-center justify-center p-3 bg-surface-900/40 border border-surface-700/60 rounded-xl relative overflow-hidden group">
          <div class="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-sky-500/30 to-transparent"></div>
          <svg class="w-5 h-5 text-sky-500/50 mb-1.5 group-hover:text-sky-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
          <div class="text-[9px] uppercase font-bold text-surface-500 tracking-wider mb-0.5 text-center leading-tight">Total Gerado</div>
          <div class="flex flex-col items-center gap-0">
             <span class="text-xl sm:text-2xl font-light text-surface-100 tracking-tight">{{ totalTokens.toLocaleString() }}</span>
             <span class="text-[9px] text-surface-600 font-bold uppercase tracking-widest mt-0.5">Tokens</span>
          </div>
       </div>

       <!-- 2. Cost Analysis -->
       <div class="flex flex-col items-center justify-center p-3 bg-surface-900/40 border border-emerald-500/30 rounded-xl relative overflow-hidden group">
          <div class="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-emerald-500/30 to-transparent"></div>
          <svg class="w-5 h-5 text-emerald-500/50 mb-1.5 group-hover:text-emerald-400 transition-colors lucide lucide-banknote" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="12" x="2" y="6" rx="2"/><circle cx="12" cy="12" r="2"/><path d="M6 12h.01M18 12h.01"/></svg>
          <div class="text-[9px] uppercase font-bold text-emerald-600 tracking-wider mb-0.5 text-center leading-tight">Economia Estimada</div>
          <div class="flex flex-col items-center gap-0">
             <span class="text-xl sm:text-2xl font-light text-emerald-400 tracking-tight">${{ estimatedSavings.toFixed(4) }}</span>
             <span class="text-[9px] text-emerald-700 font-bold uppercase tracking-widest mt-0.5">USD</span>
          </div>
       </div>
       
       <!-- 3. Hardware & Network Telemetry -->
       <div class="col-span-2 flex flex-col gap-3 p-3 bg-surface-900/30 border border-surface-700/50 rounded-xl mt-1">
          <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                 <div class="w-6 h-6 rounded-full bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
                    <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path></svg>
                 </div>
                 <div>
                    <div class="text-[9px] uppercase font-bold text-surface-500 tracking-wider">Desempenho da Engine O.S</div>
                    <div class="flex gap-2 text-[10px] text-surface-400 font-mono mt-0.5">
                        <span class="text-indigo-400/80">{{ averageTPS }} t/s</span>
                        <span class="text-surface-600">|</span>
                        <span>{{ clusterName }}</span>
                    </div>
                 </div>
              </div>
          </div>
          
          <!-- System Bars -->
          <div class="grid grid-cols-3 gap-2 w-full mt-1">
              <div class="flex flex-col gap-1 items-center">
                  <div class="text-[9px] font-mono"><span class="text-surface-500 mr-1">CPU</span><span class="text-amber-500">{{ hardware.cpu }}%</span></div>
                  <div class="h-1 bg-surface-950 rounded overflow-hidden w-full">
                      <div class="h-full bg-amber-500/50 transition-all duration-1000" :style="`width: ${hardware.cpu}%`"></div>
                  </div>
              </div>
              <div class="flex flex-col gap-1 items-center">
                  <div class="text-[9px] font-mono"><span class="text-surface-500 mr-1">RAM</span><span class="text-purple-400/80">{{ hardware.ram }} GB</span></div>
                  <div class="h-1 bg-surface-950 rounded overflow-hidden w-full">
                      <div class="h-full bg-purple-500/50 transition-all duration-1000" :style="`width: ${(hardware.ram / 32) * 100}%`"></div>
                  </div>
              </div>
              <div class="flex flex-col gap-1 items-center">
                  <div class="text-[9px] font-mono"><span class="text-surface-500 mr-1">I/O</span><span class="text-sky-400/80">{{ hardware.io }} MB/s</span></div>
                  <div class="h-1 bg-surface-950 rounded overflow-hidden w-full">
                      <div class="h-full bg-sky-500/50 transition-all duration-1000" :style="`width: ${(hardware.io / 500) * 100}%`"></div>
                  </div>
              </div>
          </div>
       </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const totalTokens = ref(0)
const estimatedSavings = ref(0.0)
const averageTPS = ref(0)
const hardware = ref({ cpu: 0, ram: 0, io: 0 })
const clusterName = ref('Desconhecido')

// O custo é calculado dinamicamente no Backend Node (Rust) baseado no Provider/Model

const fetchTelemetry = async () => {
   try {
      const RUST_CORE_URL = import.meta.env.VITE_RUST_CORE_URL || `http://${typeof window !== 'undefined' ? window.location.hostname : 'localhost'}:38001`
      
      if (RUST_CORE_URL.includes('localhost') || RUST_CORE_URL.includes('127.0.0.1')) {
          clusterName.value = 'Ryzen Runtime'
      } else {
          clusterName.value = 'Oracle Cloud OCI'
      }

      const res = await fetch(`${RUST_CORE_URL}/v1/analytics/telemetry`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('sovereign_token') || ''}` }
      })
      
      if (res.ok) {
          const data = await res.json()
          totalTokens.value = data.total_tokens || 0 
          averageTPS.value = data.avg_tps || 0
          estimatedSavings.value = data.estimated_cost || 0

          if (data.hardware) {
              hardware.value.cpu = data.hardware.cpu || 0
              hardware.value.ram = data.hardware.ram || 0
              hardware.value.io = data.hardware.io || 0
          }

          if (data.cronos) {
              window.dispatchEvent(new CustomEvent('cronos-telemetry-update', { detail: data.cronos }))
          }
      }
   } catch(e) {
      console.warn("⚠️ Servidor Rust (Core) não alcançável. Mantendo último estado de Telemetria.")
   }
}

let fetchInterval: any = null

onMounted(() => {
   fetchTelemetry()
   
   // Polling Agressivo no Rust O.S (Rust resolve JSONs em nanosegundos com zero I/O Bound)
   fetchInterval = setInterval(fetchTelemetry, 2500) 
})

onUnmounted(() => {
    if (fetchInterval) clearInterval(fetchInterval)
})
</script>
