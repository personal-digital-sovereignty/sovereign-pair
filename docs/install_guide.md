# 🚀 Guia de Instalação e Orquestração (v1.3.2)

Este guia descreve os procedimentos de instalação bare-metal para o Nó Sovereign Pair. Nosso sistema é independente e não requer containers ou hypervisors para operar em sua performance máxima.

---

## 1. Instalação Padrão (Binários Pré-compilados)

### 🐧 Linux (Debian, Arch, RHEL)
1. Baixe o executável `sovereign-core` para sua arquitetura (x86_64 ou aarch64).
2. Conceda permissões de execução:
   ```bash
   chmod +x sovereign-core
   sudo mv sovereign-core /usr/local/bin/
   ```
3. Instale o serviço via Systemd para persistência:
   ```bash
   sudo systemctl enable --now sovereign
   ```

### 🪟 Windows (Nativo & WSL2)
1. Baixe o `sovereign-core.exe`.
2. Crie um diretório dedicado (ex: `C:\SovereignPair`).
3. Execute via PowerShell ou configure como um serviço do Windows:
   ```powershell
   .\sovereign-core.exe --host 127.0.0.1
   ```

### 🍎 macOS (Apple Silicon / Intel)
Devido ao rigor do Gatekeeper da Apple com softwares open-source não assinados, siga estes passos:
1. Mova o **Sovereign Pair.app** para a pasta `/Applications`.
2. Abra o Terminal e remova o atributo de quarentena:
   ```bash
   sudo xattr -cr "/Applications/Sovereign Pair.app"
   ```
3. Lance o aplicativo diretamente pelo Launchpad.

---

## 🛠️ Compilação via Source (Cargo Toolchain)

Para usuários que exigem telemetria de compilação ou otimizações específicas de arquitetura (LTO/Native).

1. **Requisitos**: Rust (Toolchain 1.80+) e Node.js (v20+).
2. **Clone o Repositório**:
   ```bash
   git clone https://github.com/Personal-Digital-Sovereignty/sovereign-pair.git
   cd sovereign-pair
   ```
3. **Build do Frontend (Svelte 5)**:
   ```bash
   cd svelte-ui && npm install && npm run build && cd ..
   ```
4. **Build do Core (Rust)**:
   O binário resultante embutirá automaticamente o frontend compilado.
   ```bash
   cd core && cargo build --release
   ```
5. **Execução**:
   O binário estará localizado em `core/target/release/sovereign-core`.

---

## 🛡️ Verificação de Saúde
Após iniciar, acesse `http://localhost:38001` (ou a porta configurada). O sistema realizará o **Resilience Shield Check** inicial para validar a conectividade com o Ollama e provedores de nuvem.
