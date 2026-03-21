<script lang="ts">
    import { onMount, unmount } from 'svelte';
    import { Expand, Trash2, ShieldAlert } from 'lucide-svelte';
    import { globalState } from '$lib/state.svelte';

    let { width = 0, height = 0, onNodeClick = (node: any) => {} } = $props();

    let graphContainer: HTMLElement;
    let isLoading = $state(true);
    let graphData: any = $state({ nodes: [], links: [] });
    let contextMenu = $state({ visible: false, x: 0, y: 0, node: null as any });

    let graphInstance: any = null;
    let animationFrameId: number;
    let time = 0;
    let hoverNodeId: string | number | null = null;

    const API_BASE_URL = 'http://localhost:38001';

    // Desktop/UI Click-away for Context Menu
    function closeContextMenu() {
        contextMenu.visible = false;
    }

    $effect(() => {
        const handleClick = () => closeContextMenu();
        window.addEventListener('click', handleClick);
        return () => window.removeEventListener('click', handleClick);
    });

    function handleMenuOpen() {
        if (contextMenu.node && contextMenu.node.type === 'file') {
            onNodeClick(contextMenu.node);
        }
        closeContextMenu();
    }

    async function handleMenuDelete() {
        const node = contextMenu.node;
        if (!node) return;
        
        // Removed original emoji, enforcing strict policy
        if (confirm(`SYSTEM O.R.B: Tem certeza que deseja apagar o recurso gravitacional "${node.name}" permanentemente do disco?`)) {
            try {
                const token = localStorage.getItem('sovereign_token') || '';
                const headers = { 'Authorization': `Bearer ${token}` };
                const res = await fetch(`${API_BASE_URL}/v1/vault/fs/nodes/${node.id}`, { 
                    method: 'DELETE',
                    headers 
                });
                
                if (res.ok) {
                    graphData.nodes = graphData.nodes.filter((n: any) => n.id !== node.id);
                    graphData.links = graphData.links.filter((l: any) => l.source.id !== node.id && l.target.id !== node.id);
                    if (graphInstance) graphInstance.graphData($state.snapshot(graphData));
                }
            } catch(e) {
                console.error("Graph Deletion Error", e);
            }
        }
        closeContextMenu();
    }

    async function initGraph() {
        if (!graphContainer) return;
        try {
            const module = await import('force-graph');
            const ForceGraph = (module.default || module) as any;
            graphInstance = ForceGraph()(graphContainer)
                .minZoom(0.05)
                .maxZoom(8.0);
        } catch (err) {
            console.error("CRITICAL ERROR: Failed to instantiate ForceGraph engine", err);
            return;
        }

        const CORE_RADIUS = 30; 
        const CORE_BORDER = 36;
        const INNER_BOUND = 180;   
        const OUTER_BOUND = 1600;  
        const VISUAL_OUTER_BOUND = 2200; 

        // Sensus Palette
        const palette = [
            {r: 59, g: 130, b: 246},
            {r: 236, g: 72, b: 153},
            {r: 16, g: 185, b: 129},
            {r: 249, g: 115, b: 22},
            {r: 250, g: 204, b: 21} 
        ];

        const getInterpolatedColor = (t: number) => {
            const speed = 0.007; 
            const scaledT = t * speed;
            const index = Math.floor(scaledT) % palette.length;
            const nextIndex = (index + 1) % palette.length;
            const interp = scaledT % 1.0;
            const c1 = palette[index];
            const c2 = palette[nextIndex];
            return {
                r: Math.round(c1.r + (c2.r - c1.r) * interp),
                g: Math.round(c1.g + (c2.g - c1.g) * interp),
                b: Math.round(c1.b + (c2.b - c1.b) * interp)
            };
        };

        const NUM_DUST = 2500;
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

        const nodeDegrees = new Map<string | number, number>();
        graphData.links.forEach((l: any) => {
            const sid = typeof l.source === 'object' ? l.source.id : l.source;
            const tid = typeof l.target === 'object' ? l.target.id : l.target;
            nodeDegrees.set(sid, (nodeDegrees.get(sid) || 0) + 1);
            nodeDegrees.set(tid, (nodeDegrees.get(tid) || 0) + 1);
        });
        
        let maxConnections = 1;
        nodeDegrees.forEach(val => { if (val > maxConnections) maxConnections = val; });
        const effectiveMax = Math.min(maxConnections, 20); 

        graphInstance.d3Force('charge').strength((node: any) => {
            const d = nodeDegrees.get(node.id) || 0;
            return d > 3 ? -500 : -15;
        }).distanceMax(1000); 
        graphInstance.d3Force('link').distance(20).strength(1.5); 

        graphInstance.d3Force('gentle_orbit', (alpha: number) => {
            const currentNodes = graphInstance.graphData().nodes;
            const rootNode = currentNodes.find((n: any) => n.id === 'root');
            const centerX = rootNode ? (rootNode.x || 0) : 0;
            const centerY = rootNode ? (rootNode.y || 0) : 0;

            currentNodes.forEach((node: any) => {
                if (node.id === 'root') return;

                const dx = node.x - centerX;
                const dy = node.y - centerY;
                const r = Math.sqrt(dx*dx + dy*dy) || 1;
                
                const deg = nodeDegrees.get(node.id) || 0;

                if (deg === 0) {
                    const pullForce = (2000 - r) * 0.01 * alpha;
                    node.vx += (dx / r) * pullForce;
                    node.vy += (dy / r) * pullForce;
                } else if (deg > 3) {
                    // Impenetrable Inner Void ONLY applied to Hubs to avoid crushing leaves
                    if (r < 600) {
                        const voidPush = (600 - r) * 0.1 * alpha;
                        node.vx += (dx / r) * voidPush;
                        node.vy += (dy / r) * voidPush;
                    }
                    
                    // Scatter hubs into distinct orbital rings across the solar system (1000px to 1800px)
                    const hash = String(node.id).split('').reduce((a, b) => a + b.charCodeAt(0), 0);
                    const targetBand = 1000 + (hash % 800); 
                    const pullForce = (targetBand - r) * 0.04 * alpha; 
                    node.vx += (dx / r) * pullForce;
                    node.vy += (dy / r) * pullForce;
                } else {
                    // Leaves (deg 1 to 3) have NO hard orbital constraints! 
                    // They just smoothly revolve around their parent hub.
                    // We only prevent them from visually clipping inside the Sun graphic.
                    if (r < 180) {
                        const voidPush = (180 - r) * 0.05 * alpha;
                        node.vx += (dx / r) * voidPush;
                        node.vy += (dy / r) * voidPush;
                    }
                }

                // Smooth galactic rotation (clockwise)
                const speed = 0.0015 * alpha;
                node.vx += (-dy) * speed;
                node.vy += (dx) * speed;
            });
        });

        // ==========================================
        // ABSOLUTE SENSUS PERIMETER (POST-TICK)
        // ==========================================
        graphInstance.onEngineTick(() => {
            const VISUAL_OUTER_BOUND = 2200;
            const maxAllowedRadius = VISUAL_OUTER_BOUND - 40;
            
            const nodes = graphInstance.graphData().nodes;
            const rootNode = nodes.find((n: any) => n.id === 'root');
            const centerX = rootNode ? (rootNode.x || 0) : 0;
            const centerY = rootNode ? (rootNode.y || 0) : 0;

            nodes.forEach((node: any) => {
                if (node.id === 'root') return;
                
                const dx = node.x - centerX;
                const dy = node.y - centerY;
                const r = Math.sqrt(dx*dx + dy*dy) || 1;

                if (r > maxAllowedRadius) {
                    const nx = centerX + (dx / r) * maxAllowedRadius;
                    const ny = centerY + (dy / r) * maxAllowedRadius;
                    node.x = nx;
                    node.y = ny;
                    node.vx *= -0.5;
                    node.vy *= -0.5;
                    // Mathematically override static UI pins if they breached the absolute border
                    if (node.fx !== undefined) node.fx = nx;
                    if (node.fy !== undefined) node.fy = ny;
                }
            });
        });

        if (graphInstance.onRenderFramePre) {
            graphInstance.onRenderFramePre((ctx: CanvasRenderingContext2D, globalScale: number) => {
                ctx.save();
                const currentColor = getInterpolatedColor(time);
                const rgbStr = `${currentColor.r}, ${currentColor.g}, ${currentColor.b}`;
                const maxPulseRadius = VISUAL_OUTER_BOUND - CORE_RADIUS; 
                const pulseFrequency = 0.008; 
                const ringCount = 4;

                const runtimeNodes = graphInstance.graphData().nodes;
                const rootNode = runtimeNodes.find((n: any) => n.id === 'root');
                const centerX = rootNode ? (rootNode.x || 0) : 0;
                const centerY = rootNode ? (rootNode.y || 0) : 0;

                ctx.save();
                cosmicDust.forEach(dust => {
                    const d = Math.sqrt(dust.x*dust.x + dust.y*dust.y);
                    let distToPulse = 9999;
                    for (let i = 0; i < ringCount; i++) {
                        const phase = ((time * pulseFrequency) + (i / ringCount)) % 1.0; 
                        const pulseR = CORE_RADIUS + (phase * maxPulseRadius);
                        distToPulse = Math.min(distToPulse, Math.abs(d - pulseR));
                    }
                    let dustAlpha = 0.1;
                    let dustColor = '255,255,255';
                    if (distToPulse < 50) {
                        const intensity = 1.0 - (distToPulse / 50);
                        dustAlpha = 0.1 + (intensity * 0.9);
                        dustColor = rgbStr;
                    }
                    ctx.beginPath();
                    // dust moves with the scene naturally, we can anchor it to centerX for consistency if needed, 
                    // but for organic look, static cosmic dust is fine. Let's make it follow center.
                    ctx.arc(centerX + dust.x, centerY + dust.y, dust.size / globalScale, 0, 2 * Math.PI);
                    ctx.fillStyle = `rgba(${dustColor}, ${dustAlpha})`;
                    ctx.fill();
                });
                ctx.restore();

                ctx.beginPath();
                ctx.arc(centerX, centerY, VISUAL_OUTER_BOUND, 0, 2 * Math.PI, false);
                ctx.lineWidth = 80 / globalScale; 
                ctx.strokeStyle = `rgba(${rgbStr}, 0.08)`; 
                ctx.stroke();

                ctx.beginPath();
                ctx.arc(centerX, centerY, VISUAL_OUTER_BOUND, 0, 2 * Math.PI, false);
                ctx.lineWidth = 12 / globalScale; 
                ctx.strokeStyle = `rgba(${rgbStr}, 0.5)`; 
                ctx.stroke();
                
                for (let i = 0; i < ringCount; i++) {
                    const phase = ((time * pulseFrequency) + (i / ringCount)) % 1.0; 
                    const expandedRadius = CORE_RADIUS + (phase * maxPulseRadius); 
                    const ringAlpha = 0.5 * (Math.pow(1.0 - phase, 1.2)); 
                    ctx.beginPath();
                    ctx.arc(centerX, centerY, expandedRadius, 0, 2 * Math.PI, false);
                    ctx.lineWidth = 2 / globalScale; 
                    ctx.strokeStyle = `rgba(${rgbStr}, ${ringAlpha})`; 
                    ctx.stroke();
                }

                ctx.beginPath();
                ctx.arc(centerX, centerY, CORE_RADIUS + 6, 0, 2 * Math.PI, false);
                ctx.lineWidth = 4 / globalScale;
                ctx.strokeStyle = `rgba(${rgbStr}, 0.3)`; 
                ctx.stroke();

                ctx.beginPath();
                ctx.arc(centerX, centerY, CORE_BORDER, 0, 2 * Math.PI, false);
                ctx.fillStyle = '#021a0c'; 
                ctx.fill();

                ctx.beginPath();
                ctx.arc(centerX, centerY, CORE_RADIUS, 0, 2 * Math.PI, false);
                ctx.fillStyle = `rgb(${rgbStr})`; 
                ctx.fill();

                ctx.beginPath();
                ctx.arc(centerX, centerY, CORE_RADIUS * 0.4, 0, 2 * Math.PI, false);
                ctx.fillStyle = '#ffffff'; 
                ctx.fill();

                ctx.restore();
            });
        }

        graphInstance
            .graphData($state.snapshot(graphData))
            .backgroundColor('rgba(0,0,0,0)')
            .nodeId('id')
            .nodeVal('val')
            .linkColor(() => {
                const c = getInterpolatedColor(time);
                return `rgba(${c.r}, ${c.g}, ${c.b}, 0.22)`;
            })
            .linkWidth(0.5)
            .linkDirectionalParticles((link: any) => link.type === 'semantic' ? 2 : 0)
            .linkDirectionalParticleSpeed(0.005)
            .linkDirectionalParticleWidth(1.5)
            .linkDirectionalParticleColor(() => {
                const c = getInterpolatedColor(time);
                return `rgba(${c.r}, ${c.g}, ${c.b}, 1)`;
            })
            .nodeCanvasObject((node: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
                if (!Number.isFinite(node.x) || !Number.isFinite(node.y)) return;
                
                const label = node.name || 'Unnamed';
                const isFolder = node.type === 'folder';
                const nx = node.x as number;
                const ny = node.y as number;
                
                const currentColor = getInterpolatedColor(time);
                const rgbStr = `${currentColor.r}, ${currentColor.g}, ${currentColor.b}`;
                const baseR = Math.max((node.val || 2) * (isFolder ? 1.5 : 1), 2);

                ctx.beginPath();
                ctx.arc(nx, ny, baseR, 0, 2 * Math.PI, false);
                
                if (isFolder) {
                    ctx.fillStyle = '#ffffff';
                    ctx.fill();
                    ctx.beginPath();
                    ctx.arc(nx, ny, baseR * 2.5, 0, 2 * Math.PI, false);
                    ctx.strokeStyle = `rgba(${rgbStr}, 0.5)`;
                    ctx.lineWidth = 2 / globalScale;
                    ctx.stroke();
                } else {
                    ctx.fillStyle = `rgb(${rgbStr})`;
                    ctx.fill();
                }

                if (node.id === hoverNodeId) {
                    const hoverFontSize = Math.max(14 / (globalScale || 1), 4);
                    ctx.font = `600 ${hoverFontSize}px Inter, sans-serif`;
                    const textWidth = ctx.measureText(label).width;
                    
                    ctx.fillStyle = 'rgba(10, 10, 12, 0.90)';
                    ctx.beginPath();
                    ctx.roundRect(nx - textWidth / 2 - 6, ny + baseR + 2, textWidth + 12, hoverFontSize + 8, 4);
                    ctx.fill();
                    
                    ctx.fillStyle = 'rgba(255, 255, 255, 0.95)';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'top';
                    ctx.fillText(label, nx, ny + baseR + 6);
                }
            })
            .onNodeHover((node: any) => {
                 hoverNodeId = node ? node.id : null;
                 if (graphContainer) {
                     graphContainer.style.cursor = node ? 'pointer' : 'default';
                 }
            })
            .onNodeClick((node: any) => {
                 closeContextMenu();
                 if (node.type === 'file') {
                     onNodeClick(node);
                 }
                 graphInstance.centerAt(node.x, node.y, 1000);
                 graphInstance.zoom(4, 2000);
            })
            .onNodeRightClick((node: any, event: MouseEvent) => {
                 event.preventDefault();
                 const rect = graphContainer?.getBoundingClientRect();
                 if (rect) {
                    contextMenu.visible = true;
                    contextMenu.x = event.clientX - rect.left;
                    contextMenu.y = event.clientY - rect.top;
                    contextMenu.node = node;
                 }
            })
            .onNodeDrag((node: any) => {
                // UI Level Clamp: Resists the user dragging it completely out
                if (node.id === 'root') return;
                const nodes = graphInstance.graphData().nodes;
                const rootNode = nodes.find((n: any) => n.id === 'root');
                const centerX = rootNode ? (rootNode.x || 0) : 0;
                const centerY = rootNode ? (rootNode.y || 0) : 0;
                const dx = node.x - centerX;
                const dy = node.y - centerY;
                const r = Math.sqrt(dx*dx + dy*dy) || 1;
                const maxAllowedRadius = 2200 - 40;
                if (r > maxAllowedRadius) {
                    node.fx = centerX + (dx / r) * maxAllowedRadius;
                    node.fy = centerY + (dy / r) * maxAllowedRadius;
                }
            })
            .onNodeDragEnd((node: any) => {
                // Unpin nodes on drop to restore gorgeous fluid dynamics!
                if (node.id !== 'root') {
                    node.fx = undefined;
                    node.fy = undefined;
                }
            });

        setTimeout(() => {
            graphInstance.centerAt(0, 0, 1000);
            if ($state.snapshot(graphData).nodes.length > 2) {
                graphInstance.zoomToFit(1000, 50, () => true);
            } else {
                graphInstance.zoom(1.5, 1000);
            }
        }, 500);

        const animate = () => {
            time += 0.05;
            if (graphInstance) {
                graphInstance.nodeCanvasObject(graphInstance.nodeCanvasObject());
                graphInstance.linkColor(graphInstance.linkColor());
                graphInstance.linkDirectionalParticleColor(graphInstance.linkDirectionalParticleColor());
            }
            animationFrameId = requestAnimationFrame(animate);
        };
        animate();
        handleResize();
    }

    function handleResize() {
        if (graphInstance && graphContainer) {
            try {
                const w = Math.max(width || graphContainer.clientWidth || window.innerWidth || 800, 100);
                const h = Math.max(height || graphContainer.clientHeight || window.innerHeight || 600, 100);
                graphInstance.width(w);
                graphInstance.height(h);
            } catch(e) { /* ignore */ }
        }
    }

    async function fetchData() {
        isLoading = true;
        try {
            const token = localStorage.getItem('sovereign_token') || '';
            const ws_id = globalState.activeWorkspaceId || 'default';
            const res = await fetch(`${API_BASE_URL}/v1/vault/graph?workspace_id=${ws_id}`, { headers: { 'Authorization': `Bearer ${token}` } });
            
            // Allow mock fallback if backend disconnected
            if (res.ok) {
                graphData = await res.json();
            } else {
                graphData = {
                    nodes: [{id: "1", name: "Sovereign Node", type: "folder", val: 5}],
                    links: []
                };
            }
            
            if (graphInstance) {
                graphInstance._destructor();
                const canvasEl = graphContainer?.querySelector('canvas');
                if (canvasEl) canvasEl.remove();
            }
            initGraph();
        } catch(e) {
            console.error(e);
        } finally {
            isLoading = false;
        }
    }

    $effect(() => {
        handleResize();
    });

    // Re-fetch data instantly when Active Workspace changes
    import { untrack } from 'svelte';
    $effect(() => {
        const _trigger = globalState.activeWorkspaceId;
        untrack(() => {
            if (!isLoading && graphContainer) {
                fetchData();
            }
        });
    });

    onMount(() => {
        fetchData();
        window.addEventListener('resize', handleResize);
        setTimeout(() => {
            handleResize();
            if (graphInstance) graphInstance.zoomToFit(400, 50);
        }, 500);
    });

