<script lang="ts">
    import { projectState } from '$lib/projects.svelte';
    import { FolderKanban, Clock, Activity, FileText } from 'lucide-svelte';

    let totalProjects = $derived(projectState.projects.length);
    let activeProjects = $derived(projectState.projects.filter(p => !p.is_archived).length);
    
    let totalTasks = $derived(projectState.projects.reduce((acc, p) => acc + (p.tasks?.length || 0), 0));
    let avgTasksPerProject = $derived(totalProjects ? (totalTasks / totalProjects).toFixed(1) : '0');
    
    // Simulated metric for now
    let avgCycleTime = "2.4 dias"; 
</script>

<div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
    <div class="bg-white/80 dark:bg-[#12192b]/80 p-4 rounded-xl border border-blue-100 dark:border-blue-900/40 shadow-sm flex items-center gap-4 transition-colors">
        <div class="p-3 bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-lg transition-colors"><FolderKanban class="w-6 h-6" /></div>
        <div>
            <p class="text-[10px] text-slate-500 dark:text-slate-400 font-bold uppercase tracking-wider mb-0.5 transition-colors">Projetos Ativos</p>
            <p class="text-2xl font-black text-slate-800 dark:text-slate-200 transition-colors">{activeProjects} <span class="text-xs font-medium text-slate-400 dark:text-slate-500">/{totalProjects} total</span></p>
        </div>
    </div>
    <div class="bg-white/80 dark:bg-[#12192b]/80 p-4 rounded-xl border border-emerald-100 dark:border-emerald-900/40 shadow-sm flex items-center gap-4 transition-colors">
        <div class="p-3 bg-emerald-50 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 rounded-lg transition-colors"><Activity class="w-6 h-6" /></div>
        <div>
            <p class="text-[10px] text-slate-500 dark:text-slate-400 font-bold uppercase tracking-wider mb-0.5 transition-colors">Média Tarefas/Proj</p>
            <p class="text-2xl font-black text-slate-800 dark:text-slate-200 transition-colors">{avgTasksPerProject}</p>
        </div>
    </div>
    <div class="bg-white/80 dark:bg-[#12192b]/80 p-4 rounded-xl border border-amber-100 dark:border-amber-900/40 shadow-sm flex items-center gap-4 transition-colors">
        <div class="p-3 bg-amber-50 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400 rounded-lg transition-colors"><Clock class="w-6 h-6" /></div>
        <div>
            <p class="text-[10px] text-slate-500 dark:text-slate-400 font-bold uppercase tracking-wider mb-0.5 transition-colors">Lead Time (Ciclo Médio)</p>
            <p class="text-2xl font-black text-slate-800 dark:text-slate-200 transition-colors">{avgCycleTime}</p>
        </div>
    </div>
    <div class="bg-white/80 dark:bg-[#12192b]/80 p-4 rounded-xl border border-indigo-100 dark:border-indigo-900/40 shadow-sm flex items-center gap-4 transition-colors">
        <div class="p-3 bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 rounded-lg transition-colors"><FileText class="w-6 h-6" /></div>
        <div>
            <p class="text-[10px] text-slate-500 dark:text-slate-400 font-bold uppercase tracking-wider mb-0.5 transition-colors">Densidade de Anexos</p>
            <p class="text-2xl font-black text-slate-800 dark:text-slate-200 transition-colors">~0.8 <span class="text-xs font-medium text-slate-400 dark:text-slate-500">docs/proj</span></p>
        </div>
    </div>
</div>
