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
    <div class="bg-white/80 p-4 rounded-xl border border-blue-100 shadow-sm flex items-center gap-4">
        <div class="p-3 bg-blue-50 text-blue-600 rounded-lg"><FolderKanban class="w-6 h-6" /></div>
        <div>
            <p class="text-[10px] text-slate-500 font-bold uppercase tracking-wider mb-0.5">Projetos Ativos</p>
            <p class="text-2xl font-black text-slate-800">{activeProjects} <span class="text-xs font-medium text-slate-400">/{totalProjects} total</span></p>
        </div>
    </div>
    <div class="bg-white/80 p-4 rounded-xl border border-emerald-100 shadow-sm flex items-center gap-4">
        <div class="p-3 bg-emerald-50 text-emerald-600 rounded-lg"><Activity class="w-6 h-6" /></div>
        <div>
            <p class="text-[10px] text-slate-500 font-bold uppercase tracking-wider mb-0.5">Média Tarefas/Proj</p>
            <p class="text-2xl font-black text-slate-800">{avgTasksPerProject}</p>
        </div>
    </div>
    <div class="bg-white/80 p-4 rounded-xl border border-amber-100 shadow-sm flex items-center gap-4">
        <div class="p-3 bg-amber-50 text-amber-600 rounded-lg"><Clock class="w-6 h-6" /></div>
        <div>
            <p class="text-[10px] text-slate-500 font-bold uppercase tracking-wider mb-0.5">Lead Time (Ciclo Médio)</p>
            <p class="text-2xl font-black text-slate-800">{avgCycleTime}</p>
        </div>
    </div>
    <div class="bg-white/80 p-4 rounded-xl border border-indigo-100 shadow-sm flex items-center gap-4">
        <div class="p-3 bg-indigo-50 text-indigo-600 rounded-lg"><FileText class="w-6 h-6" /></div>
        <div>
            <p class="text-[10px] text-slate-500 font-bold uppercase tracking-wider mb-0.5">Densidade de Anexos</p>
            <p class="text-2xl font-black text-slate-800">~0.8 <span class="text-xs font-medium text-slate-400">docs/proj</span></p>
        </div>
    </div>
</div>
