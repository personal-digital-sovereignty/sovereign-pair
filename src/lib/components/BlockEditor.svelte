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

    import { Code, Bold, Italic, Strikethrough, Heading1, Heading2, Heading3, List, ListOrdered, CheckSquare, Quote, Minus, Table as TableIcon } from 'lucide-svelte';

    let { documentId = '', onSave = (content: string) => {} } = $props();

    let editorElement: HTMLElement;
    let editor: Editor | null = $state(null);
    let rawMarkdown = $state('');

    // Document Properties (Frontmatter)
    let documentProperties = $state<Record<string, any>>({});
    let showProperties = $state(false);

    let viewMode = $state<'visual' | 'split' | 'source'>('visual');

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
        saveDocument(fullMarkdown);
    }

    async function fetchDocument() {
        try {
            const token = localStorage.getItem('sovereign_token') || '';
            const ws_id = globalState.activeWorkspaceId || 'default';
            // The UUID or File Path is sent as documentId
            const res = await fetch(`http://localhost:38001/v1/vault/document/${encodeURIComponent(documentId)}?workspace_id=${ws_id}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) {
                const data = await res.json();
                const content = data.content_raw || '';
                const parsed = parseFrontmatter(content);
                documentProperties = parsed.frontmatter as Record<string, any>;
                rawMarkdown = buildMarkdown(parsed.content, $state.snapshot(documentProperties));
                if (editor) editor.commands.setContent(parsed.content, { emitUpdate: false });
            } else {
                console.warn(`Doc ${documentId} fetch failed. Using template.`);
                const template = `---\ntitle: ${documentId}\n---\n# ${documentId}\n\nInicie sua documentação.`;
                const parsed = parseFrontmatter(template);
                documentProperties = parsed.frontmatter as Record<string, any>;
                rawMarkdown = template;
                if (editor) editor.commands.setContent(parsed.content, { emitUpdate: false });
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
            ],
            content: '', // Initialized empty, immediately hydrated
            editorProps: {
                attributes: {
                    class: 'prose prose-invert max-w-none focus:outline-none min-h-[500px] text-surface-200'
                }
            },
            onUpdate: ({ editor: e }) => {
                // @ts-ignore
                const currentContent = e.storage.markdown.getMarkdown();
                const fullMarkdown = buildMarkdown(currentContent, $state.snapshot(documentProperties));
                rawMarkdown = fullMarkdown;
                saveDocument(fullMarkdown);
                
                // Triggers Svelte reactivity for the floating menus
                editor = editor; 
            },
            onSelectionUpdate: () => {
                editor = editor;
            }
        });

        fetchDocument();

        return () => {
            if (editor) {
                editor.destroy();
            }
        };
    });

</script>

