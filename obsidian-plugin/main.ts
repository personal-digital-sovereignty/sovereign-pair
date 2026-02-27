import { App, Plugin, PluginSettingTab, Setting, ItemView, WorkspaceLeaf, MarkdownView, Notice, Editor, MarkdownFileInfo, Modal, Component, MarkdownRenderer, SuggestModal } from 'obsidian';

export const VIEW_TYPE_CHAT = "sovereign-pair-chat-view";

interface SovereignPairSettings {
    apiUrl: string;
    authToken: string;
    historyViewMode: 'mini' | 'minimalist' | 'spotlight';
}

const DEFAULT_SETTINGS: SovereignPairSettings = {
    apiUrl: 'https://localhost',
    authToken: '',
    historyViewMode: 'mini'
}

export class SovereignPairView extends ItemView {
    messageContainer: HTMLElement;
    inputField: HTMLTextAreaElement;
    submitButton: HTMLButtonElement;
    sessionSelectBtn: HTMLButtonElement;
    sessionSelectNative: HTMLSelectElement;
    spotlightBtn: HTMLButtonElement;
    dropdownPanel: HTMLElement;
    searchInput: HTMLInputElement;
    sessionsListContainer: HTMLElement;

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

        // Container that holds the faux-select button and the dropdown panel relative to it
        const selectContainer = historyArea.createDiv();
        selectContainer.style.position = "relative";
        selectContainer.style.flex = "1";

        const viewMode = this.plugin.settings.historyViewMode || 'mini';

