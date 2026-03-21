<script lang="ts">
   import BlockEditor from '$lib/components/BlockEditor.svelte';
   import ChatPanel from '$lib/components/ChatPanel.svelte';
   import { globalState } from '$lib/state.svelte.js';
</script>

<div class="flex w-full h-full overflow-hidden bg-surface-900 border-l border-surface-700">
   <!-- TipTap Editor Workspace with {#key} Block to force remounts on file change -->
   <main class="flex-1 h-full relative bg-surface-900">
       {#if globalState.vault.activeDocumentId}
           {#key globalState.vault.activeDocumentId}
               <BlockEditor 
                   documentId={globalState.vault.activeDocumentId} 
               />
           {/key}
       {/if}
   </main>

   <!-- Cibrid Chat Sidebar -->
   <aside class="w-[450px] border-l border-surface-700 h-full hidden xl:block shadow-2xl relative z-10">
       <ChatPanel />
   </aside>
</div>
