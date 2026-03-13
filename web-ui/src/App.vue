<template>
  <div v-if="authPhase === 'loading'" class="fixed inset-0 flex w-full bg-surface-900 items-center justify-center">
      <div class="text-white animate-pulse">Invocando o RAG...</div>
  </div>
  <Setup v-else-if="authPhase === 'setup'" @setup-complete="checkAuthStatus" />
  <Login v-else-if="authPhase === 'login'" @login-success="checkAuthStatus" />
  
  <!-- Render the active route when Authenticated -->
  <div v-else class="flex w-full h-screen bg-surface-900 text-surface-200 overflow-hidden font-sans">
    
    <!-- Global Wrapper for Sidebar + Content -->
    <div class="flex h-full w-full relative z-10">
      
      <!-- 1. Permanent Activity Bar (Always 64px) -->
      <nav class="w-[64px] bg-surface-900 border-r border-surface-700 flex flex-col h-full shrink-0 z-30 relative">
        <!-- Top Identity Logo (Toggles Context Panel) -->
        <div class="h-14 flex items-center justify-center border-b border-surface-700 shrink-0">
          <button @click="isSidebarOpen = !isSidebarOpen" class="text-emerald-500 hover:scale-110 transition-transform p-2 rounded-lg" :title="isSidebarOpen ? 'Ocultar Contexto' : 'Mostrar Contexto'">
             <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" class="shrink-0">
               <circle cx="12" cy="12" r="4.5" fill="currentColor"/>
               <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.5" stroke-opacity="0.3"/>
             </svg>
          </button>
        </div>

        <!-- Global Navigation Icons -->
        <div class="p-3 flex flex-col gap-2 shrink-0 items-center">
          <router-link to="/dashboard" @click="isSidebarOpen = true" class="flex items-center justify-center w-[42px] h-[42px] rounded-[14px] transition-all overflow-hidden" :class="[$route.path === '/dashboard' ? 'text-primary-400 bg-surface-800 shadow-[inset_3px_0_0_0_currentColor]' : 'text-surface-400 hover:text-surface-200 hover:bg-surface-800/50']" title="Sensus Dashboard">
            <Home class="w-6 h-6 shrink-0" />
          </router-link>
          
          <router-link to="/chat" @click="isSidebarOpen = true" class="flex items-center justify-center w-[42px] h-[42px] rounded-[14px] transition-all overflow-hidden" :class="[$route.path.startsWith('/chat') ? 'text-primary-400 bg-surface-800 shadow-[inset_3px_0_0_0_currentColor]' : 'text-surface-400 hover:text-surface-200 hover:bg-surface-800/50']" title="Sovereign Chat">
            <MessageCircle class="w-6 h-6 shrink-0" />
          </router-link>
          
          <router-link to="/vault" @click="isSidebarOpen = true" class="flex items-center justify-center w-[42px] h-[42px] rounded-[14px] transition-all overflow-hidden" :class="[$route.path.startsWith('/vault') ? 'text-primary-400 bg-surface-800 shadow-[inset_3px_0_0_0_currentColor]' : 'text-surface-400 hover:text-surface-200 hover:bg-surface-800/50']" title="Sensus Vault / Explorador">
            <Folder class="w-6 h-6 shrink-0" />
          </router-link>
          
          <router-link to="/projects" @click="isSidebarOpen = true" class="flex items-center justify-center w-[42px] h-[42px] rounded-[14px] transition-all overflow-hidden" :class="[$route.path.startsWith('/projects') ? 'text-primary-400 bg-surface-800 shadow-[inset_3px_0_0_0_currentColor]' : 'text-surface-400 hover:text-surface-200 hover:bg-surface-800/50']" title="Sensus Projects / Hub">
            <LayoutGrid class="w-6 h-6 shrink-0" />
          </router-link>
        </div>

        <div class="mt-auto p-3 flex flex-col gap-2 items-center border-t border-surface-700">
          <button @click="toggleRemoteIntegration" class="flex items-center justify-center w-[42px] h-[42px] rounded-[14px] transition-all overflow-hidden" :class="[clusterState.status === 'optimal' ? 'text-primary-400 bg-surface-800 shadow-[inset_3px_0_0_0_currentColor]' : 'text-surface-400 hover:text-amber-400 hover:bg-surface-800/50']" :title="clusterState.status === 'optimal' ? 'Cibrid Cloud: On (Desativar)' : 'Local-First: Off (Ativar Cloud)'">
            <Cloud v-if="clusterState.status === 'optimal'" class="w-6 h-6 shrink-0" />
            <CloudOff v-else class="w-6 h-6 shrink-0" />
          </button>
          
          <router-link to="/settings" class="flex items-center justify-center w-[42px] h-[42px] rounded-[14px] transition-all overflow-hidden" :class="[$route.path.startsWith('/settings') ? 'text-primary-400 bg-surface-800 shadow-[inset_3px_0_0_0_currentColor]' : 'text-surface-400 hover:text-surface-200 hover:bg-surface-800/50']" title="Configurações e Identidade">
            <Settings class="w-6 h-6 shrink-0" />
          </router-link>
        </div>
      </nav>

      <!-- 2. Sliding Context Panel (Trees, Chat History, Settings) -->
      <aside 
        class="bg-surface-800 flex flex-col h-full transition-all duration-300 relative z-20 shrink-0 overflow-x-hidden overflow-y-auto border-r border-surface-700"
        :class="isSidebarOpen ? '' : 'border-r-0 pointer-events-none opacity-0'"
        :style="{ width: isSidebarOpen ? `${sidebarWidth}px` : '0px' }"
      >
        <div class="flex flex-col h-full shrink-0" :style="{ width: `${sidebarWidth}px`, minWidth: `${sidebarWidth}px` }">
          
          <!-- Context Header -->
          <div class="h-14 px-4 flex items-center border-b border-surface-700 shrink-0">
            <span class="font-semibold text-surface-300 tracking-wide text-sm truncate">
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
      
      <!-- Resizer Edge Handle (Draggable Divider) -->
      <div 
        v-show="isSidebarOpen"
        class="w-[6px] h-full cursor-col-resize hover:bg-primary-500/50 active:bg-primary-500 transition-colors z-40 absolute top-0 bottom-0 flex-shrink-0"
        title="Redimensionar Painel O.S"
        :style="{ left: `calc(64px + ${sidebarWidth}px - 3px)` }"
        @mousedown="startResize"
      ></div>
      
      <!-- Main Area -->
      <main class="flex-1 flex flex-col overflow-hidden relative min-w-0 focus:outline-none bg-surface-900 shadow-[inset_10px_0_30px_rgba(0,0,0,0.5)]">
        
        <!-- Local-First Restricted Mode Banner -->
        <div v-if="clusterState.status === 'degraded' && showRestrictedBanner" class="flex-shrink-0 bg-amber-500/10 border-b border-amber-500/20 px-4 py-1.5 flex items-center justify-center text-amber-500 text-xs gap-2 select-none z-40 relative">
          <CloudOff class="w-3.5 h-3.5 shrink-0" />
          <span><strong>Modo Restrito (Local-First):</strong> Nó Remoto isolado ou desativado. Operando com {{ clusterState.active_agents ? clusterState.active_agents.join(', ') : 'The Mom, The Dad, The Nurse' }}.</span>
        </div>

        <router-view />
      </main>
      
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { Home, MessageCircle, Folder, LayoutGrid, Settings, Cloud, CloudOff } from 'lucide-vue-next'
import Setup from './views/Setup.vue'
import Login from './views/Login.vue'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || `http://${typeof window !== 'undefined' ? window.location.hostname : 'localhost'}:8000`
const authPhase = ref('loading')
const isSidebarOpen = ref(true)

