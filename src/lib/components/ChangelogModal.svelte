<script lang="ts">
    import { X, History } from 'lucide-svelte';
    import { marked } from 'marked';
    import DOMPurify from 'dompurify';
    import changelogRaw from '../../../../CHANGELOG.md?raw';
    
    let { isOpen = $bindable(false) } = $props();

    let renderedChangelog = $state("");

    $effect(() => {
        if (isOpen && !renderedChangelog) {
            renderedChangelog = DOMPurify.sanitize(marked.parse(changelogRaw) as string);
        }
    });
</script>

{#if isOpen}
<!-- Backdrop / Esc listener handled via wrapper or click outside -->
<div class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4 sm:p-6 animate-in fade-in duration-200">
    <!-- Click outside to close -->
    <div class="absolute inset-0" onclick={() => isOpen = false} aria-label="Close modal" role="button" tabindex="0" onkeydown={(e) => e.key === 'Escape' && (isOpen = false)}></div>
    
    <div class="relative bg-white w-full max-w-4xl max-h-[85vh] rounded-2xl shadow-2xl flex flex-col border border-slate-200 overflow-hidden animate-in zoom-in-95 duration-200">
        
        <!-- Header -->
        <div class="flex items-center justify-between px-6 py-4 border-b border-slate-100 bg-slate-50/80 shrink-0">
            <div class="flex items-center gap-3">
                <div class="p-2 bg-blue-100 text-blue-600 rounded-lg shadow-sm">
                    <History class="w-5 h-5" />
                </div>
                <div>
                    <h2 class="text-lg font-bold text-slate-800 tracking-tight">Sovereign Changelog</h2>
                    <p class="text-xs text-slate-500 font-mono tracking-wide uppercase mt-0.5">Version History & Release Notes</p>
                </div>
            </div>
            <button onclick={() => isOpen = false} class="p-2 text-slate-400 hover:text-slate-700 hover:bg-slate-200 rounded-lg transition-colors cursor-pointer">
                <X class="w-5 h-5" />
            </button>
        </div>

        <!-- Body -->
        <div class="flex-1 overflow-y-auto p-6 md:p-8 bg-white custom-scrollbar">
            <div class="prose prose-slate prose-sm md:prose-base max-w-none prose-headings:text-slate-800 prose-a:text-blue-600 prose-code:text-indigo-600 prose-code:bg-indigo-50 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded-md prose-code:before:content-none prose-code:after:content-none">
                {@html renderedChangelog}
            </div>
        </div>
        
    </div>
</div>
{/if}
