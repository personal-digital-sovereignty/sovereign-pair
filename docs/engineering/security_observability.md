# 🛡️ Segurança & Observabilidade (Telemetry Sinkhole)

Este guia detalha os protocolos de blindagem do sistema e as métricas de monitoramento vital.

---

## 1. Auditoria de Segurança (Security Audit)

O Sovereign Pair segue o princípio de **Zero-Trust Local**.

- **Epistemic Guard**: Verificação de proveniência criptográfica (SHA-256) para garantir que arquivos de contexto não foram alterados entre a leitura e a inferência.
- **KMS (Key Management System)**: Criptografia AES-256-GCM para chaves de API e tokens de sessão.
- **Zeroize Memory**: Buffers sensíveis são zerados em memória após o uso para evitar vazamentos em memory dumps.

---

## 2. Telemetry Sinkhole

A observabilidade é a chave para o controle soberano. Monitoramos a "saúde" do cérebro artificial sem exfiltrar dados para terceiros.

- **Métricas Vitais**:
    - **TTFT (Time to First Token)**: Latência inicial de resposta.
    - **TPS (Tokens Per Second)**: Vazão da inferência.
    - **VRAM/RAM Usage**: Monitoramento preventivo de OOM.
- **Sovereign Sinkhole**: Toda telemetria é armazenada localmente no SQLite e nunca deixa a rede do usuário, a menos que explicitamente exportada em formato de relatório.
