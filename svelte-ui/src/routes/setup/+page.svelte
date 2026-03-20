<script lang="ts">
	import { onMount } from 'svelte';
	import { invoke } from '@tauri-apps/api/core';
	import { desktopDir, join } from '@tauri-apps/api/path';
	import { writeTextFile } from '@tauri-apps/plugin-fs';
	import { Command } from '@tauri-apps/plugin-shell';

	let statusLogs: string[] = [];
	let isInstalling = false;
	let ollamaDetected = false;
	let setupComplete = false;

	function appendLog(msg: string) {
		statusLogs = [...statusLogs, msg];
	}

	async function startInstallation() {
		isInstalling = true;
		appendLog("🚀 Iniciando instalação Cíbrida Sovereign Pair...");

		// 1. Detectar Ollama via Fetch Local (Simulação Cliente)
		appendLog("🔍 Checando Engine RAG (Ollama) em localhost:11434...");
		try {
			const res = await fetch("http://127.0.0.1:11434/api/tags");
			if (res.ok) {
				ollamaDetected = true;
				appendLog("✅ Motor Ollama detectado com sucesso!");
			}
		} catch (e) {
			ollamaDetected = false;
			appendLog("⚠️ AVISO: Ollama não está rodando! O Sovereign irá funcionar, mas sem RAG Local.");
			appendLog("👉 Por favor, acesse https://ollama.com e instale.");
		}

		// 2. Invocar o backend Rust para Instalar Serviço e SysTray
		appendLog("⚙️ Solicitando privilégios ao Sistema Operacional para criar OS Daemons...");
		
		try {
			// Como o backend Rust "sovereign-core" é agora nosso sidecar, 
			// vamos executar sovereign-core --setup via shell do Tauri
			// Nota: se precisarmos de root, precisamos de um comando com pkexec / macOS osascript
			// Mas para MVP de setup UI, podemos rodar o CLI compilado e capturar stdout.
			const coreCommand = Command.sidecar('binaries/sovereign-core', ['--setup']);
			
			coreCommand.stdout.on('data', line => {
				appendLog(`[Core] ${line}`);
			});
			
			coreCommand.stderr.on('data', line => {
				appendLog(`[Core Err] ${line}`);
			});

			const output = await coreCommand.execute();
			
			if (output.code === 0) {
				appendLog("✅ Sovereign Daemons e Logs Inicializados!");
				
				appendLog("🧩 Injetando Widgets de Desktop (KDE/Gnome) no Espaço do Usuário Local...");
				try {
					const widgetMsg = await invoke("install_desktop_widgets") as string;
					appendLog(`✅ ${widgetMsg}`);
				} catch (wErr) {
					appendLog(`⚠️ AVISO Widget: ${wErr}`);
				}

				try {
					const deskPath = await join(await desktopDir(), "Sovereign_Install.log");
					await writeTextFile(deskPath, statusLogs.join("\n"));
					appendLog(`📄 Log de implantação exportado para a sua Área de Trabalho!`);
				} catch (logErr) {
					appendLog(`⚠️ Falha ao exportar Log: ${logErr}`);
				}

				setupComplete = true;
			} else {
				appendLog(`❌ Erro de Sistema: Permissão Negada ou Falha (Código ${output.code}). Tente rodar o instalador como Administrador.`);
			}
			
		} catch (err) {
			appendLog(`❌ Exceção Fatal ao integrar O.S: ${err}`);
		}

		isInstalling = false;
	}

</script>

<div class="wizard-container">
	<div class="glass-card">
		<h1 class="gradient-text">Bem-vindo ao Sovereign Pair</h1>
		<p class="subtitle">O seu Cíbrido Descentralizado está pronto para habitar o seu O.S</p>

		<div class="actions">
			<button class="primary-btn" on:click={startInstallation} disabled={isInstalling || setupComplete}>
				{#if isInstalling}
					Instalando Background Services...
				{:else if setupComplete}
					✅ Instalação Concluída
				{:else}
					🚀 Instalar Integração do Sistema
				{/if}
			</button>
		</div>

		<div class="terminal">
			{#if statusLogs.length === 0}
				<div class="empty-term">Aguardando início... O Log de Implantação aparecerá aqui.</div>
			{/if}
			{#each statusLogs as log (log)}
				<div class="log-line">> {log}</div>
			{/each}
		</div>

		{#if setupComplete}
			<a href="/" class="continue-btn">Prosseguir para o Dashboard ➔</a>
		{/if}
	</div>
</div>

<style>
	.wizard-container {
		display: flex;
		justify-content: center;
		align-items: center;
		height: 100vh;
		background: radial-gradient(circle at center, #1a1a24, #0d0d14);
		color: white;
		font-family: 'Inter', sans-serif;
	}

	.glass-card {
		background: rgba(255, 255, 255, 0.05);
		backdrop-filter: blur(16px);
		border-radius: 20px;
		padding: 2.5rem;
		width: 100%;
		max-width: 650px;
		border: 1px solid rgba(255, 255, 255, 0.1);
		box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
		text-align: center;
	}

	.gradient-text {
		background: linear-gradient(135deg, #a370f7, #5a4fcf);
		background-clip: text;
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		font-size: 2.2rem;
		margin-bottom: 0.5rem;
	}

	.subtitle {
		color: #9ba1a6;
		margin-bottom: 2rem;
	}

	.actions {
		margin-bottom: 2rem;
	}

	.primary-btn {
		background: linear-gradient(135deg, #a370f7, #5a4fcf);
		color: white;
		border: none;
		padding: 12px 28px;
		font-size: 1.1rem;
		border-radius: 8px;
		cursor: pointer;
		font-weight: 500;
		transition: transform 0.2s, box-shadow 0.2s;
	}

	.primary-btn:hover:not(:disabled) {
		transform: translateY(-2px);
		box-shadow: 0 8px 15px rgba(163, 112, 247, 0.4);
	}

	.primary-btn:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.continue-btn {
		display: inline-block;
		margin-top: 1.5rem;
		color: #a370f7;
		text-decoration: none;
		font-weight: 600;
		transition: color 0.2s;
	}
	.continue-btn:hover {
		color: #c9a3ff;
	}

	.terminal {
		background: #000;
		border-radius: 8px;
		padding: 1rem;
		height: 250px;
		overflow-y: auto;
		text-align: left;
		font-family: 'Fira Code', monospace;
		font-size: 0.85rem;
		color: #0f0;
		border: 1px solid #333;
	}

	.empty-term {
		color: #555;
		font-style: italic;
	}

	.log-line {
		margin-bottom: 0.25rem;
	}
</style>
