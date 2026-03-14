# Integração de Extensões via Sovereign Pair Proxy

Este manual abrange métodos para integração padronizada de ecossistemas auxiliares e clientes programáveis de IA de código no Visual Studio Code (ex: OpenCode, Cursor, Cline) frente ao URL base local do sistema (Sovereign Pair Local / OCI Proxy).

## 1. Sobresposição de Configuração
Certos middlewares de extensões adotam endpoints "hardcoded" ligados a infraestruturas de processamento comerciais restritas ou carecem de métodos gráficos de alteração sob a interface. 
Nestas ocorrências, aplica-se a sobrescrita injetando configurações base puras diretamente no arquivo raiz do projeto (Workspace).

## 2. Padrões Declarativos do Workspace
Implementou-se a alteração paramétrica sob os manifestos de identificação e parâmetros contidos no diretório raiz do desenvolvedor:
- `.vscode/settings.json`
- `.opencode.json` (Especificador declarativo do OpenCode)

### Metadados Injetados para O.S Proxy
De acordo com os protocolos integrativos do VS Code, qualquer chamada de extensão buscará priorizar escopos referenciados nestes arquivos locais.
Aplica-se sob ambos os arquivos a seguinte estruturação:
```json
{
  "apiProvider": "openai",
  "apiBaseUrl": "http://localhost:8000/opencode/v1",
  "apiKey": "sovereign-local-key",
  "model": "qwen2.5:0.5b"
}
```

## 3. Direcionamento e Proxy HTTP
O fluxo restritivo que estabelece as intermediações desenvolve-se processualmente em:
1. **Transmissão Inicial**: A solicitação da Extensão (IDE) envia payload compatível com APIs comerciais.
2. **Interceptação Nativa**: O parâmetro `apiBaseUrl` contendo loopback `localhost` repassa o envio transacional HTTPS/HTTP ao Endpoint O.S Framework do FastAPI Python.
3. **Conversão Relacional**: A API do RAG local lê, intercepta a requisição Pydantic e a converte em objetos nativos RAG Standard LlamaIndex para inferência.
4. **Avaliação Direcionada**: Se o modelo solicitado exigir processamento extenso, a orquestração direcionará via conexão mTLS encapsulada à Oracle Cloud OCI. Requisições leves ou de baixa latência são atendidas localmente com `Ollama Local`.
5. **SSE Stream Delivery**: Respostas retornam estruturadas dinamicamente em protocolo Server-Sent Events do FastAPI diretamente para a aba do cliente no VS Code.

## 4. Confirmações E2E Locais
Uma vez os diretórios indexados sob controle de repositório GIT, inicializações em novas instâncias do VS Code acatarão como servidor de inferência primária o roteador local do FastAPI. Verifique os retornos através do Terminal Monitor Uvicorn durante a rotina do desenvolvedor.
