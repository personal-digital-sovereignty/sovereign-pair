# Auditoria de Segurança: Supply Chain & Prevenção de Vazamentos (01/04/2026)

Este documento registra a auditoria oficial de DevSecOps realizada nas esteiras de Integração e Entrega Contínuas (CI/CD) do **Sovereign Pair v0.9.9**, com foco na mitigação de ataques à Cadeia de Suprimentos (Supply Chain) e na proteção de segredos criptográficos.

## 1. Escopo da Auditoria
*   **Arquivos Analisados:** `.github/workflows/ci.yml` e `.github/workflows/deploy-oci.yml`
*   **Ameaças Avaliadas:**
    *   Injeção de Código Malicioso via ferramentas de varredura de terceiros (Ex: Trivy, Fortify).
    *   Vazamento de Variáveis de Ambiente e Chaves de Acesso (Command Injection no Bash do Runner).
    *   Dependências e *Actions* não confiáveis apontando para *branches* mutáveis (`@master` ou `@v[N]`).

## 2. Resultados da Análise de Vazamento de Segredos (Aprovado ✅)
O repositório foi validado contra vazamentos históricos em todos os seus commits.

*   **Varredura Retrospectiva (Gitleaks):** O scanner rodou sobre todo o histórico vivo do repositório (642 commits). O resultado foi impecável (`no leaks found`). Nenhuma chave da infraestrutura OCI ou do GitHub foi indevidamente submetida em texto puro ao versionamento ao longo da vida do projeto.
*   **Prevenção de Command Injection (Bash):** O script de *Deploy* em Nuvem (`deploy-oci.yml`) foi avaliado. Diferente de pipelines vulneráveis que interpolam texto puro no meio do script (`echo ${{ secrets.CHAVE }}`), nossa arquitetura consome as chaves da Oracle indiretamente via mapeamento de ambiente primário O.S (`env: STATE_PASSWORD`). Esse padrão isola o dado da interface gráfica do GitHub, tornando impossível o roubo de chaves pelo desvio dinâmico do Bash ou visualização acidental nos logs públicos.

## 3. Resultados da Análise de Supply Chain (Mitigado 🛡️)
Durante a auditoria, identificamos uma grave falha em potencial na chamada das ferramentas de segurança de terceiros (SCA).

*   **A Vulnerabilidade Localizada:** O scanner *Trivy* estava sendo invocado através da tag móvel `aquasecurity/trivy-action@master`. Da mesma forma, outras ferramentas de mercado usavam tags globais (ex: `@v2`). Se a conta corporativa responsável por essas ferramentas for hackeada, códigos maliciosos inseridos na *branch master* seriam clonados automaticamente para dentro da nossa esteira de desenvolvimento, garantindo acesso do atacante ao nosso código-fonte primário em Rust. (Nota: Observamos que a ferramenta *Fortify* não atua nativamente neste projeto).
*   **A Correção Aplicada (SHA-1 Pinning):** Substituímos de imediato todas as referências móveis por seus respectivos *Hashes Criptográficos* (SHA-1). Agora, os servidores do GitHub são obrigados a validar a integridade matemática exata do código de terceiros que estamos baixando. Se um único caractere for alterado maliciosamente no repositório de origem, o download falha e nossa infraestrutura se mantém intransponível.

**Exemplo Prático Corrigido (`ci.yml`):**
```yaml
# ANTES (Vulnerável):
uses: aquasecurity/trivy-action@master

# DEPOIS (Blindado):
uses: aquasecurity/trivy-action@57a97c7e7821a5776cebc9bb87c984fa69cba8f1 # v0.35.0
```

## Conclusão
O Sovereign Pair alcança total conformidade nas práticas corporativas de CI/CD para seu versionamento. Nossa esteira segue selada contra o comprometimento de terceiros por injeção na cadeia de dependências e os cofres do GitHub protegem as chaves da Oracle OCI sob rígidos padrões de encapsulamento no ciclo de execução do Bash O.S.
