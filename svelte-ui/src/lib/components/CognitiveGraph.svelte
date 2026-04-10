<script lang="ts">
    import { onMount, untrack } from 'svelte';
    import { browser } from '$app/environment';

    // Props originais
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

    function handleMouseMove(e: MouseEvent) {
        if (tooltip.show) {
            tooltip.x = e.clientX + 15;
            tooltip.y = e.clientY + 15;
        }
    }

    // Hash function to assign beautiful neon colors to nodes
    function getNodeColor(str: string) {
        const colors = [
            '#ffaa00', '#00aaff', '#aa00ff', '#ff0055', 
            '#00ff88', '#ff00ff', '#0055ff', '#00ffff'
        ];
        let sum = 0;
        for(let i = 0; i < str.length; i++) sum += str.charCodeAt(i);
        return colors[sum % colors.length];
    }

    onMount(async () => {
        if (!browser || !container) return;
        
        // Dynamic imports para SSR bypass
        const ForceGraph3D = (await import('3d-force-graph')).default;
        const THREE = await import('three');
        // @ts-ignore
        const { UnrealBloomPass } = await import('three/examples/jsm/postprocessing/UnrealBloomPass.js');
        // @ts-ignore
        const SpriteText = (await import('three-spritetext')).default;

        Graph = ForceGraph3D()(container)
            .backgroundColor('#02020a') // Fundo bem escuro
            .onNodeHover((node: any) => {
                if (node) {
                    container.style.cursor = 'pointer';
                    tooltip.title = node.name || node.id;
                    tooltip.type = node.type || 'Cognitive Node';
                    tooltip.show = true;
                    autoRotateActive = false; // Pausa o universo p/ o usuário enxergar
                } else {
                    container.style.cursor = 'crosshair';
                    tooltip.show = false;
                    autoRotateActive = true;
                }
            })
            // Cinemática Cyberpunk Data Flow
            .linkDirectionalParticles(2)
            .linkDirectionalParticleWidth(1.5)
            .linkDirectionalParticleColor((link: any) => getNodeColor(link.source?.name || link.source || "x"))
            .linkDirectionalParticleSpeed(0.005)
            .linkColor(() => 'rgba(0, 255, 255, 0.15)')
            .linkOpacity(0.3)
            .onNodeClick((node: any) => {
                const distance = 80;
                const distRatio = 1 + distance/Math.hypot(node.x, node.y, node.z);
                
                Graph.cameraPosition(
                    { x: node.x * distRatio, y: node.y * distRatio, z: node.z * distRatio }, 
                    node, 
                    1500  
                );
                
                setTimeout(() => {
                    onNodeClick(node);
                }, 1000); 
            })
            // A Magia de Rendering Customizado WebGL
            .nodeThreeObject((node: any) => {
                const group = new THREE.Group();
                const radius = Math.max(2, (node.val || 1) * 1.8);
                const color = getNodeColor(node.name || node.id);
                
                // 1. O Núcleo do Nó Sólido
                const geometry = new THREE.SphereGeometry(radius, 16, 16);
                const material = new THREE.MeshBasicMaterial({ color: color });
                const sphere = new THREE.Mesh(geometry, material);
                group.add(sphere);

                // 2. A Aura de Brilho Translúcida
                const auraGeom = new THREE.SphereGeometry(radius * 1.6, 16, 16);
                const auraMat = new THREE.MeshBasicMaterial({ color: color, transparent: true, opacity: 0.25 });
                const aura = new THREE.Mesh(auraGeom, auraMat);
                group.add(aura);

                // 3. A Placa de Identificação Flutuante
                const sprite = new SpriteText(node.name || node.id);
                sprite.color = 'rgba(255, 255, 255, 0.85)';
                sprite.textHeight = Math.max(3.5, radius * 0.8);
                sprite.position.y = radius + sprite.textHeight + 1; // Flutua sobre a aura
                group.add(sprite);

                return group;
            });

        // Efeito de Neon / Post-Processing Bloom
        const bloomPass = new UnrealBloomPass(
            new THREE.Vector2(window.innerWidth, window.innerHeight), 
            1.2, // strength
            1.0, // radius
            0.1  // threshold
        );
        Graph.postProcessingComposer().addPass(bloomPass);

        // Grade Espacial Cyberpunk (Chão do Grid)
        const gridHelper = new THREE.GridHelper(2000, 100, 0x00ffff, 0x002233);
        gridHelper.position.y = -150; // Joga bem pra baixo da área de colisão da rede
        Graph.scene().add(gridHelper);

        // Configuração Física Base
        Graph.d3Force('charge').strength(-200 - (Number(graphDepth) * 50));
        Graph.d3Force('link').distance(150 - (Number(graphDepth) * 15));

        // Setup Initial Data
        Graph.graphData({ 
            nodes: JSON.parse(JSON.stringify(nodes)), 
            links: JSON.parse(JSON.stringify(links)) 
        });

        // Engine de Rotação
        const renderLoop = setInterval(() => {
            if (Graph && autoRotateActive) {
                // Afasta um pouco mais pra ver o layout majestoso
                Graph.cameraPosition({
                    x: 400 * Math.sin(rotationAngle),
                    y: 50, // Olha ligeiramente de cima
                    z: 400 * Math.cos(rotationAngle)
                });
                rotationAngle += Math.PI / 4000;
            }
        }, 30);

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

    $effect(() => {
        const d = Number(graphDepth);
        if (Graph) {
            Graph.d3Force('charge').strength(-200 - (d * 50));
            Graph.d3Force('link').distance(150 - (d * 15));
            Graph.d3ReheatSimulation();
        }
    });

    $effect(() => {
        const h = Number(dataFlowHistory);
        if (Graph && nodes.length > 0) {
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

