<script lang="ts">
   import BlockEditor from '$lib/components/BlockEditor.svelte';
   import { FileText, Database } from 'lucide-svelte';

   let activeDocumentId = $state('sovereign_manifesto.md');
   let sidebarWidth = $state(280);

   let mockFiles = [
       { id: 'sovereign_manifesto.md', name: 'Sovereign Manifesto', type: 'file' },
       { id: 'mesh_network_arch.md', name: 'Mesh Network Arch', type: 'file' },
       { id: 'oracle_cloud_setup.md', name: 'Oracle Cloud Setup', type: 'file' }
   ];

   function openDocument(id: string) {
       activeDocumentId = id;
   }
</script>

<div class="flex w-full h-full overflow-hidden bg-surface-900 border-l border-surface-700">
   
   <!-- Vault Sidebar -->
   <aside class="flex flex-col h-full bg-surface-800 border-r border-surface-700 shrink-0" style="width: {sidebarWidth}px">
       <div class="p-4 border-b border-surface-700 flex items-center justify-between">
           <h2 class="text-xs font-bold uppercase tracking-widest text-surface-400">Knowledge Vault</h2>
           <Database class="w-4 h-4 text-surface-500" />
       </div>
       <div class="flex-1 overflow-y-auto p-2 flex flex-col gap-1">
           {#each mockFiles as file}
               <button 
                 onclick={() => openDocument(file.id)}
                 class="w-full text-left px-3 py-2 rounded-lg text-sm flex items-center gap-2 transition-colors {activeDocumentId === file.id ? 'bg-primary-500/10 text-primary-400' : 'text-surface-400 hover:bg-surface-700 hover:text-surface-200'}"
               >
                   <FileText class="w-4 h-4 shrink-0" />
                   <span class="truncate">{file.name}</span>
               </button>
           {/each}
       </div>
   </aside>

   <!-- TipTap Editor Workspace with {#key} Block (The Render Glitch Slayer) -->
   <main class="flex-1 h-full relative bg-surface-900">
       {#key activeDocumentId}
           <BlockEditor 
               documentId={activeDocumentId} 
               initialContent={`---\ntitle: ${activeDocumentId}\ntags: [sovereign, cybrid]\n---\n# ${activeDocumentId}\n\nStart writing your raw markdown here...`} 
               onSave={(content: string) => {
                   console.log(`Saved ${activeDocumentId}:`, content);
               }}
           />
       {/key}
   </main>

</div>
