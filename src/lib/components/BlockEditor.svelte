<script lang="ts">
    import { onMount, unmount } from 'svelte';
    import { Editor } from '@tiptap/core';
    import StarterKit from '@tiptap/starter-kit';
    import TaskList from '@tiptap/extension-task-list';
    import TaskItem from '@tiptap/extension-task-item';
    import { Table } from '@tiptap/extension-table';
    import TableRow from '@tiptap/extension-table-row';
    import TableHeader from '@tiptap/extension-table-header';
    import TableCell from '@tiptap/extension-table-cell';
    import { Markdown } from 'tiptap-markdown';
    import yaml from 'js-yaml';
    import { globalState } from '$lib/state.svelte.js';

    import { Plugin, PluginKey } from '@tiptap/pm/state';
    import { Decoration, DecorationSet } from '@tiptap/pm/view';
    import { Extension } from '@tiptap/core';

    import { Code, Bold, Italic, Strikethrough, Heading1, Heading2, Heading3, List, ListOrdered, CheckSquare, Quote, Minus, Table as TableIcon } from 'lucide-svelte';

    export const ObsidianLinks = Extension.create({
        name: 'obsidianLinks',
        addProseMirrorPlugins() {
            return [
                new Plugin({
                    key: new PluginKey('obsidianLinks'),
                    state: {
                        init(_, { doc }) { return getDecorations(doc); },
                        apply(tr, old) { return tr.docChanged ? getDecorations(tr.doc) : old; },
                    },
                    props: {
                        decorations(state) { return this.getState(state); },
                    },
                }),
            ];
        },
    });

    function getDecorations(doc: any) {
        const decorations: Decoration[] = [];
        doc.descendants((node: any, pos: number) => {
            if (node.isText && node.text) {
                const regex = /\[\[([^\]]+)\]\]/g;
                let match;
                while ((match = regex.exec(node.text)) !== null) {
                    decorations.push(
                        Decoration.inline(pos + match.index, pos + match.index + match[0].length, {
                            class: 'text-blue-600 hover:text-blue-800 hover:underline cursor-pointer transition-colors mx-0.5',
                            style: 'text-decoration-thickness: 1px; text-underline-offset: 2px;'
                        })
                    );
                }
            }
        });
        return DecorationSet.create(doc, decorations);
    }

    export const ObsidianImages = Extension.create({
        name: 'obsidianImages',
        addProseMirrorPlugins() {
            return [
                new Plugin({
                    key: new PluginKey('obsidianImages'),
                    state: {
                        init(_, { doc }) { return getImageDecorations(doc); },
                        apply(tr, old) { return tr.docChanged ? getImageDecorations(tr.doc) : old; },
                    },
                    props: {
                        decorations(state) { return this.getState(state); },
                    },
                }),
            ];
        },
    });

    function getImageDecorations(doc: any) {
        const decorations: Decoration[] = [];
        doc.descendants((node: any, pos: number) => {
            if (node.isText && node.text) {
                const regex = /!\[\[([^\]]+)\]\]/g;
                let match;
                while ((match = regex.exec(node.text)) !== null) {
                    const filename = match[1];
                    const img = document.createElement('img');
                    img.src = `http://localhost:38001/v1/vault/media?path=${encodeURIComponent(filename)}`;
                    img.className = 'max-w-full rounded-lg shadow-sm border border-slate-200 block my-4';
                    img.alt = filename;
                    
                    decorations.push(
                        Decoration.widget(pos + match.index, () => img)
                    );
                    
                    decorations.push(
                        Decoration.inline(pos + match.index, pos + match.index + match[0].length, {
                            style: 'display: none;',
                            class: 'hidden-obsidian-image-tag'
                        })
                    );
                }
            }
        });
        return DecorationSet.create(doc, decorations);
    }


    export const ObsidianCallouts = Extension.create({
        name: 'obsidianCallouts',
        addProseMirrorPlugins() {
            return [
                new Plugin({
                    key: new PluginKey('obsidianCallouts'),
                    state: {
                        init(_, { doc }) { return getCalloutDecorations(doc); },
                        apply(tr, old) { return tr.docChanged ? getCalloutDecorations(tr.doc) : old; },
                    },
                    props: {
                        decorations(state) { return this.getState(state); },
                    },
                }),
            ];
        },
    });

    function getCalloutDecorations(doc: any) {
        const decorations: Decoration[] = [];
        doc.descendants((node: any, pos: number) => {
            if (node.isBlock && node.textContent) {
                const match = node.textContent.match(/^\[!(info|warning|danger|success|tip|note)\]/i);
                if (match) {
                    const calloutType = match[1].toLowerCase();
                    decorations.push(Decoration.node(pos, pos + node.nodeSize, {
                        class: `obsidian-callout callout-${calloutType}`
                    }));
                }
            }
        });
        return DecorationSet.create(doc, decorations);
    }

    let { documentId = '', onSave = (content: string) => {} } = $props();

    let editorElement: HTMLElement;
    let selectionContext = $state<{ text: string, top: number, left: number } | null>(null);

    function updateSelection() {
        if (!editor || editor.state.selection.empty) {
            selectionContext = null;
            return;
        }
        const { from, to } = editor.state.selection;
        if (to - from > 3000) { selectionContext = null; return; }
        
        const text = editor.state.doc.textBetween(from, to, ' ');
        if (!text.trim() || text.length < 5) { selectionContext = null; return; }
        
        const coords = editor.view.coordsAtPos(from);
        selectionContext = {
            text: text.trim(),
            top: coords.top - 50,
            left: coords.left
        };
    }

    function sendToChat(text: string) {
        globalState.chat.inputContext = text;
        selectionContext = null;
    }
    let editor: Editor | null = $state(null);
    let rawMarkdown = $state('');

    // Document Properties (Frontmatter)
    let documentProperties = $state<Record<string, any>>({});
    let showProperties = $state(false);

    let viewMode = $state<'visual' | 'split' | 'source'>('visual');

    let wordCount = $derived(rawMarkdown ? rawMarkdown.trim().split(/\s+/).filter((w: string) => w.length > 0).length : 0);
    let byteCount = $derived(rawMarkdown ? new Blob([rawMarkdown]).size : 0);
    let displayName = $derived(documentProperties?.title || documentId.split('/').pop() || 'Untitled Document');

    const parseFrontmatter = (md: string) => {
        const yamlRegex = /^---\n([\s\S]*?)\n---(?:\n([\s\S]*))?$/;
        const match = md.match(yamlRegex);
        if (match) {
            try {
                return {
                    frontmatter: yaml.load(match[1]) || {},
                    content: match[2] ? match[2].trimStart() : ''
                };
            } catch (e) {
                return { frontmatter: { _error: "Invalid YAML" }, content: md };
            }
        }
        return { frontmatter: {}, content: md };
    };

    const buildMarkdown = (content: string, propsObj: Record<string, any>) => {
        if (Object.keys(propsObj).length === 0) return content;
        try {
            const yamlStr = yaml.dump(propsObj);
            return `---\n${yamlStr}---\n${content}`;
        } catch {
            return content;
        }
    };

    function syncToSource() {
        if (!editor) return;
        // @ts-ignore
        const currentContent = editor.storage.markdown.getMarkdown();
        const fullMarkdown = buildMarkdown(currentContent, documentProperties);
        rawMarkdown = fullMarkdown;
        globalState.vault.activeDocumentContent = fullMarkdown;
        saveDocument(fullMarkdown);
    }

    function bootEditor(contentMarkdown: string) {
        editor = new Editor({
            element: editorElement,
            extensions: [
                StarterKit,
                Markdown,
                TaskList,
                TaskItem.configure({ nested: true }),
                Table.configure({ resizable: true }),
                TableRow,
                TableHeader,
                TableCell,
                ObsidianLinks,
                ObsidianImages,
                ObsidianCallouts,
            ],
            content: contentMarkdown,
            editorProps: {
                attributes: {
                    // Removed prose-invert for Light Theme
                    class: 'prose max-w-none focus:outline-none min-h-[500px] text-slate-800'
                }
            },
            onUpdate: ({ editor: e }) => {
                // @ts-ignore
                const currentContent = e.storage.markdown.getMarkdown();
                const fullMarkdown = buildMarkdown(currentContent, $state.snapshot(documentProperties));
                rawMarkdown = fullMarkdown;
                globalState.vault.activeDocumentContent = fullMarkdown;
                saveDocument(fullMarkdown);
                editor = editor; 
            },
            onSelectionUpdate: () => {
                updateSelection();
                editor = editor;
            }
        });
    }

    async function fetchDocument() {
        try {
            const token = localStorage.getItem('sovereign_token') || '';
            const ws_id = globalState.activeWorkspaceId || 'default';
            const res = await fetch(`http://localhost:38001/v1/vault/document/${encodeURIComponent(documentId)}?workspace_id=${ws_id}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) {
                const data = await res.json();
                const content = data.content || data.content_raw || '';
                const parsed = parseFrontmatter(content);
                documentProperties = parsed.frontmatter as Record<string, any>;
                const fullMarkdown = buildMarkdown(parsed.content, $state.snapshot(documentProperties));
                rawMarkdown = fullMarkdown;
                globalState.vault.activeDocumentContent = fullMarkdown;
                bootEditor(parsed.content);
            } else {
                console.warn(`Doc ${documentId} fetch failed. Using template.`);
                const template = `---\ntitle: ${documentId}\n---\n# ${documentId}\n\nInicie sua documentação.`;
                const parsed = parseFrontmatter(template);
                documentProperties = parsed.frontmatter as Record<string, any>;
                rawMarkdown = template;
                globalState.vault.activeDocumentContent = template;
                bootEditor(parsed.content);
            }
        } catch(e) { console.error("Could not fetch doc:", e); }
    }

    async function saveDocument(fullMarkdown: string) {
        try {
            const token = localStorage.getItem('sovereign_token') || '';
            const ws_id = globalState.activeWorkspaceId || 'default';
            await fetch(`http://localhost:38001/v1/vault/document/${encodeURIComponent(documentId)}?workspace_id=${ws_id}`, {
                method: 'PUT',
                headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
                body: JSON.stringify({ content_raw: fullMarkdown })
            });
            onSave(fullMarkdown);
        } catch(e) { console.error("Save failed:", e); }
    }

    onMount(() => {
        fetchDocument();
        return () => {
            if (editor) editor.destroy();
        };
    });