        if (viewMode === 'minimalist') {
            this.sessionSelectNative = selectContainer.createEl('select', { cls: 'sp-session-select' });
            this.sessionSelectNative.style.width = "100%";
            this.sessionSelectNative.style.padding = "6px 8px";
            this.sessionSelectNative.style.borderRadius = "4px";
            this.sessionSelectNative.style.backgroundColor = "var(--background-modifier-form-field)";
            this.sessionSelectNative.style.color = "var(--text-normal)";

            this.sessionSelectNative.onchange = async () => {
                const val = this.sessionSelectNative.value;
                if (val === 'new') {
                    this.currentSessionId = null;
                    this.messageContainer.empty();
                    this.addMessage("Nova conversa iniciada. Como posso ajudar?", "ai");
                } else {
                    await this.loadSession(parseInt(val));
                }
            };
        } else if (viewMode === 'spotlight') {
            this.spotlightBtn = selectContainer.createEl('button', { text: '🔍 Buscar Conversa (Spotlight)', cls: 'sp-session-btn' });
            this.spotlightBtn.style.width = "100%";
            this.spotlightBtn.style.textAlign = "left";
            this.spotlightBtn.style.padding = "4px 8px";
            this.spotlightBtn.style.borderRadius = "4px";
            this.spotlightBtn.style.backgroundColor = "var(--background-modifier-form-field)";
            this.spotlightBtn.style.color = "var(--text-normal)";
            this.spotlightBtn.style.border = "1px solid var(--background-modifier-border)";
            this.spotlightBtn.style.cursor = "pointer";

            this.spotlightBtn.onclick = () => {
                new SovereignPairHistoryModal(this.app, this).open();
            };
        } else {
            // viewMode === 'mini' Default
            this.sessionSelectBtn = selectContainer.createEl('button', { cls: 'sp-session-btn', text: '--- Nova Conversa ---' });
            this.sessionSelectBtn.style.width = "100%";
            this.sessionSelectBtn.style.textAlign = "left";
            this.sessionSelectBtn.style.padding = "4px 8px";
            this.sessionSelectBtn.style.borderRadius = "4px";
            this.sessionSelectBtn.style.backgroundColor = "var(--background-modifier-form-field)";
            this.sessionSelectBtn.style.color = "var(--text-normal)";
            this.sessionSelectBtn.style.border = "1px solid var(--background-modifier-border)";
            this.sessionSelectBtn.style.cursor = "pointer";
            this.sessionSelectBtn.style.display = "flex";
            this.sessionSelectBtn.style.justifyContent = "space-between";
            this.sessionSelectBtn.style.alignItems = "center";

            // Add a dropdown chevron icon to the button
            this.sessionSelectBtn.innerHTML = `<span>--- Nova Conversa ---</span><span style="opacity: 0.5; font-size: 0.8em;">▼</span>`;

            // The floating panel for the Mini-Web UI History
            this.dropdownPanel = selectContainer.createDiv({ cls: 'sp-history-dropdown' });
            this.dropdownPanel.style.position = "absolute";
            this.dropdownPanel.style.top = "100%";
            this.dropdownPanel.style.left = "0";
            this.dropdownPanel.style.width = "100%";
            this.dropdownPanel.style.zIndex = "1000";
            this.dropdownPanel.style.backgroundColor = "var(--background-primary)";
            this.dropdownPanel.style.border = "1px solid var(--background-modifier-border)";
            this.dropdownPanel.style.borderRadius = "4px";
            this.dropdownPanel.style.marginTop = "4px";
            this.dropdownPanel.style.boxShadow = "0 4px 6px rgba(0,0,0,0.1), 0 1px 3px rgba(0,0,0,0.08)";
            this.dropdownPanel.style.display = "none";
            this.dropdownPanel.style.flexDirection = "column";
            this.dropdownPanel.style.maxHeight = "400px";

            // The Search Input (Option 3 UX)
            const searchWrapper = this.dropdownPanel.createDiv();
            searchWrapper.style.padding = "8px";
            searchWrapper.style.borderBottom = "1px solid var(--background-modifier-border)";

            this.searchInput = searchWrapper.createEl('input', { type: 'text', placeholder: '🔎 Buscar conversas...' });
            this.searchInput.style.width = "100%";
            this.searchInput.style.backgroundColor = "var(--background-secondary)";
            this.searchInput.style.border = "1px solid var(--background-modifier-border)";
            this.searchInput.style.borderRadius = "4px";
            this.searchInput.style.padding = "6px 8px";

            // The scrollable list
            this.sessionsListContainer = this.dropdownPanel.createDiv();
            this.sessionsListContainer.style.flex = "1";
            this.sessionsListContainer.style.overflowY = "auto";
            this.sessionsListContainer.style.padding = "4px";
            this.sessionsListContainer.style.display = "flex";
            this.sessionsListContainer.style.flexDirection = "column";
            this.sessionsListContainer.style.gap = "4px";

            // Toggle logic
            this.sessionSelectBtn.addEventListener('click', () => {
                const isClosed = this.dropdownPanel.style.display === "none";
                this.dropdownPanel.style.display = isClosed ? "flex" : "none";
                if (isClosed) {
                    this.searchInput.value = '';
                    this.searchInput.dispatchEvent(new Event('keyup')); // reset filter
                    this.searchInput.focus();
                }
            });

            // Close when clicking outside
            document.addEventListener('click', (e) => {
                if (!selectContainer.contains(e.target as Node)) {
                    this.dropdownPanel.style.display = "none";
                }
            });

            // Search filter logic
            this.searchInput.addEventListener('keyup', (e) => {
                const query = this.searchInput.value.toLowerCase().trim();
                const isTagSearch = query.startsWith('#');
                const cleanQuery = isTagSearch ? query.replace(/^#/, '') : query;

                const buttons = this.sessionsListContainer.querySelectorAll('.sp-session-item') as NodeListOf<HTMLElement>;

                buttons.forEach(btn => {
                    const title = btn.getAttribute('data-title') || '';
                    const tagsData = btn.getAttribute('data-tags') || '[]';
                    let tags: string[] = [];
                    try { tags = JSON.parse(tagsData); } catch (e) { }

                    let isMatch = false;

                    if (isTagSearch) {
                        isMatch = tags.some(t => t.toLowerCase().includes(cleanQuery));
                    } else {
                        const titleMatch = title.toLowerCase().includes(cleanQuery);
                        const tagsMatch = tags.some(t => t.toLowerCase().includes(cleanQuery));
                        isMatch = titleMatch || tagsMatch;
                    }

                    btn.style.display = isMatch ? "flex" : "none";
                });
            });
        }

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
            bubble.setText(content);
        } else {
            bubble.style.backgroundColor = "var(--background-secondary-alt)";
            bubble.style.border = "1px solid var(--background-modifier-border)";
            // Use native Obsidian Markdown renderer for AI messages
            MarkdownRenderer.render(this.app, content, bubble, '', this.plugin as unknown as Component);
        }

        this.messageContainer.scrollTo({ top: this.messageContainer.scrollHeight, behavior: 'smooth' });

