# Sovereign Pair - Desktop Application

Este é o cliente Desktop nativo e multiplataforma do **Sovereign Pair**, construído com **Tauri**, **Vue 3** e **Rust**. Ele atua como um widget "Spotlight" invisível no System Tray do seu Sistema Operacional, oferecendo acesso instantâneo aos Agentes Cíbridos através da sua bandeja do sistema.

## 🛠️ Como Compilar Nativamente (Para Hackers & Devs Avançados)

Se você não quer confiar nos binários pré-compilados do GitHub Releases e prefere gerar o seu próprio instalador super otimizado na sua máquina, siga os passos abaixo.

### 1. Pré-requisitosGlobais
Você precisará ter instalado na sua máquina:
1. [Node.js](https://nodejs.org/) (v20+)
2. [Rust / Cargo](https://rustup.rs/) (Stable)

### 2. Dependências do Sistema Operacional

#### 🐧 Linux (Debian / Ubuntu)
O Tauri exige que bibliotecas nativas como o WebKit e o GTK estejam presentes para embutir o motor do navegador na janela transparente.
```bash
sudo apt-get update
sudo apt-get install -y libwebkit2gtk-4.1-dev \
    build-essential \
    curl \
    wget \
    file \
    libxdo-dev \
    libssl-dev \
    libayatana-appindicator3-dev \
    librsvg2-dev
```

#### 🍎 MacOS
Requer apenas a build chain da Apple. Instale via terminal:
```bash
xcode-select --install
```

#### 🪟 Windows
Baixe e instale a [C++ Build Tools do Visual Studio](https://visualstudio.microsoft.com/visual-cpp-build-tools/). Mantenha marcado as opções de `Desenvolvimento para Desktop com C++` e os SDKs do Windows 10/11.

---

### 3. Instalando Pacotes Frontend
Entre na pasta do projeto desktop e instale as dependências Vue:
```bash
cd desktop
npm install
```

### 4. Rodando em Modo Desenvolvedor (Hot-Reload)
Se quiser testar ou modificar a UI do pop-up do relógio visualmente:
```bash
npm run tauri dev
```
*(Um ícone de 🧠 aparecerá no seu relógio/tray!)*

### 5. Compilando o Embalamento Final (Build Release)
Para gerar executáveis prontos para instalação (ex: `.deb`, `.AppImage`, `.msi`, `.dmg`):
```bash
npm run tauri build
```
O framework passará os parâmetros otimizados definidos no `src-tauri/Cargo.toml` (`opt-level = "z"`, `lto = true`). Quando terminado, os instaladores nativos estrão disponíveis na pasta:
`desktop/src-tauri/target/release/bundle/`

> **⚠️ Atenção:** O Desktop App não carrega modelos LLM pesado por padrão para preservar o instalador enxuto (< 10MB). O App se comunicará via HTTP na porta local com o Motor Principal do `Sovereign Pair`. Certifique-se de startar o `sovereign-core` localmente ou no Docker!
