<template>
  <div class="h-full w-full flex flex-col gap-4 p-4">
    <div class="flex justify-between items-center mb-2">
      <div>
        <h2 class="text-xl font-medium text-white tracking-tight">Project Board</h2>
        <p class="text-sm text-zinc-400 mt-1">Plan & Execute Tactical Tasks</p>
      </div>
      <button 
        @click="showNewTaskModal = true"
        class="bg-blue-600/20 hover:bg-blue-600/30 text-blue-400 border border-blue-500/30 px-3 py-1.5 rounded-md text-sm font-medium transition-colors flex items-center gap-2">
        <i class="i-lucide-plus"></i>
        New Task
      </button>
    </div>

    <!-- Kanban Columns -->
    <div class="flex-1 flex gap-4 overflow-x-auto pb-2">
      
      <div 
        v-for="col in columns" 
        :key="col.id" 
        class="flex-shrink-0 w-80 bg-black/40 border border-white/5 rounded-xl flex flex-col overflow-hidden"
        @dragover.prevent
        @drop="onDrop($event, col.id)">
        
        <!-- Column Header -->
        <div class="p-3 border-b border-white/5 flex justify-between items-center bg-white/[0.02]">
          <h3 class="text-sm font-medium text-zinc-300 flex items-center gap-2">
            <div :class="col.colorClass" class="w-2 h-2 rounded-full"></div>
            {{ col.title }}
          </h3>
          <span class="text-xs text-zinc-500 bg-white/5 px-2 py-0.5 rounded-full">
            {{ getTasksByStatus(col.id).length }}
          </span>
        </div>

        <!-- Task List -->
        <div class="p-3 flex-1 overflow-y-auto space-y-3">
          <div 
            v-for="task in getTasksByStatus(col.id)" 
            :key="task.id"
            draggable="true"
            @dragstart="onDragStart($event, task)"
            class="group bg-zinc-900 border border-white/10 rounded-lg p-3 cursor-grab active:cursor-grabbing hover:border-white/20 transition-all shadow-sm">
            <div class="flex justify-between items-start mb-2">
              <span 
                :class="{
                  'bg-red-500/10 text-red-500 border-red-500/20': task.priority === 'High',
                  'bg-yellow-500/10 text-yellow-500 border-yellow-500/20': task.priority === 'Medium',
                  'bg-blue-500/10 text-blue-500 border-blue-500/20': task.priority === 'Low'
                }"
                class="text-[10px] px-2 py-0.5 rounded border uppercase tracking-wider font-semibold">
                {{ task.priority }}
              </span>
              <button @click="deleteTask(task.id)" class="text-zinc-500 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity">
                <i class="i-lucide-trash-2 text-sm"></i>
              </button>
            </div>
            
            <h4 class="text-zinc-200 text-sm font-medium leading-snug">{{ task.title }}</h4>
            <p v-if="task.description" class="text-zinc-500 text-xs mt-2 line-clamp-2 leading-relaxed">
              {{ task.description }}
            </p>
            
            <div class="mt-3 flex items-center justify-between text-xs text-zinc-500">
              <div v-if="task.deadline" class="flex items-center gap-1.5 flex-1 w-0">
                <i class="i-lucide-calendar text-xs flex-shrink-0"></i>
                <span class="truncate">{{ task.deadline }}</span>
              </div>
            </div>
          </div>
          
          <!-- Empty State -->
          <div v-if="getTasksByStatus(col.id).length === 0" class="h-24 border-2 border-dashed border-white/5 rounded-lg flex items-center justify-center text-zinc-600 text-sm">
            Drop tasks here
          </div>
        </div>
      </div>

    </div>

    <!-- Modal de Nova Tarefa -->
    <Teleport to="body">
      <div v-if="showNewTaskModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
        <div class="bg-[#151518] border border-white/10 p-6 rounded-xl shadow-2xl w-full max-w-md flex flex-col gap-4 text-white" @click.stop>
          <div class="flex justify-between items-center mb-1">
             <h3 class="text-lg font-medium tracking-tight text-white flex items-center gap-2">
                <i class="i-lucide-check-square text-blue-400"></i>
                Nova Micro-Tarefa O.S
             </h3>
             <button @click="showNewTaskModal = false" class="text-zinc-500 hover:text-white"><i class="i-lucide-x text-lg"></i></button>
          </div>
          
          <div class="flex flex-col gap-3">
             <label class="flex flex-col gap-1.5 text-xs font-medium text-zinc-400">
               TÍTULO DA TAREFA
               <input v-model="newTaskForm.title" type="text" class="bg-black/50 border border-white/10 p-2.5 rounded-lg text-white text-sm focus:outline-none focus:border-blue-500/50 transition-colors" placeholder="Ex: Analisar dependência do Rust" @keyup.enter="handleCreateTask" autofocus>
             </label>
             
             <label class="flex flex-col gap-1.5 text-xs font-medium text-zinc-400">
               DESCRIÇÃO
               <textarea v-model="newTaskForm.description" rows="3" class="bg-black/50 border border-white/10 p-2.5 rounded-lg text-white text-sm focus:outline-none focus:border-blue-500/50 transition-colors resize-none" placeholder="O que exatamente precisa ser feito?"></textarea>
             </label>

             <div class="flex gap-4">
               <label class="flex flex-col gap-1.5 text-xs font-medium text-zinc-400 flex-1">
                 NÍVEL DE PRIORIDADE
                 <select v-model="newTaskForm.priority" class="bg-black/50 border border-white/10 p-2.5 rounded-lg text-white text-sm focus:outline-none focus:border-blue-500/50 appearance-none">
                   <option value="High">🔴 Alta (High)</option>
                   <option value="Medium">🟡 Média (Medium)</option>
                   <option value="Low">🔵 Baixa (Low)</option>
                 </select>
               </label>
               
               <label class="flex flex-col gap-1.5 text-xs font-medium text-zinc-400 flex-1">
                 ESTADO INICIAL
                 <select v-model="newTaskForm.status" class="bg-black/50 border border-white/10 p-2.5 rounded-lg text-white text-sm focus:outline-none focus:border-blue-500/50 appearance-none">
                   <option v-for="col in columns" :key="col.id" :value="col.id">{{ col.title }}</option>
                 </select>
               </label>
             </div>
             
             <label class="flex flex-col gap-1.5 text-xs font-medium text-zinc-400 mt-1">
               DEADLINE / PRAZO (Opcional)
               <input v-model="newTaskForm.deadline" type="date" class="bg-black/50 border border-white/10 p-2.5 rounded-lg text-white text-sm focus:outline-none focus:border-blue-500/50 [color-scheme:dark]">
             </label>
          </div>

          <div class="flex justify-end gap-2 mt-4">
            <button @click="showNewTaskModal = false" class="px-4 py-2 text-sm text-zinc-400 hover:text-white transition-colors">Cancelar</button>
            <button @click="handleCreateTask" class="px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium transition-colors border border-blue-500/20 shadow-[0_0_15px_rgba(37,99,235,0.2)]" :disabled="!newTaskForm.title.trim()">
               Criar Tarefa
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useTasksStore, type Task } from '../../stores/tasks'

