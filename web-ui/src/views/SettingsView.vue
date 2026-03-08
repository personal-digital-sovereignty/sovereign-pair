<template>
  <div class="p-6">
    <h2 class="text-2xl font-bold mb-4">Settings</h2>
    <div class="mb-4 flex items-center gap-3">
       <input type="checkbox" id="proxy-opencode" v-model="proxyEnabled" class="w-4 h-4 rounded bg-surface-800 border-surface-600 text-emerald-500 focus:ring-emerald-500">
       <label for="proxy-opencode" class="text-sm text-surface-200">Habilitar Proxy Local OpenCode via Sovereign Pair</label>
    </div>
    <div class="text-sm text-surface-400">
       <p v-if="proxyEnabled">O tráfego do OpenCode será interceptado e processado pela Inteligência Artificial do Sovereign Pair (Ollama Local ou Oracle Cloud).</p>
       <p v-else>O plugin OpenCode se conectará normalmente ao provedor externo (OpenAI) conforme configurado no VS Code.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'

const proxyEnabled = ref(false)

onMounted(() => {
   const saved = localStorage.getItem('sensus_opencode_proxy_enabled')
   if (saved) proxyEnabled.value = saved === 'true'
})

watch(proxyEnabled, (val) => {
   localStorage.setItem('sensus_opencode_proxy_enabled', String(val))
})
</script>
