<script lang="ts">
   import BlockEditor from '$lib/components/BlockEditor.svelte';
   import { FileText, Database } from 'lucide-svelte';
   import { globalState } from '$lib/state.svelte.ts';

   let activeDocumentId = $state('');
   let sidebarWidth = $state(280);

   let workspaceFiles = $state<any[]>([]);

   const API_BASE_URL = 'http://localhost:38001';

   async function fetchVaultFiles() {
       try {
           const token = localStorage.getItem('sovereign_token') || '';
           const ws_id = globalState.activeWorkspaceId || 'default';
           const res = await fetch(`${API_BASE_URL}/v1/vault/graph?workspace_id=${ws_id}`, { headers: { 'Authorization': `Bearer ${token}` } });
           
           if (res.ok) {
               const graphData = await res.json();
               // Apenas filtra nós to tipo arquivo para mostrar na lista lateral
               workspaceFiles = (graphData.nodes || []).filter((n: any) => n.type === 'file');
               if (workspaceFiles.length > 0 && !activeDocumentId) {
                   activeDocumentId = workspaceFiles[0].id;
               }
           }
       } catch(e) {
           console.error("Vault UI: Failed to sync physical workspace documents from Rust Mesh", e);
       }
   }

   function openDocument(id: string) {
       activeDocumentId = id;
   }

   $effect(() => {
       const _trigger = globalState.activeWorkspaceId;
       fetchVaultFiles();
   });

</script>

<div class="flex w-full h-full overflow-hidden bg-surface-900 border-l border-surface-700">
   
   <!-- Vault Sidebar -->
   <aside class="flex flex-col h-full bg-surface-800 border-r border-surface-700 shrink-0" style="width: {sidebarWidth}px">
       <div class="p-4 border-b border-surface-700 flex items-center justify-between">
           <h2 class="text-xs font-bold uppercase tracking-widest text-surface-400">Knowledge Vault</h2>
           <Database class="w-4 h-4 text-surface-500" />
       </div>
       <div class="flex-1 overflow-y-auto p-2 flex flex-col gap-1">
           {#each workspaceFiles as file}
               <button 
                 onclick={() => openDocument(file.id)}
                 class="w-full text-left px-3 py-2 rounded-lg text-sm flex items-center gap-2 transition-colors {activeDocumentId === file.id ? 'bg-primary-500/10 text-primary-400' : 'text-surface-400 hover:bg-surface-700 hover:text-surface-200'}"
               >
                   <FileText class="w-4 h-4 shrink-0" />
                   <span class="truncate">{file.name}</span>
               </button>
           {/each}
           {#if workspaceFiles.length === 0}
               <div class="p-4 text-xs text-surface-500 text-center italic">
                   No documents found in Workspace.
               </div>
           {/if}
       </div>
   </aside>

   <!-- TipTap Editor Workspace with {#key} Block (The Render Glitch Slayer) -->
   <main class="flex-1 h-full relative bg-surface-900">
       {#if activeDocumentId}
           {#key activeDocumentId}
               <BlockEditor 
                   documentId={activeDocumentId} 
                   initialContent={`---\ntitle: ${activeDocumentId}\ntags: [sovereign, cybrid]\n---\n# ${activeDocumentId}\n\nStart writing your raw markdown here...`} 
                   onSave={(content: string) => {
                       console.log(`Saved ${activeDocumentId}:`, content);
                   }}
               />
           {/key}
       {/if}
   </main>

</div>
