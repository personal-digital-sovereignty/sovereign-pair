# Universal Installation Guide (Sovereign Pair v0.8.0+)

**Sovereign Pair** leverages a hybrid architecture designed for both **Graphical Desktop** interfaces (Thin-Client) and **Cloud Servers** (Headless Daemons). Below are the official deployment instructions covering both operational scenarios.

---

## Scenario 1: Ubuntu / Linux Desktop (Graphical Installation)

Designed for local virtual machines, laptops, and workstations. This method utilizes the Universal Packager (Tauri) to deliver the Dashboard UI, the Native Daemon, and the Shell Extensions (Plasmoids) in a single unified sweep.

### Step-by-Step

1. **Download the Installer**:
   Navigate to the [GitHub Releases](https://github.com/Personal-Digital-Sovereignty/sovereign-pair/releases/latest) page and download the corresponding Debian bundle (e.g., `Sovereign_Pair_0.8.0_amd64.deb`).

2. **OS Package Installation**:
   Open a terminal and trigger the package manager:
   ```bash
   sudo dpkg -i Sovereign_Pair_0.8.0_amd64.deb
   sudo apt-get install -f # (Only needed if Ubuntu requests dependencies like libwebkit2gtk)
   ```
   *(Alternatively: Double-click the `.deb` file to install it graphically via Gnome Software or Discover).*

3. **First-Run Wizard**:
   - Launch "Sovereign Pair" from your Ubuntu App Launcher.
   - The desktop app will execute a *cold boot*, detect that the backend daemon is missing on port `38001`, and invoke the visual **First-Run Wizard**.
   - Follow the steps sequentially. During the "System Integration" slice, a native privilege escalation popup (Polkit/pkexec) will appear. Enter your system password to authorize the background Daemon embedding.

4. **KDE / Gnome Extensions**:
   Once the daemon is safely registered under ROOT space (Systemd), the Wizard gracefully returns to standard user privileges and quietly copies the Plasmoids to your Shell without leaking superuser paths.
   - Optional Check: Read the generated `~/Desktop/Sovereign_Install.log` file to verify the successful SysTray and Widget deployments.

---

## Scenario 2: Oracle Cloud OCI A1 (Headless Server Installation)

Designed for ARM64 / Ampere A1 processors running inside scalable cloud architectures. This environment requires no Svelte GUI. We operate strictly around the compiled "Fat-Daemon" Rust binary.

### Step-by-Step (Manual CLI)

1. **Tunnel into the Machine & Binary Fetch**:
   SSH into your Oracle Ubuntu box:
   ```bash
   ssh ubuntu@your-oracle-ip
   ```

2. **Curl the Stable Release**:
   Since the server is headless, utilize `wget` or `curl` to capture the native executable explicitly compiled by the `publish-stable` continuous integration pipeline:
   ```bash
   # Via wget
   wget https://github.com/Personal-Digital-Sovereignty/sovereign-pair/releases/download/0.8.0/sovereign-core-linux-arm64-binary -O sovereign-core
   
   # Or via curl
   curl -L https://github.com/Personal-Digital-Sovereignty/sovereign-pair/releases/download/0.8.0/sovereign-core-linux-arm64-binary -o sovereign-core
   ```
   *(Replace `0.8.0` with the current target tag if tracking a newer release).*

3. **Daemon Injection**:
   Grant execution rights and execute the architecture's native `--setup` privilege escalation flag. Because we are in CLI, invoke it alongside pure `sudo`:
   ```bash
   chmod +x sovereign-core
   sudo ./sovereign-core --setup
   ```
   > 💡 **Technical Note**: The Rust Core will dynamically detect real absolute `ROOT` access (UID 0), generating the OS `Systemd` service blueprints explicitly bypassing the GUI.

4. **State Validation**:
   Assert that the Cibrid Node woke up properly, enforcing SQLite KMS encryptions and listening via the OpenCode Networking protocol:
   ```bash
   systemctl status sovereign.service
   ```
   Your remote OCI Node is currently active and awaiting Tailscale peer-mesh communication on `38001`.

---

## Architectural Breakdown

By mechanically separating the packaged **Frontend Bundle** (`.deb / .dmg / .msi`) from the bare-metal **Backend Runtime** (`binary_core_arm64`), we guarantee cloud environments rely on hardcore zero-trust mechanics while local consumers enjoy polished UX interfaces without jeopardizing strict superuser authorization bounds.