        return bubbleWrap;
    }

    addEditBar(wrapper: HTMLElement, content: string) {
        const actionBar = wrapper.createDiv();
        actionBar.style.display = "flex";
        actionBar.style.gap = "8px";
        actionBar.style.marginTop = "4px";
        actionBar.style.paddingRight = "4px";
        actionBar.style.alignSelf = "flex-end";
        actionBar.style.opacity = "0"; // Start hidden
        actionBar.style.transition = "opacity 0.2s";

        // Show on hover
        wrapper.addEventListener('mouseenter', () => actionBar.style.opacity = "1");
        wrapper.addEventListener('mouseleave', () => actionBar.style.opacity = "0");

        const btnEdit = actionBar.createEl("button");
        btnEdit.innerHTML = "✏️";
        btnEdit.title = "Editar e reescrever";
        btnEdit.style.background = "transparent";
        btnEdit.style.border = "none";
        btnEdit.style.cursor = "pointer";
        btnEdit.style.fontSize = "12px";
        btnEdit.style.opacity = "0.6";

        const btnResend = actionBar.createEl("button");
        btnResend.innerHTML = "🔄";
        btnResend.title = "Reenviar imediatamente";
        btnResend.style.background = "transparent";
        btnResend.style.border = "none";
        btnResend.style.cursor = "pointer";
        btnResend.style.fontSize = "12px";
        btnResend.style.opacity = "0.6";

        btnEdit.onclick = () => {
            this.inputField.value = content;
            this.inputField.focus();
        };

        btnResend.onclick = () => {
            this.inputField.value = content;
            this.handleSubmit();
        };
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
                await fetch(`${this.plugin.settings.apiUrl}/v1/feedback`, {
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
            const res = await fetch(`${this.plugin.settings.apiUrl}/v1/sessions`, {
                headers: this.getAuthHeaders()
            });
            if (res.ok) {
                this.sessionsList = await res.json();
                // Helper function to update the main button text
                const updateMainButton = (text: string) => {
                    if (this.sessionSelectBtn) {
                        this.sessionSelectBtn.empty();
                        const titleSpan = this.sessionSelectBtn.createEl('span');
                        titleSpan.style.whiteSpace = 'nowrap';
                        titleSpan.style.overflow = 'hidden';
                        titleSpan.style.textOverflow = 'ellipsis';
                        titleSpan.style.maxWidth = '85%';
                        titleSpan.setText(text);
                        const arrowSpan = this.sessionSelectBtn.createEl('span');
                        arrowSpan.style.opacity = '0.5';
                        arrowSpan.style.fontSize = '0.8em';
                        arrowSpan.style.flexShrink = '0';
                        arrowSpan.setText('▼');
                    }
                };

                const isCurrentSet = this.sessionsList.some(s => s.id === this.currentSessionId);
                const viewMode = this.plugin.settings.historyViewMode || 'mini';

                if (viewMode === 'minimalist' && this.sessionSelectNative) {
                    this.sessionSelectNative.empty();
                    this.sessionSelectNative.createEl('option', { value: 'new', text: '--- Nova Conversa ---' });
                    for (const sess of this.sessionsList) {
                        this.sessionSelectNative.createEl('option', { value: sess.id.toString(), text: sess.title });
                    }
                    if (isCurrentSet && this.currentSessionId !== null) {
                        this.sessionSelectNative.value = this.currentSessionId.toString();
                    } else {
                        this.sessionSelectNative.value = 'new';
                    }
                    return;
                }

                if (viewMode === 'spotlight' && this.spotlightBtn) {
                    if (!isCurrentSet || this.currentSessionId === null) {
                        this.spotlightBtn.setText(`🔍 Buscar Conversa (Spotlight)`);
                    } else {
                        const curr = this.sessionsList.find(s => s.id === this.currentSessionId);
                        this.spotlightBtn.setText(`🔍 ${curr?.title || 'Conversa'}`);
                    }
                    return;
                }

                // Default Mini-Web View Mode
                if (this.sessionsListContainer) this.sessionsListContainer.empty();

                if (!isCurrentSet || this.currentSessionId === null) {
                    updateMainButton('--- Nova Conversa ---');
                } else {
                    const curr = this.sessionsList.find(s => s.id === this.currentSessionId);
                    updateMainButton(curr?.title || 'Conversa');
                }

                if (!this.sessionsListContainer) return;

                // Add "Nova Conversa" button
                const newChatBtn = this.sessionsListContainer.createEl('button', { cls: 'sp-session-item sp-session-new' });
                newChatBtn.style.padding = "8px";
                newChatBtn.style.textAlign = "left";
                newChatBtn.style.backgroundColor = "var(--interactive-accent)";
                newChatBtn.style.color = "var(--text-on-accent)";
                newChatBtn.style.border = "none";
                newChatBtn.style.borderRadius = "4px";
                newChatBtn.style.cursor = "pointer";
                newChatBtn.style.fontWeight = "bold";
                newChatBtn.style.marginBottom = "8px";
                newChatBtn.style.display = "flex";
                newChatBtn.innerHTML = "➕ Nova Conversa";
                newChatBtn.setAttribute('data-title', 'nova conversa');

                newChatBtn.onclick = () => {
                    this.currentSessionId = null;
                    this.messageContainer.empty();
                    updateMainButton('--- Nova Conversa ---');
                    this.addMessage("Nova conversa iniciada. Como posso ajudar?", "ai");
                    this.dropdownPanel.style.display = "none";
                };

                // Group Sessions
                const today = new Date();
                today.setHours(0, 0, 0, 0);

                const yesterday = new Date(today);
                yesterday.setDate(yesterday.getDate() - 1);

                const lastWeek = new Date(today);
                lastWeek.setDate(lastWeek.getDate() - 7);

                const lastMonth = new Date(today);
                lastMonth.setMonth(lastMonth.getMonth() - 1);

                const groups: Record<string, any[]> = {
                    'Hoje': [],
                    'Ontem': [],
                    'Últimos 7 dias': [],
                    'Últimos 30 dias': [],
                    'Mais antigos': []
                };

                // Note: The API should sort by updated_at DESC, but we group them anyway.
                for (const sess of this.sessionsList) {
                    const updatedAt = sess.updated_at ? new Date(sess.updated_at) : new Date(0);
                    if (updatedAt >= today) groups['Hoje'].push(sess);
                    else if (updatedAt >= yesterday) groups['Ontem'].push(sess);
                    else if (updatedAt >= lastWeek) groups['Últimos 7 dias'].push(sess);
                    else if (updatedAt >= lastMonth) groups['Últimos 30 dias'].push(sess);
                    else groups['Mais antigos'].push(sess);
                }

                // Add past sessions by group
                for (const [groupName, sessions] of Object.entries(groups)) {
                    if (sessions.length === 0) continue;

                    const groupContainer = this.sessionsListContainer.createDiv({ cls: 'sp-history-group' });

                    const header = groupContainer.createDiv({ cls: 'sp-history-group-header' });
                    header.style.fontSize = "11px";
                    header.style.color = "var(--text-muted)";
                    header.style.textTransform = "uppercase";
                    header.style.letterSpacing = "0.05em";
                    header.style.padding = "10px 4px 4px 4px";
                    header.style.fontWeight = "bold";
                    header.innerText = groupName;

                    for (const sess of sessions) {
                        const btn = groupContainer.createEl('button', { cls: 'sp-session-item' });
                        btn.style.padding = "8px";
                        btn.style.textAlign = "left";
                        btn.style.backgroundColor = this.currentSessionId === sess.id ? "var(--background-modifier-active-hover)" : "transparent";
                        btn.style.border = "1px solid transparent";
                        btn.style.borderRadius = "4px";
                        btn.style.cursor = "pointer";
                        btn.style.display = "flex";
                        btn.style.flexDirection = "column";
                        btn.style.gap = "4px";
                        btn.style.transition = "background-color 0.1s";

                        btn.setAttribute('data-title', sess.title);
                        btn.setAttribute('data-tags', JSON.stringify(sess.tags || []));

                        // Truncate title
                        const titleSpan = btn.createSpan({ text: sess.title });
                        titleSpan.style.fontWeight = this.currentSessionId === sess.id ? "bold" : "normal";
                        titleSpan.style.width = "100%";
                        titleSpan.style.whiteSpace = "nowrap";
                        titleSpan.style.overflow = "hidden";
                        titleSpan.style.textOverflow = "ellipsis";
                        titleSpan.style.color = "var(--text-normal)";

                        // Add tags inline below title
                        if (sess.tags && sess.tags.length > 0) {
                            const tagsDiv = btn.createDiv();
                            tagsDiv.style.display = "flex";
                            tagsDiv.style.flexWrap = "wrap";
                            tagsDiv.style.gap = "4px";
                            for (const tag of sess.tags) {
                                const tagBadge = tagsDiv.createSpan({ text: `#${tag}` });
                                tagBadge.style.fontSize = "10px";
                                tagBadge.style.padding = "2px 6px";
                                tagBadge.style.backgroundColor = "var(--background-modifier-border)";
                                tagBadge.style.color = "var(--text-muted)";
                                tagBadge.style.borderRadius = "12px";
                            }
                        }

                        // Hover effects
                        btn.addEventListener('mouseenter', () => {
                            if (this.currentSessionId !== sess.id) btn.style.backgroundColor = "var(--background-modifier-hover)";
                        });
                        btn.addEventListener('mouseleave', () => {
                            if (this.currentSessionId !== sess.id) btn.style.backgroundColor = "transparent";
                        });

                        btn.onclick = async () => {
                            this.dropdownPanel.style.display = "none";
                            updateMainButton(sess.title);
                            await this.loadSession(sess.id);
                        };
                    }
                }
            }
        } catch (e) {
            console.error("Falha ao recuperar histórico", e);
        }
    }

    async loadSession(id: number) {
        try {
            const res = await fetch(`${this.plugin.settings.apiUrl}/v1/sessions/${id}`, {
                headers: this.getAuthHeaders()
            });
            if (res.ok) {
                const data = await res.json();
                this.currentSessionId = data.id;
                this.messageContainer.empty();

                for (const msg of data.messages) {
                    const wrap = this.addMessage(msg.content, msg.role as 'user' | 'ai');
                    if (msg.role === 'ai') {
                        this.addFeedbackBar(wrap, msg.id);
                    } else if (msg.role === 'user') {
                        this.addEditBar(wrap, msg.content);
                    }
                    if (msg.role === 'assistant') {
                        // Converter Markdown DB estático para algo visivel
                        const inner = wrap.querySelector('.sp-message-ai') as HTMLElement;
                        if (inner) {
                            inner.empty();
                            MarkdownRenderer.render(this.app, msg.content, inner, '', this.plugin as unknown as Component);
                        }
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
        const userWrap = this.addMessage(text, 'user');
        this.addEditBar(userWrap, text);

        const wrapperNode = this.addMessage("...", 'ai');
        const aiBubble = wrapperNode.querySelector('.sp-message-ai') as HTMLElement;
        aiBubble.style.opacity = "0.7";

        try {
            // Capturar documento atual silenciosamente
            const activeContext = await this.getActiveNoteContext();

            const response = await fetch(`${this.plugin.settings.apiUrl}/v1/chat`, {
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
                                        // Renderizando Markdown dinâmico no DOM do Obsidian
                                        aiBubble.empty();
                                        MarkdownRenderer.render(this.app, fullResponse, aiBubble, '', this.plugin);
                                        this.messageContainer.scrollTo({ top: this.messageContainer.scrollHeight });
                                    }
                                } catch (e) { console.error("Parse erro", e, dataStr); }
                            }
                        }
                    }
                }

                // One final render pass to ensure code blocks and formatting are perfectly sealed
                aiBubble.empty();
                MarkdownRenderer.render(this.app, fullResponse, aiBubble, '', this.plugin);
            }

        } catch (e) {
            aiBubble.innerHTML = "⚠️ _Erro de conexão com o Motor FastAPI._";
            console.error("SSE Error:", e);
        }
    }

    async onClose() { }
}

