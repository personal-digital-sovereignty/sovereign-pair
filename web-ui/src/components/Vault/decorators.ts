import { Extension } from '@tiptap/core'
import { Plugin, PluginKey } from 'prosemirror-state'
import { Decoration, DecorationSet } from 'prosemirror-view'

/**
 * VaultSyntaxHighlighter
 * Decora visualmente #tags e [[wikilinks]] usando a engine do ProseMirror
 * sem alterar o Node real, preservando 100% o Markdown cru.
 */
export const VaultSyntaxHighlighter = Extension.create({
    name: 'vaultSyntaxHighlighter',

    addProseMirrorPlugins() {
        return [
            new Plugin({
                key: new PluginKey('vaultSyntaxHighlighter'),
                state: {
                    init(_, { doc }) {
                        return getDecorations(doc)
                    },
                    apply(tr, old) {
                        // Em vez de mapear (que pode quebrar dependendo das mudanças locais),
                        // a abordagem bruta de recalcular na view é barata e segura para notas curtas.
                        return tr.docChanged ? getDecorations(tr.doc) : old.map(tr.mapping, tr.doc)
                    },
                },
                props: {
                    decorations(state) {
                        return this.getState(state)
                    },
                },
            }),
        ]
    },
})

function getDecorations(doc: any) {
    const decorations: Decoration[] = []

    doc.descendants((node: any, pos: number) => {
        if (!node.isText) return

        const text = node.text || ''

        // 1. Highlight #tags
        // Regex matches a hashtag that starts at the beginning or after a whitespace
        const tagRegex = /(?:^|\s)(#[a-zA-Z0-9_\-À-ÿ]+)/g
        let match

        while ((match = tagRegex.exec(text)) !== null) {
            // match[1] is the captured #tag
            // we need to find the correct offset by adding the difference in length between match[0] and match[1]
            const m0 = match[0] as string;
            const m1 = match[1] as string;
            const offset = m0.length - m1.length
            const start = pos + (match.index as number) + offset
            const end = start + m1.length

            decorations.push(
                Decoration.inline(start, end, {
                    class: 'text-emerald-400 bg-emerald-500/10 px-1 py-0.5 rounded text-[0.9em] font-medium ring-1 ring-emerald-500/20',
                })
            )
        }

        // 2. Highlight [[wikilinks]]
        const wikilinkRegex = /\[\[(.*?)\]\]/g
        while ((match = wikilinkRegex.exec(text)) !== null) {
            const start = pos + match.index
            const end = start + match[0].length

            decorations.push(
                Decoration.inline(start, end, {
                    class: 'text-violet-400 bg-violet-500/10 px-1 py-0.5 border-b border-violet-500/40 rounded-t font-semibold cursor-pointer hover:bg-violet-500/20 transition-colors',
                })
            )
        }
    })

    return DecorationSet.create(doc, decorations)
}
