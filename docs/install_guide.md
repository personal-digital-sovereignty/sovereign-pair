# Sovereign Pair: Installation & Orchestration Guide

This document formally describes the bare-metal installation procedures for the Sovereign Pair Cibrid Node natively across environments. There is no reliance on Standalone Binary, Hypervisors, or Rust distributions.

## Abstract

The architecture uses a statically compiled Rust daemon (`sovereign-core`) and an embedded SvelteKit frontend server mechanism.

## Standard Installation (Pre-compiled Binaries)

### Linux (Debian, Arch, RHEL)

1. Navigate to the GitHub Releases page and download the `sovereign-core-linux-amd64` (or `arm64` for Ampere/Raspberry) ELF executable.
2. Grant executing privileges:
```bash
chmod +x sovereign-core
sudo mv sovereign-core /usr/local/bin/
```
3. Install the Systemd Daemon:
```bash
sudo curl -o /etc/systemd/system/sovereign.service https://raw.githubusercontent.com/Personal-Digital-Sovereignty/sovereign-pair/main/scripts/sovereign.service
sudo systemctl daemon-reload
sudo systemctl enable --now sovereign
```

### Windows (Native & WSL2)

1. Download the `sovereign-core.exe` executable file from the Releases tab.
2. In PowerShell, create an explicit directory:
```powershell
New-Item -ItemType Directory -Force -Path C:\SovereignPair
Move-Item .\sovereign-core.exe C:\SovereignPair\
```
3. Establish the executable as a Windows Service or execute it directly:
```powershell
./sovereign-core.exe --host 127.0.0.1
```

### macOS (Graphical Desktop .DMG Install)

1. Download the `SovereignPair_0.9.x_aarch64.dmg` from the Releases tab.
2. Open the DMG and drag **Sovereign Pair.app** into your `/Applications` folder.
3. Because the open-source bundle is intentionally NOT code-signed via the paid Apple Developer M1 program, macOS Gatekeeper will forcefully flag the `.app` as "Damaged or compromised by malware".
4. To remove the arbitrary Quarantine Attribute, open your Terminal and execute:
```bash
sudo xattr -cr "/Applications/Sovereign Pair.app"
```
5. You can now launch the Sovereign Pair icon directly from your Launchpad!

---

### macOS (Headless Binary Mode)

1. Download the `sovereign-core-macos-arm64-binary`.
2. Authenticate the execution through Gatekeeper exceptions:
```bash
chmod +x sovereign-core-macos-arm64-binary
xattr -d com.apple.quarantine sovereign-core-macos-arm64-binary
./sovereign-core-macos-arm64-binary
```

---

## Compiling from Source (Cargo Toolchain)

If you strictly require compilation telemetry or a fully native host architecture optimization, follow the `cargo` build sequence.

1. Install the Rust compiler and the Node.js package manager:
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
sudo apt-get install -y nodejs npm
```
2. Proceed to clone the codebase:
```bash
git clone https://github.com/Personal-Digital-Sovereignty/sovereign-pair.git
cd sovereign-pair
```
3. Construct the Svelte Frontend interface:
```bash
cd svelte-ui
npm install
npm run build
cd ..
```
4. Perform the isolated Release Build (which will permanently embed the `svelte-ui/build/` directory via `include_dir!` macro payload):
```bash
cd core
cargo build --release
```
5. Execute the freshly forged binary:
```bash
./target/release/sovereign-core
```
