<script lang="ts">
    import { onMount, untrack } from 'svelte';
    import * as d3 from 'd3';

    let { nodes = [], links = [], onNodeClick = (n: any) => {}, graphDepth = 5, dataFlowHistory = 100 } = $props();

    let svgContainer: HTMLDivElement;
    let svg: any;
    let simulation: any;

    let tooltip = $state({ show: false, x: 0, y: 0, title: '', type: '' });

    function renderGraph() {
        if (!svgContainer || !nodes.length) return;
        
        const width = svgContainer.clientWidth;
        const height = svgContainer.clientHeight;

        d3.select(svgContainer).selectAll('svg').remove();

        svg = d3.select(svgContainer)
            .append('svg')
            .attr('width', '100%')
            .attr('height', '100%')
            .attr('viewBox', [0, 0, width, height]);

        const container = svg.append('g');

        svg.call(d3.zoom()
            .scaleExtent([0.1, 4])
            .on('zoom', (e) => container.attr('transform', e.transform))
        );

        // Create deep copies to prevent d3 from mutating original store state
        const simNodes = nodes.map(d => ({...d}));
        const simLinks = links.map(d => ({...d}));

        simulation = d3.forceSimulation(simNodes)
            .force('link', d3.forceLink(simLinks).id((d: any) => d.id).distance(120))
            .force('charge', d3.forceManyBody().strength(-400))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collide', d3.forceCollide().radius((d: any) => (d.val * 3) + 15));

        // Synapse Links
        const link = container.append('g')
            .attr('stroke', '#475569') // slate-600
            .attr('stroke-opacity', 0.5)
            .selectAll('line')
            .data(simLinks)
            .join('line')
            .attr('stroke-width', 2);

        // Nodes
        const node = container.append('g')
            .selectAll('circle')
            .data(simNodes)
            .join('circle')
            .attr('r', (d: any) => d.val * 3)
            .attr('fill', (d: any) => d.type === 'folder' ? '#2563eb' : '#10b981')
            .attr('stroke', '#0f172a')
            .attr('stroke-width', 2)
            .on('mouseover', (event: MouseEvent, d: any) => {
                tooltip = { show: true, x: event.pageX, y: event.pageY, title: d.name, type: d.type };
                d3.select(event.currentTarget as Element).attr('stroke', '#f8fafc').attr('stroke-width', 3);
            })
            .on('mousemove', (event: MouseEvent) => {
                tooltip.x = event.pageX + 10;
                tooltip.y = event.pageY + 10;
            })
            .on('mouseout', (event: MouseEvent) => {
                tooltip.show = false;
                d3.select(event.currentTarget as Element).attr('stroke', '#0f172a').attr('stroke-width', 2);
            })
            .on('click', (event: MouseEvent, d: any) => onNodeClick(d))
            .call(drag(simulation));

        // Node Labels
        const labels = container.append('g')
            .selectAll('text')
            .data(simNodes)
            .join('text')
            .text((d: any) => d.name)
            .attr('font-size', '12px')
            .attr('fill', '#94a3b8')
            .attr('dx', (d: any) => (d.val * 3) + 6)
            .attr('dy', 4)
            .attr('pointer-events', 'none')
            .style('text-shadow', '0 1px 3px rgba(0,0,0,0.8)');

        simulation.on('tick', () => {
            link
                .attr('x1', (d: any) => d.source.x)
                .attr('y1', (d: any) => d.source.y)
                .attr('x2', (d: any) => d.target.x)
                .attr('y2', (d: any) => d.target.y);

            node
                .attr('cx', (d: any) => d.x)
                .attr('cy', (d: any) => d.y);
                
            labels
                .attr('x', (d: any) => d.x)
                .attr('y', (d: any) => d.y);
        });
    }

    function drag(simulation: any) {
        return d3.drag()
            .on('start', (event: any, d: any) => {
                if (!event.active) simulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
            })
            .on('drag', (event: any, d: any) => {
                d.fx = event.x;
                d.fy = event.y;
            })
            .on('end', (event: any, d: any) => {
                if (!event.active) simulation.alphaTarget(0);
                d.fx = null;
                d.fy = null;
            });
    }

    $effect(() => {
        // Effect tracks reactive nodes/links (Initial Mount)
        if (nodes.length > 0 && !simulation) {
            untrack(() => {
                renderGraph();
            });
        }
    });

    $effect(() => {
        // React to Graph Depth Slider (Modifies repulsion forces dynamically)
        const depth = Number(graphDepth);
        if (simulation) {
            const linkDistance = 150 - (depth * 15);
            const repelForce = -200 - (depth * 50);
            simulation.force('link').distance(linkDistance);
            simulation.force('charge').strength(repelForce);
            simulation.alpha(0.5).restart();
        }
    });

    $effect(() => {
        // React to Data Flow History (Timetravel nodes by hiding/showing them)
        const history = Number(dataFlowHistory);
        if (svg && nodes.length > 0) {
            const cutoff = Math.max(1, Math.floor(nodes.length * (history / 100)));
            
            svg.selectAll('circle').style('opacity', (d: any, i: number) => i < cutoff ? 1 : 0).style('pointer-events', (d: any, i: number) => i < cutoff ? 'all' : 'none');
            svg.selectAll('text').style('opacity', (d: any, i: number) => i < cutoff ? 1 : 0);
            svg.selectAll('line').style('opacity', (d: any) => {
                return (d.source.index < cutoff && d.target.index < cutoff) ? 0.6 : 0;
            });
        }
    });
</script>

<div class="relative w-full h-full bg-[#0f172a] overflow-hidden" bind:this={svgContainer}>
    {#if tooltip.show}
        <!-- Portal logic is simpler, but absolute is fine for now assuming container spans screen -->
        <div class="fixed z-[9999] px-3 py-2 bg-slate-800/90 backdrop-blur-md text-white text-sm rounded-lg shadow-xl border border-slate-700/50 pointer-events-none transition-opacity duration-100"
             style="left: {tooltip.x}px; top: {tooltip.y}px; transform: translate(-50%, -100%); margin-top: -10px;">
            <div class="font-bold">{tooltip.title}</div>
            <div class="text-slate-400 text-xs uppercase tracking-wider mt-1">{tooltip.type}</div>
        </div>
    {/if}
</div>
