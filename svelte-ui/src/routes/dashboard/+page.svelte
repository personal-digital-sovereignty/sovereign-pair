<script lang="ts">
    import { Search, Activity, Cpu, Database, Network } from 'lucide-svelte';
</script>

<div class="h-full w-full flex flex-col pb-2">
  <div class="bg-white rounded-2xl shadow-sm border border-slate-100 flex-1 flex flex-col relative overflow-hidden h-full p-8">
    <div class="flex items-center gap-3 mb-6">
        <div class="bg-indigo-600/10 p-3 rounded-xl">
            <Activity class="w-6 h-6 text-indigo-600" />
        </div>
        <h2 class="text-2xl font-bold text-slate-800 tracking-tight">System Overview</h2>
    </div>

    <!-- Dashboard Widgets Skeleton -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="bg-slate-50 border border-slate-100 rounded-2xl p-6 flex flex-col">
            <h3 class="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-2">Vault Size</h3>
            <span class="text-3xl font-bold text-slate-800">12.4 GB</span>
        </div>
        <div class="bg-slate-50 border border-slate-100 rounded-2xl p-6 flex flex-col">
            <h3 class="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-2">Active Models</h3>
            <span class="text-3xl font-bold text-slate-800">2</span>
        </div>
        <div class="bg-slate-50 border border-slate-100 rounded-2xl p-6 flex flex-col">
            <h3 class="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-2">Network Nodes</h3>
            <span class="text-3xl font-bold text-slate-800">142</span>
        </div>
    </div>

    <div class="mt-8 flex-1 bg-slate-50 border border-slate-100 rounded-2xl border-dashed flex flex-col items-center justify-center text-slate-400">
        <Database class="w-12 h-12 mb-4 text-slate-300" />
        <span class="font-medium text-lg text-slate-500">Dashboard Metrics Pending</span>
        <span class="text-sm max-w-sm text-center mt-2">Os widgets analíticos serão montados aqui na próxima fase do projeto. O Cognitive Graph agora reside nos System Modules da barra lateral.</span>
    </div>
  </div>
</div>