<div class="h-full bg-surface-900 text-surface-200 relative flex flex-col pt-16">
    
    <!-- Floating Header Toolbar -->
    <div class="absolute top-4 left-6 z-40 bg-surface-800 rounded-lg border border-surface-700 p-1 flex gap-1 shadow-lg pointer-events-auto">
        <button onclick={() => viewMode = 'visual'} class="px-3 py-1 text-xs rounded font-medium transition-colors {viewMode === 'visual' ? 'bg-surface-700 text-white' : 'text-surface-500 hover:text-white'}">Visual</button>
        <button onclick={() => viewMode = 'split'} class="px-3 py-1 text-xs rounded font-medium transition-colors {viewMode === 'split' ? 'bg-surface-700 text-white' : 'text-surface-500 hover:text-white'}">Split</button>
        <button onclick={() => viewMode = 'source'} class="px-3 py-1 text-xs rounded font-medium transition-colors {viewMode === 'source' ? 'bg-surface-700 text-white' : 'text-surface-500 hover:text-white'}">Código</button>
        
        <div class="w-px h-4 bg-surface-700 mx-1 self-center"></div>
        <button onclick={() => showProperties = !showProperties} class="px-3 py-1 text-xs rounded font-medium transition-colors {showProperties ? 'bg-primary-500/20 text-primary-400' : 'text-primary-500 hover:bg-surface-800'}">Props</button>
    </div>

    <!-- Toolbar for Formatting (Visible only in Visual/Split mode if editor exists) -->
    {#if editor && (viewMode === 'visual' || viewMode === 'split')}
      <div class="w-full flex justify-center mb-4">
        <div class="flex items-center gap-1 bg-surface-800 border border-surface-700 px-2 py-1.5 rounded-xl shadow-md overflow-x-auto max-w-full">
            <button onclick={() => editor?.chain().focus().toggleBold().run()} class="p-1.5 rounded hover:bg-surface-700 {editor.isActive('bold') ? 'text-primary-400 bg-primary-500/10' : 'text-surface-400'}"><Bold class="w-4 h-4"/></button>
            <button onclick={() => editor?.chain().focus().toggleItalic().run()} class="p-1.5 rounded hover:bg-surface-700 {editor.isActive('italic') ? 'text-primary-400 bg-primary-500/10' : 'text-surface-400'}"><Italic class="w-4 h-4"/></button>
            <button onclick={() => editor?.chain().focus().toggleStrike().run()} class="p-1.5 rounded hover:bg-surface-700 {editor.isActive('strike') ? 'text-primary-400 bg-primary-500/10' : 'text-surface-400'}"><Strikethrough class="w-4 h-4"/></button>
            <button onclick={() => editor?.chain().focus().toggleCode().run()} class="p-1.5 rounded hover:bg-surface-700 {editor.isActive('code') ? 'text-indigo-400 bg-indigo-500/10' : 'text-surface-400'}"><Code class="w-4 h-4"/></button>
            
            <div class="w-px h-5 bg-surface-700 mx-1"></div>
            
            <button onclick={() => editor?.chain().focus().toggleHeading({ level: 1 }).run()} class="p-1.5 rounded hover:bg-surface-700 {editor.isActive('heading', { level: 1 }) ? 'text-primary-400 bg-primary-500/10' : 'text-surface-400'}"><Heading1 class="w-4 h-4"/></button>
            <button onclick={() => editor?.chain().focus().toggleHeading({ level: 2 }).run()} class="p-1.5 rounded hover:bg-surface-700 {editor.isActive('heading', { level: 2 }) ? 'text-primary-400 bg-primary-500/10' : 'text-surface-400'}"><Heading2 class="w-4 h-4"/></button>
            <button onclick={() => editor?.chain().focus().toggleHeading({ level: 3 }).run()} class="p-1.5 rounded hover:bg-surface-700 {editor.isActive('heading', { level: 3 }) ? 'text-primary-400 bg-primary-500/10' : 'text-surface-400'}"><Heading3 class="w-4 h-4"/></button>

            <div class="w-px h-5 bg-surface-700 mx-1"></div>

            <button onclick={() => editor?.chain().focus().toggleBulletList().run()} class="p-1.5 rounded hover:bg-surface-700 {editor.isActive('bulletList') ? 'text-primary-400 bg-primary-500/10' : 'text-surface-400'}"><List class="w-4 h-4"/></button>
            <button onclick={() => editor?.chain().focus().toggleOrderedList().run()} class="p-1.5 rounded hover:bg-surface-700 {editor.isActive('orderedList') ? 'text-primary-400 bg-primary-500/10' : 'text-surface-400'}"><ListOrdered class="w-4 h-4"/></button>
            <button onclick={() => editor?.chain().focus().toggleTaskList().run()} class="p-1.5 rounded hover:bg-surface-700 {editor.isActive('taskList') ? 'text-primary-400 bg-primary-500/10' : 'text-surface-400'}"><CheckSquare class="w-4 h-4"/></button>
            <button onclick={() => editor?.chain().focus().toggleBlockquote().run()} class="p-1.5 rounded hover:bg-surface-700 {editor.isActive('blockquote') ? 'text-primary-400 bg-primary-500/10' : 'text-surface-400'}"><Quote class="w-4 h-4"/></button>

            <div class="w-px h-5 bg-surface-700 mx-1"></div>

            <button onclick={() => editor?.chain().focus().setHorizontalRule().run()} class="p-1.5 rounded hover:bg-surface-700 text-surface-400"><Minus class="w-4 h-4"/></button>
            <button onclick={() => editor?.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run()} class="p-1.5 rounded hover:bg-surface-700 text-primary-500"><TableIcon class="w-4 h-4"/></button>
        </div>
      </div>
    {/if}

    <div class="flex-1 w-full flex overflow-hidden">
        
        <!-- Source Code View -->
        {#if viewMode === 'source' || viewMode === 'split'}
            <div class="{viewMode === 'split' ? 'w-1/2 border-r border-surface-800' : 'w-full max-w-4xl mx-auto'} h-full flex flex-col p-8 overflow-y-auto">
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
                    class="flex-1 w-full bg-transparent text-primary-400 font-mono text-sm leading-relaxed resize-none outline-none" 
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
                <div class="mb-6 p-4 rounded-xl bg-surface-800 border border-surface-700">
                    <h3 class="text-xs font-bold uppercase text-surface-500 mb-3">Frontmatter YAML</h3>
                    <div class="flex flex-col gap-2">
                        {#each Object.entries(documentProperties) as [key, value]}
                           <div class="flex items-center gap-2">
                               <input value={key} readonly class="text-xs bg-transparent text-surface-500 border border-surface-700 rounded px-2 py-1 w-32" />
                               <span class="text-surface-600">:</span>
                               <input value={value} oninput={e => {
                                   documentProperties[key] = (e.currentTarget as HTMLInputElement).value;
                                   syncToSource();
                               }} class="flex-1 text-sm bg-surface-900 border border-surface-700 rounded px-3 py-1 text-surface-300" />
                           </div>
                        {/each}
                    </div>
                </div>
            {/if}

            <h1 class="text-4xl font-bold tracking-tight text-surface-100 placeholder:text-surface-700 outline-none mb-8 border-b border-surface-800 pb-4">
                {documentId || 'Untitled Document'}
            </h1>

            <div bind:this={editorElement} class="w-full pb-32"></div>
        </div>

    </div>
</div>
