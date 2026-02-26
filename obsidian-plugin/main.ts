import { App, Plugin, PluginSettingTab, Setting, ItemView, WorkspaceLeaf, MarkdownView, Notice, Editor, MarkdownFileInfo, Modal } from 'obsidian';

export const VIEW_TYPE_CHAT = "sovereign-pair-chat-view";

interface SovereignPairSettings {
    authToken: string;
}

const DEFAULT_SETTINGS: SovereignPairSettings = {
    authToken: ''
}

export class SovereignPairView extends ItemView {
    messageContainer: HTMLElement;
    inputField: HTMLTextAreaElement;
    submitButton: HTMLButtonElement;
    sessionSelect: HTMLSelectElement;

    currentSessionId: number | null = null;
    sessionsList: any[] = [];
    plugin: SovereignPairPlugin;

    constructor(leaf: WorkspaceLeaf, plugin: SovereignPairPlugin) {
        super(leaf);
        this.plugin = plugin;
    }

    getViewType() {
        return VIEW_TYPE_CHAT;
    }

    getDisplayText() {
        return "Sovereign Pair";
    }

    getIcon() {
        return "bot";
    }

    getAuthHeaders(): Record<string, string> {
        const token = this.plugin.settings.authToken;
        return token ? { 'Authorization': `Bearer ${token}` } : {};
    }

