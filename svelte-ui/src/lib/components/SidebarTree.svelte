<script lang="ts">
import { API_BASE_URL } from '$lib/env_config';

   import { FileText, Database, Folder, FolderOpen } from 'lucide-svelte';
   import { globalState } from '$lib/state.svelte.js';
   import { untrack } from 'svelte';

   

   async function fetchVaultFiles() {
       try {
           const token = localStorage.getItem('sovereign_token') || '';
           const ws_id = globalState.activeWorkspaceId || 'default';
           const res = await fetch(`${API_BASE_URL}/v1/workspaces/${ws_id}/tree`, { headers: { 'Authorization': `Bearer ${token}` } });
           
           if (res.ok) {
               const treeNodes = await res.json();
               globalState.vault.workspaceFiles = treeNodes;
               
               // Optionally set the active document to a known file if none exists (skipping directories)
               if (!globalState.vault.activeDocumentId && treeNodes.length > 0) {
                   const firstRoot = treeNodes[0];
                   if (firstRoot.children && firstRoot.children.length > 0) {
                       const firstFile = firstRoot.children.find((c: any) => !c.is_dir);
                       if (firstFile) globalState.vault.activeDocumentId = firstFile.path;
                   }
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
    
    <div class="flex-1 overflow-y-auto w-full flex flex-col gap-1 custom-scrollbar px-1">
        {#snippet treeNode(node: any)}
            {#if node.is_dir}
                <details class="group" open={node.id === 'root'}>
                    <summary class="flex items-center gap-2 w-full text-left px-2 py-1.5 rounded-lg hover:bg-surface-700 text-surface-300 cursor-pointer list-none text-xs font-semibold select-none transition-colors mt-0.5">
                        <Folder class="w-3.5 h-3.5 text-amber-500/70 group-open:hidden" />
                        <FolderOpen class="w-3.5 h-3.5 text-amber-500 group-open:block hidden" />
                        {node.name}
                    </summary>
                    <div class="pl-2.5 ml-3 border-l-2 border-surface-700/50 flex flex-col gap-0.5 mt-0.5">
                        {#if node.children}
                            {#each node.children as child}
                                {@render treeNode(child)}
                            {/each}
                        {/if}
                    </div>
                </details>
            {:else}
                <button 
                    onclick={() => openDocument(node.path)}
                    class="w-full text-left px-2 py-1.5 rounded-lg text-[13px] flex items-center gap-2 transition-colors {globalState.vault.activeDocumentId === node.path ? 'bg-primary-500/10 text-primary-400' : 'text-surface-400 hover:bg-surface-700 hover:text-surface-100'}"
                >
                    <FileText class="w-3.5 h-3.5 shrink-0 {globalState.vault.activeDocumentId === node.path ? 'text-primary-500' : 'opacity-40'}" />
                    <span class="truncate font-medium">{node.name}</span>
                </button>
            {/if}
        {/snippet}

        {#each globalState.vault.workspaceFiles as rootNode}
            {@render treeNode(rootNode)}
        {/each}
        
        {#if globalState.vault.workspaceFiles.length === 0}
            <div class="px-3 py-4 text-xs text-surface-500 text-center italic border border-dashed border-surface-700/50 rounded-lg mx-2 mt-2">
                Workspace Vazio.
            </div>
        {/if}
    </div>
</div>