export class SovereignPairHistoryModal extends SuggestModal<any> {
    view: SovereignPairView;

    constructor(app: App, view: SovereignPairView) {
        super(app);
        this.view = view;
        this.setPlaceholder("Buscar chat ou tag...");
    }

    getSuggestions(query: string): any[] {
        const q = query.toLowerCase();
        const results = this.view.sessionsList.filter(s => {
            const titleMatch = s.title.toLowerCase().includes(q);
            const tagMatch = (s.tags || []).some((t: string) => t.toLowerCase().includes(q));
            return titleMatch || tagMatch;
        });

        // Sempre injeta o botão de Nova Conversa no topo se a busca estiver vazia ou próxima disso
        if (q.length === 0 || 'nova conversa'.includes(q)) {
            return [{ id: -1, title: '➕ Nova Conversa', tags: [] }, ...results];
        }
        return results;
    }

    renderSuggestion(sess: any, el: HTMLElement) {
        if (sess.id === -1) {
            el.createEl("strong", { text: sess.title });
            el.style.backgroundColor = "var(--interactive-accent)";
            el.style.color = "var(--text-on-accent)";
            return;
        }

        const container = el.createDiv();
        container.style.display = "flex";
        container.style.flexDirection = "column";
        container.style.gap = "2px";

        container.createDiv({ text: sess.title, cls: "sp-spotlight-title" });

        if (sess.tags && sess.tags.length > 0) {
            const tagsDiv = container.createDiv();
            tagsDiv.style.display = "flex";
            tagsDiv.style.gap = "4px";
            for (const tag of sess.tags) {
                const tagBadge = tagsDiv.createSpan({ text: `#${tag}` });
                tagBadge.style.fontSize = "10px";
                tagBadge.style.padding = "2px 4px";
                tagBadge.style.backgroundColor = "var(--background-modifier-border)";
                tagBadge.style.color = "var(--text-muted)";
                tagBadge.style.borderRadius = "8px";
            }
        }
    }