    async onOpen() {
        const container = this.containerEl.children[1];
        container.empty();
        container.addClass('sovereign-pair-container');

        // Habilitar seleção de texto e cópia
        const containerEl = container as HTMLElement;
        containerEl.style.userSelect = "text";
        containerEl.style.webkitUserSelect = "text";

        const header = container.createEl("h2", { text: "Sovereign Pair" });
        header.style.textAlign = "center";
        header.style.marginBottom = "15px";

        // Mover o Header e History area para cima da lista de mensagens
        const historyArea = container.createDiv({ cls: 'sp-history-area' });
        historyArea.style.padding = "5px 10px 10px";
        historyArea.style.display = "flex";
        historyArea.style.alignItems = "center";
        historyArea.style.justifyContent = "space-between";
        historyArea.style.gap = "8px";

        this.sessionSelect = historyArea.createEl('select', { cls: 'sp-session-select' });
        this.sessionSelect.style.flex = "1";
        this.sessionSelect.style.padding = "4px";
        this.sessionSelect.style.borderRadius = "4px";
        this.sessionSelect.style.backgroundColor = "var(--background-modifier-form-field)";
        this.sessionSelect.style.color = "var(--text-normal)";
        this.sessionSelect.style.border = "1px solid var(--background-modifier-border)";

        this.sessionSelect.createEl('option', { value: '', text: '--- Nova Conversa ---' });

        this.sessionSelect.addEventListener('change', async (e) => {
            const target = e.target as HTMLSelectElement;
            const selectedId = target.value;
            if (selectedId) {
                await this.loadSession(parseInt(selectedId));
            } else {
                this.currentSessionId = null;
                this.messageContainer.empty();
                this.addMessage("Nova conversa iniciada. Como posso ajudar?", "ai");
            }
        });

        const refreshBtn = historyArea.createEl('button', { text: '🔄', title: 'Recarregar Sessões' });
        refreshBtn.style.cursor = "pointer";
        refreshBtn.style.padding = "4px 8px";
        refreshBtn.style.background = "transparent";
        refreshBtn.style.border = "1px solid var(--background-modifier-border)";
        refreshBtn.style.borderRadius = "4px";
        refreshBtn.onclick = () => this.refreshSessionsList();

        const configBtn = historyArea.createEl('button', { text: '⚙️', title: 'Configurações LLM' });
        configBtn.style.cursor = "pointer";
        configBtn.style.padding = "4px 8px";
        configBtn.style.background = "transparent";
        configBtn.style.border = "1px solid var(--background-modifier-border)";
        configBtn.style.borderRadius = "4px";
        configBtn.onclick = () => {
            new SovereignPairConfigModal(this.app, this.plugin).open();
        };

        // Messages Container
        this.messageContainer = container.createDiv({ cls: 'sp-messages-container' });
        this.messageContainer.style.flex = "1";
        this.messageContainer.style.overflowY = "auto";
        this.messageContainer.style.padding = "10px";
        this.messageContainer.style.display = "flex";
        this.messageContainer.style.flexDirection = "column";
        this.messageContainer.style.gap = "10px";

        this.addMessage("Olá! Sou a Sovereign Pair. Pergunte-me qualquer coisa sobre o seu Vault, ou sobre a anotação que você está lendo agora!", "ai");

        // Input Area at the bottom
        const inputArea = container.createDiv({ cls: 'sp-input-area' });
        inputArea.style.display = "flex";
        inputArea.style.gap = "8px";
        inputArea.style.marginTop = "10px";
        inputArea.style.padding = "10px";
        inputArea.style.borderTop = "1px solid var(--background-modifier-border)";
        // FIX: Evita que os botões do rodapé fiquem escondidos na interface do Obsidian
        inputArea.style.paddingBottom = "30px";

        this.inputField = inputArea.createEl('textarea', {
            cls: 'sp-chat-input',
            attr: { placeholder: 'Sovereign Pair vai analisar sua nota ativa...' }
        });
        this.inputField.style.flex = "1";
        this.inputField.style.resize = "none";
        this.inputField.style.height = "50px";
        this.inputField.style.borderRadius = "5px";

        this.inputField.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleSubmit();
            }
        });

        // Habilitar paste no input field explicitly if needed, but obsidian forms usually handle it.
        // The container.style.userSelect = "text"; above usually handles copy inside the view.

        this.submitButton = inputArea.createEl('button', { text: 'Envia' });
        this.submitButton.style.cursor = "pointer";
        this.submitButton.onclick = () => this.handleSubmit();

        // Load sessions initially
        this.refreshSessionsList();
    }

    addMessage(content: string, sender: 'user' | 'ai'): HTMLElement {
        const bubbleWrap = this.messageContainer.createDiv({ cls: `sp-message-wrapper sp-wrapper-${sender}` });
        bubbleWrap.style.display = "flex";
        bubbleWrap.style.flexDirection = "column";
        if (sender === 'user') bubbleWrap.style.alignItems = "flex-end";
        else bubbleWrap.style.alignItems = "flex-start";

        const bubble = bubbleWrap.createDiv({ cls: `sp-message sp-message-${sender}` });

        bubble.style.padding = "10px 14px";
        bubble.style.borderRadius = "8px";
        bubble.style.maxWidth = "90%";
        bubble.style.lineHeight = "1.5";

        if (sender === 'user') {
            bubble.style.backgroundColor = "var(--interactive-accent)";
            bubble.style.color = "var(--text-on-accent)";
        } else {
            bubble.style.backgroundColor = "var(--background-secondary-alt)";
            bubble.style.border = "1px solid var(--background-modifier-border)";
        }

        bubble.innerHTML = content; // Mudar para um renderizador markdown futuramente
        this.messageContainer.scrollTo({ top: this.messageContainer.scrollHeight, behavior: 'smooth' });

        // Return wrapper for AI so we can append action bars
        return sender === 'ai' ? bubbleWrap : bubbleWrap;
    }

    addFeedbackBar(wrapper: HTMLElement, messageId: number) {
        const actionBar = wrapper.createDiv();
        actionBar.style.display = "flex";
        actionBar.style.gap = "8px";
        actionBar.style.marginTop = "4px";
        actionBar.style.paddingLeft = "4px";

        const btnUp = actionBar.createEl("button");
        btnUp.innerHTML = "👍";
        btnUp.style.background = "transparent";
        btnUp.style.border = "none";
        btnUp.style.cursor = "pointer";
        btnUp.style.fontSize = "12px";
        btnUp.style.opacity = "0.6";

        const btnDown = actionBar.createEl("button");
        btnDown.innerHTML = "👎";
        btnDown.style.background = "transparent";
        btnDown.style.border = "none";
        btnDown.style.cursor = "pointer";
        btnDown.style.fontSize = "12px";
        btnDown.style.opacity = "0.6";

        const sendFeedback = async (up: boolean, down: boolean) => {
            btnUp.style.opacity = up ? "1" : "0.3";
            btnDown.style.opacity = down ? "1" : "0.3";
            try {
                await fetch('http://127.0.0.1:8000/v1/feedback', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        ...this.getAuthHeaders()
                    },
                    body: JSON.stringify({ message_id: messageId, thumbs_up: up, thumbs_down: down })
                });
            } catch (e) {
                console.error("Feedback error", e);
            }
        };

        btnUp.onclick = () => sendFeedback(true, false);
        btnDown.onclick = () => sendFeedback(false, true);
    }

    async refreshSessionsList() {
        try {
            const res = await fetch('http://127.0.0.1:8000/v1/sessions', {
                headers: this.getAuthHeaders()
            });
            if (res.ok) {
                this.sessionsList = await res.json();
                this.sessionSelect.empty();
                this.sessionSelect.createEl('option', { value: '', text: '--- Nova Conversa ---' });
                for (const sess of this.sessionsList) {
                    const opt = this.sessionSelect.createEl('option', { value: sess.id.toString(), text: sess.title });
                    if (this.currentSessionId === sess.id) opt.selected = true;
                }
            }
        } catch (e) {
            console.error("Falha ao recuperar histórico", e);
        }
    }

    async loadSession(id: number) {
        try {
            const res = await fetch(`http://127.0.0.1:8000/v1/sessions/${id}`, {
                headers: this.getAuthHeaders()
            });
            if (res.ok) {
                const data = await res.json();
                this.currentSessionId = data.id;
                this.messageContainer.empty();

                for (const msg of data.messages) {
                    const wrap = this.addMessage(msg.content, msg.role as 'user' | 'ai');
                    if (msg.role === 'assistant') {
                        // Converter Markdown DB estático para algo visivel
                        const inner = wrap.querySelector('.sp-message-ai') as HTMLElement;
                        if (inner) inner.innerHTML = msg.content.replace(/\n/g, '<br>');
                        this.addFeedbackBar(wrap, msg.id);
                    }
                }
                setTimeout(() => {
                    this.messageContainer.scrollTo({ top: this.messageContainer.scrollHeight, behavior: 'smooth' });
                }, 50);
            }
        } catch (e) {
            console.error("Erro recarregando historico via Session ID", e);
        }
    }

    async getActiveNoteContext(): Promise<string> {
        const activeFile = this.app.workspace.getActiveFile();
        if (activeFile && activeFile.extension === 'md') {
            const content = await this.app.vault.read(activeFile);
            return `[DOCUMENTO ATUALMENTE ABERTO E FOCADO NO EDITOR DO USUÁRIO:\nTítulo: ${activeFile.basename}\nCaminho: ${activeFile.path}\nConteúdo Histórico:\n${content}\n--- FIM DO DOCUMENTO ATUAL ---]\n\n`;
        }
        return "";
    }

    // Gerador de ID local fake pro DOM (quando o Backend não retornou ainda o message_id real na UI Vanilla)
    private _fallbackIdCounter = 999000;

    async handleSubmit() {
        const text = this.inputField.value.trim();
        if (!text) return;

        this.inputField.value = "";
        this.addMessage(text, 'user');

        const wrapperNode = this.addMessage("...", 'ai');
        const aiBubble = wrapperNode.querySelector('.sp-message-ai') as HTMLElement;
        aiBubble.style.opacity = "0.7";

        try {
            // Capturar documento atual silenciosamente
            const activeContext = await this.getActiveNoteContext();

            const response = await fetch('http://127.0.0.1:8000/v1/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...this.getAuthHeaders()
                },
                body: JSON.stringify({
                    message: text,
                    active_document: activeContext ? activeContext : null,
                    stream: true,
                    session_id: this.currentSessionId
                })
            });

            if (!response.ok) throw new Error("API Indisponível (FastAPI)");

            const reader = response.body?.getReader();
            const decoder = new TextDecoder();

            if (reader) {
                aiBubble.innerHTML = "";
                aiBubble.style.opacity = "1";
                let fullResponse = "";

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;

                    const chunk = decoder.decode(value, { stream: true });
                    const lines = chunk.split('\n');

                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            const dataStr = line.replace('data: ', '').trim();
                            if (dataStr === '[DONE]') continue;
                            if (dataStr) {
                                try {
                                    const data = JSON.parse(dataStr);
                                    if (data.session_id_established) {
                                        this.currentSessionId = data.session_id_established;
                                    }
                                    if (data.message_id) {
                                        // Hidrata o ID real da mensagem no banco local FastAPI para feedback
                                        this.addFeedbackBar(wrapperNode, data.message_id);
                                    }
                                    if (data.content) {
                                        fullResponse += data.content;
                                        // Renderizando quebras de linha básicas no DOM
                                        aiBubble.innerHTML = fullResponse.replace(/\n/g, '<br>');
                                        this.messageContainer.scrollTo({ top: this.messageContainer.scrollHeight });
                                    }
                                } catch (e) { console.error("Parse erro", e, dataStr); }
                            }
                        }
                    }
                }
            }

        } catch (e) {
            aiBubble.innerHTML = "⚠️ _Erro de conexão com o Motor FastAPI._";
            console.error("SSE Error:", e);
        }
    }

    async onClose() { }
}

