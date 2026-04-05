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
    import Image from '@tiptap/extension-image';
    import yaml from 'js-yaml';
    import { globalState } from '$lib/state.svelte.js';

    import { Plugin, PluginKey, TextSelection } from '@tiptap/pm/state';
    import { Decoration, DecorationSet } from '@tiptap/pm/view';
    import { Extension } from '@tiptap/core';

    import { Code, Bold, Italic, Strikethrough, Heading1, Heading2, Heading3, List, ListOrdered, CheckSquare, Quote, Minus, Table as TableIcon, Copy, BrainCircuit } from 'lucide-svelte';

    export const SovereignLinks = Extension.create({
        name: 'sovereignLinks',
        addProseMirrorPlugins() {
            return [
                new Plugin({
                    key: new PluginKey('sovereignLinks'),
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

    export const SovereignImages = Extension.create({
        name: 'sovereignImages',
        addProseMirrorPlugins() {
            return [
                new Plugin({
                    key: new PluginKey('sovereignImages'),
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
                // 1. Match Sovereign style ![[filename.png]]
                const regexObs = /!\[\[([^\]]+)\]\]/g;
                let match;
                while ((match = regexObs.exec(node.text)) !== null) {
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
                            class: 'hidden-sovereign-image-tag'
                        })
                    );
                }


            }
        });
        return DecorationSet.create(doc, decorations);
    }


    export const SovereignCallouts = Extension.create({
        name: 'sovereignCallouts',
        addProseMirrorPlugins() {
            return [
                new Plugin({
                    key: new PluginKey('sovereignCallouts'),
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
                        class: `sovereign-callout callout-${calloutType}`
                    }));
                }
            }
        });
        return DecorationSet.create(doc, decorations);
    }

    export const TheAccountantMath = Extension.create({
        name: 'theAccountantMath',
        addProseMirrorPlugins() {
            return [
                new Plugin({
                    key: new PluginKey('theAccountantMath'),
                    appendTransaction(transactions, oldState, newState) {
                        if (!transactions.some(tr => tr.docChanged || tr.selectionSet)) return;

                        let tr = newState.tr;
                        let modified = false;

                        const tables: any[] = [];
                        newState.doc.descendants((node, pos) => {
                            if (node.type.name === 'table') tables.push({ node, pos });
                            return false;
                        });

                        const head = newState.selection.$head.pos;

                        tables.forEach(({node: tableNode, pos: tablePos}) => {
                            const rows: any[] = [];
                            const cellData: any[] = [];
                            
                            tableNode.descendants((node: any, pos: number) => {
                                if (node.type.name === 'tableRow') {
                                    rows.push([]);
                                } else if (node.type.name === 'tableCell' || node.type.name === 'tableHeader') {
                                    const absPos = tablePos + 1 + pos;
                                    let text = '';
                                    let mathHref = null;
                                    
                                    node.descendants((child: any) => {
                                        if (child.isText) {
                                            text += child.text;
                                            child.marks.forEach((m: any) => {
                                                if (m.type.name === 'link' && m.attrs.href && m.attrs.href.startsWith('=')) {
                                                    mathHref = m.attrs.href;
                                                }
                                            });
                                        }
                                    });

                                    text = text.trim();
                                    rows[rows.length - 1].push(mathHref ? mathHref : text);
                                    
                                    const isFocused = head > absPos && head < absPos + node.nodeSize;

                                    cellData.push({ 
                                        pos: absPos, 
                                        nodeSize: node.nodeSize,
                                        text: text,
                                        mathHref: mathHref,
                                        isFocused: isFocused
                                    });
                                    return false;
                                }
                            });

                            const getVal = (r: number, c: number) => {
                                if (r < 0 || r >= rows.length || c < 0 || c >= rows[r].length) return '0';
                                let v = rows[r][c].replace(/\\\*/g, '*').replace(/\\_/g, '_').trim();
                                if (v === '') return '0';
                                if (v.startsWith('=')) return '(' + v.substring(1).toUpperCase() + ')';
                                return isNaN(Number(v)) ? '0' : v;
                            };

                            let cellIndex = 0;
                            for(let r=0; r<rows.length; r++) {
                                for(let c=0; c<rows[r].length; c++) {
                                    const cell = cellData[cellIndex++];
                                    
                                    if (cell.isFocused && cell.mathHref) {
                                        const from = cell.pos + 1;
                                        const to = cell.pos + cell.nodeSize - 1;
                                        const pNode = newState.schema.nodes.paragraph.create({}, newState.schema.text(cell.mathHref));
                                        tr.replaceWith(from, to, pNode);
                                        tr.setSelection(TextSelection.create(tr.doc, from + 1 + cell.mathHref.length));
                                        modified = true;
                                    } 
                                    else if (!cell.isFocused) {
                                        let formula = null;
                                        if (cell.mathHref) {
                                            formula = cell.mathHref;
                                        } else if (cell.text.startsWith('=')) {
                                            formula = cell.text;
                                        }

                                        if (formula) {
                                            let evalFormula = formula.substring(1).toUpperCase().replace(/\\\*/g, '*').replace(/\\_/g, '_');
                                            let depth = 0;
                                            while(depth < 10 && /[A-Z][0-9]+/.test(evalFormula)) {
                                                evalFormula = evalFormula.replace(/([A-Z])([0-9]+)/g, (m: string, colChar: string, rowStr: string) => {
                                                    const col = colChar.charCodeAt(0) - 65;
                                                    const rw = parseInt(rowStr, 10) - 1;
                                                    return getVal(rw, col);
                                                });
                                                depth++;
                                            }

                                            if (/^[0-9+\-*/(). ]+$/.test(evalFormula)) {
                                                try {
                                                    let resNum = Number(new Function('return ' + evalFormula)());
                                                    if (!isNaN(resNum) && isFinite(resNum)) {
                                                        const valStr = Number.isInteger(resNum) ? resNum.toString() : parseFloat(resNum.toFixed(5)).toString();
                                                        
                                                        if (!cell.mathHref || valStr !== cell.text) {
                                                            const from = cell.pos + 1;
                                                            const to = cell.pos + cell.nodeSize - 1;
                                                            const linkMark = newState.schema.marks.link.create({ href: formula });
                                                            const pNode = newState.schema.nodes.paragraph.create({}, newState.schema.text(valStr, [linkMark]));
                                                            tr.replaceWith(from, to, pNode);
                                                            modified = true;
                                                        }
                                                    }
                                                } catch(e) {}
                                            }
                                        }
                                    }
                                }
                            }
                        });

                        if (modified) {
                            tr.setMeta('addToHistory', false);
                            return tr;
                        }
                    }
                })
            ];
        }
    });

    let { documentId = '', onSave = (content: string) => {} } = $props();

    const API_BASE_URL = 'http://localhost:38001';

    async function saveDocument(content: string) {
        if (!documentId) return;
        try {
            await fetch(`${API_BASE_URL}/v1/vault/document/${encodeURIComponent(documentId)}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('sovereign_token') || ''}` },
                body: JSON.stringify({ workspace_id: Number(globalState.activeWorkspaceId) || null, content })
            });
            onSave(content);
        } catch(e) { console.error('Failed to save via API', e); }
    }

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
        if (!text || text.trim() === '') text = 'Por favor, analise a edição que estou fazendo agora.';
        globalState.chat.inputContext = text;
        selectionContext = null;
    }

    let contextMenu = $state<{ x: number, y: number, show: boolean, isTable: boolean } | null>(null);

    function handleContextMenu(e: MouseEvent) {
        // only override inside editor bounding box
        if (!editorElement || !editorElement.contains(e.target as Node)) return;
        e.preventDefault();
        
        let isTable = false;
        if (editor) {
            isTable = editor.isActive('table');
        }
        
        contextMenu = {
            x: e.clientX,
            y: e.clientY,
            show: true,
            isTable
        };
    }

    $effect(() => {
        const handleClickOutside = () => { if (contextMenu) contextMenu.show = false; };
        document.addEventListener('click', handleClickOutside);
        document.addEventListener('contextmenu', handleContextMenu);
        return () => {
            document.removeEventListener('click', handleClickOutside);
            document.removeEventListener('contextmenu', handleContextMenu);
        };
    });
    let editor: Editor | null = $state(null);
    let rawMarkdown = $state('');

    // Strict Typescript Document Properties Schema
    type FrontmatterValue = string | number | boolean | null | string[];
    type DocumentProperties = Record<string, FrontmatterValue>;

    let documentProperties = $state<DocumentProperties>({});
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
                    frontmatter: yaml.load(match[1]) as DocumentProperties || ({} as DocumentProperties),
                    content: match[2] ? match[2].trimStart() : ''
                };
            } catch (e) {
                return { frontmatter: { _error: "Invalid YAML" } as DocumentProperties, content: md };
            }
        }
        return { frontmatter: {} as DocumentProperties, content: md };
    };

    const buildMarkdown = (content: string, propsObj: DocumentProperties) => {
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
        const storage = editor.storage as Record<string, any>;
        const markdownStorage = storage.markdown as { getMarkdown: () => string };
        const currentContent = markdownStorage.getMarkdown();
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
                Markdown.configure({ html: true, transformPastedText: true, transformCopiedText: true }),
                TaskList,
                TaskItem.configure({ nested: true }),
                Table.configure({ resizable: true }),
                TableRow,
                TableHeader,
                TableCell,
                SovereignLinks,
                Image.configure({ inline: true, allowBase64: true }),
                SovereignImages,
                SovereignCallouts,
                TheAccountantMath,
            ],
            content: contentMarkdown,
            editorProps: {
                attributes: {
                    class: 'prose dark:prose-invert max-w-none focus:outline-none min-h-[500px] text-slate-800 dark:text-slate-200'
                }
            },
            onUpdate: ({ editor: e }) => {
                const storage = e.storage as Record<string, any>;
                const markdownStorage = storage.markdown as { getMarkdown: () => string };
                const currentContent = markdownStorage.getMarkdown();
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



    onMount(() => {
        fetchDocument();
        return () => {
            if (editor) editor.destroy();
        };
    });

</script>

<div class="h-full bg-white dark:bg-[#0c1324] text-slate-800 dark:text-slate-200 relative flex flex-col pt-16 transition-colors">
    
    <!-- Floating Header Toolbar -->
    <div class="absolute top-4 left-6 z-40 bg-white dark:bg-[#12192b] rounded-lg border border-slate-200 dark:border-slate-800 p-1 flex gap-1 shadow-[0_2px_8px_-4px_rgba(0,0,0,0.1)] dark:shadow-none pointer-events-auto">
        <button onclick={() => viewMode = 'visual'} class="px-3 py-1 text-xs rounded font-medium transition-colors {viewMode === 'visual' ? 'bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200' : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200'}">Visual</button>
        <button onclick={() => viewMode = 'split'} class="px-3 py-1 text-xs rounded font-medium transition-colors {viewMode === 'split' ? 'bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200' : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200'}">Split</button>
        <button onclick={() => viewMode = 'source'} class="px-3 py-1 text-xs rounded font-medium transition-colors {viewMode === 'source' ? 'bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200' : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200'}">Código</button>
        
        <div class="w-px h-4 bg-slate-200 dark:bg-slate-700 mx-1 self-center"></div>
        <button onclick={() => showProperties = !showProperties} class="px-3 py-1 text-xs rounded font-medium transition-colors {showProperties ? 'bg-blue-50 dark:bg-blue-900/40 text-blue-600 dark:text-blue-400' : 'text-blue-500 dark:text-blue-400 hover:bg-slate-50 dark:hover:bg-slate-800'}">Props</button>
    </div>

    <!-- Toolbar for Formatting -->
    {#if editor && (viewMode === 'visual' || viewMode === 'split')}
      <div class="w-full flex justify-center mb-4">
        <div class="flex items-center gap-1 bg-white dark:bg-[#12192b] border border-slate-200 dark:border-slate-800 px-2 py-1.5 rounded-xl shadow-sm dark:shadow-none overflow-x-auto max-w-full">
            <button onclick={() => editor?.chain().focus().toggleBold().run()} class="p-1.5 rounded hover:bg-slate-50 dark:hover:bg-slate-800 {editor.isActive('bold') ? 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/40' : 'text-slate-400 dark:text-slate-500'}"><Bold class="w-4 h-4"/></button>
            <button onclick={() => editor?.chain().focus().toggleItalic().run()} class="p-1.5 rounded hover:bg-slate-50 dark:hover:bg-slate-800 {editor.isActive('italic') ? 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/40' : 'text-slate-400 dark:text-slate-500'}"><Italic class="w-4 h-4"/></button>
            <button onclick={() => editor?.chain().focus().toggleStrike().run()} class="p-1.5 rounded hover:bg-slate-50 dark:hover:bg-slate-800 {editor.isActive('strike') ? 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/40' : 'text-slate-400 dark:text-slate-500'}"><Strikethrough class="w-4 h-4"/></button>
            <button onclick={() => editor?.chain().focus().toggleCode().run()} class="p-1.5 rounded hover:bg-slate-50 dark:hover:bg-slate-800 {editor.isActive('code') ? 'text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-900/40' : 'text-slate-400 dark:text-slate-500'}"><Code class="w-4 h-4"/></button>
            
            <div class="w-px h-5 bg-slate-200 dark:bg-slate-700 mx-1"></div>
            
            <button onclick={() => editor?.chain().focus().toggleHeading({ level: 1 }).run()} class="p-1.5 rounded hover:bg-slate-50 dark:hover:bg-slate-800 {editor.isActive('heading', { level: 1 }) ? 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/40' : 'text-slate-400 dark:text-slate-500'}"><Heading1 class="w-4 h-4"/></button>
            <button onclick={() => editor?.chain().focus().toggleHeading({ level: 2 }).run()} class="p-1.5 rounded hover:bg-slate-50 dark:hover:bg-slate-800 {editor.isActive('heading', { level: 2 }) ? 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/40' : 'text-slate-400 dark:text-slate-500'}"><Heading2 class="w-4 h-4"/></button>
            <button onclick={() => editor?.chain().focus().toggleHeading({ level: 3 }).run()} class="p-1.5 rounded hover:bg-slate-50 dark:hover:bg-slate-800 {editor.isActive('heading', { level: 3 }) ? 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/40' : 'text-slate-400 dark:text-slate-500'}"><Heading3 class="w-4 h-4"/></button>

            <div class="w-px h-5 bg-slate-200 dark:bg-slate-700 mx-1"></div>

            <button onclick={() => editor?.chain().focus().toggleBulletList().run()} class="p-1.5 rounded hover:bg-slate-50 dark:hover:bg-slate-800 {editor.isActive('bulletList') ? 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/40' : 'text-slate-400 dark:text-slate-500'}"><List class="w-4 h-4"/></button>
            <button onclick={() => editor?.chain().focus().toggleOrderedList().run()} class="p-1.5 rounded hover:bg-slate-50 dark:hover:bg-slate-800 {editor.isActive('orderedList') ? 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/40' : 'text-slate-400 dark:text-slate-500'}"><ListOrdered class="w-4 h-4"/></button>
            <button onclick={() => editor?.chain().focus().toggleTaskList().run()} class="p-1.5 rounded hover:bg-slate-50 dark:hover:bg-slate-800 {editor.isActive('taskList') ? 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/40' : 'text-slate-400 dark:text-slate-500'}"><CheckSquare class="w-4 h-4"/></button>
            <button onclick={() => editor?.chain().focus().toggleBlockquote().run()} class="p-1.5 rounded hover:bg-slate-50 dark:hover:bg-slate-800 {editor.isActive('blockquote') ? 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/40' : 'text-slate-400 dark:text-slate-500'}"><Quote class="w-4 h-4"/></button>

            <div class="w-px h-5 bg-slate-200 dark:bg-slate-700 mx-1"></div>

            <button onclick={() => editor?.chain().focus().setHorizontalRule().run()} class="p-1.5 rounded hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-400 dark:text-slate-500"><Minus class="w-4 h-4"/></button>
            <button onclick={() => editor?.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run()} class="p-1.5 rounded hover:bg-slate-50 dark:hover:bg-slate-800 text-blue-500 dark:text-blue-400"><TableIcon class="w-4 h-4"/></button>
        </div>
      </div>
    {/if}

    <div class="flex-1 w-full flex overflow-hidden">
        
        <!-- Source Code View -->
        {#if viewMode === 'source' || viewMode === 'split'}
            <div class="{viewMode === 'split' ? 'w-1/2 border-r border-slate-200 dark:border-slate-800' : 'w-full max-w-4xl mx-auto'} h-full flex flex-col p-8 overflow-y-auto">
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
                <div class="absolute top-20 right-8 w-[450px] p-5 rounded-2xl bg-white/95 dark:bg-[#12192b]/95 backdrop-blur-xl border border-slate-200 dark:border-slate-800 shadow-[0_10px_40px_-10px_rgba(0,0,0,0.15)] dark:shadow-none z-50">
                    <h3 class="text-[10px] uppercase tracking-widest font-bold text-slate-400 dark:text-slate-500 mb-4 flex items-center gap-2">
                        <div class="w-1.5 h-1.5 rounded-full bg-blue-500 dark:bg-blue-400"></div>
                        Frontmatter YAML
                    </h3>
                    <div class="flex flex-col gap-3">
                        {#each Object.entries(documentProperties) as [key, value]}
                           <div class="flex items-center gap-2">
                               <input value={key} readonly class="text-xs bg-transparent text-slate-500 dark:text-slate-400 border border-slate-200 dark:border-slate-700 rounded px-2 py-1 w-32 outline-none" />
                               <span class="text-slate-400 dark:text-slate-500">:</span>
                               <input value={value} oninput={e => {
                                   documentProperties[key] = (e.currentTarget as HTMLInputElement).value;
                                   syncToSource();
                               }} class="flex-1 text-sm bg-white dark:bg-[#0c1324] border border-slate-200 dark:border-slate-700 rounded px-3 py-1 text-slate-700 dark:text-slate-300 focus:border-blue-400 focus:ring-1 focus:ring-blue-100 dark:focus:ring-blue-900/40 outline-none transition-all" />
                           </div>
                        {/each}
                    </div>
                </div>
            {/if}

            <h1 class="text-4xl font-bold tracking-tight text-slate-900 dark:text-white placeholder:text-slate-400 dark:placeholder:text-slate-500 outline-none mb-8 border-b border-slate-200 dark:border-slate-800 pb-4">
                {displayName}
            </h1>

            <div class="flex-1 overflow-auto custom-scrollbar p-12 pr-6" bind:this={editorElement}></div>

            <!-- Right Click Context Menu -->
            {#if contextMenu && contextMenu.show}
                <div 
                    class="fixed z-50 bg-white/95 dark:bg-[#12192b]/95 backdrop-blur-xl border border-slate-200 dark:border-slate-700 shadow-xl dark:shadow-none rounded-xl w-64 flex flex-col py-2 text-sm text-slate-700 dark:text-slate-300"
                    style="top: {contextMenu.y}px; left: {contextMenu.x}px;"
                >
                    <button class="px-4 py-2 text-left hover:bg-slate-100 dark:hover:bg-slate-800 flex items-center gap-3 transition-colors" onclick={() => editor?.chain().focus().toggleBold().run()}><Bold class="w-4 h-4 text-slate-400 dark:text-slate-500"/> Negrito</button>
                    <button class="px-4 py-2 text-left hover:bg-slate-100 dark:hover:bg-slate-800 flex items-center gap-3 transition-colors" onclick={() => editor?.chain().focus().toggleItalic().run()}><Italic class="w-4 h-4 text-slate-400 dark:text-slate-500"/> Itálico</button>
                    <button class="px-4 py-2 text-left hover:bg-slate-100 dark:hover:bg-slate-800 flex items-center gap-3 transition-colors" onclick={() => navigator.clipboard.writeText(editor?.state.doc.textBetween(editor.state.selection.from, editor.state.selection.to, ' ') || '')}><Copy class="w-4 h-4 text-slate-400 dark:text-slate-500"/> Copiar</button>
                    <div class="h-px bg-slate-200 dark:bg-slate-700 my-1 mx-2"></div>
                    <button class="px-4 py-2 text-left hover:bg-blue-50 dark:hover:bg-blue-900/30 text-blue-700 dark:text-blue-400 font-medium flex items-center gap-3 transition-colors" onclick={() => sendToChat(editor?.state.doc.textBetween(editor.state.selection.from, editor.state.selection.to, ' ') || '')}><BrainCircuit class="w-4 h-4 text-blue-500 dark:text-blue-400"/> Consultar IA</button>
                    
                    {#if contextMenu.isTable}
                        <div class="h-px bg-slate-200 dark:bg-slate-700 my-1 mx-2"></div>
                        <div class="px-4 py-1.5 text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest bg-slate-50/50 dark:bg-[#0c1324]/50">Ferramentas de Planilha</div>
                        <button class="px-4 py-2 text-left hover:bg-slate-100 dark:hover:bg-slate-800 flex items-center gap-3 transition-colors" onclick={() => editor?.chain().focus().addColumnAfter().run()}>+ Inserir Coluna (Direita)</button>
                        <button class="px-4 py-2 text-left hover:bg-slate-100 dark:hover:bg-slate-800 flex items-center gap-3 transition-colors" onclick={() => editor?.chain().focus().addRowAfter().run()}>+ Inserir Linha (Baixo)</button>
                        <button class="px-4 py-2 text-left hover:bg-rose-50 dark:hover:bg-rose-900/30 text-rose-600 dark:text-rose-400 flex items-center gap-3 transition-colors" onclick={() => editor?.chain().focus().deleteRow().run()}>✖ Deletar Linha</button>
                        <button class="px-4 py-2 text-left hover:bg-rose-50 dark:hover:bg-rose-900/30 text-rose-600 dark:text-rose-400 flex items-center gap-3 transition-colors" onclick={() => editor?.chain().focus().deleteColumn().run()}>✖ Deletar Coluna</button>
                    {/if}
                </div>
            {/if}
        </div>

    </div>

    <!-- Status Bar Footer -->
    <footer class="h-8 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-[#0c1324] flex items-center justify-between px-4 text-[11px] text-slate-500 dark:text-slate-400 font-mono shrink-0 z-50">
        <div class="flex items-center gap-3 truncate max-w-[60%]">
            <span class="truncate" title={documentId}>{documentId}</span>
        </div>
        <div class="flex items-center gap-3 shrink-0">
            <span>{wordCount} words</span>
            <span class="text-slate-300 dark:text-slate-700">|</span>
            <span>{byteCount} bytes</span>
            <span class="text-slate-300 dark:text-slate-700">|</span>
            <span class="text-emerald-600/80 dark:text-emerald-500/80 font-bold uppercase tracking-widest text-[9px]">Sovereign Sync</span>
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
    :global(.sovereign-callout) {
        border-left-width: 4px !important;
        padding: 12px 16px !important;
        margin: 16px 0 !important;
        border-radius: 6px !important;
        font-size: 0.9em;
    }
    :global(.callout-info), :global(.callout-note) { border-left-color: #3b82f6 !important; background-color: #eff6ff !important; color: #1e3a8a !important; }
    :global(.dark .callout-info), :global(.dark .callout-note) { border-left-color: #3b82f6 !important; background-color: rgba(59, 130, 246, 0.1) !important; color: #93c5fd !important; }
    :global(.callout-warning) { border-left-color: #f59e0b !important; background-color: #fffbeb !important; color: #78350f !important; }
    :global(.dark .callout-warning) { border-left-color: #f59e0b !important; background-color: rgba(245, 158, 11, 0.1) !important; color: #fcd34d !important; }
    :global(.callout-danger) { border-left-color: #ef4444 !important; background-color: #fef2f2 !important; color: #7f1d1d !important; }
    :global(.dark .callout-danger) { border-left-color: #ef4444 !important; background-color: rgba(239, 68, 68, 0.1) !important; color: #fca5a5 !important; }
    :global(.callout-success), :global(.callout-tip) { border-left-color: #10b981 !important; background-color: #ecfdf5 !important; color: #064e3b !important; }
    :global(.dark .callout-success), :global(.dark .callout-tip) { border-left-color: #10b981 !important; background-color: rgba(16, 185, 129, 0.1) !important; color: #6ee7b7 !important; }

    /* TipTap Table Styles */
    :global(.tiptap table) {
        border-collapse: collapse;
        table-layout: fixed;
        width: 100%;
        margin: 1rem 0;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border-radius: 6px;
        border-style: hidden;
    }
    :global(.tiptap td), :global(.tiptap th) {
        min-width: 1em;
        border: 1px solid #e2e8f0;
        padding: 8px 12px;
        vertical-align: top;
        box-sizing: border-box;
        position: relative;
    }
    :global(.dark .tiptap td), :global(.dark .tiptap th) {
        border-color: rgba(66, 72, 89, 0.4);
    }
    :global(.tiptap th) {
        font-weight: bold;
        text-align: left;
        background-color: #f8fafc;
    }
    :global(.dark .tiptap th) {
        background-color: rgba(12, 19, 36, 0.6);
        color: #e2e8f0;
    }
    :global(.tiptap .selectedCell:after) {
        z-index: 2;
        position: absolute;
        content: "";
        left: 0; right: 0; top: 0; bottom: 0;
        background: rgba(200, 200, 255, 0.4);
        pointer-events: none;
    }
    :global(.tiptap .column-resize-handle) {
        position: absolute;
        right: -2px;
        top: 0;
        bottom: -2px;
        width: 4px;
        background-color: #3b82f6;
        pointer-events: none;
    }
    :global(.tiptap td a[href^="="]) {
        text-decoration: none !important;
        color: #1e293b !important;
        cursor: text;
        pointer-events: none;
    }
    :global(.tiptap td a[href^="="]::after) {
        content: attr(href);
        background-color: #d1fae5;
        color: #047857;
        font-family: monospace;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 700;
        margin-left: 8px;
        display: inline-block;
        vertical-align: middle;
    }
</style>
