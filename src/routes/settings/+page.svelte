<script lang="ts">
    import { ChevronDown, Server, Cpu, Shield, User, GlobeLock, Cloud, Download, Upload, Brain, SlidersHorizontal, Loader2, BookOpen, Printer, X, Database } from 'lucide-svelte';
    import { onMount } from 'svelte';
    import { marked } from 'marked';

    let expandedCard = $state<string | null>('mesh');

    function toggleCard(cardId: string) {
        expandedCard = expandedCard === cardId ? null : cardId;
    }

    // Mock profiles based on Mesh Router engine
    let activeNodes = [
        { id: '1', hostname: 'oracle-a1-max', role: 'The Doctor', hardware: '24GB RAM, ARM64', location: 'Cloud' },
        { id: '2', hostname: 'ryzen-local-alpha', role: 'The Coder (Sandbox)', hardware: '32GB RAM, Ryzen 9', location: 'Local Network' }
    ];

    let aiSettings = $state({
        nurse_model: "qwen2.5:3b",
        doctor_model: "qwen2.5:3b",
        coder_model: "qwen2.5:3b",
        temperature: 0.7,
        top_k: 40,
        system_prompt: "",
        default_route: "/dashboard"
    });

    // Mock Offline Corpora Settings
    let corporaVaultPath = $state('/Vault/Offline_Corpus');
    let offlineCorpora = $state([
        { id: 'fineweb', name: 'FineWeb / FineWeb-Edu (Parquet)', size: '2.4 TB', active: false, priority: 1, type: 'HuggingFace' },
        { id: 'oscar', name: 'OSCAR Corpus (JSONL)', size: '850 GB', active: false, priority: 2, type: 'Multilingual' },
        { id: 'redpajama', name: 'RedPajama-Data-v2', size: '1.2 TB', active: false, priority: 3, type: 'Web Crawl' },
        { id: 'zim-wiki', name: 'Wikipedia Integral (Kiwix ZIM)', size: '98 GB', active: true, priority: 4, type: 'ZIM Dump' },
        { id: 'zim-stack', name: 'StackOverflow (Kiwix ZIM)', size: '145 GB', active: false, priority: 5, type: 'ZIM Dump' },
        { id: 'zim-pubmed', name: 'PubMed Central (Kiwix ZIM)', size: '320 GB', active: false, priority: 6, type: 'ZIM Dump' }
    ]);

    let availableModels = $state<{name: string, size: number}[]>([]);
    let isLoadingModels = $state(true);

    const PREDEFINED_PERSONAS = [
        { label: "1. The Sovereign Practitioner (Padrão)", prompt: "" },
        { label: "2. The Code Architect (Engenheiro Sênior)", prompt: "Você é O Arquiteto de Código. Forneça código impecável, idiomático e altamente documentado. Otimize para complexidade de tempo O(1) quando possível. Recuse-se a escrever algoritmos inseguros ou com bugs." },
        { label: "3. The Security Auditor (DevSecOps)", prompt: "Você é um Auditor de Segurança implacável. Analise todas as consultas em busca de falhas de injeção, condições de corrida, vazamentos de memória e riscos de dependência. Assuma que tudo é vulnerável até prova em contrário." },
        { label: "4. The Financial Analyst (Quant)", prompt: "Você é um analista financeiro quantitativo. Foco estritamente em margens, taxas de juros compostos, distribuições estatísticas e análise de P/L. Formate as respostas em tabelas rigorosas e conclusões em tópicos." },
        { label: "5. The Visual Engineer (UX/UI)", prompt: "Você é um maestro de UX/UI especializado em TailwindCSS V4 e Svelte 5. Priorize uma estética com precisão de pixels, micro-animações, glassmorfismo e acessibilidade responsiva." },
        { label: "6. The DevOps General (Cloud Arch)", prompt: "Você é um General DevOps. Fale em termos de YAMLs do Kubernetes, estados do Terraform, redes Docker, pipelines de CI/CD e clusters de alta disponibilidade. Mantenha a latência fora da equação." },
        { label: "7. The Creative Mind (Copywriter)", prompt: "Você é uma Mente Criativa lendária. Teça palavras como mágica. Use metáforas, narrativas atraentes e ganchos profundamente emotivos para capturar a atenção absoluta do leitor." },
        { label: "8. The Legal Counsel (Compliance)", prompt: "Você é O Consultor Jurídico. Elabore contratos, revise os termos de serviço e navegue pelas leis de conformidade (GDPR, LGPD) com absoluta rigidez e taxonomia formal." },
        { label: "9. The Maestro (Musician/Audio Eng)", prompt: "Você é o Maestro. Especialista em teoria musical, mixagem de áudio, masterização, engenharia de som e composição. Entende de formações harmônicas complexas e equipamentos de áudio profissionais." }
    ];

    onMount(async () => {
        // Fetch Settings
        try {
            const res = await fetch('http://localhost:38001/v1/settings');
            if (res.ok) {
                const data = await res.json();
                if (data.nurse_model) aiSettings.nurse_model = data.nurse_model;
                if (data.doctor_model) aiSettings.doctor_model = data.doctor_model;
                if (data.coder_model) aiSettings.coder_model = data.coder_model;
                if (data.temperature !== undefined) aiSettings.temperature = data.temperature;
                if (data.top_k !== undefined) aiSettings.top_k = data.top_k;
                if (data.system_prompt) aiSettings.system_prompt = data.system_prompt;
                if (data.default_route) aiSettings.default_route = data.default_route;
            }
        } catch(e) { console.error("Agent offline:", e); }

        // Fetch Dynamic Models from Mesh Target
        try {
            const mRes = await fetch('http://localhost:38001/v1/system/available_models');
            if (mRes.ok) {
                const data = await mRes.json();
                if (data.models) {
                    availableModels = data.models.map((m: any) => ({ name: m.name, size: m.size }));
                }
            }
        } catch(e) { console.error("Ollama Daemon unreachable:", e); } finally {
            isLoadingModels = false;
        }

        // Fetch Cold Storage Database
        try {
            const csRes = await fetch('http://localhost:38001/v1/settings/cold_storage');
            if (csRes.ok) {
                const data = await csRes.json();
                if (data.corporaVaultPath) corporaVaultPath = data.corporaVaultPath;
                if (data.offlineCorpora && data.offlineCorpora.length > 0) offlineCorpora = data.offlineCorpora;
            }
        } catch(e) { console.error("Cold Storage DB unreachable:", e); }

    });

    async function saveAiSettings() {
        try {
            const res = await fetch('http://localhost:38001/v1/settings');
            let data = res.ok ? await res.json() : {};
            
            data.nurse_model = aiSettings.nurse_model;
            data.doctor_model = aiSettings.doctor_model;
            data.coder_model = aiSettings.coder_model;
            data.temperature = Number(aiSettings.temperature);
            data.top_k = Number(aiSettings.top_k);
            data.system_prompt = aiSettings.system_prompt;
            data.default_route = aiSettings.default_route;
            
            const postRes = await fetch('http://localhost:38001/v1/settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            
            if (postRes.ok) {
                alert('AI Core Settings Synchronized!');
            }
        } catch(e) { 
            console.error(e);
            alert('Failed to reach Sovereign Core.');
        }
    }

    async function saveColdStorage() {
        try {
            const res = await fetch('http://localhost:38001/v1/settings/cold_storage', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    corporaVaultPath,
                    offlineCorpora
                })
            });
            if (res.ok) alert('Sovereign Cold Storage Sincronizado com o Vault O.S!');
        } catch (e) {
            console.error(e);
            alert('Falha ao sincronizar Cold Storage.');
        }
    }

    let fileInput: HTMLInputElement | undefined = $state(undefined);

    async function handleFileImport(e: Event) {
        const input = e.target as HTMLInputElement;
        if (!input.files || input.files.length === 0) return;
        
        const file = input.files[0];
        const reader = new FileReader();
        reader.onload = async (e) => {
            const content = e.target?.result as string;
            try {
                const res = await fetch('http://localhost:38001/v1/system/import_config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'text/plain' },
                    body: content
                });
                if (res.ok) {
                    alert('Sovereign Cortex successfully imported. The system and mesh nodes are synchronized.');
                    window.location.reload();
                } else {
                    alert('Failed to absorb Cybrid Cortex. File may be corrupted.');
                }
            } catch (err) {
                console.error(err);
                alert('P2P Hub offline or unreachable.');
            }
        };
        reader.readAsText(file);
    }