</script>

<div bind:clientWidth={width} bind:clientHeight={height} class="relative w-full h-full bg-black overflow-hidden rounded-xl border border-white/5 shadow-2xl">
    
    <div bind:this={graphContainer} class="w-full h-full absolute inset-0"></div>

    <div class="absolute top-4 left-4 z-10 pointer-events-none flex flex-col gap-1">
      <h2 class="text-white/60 font-medium text-xs flex items-center gap-2">
        <ShieldAlert size={14} class="opacity-60" />
        Sovereign Cognitive Graph
      </h2>
      <p class="text-[10px] text-white/40 font-mono tracking-widest uppercase pl-5">
        {graphData.nodes.length} NODES · {graphData.links.length} EDGES
      </p>
    </div>

    {#if Object.keys(contextMenu).length > 0 && contextMenu.visible}
      <!-- svelte-ignore a11y_click_events_have_key_events -->
      <!-- svelte-ignore a11y_no_static_element_interactions -->
      <div 
        style="top: {contextMenu.y}px; left: {contextMenu.x}px"
        class="absolute z-50 w-48 bg-surface-800 border border-surface-700 shadow-2xl rounded-lg py-1 text-sm overflow-hidden"
        onclick={(e) => e.stopPropagation()}
      >
        <div class="px-3 py-2 border-b border-surface-700/50">
          <p class="text-[10px] font-bold tracking-wider text-surface-400 uppercase truncate" title={contextMenu.node?.name}>
            {contextMenu.node?.name || 'NODE UNKNOWN'}
          </p>
        </div>
        
        {#if contextMenu.node?.type === 'file'}
        <button 
          onclick={handleMenuOpen} 
          class="w-full text-left px-3 py-2 text-surface-200 hover:bg-surface-700 hover:text-white flex items-center gap-2 transition-colors cursor-pointer"
        >
          <Expand class="w-3.5 h-3.5" />
          Abrir Conhecimento
        </button>
        {/if}

        <div class="h-px bg-surface-700 w-full my-1"></div>

        <button 
          onclick={handleMenuDelete} 
          class="w-full text-left px-3 py-2 text-red-400 hover:bg-red-500/10 hover:text-red-300 flex items-center gap-2 transition-colors cursor-pointer"
        >
          <Trash2 class="w-3.5 h-3.5" />
          Excluir Registro O.S
        </button>
      </div>
    {/if}

    {#if isLoading}
    <div class="absolute inset-0 bg-surface-900/50 backdrop-blur-sm z-20 flex items-center justify-center pointer-events-none">
        <div class="flex flex-col items-center gap-3">
            <ShieldAlert class="w-8 h-8 animate-spin text-primary-500" />
            <span class="text-sm font-mono tracking-widest text-primary-400/80 animate-pulse">RENDERIZANDO ORB...</span>
        </div>
    </div>
    {/if}

</div>
