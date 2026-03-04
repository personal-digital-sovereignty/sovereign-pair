<template>
  <div class="relative w-full h-full bg-black overflow-hidden rounded-xl border border-white/5 shadow-2xl">
    
    <!-- Graph Canvas Container -->
    <div ref="graphContainer" class="w-full h-full absolute inset-0"></div>

    <!-- Graph Overlay / Stats -->
    <div class="absolute top-4 left-4 z-10 pointer-events-none flex flex-col gap-1">
      <h2 class="text-white/80 font-medium text-sm flex items-center gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="opacity-60"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
        Sovereign Cognitive Graph
      </h2>
      <p class="text-xs text-white/40 font-mono tracking-wider">
        {{ graphData.nodes.length }} NODES · {{ graphData.links.length }} EDGES
      </p>
    </div>

    <!-- Loading Overlay -->
    <div v-if="isLoading" class="absolute inset-0 bg-surface-900/50 backdrop-blur-sm z-20 flex items-center justify-center pointer-events-none">
        <div class="flex flex-col items-center gap-3">
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" class="animate-spin text-primary-500" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
            <span class="text-sm font-mono tracking-widest text-primary-400/80 animate-pulse">RENDERIZANDO ORB...</span>
        </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import * as fgModule from 'force-graph'

const props = defineProps<{
    width?: number
    height?: number
}>()

const emit = defineEmits(['node-click'])

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const graphContainer = ref<HTMLElement | null>(null)
const isLoading = ref(true)
const graphData = ref({ nodes: [], links: [] })

let graphInstance: any = null
let animationFrameId: number

// Helper para pegar cor do Tema Atual (CSS Vars)
const getThemeColor = (varName: string) => {
    return getComputedStyle(document.documentElement).getPropertyValue(varName).trim() || '#10b981'
}

// Global Glowing Time
let time = 0

const initGraph = () => {
    if (!graphContainer.value) return

    console.log("Initializing Graph with data:", graphData.value.nodes.length, "nodes")
    console.log("Container Dimensions:", graphContainer.value.clientWidth, "x", graphContainer.value.clientHeight)
    if (graphData.value.nodes.length > 0) {
        console.log("Sample node:", graphData.value.nodes[0])
    }

    const primaryColor = getThemeColor('--color-primary-400')
    
    try {
        // Resolve constructor dynamicly
        // @ts-ignore
        const ForceGraphInit = (typeof fgModule.default === 'function') ? fgModule.default : (typeof fgModule === 'function' ? fgModule : fgModule.default?.default)
        
        if (!ForceGraphInit) {
            console.error("ForceGraph constructor not found! Module object:", fgModule)
            return
        }
        
        // @ts-ignore
        graphInstance = ForceGraphInit()(graphContainer.value)
    } catch (err) {
        console.error("CRITICAL ERROR: Failed to instantiate ForceGraph engine:", err)
        return
    }

    graphInstance
        .graphData(graphData.value)
        .backgroundColor('rgba(0,0,0,0)') // Transparent bg to let Tailwind shine
        .nodeId('id')
        .nodeVal('val')
        .nodeLabel('name')
        .linkColor(() => `rgba(255,255,255,0.15)`)
        .linkWidth((link: any) => link.type === 'hierarchy' ? 1.5 : 0.8)
        .linkDirectionalParticles((link: any) => link.type === 'semantic' ? 2 : 0) // Particles flying on semantic links
        .linkDirectionalParticleSpeed(0.005)
        .nodeCanvasObject((node: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
            if (!Number.isFinite(node.x) || !Number.isFinite(node.y)) return;
            
            const label = node.name || 'Unnamed'
            const fontSize = Math.max(12 / (globalScale || 1), 2)
            const isFolder = node.type === 'folder'
            
            // Pulsing logic safely
            const nx = node.x
            const ny = node.y
            const pulse = (time ? Math.sin(time + (node.id?.length || 0)) * 0.15 : 0) + 1.0
            const baseR = Math.max((node.val || 2) * (isFolder ? 1.5 : 1) * pulse, 1)

            ctx.beginPath()
            ctx.arc(nx, ny, baseR, 0, 2 * Math.PI, false)
            
            if (isFolder) {
                ctx.fillStyle = `rgba(255, 255, 255, 0.2)`
                ctx.fill()
                // Outer glow
                ctx.strokeStyle = `rgba(255, 255, 255, 0.4)`
                ctx.lineWidth = 0.5 / globalScale
                ctx.stroke()
            } else {
                // Glow effect for files
                try {
                    const gradient = ctx.createRadialGradient(nx, ny, 0, nx, ny, baseR * 2)
                    gradient.addColorStop(0, primaryColor)
                    gradient.addColorStop(1, 'rgba(0,0,0,0)')
                    
                    ctx.fillStyle = gradient
                    ctx.fill()
                } catch(e) { /* ignore gradient errors if nx/ny corrupt */ }
                
                // Solid core
                ctx.beginPath()
                ctx.arc(nx, ny, baseR * 0.5, 0, 2 * Math.PI, false)
                ctx.fillStyle = '#ffffff'
                ctx.fill()
            }

            // Draw Label
            if (globalScale > 1.5) {
                ctx.font = `${fontSize}px Inter, sans-serif`
                ctx.fillStyle = 'rgba(255, 255, 255, 0.8)'
                ctx.textAlign = 'center'
                ctx.textBaseline = 'top'
                ctx.fillText(label, nx, ny + baseR + 2)
            }
        })
        .onNodeClick((node: any) => {
             // Redireciona via Emissão ou Router
             if (node.type === 'file') {
                 emit('node-click', node)
             }
             // Zoom to node
             graphInstance.centerAt(node.x, node.y, 1000)
             graphInstance.zoom(4, 2000)
        })

    // Animation loop para pulsar em tempo real
    const animate = () => {
        time += 0.05
        if (graphInstance) graphInstance.nodeCanvasObject(graphInstance.nodeCanvasObject()) // Trigger re-render do canvas custom
        animationFrameId = requestAnimationFrame(animate)
    }
    animate()

    handleResize()
}