</script>

<div class="h-full w-full max-w-4xl mx-auto p-4 md:p-8 flex flex-col gap-6 overflow-y-auto">
    
    <!-- Settings Header -->
    <header class="flex flex-col gap-1 mb-2">
        <h1 class="text-2xl md:text-3xl font-bold tracking-tight text-surface-50">Sovereign Settings</h1>
        <p class="text-surface-400 text-sm">Configure Identity, Telemetry, and Mesh Sandboxes</p>
    </header>

    <!-- Material/iOS Style Cards -->
    <main class="flex flex-col gap-4 pb-12">
        
        <!-- CARD 1: Identity -->
        <section class="bg-surface-800/80 backdrop-blur-md rounded-2xl border border-surface-700/50 overflow-hidden shadow-lg transition-all duration-300">
            <button class="w-full flex items-center justify-between p-5 text-left hover:bg-surface-700/30 cursor-pointer" onclick={() => toggleCard('identity')}>
                <div class="flex items-center gap-4">
                    <div class="p-2 bg-primary-500/20 text-primary-400 rounded-lg">
                        <User class="w-6 h-6" />
                    </div>
                    <div>
                        <h2 class="font-semibold text-surface-100 text-lg">Sovereign Identity</h2>
                        <p class="text-sm text-surface-400">Master user, Pin Codes, UI Preferences</p>
                    </div>
                </div>
                <ChevronDown class="w-5 h-5 text-surface-500 transition-transform duration-300 transform {expandedCard === 'identity' ? 'rotate-180' : ''}" />
            </button>
            {#if expandedCard === 'identity'}
            <div class="p-5 border-t border-surface-700/50 bg-surface-900/30 flex flex-col gap-4">
                <p class="text-sm text-surface-400">Manage your local Identity parameters and export your entire Sovereign configuration to securely roam between multiple nodes.</p>
                
                <div class="bg-surface-800 p-4 rounded-xl border border-surface-700 flex flex-col gap-3">
                    <h3 class="text-surface-200 font-bold text-sm tracking-widest uppercase mb-1">Cortex Continuity (Backup)</h3>
                    <p class="text-xs text-surface-400 mb-2">A file with the `.cybrid` extension contains fully encrypted O.S State (Global Workspaces, Mesh Keys, Node Preferences) to instantly synchronize a new machine.</p>
                    
                    <input type="file" bind:this={fileInput} accept=".cybrid" class="hidden" onchange={handleFileImport} />

                    <div class="flex gap-2 w-full">
                        <button onclick={() => fileInput?.click()} class="flex-1 py-2 rounded-lg bg-surface-700 text-surface-200 hover:bg-surface-600 transition-colors flex items-center justify-center gap-2 cursor-pointer border border-surface-600">
                            <Upload class="w-4 h-4" />
                            <span class="text-sm">Import Config</span>
                        </button>
                        <a href="http://localhost:38001/v1/system/export_config" target="_blank" class="flex-1 py-2 rounded-lg bg-primary-600 text-white hover:bg-primary-500 transition-colors flex items-center justify-center gap-2 cursor-pointer shadow-[0_0_15px_rgba(16,185,129,0.2)]">
                            <Download class="w-4 h-4" />
                            <span class="text-sm">Export .cybrid</span>
                        </a>
                    </div>
                </div>

                <div class="bg-surface-800 p-4 rounded-xl border border-surface-700 flex flex-col gap-3 mt-1">
                    <h3 class="text-surface-200 font-bold text-sm tracking-widest uppercase mb-1">Hub Preferences & Output</h3>
                    <div class="flex flex-col gap-1.5 mb-2">
                        <label for="default_route" class="text-[10px] font-bold uppercase tracking-widest text-surface-400">Startup Landing Page</label>
                        <select id="default_route" bind:value={aiSettings.default_route} class="w-full bg-surface-900 border border-surface-600 rounded-lg px-3 py-2 text-surface-200 text-sm outline-none focus:border-primary-500 transition-colors cursor-pointer">
                            <option value="/dashboard">Home (Dashboard)</option>
                            <option value="/chat">Chat Interface</option>
                            <option value="/vault">Vault Explorer</option>
                            <option value="/projects">Projects (Kanban)</option>
                        </select>
                        <p class="text-xs text-surface-500 mt-1">Sovereign Pair will boot directly to this page. Requires applying the 'Core Variables' physically at the bottom of the Sovereign Core card below to save into DB.</p>
                    </div>


                </div>
            </div>
            {/if}
        </section>

        <!-- CARD 2: Sovereign Mesh (Highlight as requested) -->
        <section class="bg-surface-800/80 backdrop-blur-md rounded-2xl border border-primary-500/30 overflow-hidden shadow-[0_0_20px_rgba(16,185,129,0.05)] transition-all duration-300 relative">
            <!-- Active Glow Indicator -->
            <div class="absolute top-0 right-0 w-32 h-32 bg-primary-500/10 blur-[50px] pointer-events-none"></div>

            <button class="w-full flex items-center justify-between p-5 text-left hover:bg-surface-700/30 cursor-pointer" onclick={() => toggleCard('mesh')}>
                <div class="flex items-center gap-4">
                    <div class="p-2 bg-primary-500/20 text-primary-400 rounded-lg">
                        <Server class="w-6 h-6" />
                    </div>
                    <div>
                        <h2 class="font-semibold text-primary-50 text-lg">Sovereign Mesh P2P</h2>
                        <p class="text-sm text-primary-400/80">Active Tunnels & Hardware Profiles</p>
                    </div>
                </div>
                <ChevronDown class="w-5 h-5 text-surface-500 transition-transform duration-300 transform {expandedCard === 'mesh' ? 'rotate-180' : ''}" />
            </button>
            {#if expandedCard === 'mesh'}
            <div class="p-5 border-t border-surface-700/50 bg-surface-900/30 flex flex-col gap-4">
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {#each activeNodes as node}
                    <div class="bg-surface-800 p-4 rounded-xl border border-surface-700 hover:border-surface-600 transition-colors">
                        <div class="flex items-start justify-between mb-3">
                            <span class="font-semibold text-surface-200">{node.hostname}</span>
                            <span class="text-[10px] uppercase font-bold tracking-wider px-2 py-1 rounded bg-surface-700 text-surface-300">{node.location}</span>
                        </div>
                        <div class="flex flex-col gap-2 text-sm text-surface-400">
                            <div class="flex items-center gap-2">
                                <Shield class="w-4 h-4 text-emerald-500" />
                                <span>{node.role}</span>
                            </div>
                            <div class="flex items-center gap-2">
                                <Cpu class="w-4 h-4 text-emerald-500" />
                                <span>{node.hardware}</span>
                            </div>
                        </div>
                    </div>
                    {/each}
                </div>

                <button class="mt-2 w-full py-3 rounded-xl border border-dashed border-surface-600 text-surface-300 flex items-center justify-center gap-2 hover:bg-surface-800 transition-colors cursor-pointer">
                    <GlobeLock class="w-4 h-4" />
                    <span>Establish New P2P Tunnel</span>
                </button>
            </div>
            {/if}
        </section>

        <!-- CARD 3: Fallback Cloud OCI -->
        <section class="bg-surface-800/80 backdrop-blur-md rounded-2xl border border-surface-700/50 overflow-hidden shadow-lg transition-all duration-300">
            <button class="w-full flex items-center justify-between p-5 text-left hover:bg-surface-700/30 cursor-pointer" onclick={() => toggleCard('cloud')}>
                <div class="flex items-center gap-4">
                    <div class="p-2 border border-surface-600/50 text-surface-400 rounded-lg">
                        <Cloud class="w-6 h-6" />
                    </div>
                    <div>
                        <h2 class="font-semibold text-surface-100 text-lg">Cloud Sandboxing (OCI)</h2>
                        <p class="text-sm text-surface-400">Oracle credentials & Default Execution Pipeline</p>
                    </div>
                </div>
                <ChevronDown class="w-5 h-5 text-surface-500 transition-transform duration-300 transform {expandedCard === 'cloud' ? 'rotate-180' : ''}" />
            </button>
            {#if expandedCard === 'cloud'}
            <div class="p-5 border-t border-surface-700/50 bg-surface-900/30">
                <p class="text-sm text-surface-400 mb-4">Fallback Execution node when Sovereign Mesh is unavailable.</p>
                <div class="flex flex-col gap-3">
                    <input type="text" placeholder="OCI Public IP" class="w-full bg-surface-800 border border-surface-600 rounded-lg px-4 py-2 text-surface-200 outline-none focus:border-primary-500 transition-colors">
                    <input type="password" placeholder="OCI Secret Key Path" class="w-full bg-surface-800 border border-surface-600 rounded-lg px-4 py-2 text-surface-200 outline-none focus:border-primary-500 transition-colors">
                </div>
            </div>
            {/if}
        </section>

        <!-- CARD 4: Sovereign Core (AI Engine) -->
        <section class="bg-surface-800/80 backdrop-blur-md rounded-2xl border border-surface-700/50 overflow-hidden shadow-lg transition-all duration-300">
            <button class="w-full flex items-center justify-between p-5 text-left hover:bg-surface-700/30 cursor-pointer" onclick={() => toggleCard('ai')}>
                <div class="flex items-center gap-4">
                    <div class="p-2 bg-emerald-500/20 text-emerald-400 rounded-lg">
                        <Brain class="w-6 h-6" />
                    </div>
                    <div>
                        <h2 class="font-semibold text-surface-100 text-lg">Sovereign Core (AI Engine)</h2>
                        <p class="text-sm text-surface-400">LLM Strategy, System Prompts, Inference Limits</p>
                    </div>
                </div>
                <ChevronDown class="w-5 h-5 text-surface-500 transition-transform duration-300 transform {expandedCard === 'ai' ? 'rotate-180' : ''}" />
            </button>
            {#if expandedCard === 'ai'}
            <div class="p-5 border-t border-surface-700/50 bg-surface-900/30 flex flex-col gap-5">
                
                <div class="bg-surface-800 p-4 rounded-xl border border-surface-700 flex flex-col gap-4">
                    <h3 class="text-surface-200 font-bold text-sm tracking-widest uppercase flex justify-between items-center">
                        Tri-Agent Hierarchy (Mesh Target)
                        {#if isLoadingModels}<Loader2 class="w-4 h-4 animate-spin text-primary-500"/>{/if}
                    </h3>

                    <div class="flex flex-col md:flex-row gap-4">
                        <div class="flex flex-col gap-1.5 flex-1">
                            <label for="nurse_model" class="text-xs font-semibold text-primary-400">The Nurse (Scraping/Triage)</label>
                            <select id="nurse_model" bind:value={aiSettings.nurse_model} class="w-full bg-surface-900 border border-surface-600 rounded-lg px-3 py-2 text-surface-200 text-sm outline-none focus:border-primary-500 transition-colors">
                                {#each availableModels as model}
                                    <option value={model.name}>{model.name} ({(model.size / 1024 / 1024 / 1024).toFixed(1)} GB)</option>
                                {:else}
                                    <option value={aiSettings.nurse_model}>{aiSettings.nurse_model}</option>
                                {/each}
                            </select>
                        </div>

                        <div class="flex flex-col gap-1.5 flex-1">
                            <label for="doctor_model" class="text-xs font-semibold text-sky-400">The Doctor (Planning/Chat)</label>
                            <select id="doctor_model" bind:value={aiSettings.doctor_model} class="w-full bg-surface-900 border border-surface-600 rounded-lg px-3 py-2 text-surface-200 text-sm outline-none focus:border-primary-500 transition-colors">
                                {#each availableModels as model}
                                    <option value={model.name}>{model.name} ({(model.size / 1024 / 1024 / 1024).toFixed(1)} GB)</option>
                                {:else}
                                    <option value={aiSettings.doctor_model}>{aiSettings.doctor_model}</option>
                                {/each}
                            </select>
                        </div>

                        <div class="flex flex-col gap-1.5 flex-1">
                            <label for="coder_model" class="text-xs font-semibold text-rose-400">The Coder (Execution/Scripting)</label>
                            <select id="coder_model" bind:value={aiSettings.coder_model} class="w-full bg-surface-900 border border-surface-600 rounded-lg px-3 py-2 text-surface-200 text-sm outline-none focus:border-primary-500 transition-colors">
                                {#each availableModels as model}
                                    <option value={model.name}>{model.name} ({(model.size / 1024 / 1024 / 1024).toFixed(1)} GB)</option>
                                {:else}
                                    <option value={aiSettings.coder_model}>{aiSettings.coder_model}</option>
                                {/each}
                            </select>
                        </div>
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div class="flex flex-col gap-2">
                        <label for="temperature" class="text-sm font-semibold text-surface-300 flex justify-between">
                            <span>Temperature</span>
                            <span class="text-primary-400">{aiSettings.temperature}</span>
                        </label>
                        <input id="temperature" type="range" min="0" max="1" step="0.1" bind:value={aiSettings.temperature} class="w-full accent-primary-500">
                    </div>
                    
                    <div class="flex flex-col gap-2">
                        <label for="top_k" class="text-sm font-semibold text-surface-300 flex justify-between">
                            <span>Top-K Sampling</span>
                            <span class="text-primary-400">{aiSettings.top_k}</span>
                        </label>
                        <input id="top_k" type="range" min="1" max="100" step="1" bind:value={aiSettings.top_k} class="w-full accent-primary-500">
                    </div>
                </div>

                <div class="flex flex-col gap-2 relative">
                    <label for="system_prompt" class="text-sm font-semibold text-surface-300 flex justify-between items-center">
                        Global System Prompt (Persona Override)
                        <select onchange={(e) => aiSettings.system_prompt = (e.target as HTMLSelectElement).value} class="bg-surface-800 border-none text-xs text-primary-400 focus:outline-none cursor-pointer p-1">
                            <option value="">Load Template...</option>
                            {#each PREDEFINED_PERSONAS as tpl}
                                <option value={tpl.prompt}>{tpl.label}</option>
                            {/each}
                        </select>
                    </label>
                    <textarea id="system_prompt" bind:value={aiSettings.system_prompt} placeholder="Leave empty for generic The Nurse system logic..." rows="3" class="w-full bg-surface-800 border border-surface-600 rounded-lg px-4 py-2 text-surface-200 outline-none focus:border-primary-500 transition-colors resize-none"></textarea>
                </div>

                <button onclick={saveAiSettings} class="mt-2 flex items-center justify-center gap-2 bg-primary-600 hover:bg-primary-500 text-white py-2 rounded-lg transition-colors shadow-lg shadow-primary-500/20 font-medium cursor-pointer">
                    <SlidersHorizontal class="w-4 h-4" />
                    <span>Apply Core Variables</span>
                </button>

            </div>
            {/if}
        </section>

        <!-- CARD 5: Sovereign Cold Storage (Offline Datasets) -->
        <section class="bg-surface-800/80 backdrop-blur-md rounded-2xl border border-teal-500/30 overflow-hidden shadow-[0_0_20px_rgba(20,184,166,0.05)] transition-all duration-300 relative mt-2">
            <!-- Active Glow Indicator -->
            <div class="absolute top-0 right-0 w-32 h-32 bg-teal-500/10 blur-[50px] pointer-events-none"></div>

            <button class="w-full flex items-center justify-between p-5 text-left hover:bg-surface-700/30 cursor-pointer" onclick={() => toggleCard('cold-storage')}>
                <div class="flex items-center gap-4">
                    <div class="p-2 bg-teal-500/20 text-teal-400 rounded-lg">
                        <Database class="w-6 h-6" />
                    </div>
                    <div>
                        <h2 class="font-semibold text-teal-50 text-lg">Sovereign Cold Storage</h2>
                        <p class="text-sm text-teal-400/80">Gestão de Corpora Massivos Offline (Plan B)</p>
                    </div>
                </div>
                <ChevronDown class="w-5 h-5 text-surface-500 transition-transform duration-300 transform {expandedCard === 'cold-storage' ? 'rotate-180' : ''}" />
            </button>
            {#if expandedCard === 'cold-storage'}
            <div class="p-5 border-t border-surface-700/50 bg-surface-900/30 flex flex-col gap-5">
                
                <p class="text-sm text-surface-400">O *Plano B Frio* do mecanismo Sovereign RAG. Defina a rota mestre onde residem dezenas de Terabytes de Dumps Estáticos (ZIM) e Datasets (Parquet/JSONL) para indexação vetorizada invisível e totalmente Air-Gapped.</p>
                
                <div class="flex flex-col gap-1.5">
                    <label for="corpora_vault_path" class="text-xs font-semibold text-teal-400 tracking-wider uppercase">Caminho Absoluto do Vault</label>
                    <input id="corpora_vault_path" type="text" bind:value={corporaVaultPath} class="w-full bg-surface-800 border border-surface-600 rounded-lg px-4 py-2.5 text-surface-200 outline-none focus:border-teal-500 transition-colors font-mono text-sm" placeholder="/home/user/Vault/Offline_Corpus">
                </div>

                <div class="bg-surface-800 p-4 rounded-xl border border-surface-700 flex flex-col gap-4">
                    <h3 class="text-surface-200 font-bold text-sm tracking-widest uppercase flex justify-between items-center">
                        Offline Corpora Mapeados
                    </h3>
                    
                    <div class="flex flex-col gap-3">
                        {#each offlineCorpora as corpus}
                            <div class="flex items-center justify-between p-3 rounded-lg border border-surface-700 bg-surface-900/50 hover:bg-surface-700 transition-colors">
                                <div class="flex items-center gap-4">
                                    <div class="w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs {corpus.active ? 'bg-teal-500/20 text-teal-400 border border-teal-500/50' : 'bg-surface-700 text-surface-500 border border-surface-600'}">
                                        #{corpus.priority}
                                    </div>
                                    <div class="flex flex-col">
                                        <span class="font-semibold text-sm text-surface-200">{corpus.name}</span>
                                        <span class="text-xs text-surface-400 flex items-center gap-2">
                                            {corpus.size}
                                            <span class="w-1 h-1 rounded-full bg-surface-600"></span>
                                            {corpus.type}
                                        </span>
                                    </div>
                                </div>
                                <div class="flex items-center gap-3">
                                    <span class="text-[10px] font-bold uppercase tracking-wider {corpus.active ? 'text-teal-400' : 'text-surface-500'}">
                                        {corpus.active ? 'Visível (Ativo)' : 'Oculto (Inativo)'}
                                    </span>
                                    <!-- Toggle Switch -->
                                    <button aria-label="Ligar/Desligar {corpus.name}" title="Alternar visibilidade do Corpus" class="w-12 h-6 rounded-full p-1 transition-colors {corpus.active ? 'bg-teal-500' : 'bg-surface-600'}" onclick={() => corpus.active = !corpus.active}>
                                        <div class="w-4 h-4 rounded-full bg-white shadow-sm transform transition-transform {corpus.active ? 'translate-x-6' : 'translate-x-0'}"></div>
                                    </button>
                                </div>
                            </div>
                        {/each}
                    </div>
                </div>

                <button onclick={saveColdStorage} class="mt-2 flex items-center justify-center gap-2 bg-teal-600 hover:bg-teal-500 text-white py-2.5 rounded-lg transition-colors shadow-lg shadow-teal-500/20 font-medium cursor-pointer">
                    <SlidersHorizontal class="w-4 h-4" />
                    <span>Sincronizar Índices Offline com o Vault</span>
                </button>

            </div>
            {/if}
        </section>

    </main>
</div>