export default class SovereignPairPlugin extends Plugin {
    lastSyncTime: number = Date.now();
    settings: SovereignPairSettings;

    async onload() {
        console.log('Carregando Sovereign Pair RAG Plugin...');

        await this.loadSettings();

        this.registerView(
            VIEW_TYPE_CHAT,
            (leaf) => new SovereignPairView(leaf, this)
        );

        this.addRibbonIcon('bot', 'Sovereign Pair Chat', () => {
            this.activateView();
        });

        this.addCommand({
            id: 'open-sovereign-pair-chat',
            name: 'Abrir Barra Lateral do Sovereign Pair',
            callback: () => {
                this.activateView();
            }
        });

        // 1. Interceptar Colagem de Arquivos (Ctrl+V)
        this.registerEvent(
            this.app.workspace.on('editor-paste', async (evt: ClipboardEvent, editor: Editor) => {
                if (evt.clipboardData && evt.clipboardData.files.length > 0) {
                    const file = evt.clipboardData.files[0];
                    new Notice(`Sovereign Pair: Recebendo arquivo colado '${file.name}' para o RAG...`);
                    await this.uploadFileToAPI(file);
                }
            })
        );

        // 2. Rotina de Auto-Sync de Notas Locais (A cada 5 minutos)
        this.registerInterval(
            window.setInterval(() => this.backgroundSync(), 5 * 60 * 1000)
        );
    }