const handleResize = () => {
    if (graphInstance && graphContainer.value) {
        try {
            const w = Math.max(props.width || graphContainer.value.clientWidth || window.innerWidth || 800, 100)
            const h = Math.max(props.height || graphContainer.value.clientHeight || window.innerHeight || 600, 100)
            graphInstance.width(w)
            graphInstance.height(h)
        } catch(e) {
            console.error("Resize Error on ForceGraph:", e)
        }
    }
}

const fetchData = async () => {
    isLoading.value = true
    try {
        const token = localStorage.getItem('sovereign_token') || ''
        const headers = { 'Authorization': `Bearer ${token}` }
        const res = await fetch(`${API_BASE_URL}/v1/vault/graph`, { headers })
        const data = await res.json()
        graphData.value = data
        
        if (graphInstance) {
            graphInstance.graphData(data)
        } else {
            initGraph()
        }
    } catch(e) {
        console.error("Erro renderizando Grafo", e)
    } finally {
        isLoading.value = false
    }
}

watch(() => props.width, handleResize)
watch(() => props.height, handleResize)

onMounted(() => {
    fetchData()
    window.addEventListener('resize', handleResize)
    
    // Safety check se o container inicia zerado pelo display: none do v-show na aba
    setTimeout(() => {
        handleResize()
        if (graphInstance) {
            graphInstance.zoomToFit(400, 50)
        }
    }, 500)
    setTimeout(() => {
        handleResize()
    }, 2000)
})

onBeforeUnmount(() => {
    if (animationFrameId) cancelAnimationFrame(animationFrameId)
    window.removeEventListener('resize', handleResize)
    if (graphInstance) {
        // cleanup forcegraph if needed.
        graphInstance._destructor && graphInstance._destructor()
    }
})

// Exposing for parent Vue component (like DashboardView)
defineExpose({ handleResize })
</script>
