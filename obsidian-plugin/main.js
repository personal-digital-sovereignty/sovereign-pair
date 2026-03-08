/*
Este é um arquivo compilado pelo esbuild para uso exclusivo no Obsidian.
Não edite este arquivo diretamente.
*/

var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __export = (target, all) => {
  for (var name in all)
    __defProp(target, name, { get: all[name], enumerable: true });
};
var __copyProps = (to, from, except, desc) => {
  if (from && typeof from === "object" || typeof from === "function") {
    for (let key of __getOwnPropNames(from))
      if (!__hasOwnProp.call(to, key) && key !== except)
        __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
  }
  return to;
};
var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);

// main.ts
var main_exports = {};
__export(main_exports, {
  SovereignPairHistoryModal: () => SovereignPairHistoryModal,
  SovereignPairView: () => SovereignPairView,
  VIEW_TYPE_CHAT: () => VIEW_TYPE_CHAT,
  default: () => SovereignPairPlugin
});
module.exports = __toCommonJS(main_exports);
var import_obsidian = require("obsidian");
var VIEW_TYPE_CHAT = "sovereign-pair-chat-view";
var DEFAULT_SETTINGS = {
  apiUrl: "https://localhost",
  authToken: "",
  historyViewMode: "mini"
};
var SovereignPairView = class extends import_obsidian.ItemView {
  constructor(leaf, plugin) {
    super(leaf);
    this.currentSessionId = null;
    this.sessionsList = [];
    // Gerador de ID local fake pro DOM (quando o Backend não retornou ainda o message_id real na UI Vanilla)
    this._fallbackIdCounter = 999e3;
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
  getAuthHeaders() {
    const token = this.plugin.settings.authToken;
    return token ? { "Authorization": `Bearer ${token}` } : {};
  }
  async onOpen() {
    const container = this.containerEl.children[1];
    container.empty();
    container.addClass("sovereign-pair-container");
    const containerEl = container;
    containerEl.style.userSelect = "text";
    containerEl.style.webkitUserSelect = "text";
    const header = container.createEl("h2", { text: "Sovereign Pair" });
    header.style.textAlign = "center";
    header.style.marginBottom = "15px";
    const historyArea = container.createDiv({ cls: "sp-history-area" });
    historyArea.style.padding = "5px 10px 10px";
    historyArea.style.display = "flex";
    historyArea.style.alignItems = "center";
    historyArea.style.justifyContent = "space-between";
    historyArea.style.gap = "8px";
    const selectContainer = historyArea.createDiv();
    selectContainer.style.position = "relative";
    selectContainer.style.flex = "1";
    const viewMode = this.plugin.settings.historyViewMode || "mini";
    if (viewMode === "minimalist") {
      this.sessionSelectNative = selectContainer.createEl("select", { cls: "sp-session-select" });
      this.sessionSelectNative.style.width = "100%";
      this.sessionSelectNative.style.padding = "6px 8px";
      this.sessionSelectNative.style.borderRadius = "4px";
      this.sessionSelectNative.style.backgroundColor = "var(--background-modifier-form-field)";
      this.sessionSelectNative.style.color = "var(--text-normal)";
      this.sessionSelectNative.onchange = async () => {
        const val = this.sessionSelectNative.value;
        if (val === "new") {
          this.currentSessionId = null;
          this.messageContainer.empty();
          this.addMessage("Nova conversa iniciada. Como posso ajudar?", "ai");
        } else {
          await this.loadSession(parseInt(val));
        }
      };
    } else if (viewMode === "spotlight") {
      this.spotlightBtn = selectContainer.createEl("button", { text: "\u{1F50D} Buscar Conversa (Spotlight)", cls: "sp-session-btn" });
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
      this.sessionSelectBtn = selectContainer.createEl("button", { cls: "sp-session-btn", text: "--- Nova Conversa ---" });
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
      this.sessionSelectBtn.innerHTML = `<span>--- Nova Conversa ---</span><span style="opacity: 0.5; font-size: 0.8em;">\u25BC</span>`;
      this.dropdownPanel = selectContainer.createDiv({ cls: "sp-history-dropdown" });
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
      const searchWrapper = this.dropdownPanel.createDiv();
      searchWrapper.style.padding = "8px";
      searchWrapper.style.borderBottom = "1px solid var(--background-modifier-border)";
      this.searchInput = searchWrapper.createEl("input", { type: "text", placeholder: "\u{1F50E} Buscar conversas..." });
      this.searchInput.style.width = "100%";
      this.searchInput.style.backgroundColor = "var(--background-secondary)";
      this.searchInput.style.border = "1px solid var(--background-modifier-border)";
      this.searchInput.style.borderRadius = "4px";
      this.searchInput.style.padding = "6px 8px";
      this.sessionsListContainer = this.dropdownPanel.createDiv();
      this.sessionsListContainer.style.flex = "1";
      this.sessionsListContainer.style.overflowY = "auto";
      this.sessionsListContainer.style.padding = "4px";
      this.sessionsListContainer.style.display = "flex";
      this.sessionsListContainer.style.flexDirection = "column";
      this.sessionsListContainer.style.gap = "4px";
      this.sessionSelectBtn.addEventListener("click", () => {
        const isClosed = this.dropdownPanel.style.display === "none";
        this.dropdownPanel.style.display = isClosed ? "flex" : "none";
        if (isClosed) {
          this.searchInput.value = "";
          this.searchInput.dispatchEvent(new Event("keyup"));
          this.searchInput.focus();
        }
      });
      document.addEventListener("click", (e) => {
        if (!selectContainer.contains(e.target)) {
          this.dropdownPanel.style.display = "none";
        }
      });
      this.searchInput.addEventListener("keyup", (e) => {
        const query = this.searchInput.value.toLowerCase().trim();
        const isTagSearch = query.startsWith("#");
        const cleanQuery = isTagSearch ? query.replace(/^#/, "") : query;
        const buttons = this.sessionsListContainer.querySelectorAll(".sp-session-item");
        buttons.forEach((btn) => {
          const title = btn.getAttribute("data-title") || "";
          const tagsData = btn.getAttribute("data-tags") || "[]";
          let tags = [];
          try {
            tags = JSON.parse(tagsData);
          } catch (e2) {
          }
          let isMatch = false;
          if (isTagSearch) {
            isMatch = tags.some((t) => t.toLowerCase().includes(cleanQuery));
          } else {
            const titleMatch = title.toLowerCase().includes(cleanQuery);
            const tagsMatch = tags.some((t) => t.toLowerCase().includes(cleanQuery));
            isMatch = titleMatch || tagsMatch;
          }
          btn.style.display = isMatch ? "flex" : "none";
        });
      });
    }
    const refreshBtn = historyArea.createEl("button", { text: "\u{1F504}", title: "Recarregar Sess\xF5es" });
    refreshBtn.style.cursor = "pointer";
    refreshBtn.style.padding = "4px 8px";
    refreshBtn.style.background = "transparent";
    refreshBtn.style.border = "1px solid var(--background-modifier-border)";
    refreshBtn.style.borderRadius = "4px";
    refreshBtn.onclick = () => this.refreshSessionsList();
    const configBtn = historyArea.createEl("button", { text: "\u2699\uFE0F", title: "Configura\xE7\xF5es LLM" });
    configBtn.style.cursor = "pointer";
    configBtn.style.padding = "4px 8px";
    configBtn.style.background = "transparent";
    configBtn.style.border = "1px solid var(--background-modifier-border)";
    configBtn.style.borderRadius = "4px";
    configBtn.onclick = () => {
      new SovereignPairConfigModal(this.app, this.plugin).open();
    };
    this.messageContainer = container.createDiv({ cls: "sp-messages-container" });
    this.messageContainer.style.flex = "1";
    this.messageContainer.style.overflowY = "auto";
    this.messageContainer.style.padding = "10px";
    this.messageContainer.style.display = "flex";
    this.messageContainer.style.flexDirection = "column";
    this.messageContainer.style.gap = "10px";
    this.addMessage("Ol\xE1! Sou a Sovereign Pair. Pergunte-me qualquer coisa sobre o seu Vault, ou sobre a anota\xE7\xE3o que voc\xEA est\xE1 lendo agora!", "ai");
    const inputArea = container.createDiv({ cls: "sp-input-area" });
    inputArea.style.display = "flex";
    inputArea.style.gap = "8px";
    inputArea.style.marginTop = "10px";
    inputArea.style.padding = "10px";
    inputArea.style.borderTop = "1px solid var(--background-modifier-border)";
    inputArea.style.paddingBottom = "30px";
    this.inputField = inputArea.createEl("textarea", {
      cls: "sp-chat-input",
      attr: { placeholder: "Sovereign Pair vai analisar sua nota ativa..." }
    });
    this.inputField.style.flex = "1";
    this.inputField.style.resize = "none";
    this.inputField.style.height = "50px";
    this.inputField.style.borderRadius = "5px";
    this.inputField.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        this.handleSubmit();
      }
    });
    this.submitButton = inputArea.createEl("button", { text: "Envia" });
    this.submitButton.style.cursor = "pointer";
    this.submitButton.onclick = () => this.handleSubmit();
    this.refreshSessionsList();
  }
  addMessage(content, sender) {
    const bubbleWrap = this.messageContainer.createDiv({ cls: `sp-message-wrapper sp-wrapper-${sender}` });
    bubbleWrap.style.display = "flex";
    bubbleWrap.style.flexDirection = "column";
    if (sender === "user") bubbleWrap.style.alignItems = "flex-end";
    else bubbleWrap.style.alignItems = "flex-start";
    const bubble = bubbleWrap.createDiv({ cls: `sp-message sp-message-${sender}` });
    bubble.style.padding = "10px 14px";
    bubble.style.borderRadius = "8px";
    bubble.style.maxWidth = "90%";
    bubble.style.lineHeight = "1.5";
    if (sender === "user") {
      bubble.style.backgroundColor = "var(--interactive-accent)";
      bubble.style.color = "var(--text-on-accent)";
      bubble.setText(content);
    } else {
      bubble.style.backgroundColor = "var(--background-secondary-alt)";
      bubble.style.border = "1px solid var(--background-modifier-border)";
      import_obsidian.MarkdownRenderer.render(this.app, content, bubble, "", this.plugin);
    }
    this.messageContainer.scrollTo({ top: this.messageContainer.scrollHeight, behavior: "smooth" });
    return bubbleWrap;
  }
  addEditBar(wrapper, content) {
    const actionBar = wrapper.createDiv();
    actionBar.style.display = "flex";
    actionBar.style.gap = "8px";
    actionBar.style.marginTop = "4px";
    actionBar.style.paddingRight = "4px";
    actionBar.style.alignSelf = "flex-end";
    actionBar.style.opacity = "0";
    actionBar.style.transition = "opacity 0.2s";
    wrapper.addEventListener("mouseenter", () => actionBar.style.opacity = "1");
    wrapper.addEventListener("mouseleave", () => actionBar.style.opacity = "0");
    const btnEdit = actionBar.createEl("button");
    btnEdit.innerHTML = "\u270F\uFE0F";
    btnEdit.title = "Editar e reescrever";
    btnEdit.style.background = "transparent";
    btnEdit.style.border = "none";
    btnEdit.style.cursor = "pointer";
    btnEdit.style.fontSize = "12px";
    btnEdit.style.opacity = "0.6";
    const btnResend = actionBar.createEl("button");
    btnResend.innerHTML = "\u{1F504}";
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
  addFeedbackBar(wrapper, messageId) {
    const actionBar = wrapper.createDiv();
    actionBar.style.display = "flex";
    actionBar.style.gap = "8px";
    actionBar.style.marginTop = "4px";
    actionBar.style.paddingLeft = "4px";
    const btnUp = actionBar.createEl("button");
    btnUp.innerHTML = "\u{1F44D}";
    btnUp.style.background = "transparent";
    btnUp.style.border = "none";
    btnUp.style.cursor = "pointer";
    btnUp.style.fontSize = "12px";
    btnUp.style.opacity = "0.6";
    const btnDown = actionBar.createEl("button");
    btnDown.innerHTML = "\u{1F44E}";
    btnDown.style.background = "transparent";
    btnDown.style.border = "none";
    btnDown.style.cursor = "pointer";
    btnDown.style.fontSize = "12px";
    btnDown.style.opacity = "0.6";
    const sendFeedback = async (up, down) => {
      btnUp.style.opacity = up ? "1" : "0.3";
      btnDown.style.opacity = down ? "1" : "0.3";
      try {
        await fetch(`${this.plugin.settings.apiUrl}/v1/feedback`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
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
        const updateMainButton = (text) => {
          if (this.sessionSelectBtn) {
            this.sessionSelectBtn.empty();
            const titleSpan = this.sessionSelectBtn.createEl("span");
            titleSpan.style.whiteSpace = "nowrap";
            titleSpan.style.overflow = "hidden";
            titleSpan.style.textOverflow = "ellipsis";
            titleSpan.style.maxWidth = "85%";
            titleSpan.setText(text);
            const arrowSpan = this.sessionSelectBtn.createEl("span");
            arrowSpan.style.opacity = "0.5";
            arrowSpan.style.fontSize = "0.8em";
            arrowSpan.style.flexShrink = "0";
            arrowSpan.setText("\u25BC");
          }
        };
        const isCurrentSet = this.sessionsList.some((s) => s.id === this.currentSessionId);
        const viewMode = this.plugin.settings.historyViewMode || "mini";
        if (viewMode === "minimalist" && this.sessionSelectNative) {
          this.sessionSelectNative.empty();
          this.sessionSelectNative.createEl("option", { value: "new", text: "--- Nova Conversa ---" });
          for (const sess of this.sessionsList) {
            this.sessionSelectNative.createEl("option", { value: sess.id.toString(), text: sess.title });
          }
          if (isCurrentSet && this.currentSessionId !== null) {
            this.sessionSelectNative.value = this.currentSessionId.toString();
          } else {
            this.sessionSelectNative.value = "new";
          }
          return;
        }
        if (viewMode === "spotlight" && this.spotlightBtn) {
          if (!isCurrentSet || this.currentSessionId === null) {
            this.spotlightBtn.setText(`\u{1F50D} Buscar Conversa (Spotlight)`);
          } else {
            const curr = this.sessionsList.find((s) => s.id === this.currentSessionId);
            this.spotlightBtn.setText(`\u{1F50D} ${(curr == null ? void 0 : curr.title) || "Conversa"}`);
          }
          return;
        }
        if (this.sessionsListContainer) this.sessionsListContainer.empty();
        if (!isCurrentSet || this.currentSessionId === null) {
          updateMainButton("--- Nova Conversa ---");
        } else {
          const curr = this.sessionsList.find((s) => s.id === this.currentSessionId);
          updateMainButton((curr == null ? void 0 : curr.title) || "Conversa");
        }
        if (!this.sessionsListContainer) return;
        const newChatBtn = this.sessionsListContainer.createEl("button", { cls: "sp-session-item sp-session-new" });
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
        newChatBtn.innerHTML = "\u2795 Nova Conversa";
        newChatBtn.setAttribute("data-title", "nova conversa");
        newChatBtn.onclick = () => {
          this.currentSessionId = null;
          this.messageContainer.empty();
          updateMainButton("--- Nova Conversa ---");
          this.addMessage("Nova conversa iniciada. Como posso ajudar?", "ai");
          this.dropdownPanel.style.display = "none";
        };
        const today = /* @__PURE__ */ new Date();
        today.setHours(0, 0, 0, 0);
        const yesterday = new Date(today);
        yesterday.setDate(yesterday.getDate() - 1);
        const lastWeek = new Date(today);
        lastWeek.setDate(lastWeek.getDate() - 7);
        const lastMonth = new Date(today);
        lastMonth.setMonth(lastMonth.getMonth() - 1);
        const groups = {
          "Hoje": [],
          "Ontem": [],
          "\xDAltimos 7 dias": [],
          "\xDAltimos 30 dias": [],
          "Mais antigos": []
        };
        for (const sess of this.sessionsList) {
          const updatedAt = sess.updated_at ? new Date(sess.updated_at) : /* @__PURE__ */ new Date(0);
          if (updatedAt >= today) groups["Hoje"].push(sess);
          else if (updatedAt >= yesterday) groups["Ontem"].push(sess);
          else if (updatedAt >= lastWeek) groups["\xDAltimos 7 dias"].push(sess);
          else if (updatedAt >= lastMonth) groups["\xDAltimos 30 dias"].push(sess);
          else groups["Mais antigos"].push(sess);
        }
        for (const [groupName, sessions] of Object.entries(groups)) {
          if (sessions.length === 0) continue;
          const groupContainer = this.sessionsListContainer.createDiv({ cls: "sp-history-group" });
          const header = groupContainer.createDiv({ cls: "sp-history-group-header" });
          header.style.fontSize = "11px";
          header.style.color = "var(--text-muted)";
          header.style.textTransform = "uppercase";
          header.style.letterSpacing = "0.05em";
          header.style.padding = "10px 4px 4px 4px";
          header.style.fontWeight = "bold";
          header.innerText = groupName;
          for (const sess of sessions) {
            const btn = groupContainer.createEl("button", { cls: "sp-session-item" });
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
            btn.setAttribute("data-title", sess.title);
            btn.setAttribute("data-tags", JSON.stringify(sess.tags || []));
            const titleSpan = btn.createSpan({ text: sess.title });
            titleSpan.style.fontWeight = this.currentSessionId === sess.id ? "bold" : "normal";
            titleSpan.style.width = "100%";
            titleSpan.style.whiteSpace = "nowrap";
            titleSpan.style.overflow = "hidden";
            titleSpan.style.textOverflow = "ellipsis";
            titleSpan.style.color = "var(--text-normal)";
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
            btn.addEventListener("mouseenter", () => {
              if (this.currentSessionId !== sess.id) btn.style.backgroundColor = "var(--background-modifier-hover)";
            });
            btn.addEventListener("mouseleave", () => {
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
      console.error("Falha ao recuperar hist\xF3rico", e);
    }
  }
  async loadSession(id) {
    try {
      const res = await fetch(`${this.plugin.settings.apiUrl}/v1/sessions/${id}`, {
        headers: this.getAuthHeaders()
      });
      if (res.ok) {
        const data = await res.json();
        this.currentSessionId = data.id;
        this.messageContainer.empty();
        for (const msg of data.messages) {
          const wrap = this.addMessage(msg.content, msg.role);
          if (msg.role === "ai") {
            this.addFeedbackBar(wrap, msg.id);
          } else if (msg.role === "user") {
            this.addEditBar(wrap, msg.content);
          }
          if (msg.role === "assistant") {
            const inner = wrap.querySelector(".sp-message-ai");
            if (inner) {
              inner.empty();
              import_obsidian.MarkdownRenderer.render(this.app, msg.content, inner, "", this.plugin);
            }
            this.addFeedbackBar(wrap, msg.id);
          }
        }
        setTimeout(() => {
          this.messageContainer.scrollTo({ top: this.messageContainer.scrollHeight, behavior: "smooth" });
        }, 50);
      }
    } catch (e) {
      console.error("Erro recarregando historico via Session ID", e);
    }
  }
  async getActiveNoteContext() {
    const activeFile = this.app.workspace.getActiveFile();
    if (activeFile && activeFile.extension === "md") {
      const content = await this.app.vault.read(activeFile);
      return `[DOCUMENTO ATUALMENTE ABERTO E FOCADO NO EDITOR DO USU\xC1RIO:
T\xEDtulo: ${activeFile.basename}
Caminho: ${activeFile.path}
Conte\xFAdo Hist\xF3rico:
${content}
--- FIM DO DOCUMENTO ATUAL ---]

`;
    }
    return "";
  }
  async handleSubmit() {
    var _a;
    const text = this.inputField.value.trim();
    if (!text) return;
    this.inputField.value = "";
    const userWrap = this.addMessage(text, "user");
    this.addEditBar(userWrap, text);
    const wrapperNode = this.addMessage("...", "ai");
    const aiBubble = wrapperNode.querySelector(".sp-message-ai");
    aiBubble.style.opacity = "0.7";
    try {
      const activeContext = await this.getActiveNoteContext();
      const response = await fetch(`${this.plugin.settings.apiUrl}/v1/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...this.getAuthHeaders()
        },
        body: JSON.stringify({
          message: text,
          active_document: activeContext ? activeContext : null,
          stream: true,
          session_id: this.currentSessionId
        })
      });
      if (!response.ok) throw new Error("API Indispon\xEDvel (FastAPI)");
      const reader = (_a = response.body) == null ? void 0 : _a.getReader();
      const decoder = new TextDecoder();
      if (reader) {
        aiBubble.innerHTML = "";
        aiBubble.style.opacity = "1";
        let fullResponse = "";
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split("\n");
          for (const line of lines) {
            if (line.startsWith("data: ")) {
              const dataStr = line.replace("data: ", "").trim();
              if (dataStr === "[DONE]") continue;
              if (dataStr) {
                try {
                  const data = JSON.parse(dataStr);
                  if (data.session_id_established) {
                    this.currentSessionId = data.session_id_established;
                  }
                  if (data.message_id) {
                    this.addFeedbackBar(wrapperNode, data.message_id);
                  }
                  if (data.content) {
                    fullResponse += data.content;
                    aiBubble.empty();
                    import_obsidian.MarkdownRenderer.render(this.app, fullResponse, aiBubble, "", this.plugin);
                    this.messageContainer.scrollTo({ top: this.messageContainer.scrollHeight });
                  }
                } catch (e) {
                  console.error("Parse erro", e, dataStr);
                }
              }
            }
          }
        }
        aiBubble.empty();
        import_obsidian.MarkdownRenderer.render(this.app, fullResponse, aiBubble, "", this.plugin);
      }
    } catch (e) {
      aiBubble.innerHTML = "\u26A0\uFE0F _Erro de conex\xE3o com o Motor FastAPI._";
      console.error("SSE Error:", e);
    }
  }
  async onClose() {
  }
};
var SovereignPairHistoryModal = class extends import_obsidian.SuggestModal {
  constructor(app, view) {
    super(app);
    this.view = view;
    this.setPlaceholder("Buscar chat ou tag...");
  }
  getSuggestions(query) {
    const q = query.toLowerCase();
    const results = this.view.sessionsList.filter((s) => {
      const titleMatch = s.title.toLowerCase().includes(q);
      const tagMatch = (s.tags || []).some((t) => t.toLowerCase().includes(q));
      return titleMatch || tagMatch;
    });
    if (q.length === 0 || "nova conversa".includes(q)) {
      return [{ id: -1, title: "\u2795 Nova Conversa", tags: [] }, ...results];
    }
    return results;
  }
  renderSuggestion(sess, el) {
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
  async onChooseSuggestion(item, evt) {
    if (item.id === -1) {
      this.view.currentSessionId = null;
      this.view.messageContainer.empty();
      if (this.view.spotlightBtn) this.view.spotlightBtn.setText(`\u{1F50D} --- Nova Conversa ---`);
      this.view.addMessage("Nova conversa iniciada. Como posso ajudar?", "ai");
      return;
    }
    if (this.view.spotlightBtn) {
      this.view.spotlightBtn.setText(`\u{1F50D} ${item.title}`);
    }
    await this.view.loadSession(item.id);
  }
};
var SovereignPairPlugin = class extends import_obsidian.Plugin {
  constructor() {
    super(...arguments);
    this.lastSyncTime = Date.now();
  }
  async onload() {
    console.log("Carregando Sovereign Pair RAG Plugin...");
    await this.loadSettings();
    this.registerView(
      VIEW_TYPE_CHAT,
      (leaf) => new SovereignPairView(leaf, this)
    );
    this.addRibbonIcon("bot", "Sovereign Pair Chat", () => {
      this.activateView();
    });
    this.addCommand({
      id: "open-sovereign-pair-chat",
      name: "Abrir Barra Lateral do Sovereign Pair",
      callback: () => {
        this.activateView();
      }
    });
    this.registerEvent(
      this.app.workspace.on("editor-paste", async (evt, editor) => {
        if (evt.clipboardData && evt.clipboardData.files.length > 0) {
          const file = evt.clipboardData.files[0];
          new import_obsidian.Notice(`Sovereign Pair: Recebendo arquivo colado '${file.name}' para o RAG...`);
          await this.uploadFileToAPI(file);
        }
      })
    );
    this.registerInterval(
      window.setInterval(() => this.backgroundSync(), 5 * 60 * 1e3)
    );
  }
  async uploadFileToAPI(file, filename) {
    const formData = new FormData();
    if (filename) {
      formData.append("file", file, filename);
      formData.append("force_overwrite", "true");
    } else {
      formData.append("file", file);
    }
    try {
      const res = await fetch(`${this.settings.apiUrl}/v1/upload`, {
        method: "POST",
        headers: this.settings.authToken ? { "Authorization": `Bearer ${this.settings.authToken}` } : {},
        body: formData
      });
      const data = await res.json();
      if (data.status === "conflict") {
        new import_obsidian.Notice(`Sovereign Pair RAG: Conflito ignorado ao vetorizar ${filename || file.name}.`);
      } else if (res.ok) {
        new import_obsidian.Notice(`Sovereign Pair RAG: '${filename || file.name}' indexado!`);
      }
    } catch (e) {
      console.error("Erro no upload RAG do Obsidian", e);
    }
  }
  async backgroundSync() {
    const now = Date.now();
    const files = this.app.vault.getMarkdownFiles();
    const modifiedFiles = files.filter((f) => f.stat.mtime > this.lastSyncTime);
    this.lastSyncTime = now;
    if (modifiedFiles.length === 0) return;
    for (const file of modifiedFiles) {
      try {
        const content = await this.app.vault.read(file);
        const blob = new Blob([content], { type: "text/markdown" });
        await this.uploadFileToAPI(blob, file.name);
      } catch (e) {
        console.error("Background sync falhou para", file.name, e);
      }
    }
  }
  onunload() {
    console.log("Descarregando Sovereign Pair RAG Plugin...");
  }
  async loadSettings() {
    this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
  }
  async saveSettings() {
    await this.saveData(this.settings);
  }
  async activateView() {
    const { workspace } = this.app;
    let leaf = null;
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
};
var SovereignPairConfigModal = class extends import_obsidian.Modal {
  constructor(app, plugin) {
    super(app);
    this.plugin = plugin;
  }
  async onOpen() {
    const { contentEl } = this;
    contentEl.empty();
    contentEl.createEl("h2", { text: "Sovereign Pair LLM Settings" });
    new import_obsidian.Setting(contentEl).setName("Estilo de Navega\xE7\xE3o do Hist\xF3rico").setDesc("Escolha a fluidez de busca temporal (Mini-Web, Minimalista ou Modal Spotlight).").addDropdown(
      (dropdown) => dropdown.addOption("mini", "Mini-Web UI (Sovereign Pair)").addOption("minimalist", "Filtro Minimalista Gen\xE9rico").addOption("spotlight", "Spotlight (Modal Central Flutuante)").setValue(this.plugin.settings.historyViewMode || "mini").onChange(async (val) => {
        this.plugin.settings.historyViewMode = val;
        await this.plugin.saveSettings();
      })
    );
    new import_obsidian.Setting(contentEl).setName("URL Base da API do Sovereign Pair").setDesc("Insira a URL. Use https://localhost ou a URL p\xFAblica. Com o Caddy, o Node conectar\xE1 via porta HTTPS 443 implicitamente.").addText(
      (text) => text.setPlaceholder("https://localhost").setValue(this.plugin.settings.apiUrl).onChange(async (val) => {
        this.plugin.settings.apiUrl = val.replace(/\/+$/, "");
        await this.plugin.saveSettings();
      })
    );
    new import_obsidian.Setting(contentEl).setName("Token de Acesso (API Key)").setDesc("Cole o Sovereign Token exibido na interface Web (Settings -> API Config).").addText(
      (text) => text.setPlaceholder("ey...").setValue(this.plugin.settings.authToken).onChange(async (val) => {
        this.plugin.settings.authToken = val.trim();
        await this.plugin.saveSettings();
      })
    );
    const loadingMsg = contentEl.createEl("p", { text: "Carregando configura\xE7\xF5es do Backend RAG..." });
    try {
      const res = await fetch(`${this.plugin.settings.apiUrl}/v1/config`, {
        headers: this.plugin.settings.authToken ? { "Authorization": `Bearer ${this.plugin.settings.authToken}` } : {}
      });
      if (res.ok) {
        const settings = await res.json();
        loadingMsg.remove();
        const modelOptionsByProvider = {
          "ollama": {
            "llama3.2": "Llama 3.2 (Local)",
            "llama3": "Llama 3 (Local)",
            "mistral": "Mistral (Local)",
            "gemma2": "Gemma 2 (Local)",
            "phi3": "Phi-3 (Local)",
            "qwen2.5": "Qwen 2.5 (Local)",
            "bge-m3": "BGE-M3 (Ollama)"
          },
          "openai": {
            "gpt-4o": "GPT-4o",
            "gpt-4o-mini": "GPT-4o Mini",
            "gpt-4-turbo": "GPT-4 Turbo",
            "gpt-3.5-turbo": "GPT-3.5 Turbo"
          },
          "anthropic": {
            "claude-3-5-sonnet-latest": "Claude 3.5 Sonnet",
            "claude-3-opus-latest": "Claude 3 Opus",
            "claude-3-haiku-20240307": "Claude 3 Haiku"
          },
          "groq": {
            "llama-3.1-70b-versatile": "Llama 3.1 70B",
            "llama-3.1-8b-instant": "Llama 3.1 8B",
            "mixtral-8x7b-32768": "Mixtral 8x7B",
            "gemma2-9b-it": "Gemma 2 9B"
          },
          "gemini": {
            "gemini-1.5-pro-latest": "Gemini 1.5 Pro",
            "gemini-1.5-flash-latest": "Gemini 1.5 Flash",
            "gemini-pro": "Gemini Pro"
          }
        };
        let modelDropdownComponent;
        let customModelTextComponent;
        const updateModelDropdown = async (provider) => {
          if (!modelDropdownComponent) return;
          modelDropdownComponent.selectEl.innerHTML = "";
          modelDropdownComponent.selectEl.disabled = true;
          if (provider === "ollama") {
            try {
              const res2 = await fetch("http://127.0.0.1:11434/api/tags");
              if (res2.ok) {
                const data = await res2.json();
                const dynamicOptions = {};
                if (data.models && data.models.length > 0) {
                  data.models.forEach((m) => {
                    dynamicOptions[m.name] = m.name + " (Local)";
                  });
                  modelOptionsByProvider["ollama"] = dynamicOptions;
                }
              }
            } catch (e) {
              console.warn("SovereignPair: Failed to fetch Ollama models natively, falling back to cached list.", e);
            }
          }
          modelDropdownComponent.selectEl.disabled = false;
          const options = modelOptionsByProvider[provider] || modelOptionsByProvider["ollama"];
          for (const [key, value] of Object.entries(options)) {
            modelDropdownComponent.addOption(key, value);
          }
          modelDropdownComponent.addOption("custom", "Outro (Personalizado)");
          const currentModel = settings.llm_model;
          if (Object.keys(options).includes(currentModel)) {
            modelDropdownComponent.setValue(currentModel);
            if (customModelTextComponent) customModelTextComponent.inputEl.parentElement.parentElement.style.display = "none";
          } else if (currentModel) {
            modelDropdownComponent.setValue("custom");
            if (customModelTextComponent) {
              customModelTextComponent.setValue(currentModel);
              customModelTextComponent.inputEl.parentElement.parentElement.style.display = "flex";
            }
          } else {
            const firstOption = Object.keys(options)[0];
            if (firstOption) {
              modelDropdownComponent.setValue(firstOption);
              settings.llm_model = firstOption;
              if (customModelTextComponent) customModelTextComponent.inputEl.parentElement.parentElement.style.display = "none";
            } else {
              modelDropdownComponent.setValue("custom");
            }
          }
        };
        new import_obsidian.Setting(contentEl).setName("Provedor LLM").setDesc("Selecione o motor de infer\xEAncia (Local ou Cloud)").addDropdown(
          (dropdown) => dropdown.addOption("ollama", "Ollama (Local)").addOption("openai", "OpenAI").addOption("anthropic", "Anthropic").addOption("groq", "Groq").addOption("gemini", "Google Gemini").setValue(settings.llm_provider || "ollama").onChange(async (val) => {
            settings.llm_provider = val;
            updateModelDropdown(val);
          })
        );
        new import_obsidian.Setting(contentEl).setName("Nome do Modelo").setDesc("Selecione um modelo da lista sugerida pelo provedor ou escolha Personalizado.").addDropdown((dropdown) => {
          modelDropdownComponent = dropdown;
          dropdown.onChange(async (val) => {
            if (val === "custom") {
              if (customModelTextComponent) {
                customModelTextComponent.inputEl.parentElement.parentElement.style.display = "flex";
                settings.llm_model = customModelTextComponent.getValue();
              }
            } else {
              if (customModelTextComponent) customModelTextComponent.inputEl.parentElement.parentElement.style.display = "none";
              settings.llm_model = val;
            }
          });
        });
        const customModelSetting = new import_obsidian.Setting(contentEl).setName("Modelo Personalizado").setDesc("Digite o ID/Tag exata do modelo (ex: my-custom-model:latest)").addText((text) => {
          customModelTextComponent = text;
          text.setValue(settings.llm_model).onChange(async (val) => {
            if (modelDropdownComponent.getValue() === "custom") {
              settings.llm_model = val.trim();
            }
          });
        });
        customModelSetting.settingEl.style.display = "none";
        await updateModelDropdown(settings.llm_provider || "ollama");
        new import_obsidian.Setting(contentEl).setName("Temperatura (Criatividade)").setDesc("Valores pr\xF3ximos de 0.0 geram respostas mais anal\xEDticas e exatas. Valores altos aumentam a criatividade.").addSlider(
          (slider) => slider.setLimits(0, 2, 0.1).setValue(settings.temperature || 0.1).setDynamicTooltip().onChange(async (val) => {
            settings.temperature = val;
          })
        );
        const personaOptions = [
          { id: "default", name: "Assistente Padr\xE3o (Default)", prompt: "Foco em respostas anal\xEDticas, pragm\xE1ticas e diretas. Traga conhecimento fundamentado sem enrola\xE7\xE3o." },
          { id: "developer", name: "Desenvolvedor S\xEAnior", prompt: "Aja como um Arquiteto de Software s\xEAnior. Foco em c\xF3digo limpo (Clean Code), design patterns, otimiza\xE7\xE3o de performance e explica\xE7\xF5es t\xE9cnicas concisas e precisas." },
          { id: "marketing", name: "Mestre do Marketing", prompt: "Voc\xEA \xE9 um especialista em Marketing Digital. Use copywriting persuasivo focado em convers\xE3o, m\xE9tricas, SEO e lan\xE7amento de produtos. Adote um tom empolgante." },
          { id: "admin", name: "Gestor & Admin", prompt: "Aja como um administrador de empresas e gerente de projetos s\xEAnior. Foco em organiza\xE7\xE3o corporativa, planilhas estruturadas, relat\xF3rios processuais e finan\xE7as limpas." },
          { id: "professor", name: "Professor Acad\xEAmico", prompt: "Voc\xEA \xE9 um mentor acad\xEAmico compassivo e sagaz. Explique conceitos complexos com met\xE1foras did\xE1ticas, passo a passo, fomentando o racioc\xEDnio sem dar apenas a resposta pronta imediata." },
          { id: "career", name: "Mentor de Carreira", prompt: "Voc\xEA \xE9 um Headhunter experiente. Foco na evolu\xE7\xE3o profissional do usu\xE1rio, melhoria de propostas de valor (curr\xEDculos e portf\xF3lios) e dicas cir\xFArgicas de networking e entrevistas." },
          { id: "productivity", name: "Hacker de Rendimento", prompt: "Comporte-se como um executor fan\xE1tico por otimiza\xE7\xE3o de tempo. Foco r\xEDgido na gera\xE7\xE3o de checklists diretos, m\xE9todos \xE1geis (Kanban/Scrum) e atalhos de produtividade extrema." },
          { id: "creative", name: "Brainstormer Criativo", prompt: "Seja extremamente imaginativo e fora-da-caixa. Seu objetivo \xE9 ajudar a encontrar solu\xE7\xF5es inovadoras para problemas normais, usando um tom entusiasmado e proativo. Proponha cen\xE1rios alternativos abundantes." }
        ];
        let promptTextArea;
        let personaDropdownComponent;
        new import_obsidian.Setting(contentEl).setName("Comportamento da IA (Persona)").setDesc("Escolha a especialidade ou selecione Personalizado e altere o campo abaixo manualmente.").addDropdown((dropdown) => {
          personaDropdownComponent = dropdown;
          for (const p of personaOptions) dropdown.addOption(p.id, p.name);
          dropdown.addOption("custom", "Personalizado");
          dropdown.setValue(settings.persona || "default");
          dropdown.onChange(async (val) => {
            settings.persona = val;
            if (val !== "custom") {
              const selected = personaOptions.find((p) => p.id === val);
              if (selected) {
                settings.system_prompt = selected.prompt;
                if (promptTextArea) promptTextArea.setValue(selected.prompt);
              }
            }
          });
        });
        new import_obsidian.Setting(contentEl).setName("Instru\xE7\xE3o Base (System Prompt)").addTextArea((text) => {
          promptTextArea = text;
          text.setValue(settings.system_prompt).onChange(async (val) => {
            settings.system_prompt = val;
            settings.persona = "custom";
            if (personaDropdownComponent) personaDropdownComponent.setValue("custom");
          });
          text.inputEl.style.minHeight = "100px";
          text.inputEl.style.width = "100%";
        });
        new import_obsidian.Setting(contentEl).setName("Tratamento e Formalidade").setDesc("For\xE7a a IA a tratar a si mesma no g\xEAnero desejado.").addDropdown(
          (dropdown) => dropdown.addOption("feminine", "Assistente \u2640\uFE0F").addOption("neutral", "Neutro \u{1F916}").addOption("masculine", "Assistente \u2642\uFE0F").setValue(settings.formality || "neutral").onChange(async (val) => {
            settings.formality = val;
          })
        );
        contentEl.createEl("h3", { text: "Sobre Voc\xEA (Contexto de Mem\xF3ria)", cls: "sp-settings-section-title" });
        new import_obsidian.Setting(contentEl).setName("Como a IA deve te chamar?").setDesc("Seu nome ou apelido informal (Nickname).").addText(
          (text) => text.setPlaceholder("Ex: Mestre Jedi").setValue(settings.nickname || "").onChange(async (val) => {
            settings.nickname = val.trim();
          })
        );
        new import_obsidian.Setting(contentEl).setName("Ocupa\xE7\xE3o / Atua\xE7\xE3o").setDesc('Sua profiss\xE3o principal (Ex: "Designer de Interiores").').addText(
          (text) => text.setPlaceholder("Ex: Dev Backend Pleno").setValue(settings.occupation || "").onChange(async (val) => {
            settings.occupation = val.trim();
          })
        );
        new import_obsidian.Setting(contentEl).setName("Mais sobre voc\xEA").setDesc("Interesses, regras pessoais ou prefer\xEAncias que a IA deve lembrar.").addTextArea((text) => {
          text.setPlaceholder("Gosto de explica\xE7\xF5es curtas em bullet points...");
          text.setValue(settings.about_user || "").onChange(async (val) => {
            settings.about_user = val;
          });
          text.inputEl.style.minHeight = "80px";
          text.inputEl.style.width = "100%";
        });
        new import_obsidian.Setting(contentEl).setName("Idioma & Localiza\xE7\xE3o Escrita").setDesc("Defina o sotaque ou idioma base do assistente.").addDropdown(
          (dropdown) => dropdown.addOption("Portugu\xEAs do Brasil", "Portugu\xEAs do Brasil").addOption("Portugu\xEAs (Carioca)", "\u{1F1E7}\u{1F1F7} Portugu\xEAs (Carioca)").addOption("Portugu\xEAs (Paulistano)", "\u{1F1E7}\u{1F1F7} Portugu\xEAs (Paulistano)").addOption("Portugu\xEAs (Mineiro)", "\u{1F1E7}\u{1F1F7} Portugu\xEAs (Mineiro)").addOption("Portugu\xEAs (Nordestino)", "\u{1F1E7}\u{1F1F7} Portugu\xEAs (Nordestino)").addOption("Portugu\xEAs de Portugal", "\u{1F1F5}\u{1F1F9} Portugu\xEAs de Portugal").addOption("Ingl\xEAs (EUA)", "\u{1F1FA}\u{1F1F8} Ingl\xEAs Americano").addOption("Espanhol", "\u{1F1EA}\u{1F1F8} Espanhol").setValue(settings.language || "Portugu\xEAs do Brasil").onChange(async (val) => {
            settings.language = val;
          })
        );
        new import_obsidian.Setting(contentEl).setName("Geolocaliza\xE7\xE3o / Base de Opera\xE7\xF5es").setDesc("Sua cidade/pa\xEDs. Ajuda a IA a contextualizar clima, regi\xF5es e RAG.").addText(
          (text) => text.setPlaceholder("Ex: S\xE3o Paulo, Brasil").setValue(settings.geolocation || "").onChange(async (val) => {
            settings.geolocation = val.trim();
          })
        );
        contentEl.createEl("br");
        new import_obsidian.Setting(contentEl).addButton((btn) => btn.setButtonText("Salvar no Servidor").setCta().onClick(async () => {
          btn.setButtonText("Salvando...");
          const putRes = await fetch(`${this.plugin.settings.apiUrl}/v1/config`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              ...this.plugin.settings.authToken ? { "Authorization": `Bearer ${this.plugin.settings.authToken}` } : {}
            },
            body: JSON.stringify(settings)
          });
          if (putRes.ok) {
            new import_obsidian.Notice("Configura\xE7\xF5es do LLM salvas no backend!");
            this.close();
          } else {
            new import_obsidian.Notice("Erro ao salvar as configura\xE7\xF5es.");
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
};
