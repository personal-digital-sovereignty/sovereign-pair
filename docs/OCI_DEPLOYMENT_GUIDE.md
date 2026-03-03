# Guia Definitivo: Sobrevivendo ao Oracle Cloud Infrastructure (OCI)

A implantação do braço "Cibrid" (Sovereign Node) na Oracle Cloud Framework sofreu com gargalos corporativos severos durante os testes reais em Ashburn (us-ashburn-1). Este documento serve como post-mortem e "How-To" definitivo para não arrancarmos os cabelos no futuro.

---

## 1. O Temido Erro: `500-InternalError, Out of host capacity`

**O Problema**:
Mesmo atualizando a conta de *Always Free* para *Pay As You Go* (Pague Pelo Que Usar), a tentativa de rodar `tofu apply` para criar uma VM Ampere A1.Flex (ARM64) retornou o erro `Out of host capacity`.
Ao contrário da intuição, a Oracle **não reserva hardware físico separado para clientes pagantes nas máquinas Ampere**. Eles dividem o mesmo rack com o Free Tier. Como há milhares de robôs no mundo todo farmando IPs gratuitos, as regiões mais quentes (como Virgínia/Ashburn) ficam sem capacidade 24 horas por dia.

**O Workaround (O Script "Martelo")**:
Construímos o script `infra/terraform/retry_deploy.sh`. Ele ignora o erro 500 e bate na porta da API da Oracle a cada 2 minutos (`sleep 120`).
Quando alguém deleta uma máquina e um slot surge, o script rapidamente executa `tofu apply -auto-approve` e rouba a vaga antes de um humano conseguir clicar na interface Web.

**Importante:** Nunca apague a máquina se for mudar algo. Modifique *em cima* dela. Se você der `tofu destroy`, outro bot rouba a sua vaga em 4 segundos e você volta ao fim da fila.

---

## 2. A Incomunicação: OCI DNS Failure (Erro 502/Timeout)

**O Problema**:
Nosso código Terraform injeta um script `cloud-init.yaml` para instalar a Tailscale e o Docker assim que o Ubuntu dá o primeiro boot.
No entanto, quando a nossa máquina de 6 Cores finalmente "nasceu", a placa de rede da VCN (Virtual Cloud Network) da Oracle demorou para inicializar o resolvedor de DNS padrão. O `apt-get update` e o `curl` da Tailscale falharam (Temporary failure resolving 'ports.ubuntu.com'). A máquina ligou, mas vazia e inútil.

**O Workaround (Intervenção na Unha)**:
1. Conectamos via SSH na máquina moribunda.
2. Forçamos o DNS do Google editando os Nameservers:
   `echo 'nameserver 8.8.8.8' | sudo tee /etc/resolv.conf > /dev/null`
3. Executamos os comandos de instalação da Tailscale e do Ollama nativamente no bash da Oracle, resolvendo a questão sem perder a preciosa vaga.

---

## 3. O Inferno das Chaves SSH (.PEM vs RSA)

**O Problema**:
Por padrão, o Terraform/Sovereign paira em chaves de criptografia Curva Elíptica (ED25519) (`~/.ssh/id_ed25519.pub`). 
Contudo, se você for criar a máquina **manualmente pela interface Web da Oracle** (ou usar a suíte legada deles), a OCI costuma rejeitar ou formatar mal chaves recém-criadas sem o cabeçalho clássico `ssh-rsa` (o formato das antigas `.pem`).
Isso causava erro de `Permission denied (publickey)` ao tentarmos resgatar a máquina fantasma.

**O Workaround**:
Sempre use o `cloud-init.yaml` (bloco `ssh_authorized_keys:`) do Terraform para "injetar" a chave local pura. A injeção via boot-script ignora a UI da Oracle Cloud e escreve a chave correta direto na raiz do Ubuntu, garantindo que o seu par gerado via Terminal Linux funcionará.

---

## 4. Estratégias Financeiras e Tabelas de Preços

O Sovereign Pair funciona maravilhosamente bem sob a política de "Pay As You Go" para ganharmos velocidade. 

### A Grande Pergunta: Posso ter a máquina de 6 Cores e também "farmar" uma máquina Free Tier de 4 cores em outra região?
**Resposta**: Não simultaneamente. A Oracle garante um *total global* de 4 OCPUs e 24GB de RAM gratuitos por **Tenancy** (Conta/CPF).
Isso significa que, se você está usando a máquina paga de 6 OCPUs, 4 desses OCPUs e 24GB desses GBs ainda entrarão no "desconto" do Free Tier, e você *só pagará o excedente* (Neste caso, você paga apenas por 2 OCPUs e 8 GB extras num datacenter, mas não conseguirá levantar os 4 grátis do outro lado ao mesmo tempo sem pagar por 100% deles).

### Cálculo de Custos (VM.Standard.A1.Flex - 6 Cores, 32 GB RAM)
*Cotação OCI Arm Ampere Base: $0.010 por OCPU/h + $0.0015 por GB/h.*

*Porém, se a conta absorve o desconto Free Tier nos primeiros 4 Cores e 24GB, a conta fica assim:*

| Recurso | Utilizado | Coberto pelo Free Tier | Quantidade Faturável | Custo por Hora | Custo por Mês (730h) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **OCPU (Cores)** | 6 | - 4 | **2 OCPUs** | $ 0.02 | **$ 14.60** |
| **Memória (RAM)**| 32 GB | - 24 GB | **8 GB** | $ 0.012 | **$ 8.76** |
| **Armazenamento**| 50 GB | - 50 GB | **0 GB** | $ 0.00 | **$ 0.00** |
| **IP Público** | 1 | - 1 | **0** | $ 0.00 | **$ 0.00** |

**Total Estimado por Mês ($ USD):** ~$23.36  
**Total Estimado por Mês (R$ BRL):** ~R$ 130,00  

Se você precisar desligar a máquina ou deixá-la parada, a cobrança cessa (exceto centavos pelo disco armazenado). Se você for rodar o Sovereign Node o mês inteiro sem parar, o custo final extraindo petróleo com 6 núcleos de processamento será de apenas **R$ 130 por mês**.

---

## 5. Como usar 100% "The Coder" na Oracle (Cibrid Network)

Agora que o *sovereign-rag-cloud* local pode ser desligado, o fluxo do Tailscale substitui o host do Doctor.
Para usar apenas a Oracle:
1. Abra o arquivo `.env` do Sovereign Pair nativo.
2. Troque as URIs locais para o IP da Tailscale de Ashburn:  
   `OLLAMA_API_BASE=http://100.116.34.115:11434`
3. Mate qualquer Ollama rodando no seu Linux (Ryzen). A partir de agora, o The Accountant e o The Coder usam 100% o OCI Cloud.
