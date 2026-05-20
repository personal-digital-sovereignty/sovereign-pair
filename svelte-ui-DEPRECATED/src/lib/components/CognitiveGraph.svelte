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
    let mouse = { x: 0, y: 0 }; // Normalizado -1 a 1

    function handleMouseMove(e: MouseEvent) {
        if (tooltip.show) {
            tooltip.x = e.clientX + 15;
            tooltip.y = e.clientY + 15;
        }
        if (container) {
            mouse.x = (e.clientX / container.clientWidth) * 2 - 1;
            mouse.y = -(e.clientY / container.clientHeight) * 2 + 1;
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
                sprite.textHeight = Math.max(6, radius * 1.5);
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

        // Grade Espacial Cibernética (Gravitacional)
        // Substituímos o GridHelper estático por um PlaneGeometry denso pra podermos distorcer os vértices
        const gridGeo = new THREE.PlaneGeometry(3000, 3000, 60, 60);
        gridGeo.rotateX(-Math.PI / 2);
        const gridMat = new THREE.MeshBasicMaterial({ color: 0x00ffff, wireframe: true, transparent: true, opacity: 0.2 });
        const gridMesh = new THREE.Mesh(gridGeo, gridMat);
        gridMesh.position.y = -150;
        Graph.scene().add(gridMesh);

        // Raycaster para pegar a colisão do mouse na rede
        const raycaster = new THREE.Raycaster();

        // Configuração Física Base
        Graph.d3Force('charge').strength(-200 - (Number(graphDepth) * 50));
        Graph.d3Force('link').distance(150 - (Number(graphDepth) * 15));

        // Setup Initial Data
        Graph.graphData({ 
            nodes: JSON.parse(JSON.stringify(nodes)), 
            links: JSON.parse(JSON.stringify(links)) 
        });

        const positionAttribute = gridGeo.getAttribute('position');
        const vertex = new THREE.Vector3();

        // Engine de Rotação Orbital e Físicas de Malha (Preservando O Zoom do Usuário)
        const renderLoop = setInterval(() => {
            if (!Graph) return;

            // --- 1. Distorção Gravitacional da Malha (Cyber-Grid) ---
            raycaster.setFromCamera(mouse, Graph.camera());
            const intersects = raycaster.intersectObject(gridMesh);
            let targetX = 0, targetZ = 0;
            
            // Foco de gravidade (Mouse)
            if (intersects.length > 0) {
                targetX = intersects[0].point.x;
                targetZ = intersects[0].point.z;
            }

            // Ondulação senoidal de fundo + Poço Gravitacional no ponto do mouse
            const time = Date.now() / 400;
            for (let i = 0; i < positionAttribute.count; i++) {
                vertex.fromBufferAttribute(positionAttribute, i);
                
                // Distância do vértice ao alvo do mouse
                const distToMouse = Math.hypot(vertex.x - targetX, vertex.z - targetZ);
                
                // Distorção Profunda tipo "Buraco Negro" 
                let depth = 0;
                if (intersects.length > 0) {
                    depth = -120 * Math.exp(-(distToMouse * distToMouse) / 30000); 
                }

                // Ondas cibernéticas viajando pelo mar de neon
                const ripple = Math.sin(vertex.x / 40 + time) * 8 + Math.cos(vertex.z / 40 + time) * 8;
                
                // Aplica a altura do vértice
                positionAttribute.setY(i, depth + ripple);
            }
            positionAttribute.needsUpdate = true;

            // --- 2. Rotação Orbital ---
            if (autoRotateActive) {
                const camPos = Graph.cameraPosition();
                // Mede a distância atual (permitindo scroll de zoom livre)
                let radius = Math.hypot(camPos.x, camPos.z);
                // Se o radius for zero na inicialização, definimos um padrão mais próximo
                if (!radius || radius < 50) radius = 200; 

                let currentAngle = Math.atan2(camPos.x, camPos.z);
                currentAngle += Math.PI / 4000;

                Graph.cameraPosition({
                    x: radius * Math.sin(currentAngle),
                    y: camPos.y, // Mantém a inclinação Y escolhida pelo usuário
                    z: radius * Math.cos(currentAngle)
                });
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

    // Telemetria do Vault: HUD Top Legend Svelte
    let topCategories = $derived.by(() => {
        const counts: Record<string, {count: number, color: string}> = {};
        nodes.forEach((n: any) => {
            let cat = 'Desconhecido';
            if (n.name) {
                const parts = n.name.split('.');
                if (parts.length > 1) {
                    cat = '.' + parts.pop()!.toUpperCase();
                } else if (n.type === 'folder') {
                    cat = 'DIRETÓRIO';
                } else {
                    cat = 'DOCUMENTO';
                }
            } else {
               cat = n.type ? String(n.type).toUpperCase() : 'NÓ';
            }
            if (!counts[cat]) counts[cat] = { count: 0, color: getNodeColor(n.name || n.id || cat) };
            counts[cat].count++;
        });
        return Object.entries(counts)
            .sort((a,b) => b[1].count - a[1].count)
            .slice(0, 10)
            .map(x => ({ name: x[0], ...x[1]}));
    });
</script>

<!-- Container em tela cheia que captura eventos do Mouse p/ tooltips customizadas Svelte -->
<!-- svelte-ignore a11y_no_static_element_interactions -->
<div 
    bind:this={container} 
    onmousemove={handleMouseMove}
    class="w-full h-full absolute inset-0 cursor-crosshair overflow-hidden rounded-2xl">
</div>

<!-- Glassmorphism Stats HUD (Categorias do Vault) -->
{#if topCategories.length > 0}
<div class="pointer-events-none absolute left-6 top-6 w-60 bg-[#050510]/50 backdrop-blur-xl rounded-xl border border-slate-700/50 p-5 shadow-[0_0_30px_rgba(0,255,255,0.05)] z-10 transition-all text-white">
    <div class="flex items-center gap-2 mb-4 border-b border-slate-700/50 pb-3">
        <div class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_8px_#34d399]"></div>
        <h3 class="text-[11px] font-mono tracking-widest text-slate-300 font-bold uppercase shadow-sm">Vault Taxonomy</h3>
    </div>
    <ul class="flex flex-col gap-2.5">
        {#each topCategories as cat}
            <li class="flex items-center justify-between text-xs font-mono">
                <div class="flex items-center gap-2.5">
                    <span class="w-1.5 h-1.5 rounded-full shadow-[0_0_8px_currentColor]" style="background-color: {cat.color}; color: {cat.color};"></span>
                    <span class="text-slate-300 opacity-90">{cat.name}</span>
                </div>
                <span class="text-slate-400 font-bold tracking-wider">{cat.count}</span>
            </li>
        {/each}
    </ul>
</div>
{/if}

{#if tooltip.show}
    <!-- Tooltip Holográfica do Svelte injetada sobre o WebGL -->
    <div 
        class="fixed z-[9999] px-3 py-2 bg-[#050510]/80 backdrop-blur-md text-[#00ffff] font-mono text-sm rounded-lg shadow-[0_0_15px_#00ffff40] border border-[#00ffff]/50 pointer-events-none transition-all duration-75"
        style="left: {tooltip.x}px; top: {tooltip.y}px;">
        <div class="font-bold tracking-wider">{tooltip.title}</div>
        <div class="text-[#aa00ff] text-[10px] uppercase tracking-widest mt-1">[ {tooltip.type} ]</div>
    </div>
{/if}