    async uploadFileToAPI(file: File | Blob, filename?: string) {
        const formData = new FormData();
        // Se for um Blob, anexamos o nome explicitamente
        if (filename) {
            formData.append('file', file, filename);
            formData.append('force_overwrite', 'true'); // Auto-sync sobrescreve
        } else {
            formData.append('file', file as File);
        }

        try {
            const res = await fetch('http://127.0.0.1:8000/v1/upload', {
                method: 'POST',
                headers: this.settings.authToken ? { 'Authorization': `Bearer ${this.settings.authToken}` } : {},
                body: formData
            });
            const data = await res.json();
            if (data.status === 'conflict') {
                new Notice(`Sovereign Pair RAG: Conflito ignorado ao vetorizar ${filename || (file as File).name}.`);
            } else if (res.ok) {
                new Notice(`Sovereign Pair RAG: '${filename || (file as File).name}' indexado!`);
            }
        } catch (e) {
            console.error("Erro no upload RAG do Obsidian", e);
        }
    }

    async backgroundSync() {
        const now = Date.now();
        const files = this.app.vault.getMarkdownFiles();

        // Procura arquivos modificados desde a ultima sincronização
        const modifiedFiles = files.filter(f => f.stat.mtime > this.lastSyncTime);
        this.lastSyncTime = now;

        if (modifiedFiles.length === 0) return;

        for (const file of modifiedFiles) {
            try {
                const content = await this.app.vault.read(file);
                const blob = new Blob([content], { type: 'text/markdown' });
                await this.uploadFileToAPI(blob, file.name);
            } catch (e) {
                console.error("Background sync falhou para", file.name, e);
            }
        }
    }

