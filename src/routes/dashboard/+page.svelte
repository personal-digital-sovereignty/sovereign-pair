<script lang="ts">
    import CognitiveGraph from '$lib/components/CognitiveGraph.svelte';
    import { Search, Play, Minus, Plus } from 'lucide-svelte';
</script>

<div class="h-full w-full flex flex-col pb-2">
  <div class="bg-white rounded-2xl shadow-sm border border-slate-100 flex-1 flex flex-col relative overflow-hidden h-full">
    <!-- Inner Header: Title and Search -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center p-6 shrink-0 z-10 gap-4">
      <h2 class="text-2xl font-semibold text-slate-800">Sovereign Cognitive Graph</h2>
      <div class="relative w-full sm:w-72">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-4 h-4" />
        <input class="w-full pl-9 pr-4 py-2 bg-white border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent placeholder-slate-400 shadow-sm" placeholder="Search Sovereign Network..." type="text"/>
      </div>
    </div>

    <!-- Graph Area -->
    <div class="flex-1 flex items-center justify-center relative min-h-0 bg-slate-50/50">
      <CognitiveGraph />
    </div>

    <!-- Bottom Controls Bar -->
    <div class="absolute bottom-0 left-0 right-0 p-6 bg-gradient-to-t from-white via-white/80 to-transparent flex flex-col sm:flex-row justify-between items-end z-10 pointer-events-none gap-4">
      <!-- Data Flow History Slider -->
      <div class="flex-1 w-full max-w-2xl flex items-center gap-4 pointer-events-auto bg-white/80 backdrop-blur-sm p-3 rounded-xl border border-slate-100 shadow-sm">
        <button class="w-8 h-8 flex items-center justify-center rounded-full border border-slate-200 text-slate-500 hover:bg-slate-50 hover:text-indigo-500 transition-colors">
          <Play class="w-4 h-4 ml-0.5" />
        </button>
        <div class="flex-1 flex flex-col gap-1 mt-1">
          <input class="w-full" max="100" min="0" type="range" value="45"/>
          <span class="text-[10px] text-slate-500 font-medium">Data Flow History</span>
        </div>
      </div>
      
      <!-- Graph Depth Controls -->
      <div class="flex items-center gap-3 pointer-events-auto bg-white/80 backdrop-blur-sm p-3 rounded-xl border border-slate-100 shadow-sm">
        <button class="w-6 h-6 flex items-center justify-center rounded-full border border-slate-200 text-slate-500 hover:bg-slate-50 transition-colors">
          <Minus class="w-3 h-3" />
        </button>
        <div class="w-32 flex flex-col items-center gap-1 mt-1">
          <input class="w-full" max="100" min="0" type="range" value="80"/>
          <span class="text-[10px] text-slate-500 font-medium">Graph Depth</span>
        </div>
        <button class="w-6 h-6 flex items-center justify-center rounded-full border border-slate-200 text-slate-500 hover:bg-slate-50 transition-colors">
          <Plus class="w-3 h-3" />
        </button>
      </div>
    </div>
  </div>
</div>
