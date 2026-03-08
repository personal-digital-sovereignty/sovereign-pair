# Guia de Integração: OpenCode Plugin & Sovereign Pair Proxy

Este documento serve como o passo a passo oficial para integrar extensões de IA de Código (ex: **OpenCode**, Cursor, Cline ou Continue.dev) que não possuem painéis de configuração na UI do VS Code, conectando-as diretamente ao Backend do **Sovereign Pair** (`Local-First` e `Oracle OCI Proxy`).

## 1. Por que "Injetar no Coração" da Configuração?
Extensões recém-lançadas ou construídas visando apenas a OpenAI, muitas vezes não expõem campos como "Custom Base URL" amigavelmente na interface do VS Code (`Ctrl + ,`).
Quando isso acontece, precisamos forçar a sobreposição dessas chaves diretamente nos arquivos de escopo do Workspace (a pasta atual onde trabalhamos).

## 2. Passo a Passo: O que foi feito?
Criamos dois arquivos de rastreio de Configuração no diretório atual do projeto (Workspace).
1. `.vscode/settings.json`
2. `.opencode.json` (usado nativamente pelo OpenCode V1)

### O Payload Injetado
Ambos os arquivos levam a mesma matriz de autoridade. Se a extensão lê as configurações do próprio VSC, ela o fará pela pasta `.vscode`. Se lê de configuração customizada, fará pelo `.opencode.json`:
```json
{
  "apiProvider": "openai",
  "apiBaseUrl": "http://localhost:8000/opencode/v1",
  "apiKey": "sovereign-local-key",
  "model": "qwen2.5:0.5b"
}
```

## 3. Dinâmica de Funcionamento (The Coder)
Assim que o Desenvolvedor disparar um Prompt via atalho na janela lateral do VS Code:
1. **O Plugin** acha que está se comunicando com o servidor Cloud da `OpenAI` (`api.openai.com/v1/chat/completions`).
2. **Localização**: Como reescrevemos o `apiBaseUrl`, a request viaja via HTTP (localhost) e bate diretamente no nosso Endpoint `routes_opencode.py`.
3. **Conversão Silenciosa**: Nossos Modelos Pydantic recebem o JSON rigoroso, convertem para `LlamaIndex Messages` e analisam a Tag do modelo.
4. **Veredicto / Fallback**: Se o Desenvolvedor solicitou um modelo proprietário pesado (ex: `gpt-4o` ou `claude-3-5-sonnet`), o Sovereign Backend encaminhará este pacote via conexão **mTLS criptografada** para o Cluster na Oracle. Caso contrário, resolverá tudo puramente local (Ryzen/Local Llama).
5. **Automação Escrita (SSE)**: O resultado voltará via Streaming Assíncrono para o Editor escrevendo o código em tempo real.

## 4. O que testar no End-to-End?
Com estes arquivos agora adicionados ao rastreio GIT, qualquer pessoa que abrir essa Workspace e possuir o VS Code ou Cursor, já virá configurado por padrão a se reportar ao Sovereign.
Abra o painel "Chat" da sua extensão, solicite a extração de uma classe em Python e observe o log na janela do `Uvicorn` do Backend reagindo à sua escrita.
