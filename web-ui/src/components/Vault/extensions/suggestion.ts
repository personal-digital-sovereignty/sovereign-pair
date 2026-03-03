import { VueRenderer } from '@tiptap/vue-3'
import tippy, { type Instance } from 'tippy.js'
import SlashCommandList from './SlashCommandList.vue'

export default {
    items: ({ query }: { query: string }) => {
        return [
            {
                title: 'Título 1',
                description: 'Cabeçalho Maior',
                icon: '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 12h8"/><path d="M4 18V6"/><path d="M12 18V6"/><path d="m17 12 3-2v8"/></svg>',
                command: ({ editor, range }: any) => {
                    editor.chain().focus().deleteRange(range).setNode('heading', { level: 1 }).run()
                },
            },
            {
                title: 'Título 2',
                description: 'Cabeçalho Intermediário',
                icon: '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 12h8"/><path d="M4 18V6"/><path d="M12 18V6"/><path d="M21 18h-4c0-4 4-3 4-6 0-1.5-2-2.5-4-1"/></svg>',
                command: ({ editor, range }: any) => {
                    editor.chain().focus().deleteRange(range).setNode('heading', { level: 2 }).run()
                },
            },
            {
                title: 'Título 3',
                description: 'Cabeçalho Menor',
                icon: '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 12h8"/><path d="M4 18V6"/><path d="M12 18V6"/><path d="M17.5 10.5c1.7-1 3.5 0 3.5 1.5a2 2 0 0 1-2 2"/><path d="M17 17.5c2 1.5 4 .3 4-1.5a2 2 0 0 0-2-2"/></svg>',
                command: ({ editor, range }: any) => {
                    editor.chain().focus().deleteRange(range).setNode('heading', { level: 3 }).run()
                },
            },
            {
                title: 'Lista de Tarefas',
                description: 'Acompanhar progresso',
                icon: '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" class="text-emerald-500" stroke="currentColor" stroke-width="2"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="m9 12 2 2 4-4"/></svg>',
                command: ({ editor, range }: any) => {
                    editor.chain().focus().deleteRange(range).toggleTaskList().run()
                },
            },
            {
                title: 'Lista de Tópicos',
                description: 'Lista pontuada clássica',
                icon: '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="8" x2="21" y1="6" y2="6"/><line x1="8" x2="21" y1="12" y2="12"/><line x1="8" x2="21" y1="18" y2="18"/><line x1="3" x2="3.01" y1="6" y2="6"/><line x1="3" x2="3.01" y1="12" y2="12"/><line x1="3" x2="3.01" y1="18" y2="18"/></svg>',
                command: ({ editor, range }: any) => {
                    editor.chain().focus().deleteRange(range).toggleBulletList().run()
                },
            },
            {
                title: 'Bloco de Código',
                description: 'Código com Syntax Highlight',
                icon: '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" class="text-indigo-400" stroke="currentColor" stroke-width="2"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>',
                command: ({ editor, range }: any) => {
                    editor.chain().focus().deleteRange(range).toggleCodeBlock().run()
                },
            },
            {
                title: 'Tabela Inteligente',
                description: 'Grade de dados com fórmulas Sensus',
                icon: '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" class="text-sky-500" stroke="currentColor" stroke-width="2"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M3 9h18"/><path d="M3 15h18"/><path d="M9 3v18"/><path d="M15 3v18"/></svg>',
                command: ({ editor, range }: any) => {
                    editor.chain().focus().deleteRange(range).insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run()
                },
            },
            {
                title: 'Apresentação (Slide)',
                description: 'Insere um card 16:9 destacável',
                icon: '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" class="text-amber-500" stroke="currentColor" stroke-width="2"><rect width="20" height="14" x="2" y="3" rx="2"/><line x1="8" x2="16" y1="21" y2="21"/><line x1="12" x2="12" y1="17" y2="21"/></svg>',
                command: ({ editor, range }: any) => {
                    editor.chain().focus().deleteRange(range).setPresentationBlock().run()
                },
            }
        ].filter(item => item.title.toLowerCase().startsWith(query.toLowerCase()))
    },

    render: () => {
        let component: VueRenderer
        let popup: Instance[]

        return {
            onStart: (props: any) => {
                component = new VueRenderer(SlashCommandList, {
                    props,
                    editor: props.editor,
                })

                if (!props.clientRect) {
                    return
                }

                popup = tippy('body', {
                    getReferenceClientRect: props.clientRect,
                    appendTo: () => document.body,
                    content: component.element as Element,
                    showOnCreate: true,
                    interactive: true,
                    trigger: 'manual',
                    placement: 'bottom-start',
                })
            },

            onUpdate(props: any) {
                component.updateProps(props)

                if (!props.clientRect) {
                    return
                }

                popup[0]?.setProps({
                    getReferenceClientRect: props.clientRect,
                })
            },

            onKeyDown(props: any) {
                if (props.event.key === 'Escape') {
                    popup[0]?.hide()
                    return true
                }
                return component.ref?.onKeyDown(props)
            },

            onExit() {
                popup[0]?.destroy()
                component.destroy()
            },
        }
    },
}
