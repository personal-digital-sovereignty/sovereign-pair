<template>
  <div class="p-8 h-full w-full bg-[#111111] text-zinc-100 flex flex-col gap-6 overflow-hidden">
    <header class="flex flex-col gap-1 pb-4 border-b border-white/5 flex-shrink-0">
      <h1 class="text-3xl font-light tracking-tight text-white flex items-center gap-3">
        <div class="px-2 py-1 bg-white/5 border border-white/10 rounded-md shadow-[inset_0_1px_0_rgba(255,255,255,0.1)]">
            <span class="text-cyan-400">⚡</span>
        </div>
        Sovereign "Plan & Execute" Hub
      </h1>
      <!-- Teleport the Projects list to global sidebar -->
      <Teleport to="#sidebar-context-area" v-if="isMounted">
          <div class="w-full h-full flex flex-col overflow-hidden p-3 gap-2">
              <div class="flex items-center justify-between mb-2 shrink-0 px-2 mt-2">
                  <h2 class="text-sm font-medium text-purple-400 flex items-center gap-2">
                      Iniciativas
                  </h2>
                  <button class="bg-white/5 hover:bg-white/10 px-2 py-1 rounded border border-white/10 text-xs text-white transition-colors" @click="createNewProject"><i class="i-lucide-plus"></i></button>
              </div>
              
              <div class="flex-1 overflow-y-auto custom-scroll space-y-2 px-1 pb-4">
                  <div 
                    v-for="project in projectsStore.projects" 
                    :key="project.id" 
                    @click="activeProjectId = project.id"
                    :class="{'bg-[#1C1C1E] border border-white/10 shadow-[inset_3px_0_0_0_#a855f7]': activeProjectId === project.id, 'border border-transparent hover:bg-white/5': activeProjectId !== project.id}"
                    class="p-2.5 rounded-lg cursor-pointer transition-all flex flex-col gap-1 relative group">
                      
                      <div class="flex justify-between items-start">
                         <h3 class="font-medium text-sm pr-12 truncate" :class="activeProjectId === project.id ? 'text-white' : 'text-zinc-300'">{{ project.name }}</h3>
                         
                         <div class="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity bg-black/60 rounded backdrop-blur flex items-center p-0.5 border border-white/10">
                             <button @click.stop="openEditProject(project)" class="p-1 hover:bg-white/10 rounded text-zinc-400 hover:text-white transition-colors flex items-center justify-center" title="Renomear Projeto"><i class="i-lucide-pencil text-[10px]"></i></button>
                             <button @click.stop="deleteProject(project)" class="p-1 hover:bg-red-500/20 rounded text-zinc-400 hover:text-red-400 transition-colors flex items-center justify-center" title="Excluir Projeto"><i class="i-lucide-trash-2 text-[10px]"></i></button>
                         </div>
                      </div>

                      <p v-if="project.purpose" class="text-[10px] text-zinc-500 line-clamp-1 truncate">{{ project.purpose }}</p>
                      <div class="flex items-center justify-between mt-1 pt-1 opacity-80">
                          <div class="flex-1 bg-black rounded-full h-1 mr-2"><div class="bg-purple-500 h-1 rounded-full transition-all duration-500" :style="{ width: `${project.progress_percent}%` }"></div></div>
                          <span class="text-[9px] text-zinc-500 font-mono">{{ project.progress_percent }}%</span>
                      </div>
                  </div>
                  <div v-if="projectsStore.loading" class="text-center text-zinc-500 text-xs py-4 flex flex-col items-center gap-2">
                     <i class="i-lucide-loader-2 animate-spin"></i> Sync...
                  </div>
              </div>
          </div>
      </Teleport>
      <p class="text-sm text-zinc-500 font-mono tracking-wider ml-1">ORQUESTRAÇÃO DESACOPLADA DE CONHECIMENTO & EXECUÇÃO</p>
    </header>

    <div class="flex-1 min-h-0 flex gap-6 overflow-hidden">
      
      <!-- 1. KANBAN (Main Engine) -->
      <section class="flex-1 bg-[#151518] border border-white/5 rounded-xl flex flex-col min-w-0 overflow-hidden relative">
          <div v-if="!activeProjectId" class="absolute inset-0 flex flex-col items-center justify-center text-zinc-500">
             <i class="i-lucide-layout-dashboard text-4xl mb-4 opacity-20"></i>
             <p>Selecione um Projeto para iniciar o The Hub</p>
          </div>
          <ProjectKanban v-else :projectId="activeProjectId" class="w-full h-full" />
      </section>

      <!-- 2. CALENDAR & LOGS (Sidebar Right) -->
      <section class="w-80 flex flex-col gap-6 flex-shrink-0 overflow-hidden">
          <div class="h-[45%]">
            <CalendarWidget />
          </div>
          <div class="flex-1 min-h-0">
            <ActivityLogFeed />
          </div>
      </section>

    </div>
    
    <!-- Modals Globais de Conflito -->
    <DiffModal 
      :isOpen="syncConflict.show" 
      :entityTitle="syncConflict.title" 
      :fileMtime="syncConflict.fileMtime" 
      :dbUpdate="syncConflict.dbUpdate"
      @resolve="resolveConflict"
      @close="syncConflict.show = false"
    />

    <!-- Gerenciador Modal de Projetos -->
    <Teleport to="body">
      <div v-if="showProjectModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
        <div class="bg-[#151518] border border-white/10 p-6 rounded-xl shadow-2xl w-full max-w-sm flex flex-col gap-4 text-white" @click.stop>
          <div class="flex justify-between items-center mb-1">
             <h3 class="text-lg font-medium tracking-tight text-white">{{ isEditingProject ? 'Editar Iniciativa' : 'Nova Iniciativa' }}</h3>
             <button @click="showProjectModal = false" class="text-zinc-500 hover:text-white"><i class="i-lucide-x text-lg"></i></button>
          </div>
          
          <div class="flex flex-col gap-3">
             <label class="flex flex-col gap-1.5 text-xs font-medium text-zinc-400">
               NOME DO PROJETO
               <input v-model="projectForm.name" type="text" class="bg-black/50 border border-white/10 p-2.5 rounded-lg text-white text-sm focus:outline-none focus:border-purple-500/50 transition-colors" placeholder="Ex: Sovereign Engine V2" @keyup.enter="saveProject" autofocus>
             </label>
             <label class="flex flex-col gap-1.5 text-xs font-medium text-zinc-400">
               OBJETIVO TÁTICO (Opcional)
               <input v-model="projectForm.purpose" type="text" class="bg-black/50 border border-white/10 p-2.5 rounded-lg text-white text-sm focus:outline-none focus:border-purple-500/50 transition-colors" placeholder="Ex: Reestruturar camada de backend" @keyup.enter="saveProject">
             </label>
          </div>

          <div class="flex justify-end gap-2 mt-4">
            <button @click="showProjectModal = false" class="px-4 py-2 text-sm text-zinc-400 hover:text-white transition-colors">Cancelar</button>
            <button @click="saveProject" class="px-5 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-lg text-sm font-medium transition-colors border border-purple-500/20 shadow-[0_0_15px_rgba(168,85,247,0.2)]" :disabled="!projectForm.name.trim()">
               {{ isEditingProject ? 'Atualizar' : 'Criar' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useProjectsStore } from '../stores/projects'
import { useTasksStore } from '../stores/tasks'
import axios from 'axios'

import ProjectKanban from '../components/projects/ProjectKanban.vue'
import CalendarWidget from '../components/dashboard/CalendarWidget.vue'
import ActivityLogFeed from '../components/dashboard/ActivityLogFeed.vue'
import DiffModal from '../components/projects/DiffModal.vue'

const projectsStore = useProjectsStore()
const tasksStore = useTasksStore()

const activeProjectId = ref<string | null>(null)
const isMounted = ref(false)

// Sync Conflict State
const syncConflict = ref({
  show: false,
  title: '',
  fileMtime: '',
  dbUpdate: '',
  entityId: '',
  entityType: ''
})

onMounted(async () => {
  isMounted.value = true
  await projectsStore.fetchProjects()
  if (projectsStore.projects.length > 0) {
    activeProjectId.value = projectsStore.projects[0]?.id || null
  }
})

// Auto-fetch tasks when active project changes & Check Sync Diff Flag
watch(activeProjectId, async (newVal) => {
  if (newVal) {
    await tasksStore.fetchProjectTasks(newVal)
    
    // Check Sync Status for this entity
    checkSyncStatus('project', newVal)
  }
})

const checkSyncStatus = async (type: string, id: string) => {
  try {
     const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
     const token = localStorage.getItem('sovereign_token')
     const headers = token ? { Authorization: `Bearer ${token}` } : {}
     
     const res = await axios.get(`${baseURL}/sync-status/${type}/${id}`, { headers })
     if (res.data.status === 'CONFLICT') {
         syncConflict.value = {
             show: true,
             title: type === 'project' ? (projectsStore.projects.find(p => p.id === id)?.name ?? id) : id,
             fileMtime: res.data.file_mtime,
             dbUpdate: res.data.db_update,
             entityId: id,
             entityType: type
         }
     }
  } catch (err) {
     console.error("Sync Engine check bypass:", err)
  }
}

const resolveConflict = async (strategy: string) => {
  // Logic to process strategy. If "DB_WINS" we force an update PUT to save physical file again.
  // If "MARKDOWN_WINS" we would call an endpoint to parsing .md logic into SQL.
  console.log("Resolving with strategy:", strategy)
}

// --- GERENCIAMENTO DE PROJETOS MODAL UI ---
const showProjectModal = ref(false)
const isEditingProject = ref(false)
const projectForm = ref({ id: '', name: '', purpose: '' })

const createNewProject = () => {
   isEditingProject.value = false
   projectForm.value = { id: '', name: '', purpose: '' }
   showProjectModal.value = true
}

const openEditProject = (project: any) => {
   isEditingProject.value = true
   projectForm.value = { id: project.id, name: project.name, purpose: project.purpose || '' }
   showProjectModal.value = true
}

const saveProject = async () => {
   if (!projectForm.value.name.trim()) return
   
   if (isEditingProject.value) {
       await projectsStore.updateProject(projectForm.value.id, {
           name: projectForm.value.name,
           purpose: projectForm.value.purpose
       })
   } else {
       const newProj = await projectsStore.createProject({
           name: projectForm.value.name,
           purpose: projectForm.value.purpose,
           traction_status: 'Ideation',
           energy_level: 'Med',
           progress_percent: 0,
       })
       if (newProj && newProj.id) {
           activeProjectId.value = newProj.id
       }
   }
   showProjectModal.value = false
}

const deleteProject = async (project: any) => {
   if (confirm(`Atenção! Você está prestes a excluir completamente a Iniciativa "${project.name}" e todas as suas tarefas. Tem certeza?`)) {
       await projectsStore.deleteProject(project.id)
       if (activeProjectId.value === project.id) {
           activeProjectId.value = projectsStore.projects.length > 0 ? projectsStore.projects[0]?.id || null : null
       }
   }
}
</script>

<style scoped>
.custom-scroll::-webkit-scrollbar { width: 4px; }
.custom-scroll::-webkit-scrollbar-track { background: transparent; }
.custom-scroll::-webkit-scrollbar-thumb { background-color: rgba(255,255,255,0.1); border-radius: 4px; }
.custom-scroll:hover::-webkit-scrollbar-thumb { background-color: rgba(255,255,255,0.2); }
</style>
