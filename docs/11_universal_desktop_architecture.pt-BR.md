# Arquitetura de Instalação Universal: Thin-Client & Fat-Daemon

Com a evolução do Sovereign Pair para um ecossistema multiplataforma (MacOS, Windows, Linux), o projeto abandonou os binários isolados e wrappers ineficientes em prol de uma **Arquitetura Cíbrida Dual** usando Tauri v2 e Rust.

O maior desafio técnico na implantação de ferramentas que atuam como *Serviços de Sistema (Daemons)* e *Interfaces Desktop (Systray)* é o confinamento da Permissão de Root. Se o Daemon que controla a base de dados SQLite (Sensus Vault) rodasse sob a restrição do usuário Desktop local, ele não poderia se inicializar com o sistema ou atuar como servidor Headless. Se a Interface Desktop (UI) tentasse ler um banco de dados gerado por `root`, ela receberia `Permission Denied`.

Para solucionar essa dicotomia sistêmica sem comprometer a facilidade de uso, o Sovereign Pair adota o modelo **"Thin-Client / Fat-Daemon"**.

## 1. O Desacoplamento Físico e Lógico (API First)
O Motor Rust (`sovereign-core`) executa nativamente como o **Fat-Daemon** (O Cérebro). Sendo instalado em Headless Nuvem (Nó A1) ou no Desktop do Usuário, a única forma de comunicação da interface gráfica com ele é via chamadas HTTP RestFul assíncronas puras (`127.0.0.1:38001`). 

Isso significa que o banco de dados e os arquivos locais sensíveis pertencem física e legalmente ao Daemon (Sistema). O Svelte/Tauri (Systray) nunca precisa ler o arquivo SQLite, garantindo isolamento zero-trust de permissões no FileSystem.

## 2. O Cordão Umbilical Inteligente (Comportamento Adaptativo)
Diferente do Docker Desktop que força VMs pesadas, o nosso Instalador Desktop (Tauri) atua com comportamento adaptativo durante o boot:

1. **Tentativa de Engate:** Quando o aplicativo Sovereign Pair é aberto, o Frontend não atira o seu próprio servidor às cegas. Ele primeiramente dispara um *Ping* na porta de sistema (`127.0.0.1:38001`).
2. **Modo Thin-Client:** Se o Daemon do SO (Systemd / Launchd / WinSvc) responder ao ping, o Aplicativo Desktop entra no modo "Thin-Client". Ele intencionalmente *não desperta* seu executável Sidecar. Ele se acopla ao Daemon existente, transformando-se apenas num controle remoto (Painel e Systray) lindo e responsivo para o cérebro que já estava vivo.
3. **Modo Fat-Client (Fallback/Autônomo):** Caso um usuário decida rodar o App em formato *Portátil* (sem registrar Daemon no SO, sem dar senha de `root`), o ping da porta falhará. Imediatamente, o Tauri invoca seu próprio Binário Rust encapsulado (Sidecar) como *Usuário Local*. Assim a interface não quebra e roda localmente isolada até que o app seja fechado.

## 3. Ações Privilegiadas Guiadas pelo Systray
O Sovereign Pair não assume o controle root indevidamente. Quando o usuário clica na Interface para "Instalar Background Service" ou "Reiniciar Engine", a Interface Visual (Svelte v5), consciente de que não possui privilégios de alto-nível, invoca o Sidecar nativo do Rust injetando a flag `--setup`. 

O Rust Sidecar possui sua própria cadeia de escalonamento:
- Detecta que está rodando a nível de Usuário Comum.
- Acorda a interface visual gráfica de senha do S.O hospedeiro (`pkexec` no Linux X11/Wayland, `osascript` com *administrator privileges* no Mac, e flag UAC para Windows).
- Instala/Atualiza os Daemons, checa dependências como o Ollama LLM, registra ou atualiza o Systray e repassa o LOG limpo para o `stdout` da interface visual.

Este fluxo orquestrado confere ao Sovereign Pair tanto o peso bruto de um Servidor OCI Headless Oracle quanto o minimalismo "One-Click" de uma aplicação Desktop nativa unificada, gerida pelas mesmas linhas de código Rust.
