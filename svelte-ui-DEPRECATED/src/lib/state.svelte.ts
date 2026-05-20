import { API_BASE_URL } from '$lib/env_config';
/**
 * 🌐 **Global State | Svelte 5 Reactive Engine**
 * 
 * Gerencia o estado atômico de toda a aplicação usando as novas Runes do Svelte 5.
 * O uso de `$state` garante reatividade de alta performance sem a necessidade de stores legadas.
 */
export const globalState = $state({
    authPhase: 'loading',
    isSidebarOpen: true,
    sidebarWidth: 260,
    clusterState: {
        status: 'optimal',
        reason: '',
        active_agents: []
    },
    showRestrictedBanner: false,
    isManualOpen: false,

    // Global Workspaces
    activeWorkspaceId: 'mesh_roaming',
    activeWorkspaceName: 'Sovereign Mesh Roaming',
    workspaces: [] as any[],

    // Vault Teleport State
    vault: {
        activeDocumentId: '',
        activeDocumentContent: null as string | null,
        workspaceFiles: [] as any[]
    },
    
    // Chat History State (Global Execution Context)
    chat: {
        activeSessionId: null as number | null,
        activeSessionTitle: 'Nova Sessão',
        inputContext: '',
        messages: [] as any[],
        isTyping: false,
        isDeepResearchEnabled: false,
        isRewooEnabled: false,
        isCognitiveFirewallEnabled: true,
        isVisualArtistEnabled: false
    },

    // Notification Center
    notifications: [] as { id: number, title: string, text: string, time: string, read: boolean, link?: string }[],

    // Layout State
    layout: {
        isRightAuxPanelOpen: false
    }
});

export const toggleSidebar = () => {
    globalState.isSidebarOpen = !globalState.isSidebarOpen;
};

export const setSidebarWidth = (width: number) => {
    globalState.sidebarWidth = Math.max(200, Math.min(600, width));
};

// ==========================================
// NOTIFICATION SYSTEM ENGINE
// ==========================================
export const addNotification = (title: string, text: string, link?: string) => {
    globalState.notifications.unshift({
        id: Date.now(),
        title,
        text,
        time: new Date().toLocaleTimeString(),
        read: false,
        link
    });
};

export const markNotificationsRead = () => {
    globalState.notifications.forEach(n => n.read = true);
};


// ==========================================
// 🧠 **BACKGROUND CHAT PROCESSOR (Sensus SSE Engine)**
// ==========================================
/**
 * Orquestra a comunicação bidirecional via SSE (Server-Sent Events) com o backend Rust.
 * Implementa lógica de streaming, injeção de contexto dinâmico (Vault) e 
 * tratamento de erros resiliente para ambientes instáveis.
 */

let currentAbortController: AbortController | null = null;

export const stopGeneration = () => {
    if (currentAbortController) {
        currentAbortController.abort();
        currentAbortController = null;
    }
};
export const loadGlobalSession = async (id: number | null) => {
    if (!id) {
        globalState.chat.messages = [{ id: Date.now(), role: 'assistant', agent: 'Sovereign Coder', text: 'Sensus Synchronized. Ready for prompt ingestion.', time: new Date().toLocaleTimeString() }];
        return;
    }
    try {
        const token = localStorage.getItem('sovereign_token') || '';
        const res = await fetch(`${API_BASE_URL}/v1/sessions/${id}`, { headers: { 'Authorization': `Bearer ${token}` } });
        if (res.ok) {
            const data = await res.json();
            if (data.messages && data.messages.length > 0) {
                globalState.chat.messages = data.messages.map((m: any) => ({
                    id: m.id,
                    role: m.role,
                    agent: m.role === 'user' ? 'Commander' : 'Sovereign Evaluator',
                    text: m.content,
                    time: new Date(m.created_at).toLocaleTimeString()
                }));
            }
        }
    } catch(e) { console.error('Error loading session globally', e); }
};

