<template>
  <div v-if="authPhase === 'loading'" class="fixed inset-0 flex w-full bg-surface-900 items-center justify-center">
      <div class="text-white animate-pulse">Invocando o RAG...</div>
  </div>
  <Setup v-else-if="authPhase === 'setup'" @setup-complete="checkAuthStatus" />
  <Login v-else-if="authPhase === 'login'" @login-success="checkAuthStatus" />
  
  <!-- Render the active route when Authenticated -->
  <div v-else class="flex w-full h-screen bg-[#0E0E10] text-[#E0E0E0] overflow-hidden font-sans">
    
    <!-- Global Wrapper for Sidebar + Content -->
    <div class="flex h-full w-full relative z-10">
      
      <!-- 1. Permanent Activity Bar (Always 64px) -->
      <nav class="w-[64px] bg-[#0E0E10] border-r border-[#222222] flex flex-col h-full shrink-0 z-30 relative">
        <!-- Top Identity Logo (Toggles Context Panel) -->
        <div class="h-14 flex items-center justify-center border-b border-[#222222] shrink-0">
          <button @click="isSidebarOpen = !isSidebarOpen" class="text-emerald-500 hover:scale-110 transition-transform p-2 rounded-lg" :title="isSidebarOpen ? 'Ocultar Contexto' : 'Mostrar Contexto'">
             <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" class="shrink-0">
               <circle cx="12" cy="12" r="4.5" fill="currentColor"/>
               <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.5" stroke-opacity="0.3"/>
             </svg>
          </button>
        </div>

        <!-- Global Navigation Icons -->
        <div class="p-3 flex flex-col gap-2 shrink-0 items-center">
          <router-link to="/dashboard" @click="isSidebarOpen = true" class="flex items-center justify-center w-[42px] h-[42px] rounded-[14px] transition-all overflow-hidden" :class="[$route.path === '/dashboard' ? 'text-emerald-400 bg-[#151517] shadow-[inset_3px_0_0_0_#34d399,inset_0_0_15px_0_rgba(52,211,153,0.1)]' : 'text-zinc-500 hover:text-zinc-300 hover:bg-white/5']" title="Sensus Dashboard">
            <Home class="w-6 h-6 shrink-0" />
          </router-link>
          
          <router-link to="/chat" @click="isSidebarOpen = true" class="flex items-center justify-center w-[42px] h-[42px] rounded-[14px] transition-all overflow-hidden" :class="[$route.path.startsWith('/chat') ? 'text-purple-400 bg-[#151517] shadow-[inset_3px_0_0_0_#a855f7,inset_0_0_15px_0_rgba(168,85,247,0.1)]' : 'text-zinc-500 hover:text-zinc-300 hover:bg-white/5']" title="Sovereign Chat">
            <MessageCircle class="w-6 h-6 shrink-0" />
          </router-link>
          
          <router-link to="/vault" @click="isSidebarOpen = true" class="flex items-center justify-center w-[42px] h-[42px] rounded-[14px] transition-all overflow-hidden" :class="[$route.path.startsWith('/vault') ? 'text-cyan-400 bg-[#151517] shadow-[inset_3px_0_0_0_#22d3ee,inset_0_0_15px_0_rgba(34,211,238,0.1)]' : 'text-zinc-500 hover:text-zinc-300 hover:bg-white/5']" title="Sensus Vault / Explorador">
            <Folder class="w-6 h-6 shrink-0" />
          </router-link>
          
          <router-link to="/projects" @click="isSidebarOpen = true" class="flex items-center justify-center w-[42px] h-[42px] rounded-[14px] transition-all overflow-hidden" :class="[$route.path.startsWith('/projects') ? 'text-blue-400 bg-[#151517] shadow-[inset_3px_0_0_0_#3b82f6,inset_0_0_15px_0_rgba(59,130,246,0.1)]' : 'text-zinc-500 hover:text-zinc-300 hover:bg-white/5']" title="Sensus Projects / Hub">
            <LayoutGrid class="w-6 h-6 shrink-0" />
          </router-link>
        </div>

        <div class="mt-auto p-3 flex flex-col gap-2 items-center border-t border-[#222222]">
          <button @click="toggleRemoteIntegration" class="flex items-center justify-center w-[42px] h-[42px] rounded-[14px] transition-all overflow-hidden" :class="[clusterState.status === 'optimal' ? 'text-sky-400 bg-[#151517] shadow-[inset_3px_0_0_0_#38bdf8,inset_0_0_15px_0_rgba(56,189,248,0.1)]' : 'text-zinc-500 hover:text-amber-400 hover:bg-white/5']" :title="clusterState.status === 'optimal' ? 'Cibrid Cloud: On (Desativar)' : 'Local-First: Off (Ativar Cloud)'">
            <Cloud v-if="clusterState.status === 'optimal'" class="w-6 h-6 shrink-0" />
            <CloudOff v-else class="w-6 h-6 shrink-0" />
          </button>
          
          <router-link to="/settings" class="flex items-center justify-center w-[42px] h-[42px] rounded-[14px] transition-all overflow-hidden" :class="[$route.path.startsWith('/settings') ? 'text-slate-300 bg-[#151517] shadow-[inset_3px_0_0_0_#cbd5e1,inset_0_0_15px_0_rgba(203,213,225,0.1)]' : 'text-zinc-500 hover:text-zinc-300 hover:bg-white/5']" title="Configurações e Identidade">
            <Settings class="w-6 h-6 shrink-0" />
          </router-link>
        </div>
      </nav>

      <!-- 2. Sliding Context Panel (Trees, Chat History, Settings) -->
      <aside 
        class="bg-[#121214] flex flex-col h-full transition-all duration-300 relative z-20 shrink-0 overflow-x-hidden overflow-y-auto border-r border-[#222222]"
        :class="isSidebarOpen ? 'w-[260px]' : 'w-0 border-r-0 pointer-events-none opacity-0'"
      >
        <div class="min-w-[260px] w-[260px] flex flex-col h-full shrink-0">
          
          <!-- Context Header -->
          <div class="h-14 px-4 flex items-center border-b border-[#222222] shrink-0">
            <span class="font-semibold text-zinc-300 tracking-wide text-sm truncate">
              <!-- Dynamic Title based on Route -->
              {{ $route.path === '/dashboard' ? 'Overview' : 
                 $route.path.startsWith('/chat') ? 'Conversas Recentes' : 
                 $route.path.startsWith('/vault') ? 'Explorer' : 
                 $route.path.startsWith('/projects') ? 'Projetos' :
                 $route.path === '/settings' ? 'Configurações' : 'Contexto' 
              }}
            </span>
          </div>

          <!-- Dynamic Context Area -->
          <div id="sidebar-context-area" class="flex-1 w-full overflow-hidden flex flex-col relative min-h-0">
             <!-- Inject Vault Tree if in Vault -->
             <SidebarTree v-show="$route.path.startsWith('/vault')" class="w-full h-full" />
             
             <!-- Teleport target for Chat History -->
             <!-- Teleport target for Settings Layout -->
             <!-- Placeholder for Dashboard overview / Hub -->
             <div v-if="$route.path === '/dashboard'" class="p-4 text-xs text-zinc-500 flex flex-col gap-2">
                 <p>Sensus System Active.</p>
                 <p>All nodes responding.</p>
             </div>
          </div>
          
        </div>
      </aside>
      
      <!-- Main Area -->
      <main class="flex-1 flex flex-col overflow-hidden relative min-w-0 focus:outline-none bg-[#0E0E10] shadow-[inset_10px_0_30px_rgba(0,0,0,0.5)]">
        
        <!-- Local-First Restricted Mode Banner -->
        <div v-if="clusterState.status === 'degraded'" class="flex-shrink-0 bg-amber-500/10 border-b border-amber-500/20 px-4 py-1.5 flex items-center justify-center text-amber-500 text-xs gap-2 select-none z-40 relative">
          <CloudOff class="w-3.5 h-3.5 shrink-0" />
          <span><strong>Modo Restrito (Local-First):</strong> Nó Remoto isolado ou desativado. Operando com {{ clusterState.active_agents ? clusterState.active_agents.join(', ') : 'The Mom, The Dad, The Nurse' }}.</span>
        </div>

        <router-view />
      </main>
      
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { Home, MessageCircle, Folder, LayoutGrid, Settings, Cloud, CloudOff } from 'lucide-vue-next'
import Setup from './views/Setup.vue'
import Login from './views/Login.vue'
import SidebarTree from './components/Vault/SidebarTree.vue'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const authPhase = ref('loading')
const isSidebarOpen = ref(true)