    onunload() {
        console.log('Descarregando Sovereign Pair RAG Plugin...');
    }

    async loadSettings() {
        this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
    }

    async saveSettings() {
        await this.saveData(this.settings);
    }

    async activateView() {
        const { workspace } = this.app;

        let leaf: WorkspaceLeaf | null = null;
        const leaves = workspace.getLeavesOfType(VIEW_TYPE_CHAT);

        if (leaves.length > 0) {
            leaf = leaves[0];
        } else {
            leaf = workspace.getRightLeaf(false);
            if (leaf) {
                await leaf.setViewState({ type: VIEW_TYPE_CHAT, active: true });
            }
        }

        if (leaf) {
            workspace.revealLeaf(leaf);
        }
    }
}

class SovereignPairConfigModal extends Modal {
    plugin: SovereignPairPlugin;

    constructor(app: App, plugin: SovereignPairPlugin) {
        super(app);
        this.plugin = plugin;
    }

    async onOpen() {
        const { contentEl } = this;
        contentEl.empty();
        contentEl.createEl("h2", { text: "Sovereign Pair LLM Settings" });

        new Setting(contentEl)
            .setName('Token de Acesso (API Key)')
            .setDesc('Cole o Sovereign Token exibido na interface Web (Settings -> API Config).')
            .addText(text => text
                .setPlaceholder('ey...')
                .setValue(this.plugin.settings.authToken)
                .onChange(async (val) => {
                    this.plugin.settings.authToken = val.trim();
                    await this.plugin.saveSettings();
                })
            );

        const loadingMsg = contentEl.createEl("p", { text: "Carregando configurações do Backend RAG..." });

        try {
            const res = await fetch('http://127.0.0.1:8000/v1/config', {
                headers: this.plugin.settings.authToken ? { 'Authorization': `Bearer ${this.plugin.settings.authToken}` } : {}
            });
            if (res.ok) {
                const settings = await res.json();
                loadingMsg.remove();

                new Setting(contentEl)
                    .setName('Provedor LLM')
                    .setDesc('ollama, openai, groq, anthropic, gemini')
                    .addText(text => text
                        .setValue(settings.llm_provider)
                        .onChange(async (val) => { settings.llm_provider = val.trim(); })
                    );

                new Setting(contentEl)
                    .setName('Nome do Modelo')
                    .setDesc('Ex: llama3.2, gpt-4o, bge-m3')
                    .addText(text => text
                        .setValue(settings.llm_model)
                        .onChange(async (val) => { settings.llm_model = val.trim(); })
                    );

                new Setting(contentEl)
                    .setName('Temperatura (0.0 até 2.0)')
                    .setDesc('0 é frio e analítico, 2 é extremamente criativo.')
                    .addText(text => text
                        .setValue(settings.temperature.toString())
                        .onChange(async (val) => { settings.temperature = parseFloat(val) || 0.1; })
                    );

                new Setting(contentEl)
                    .setName('System Prompt / Persona')
                    .addTextArea(text => text
                        .setValue(settings.system_prompt)
                        .onChange(async (val) => { settings.system_prompt = val; })
                    );

                new Setting(contentEl)
                    .addButton(btn => btn
                        .setButtonText('Salvar no Servidor')
                        .setCta()
                        .onClick(async () => {
                            btn.setButtonText("Salvando...");
                            const putRes = await fetch('http://127.0.0.1:8000/v1/config', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                    ...(this.plugin.settings.authToken ? { 'Authorization': `Bearer ${this.plugin.settings.authToken}` } : {})
                                },
                                body: JSON.stringify(settings)
                            });
                            if (putRes.ok) {
                                new Notice('Configurações do LLM salvas no backend!');
                                this.close();
                            } else {
                                new Notice('Erro ao salvar as configurações.');
                                btn.setButtonText("Salvar no Servidor");
                            }
                        }));
            }
        } catch (e) {
            loadingMsg.innerText = "Erro ao conectar-se ao servidor RAG (http://127.0.0.1:8000).";
        }
    }

    onClose() {
        const { contentEl } = this;
        contentEl.empty();
    }
}