export const sendGlobalChatMessage = async (userText: string) => {
    if (!userText.trim() || globalState.chat.isTyping) return;
    
    // 1. Injeta Pergunta na UI
    globalState.chat.messages = [
        ...globalState.chat.messages,
        { id: Date.now(), role: 'user', agent: 'Commander', text: userText, time: new Date().toLocaleTimeString() }
    ];
    globalState.chat.isTyping = true;
    
    const newMsgId = Date.now() + 1;
    globalState.chat.messages = [
        ...globalState.chat.messages,
        { id: newMsgId, role: 'assistant', agent: 'Sovereign Evaluator', text: '', time: new Date().toLocaleTimeString() }
    ];
    const assistantIdx = globalState.chat.messages.length - 1;

    try {
        let finalUserMsg = userText;
        const currentPath = window.location.pathname;


        // --- 🧬 Context Injection (Smart RAG) ---
        // Se o usuário estiver visualizando um documento no Vault, o frontend 
        // captura automaticamente os primeiros 1500 caracteres e os injeta como 
        // contexto privilegiado, permitindo perguntas sobre o arquivo aberto.
        if (globalState.chat.inputContext) {
            finalUserMsg = `[Contexto Destacado]: "${globalState.chat.inputContext}"\n\n[Pergunta]: ${userText}`;
            globalState.chat.inputContext = ''; // Limpa pra n explodir os próximos
        } else if (currentPath.includes('/vault') && globalState.vault.activeDocumentId && globalState.vault.activeDocumentContent) {
            // Context-Lock (Sub-Tenant Vault)
            finalUserMsg = `[Documento Atual: ${globalState.vault.activeDocumentId.split('/').pop()}]\n${globalState.vault.activeDocumentContent.substring(0, 1500)}\n\n[Instrução]: ${userText}`;
        }

        const historyPayload = globalState.chat.messages.slice(0, -2)
            .filter(m => m.text && !m.text.includes('Sensus Synchronized.'))
            .map(m => ({
                role: m.role,
                content: m.text
            }));

        const contextPayload = [...historyPayload, { role: 'user', content: finalUserMsg }];
        const ws_id = String(globalState.activeWorkspaceId || 'default');
        const token = localStorage.getItem('sovereign_token') || '';

        const payload = {
            model: 'gpt-4o', // O RAG Router ignora e avalia localmente
            messages: contextPayload,
            workspace_id: ws_id,
            session_id: globalState.chat.activeSessionId,
            stream: true,
            deep_research: globalState.chat.isDeepResearchEnabled,
            rewoo_enabled: globalState.chat.isRewooEnabled,
            firewall_enabled: globalState.chat.isCognitiveFirewallEnabled,
            visual_artist_mode: globalState.chat.isVisualArtistEnabled
        };

        currentAbortController = new AbortController();

        const response = await fetch(`${API_BASE_URL}/v1/chat/completions`, {
            method: 'POST',
            signal: currentAbortController.signal,
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        if (!response.body) throw new Error("No readable stream");

        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let buffer = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';

            for (const line of lines) {
                if (line.trim() === '') continue;
                if (line.includes('[DONE]')) break;
                
                if (line.startsWith('data: ')) {
                    try {
                        const data = JSON.parse(line.substring(6));
                        
                        if (data.id && data.id.startsWith('session_')) {
                            const sid = parseInt(data.id.split('_')[1], 10);
                            if (!isNaN(sid) && sid > 0) globalState.chat.activeSessionId = sid;
                        }

                        if (data.choices && data.choices[0].delta && data.choices[0].delta.content) {
                            globalState.chat.messages[assistantIdx].text += data.choices[0].delta.content;
                            // Force proxy trigger violently
                            globalState.chat.messages[assistantIdx] = { ...globalState.chat.messages[assistantIdx] };
                        }
                    } catch(e) { }
                }
            }
        }
        
        // FIX-MacOS: Guard contra resposta invisível — se o stream acabou mas não produziu conteúdo,
        // o modelo provavelmente não foi encontrado (404) ou retornou erro silencioso.
        if (globalState.chat.messages[assistantIdx] && !globalState.chat.messages[assistantIdx].text.trim()) {
            globalState.chat.messages[assistantIdx].text = '⚠️ **Resposta Vazia do Motor Neural**\n\nO modelo configurado não retornou conteúdo. Verifique:\n1. Se o modelo está instalado no Ollama (`ollama list`)\n2. Se o nome nas **Configurações do Engine** corresponde exatamente ao nome do Ollama\n3. Se a **Model Capabilities Matrix** (System Settings → AI Models) tem o flag **CHAT** ativo para o seu modelo';
            globalState.chat.messages[assistantIdx] = { ...globalState.chat.messages[assistantIdx] };
        }

        // Dispara a Notificacão com Link Garantido caso o processamento finalize com sucesso
        addNotification("Análise Concluída", "Sovereign Evaluator encerrou o raciocínio estratégico.", "/chat");

    } catch (error: any) {
        if (error.name === 'AbortError') {
            if (globalState.chat.messages[assistantIdx]) {
                globalState.chat.messages[assistantIdx].text += `\n\n[INFERÊNCIA INTERROMPIDA PELO USUÁRIO]`;
            }
        } else {
            console.error("Global Inference Engine Error:", error);
            if (globalState.chat.messages[assistantIdx]) {
                globalState.chat.messages[assistantIdx].text += `\n\n[SYSTEM ERROR]\nDetalhes Técnicos: ${error?.message}\nFalha Sensus Node Loss.`;
            }
        }
    } finally {
        globalState.chat.isTyping = false;
        currentAbortController = null;
    }
};
