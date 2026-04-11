<script lang="ts">
import { API_BASE_URL } from '$lib/env_config';

    import { ChevronDown, Server, Cpu, Shield, User, GlobeLock, Cloud, Download, Upload, Brain, SlidersHorizontal, Loader2, BookOpen, Printer, X, Database } from 'lucide-svelte';
    import { onMount } from 'svelte';
    import { marked } from 'marked';

    let expandedCard = $state<string | null>('mesh');

    function toggleCard(cardId: string) {
        expandedCard = expandedCard === cardId ? null : cardId;
    }

    // Estado Dinâmico - Sem Hardcodes (Mocks) Iniciais
    let activeNodes = $state<{id: string, name?: string, url?: string, role?: string, hardware?: string, location?: string}[]>([]);

    interface ModelMatrixRow {
        model_name: string;
        parameter_size: number;
        supports_tools: boolean;
        is_reasoner: boolean;
        is_master: boolean;
        is_scribe: boolean;
        is_agent: boolean;
        is_coder: boolean;
        is_chat: boolean;
        is_project: boolean;
    }

    let modelMatrix = $state<ModelMatrixRow[]>([]);
    let isSavingMatrix = $state(false);

    let aiSettings = $state({
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
            const res = await fetch(`${API_BASE_URL}/v1/settings`);
            if (res.ok) {
                const data = await res.json();
                if (data.temperature !== undefined) aiSettings.temperature = data.temperature;
                if (data.top_k !== undefined) aiSettings.top_k = data.top_k;
                if (data.system_prompt) aiSettings.system_prompt = data.system_prompt;
                if (data.default_route) aiSettings.default_route = data.default_route;
            }
        } catch(e) { console.error("Agent offline:", e); }

        // Fetch Dynamic Models from Mesh Target
        try {
            const mRes = await fetch(`${API_BASE_URL}/v1/system/available_models`);
            if (mRes.ok) {
                const data = await mRes.json();
                if (data.models) {
                    availableModels = data.models.map((m: any) => ({ name: m.name, size: m.size }));
                }
            }
        } catch(e) { console.error("Ollama Daemon unreachable:", e); } finally {
            isLoadingModels = false;
        }

        // Fetch Model Capabilities Matrix
        try {
            const matrixRes = await fetch(`${API_BASE_URL}/v1/settings/model_capabilities`);
            if (matrixRes.ok) {
                modelMatrix = await matrixRes.json();
            }
        } catch(e) { console.error("Failed to load Model Matrix:", e); }

        // Fetch Mesh Nodes (Ollama Clusters Real Data)
        try {
            const meshRes = await fetch(`${API_BASE_URL}/v1/settings/ollama_clusters`);
            if (meshRes.ok) {
                const data = await meshRes.json();
                if (data.clusters && data.clusters.length > 0) {
                    activeNodes = data.clusters.map((c: any) => ({
                        id: c.id,
                        name: c.name || c.url,
                        url: c.url,
                        role: 'Cognitive Node',
                        hardware: 'Mesh Linked',
                        location: c.url?.includes('localhost') || c.url?.includes('127.0.0.1') ? 'Local Network' : 'Cloud Node'
                    }));
                }
            }
        } catch(e) { console.error("Failed to load Mesh Nodes:", e); }

        // Fetch Cold Storage Database
        try {
            const csRes = await fetch(`${API_BASE_URL}/v1/settings/cold_storage`);
            if (csRes.ok) {
                const data = await csRes.json();
                if (data.corporaVaultPath) corporaVaultPath = data.corporaVaultPath;
                if (data.offlineCorpora && data.offlineCorpora.length > 0) offlineCorpora = data.offlineCorpora;
            }
        } catch(e) { console.error("Cold Storage DB unreachable:", e); }

        await loadTenantKeys();

    });

    async function saveAiSettings() {
        try {
            const res = await fetch(`${API_BASE_URL}/v1/settings`);
            let data = res.ok ? await res.json() : {};
            
            data.temperature = Number(aiSettings.temperature);
            data.top_k = Number(aiSettings.top_k);
            data.system_prompt = aiSettings.system_prompt;
            data.default_route = aiSettings.default_route;
            
            const postRes = await fetch(`${API_BASE_URL}/v1/settings`, {
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

    async function toggleMatrixCapability(modelName: string, fieldName: keyof ModelMatrixRow, value: boolean) {
        if (isSavingMatrix) return;
        isSavingMatrix = true;
        try {
            const model = modelMatrix.find(m => m.model_name === modelName);
            if (!model) return;
            
            const payload = {
                model_name: model.model_name,
                is_master: fieldName === 'is_master' ? value : model.is_master,
                is_scribe: fieldName === 'is_scribe' ? value : model.is_scribe,
                is_agent: fieldName === 'is_agent' ? value : model.is_agent,
                is_coder: fieldName === 'is_coder' ? value : model.is_coder,
                is_chat: fieldName === 'is_chat' ? value : model.is_chat,
                is_project: fieldName === 'is_project' ? value : model.is_project
            };

            const res = await fetch(`${API_BASE_URL}/v1/settings/model_capabilities/toggles`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                (model as any)[fieldName] = value;
            }
        } catch(e) {
            console.error("Failed to update matrix toggle:", e);
        } finally {
            isSavingMatrix = false;
        }
    }

    async function saveColdStorage() {
        try {
            const res = await fetch(`${API_BASE_URL}/v1/settings/cold_storage`, {
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

    let tenantApiKeys = $state<{id: string, provider_name: string, created_at: string}[]>([]);
    let newProviderName = $state('');
    let newApiKeyValue = $state('');
    let isLoadingKeys = $state(false);

    async function loadTenantKeys() {
        isLoadingKeys = true;
        try {
            const res = await fetch(`${API_BASE_URL}/v1/settings/tenant_keys`);
            if (res.ok) tenantApiKeys = await res.json();
        } catch(e) { console.error("Failed to load SecOps Vault", e); }
        finally { isLoadingKeys = false; }
    }

    async function addTenantKey() {
        if (!newProviderName || !newApiKeyValue) { alert("Providers e Chaves não podem estar vazios"); return; }
        try {
            const res = await fetch(`${API_BASE_URL}/v1/settings/tenant_keys`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ provider_name: newProviderName, api_key_value: newApiKeyValue })
            });
            if (res.ok) {
                newProviderName = '';
                newApiKeyValue = '';
                alert("API Key selada com Criptografia Simétrica no SecOps Vault.");
                loadTenantKeys();
            } else {
                alert("Erro ao salvar Key.");
            }
        } catch(e) { console.error("Failed to save Key", e); }
    }

    async function deleteTenantKey(id: string) {
        if(!confirm("Obliteração Irreversível. Destruir API Key permanentemente?")) return;
        try {
            const res = await fetch(`${API_BASE_URL}/v1/settings/tenant_keys/${id}`, { method: 'DELETE' });
            if (res.ok) loadTenantKeys();
        } catch(e) {}
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
                const res = await fetch(`${API_BASE_URL}/v1/system/import_config`, {
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
                        <a href="{API_BASE_URL}/v1/system/export_config" target="_blank" class="flex-1 py-2 rounded-lg bg-primary-600 text-white hover:bg-primary-500 transition-colors flex items-center justify-center gap-2 cursor-pointer shadow-[0_0_15px_rgba(16,185,129,0.2)]">
                            <Download class="w-4 h-4" />
                            <span class="text-sm">Export .cybrid</span>
                        </a>
                    </div>
                </div>

                <div class="bg-surface-800 p-4 rounded-xl border border-surface-700 flex flex-col gap-3 mt-1">
                    <h3 class="text-surface-200 font-bold text-sm tracking-widest uppercase mb-1">Hub Preferences & Output</h3>
                    <div class="flex flex-col gap-1.5 mb-2">
                        <label for="default_route" class="text-[10px] font-bold uppercase tracking-widest text-surface-400">Startup Landing Page</label>
                        <select id="default_route" bind:value={aiSettings.default_route} class="w-full bg-slate-50 dark:bg-[#080e1d] border border-slate-300 dark:border-slate-700 rounded-lg px-3 py-2 text-slate-800 dark:text-slate-200 text-sm outline-none focus:border-primary-500 transition-colors cursor-pointer">
                            <option value="/dashboard" class="bg-white dark:bg-[#12192b] text-slate-800 dark:text-slate-200">Home (Dashboard)</option>
                            <option value="/chat" class="bg-white dark:bg-[#12192b] text-slate-800 dark:text-slate-200">Chat Interface</option>
                            <option value="/vault" class="bg-white dark:bg-[#12192b] text-slate-800 dark:text-slate-200">Vault Explorer</option>
                            <option value="/projects" class="bg-white dark:bg-[#12192b] text-slate-800 dark:text-slate-200">Projects (Kanban)</option>
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
                            <span class="font-semibold text-surface-200">{node.name}</span>
                            <span class="text-[10px] uppercase font-bold tracking-wider px-2 py-1 rounded bg-surface-700 text-surface-300">{node.location}</span>
                        </div>
                        <div class="flex flex-col gap-2 text-sm text-surface-400">
                            <div class="flex items-center gap-2">
                                <GlobeLock class="w-4 h-4 text-emerald-500" />
                                <span class="font-mono text-xs">{node.url}</span>
                            </div>
                            <div class="flex items-center gap-2">
                                <Server class="w-4 h-4 text-emerald-500" />
                                <span>{node.role}</span>
                            </div>
                        </div>
                    </div>
                    {:else}
                    <div class="col-span-1 md:col-span-2 text-center text-surface-400 text-sm py-4 border border-dashed border-surface-700 rounded-xl">
                        Nenhum nó de malha P2P conectado no momento. O backend operará utilizando Localhost:11434 como fallback.
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
                
                <div class="bg-surface-800 p-4 rounded-xl border border-surface-700 flex flex-col gap-4 overflow-hidden">
                    <h3 class="text-surface-200 font-bold text-sm tracking-widest uppercase flex justify-between items-center">
                        Model Operations Matrix
                        {#if modelMatrix.length === 0}<Loader2 class="w-4 h-4 animate-spin text-primary-500"/>{/if}
                    </h3>
                    
                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-sm text-surface-300">
                            <thead class="text-xs uppercase bg-surface-900/50 text-surface-400">
                                <tr>
                                    <th class="px-4 py-3 font-semibold rounded-tl-lg">Model</th>
                                    <th class="px-4 py-3 font-semibold text-center">Master</th>
                                    <th class="px-4 py-3 font-semibold text-center">Scribe</th>
                                    <th class="px-4 py-3 font-semibold text-center">Agent</th>
                                    <th class="px-4 py-3 font-semibold text-center">Coder</th>
                                    <th class="px-4 py-3 font-semibold text-center">Chat</th>
                                    <th class="px-4 py-3 font-semibold text-center rounded-tr-lg">Project</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-surface-700/50">
                                {#each modelMatrix as row}
                                    <tr class="hover:bg-surface-700/20 transition-colors">
                                        <td class="px-4 py-3">
                                        <td class="px-4 py-3">
                                            <div class="font-medium {row.is_installed ? 'text-surface-100' : 'text-surface-500 line-through decoration-surface-500/50'}">{row.model_name}</div>
                                            <div class="text-xs text-surface-500 flex flex-wrap gap-2 mt-1 items-center">
                                                <span>{(row.parameter_size).toFixed(1)}B</span>
                                                {#if row.supports_tools}<span class="text-emerald-500 text-[10px] uppercase border border-emerald-500/30 px-1 rounded">Tools</span>{/if}
                                                {#if row.is_reasoner}<span class="text-fuchsia-500 text-[10px] uppercase border border-fuchsia-500/30 px-1 rounded">Reasoner</span>{/if}
                                                {#if !row.is_installed}
                                                    <span class="text-error-400 text-[10px] uppercase border border-error-500/30 px-1 rounded flex items-center gap-1 font-bold ring-1 ring-error-500/50 bg-error-500/10" title="Modelo offline ou excluído do nó. Sua configuração Cíbrida foi preservada.">
                                                        OFFLINE
                                                    </span>
                                                {/if}
                                            </div>
                                        </td>
                                        
                                        <!-- Master: Requer Tools. Se não tiver, desabilite visualmente e trave o checkbox -->
                                        <td class="px-4 py-3 text-center">
                                            <input type="checkbox" 
                                                class="w-4 h-4 rounded border-surface-600 bg-surface-800 text-primary-500 focus:ring-primary-500 focus:ring-offset-surface-900 cursor-pointer disabled:opacity-30 disabled:cursor-not-allowed"
                                                checked={row.is_master}
                                                disabled={!row.supports_tools || isSavingMatrix || !row.is_installed}
                                                onchange={(e) => toggleMatrixCapability(row.model_name, 'is_master', (e.target as HTMLInputElement).checked)}
                                            />
                                        </td>
                                        
                                        <!-- Scribe -->
                                        <td class="px-4 py-3 text-center">
                                            <input type="checkbox" 
                                                class="w-4 h-4 rounded border-surface-600 bg-surface-800 text-primary-500 focus:ring-primary-500 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                                                checked={row.is_scribe}
                                                disabled={isSavingMatrix || !row.is_installed}
                                                onchange={(e) => toggleMatrixCapability(row.model_name, 'is_scribe', (e.target as HTMLInputElement).checked)}
                                            />
                                        </td>

                                        <!-- Agent: Requer Tools -->
                                        <td class="px-4 py-3 text-center">
                                            <input type="checkbox" 
                                                class="w-4 h-4 rounded border-surface-600 bg-surface-800 text-primary-500 focus:ring-primary-500 cursor-pointer disabled:opacity-30 disabled:cursor-not-allowed"
                                                checked={row.is_agent}
                                                disabled={!row.supports_tools || isSavingMatrix || !row.is_installed}
                                                onchange={(e) => toggleMatrixCapability(row.model_name, 'is_agent', (e.target as HTMLInputElement).checked)}
                                            />
                                        </td>

                                        <!-- Coder -->
                                        <td class="px-4 py-3 text-center">
                                            <input type="checkbox" 
                                                class="w-4 h-4 rounded border-surface-600 bg-surface-800 text-primary-500 focus:ring-primary-500 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                                                checked={row.is_coder}
                                                disabled={isSavingMatrix || !row.is_installed}
                                                onchange={(e) => toggleMatrixCapability(row.model_name, 'is_coder', (e.target as HTMLInputElement).checked)}
                                            />
                                        </td>

                                        <!-- Chat -->
                                        <td class="px-4 py-3 text-center">
                                            <input type="checkbox" 
                                                class="w-4 h-4 rounded border-surface-600 bg-surface-800 text-primary-500 focus:ring-primary-500 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                                                checked={row.is_chat}
                                                disabled={isSavingMatrix || !row.is_installed}
                                                onchange={(e) => toggleMatrixCapability(row.model_name, 'is_chat', (e.target as HTMLInputElement).checked)}
                                            />
                                        </td>

                                        <!-- Project / Kanban -->
                                        <td class="px-4 py-3 text-center">
                                            <input type="checkbox" 
                                                class="w-4 h-4 rounded border-surface-600 bg-surface-800 text-primary-500 focus:ring-primary-500 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                                                checked={row.is_project}
                                                disabled={isSavingMatrix || !row.is_installed}
                                                onchange={(e) => toggleMatrixCapability(row.model_name, 'is_project', (e.target as HTMLInputElement).checked)}
                                            />
                                        </td>
                                    </tr>
                                {:else}
                                    <tr>
                                        <td colspan="7" class="px-4 py-8 text-center text-surface-500 italic">No models registered in the Matrix yet. They auto-register when the system starts.</td>
                                    </tr>
                                {/each}
                            </tbody>
                        </table>
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
                            <option value="" class="bg-surface-800 text-surface-200">Load Template...</option>
                            {#each PREDEFINED_PERSONAS as tpl}
                                <option value={tpl.prompt} class="bg-surface-800 text-surface-200">{tpl.label}</option>
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

        <!-- CARD 6: SecOps API Vault -->
        <section class="bg-surface-800/80 backdrop-blur-md rounded-2xl border border-rose-500/30 overflow-hidden shadow-[0_0_20px_rgba(244,63,94,0.05)] transition-all duration-300 relative mt-2">
            <!-- Active Glow Indicator -->
            <div class="absolute top-0 right-0 w-32 h-32 bg-rose-500/10 blur-[50px] pointer-events-none"></div>

            <button class="w-full flex items-center justify-between p-5 text-left hover:bg-surface-700/30 cursor-pointer" onclick={() => toggleCard('secops-vault')}>
                <div class="flex items-center gap-4">
                    <div class="p-2 bg-rose-500/20 text-rose-400 rounded-lg">
                        <Shield class="w-6 h-6" />
                    </div>
                    <div>
                        <h2 class="font-semibold text-rose-50 text-lg">Sovereign SecOps API Vault</h2>
                        <p class="text-sm text-rose-400/80">Injeção Nativa de API Keys e Chaves Cypherpunk</p>
                    </div>
                </div>
                <ChevronDown class="w-5 h-5 text-surface-500 transition-transform duration-300 transform {expandedCard === 'secops-vault' ? 'rotate-180' : ''}" />
            </button>
            {#if expandedCard === 'secops-vault'}
            <div class="p-5 border-t border-surface-700/50 bg-surface-900/30 flex flex-col gap-5">
                
                <p class="text-sm text-surface-400">Gerencie chaves secretas (como <strong>TMDB, OpenAI, Anthropic, IGDB</strong>). Nenhuma chave injetada aqui transita em texto plano. Elas são criptografadas (AES-GCM at-rest) nativamente pelo KMS em Rust para o banco SQLite local.</p>
                
                <!-- Injection Form -->
                <div class="flex gap-2 items-end bg-surface-800 p-4 rounded-xl border border-surface-700">
                    <div class="flex flex-col gap-1 w-1/3">
                        <label for="provider_name" class="text-[10px] font-bold uppercase tracking-wider text-surface-400">Provedor</label>
                        <input id="provider_name" bind:value={newProviderName} placeholder="Ex: TMDB_API_KEY" class="bg-surface-700 border border-surface-600 rounded px-3 py-2 text-surface-200 text-sm outline-none focus:border-rose-500">
                    </div>
                    <div class="flex flex-col gap-1 flex-1">
                        <label for="api_key_value" class="text-[10px] font-bold uppercase tracking-wider text-surface-400">Payload Secreto (Key)</label>
                        <input id="api_key_value" type="password" bind:value={newApiKeyValue} placeholder="sk-..." class="bg-surface-700 border border-surface-600 rounded px-3 py-2 text-surface-200 text-sm outline-none focus:border-rose-500">
                    </div>
                    <button onclick={addTenantKey} class="px-5 py-2 h-[38px] bg-rose-600 hover:bg-rose-500 text-white font-medium rounded-md text-sm transition-colors uppercase tracking-wider shadow-[0_0_15px_rgba(225,29,72,0.3)] cursor-pointer">Injetar</button>
                </div>

                <!-- Vault Table -->
                <div class="rounded-xl border border-surface-700 overflow-hidden mt-2">
                    <table class="w-full text-left text-sm text-surface-300">
                        <thead class="bg-surface-800/80 text-[10px] uppercase tracking-widest text-surface-400 border-b border-surface-700">
                            <tr>
                                <th class="px-4 py-3 font-semibold">Provedor Registrado</th>
                                <th class="px-4 py-3 font-semibold">Cifra Oculta</th>
                                <th class="px-4 py-3 font-semibold">Acolhimento</th>
                                <th class="px-4 py-3 font-semibold w-24 text-center">Ações</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-surface-700/50">
                            {#if isLoadingKeys}
                            <tr><td colspan="4" class="p-4 text-center text-surface-500 text-xs"><Loader2 class="w-4 h-4 animate-spin mx-auto"/></td></tr>
                            {:else if tenantApiKeys.length === 0}
                            <tr>
                                <td colspan="4" class="p-6 text-center text-surface-500 text-xs italic">
                                    O cofre está vazio. Nenhuma chave encontrada no SQLite local.
                                </td>
                            </tr>
                            {:else}
                                {#each tenantApiKeys as key (key.id)}
                                <tr class="hover:bg-surface-800/50 transition-colors">
                                    <td class="px-4 py-3 font-mono font-medium text-rose-400">{key.provider_name}</td>
                                    <td class="px-4 py-3 font-mono text-surface-500">******************************</td>
                                    <td class="px-4 py-3 text-surface-500 text-xs">{new Date(key.created_at).toLocaleString()}</td>
                                    <td class="px-4 py-3 text-center">
                                        <button onclick={() => deleteTenantKey(key.id)} class="text-surface-500 hover:text-rose-400 transition-colors cursor-pointer" title="Obliteração de Chave">
                                            <X class="w-4 h-4 mx-auto" />
                                        </button>
                                    </td>
                                </tr>
                                {/each}
                            {/if}
                        </tbody>
                    </table>
                </div>

            </div>
            {/if}
        </section>

    </main>
</div>
