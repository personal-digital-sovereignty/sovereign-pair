<template>
  <node-view-wrapper class="presentation-block-wrapper my-8 relative group">
    <!-- Overlay/Toolbar for the slide -->
    <div class="absolute -top-3 right-4 opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1 z-10 bg-[#1A1A1D] border border-[#333] shadow-lg rounded px-2 py-1">
        <span class="text-[10px] uppercase font-bold text-zinc-500 tracking-wider mr-2">Slide 16:9</span>
    </div>

    <!-- The 16:9 Aspect Ratio Container -->
    <div class="aspect-video w-full max-w-4xl mx-auto rounded-xl border border-zinc-700/50 bg-[#0A0A0B] shadow-2xl overflow-hidden relative presentation-canvas flex flex-col justify-center items-center p-12 lg:p-16 ring-1 ring-white/5">
      <div class="w-full max-w-full prose-h1:text-5xl prose-h1:font-black prose-h1:text-center prose-h1:mb-6 prose-p:text-2xl prose-p:text-center prose-p:text-zinc-300 prose-p:leading-relaxed">
        <node-view-content />
      </div>
    </div>
  </node-view-wrapper>
</template>

<script setup lang="ts">
import { NodeViewWrapper, NodeViewContent, nodeViewProps } from '@tiptap/vue-3'

const props = defineProps(nodeViewProps)
</script>

<style scoped>
/* Optional specific styles for the presentation canvas */
.presentation-canvas {
  background-image: radial-gradient(circle at 50% 50%, rgba(20, 20, 22, 1) 0%, rgba(10, 10, 11, 1) 100%);
}
</style>
