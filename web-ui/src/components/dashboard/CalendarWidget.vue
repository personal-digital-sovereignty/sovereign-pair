<template>
  <div class="bg-black/40 border border-white/5 rounded-xl flex flex-col h-full overflow-hidden">
    <div class="p-4 border-b border-white/5 bg-white/[0.02] flex justify-between items-center">
      <h3 class="text-white font-medium flex items-center gap-2">
        <i class="i-lucide-calendar text-blue-400"></i>
        Deadlines & Milestones
      </h3>
      <div class="text-xs text-zinc-500 font-mono">
        {{ currentMonth }}
      </div>
    </div>
    
    <div class="p-4 flex-1 overflow-y-auto space-y-4">
      <div v-if="loading" class="text-center py-4">
        <div class="animate-pulse flex space-x-4">
          <div class="flex-1 space-y-4 py-1">
            <div class="h-4 bg-white/5 rounded w-3/4"></div>
            <div class="h-4 bg-white/5 rounded"></div>
          </div>
        </div>
      </div>
      
      <div v-else-if="upcomingTasks.length === 0" class="flex flex-col items-center justify-center py-8 text-zinc-500">
        <i class="i-lucide-check-circle text-4xl mb-3 opacity-20"></i>
        <p class="text-sm">No upcoming deadlines.</p>
        <p class="text-xs opacity-60">You're all caught up!</p>
      </div>

      <div 
        v-else
        v-for="task in upcomingTasks" 
        :key="task.id"
        class="flex gap-4 items-start relative group">
        
        <!-- Timeline Line -->
        <div class="flex flex-col items-center pt-1 relative z-10">
          <div class="w-2.5 h-2.5 rounded-full ring-4 ring-black" :class="getUrgencyColor(task.deadline)"></div>
          <div class="w-[1px] h-full bg-white/10 absolute top-3 -z-10 group-last:hidden"></div>
        </div>
        
        <!-- Task Card -->
        <div class="flex-1 bg-white/5 border border-white/5 rounded-lg p-3 hover:border-white/10 transition-colors">
          <div class="flex justify-between items-start mb-1">
            <h4 class="text-sm font-medium text-zinc-200">{{ task.title }}</h4>
            <span class="text-[10px] font-mono whitespace-nowrap bg-black/30 px-1.5 py-0.5 rounded text-zinc-400">
              {{ formatDate(task.deadline) }}
            </span>
          </div>
          <p class="text-xs text-zinc-500 line-clamp-1">Task Details</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useTasksStore } from '../../stores/tasks'

const tasksStore = useTasksStore()
const loading = computed(() => tasksStore.loading)

const currentMonth = computed(() => {
  return new Intl.DateTimeFormat('en-US', { month: 'long', year: 'numeric' }).format(new Date())
})

const upcomingTasks = computed(() => {
  // Filter only tasks with deadlines, sort chronologically, and take top 10
  const tasksWithDeadlines = tasksStore.tasks.filter(t => t.deadline && t.status !== 'DONE')
  tasksWithDeadlines.sort((a, b) => new Date(a.deadline!).getTime() - new Date(b.deadline!).getTime())
  return tasksWithDeadlines.slice(0, 10)
})

const formatDate = (dateString?: string) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('en-US', { month: 'short', day: '2-digit' }).format(date)
}

const getUrgencyColor = (dateString?: string) => {
  if (!dateString) return 'bg-zinc-500'
  const diffTime = new Date(dateString).getTime() - new Date().getTime()
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays < 0) return 'bg-red-500' // Overdue
  if (diffDays <= 3) return 'bg-yellow-500' // Soon
  return 'bg-blue-500' // Plenty of time
}
</script>
