import { App, Plugin, PluginSettingTab, Setting, ItemView, WorkspaceLeaf } from 'obsidian';

export const VIEW_TYPE_CHAT = "sovereign-pair-chat-view";

export class SovereignPairView extends ItemView {
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

        const header = container.createEl("h2", { text: "Sovereign Pair RAG" });
        header.style.textAlign = "center";

        const subtitle = container.createEl("p", { text: "A IA Soberana conectada ao seu Vault." });
        subtitle.style.textAlign = "center";
        subtitle.style.color = "var(--text-muted)";
    }

    async onClose() {
        // Release resources
    }
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
            leaf = leaves[0]; // Se a janela já estiver aberta, focamos nela
        } else {
            // Se não estiver aberta, cria uma nova visão no painel direito (Right Sidebar)
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
