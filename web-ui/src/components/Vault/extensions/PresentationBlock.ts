import { Node, mergeAttributes } from '@tiptap/core'
import { VueNodeViewRenderer } from '@tiptap/vue-3'
import PresentationBlockView from './PresentationBlockView.vue'

export const PresentationBlock = Node.create({
    name: 'presentationBlock',
    group: 'block',
    content: 'block+',
    defining: true,

    parseHTML() {
        return [
            {
                tag: 'div[data-type="presentation-block"]',
            },
        ]
    },

    renderHTML({ HTMLAttributes }) {
        return ['div', mergeAttributes(HTMLAttributes, { 'data-type': 'presentation-block' }), 0]
    },

    addNodeView() {
        return VueNodeViewRenderer(PresentationBlockView)
    },

    addCommands() {
        return {
            setPresentationBlock: () => ({ commands }: any) => {
                return commands.wrapIn('presentationBlock')
            },
            togglePresentationBlock: () => ({ commands }: any) => {
                return commands.toggleWrap('presentationBlock')
            },
        }
    },
})
