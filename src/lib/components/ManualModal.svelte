<script lang="ts">
    import { BookOpen, Printer, X } from 'lucide-svelte';
    import { marked } from 'marked';
    import DOMPurify from 'dompurify';
    import userGuideRaw from '../../../../docs/user_guide.md?raw';

    let { isOpen = $bindable(false) } = $props();

    let renderedManual = $state("");

    $effect(() => {
        if (isOpen && !renderedManual) {
            renderedManual = DOMPurify.sanitize(marked.parse(userGuideRaw) as string);
        }
    });

    function printManual() {
        window.print();
    }
</script>

{#if isOpen}
<!-- Backdrop / Esc listener handled via wrapper or click outside -->
<div class="fixed inset-0 z-[100] flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4 sm:p-6 animate-in fade-in duration-200 print-modal-wrapper">
    <!-- Click outside to close -->
    <div class="absolute inset-0 print-hidden" onclick={() => isOpen = false} aria-label="Close modal" role="button" tabindex="0" onkeydown={(e) => e.key === 'Escape' && (isOpen = false)}></div>
    
    <div class="relative bg-white w-full max-w-4xl max-h-[85vh] rounded-2xl shadow-2xl flex flex-col border border-slate-200 overflow-hidden animate-in zoom-in-95 duration-200 print-modal-content">
        
        <!-- Header -->
        <div class="flex items-center justify-between px-6 py-4 border-b border-slate-100 bg-slate-50/80 shrink-0 print-hidden">
            <div class="flex items-center gap-3">
                <div class="p-2 bg-emerald-100 text-emerald-600 rounded-lg shadow-sm">
                    <BookOpen class="w-5 h-5" />
                </div>
                <div>
                    <h2 class="text-lg font-bold text-slate-800 tracking-tight">Sovereign Official Manual</h2>
                    <p class="text-xs text-slate-500 font-mono tracking-wide uppercase mt-0.5">Architectural Guide & DevSecOps</p>
                </div>
            </div>
            <div class="flex items-center gap-3">
                <button onclick={printManual} class="px-3 py-1.5 rounded-lg bg-emerald-600 text-white hover:bg-emerald-500 transition-colors cursor-pointer flex items-center gap-2 shadow-sm font-medium" title="Export to PDF">
                    <Printer class="w-4 h-4" />
                    <span class="text-xs">Export PDF</span>
                </button>
                <button onclick={() => isOpen = false} class="p-2 text-slate-400 hover:text-slate-700 hover:bg-slate-200 rounded-lg transition-colors cursor-pointer">
                    <X class="w-5 h-5" />
                </button>
            </div>
        </div>

        <!-- Body -->
        <div class="flex-1 overflow-y-auto p-6 md:p-8 bg-white custom-scrollbar print-prose">
            <div class="prose prose-slate prose-sm md:prose-base max-w-none prose-headings:text-slate-800 prose-a:text-emerald-600 prose-code:text-emerald-600 prose-code:bg-emerald-50 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded-md prose-code:before:content-none prose-code:after:content-none selection:bg-emerald-500/30 font-serif">
                {@html renderedManual}
            </div>
        </div>
        
    </div>
</div>
{/if}

<style>
    /* Print Specific Styles */
    @media print {
        :global(body) { background: white !important; color: black !important; height: auto !important; overflow: visible !important; }
        :global(body > *:not(.print-modal-wrapper)) { display: none !important; }
        .print-modal-wrapper { position: absolute !important; top: 0 !important; left: 0 !important; background: transparent !important; padding: 0 !important; display: block !important; height: auto !important; width: 100% !important; overflow: visible !important; z-index: 1 !important; }
        .print-modal-content { border: none !important; box-shadow: none !important; height: auto !important; width: 100% !important; overflow: visible !important; background: white !important; color: black !important; border-radius: 0 !important; }
        .print-hidden { display: none !important; }
        .print-prose { padding: 0 !important; color: black !important; }
        :global(.print-prose h1, .print-prose h2, .print-prose h3) { color: black !important; page-break-after: avoid; }
        :global(.print-prose p, .print-prose li) { color: #333 !important; }
        :global(.print-prose code) { color: #d14 !important; background-color: #f7f7f9 !important; border: 1px solid #e1e1e8 !important; }
        :global(.print-prose pre) { background-color: #f7f7f9 !important; border: 1px solid #e1e1e8 !important; page-break-inside: avoid; }
        :global(.print-prose pre code) { color: #333 !important; border: none !important; }
        :global(.print-prose strong) { color: black !important; }
    }
</style>