// Sidebar Sliding Panel Resize Engine
const sidebarWidth = ref(260)
const minSidebarWidth = 200
const maxSidebarWidth = 600
const isResizing = ref(false)

const startResize = (e: MouseEvent) => {
  e.preventDefault()
  isResizing.value = true
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', stopResize)
  document.body.style.cursor = 'col-resize'
  document.body.style.userSelect = 'none'
}

const handleMouseMove = (e: MouseEvent) => {
  if (!isResizing.value) return
  const newWidth = e.clientX - 64 // Remove Activity Bar offset
  if (newWidth >= minSidebarWidth && newWidth <= maxSidebarWidth) {
    sidebarWidth.value = newWidth
  }
}

const stopResize = () => {
  isResizing.value = false
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', stopResize)
  document.body.style.cursor = ''
  document.body.style.userSelect = ''
  // Save State
  localStorage.setItem('sensus-sidebar-width', String(sidebarWidth.value))
}

onMounted(() => {
  const savedWidth = localStorage.getItem('sensus-sidebar-width')
  if (savedWidth) sidebarWidth.value = Number(savedWidth)
})

const clusterState = ref<{status: string, reason?: string, active_agents?: string[]}>({
  status: 'optimal',
  reason: '',
  active_agents: []
});
let healthInterval: any;

const showRestrictedBanner = ref(false);
let bannerTimeout: any;

watch(() => clusterState.value.status, (newStatus, oldStatus) => {
  if (newStatus === 'degraded' && oldStatus !== 'degraded') {
    showRestrictedBanner.value = true;
    if (bannerTimeout) clearTimeout(bannerTimeout);
    bannerTimeout = setTimeout(() => {
      showRestrictedBanner.value = false;
    }, 5000);
  }
}, { immediate: true });

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
        // Sincroniza Tema Visual O.S em Nível Mais Alto no Boot:
        const RUST_CORE_URL = import.meta.env.VITE_RUST_CORE_URL || `http://${typeof window !== 'undefined' ? window.location.hostname : 'localhost'}:8001`;
        fetch(`${RUST_CORE_URL}/v1/settings`, {
            headers: { 'Authorization': `Bearer ${token}` }
        }).then(r => r.json()).then(d => {
            if (d.theme) document.documentElement.setAttribute('data-theme', d.theme);
        }).catch(e => console.warn(e));
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
