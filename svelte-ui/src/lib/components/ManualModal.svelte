<script lang="ts">
    import { BookOpen, Printer, X } from 'lucide-svelte';
    import { marked } from 'marked';

    let { isOpen = $bindable(false) } = $props();
    let userGuideHtml = $state('<p>Carregando manual...</p>');
    let isLoaded = false;

    $effect(() => {
        if (isOpen && !isLoaded) {
            loadManual();
        }
    });

    async function loadManual() {
        try {
            const res = await fetch('http://localhost:38001/v1/system/docs/user_guide');
            if (res.ok) {
                const markdownRaw = await res.text();
                userGuideHtml = await marked.parse(markdownRaw);
                isLoaded = true;
            } else {
                userGuideHtml = '<p class="text-rose-400">Falha ao carregar o manual. Certifique-se de que docs/user_guide.md existe no diretório docs/.</p>';
            }
        } catch (e) {
            userGuideHtml = '<p class="text-rose-400">Motor offline ou inalcançável.</p>';
        }
    }

    function printManual() {
        window.print();
    }
</script>

{#if isOpen}
<div class="fixed inset-0 z-[100] flex items-center justify-center bg-surface-950/80 backdrop-blur-sm p-4 md:p-8 print-modal-wrapper">
    <div class="bg-surface-900 border border-surface-700 rounded-2xl shadow-[0_0_40px_rgba(0,0,0,0.5)] w-full max-w-4xl h-full flex flex-col overflow-hidden relative print-modal-content">
        <!-- Modal Header -->
        <div class="flex items-center justify-between p-4 border-b border-surface-800 bg-surface-800/80 print-hidden">
            <h2 class="text-lg font-bold text-surface-100 flex items-center gap-2">
                <BookOpen class="w-5 h-5 text-primary-500" />
                Sovereign Official Manual
            </h2>
            <div class="flex items-center gap-3">
                <button onclick={printManual} class="px-3 py-1.5 rounded-lg bg-primary-600 text-white hover:bg-primary-500 transition-colors cursor-pointer flex items-center gap-2 shadow-sm font-medium" title="Export to PDF">
                    <Printer class="w-4 h-4" />
                    <span class="text-xs">Export PDF</span>
                </button>
                <button onclick={() => isOpen = false} class="p-2 rounded-lg bg-surface-800 text-surface-400 hover:text-surface-100 hover:bg-surface-700 transition-colors cursor-pointer" title="Close">
                    <X class="w-5 h-5" />
                </button>
            </div>
        </div>

        <!-- Markdown Content -->
        <div class="p-6 md:p-10 overflow-y-auto flex-1 prose prose-invert prose-emerald max-w-none print-prose selection:bg-primary-500/30 font-serif">
            {@html userGuideHtml}
        </div>
    </div>
</div>
{/if}

<style>
    /* Print Specific Styles to generate spotless PDFs */
    @media print {
        :global(body) {
            background: white !important;
            color: black !important;
            height: auto !important;
            overflow: visible !important;
        }
        
        /* Hide EVERYTHING else in the app except the modal wrapper */
        :global(body > *:not(.print-modal-wrapper)) {
            display: none !important;
        }
        
        /* The wrapper becomes the entire printed page */
        .print-modal-wrapper {
            position: absolute !important;
            top: 0 !important;
            left: 0 !important;
            background: transparent !important;
            padding: 0 !important;
            display: block !important;
            height: auto !important;
            width: 100% !important;
            overflow: visible !important;
            z-index: 1 !important;
        }

        .print-modal-content {
            border: none !important;
            box-shadow: none !important;
            height: auto !important;
            width: 100% !important;
            overflow: visible !important;
            background: white !important;
            color: black !important;
            border-radius: 0 !important;
        }

        .print-hidden {
            display: none !important;
        }

        .print-prose {
            padding: 0 !important;
            color: black !important;
        }

        /* Force typography for printing black on white */
        :global(.print-prose h1, .print-prose h2, .print-prose h3) {
            color: black !important;
            page-break-after: avoid;
        }
        
        :global(.print-prose p, .print-prose li) {
            color: #333 !important;
        }

        :global(.print-prose code) {
            color: #d14 !important;
            background-color: #f7f7f9 !important;
            border: 1px solid #e1e1e8 !important;
        }

        :global(.print-prose pre) {
            background-color: #f7f7f9 !important;
            border: 1px solid #e1e1e8 !important;
            page-break-inside: avoid;
        }

        :global(.print-prose pre code) {
            color: #333 !important;
            border: none !important;
        }

        :global(.print-prose strong) {
            color: black !important;
        }
    }
</style>
