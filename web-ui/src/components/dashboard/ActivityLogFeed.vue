<template>
  <div class="bg-black/40 border border-white/5 rounded-xl flex flex-col h-full overflow-hidden">
    <div class="p-4 border-b border-white/5 bg-white/[0.02] flex justify-between items-center">
      <h3 class="text-white font-medium flex items-center gap-2">
        <i class="i-lucide-activity text-emerald-400"></i>
        System Activity Log
      </h3>
      <div class="flex items-center gap-2 text-xs text-zinc-500">
        <span class="relative flex h-2 w-2">
          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
          <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
        </span>
        Live Polling
      </div>
    </div>
    
    <div class="p-4 flex-1 overflow-y-auto space-y-0">
      <div v-if="loading && logs.length === 0" class="text-center py-4">
        <span class="text-zinc-500 text-sm">Loading telemetry...</span>
      </div>

      <div 
        v-for="(log, idx) in logs" 
        :key="log.id"
        class="flex gap-3 relative pb-4 last:pb-0">
        
        <!-- Vertical Line -->
        <div class="absolute left-1.5 top-5 bottom-0 w-[1px] bg-white/5" v-if="idx !== logs.length - 1"></div>
        
        <!-- Node Icon -->
        <div class="relative z-10 mt-1">
          <div class="w-3 h-3 rounded-full bg-zinc-800 border-2 border-zinc-600 flex items-center justify-center">
             <div class="w-1 h-1 rounded-full bg-zinc-400"></div>
          </div>
        </div>
        
        <!-- Log Content -->
        <div class="flex-1 min-w-0">
          <div class="flex justify-between items-baseline gap-2 mb-0.5">
            <span class="text-sm text-zinc-200 font-medium truncate">
              {{ formatActionType(log.action) }}
            </span>
            <span class="text-[10px] text-zinc-500 flex-shrink-0 font-mono">
              {{ formatTime(log.created_at) }}
            </span>
          </div>
          
          <div class="text-xs text-zinc-400 mt-0.5">
            <span class="font-medium text-indigo-400">{{ log.agent_name || 'System' }}</span>
            on
            <span class="uppercase tracking-wider font-mono text-[10px] bg-white/5 px-1 rounded border border-white/10">{{ log.entity_type }}</span>
          </div>

          <!-- Diff Payload -->
          <div v-if="log.details" class="mt-2 text-[10px] font-mono bg-black/60 border border-white/5 p-2 rounded text-zinc-500 overflow-x-auto">
            {{ formatDetails(log.details) }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'

interface ActivityLog {
  id: number
  agent_name: string
  action: string
  entity_type: string
  details: any
  created_at: string
}

const logs = ref<ActivityLog[]>([])
const loading = ref(false)
let pollingInterval: number | null = null

const fetchLogs = async () => {
  const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  const token = localStorage.getItem('sovereign_token')
  const headers = token ? { Authorization: `Bearer ${token}` } : {}
  
  try {
    const res = await axios.get(`${baseURL}/v1/activity-logs?limit=30`, { headers })
    logs.value = res.data
  } catch (error) {
    console.error("Failed to fetch activity logs", error)
  }
}

onMounted(() => {
  loading.value = true
  fetchLogs().finally(() => { loading.value = false })
  
  // Real-time Simulation (Fallback while SSE is not configured)
  pollingInterval = window.setInterval(fetchLogs, 10000)
})

onUnmounted(() => {
  if (pollingInterval) clearInterval(pollingInterval)
})

const formatTime = (isoString?: string) => {
  if (!isoString) return 'Just now'
  return new Intl.DateTimeFormat('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' }).format(new Date(isoString))
}

const formatActionType = (action: string) => {
  return action.replace(/_/g, ' ')
}

const formatDetails = (details: any) => {
  try {
    return JSON.stringify(details, null, 2)
  } catch {
    return String(details)
  }
}
</script>