</script>

<div class="h-full bg-white text-slate-800 relative flex flex-col pt-16">
    
    <!-- Floating Header Toolbar -->
    <div class="absolute top-4 left-6 z-40 bg-white rounded-lg border border-slate-200 p-1 flex gap-1 shadow-[0_2px_8px_-4px_rgba(0,0,0,0.1)] pointer-events-auto">
        <button onclick={() => viewMode = 'visual'} class="px-3 py-1 text-xs rounded font-medium transition-colors {viewMode === 'visual' ? 'bg-slate-100 text-slate-800' : 'text-slate-500 hover:text-slate-700'}">Visual</button>
        <button onclick={() => viewMode = 'split'} class="px-3 py-1 text-xs rounded font-medium transition-colors {viewMode === 'split' ? 'bg-slate-100 text-slate-800' : 'text-slate-500 hover:text-slate-700'}">Split</button>
        <button onclick={() => viewMode = 'source'} class="px-3 py-1 text-xs rounded font-medium transition-colors {viewMode === 'source' ? 'bg-slate-100 text-slate-800' : 'text-slate-500 hover:text-slate-700'}">Código</button>
        
        <div class="w-px h-4 bg-slate-200 mx-1 self-center"></div>
        <button onclick={() => showProperties = !showProperties} class="px-3 py-1 text-xs rounded font-medium transition-colors {showProperties ? 'bg-blue-50 text-blue-600' : 'text-blue-500 hover:bg-slate-50'}">Props</button>
    </div>

    <!-- Toolbar for Formatting -->
    {#if editor && (viewMode === 'visual' || viewMode === 'split')}
      <div class="w-full flex justify-center mb-4">
        <div class="flex items-center gap-1 bg-white border border-slate-200 px-2 py-1.5 rounded-xl shadow-sm overflow-x-auto max-w-full">
            <button onclick={() => editor?.chain().focus().toggleBold().run()} class="p-1.5 rounded hover:bg-slate-50 {editor.isActive('bold') ? 'text-blue-600 bg-blue-50' : 'text-slate-400'}"><Bold class="w-4 h-4"/></button>
            <button onclick={() => editor?.chain().focus().toggleItalic().run()} class="p-1.5 rounded hover:bg-slate-50 {editor.isActive('italic') ? 'text-blue-600 bg-blue-50' : 'text-slate-400'}"><Italic class="w-4 h-4"/></button>
            <button onclick={() => editor?.chain().focus().toggleStrike().run()} class="p-1.5 rounded hover:bg-slate-50 {editor.isActive('strike') ? 'text-blue-600 bg-blue-50' : 'text-slate-400'}"><Strikethrough class="w-4 h-4"/></button>
            <button onclick={() => editor?.chain().focus().toggleCode().run()} class="p-1.5 rounded hover:bg-slate-50 {editor.isActive('code') ? 'text-indigo-600 bg-indigo-50' : 'text-slate-400'}"><Code class="w-4 h-4"/></button>
            
            <div class="w-px h-5 bg-slate-200 mx-1"></div>
            
            <button onclick={() => editor?.chain().focus().toggleHeading({ level: 1 }).run()} class="p-1.5 rounded hover:bg-slate-50 {editor.isActive('heading', { level: 1 }) ? 'text-blue-600 bg-blue-50' : 'text-slate-400'}"><Heading1 class="w-4 h-4"/></button>
            <button onclick={() => editor?.chain().focus().toggleHeading({ level: 2 }).run()} class="p-1.5 rounded hover:bg-slate-50 {editor.isActive('heading', { level: 2 }) ? 'text-blue-600 bg-blue-50' : 'text-slate-400'}"><Heading2 class="w-4 h-4"/></button>
            <button onclick={() => editor?.chain().focus().toggleHeading({ level: 3 }).run()} class="p-1.5 rounded hover:bg-slate-50 {editor.isActive('heading', { level: 3 }) ? 'text-blue-600 bg-blue-50' : 'text-slate-400'}"><Heading3 class="w-4 h-4"/></button>

            <div class="w-px h-5 bg-slate-200 mx-1"></div>

            <button onclick={() => editor?.chain().focus().toggleBulletList().run()} class="p-1.5 rounded hover:bg-slate-50 {editor.isActive('bulletList') ? 'text-blue-600 bg-blue-50' : 'text-slate-400'}"><List class="w-4 h-4"/></button>
            <button onclick={() => editor?.chain().focus().toggleOrderedList().run()} class="p-1.5 rounded hover:bg-slate-50 {editor.isActive('orderedList') ? 'text-blue-600 bg-blue-50' : 'text-slate-400'}"><ListOrdered class="w-4 h-4"/></button>
            <button onclick={() => editor?.chain().focus().toggleTaskList().run()} class="p-1.5 rounded hover:bg-slate-50 {editor.isActive('taskList') ? 'text-blue-600 bg-blue-50' : 'text-slate-400'}"><CheckSquare class="w-4 h-4"/></button>
            <button onclick={() => editor?.chain().focus().toggleBlockquote().run()} class="p-1.5 rounded hover:bg-slate-50 {editor.isActive('blockquote') ? 'text-blue-600 bg-blue-50' : 'text-slate-400'}"><Quote class="w-4 h-4"/></button>

            <div class="w-px h-5 bg-slate-200 mx-1"></div>

            <button onclick={() => editor?.chain().focus().setHorizontalRule().run()} class="p-1.5 rounded hover:bg-slate-50 text-slate-400"><Minus class="w-4 h-4"/></button>
            <button onclick={() => editor?.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run()} class="p-1.5 rounded hover:bg-slate-50 text-blue-500"><TableIcon class="w-4 h-4"/></button>
        </div>
      </div>
    {/if}

    <div class="flex-1 w-full flex overflow-hidden">
        
        <!-- Source Code View -->
        {#if viewMode === 'source' || viewMode === 'split'}
            <div class="{viewMode === 'split' ? 'w-1/2 border-r border-slate-200' : 'w-full max-w-4xl mx-auto'} h-full flex flex-col p-8 overflow-y-auto">
                <textarea 
                    bind:value={rawMarkdown} 
                    oninput={() => {
                        const parsed = parseFrontmatter(rawMarkdown);
                        documentProperties = parsed.frontmatter;
                        if (editor && viewMode === 'split') {
                            editor.commands.setContent(parsed.content, { emitUpdate: false });
                        }
                        saveDocument(rawMarkdown);
                    }}
                    class="flex-1 w-full bg-transparent text-blue-700 font-mono text-sm leading-relaxed resize-none outline-none" 
                    spellcheck="false" 
                    placeholder="Enter Markdown...">
                </textarea>
            </div>
        {/if}

        <!-- TipTap Visual View -->
        <div 
             style="display: {viewMode === 'visual' || viewMode === 'split' ? 'flex' : 'none'}" 
             class="{viewMode === 'split' ? 'w-1/2' : 'w-full max-w-4xl mx-auto'} h-full flex-col p-8 overflow-y-auto custom-scrollbar relative">
            
            {#if showProperties}
                <div class="absolute top-20 right-8 w-[450px] p-5 rounded-2xl bg-white/95 backdrop-blur-xl border border-slate-200 shadow-[0_10px_40px_-10px_rgba(0,0,0,0.15)] z-50">
                    <h3 class="text-[10px] uppercase tracking-widest font-bold text-slate-400 mb-4 flex items-center gap-2">
                        <div class="w-1.5 h-1.5 rounded-full bg-blue-500"></div>
                        Frontmatter YAML
                    </h3>
                    <div class="flex flex-col gap-3">
                        {#each Object.entries(documentProperties) as [key, value]}
                           <div class="flex items-center gap-2">
                               <input value={key} readonly class="text-xs bg-transparent text-slate-500 border border-slate-200 rounded px-2 py-1 w-32 outline-none" />
                               <span class="text-slate-400">:</span>
                               <input value={value} oninput={e => {
                                   documentProperties[key] = (e.currentTarget as HTMLInputElement).value;
                                   syncToSource();
                               }} class="flex-1 text-sm bg-white border border-slate-200 rounded px-3 py-1 text-slate-700 focus:border-blue-400 focus:ring-1 focus:ring-blue-100 outline-none transition-all" />
                           </div>
                        {/each}
                    </div>
                </div>
            {/if}

            <h1 class="text-4xl font-bold tracking-tight text-slate-900 placeholder:text-slate-400 outline-none mb-8 border-b border-slate-200 pb-4">
                {displayName}
            </h1>

            <div bind:this={editorElement} class="w-full pb-32"></div>
        </div>

    </div>

    <!-- Status Bar Footer -->
    <footer class="h-8 border-t border-slate-200 bg-slate-50 flex items-center justify-between px-4 text-[11px] text-slate-500 font-mono shrink-0 z-50">
        <div class="flex items-center gap-3 truncate max-w-[60%]">
            <span class="truncate" title={documentId}>{documentId}</span>
        </div>
        <div class="flex items-center gap-3 shrink-0">
            <span>{wordCount} words</span>
            <span class="text-slate-300">|</span>
            <span>{byteCount} bytes</span>
            <span class="text-slate-300">|</span>
            <span class="text-emerald-600/80 font-bold uppercase tracking-widest text-[9px]">Sovereign Sync</span>
        </div>
    </footer>
</div>

{#if selectionContext}
    <div class="fixed z-[100] bg-slate-900/95 backdrop-blur-md text-white rounded-lg shadow-2xl border border-slate-700/50 p-1 flex items-center gap-1 animate-in fade-in zoom-in-95 duration-200" style="top: {selectionContext.top}px; left: {selectionContext.left}px;">
        <button onclick={() => sendToChat(selectionContext!.text)} class="flex items-center gap-2 px-3 py-1.5 hover:bg-white/10 rounded-md text-[11px] font-bold tracking-widest uppercase transition-colors cursor-pointer text-indigo-300">
            <svg class="w-3.5 h-3.5" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z"/><path d="M9 13a4.5 4.5 0 1 0 4.3-6.261"/><path d="M15 5a3 3 0 1 0 5.997.125 4 4 0 0 0 2.526 5.77 4 4 0 0 0-.556 6.588A4 4 0 1 0 15 18Z"/><path d="M15 13a4.5 4.5 0 1 0-4.3-6.261"/><path d="M12 10v4"/></svg>
            Refletir com IA
        </button>
    </div>
{/if}

<style>
    :global(.obsidian-callout) {
        border-left-width: 4px !important;
        padding: 12px 16px !important;
        margin: 16px 0 !important;
        border-radius: 6px !important;
        font-size: 0.9em;
    }
    :global(.callout-info), :global(.callout-note) { border-left-color: #3b82f6 !important; background-color: #eff6ff !important; color: #1e3a8a !important; }
    :global(.callout-warning) { border-left-color: #f59e0b !important; background-color: #fffbeb !important; color: #78350f !important; }
    :global(.callout-danger) { border-left-color: #ef4444 !important; background-color: #fef2f2 !important; color: #7f1d1d !important; }
    :global(.callout-success), :global(.callout-tip) { border-left-color: #10b981 !important; background-color: #ecfdf5 !important; color: #064e3b !important; }
</style>
