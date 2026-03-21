<script lang="ts">
   import BlockEditor from '$lib/components/BlockEditor.svelte';
   import { globalState } from '$lib/state.svelte.js';
</script>

<div class="flex w-full h-full overflow-hidden bg-surface-900 border-l border-surface-700">
   <!-- TipTap Editor Workspace with {#key} Block (The Render Glitch Slayer) -->
   <main class="flex-1 h-full relative bg-surface-900">
       {#if globalState.vault.activeDocumentId}
           {#key globalState.vault.activeDocumentId}
               <BlockEditor 
                   documentId={globalState.vault.activeDocumentId} 
                   initialContent={`---\ntitle: ${globalState.vault.activeDocumentId}\ntags: [sovereign, cybrid]\n---\n# ${globalState.vault.activeDocumentId}\n\nStart writing your raw markdown here...`} 
                   onSave={(content: string) => {
                       console.log(`Saved ${globalState.vault.activeDocumentId}:`, content);
                   }}
               />
           {/key}
       {/if}
   </main>
</div>
