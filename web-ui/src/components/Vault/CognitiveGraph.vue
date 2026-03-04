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
let time = 0


const initGraph = () => {
    if (!graphContainer.value) return

    let hoverNodeId: string | number | null = null
    
    try {
        // Resolve constructor dynamicly
        // @ts-ignore
        const ForceGraphInit = (typeof fgModule.default === 'function') ? fgModule.default : (typeof fgModule === 'function' ? fgModule : fgModule.default?.default)
        if (!ForceGraphInit) return;
        
        // @ts-ignore
        graphInstance = ForceGraphInit()(graphContainer.value)
    } catch (err) {
        console.error("CRITICAL ERROR: Failed to instantiate ForceGraph engine:", err)
        return
    }

    // Sovereign Orbital Constants (Massive Universe Scale)
    const CORE_RADIUS = 30; 
    const CORE_BORDER = 36;
    const INNER_BOUND = 180;   
    const OUTER_BOUND = 1600;  // As órbitas nominais devem permanecer profundamente dentro do limite
    const VISUAL_OUTER_BOUND = 2200; // O grande círculo intransponível (A Borda)

    // Sensus Palette & Cosmic Dust
    const palette = [
        {r: 59, g: 130, b: 246}, // Azul
        {r: 236, g: 72, b: 153}, // Rosa
        {r: 16, g: 185, b: 129}, // Verde
        {r: 249, g: 115, b: 22}, // Laranja
        {r: 250, g: 204, b: 21}  // Creme
    ];
    const getInterpolatedColor = (t: number) => {
        const speed = 0.007; 
        const scaledT = t * speed;
        const index = Math.floor(scaledT) % palette.length;
        const nextIndex = (index + 1) % palette.length;
        const interp = scaledT % 1.0;
        const c1 = palette[index] as {r:number, g:number, b:number};
        const c2 = palette[nextIndex] as {r:number, g:number, b:number};
        return {
            r: Math.round(c1.r + (c2.r - c1.r) * interp),
            g: Math.round(c1.g + (c2.g - c1.g) * interp),
            b: Math.round(c1.b + (c2.b - c1.b) * interp)
        };
    };

    const NUM_DUST = 2500; // Poera densa para preencher o novo vácuo intergalático
    const cosmicDust: any[] = [];
    for(let i=0; i<NUM_DUST; i++) {
        const radius = Math.random() * VISUAL_OUTER_BOUND;
        const angle = Math.random() * Math.PI * 2;
        cosmicDust.push({
            x: Math.cos(angle) * radius,
            y: Math.sin(angle) * radius,
            size: Math.random() * 1.5 + 0.5
        });
    }

    // --- Física Inteligente baseada em Centralidade de Grau ---
    const nodeDegrees = new Map<string | number, number>();
    graphData.value.links.forEach((l: any) => {
        const sid = typeof l.source === 'object' ? l.source.id : l.source;
        const tid = typeof l.target === 'object' ? l.target.id : l.target;
        nodeDegrees.set(sid, (nodeDegrees.get(sid) || 0) + 1);
        nodeDegrees.set(tid, (nodeDegrees.get(tid) || 0) + 1);
    });
    
    let maxConnections = 1;
    nodeDegrees.forEach(val => { if (val > maxConnections) maxConnections = val; });
    const effectiveMax = Math.min(maxConnections, 20); // Normalizador

    // 1. Limpeza de Forças Padrão Inadequadas
    graphInstance.d3Force('center', null); // Sem atração pro centro 0,0
    
    // 2. Repulsão de Espaço Profundo (Ajustado para clusters mais densos)
    graphInstance.d3Force('charge').strength(-300).distanceMax(600); 

    // 3. Força de Conexão (Gravidade Interna das Constelações)
    graphInstance.d3Force('link').distance((link: any) => {
        // Notas fortemente conectadas ficam extremamente coladas
        return link.type === 'hierarchy' ? 40 : 15; 
    }).strength(1.2); // Alta rigidez nos links

    // 4. Física Orbital Customizada (D3) - Mantém orbitando firmemente
    graphInstance.d3Force('orbital', (alpha: number) => {
        graphData.value.nodes.forEach((node: any) => {
            // Atribuir órbita baseada na Conectividade (Clusters pesados no núcleo, Isoladas na borda)
            if (!node.targetOrbit) {
                const connections = nodeDegrees.get(node.id) || 0;
                const connRatio = Math.min(connections / effectiveMax, 1.0); // 1.0 = Hub gigante, 0.0 = Isolado
                const distanceScore = 1.0 - Math.pow(connRatio, 0.7); // Curva matemática que alinha hubs mais ao centro e repele anomalias não-linkadas pra borda da poeira
                
                let hash = 0;
                const nid = node.id || '';
                for (let i = 0; i < nid.length; i++) hash = nid.charCodeAt(i) + ((hash << 5) - hash);
                const normalizedHash = Math.abs(hash) / 2147483647; // Espalhamento de 0 a 1
                
                // Posição final: 85% baseada na gravidade de conexões (afastando pra borda), 15% aleatório
                const orbitFactor = (distanceScore * 0.85) + (normalizedHash * 0.15);
                
                node.targetOrbit = INNER_BOUND + (orbitFactor * (OUTER_BOUND - INNER_BOUND));
                node.orbitSpeed = 0.005 + ((1.0 - orbitFactor) * 0.015); // Clusters massivos giram mais devagar (majestosos)
            }

            const r = Math.sqrt(node.x*node.x + node.y*node.y) || 1;
            
            // Força Radial Absoluta - Puxa agressivamente para a Órbita Alvo
            const radialForce = (node.targetOrbit - r) * 0.3 * alpha;
            node.vx += (node.x / r) * radialForce;
            node.vy += (node.y / r) * radialForce;

            // Velocidade Tangencial Orbital (Rotação Contínua)
            const speed = node.orbitSpeed * alpha;
            node.vx += (-node.y / r) * (r * speed);
            node.vy += (node.x / r) * (r * speed);

            // A MURALHA ABSOLUTA (Limitação Física de Coordenadas)
            // Impede irreversivelmente que qualquer carga de repulsão jogue o cluster para fora da Poeira Cósmica
            const maxAllowedRadius = VISUAL_OUTER_BOUND - 30;
            if (r > maxAllowedRadius) {
                node.x = (node.x / r) * maxAllowedRadius;
                node.y = (node.y / r) * maxAllowedRadius;
                // Rebate a velocidade (Bounce-back)
                node.vx *= -0.8;
                node.vy *= -0.8;
            }
        });
    });

    // Renderização do Core da Galáxia na Camada "Background"
    if (graphInstance.onRenderFramePre) {
        graphInstance.onRenderFramePre((ctx: CanvasRenderingContext2D, globalScale: number) => {
            ctx.save();
            
            const currentColor = getInterpolatedColor(time);
            const rgbStr = `${currentColor.r}, ${currentColor.g}, ${currentColor.b}`;

            const maxPulseRadius = VISUAL_OUTER_BOUND - CORE_RADIUS; 
            const pulseFrequency = 0.008; 
            const ringCount = 4;

            // 0. Cosmic Dust (Poeira Cósmica responsiva ao pulso)
            ctx.save();
            cosmicDust.forEach(dust => {
                const d = Math.sqrt(dust.x*dust.x + dust.y*dust.y);
                let distToPulse = 9999;
                
                for (let i = 0; i < ringCount; i++) {
                    const phase = ((time * pulseFrequency) + (i / ringCount)) % 1.0; 
                    const pulseR = CORE_RADIUS + (phase * maxPulseRadius);
                    distToPulse = Math.min(distToPulse, Math.abs(d - pulseR));
                }

                let dustAlpha = 0.1; // genérico e quase invisível
                let dustColor = '255,255,255';
                
                // Se o pulso do sonar varrer a poeira, ela acende incandescente com a cor rotativa
                if (distToPulse < 50) {
                    const intensity = 1.0 - (distToPulse / 50);
                    dustAlpha = 0.1 + (intensity * 0.9);
                    dustColor = rgbStr;
                }
                
                ctx.beginPath();
                ctx.arc(dust.x, dust.y, dust.size / globalScale, 0, 2 * Math.PI);
                ctx.fillStyle = `rgba(${dustColor}, ${dustAlpha})`;
                ctx.fill();
            });
            ctx.restore();

            // 1. Limite Externo Soberano (Última Linha de Defesa "A Borda")
            // A imagem pede: "A BORDA PRECISA SER MAIS GROSSA E TER AQUELE EFEITO DE POEIRA"
            
            // Efeito Camada de Poeira Grossa Espalhada na Borda
            ctx.beginPath();
            ctx.arc(0, 0, VISUAL_OUTER_BOUND, 0, 2 * Math.PI, false);
            ctx.lineWidth = 80 / globalScale; // Glow massivo de poeira 
            ctx.strokeStyle = `rgba(${rgbStr}, 0.08)`; 
            ctx.stroke();

            // Círculo Limitante Intransponível (Grosso e Denso)
            ctx.beginPath();
            ctx.arc(0, 0, VISUAL_OUTER_BOUND, 0, 2 * Math.PI, false);
            ctx.lineWidth = 12 / globalScale; // Espessura agressiva
            ctx.strokeStyle = `rgba(${rgbStr}, 0.5)`; 
            ctx.stroke();
            
            // 2. Ondas de Pulsação (Vida Digital / Sonar Effect)
            for (let i = 0; i < ringCount; i++) {
                const phase = ((time * pulseFrequency) + (i / ringCount)) % 1.0; 
                // A onda começa no CORE_RADIUS e vai até o VISUAL_OUTER_BOUND exato
                const expandedRadius = CORE_RADIUS + (phase * maxPulseRadius); 
                const ringAlpha = 0.5 * (Math.pow(1.0 - phase, 1.2)); // fading suave
                
                ctx.beginPath();
                ctx.arc(0, 0, expandedRadius, 0, 2 * Math.PI, false);
                ctx.lineWidth = 2 / globalScale; 
                ctx.strokeStyle = `rgba(${rgbStr}, ${ringAlpha})`; 
                ctx.stroke();
            }

            // 3. Aura Estática Concêntrica Dinâmica
            ctx.beginPath();
            ctx.arc(0, 0, CORE_RADIUS + 6, 0, 2 * Math.PI, false);
            ctx.lineWidth = 4 / globalScale;
            ctx.strokeStyle = `rgba(${rgbStr}, 0.3)`; 
            ctx.stroke();

            // 4. Borda Escura Gravitacional
            ctx.beginPath();
            ctx.arc(0, 0, CORE_BORDER, 0, 2 * Math.PI, false);
            ctx.fillStyle = '#021a0c'; 
            ctx.fill();

            // 5. O Núcleo Soberano (Pulsando de Cor Vibrante)
            ctx.beginPath();
            ctx.arc(0, 0, CORE_RADIUS, 0, 2 * Math.PI, false);
            ctx.fillStyle = `rgb(${rgbStr})`; 
            ctx.fill();

            // 6. O 'Olho Brilhante' interno
            ctx.beginPath();
            ctx.arc(0, 0, CORE_RADIUS * 0.4, 0, 2 * Math.PI, false);
            ctx.fillStyle = '#ffffff'; 
            ctx.fill();

            ctx.restore();
        });
    }

    graphInstance
        .graphData(graphData.value)
        .backgroundColor('rgba(0,0,0,0)') // Transparent bg to let Tailwind excel
        .nodeId('id')
        .nodeVal('val')
        .nodeLabel('name')
        .linkColor(() => {
            // As interligações agora pulsam ativamente com a cor primária do sistema num estado fantasmagórico (Sensus Palette)
            const c = getInterpolatedColor(time);
            return `rgba(${c.r}, ${c.g}, ${c.b}, 0.22)`;
        })
        .linkWidth(0.5)
        .linkDirectionalParticles((link: any) => link.type === 'semantic' ? 2 : 0)
        .linkDirectionalParticleSpeed(0.005)
        .linkDirectionalParticleWidth(1.5)
        .linkDirectionalParticleColor(() => {
            const c = getInterpolatedColor(time);
            return `rgba(${c.r}, ${c.g}, ${c.b}, 1)`; // Partículas incandescentes na mesma cor do pulso
        })
        .nodeCanvasObject((node: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
            if (!Number.isFinite(node.x) || !Number.isFinite(node.y)) return;
            
            const label = node.name || 'Unnamed';
            const isFolder = node.type === 'folder';
            const nx = node.x as number;
            const ny = node.y as number;
            
            // Cores Rotativas
            const currentColor = getInterpolatedColor(time);
            const rgbStr = `${currentColor.r}, ${currentColor.g}, ${currentColor.b}`;

            // Tamanhos simples, seguindo proporções limpas do Three.js
            const baseR = Math.max((node.val || 2) * (isFolder ? 1.5 : 1), 2);

            ctx.beginPath();
            ctx.arc(nx, ny, baseR, 0, 2 * Math.PI, false);
            
            if (isFolder) {
                // Folders = Núcleo de Constelação um pouco maior e claro
                ctx.fillStyle = '#ffffff';
                ctx.fill();
                // Halo sutil conectado as cores
                ctx.beginPath();
                ctx.arc(nx, ny, baseR * 2.5, 0, 2 * Math.PI, false);
                ctx.strokeStyle = `rgba(${rgbStr}, 0.5)`;
                ctx.lineWidth = 2 / globalScale;
                ctx.stroke();
            } else {
                // Arquivos e Notas absorvem a cor principal do pulso momentâneo
                ctx.fillStyle = `rgb(${rgbStr})`;
                ctx.fill();
            }

            // Label Renderizando no Hover
            if (node.id === hoverNodeId) {
                const hoverFontSize = Math.max(14 / (globalScale || 1), 4);
                ctx.font = `600 ${hoverFontSize}px Inter, sans-serif`;
                
                const textWidth = ctx.measureText(label).width;
                ctx.fillStyle = 'rgba(0, 0, 0, 0.85)';
                ctx.fillRect(nx - textWidth / 2 - 4, ny + baseR + 4, textWidth + 8, hoverFontSize + 4);
                
                ctx.fillStyle = `rgb(${rgbStr})`; // Texto acompanha o estado fluido de cor
                ctx.textAlign = 'center';
                ctx.textBaseline = 'top';
                ctx.fillText(label, nx, ny + baseR + 6);
            }
        })
        .onNodeHover((node: any) => {
             hoverNodeId = node ? node.id : null;
             if (graphContainer.value) {
                 graphContainer.value.style.cursor = node ? 'pointer' : 'default';
             }
        })
        .onNodeClick((node: any) => {
             if (node.type === 'file') {
                 emit('node-click', node);
             }
             graphInstance.centerAt(node.x, node.y, 1000);
             graphInstance.zoom(4, 2000);
        });

    // Garante que a câmera seja posicionada de maneira que envolva toda a galáxia
    setTimeout(() => {
        graphInstance.centerAt(0, 0, 1000);
        graphInstance.zoomToFit(1000, 50, () => true);
    }, 500);

    // Animation loop para pulsar em tempo real e atualizar a paleta global
    const animate = () => {
        time += 0.05
        if (graphInstance) {
            graphInstance.nodeCanvasObject(graphInstance.nodeCanvasObject()); // Trigger re-render nodes (pulsos e cores fluídas)
            graphInstance.linkColor(graphInstance.linkColor()); // Trigger re-render dinâmico das conexões/links
            graphInstance.linkDirectionalParticleColor(graphInstance.linkDirectionalParticleColor()); // Trigger cor dos pulsos/implosões
        }
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
        
        // Force full redraw para garantir que o onRenderFramePre atualizado seja chamado
        if (graphInstance) {
            graphInstance._destructor()
            const canvasEl = graphContainer.value?.querySelector('canvas')
            if (canvasEl) canvasEl.remove()
        }
        initGraph()
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
