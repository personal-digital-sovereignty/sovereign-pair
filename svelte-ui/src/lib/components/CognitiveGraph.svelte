<script lang="ts">
    import { onMount, untrack } from 'svelte';
    import { browser } from '$app/environment';

    // Props originais provenientes de /graph/+page.svelte
    let { 
        nodes = [], 
        links = [], 
        onNodeClick = (n: any) => {}, 
        graphDepth = 5, 
        dataFlowHistory = 100 
    } = $props();

    let container: HTMLDivElement;
    let Graph: any;
    let resizeObserver: ResizeObserver;
    
    let tooltip = $state({ show: false, x: 0, y: 0, title: '', type: '' });
    let rotationAngle = 0;
    let autoRotateActive = true;

    // Trackeia mouse para o Tooltip HTML em cima do Canvas WebGL
    function handleMouseMove(e: MouseEvent) {
        if (tooltip.show) {
            tooltip.x = e.clientX + 15;
            tooltip.y = e.clientY + 15;
        }
    }

    onMount(async () => {
        if (!browser || !container) return;
        
        // Importa Dinamicamente apenas no ClientSide para não quebrar SSR do SvelteKit
        const ForceGraph3D = (await import('3d-force-graph')).default;

        Graph = ForceGraph3D()(container)
            .backgroundColor('#050510') // Espaço Sideral Cibernético
            .nodeColor(node => node.type === 'folder' ? '#aa00ff' : '#00ffff')
            .nodeVal(node => Math.max(2, (node.val || 1) * 1.5))
            .nodeResolution(16)
            .nodeLabel(() => '') // Oculta a nativa pois usaremos HUD Svelte
            .onNodeHover((node: any) => {
                if (node) {
                    container.style.cursor = 'pointer';
                    tooltip.title = node.name || node.id;
                    tooltip.type = node.type || 'Cognitive Node';
                    tooltip.show = true;
                    autoRotateActive = false; // Pausa rotação
                } else {
                    container.style.cursor = 'crosshair';
                    tooltip.show = false;
                    autoRotateActive = true;
                }
            })
            // Cinemática Cyberpunk
            .linkDirectionalParticles(4)
            .linkDirectionalParticleWidth(2)
            .linkDirectionalParticleColor(() => '#00ffff')
            .linkDirectionalParticleSpeed(0.006)
            .linkColor(() => 'rgba(0, 255, 255, 0.2)')
            .linkOpacity(0.3)
            .onNodeClick((node: any) => {
                // Vôo de Câmera (Raycaster)
                const distance = 80;
                const distRatio = 1 + distance/Math.hypot(node.x, node.y, node.z);
                
                Graph.cameraPosition(
                    { x: node.x * distRatio, y: node.y * distRatio, z: node.z * distRatio }, 
                    node, // Alvo
                    1500  // Duração ms
                );
                
                // Dispara o evento de clique após o voo iniciar
                setTimeout(() => {
                    onNodeClick(node);
                }, 1000); // Trigger navegação na metade do voo
            });

        // Configuração de Física D3 Subjacente (Puxando a UI Depth)
        Graph.d3Force('charge').strength(-200 - (Number(graphDepth) * 50));
        Graph.d3Force('link').distance(150 - (Number(graphDepth) * 15));

        // Dados Iniciais
        Graph.graphData({ 
            nodes: JSON.parse(JSON.stringify(nodes)), 
            links: JSON.parse(JSON.stringify(links)) 
        });

        // Efeito Cinemático Contínuo de Rotação (A Mágica da Imagem)
        const renderLoop = setInterval(() => {
            if (Graph && autoRotateActive) {
                Graph.cameraPosition({
                    x: 300 * Math.sin(rotationAngle),
                    z: 300 * Math.cos(rotationAngle)
                });
                rotationAngle += Math.PI / 3000;
            }
        }, 30);

        // Responsividade do Canvas
        resizeObserver = new ResizeObserver(() => {
            if (Graph && container) {
                Graph.width(container.clientWidth);
                Graph.height(container.clientHeight);
            }
        });
        resizeObserver.observe(container);

        return () => {
            clearInterval(renderLoop);
            if (resizeObserver) resizeObserver.disconnect();
            if (Graph) Graph._destructor();
        };
    });

    // Reatividade de Sincronia de Dados (Se RAG Atualizar)
    $effect(() => {
        if (Graph && nodes.length > 0) {
            untrack(() => {
                Graph.graphData({ 
                    nodes: JSON.parse(JSON.stringify(nodes)), 
                    links: JSON.parse(JSON.stringify(links)) 
                });
            });
        }
    });

    // Reatividade Depth
    $effect(() => {
        const d = Number(graphDepth);
        if (Graph) {
            Graph.d3Force('charge').strength(-200 - (d * 50));
            Graph.d3Force('link').distance(150 - (d * 15));
            Graph.d3ReheatSimulation();
        }
    });

    // Reatividade Timetravel
    $effect(() => {
        const h = Number(dataFlowHistory);
        if (Graph && nodes.length > 0) {
            // Recorta dados limitando pelo tempo
            const cutoff = Math.max(1, Math.floor(nodes.length * (h / 100)));
            const visibleNodes = nodes.slice(0, cutoff);
            const visibleIds = new Set(visibleNodes.map((n: any) => n.id));
            const visibleLinks = links.filter((l: any) => visibleIds.has(l.source?.id || l.source) && visibleIds.has(l.target?.id || l.target));
            
            untrack(() => {
                 Graph.graphData({ 
                    nodes: JSON.parse(JSON.stringify(visibleNodes)), 
                    links: JSON.parse(JSON.stringify(visibleLinks)) 
                });
            });
        }
    });
</script>

<!-- Container em tela cheia que captura eventos do Mouse p/ tooltips customizadas Svelte -->
<!-- svelte-ignore a11y_no_static_element_interactions -->
<div 
    bind:this={container} 
    onmousemove={handleMouseMove}
    class="w-full h-full absolute inset-0 cursor-crosshair overflow-hidden rounded-2xl">
</div>

{#if tooltip.show}
    <!-- Tooltip Holográfica do Svelte injetada sobre o WebGL -->
    <div 
        class="fixed z-[9999] px-3 py-2 bg-[#050510]/80 backdrop-blur-md text-[#00ffff] font-mono text-sm rounded-lg shadow-[0_0_15px_#00ffff40] border border-[#00ffff]/50 pointer-events-none transition-all duration-75"
        style="left: {tooltip.x}px; top: {tooltip.y}px;">
        <div class="font-bold tracking-wider">{tooltip.title}</div>
        <div class="text-[#aa00ff] text-[10px] uppercase tracking-widest mt-1">[ {tooltip.type} ]</div>
    </div>
{/if}