    async onChooseSuggestion(item: any, evt: MouseEvent | KeyboardEvent) {
        if (item.id === -1) {
            this.view.currentSessionId = null;
            this.view.messageContainer.empty();
            if (this.view.spotlightBtn) this.view.spotlightBtn.setText(`🔍 --- Nova Conversa ---`);
            this.view.addMessage("Nova conversa iniciada. Como posso ajudar?", "ai");
            return;
        }

        if (this.view.spotlightBtn) {
            this.view.spotlightBtn.setText(`🔍 ${item.title}`);
        }
        await this.view.loadSession(item.id);
    }
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
            const res = await fetch(`${this.settings.apiUrl}/v1/upload`, {
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
            .setName('Estilo de Navegação do Histórico')
            .setDesc('Escolha a fluidez de busca temporal (Mini-Web, Minimalista ou Modal Spotlight).')
            .addDropdown(dropdown => dropdown
                .addOption('mini', 'Mini-Web UI (Sovereign Pair)')
                .addOption('minimalist', 'Filtro Minimalista Genérico')
                .addOption('spotlight', 'Spotlight (Modal Central Flutuante)')
                .setValue(this.plugin.settings.historyViewMode || 'mini')
                .onChange(async (val: 'mini' | 'minimalist' | 'spotlight') => {
                    this.plugin.settings.historyViewMode = val;
                    await this.plugin.saveSettings();
                })
            );

        new Setting(contentEl)
            .setName('URL Base da API do Sovereign Pair')
            .setDesc('Insira a URL. Use https://localhost ou a URL pública. Com o Caddy, o Node conectará via porta HTTPS 443 implicitamente.')
            .addText(text => text
                .setPlaceholder('https://localhost')
                .setValue(this.plugin.settings.apiUrl)
                .onChange(async (val) => {
                    this.plugin.settings.apiUrl = val.replace(/\/+$/, "");
                    await this.plugin.saveSettings();
                })
            );

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
            const res = await fetch(`${this.plugin.settings.apiUrl}/v1/config`, {
                headers: this.plugin.settings.authToken ? { 'Authorization': `Bearer ${this.plugin.settings.authToken}` } : {}
            });
            if (res.ok) {
                const settings = await res.json();
                loadingMsg.remove();

                const modelOptionsByProvider: Record<string, Record<string, string>> = {
                    'ollama': {
                        'llama3.2': 'Llama 3.2 (Local)',
                        'llama3': 'Llama 3 (Local)',
                        'mistral': 'Mistral (Local)',
                        'gemma2': 'Gemma 2 (Local)',
                        'phi3': 'Phi-3 (Local)',
                        'qwen2.5': 'Qwen 2.5 (Local)',
                        'bge-m3': 'BGE-M3 (Ollama)'
                    },
                    'openai': {
                        'gpt-4o': 'GPT-4o',
                        'gpt-4o-mini': 'GPT-4o Mini',
                        'gpt-4-turbo': 'GPT-4 Turbo',
                        'gpt-3.5-turbo': 'GPT-3.5 Turbo'
                    },
                    'anthropic': {
                        'claude-3-5-sonnet-latest': 'Claude 3.5 Sonnet',
                        'claude-3-opus-latest': 'Claude 3 Opus',
                        'claude-3-haiku-20240307': 'Claude 3 Haiku'
                    },
                    'groq': {
                        'llama-3.1-70b-versatile': 'Llama 3.1 70B',
                        'llama-3.1-8b-instant': 'Llama 3.1 8B',
                        'mixtral-8x7b-32768': 'Mixtral 8x7B',
                        'gemma2-9b-it': 'Gemma 2 9B'
                    },
                    'gemini': {
                        'gemini-1.5-pro-latest': 'Gemini 1.5 Pro',
                        'gemini-1.5-flash-latest': 'Gemini 1.5 Flash',
                        'gemini-pro': 'Gemini Pro'
                    }
                };

                let modelDropdownComponent: any;
                let customModelTextComponent: any;

                const updateModelDropdown = async (provider: string) => {
                    if (!modelDropdownComponent) return;

                    modelDropdownComponent.selectEl.innerHTML = '';
                    modelDropdownComponent.selectEl.disabled = true;

                    if (provider === 'ollama') {
                        try {
                            const res = await fetch('http://127.0.0.1:11434/api/tags'); // nosemgrep: typescript.react.security.react-insecure-request.react-insecure-request
                            if (res.ok) {
                                const data = await res.json();
                                const dynamicOptions: Record<string, string> = {};
                                if (data.models && data.models.length > 0) {
                                    data.models.forEach((m: any) => {
                                        dynamicOptions[m.name] = m.name + ' (Local)';
                                    });
                                    modelOptionsByProvider['ollama'] = dynamicOptions;
                                }
                            }
                        } catch (e) {
                            console.warn("SovereignPair: Failed to fetch Ollama models natively, falling back to cached list.", e);
                        }
                    }

                    modelDropdownComponent.selectEl.disabled = false;

                    const options = modelOptionsByProvider[provider] || modelOptionsByProvider['ollama'];
                    for (const [key, value] of Object.entries(options)) {
                        modelDropdownComponent.addOption(key, value);
                    }
                    modelDropdownComponent.addOption('custom', 'Outro (Personalizado)');

                    const currentModel = settings.llm_model;
                    if (Object.keys(options).includes(currentModel)) {
                        modelDropdownComponent.setValue(currentModel);
                        if (customModelTextComponent) customModelTextComponent.inputEl.parentElement.parentElement.style.display = 'none';
                    } else if (currentModel) {
                        modelDropdownComponent.setValue('custom');
                        if (customModelTextComponent) {
                            customModelTextComponent.setValue(currentModel);
                            customModelTextComponent.inputEl.parentElement.parentElement.style.display = 'flex';
                        }
                    } else {
                        const firstOption = Object.keys(options)[0];
                        if (firstOption) {
                            modelDropdownComponent.setValue(firstOption);
                            settings.llm_model = firstOption;
                            if (customModelTextComponent) customModelTextComponent.inputEl.parentElement.parentElement.style.display = 'none';
                        } else {
                            modelDropdownComponent.setValue('custom');
                        }
                    }
                };

                new Setting(contentEl)
                    .setName('Provedor LLM')
                    .setDesc('Selecione o motor de inferência (Local ou Cloud)')
                    .addDropdown(dropdown => dropdown
                        .addOption('ollama', 'Ollama (Local)')
                        .addOption('openai', 'OpenAI')
                        .addOption('anthropic', 'Anthropic')
                        .addOption('groq', 'Groq')
                        .addOption('gemini', 'Google Gemini')
                        .setValue(settings.llm_provider || 'ollama')
                        .onChange(async (val) => {
                            settings.llm_provider = val;
                            updateModelDropdown(val);
                        })
                    );

                new Setting(contentEl)
                    .setName('Nome do Modelo')
                    .setDesc('Selecione um modelo da lista sugerida pelo provedor ou escolha Personalizado.')
                    .addDropdown(dropdown => {
                        modelDropdownComponent = dropdown;
                        dropdown.onChange(async (val) => {
                            if (val === 'custom') {
                                if (customModelTextComponent) {
                                    customModelTextComponent.inputEl.parentElement.parentElement.style.display = 'flex';
                                    settings.llm_model = customModelTextComponent.getValue();
                                }
                            } else {
                                if (customModelTextComponent) customModelTextComponent.inputEl.parentElement.parentElement.style.display = 'none';
                                settings.llm_model = val;
                            }
                        });
                    });

                const customModelSetting = new Setting(contentEl)
                    .setName('Modelo Personalizado')
                    .setDesc('Digite o ID/Tag exata do modelo (ex: my-custom-model:latest)')
                    .addText(text => {
                        customModelTextComponent = text;
                        text.setValue(settings.llm_model)
                            .onChange(async (val) => {
                                if (modelDropdownComponent.getValue() === 'custom') {
                                    settings.llm_model = val.trim();
                                }
                            });
                    });

                // Hide custom setting by default, visibility is handled by updateModelDropdown
                customModelSetting.settingEl.style.display = 'none';

                // Initialize the model dropdown with current provider
                await updateModelDropdown(settings.llm_provider || 'ollama');

                new Setting(contentEl)
                    .setName('Temperatura (Criatividade)')
                    .setDesc('Valores próximos de 0.0 geram respostas mais analíticas e exatas. Valores altos aumentam a criatividade.')
                    .addSlider(slider => slider
                        .setLimits(0.0, 2.0, 0.1)
                        .setValue(settings.temperature || 0.1)
                        .setDynamicTooltip()
                        .onChange(async (val) => { settings.temperature = val; })
                    );

                const personaOptions = [
                    { id: 'default', name: 'Assistente Padrão (Default)', prompt: 'Foco em respostas analíticas, pragmáticas e diretas. Traga conhecimento fundamentado sem enrolação.' },
                    { id: 'developer', name: 'Desenvolvedor Sênior', prompt: 'Aja como um Arquiteto de Software sênior. Foco em código limpo (Clean Code), design patterns, otimização de performance e explicações técnicas concisas e precisas.' },
                    { id: 'marketing', name: 'Mestre do Marketing', prompt: 'Você é um especialista em Marketing Digital. Use copywriting persuasivo focado em conversão, métricas, SEO e lançamento de produtos. Adote um tom empolgante.' },
                    { id: 'admin', name: 'Gestor & Admin', prompt: 'Aja como um administrador de empresas e gerente de projetos sênior. Foco em organização corporativa, planilhas estruturadas, relatórios processuais e finanças limpas.' },
                    { id: 'professor', name: 'Professor Acadêmico', prompt: 'Você é um mentor acadêmico compassivo e sagaz. Explique conceitos complexos com metáforas didáticas, passo a passo, fomentando o raciocínio sem dar apenas a resposta pronta imediata.' },
                    { id: 'career', name: 'Mentor de Carreira', prompt: 'Você é um Headhunter experiente. Foco na evolução profissional do usuário, melhoria de propostas de valor (currículos e portfólios) e dicas cirúrgicas de networking e entrevistas.' },
                    { id: 'productivity', name: 'Hacker de Rendimento', prompt: 'Comporte-se como um executor fanático por otimização de tempo. Foco rígido na geração de checklists diretos, métodos ágeis (Kanban/Scrum) e atalhos de produtividade extrema.' },
                    { id: 'creative', name: 'Brainstormer Criativo', prompt: 'Seja extremamente imaginativo e fora-da-caixa. Seu objetivo é ajudar a encontrar soluções inovadoras para problemas normais, usando um tom entusiasmado e proativo. Proponha cenários alternativos abundantes.' }
                ];

                let promptTextArea: any;
                let personaDropdownComponent: any;

                new Setting(contentEl)
                    .setName('Comportamento da IA (Persona)')
                    .setDesc('Escolha a especialidade ou selecione Personalizado e altere o campo abaixo manualmente.')
                    .addDropdown(dropdown => {
                        personaDropdownComponent = dropdown;
                        for (const p of personaOptions) dropdown.addOption(p.id, p.name);
                        dropdown.addOption('custom', 'Personalizado');

                        dropdown.setValue(settings.persona || 'default');
                        dropdown.onChange(async (val) => {
                            settings.persona = val;
                            if (val !== 'custom') {
                                const selected = personaOptions.find(p => p.id === val);
                                if (selected) {
                                    settings.system_prompt = selected.prompt;
                                    if (promptTextArea) promptTextArea.setValue(selected.prompt);
                                }
                            }
                        });
                    });

                new Setting(contentEl)
                    .setName('Instrução Base (System Prompt)')
                    .addTextArea(text => {
                        promptTextArea = text;
                        text.setValue(settings.system_prompt)
                            .onChange(async (val) => {
                                settings.system_prompt = val;
                                settings.persona = 'custom';
                                if (personaDropdownComponent) personaDropdownComponent.setValue('custom');
                            });
                        text.inputEl.style.minHeight = "100px";
                        text.inputEl.style.width = "100%";
                    });

                new Setting(contentEl)
                    .setName('Tratamento e Formalidade')
                    .setDesc('Força a IA a tratar a si mesma no gênero desejado.')
                    .addDropdown(dropdown => dropdown
                        .addOption('feminine', 'Assistente ♀️')
                        .addOption('neutral', 'Neutro 🤖')
                        .addOption('masculine', 'Assistente ♂️')
                        .setValue(settings.formality || 'neutral')
                        .onChange(async (val) => { settings.formality = val; })
                    );

                new Setting(contentEl)
                    .setName('Estilo Visual das Personas')
                    .setDesc('Sincroniza o Avatar visual com a Web UI globalmente.')
                    .addDropdown(dropdown => dropdown
                        .addOption('emoji', 'Emojis 🧠')
                        .addOption('vector', 'Cérebro Virtual 🧬')
                        .addOption('dots', 'Minimal 🟢')
                        .setValue(settings.persona_graphic_style || 'emoji')
                        .onChange(async (val) => { settings.persona_graphic_style = val; })
                    );

                contentEl.createEl("h3", { text: "Sobre Você (Contexto de Memória)", cls: "sp-settings-section-title" });

                new Setting(contentEl)
                    .setName('Como a IA deve te chamar?')
                    .setDesc('Seu nome ou apelido informal (Nickname).')
                    .addText(text => text
                        .setPlaceholder('Ex: Mestre Jedi')
                        .setValue(settings.nickname || '')
                        .onChange(async (val) => { settings.nickname = val.trim(); })
                    );

                new Setting(contentEl)
                    .setName('Ocupação / Atuação')
                    .setDesc('Sua profissão principal (Ex: "Designer de Interiores").')
                    .addText(text => text
                        .setPlaceholder('Ex: Dev Backend Pleno')
                        .setValue(settings.occupation || '')
                        .onChange(async (val) => { settings.occupation = val.trim(); })
                    );

                new Setting(contentEl)
                    .setName('Mais sobre você')
                    .setDesc('Interesses, regras pessoais ou preferências que a IA deve lembrar.')
                    .addTextArea(text => {
                        text.setPlaceholder('Gosto de explicações curtas em bullet points...');
                        text.setValue(settings.about_user || '')
                            .onChange(async (val) => { settings.about_user = val; });
                        text.inputEl.style.minHeight = "80px";
                        text.inputEl.style.width = "100%";
                    });

                new Setting(contentEl)
                    .setName('Idioma & Localização Escrita')
                    .setDesc('Defina o sotaque ou idioma base do assistente.')
                    .addDropdown(dropdown => dropdown
                        .addOption('Português do Brasil', 'Português do Brasil')
                        .addOption('Português (Carioca)', '🇧🇷 Português (Carioca)')
                        .addOption('Português (Paulistano)', '🇧🇷 Português (Paulistano)')
                        .addOption('Português (Mineiro)', '🇧🇷 Português (Mineiro)')
                        .addOption('Português (Nordestino)', '🇧🇷 Português (Nordestino)')
                        .addOption('Português de Portugal', '🇵🇹 Português de Portugal')
                        .addOption('Inglês (EUA)', '🇺🇸 Inglês Americano')
                        .addOption('Espanhol', '🇪🇸 Espanhol')
                        .setValue(settings.language || 'Português do Brasil')
                        .onChange(async (val) => { settings.language = val; })
                    );

                new Setting(contentEl)
                    .setName('Geolocalização / Base de Operações')
                    .setDesc('Sua cidade/país. Ajuda a IA a contextualizar clima, regiões e RAG.')
                    .addText(text => text
                        .setPlaceholder('Ex: São Paulo, Brasil')
                        .setValue(settings.geolocation || '')
                        .onChange(async (val) => { settings.geolocation = val.trim(); })
                    );
                contentEl.createEl("br");

                new Setting(contentEl)
                    .addButton(btn => btn
                        .setButtonText('Salvar no Servidor')
                        .setCta()
                        .onClick(async () => {
                            btn.setButtonText("Salvando...");
                            const putRes = await fetch(`${this.plugin.settings.apiUrl}/v1/config`, {
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
            loadingMsg.innerText = `Erro ao conectar-se ao servidor RAG (${this.plugin.settings.apiUrl}).`;
        }
    }

    onClose() {
        const { contentEl } = this;
        contentEl.empty();
    }
}