const props = defineProps<{
  projectId: string
}>()

const tasksStore = useTasksStore()
const showNewTaskModal = ref(false)
const newTaskForm = ref({
  title: '',
  description: '',
  priority: 'Medium',
  status: 'TODO',
  deadline: '' // ISO Date string (YYYY-MM-DD)
})

const columns = [
  { id: 'TODO', title: 'To Do', colorClass: 'bg-zinc-500' },
  { id: 'DOING', title: 'In Progress', colorClass: 'bg-blue-500' },
  { id: 'BLOCKED', title: 'Blocked', colorClass: 'bg-red-500' },
  { id: 'DONE', title: 'Done', colorClass: 'bg-emerald-500' }
]

const handleCreateTask = async () => {
    if (!newTaskForm.value.title.trim()) return
    const maxOrder = Math.max(0, ...tasksStore.tasksByProject(props.projectId).map((t: any) => t.order_index || 0))
    
    await tasksStore.createTask(props.projectId, {
        title: newTaskForm.value.title,
        description: newTaskForm.value.description,
        priority: newTaskForm.value.priority,
        status: newTaskForm.value.status,
        order_index: maxOrder + 1,
        // Envia null se vazio, ou timestamp se preenchido.
        deadline: newTaskForm.value.deadline ? new Date(newTaskForm.value.deadline).toISOString() : undefined
    })
    
    // Reset form
    newTaskForm.value = { title: '', description: '', priority: 'Medium', status: 'TODO', deadline: '' }
    showNewTaskModal.value = false
}

const getTasksByStatus = (statusId: string) => {
  return tasksStore.tasksByProject(props.projectId)
    .filter(t => t.status === statusId)
    .sort((a, b) => a.order_index - b.order_index)
}

const onDragStart = (evt: DragEvent, task: Task) => {
  if (evt.dataTransfer) {
    evt.dataTransfer.dropEffect = 'move'
    evt.dataTransfer.effectAllowed = 'move'
    evt.dataTransfer.setData('taskId', task.id)
  }
}

const onDrop = async (evt: DragEvent, newStatus: string) => {
  const taskId = evt.dataTransfer?.getData('taskId')
  if (!taskId) return

  const task = tasksStore.tasks.find(t => t.id === taskId)
  if (task && task.status !== newStatus) {
    // Optimistic Update
    task.status = newStatus
    try {
      await tasksStore.updateTask(taskId, { status: newStatus })
    } catch (e) {
      console.error("Failed to update task status:", e)
      // Revert optimism if failed later
      await tasksStore.fetchProjectTasks(props.projectId)
    }
  }
}

const deleteTask = async (taskId: string) => {
  if (confirm("Delete this task?")) {
    await tasksStore.deleteTask(taskId)
  }
}

// Em um ambiente real, poderíamos chamar onMounted(() => tasksStore.fetchProjectTasks(props.projectId)) aqui.
// Mas se o componente pai (Dashboard) orquestrar isso, não precisamos.
</script>
