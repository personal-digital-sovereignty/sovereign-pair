# Universal Installation Architecture: Thin-Client & Fat-Daemon

As Sovereign Pair transitions towards a multi-platform ecosystem (MacOS, Windows, Linux), the project has deprecated isolated binaries and inefficient wrappers in favor of a **Dual Cibrid Architecture** powered by Tauri v2 and Rust.

The greatest technical challenge in deploying environments that act as *System Services (Daemons)* and *Desktop Interfaces (Systray)* simultaneously is Root Permission boundary confinement. If the Daemon controlling the SQLite database (Sensus Vault) ran under restricted Local Desktop User permissions, it could not boot with the OS or act as an isolated Node. Conversely, if the Desktop Interface attempted to directly read a root-owned SQLite database, it would crash via `Permission Denied` exceptions.

To elegantly solve this persistent Operating System dichotomy without affecting user fluidity, Sovereign Pair adopts the **"Thin-Client / Fat-Daemon"** paradigm.

## 1. Physical and Logical Decoupling (API First)
The Core Rust Engine (`sovereign-core`) runs natively as the **Fat-Daemon** (The Brain). Whether installed on an Oracle Cloud A1 node or a Local MacOS Desktop, the Svelte graphical interface communicates with the Engine through pure Asynchronous HTTP Rest API calls (`127.0.0.1:38001`).

This fundamental rule physically assigns the SQLite database and sensitive local file structures directly to the System Daemon. The Tauri app (Systray) never reads the Database SQLite binary itself, guaranteeing a Zero-Trust permission isolation at the OS FileSystem level.

## 2. The Smart Umbilical Cord (Adaptive Boot)
Unlike Heavy-VM implementations (like Docker Desktop), our Desktop UI Installer (Tauri) operates with smart adaptive routines during boot:

1. **Coupling Attempt:** Upon application launch, the Frontend refuses to blindly fire its own sidecar server. It first issues a fast *Health Ping* to the system port (`127.0.0.1:38001`).
2. **Thin-Client Mode:** If the native OS Daemon (Systemd / Launchd / WinSvc) actively responds to the ping, the Desktop App engages "Thin-Client" Mode. It intentionally *sleeps* its Sidecar binary. The UI seamlessly attaches to the running Daemon, acting strictly as a beautiful, high-performance remote control panel and Systray.
3. **Fat-Client Mode (Fallback):** Should a user run the app as *Portable* (without providing Root passwords or installing OS Daemons), the port ping will naturally timeout. To ensure zero-friction, Tauri instantly spawns its packaged Rust Binary (Sidecar) confined to the *Local User Context*. The App runs flawlessly isolated until closed.

## 3. Systray Privileged Workflows
Sovereign Pair respects the Principle of Least Privilege. If the user clicks "Install Background Service" or "Restart Engine" through the User Interface, the Sandboxed Svelte UI visually delegates the command to the Rust Sidecar invoking the `--setup` flag.

The Rust Sidecar harbors its self-aware escalation routing:
- It detects current execution UID (Unprivileged User Boundary).
- Spawns the official OS visual password prompt mechanism (`pkexec` for Linux X11/Wayland, `osascript` with *administrator privileges* for Mac, and UAC elevation for Windows).
- It registers the Daemon services, detects required Local LLMs (Ollama), bridges the global Desktop Extensions (Gnome/KDE Plasmoids), and seamlessly pipes a human-readable stream back to the UI's `stdout` terminal component.

This orchestrated logic grants Sovereign Pair the raw computational velocity of an Oracle OCI Headless Server while maintaining the magical "One-Click" convenience of a unified, native Desktop application — executing on the precise same Rust kernel.
