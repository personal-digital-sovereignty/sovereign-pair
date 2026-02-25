import { App, Plugin, PluginSettingTab, Setting, ItemView, WorkspaceLeaf, MarkdownView } from 'obsidian';

export const VIEW_TYPE_CHAT = "sovereign-pair-chat-view";

export class SovereignPairView extends ItemView {
    messageContainer: HTMLElement;
    inputField: HTMLTextAreaElement;
    submitButton: HTMLButtonElement;

    constructor(leaf: WorkspaceLeaf) {
        super(leaf);
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

    async onOpen() {
        const container = this.containerEl.children[1];
        container.empty();
        container.addClass('sovereign-pair-container');

        const header = container.createEl("h2", { text: "Sovereign Pair" });
        header.style.textAlign = "center";
        header.style.marginBottom = "15px";

        // Messages Container
        this.messageContainer = container.createDiv({ cls: 'sp-messages-container' });
        this.messageContainer.style.flex = "1";
        this.messageContainer.style.overflowY = "auto";
        this.messageContainer.style.padding = "10px";
        this.messageContainer.style.display = "flex";
        this.messageContainer.style.flexDirection = "column";
        this.messageContainer.style.gap = "10px";

        // Adiciona mensagem de boas vindas
        this.addMessage("Olá! Sou a Sovereign Pair. Pergunte-me qualquer coisa sobre o seu Vault, ou sobre a anotação que você está lendo agora!", "ai");

        // Imput Area
        const inputArea = container.createDiv({ cls: 'sp-input-area' });
        inputArea.style.display = "flex";
        inputArea.style.gap = "8px";
        inputArea.style.marginTop = "10px";
        inputArea.style.padding = "10px";
        inputArea.style.borderTop = "1px solid var(--background-modifier-border)";

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

        this.submitButton = inputArea.createEl('button', { text: 'Envia' });
        this.submitButton.style.cursor = "pointer";
        this.submitButton.onclick = () => this.handleSubmit();
    }

    addMessage(content: string, sender: 'user' | 'ai'): HTMLElement {
        const bubble = this.messageContainer.createDiv({ cls: `sp-message sp-message-${sender}` });

        bubble.style.padding = "10px 14px";
        bubble.style.borderRadius = "8px";
        bubble.style.maxWidth = "90%";
        bubble.style.lineHeight = "1.5";

        if (sender === 'user') {
            bubble.style.alignSelf = "flex-end";
            bubble.style.backgroundColor = "var(--interactive-accent)";
            bubble.style.color = "var(--text-on-accent)";
        } else {
            bubble.style.alignSelf = "flex-start";
            bubble.style.backgroundColor = "var(--background-secondary-alt)";
            bubble.style.border = "1px solid var(--background-modifier-border)";
        }

        bubble.innerHTML = content; // Mudar para um renderizador markdown futuramente
        this.messageContainer.scrollTo({ top: this.messageContainer.scrollHeight, behavior: 'smooth' });
        return bubble;
    }

    async getActiveNoteContext(): Promise<string> {
        const activeView = this.app.workspace.getActiveViewOfType(MarkdownView);
        if (activeView) {
            const activeFile = activeView.file;
            if (activeFile) {
                const content = await this.app.vault.read(activeFile);
                return `[DOCUMENTO ATUAL QUE O USUÁRIO ESTÁ LENDO LENDO NO EDITOR:\nTítulo: ${activeFile.basename}\nCaminho: ${activeFile.path}\nConteúdo: ${content}\n--- FIM DO DOCUMENTO ATUAL ---]\n\n`;
            }
        }
        return "";
    }

    async handleSubmit() {
        const text = this.inputField.value.trim();
        if (!text) return;

        this.inputField.value = "";
        this.addMessage(text, 'user');

        const aiBubble = this.addMessage("...", 'ai');
        aiBubble.style.opacity = "0.7";

        try {
            // Capturar documento atual silenciosamente
            const activeContext = await this.getActiveNoteContext();
            const finalPrompt = activeContext ? `${activeContext}Considerando o documento atual acima que estou lendo no meu editor (caso a minha pergunta tenha relação com ele), responda à seguinte pergunta:\n${text}` : text;

            const response = await fetch('http://localhost:8000/v1/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: finalPrompt, stream: true })
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
            aiBubble.innerHTML = "⚠️ _Erro de conexão com o Motor FastAPI._ Verifique se `uvicorn` está rodando em localhost:8000.";
            console.error("SSE Error:", e);
        }
    }

    async onClose() { }
}

export default class SovereignPairPlugin extends Plugin {
    async onload() {
        console.log('Carregando Sovereign Pair RAG Plugin...');

        this.registerView(
            VIEW_TYPE_CHAT,
            (leaf) => new SovereignPairView(leaf)
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
    }

    onunload() {
        console.log('Descarregando Sovereign Pair RAG Plugin...');
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
