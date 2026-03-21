<script lang="ts">
   import { FileText, Database } from 'lucide-svelte';
   import { globalState } from '$lib/state.svelte.js';
   import { untrack } from 'svelte';

   const API_BASE_URL = 'http://localhost:38001';

   async function fetchVaultFiles() {
       try {
           const token = localStorage.getItem('sovereign_token') || '';
           const ws_id = globalState.activeWorkspaceId || 'default';
           const res = await fetch(`${API_BASE_URL}/v1/vault/graph?workspace_id=${ws_id}`, { headers: { 'Authorization': `Bearer ${token}` } });
           
           if (res.ok) {
               const graphData = await res.json();
               globalState.vault.workspaceFiles = (graphData.nodes || []).filter((n: any) => n.type === 'file');
               if (globalState.vault.workspaceFiles.length > 0 && !globalState.vault.activeDocumentId) {
                   globalState.vault.activeDocumentId = globalState.vault.workspaceFiles[0].id;
               }
           }
       } catch(e) {
           console.error("Failed to sync Vault Graph:", e);
       }
   }

   function openDocument(id: string) {
       globalState.vault.activeDocumentId = id;
   }

   $effect(() => {
       const _trigger = globalState.activeWorkspaceId;
       untrack(() => {
           fetchVaultFiles();
       });
   });
</script>

<div class="flex-1 flex flex-col gap-1 p-2 w-full h-full">
    <div class="px-2 py-2 mb-2 border-b border-surface-700/50 flex flex-col gap-1 shrink-0">
        <h2 class="text-[10px] font-bold uppercase tracking-widest text-surface-500 flex items-center justify-between">
            Knowledge Vault
            <Database class="w-3 h-3 text-surface-600" />
        </h2>
    </div>
    
    <div class="flex-1 overflow-y-auto w-full flex flex-col gap-1 custom-scrollbar">
        {#each globalState.vault.workspaceFiles as file}
            <button 
                onclick={() => openDocument(file.id)}
                class="w-full text-left px-3 py-2 rounded-lg text-sm flex items-center gap-3 transition-colors {globalState.vault.activeDocumentId === file.id ? 'bg-primary-500/10 text-primary-400' : 'text-surface-400 hover:bg-surface-700 hover:text-surface-200'}"
            >
                <FileText class="w-4 h-4 shrink-0 {globalState.vault.activeDocumentId === file.id ? 'text-primary-500' : 'opacity-50'}" />
                <span class="truncate font-medium">{file.name}</span>
            </button>
        {/each}
        {#if globalState.vault.workspaceFiles.length === 0}
            <div class="px-3 py-4 text-xs text-surface-500 text-center italic border border-dashed border-surface-700/50 rounded-lg mx-2 mt-2">
                Workspace Vazio.
            </div>
        {/if}
    </div>
</div>
