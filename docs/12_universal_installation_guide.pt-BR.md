# Guia de Instalação Universal (Sovereign Pair v0.8.0+)

O **Sovereign Pair** possui uma arquitetura híbrida projetada tanto para interfaces **Desktop Gráficas** (Thin-Client) quanto para **Servidores em Nuvem** (Headless Daemons). Abaixo, documentamos as instruções oficiais de instalação para os dois cenários principais de implantação.

---

## Cenário 1: Ubuntu / Linux Desktop (Instalação Gráfica)

Ideal para máquinas virtuais locais, notebooks e estações de trabalho. Esta modalidade utiliza o Empacotador Universal (Tauri) para entregar a Dashboard UI, o Daemon nativo e as Extensões de Shell (Plasmoids) em um único passo.

### Passo a Passo

1. **Download do Instalador**:
   Acesse a página de [Releases do GitHub](https://github.com/Personal-Digital-Sovereignty/sovereign-pair/releases/tag/0.8.0) e baixe o arquivo Debian correspondente (ex: `Sovereign_Pair_0.8.0_amd64.deb`).

2. **Instalação no Sistema Operacional**:
   Abra seu terminal e execute o gerenciador de pacotes:
   ```bash
   sudo dpkg -i Sovereign_Pair_0.8.0_amd64.deb
   sudo apt-get install -f # (Apenas se o Ubuntu pedir dependências como libwebkit2gtk)
   ```
   *(Alternativamente: Dê dois cliques no `.deb` para instalar via Gnome Software / Discover).*

3. **Gatilho Inicial (Setup Wizard)**:
   - Abra o "Sovereign Pair" menu de aplicativos do seu Desktop Ubuntu.
   - O aplicativo fará um *cold boot* e interceptará a falta do Backend na porta `38001`, guiando você visualmente pelo **First-Run Wizard**.
   - Siga as instruções até o passo de "Integrar Serviços de Sistema". Uma janela nativa (Polkit/pkexec) de superusuário abrirá. Digite sua senha de usuário para permitir a integração escalonada do Daemon.

4. **KDE / Gnome Extensions**:
   Após o daemon ser injetado com privilégios de ROOT (Systemd), o Wizard devolverá o poder para sua "sessão de usuário livre" e injetará silenciosamente o Plasmoid/Widgets na engrenagem do seu Desktop sem vazar permissões do root.
   - Opcional: Verifique o arquivo `~/Desktop/Sovereign_Install.log` para o resultado da integração da barra de tarefas!

---

## Cenário 2: Oracle Cloud OCI A1 (Instalação Headless / Servidor)

Ideal para processadores ARM64/Ampere A1 na Nuvem. Neste cenário, não há Desktop (GUI) nem Svelte. Trabalharemos apenas com o "Fat-Daemon" puramente compilado em Rust.

### Passo a Passo (Manual CLI)

1. **Acessando a Máquina e Baixando o Binário**:
   Conecte-se via SSH na sua máquina Ubuntu (Oracle A1):
   ```bash
   ssh ubuntu@seu-ip-oracle
   ```

2. **Capturar a Release**:
   Como a instância não tem GUI, usaremos o `wget` ou `curl` para capturar a release compilada pela própria esteira `publish-stable`:
   ```bash
   # Via wget
   wget https://github.com/Personal-Digital-Sovereignty/sovereign-pair/releases/download/0.8.0/sovereign-core-linux-arm64-binary -O sovereign-core
   
   # Ou via curl
   curl -L https://github.com/Personal-Digital-Sovereignty/sovereign-pair/releases/download/0.8.0/sovereign-core-linux-arm64-binary -o sovereign-core
   ```
   *(Substitua `0.8.0` pela tag atual caso lance versões novas).*

3. **Injeção do Daemon**:
   Dê permissão de execução e utilize a flag `--setup` do nosso sistema de `Privilege Escalation`. Como estamos via CLI, usaremos o `sudo` puro:
   ```bash
   chmod +x sovereign-core
   sudo ./sovereign-core --setup
   ```
   > 💡 **Nota**: O sistema rastreará que você executou via Root e criará instintivamente o manifesto de serviço do `Systemd` sem necessidade do painel Tauri.

4. **Validação**:
   Confirme se o Backend Cíbrido acordou, injetou as defesas SQLite KMS e conectou via OpenCode Network:
   ```bash
   systemctl status sovereign.service
   ```
   Seu nó na OCI está ativo e pronto para pareamento via Tailscale na porta `38001`.

---

## Conclusão de Arquitetura

Ao separar o **Frontend** empacotado (`.deb / .dmg / .msi`) do **Backend Puro** (`binary_core_arm64`), garantimos que a nuvem execute algoritmos extremamente minimalistas de zero-trust, enquanto a experiência local do usuário entrega todo o ecossistema Desktop sem comprometer a Segurança de Superusuários.