const clusterState = ref<{status: string, reason?: string, active_agents?: string[]}>({
  status: 'optimal',
  reason: '',
  active_agents: []
});
let healthInterval: any;

const checkClusterHealth = async () => {
  if (authPhase.value !== 'authenticated') return;
  try {
    const res = await fetch(`${API_BASE_URL}/v1/health/cluster`, {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('sovereign_token')}` }
    });
    if (res.ok) {
      clusterState.value = await res.json();
    } else if (res.status === 401) {
      console.warn("Sovereign Token Expirado ou Inválido. Deslogando.");
      localStorage.removeItem('sovereign_token');
      authPhase.value = 'login';
      if (healthInterval) clearInterval(healthInterval);
    } else {
      clusterState.value = { status: 'degraded', reason: 'backend_down', active_agents: ['The Mom', 'The Dad', 'The Nurse'] };
    }
  } catch(e) {
    clusterState.value = { status: 'degraded', reason: 'offline', active_agents: ['The Mom', 'The Dad', 'The Nurse'] };
  }
}

const toggleRemoteIntegration = async () => {
  try {
    const res = await fetch(`${API_BASE_URL}/v1/settings/remote-toggle`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('sovereign_token')}` }
    });
    if (res.ok) {
       checkClusterHealth();
    }
  } catch (e) {
    console.error(e);
  }
}

const checkAuthStatus = async () => {
  try {
    const res = await fetch(`${API_BASE_URL}/v1/auth/status`)
    if (!res.ok) {
        // Se a rota falhar no Backend Rust (404), habilitamos o bypass Air-Gapped:
        authPhase.value = 'authenticated'
        checkClusterHealth();
        return;
    }
    const data = await res.json()
    if (!data.is_setup) {
      authPhase.value = 'setup'
    } else {
      const token = localStorage.getItem('sovereign_token')
      if (!token) {
        authPhase.value = 'login'
      } else {
        authPhase.value = 'authenticated'
        checkClusterHealth();
      }
    }
  } catch(e) {
    console.error("Sovereign Auth Network Offline -> Forcing Air-Gapped Mode.", e)
    // Se o Engine O.S sumir, destravamos a UI do 'Invocando o RAG' pelo menos.
    authPhase.value = 'authenticated'
  }
}

onMounted(() => {
  checkAuthStatus().then(() => {
     healthInterval = setInterval(checkClusterHealth, 30000);
  });
})

onUnmounted(() => {
  if (healthInterval) clearInterval(healthInterval);
})
</script>
