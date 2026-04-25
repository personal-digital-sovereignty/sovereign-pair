# 🏗️ Infraestrutura & Provisionamento Cíbrido
## Topologia de Rede e Gestão de Nós

O Sovereign Pair opera como uma malha distribuída de nós. Este guia detalha a infraestrutura necessária para hospedar o motor e seus workers, com foco especial em nuvem híbrida (OCI) e otimização de baixo nível.

---

## 1. Provisionamento de Nó Oracle Cloud (OCI - Ampere aarch64)

Para usuários que desejam realizar **Offload de Inferência**, o uso de instâncias ARM64 na Oracle Cloud é a solução recomendada devido à alta contagem de cores e RAM gratuita.

### 1.1 Configuração do Host
1. **OS**: Ubuntu 22.04 ou 24.04 (aarch64).
2. **Firewall (Ingress Rules)**: 
    - **NÃO EXPOR** a porta 11434 ou 38001 publicamente.
    - O tráfego deve ser tunelado via SSH conforme o [Sovereign Mesh Protocol](BLUEPRINT.md#3-topologia-de-rede-oci-mesh).
3. **Dependências Base**:
   ```bash
   sudo apt update && sudo apt install -y curl git python3-venv python3-pip
   ```

### 1.2 Instalação do Motor de Inferência (Ollama)
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 1.3 Preparação dos Python Workers (Sandbox)
O Sovereign Pair provisiona automaticamente os workers via SSH, mas o host precisa ter o ambiente base:
```bash
# Garantir que o diretório de workers exista
mkdir -p ~/sovereign/python_workers
```

---

## 2. Otimização de Hardware (The Purist Config)

Para extrair performance máxima em LLMs locais (Air-Gapped), o Kernel do Linux deve ser configurado para não interferir na alocação de memória dos tensores.

### 2.1 A Armadilha do ZRAM
Modelos GGUF quantizados são matematicamente incomprimíveis. O uso de ZRAM (Swap compactada) causa picos de CPU inofensivos e queda drástica de tokens por segundo (T/s).

**Diretriz**: Em máquinas com >16GB de RAM dedicadas à IA, **desative o ZRAM**.
```bash
sudo zramctl --reset /dev/zram0  # Se existir
sudo systemctl disable --now zram-config
```

### 2.2 Swap & Swappiness
Reduza a agressividade do Kernel em trocar páginas de memória para o disco, garantindo que o modelo permaneça "travado" na RAM física.
```bash
# Definir swappiness para 10 (mínimo conservador)
sudo sysctl vm.swappiness=10
echo "vm.swappiness=10" | sudo tee -a /etc/sysctl.conf
```

---

## 3. Sovereign Mesh (Túneis SSH)

O sistema utiliza o `ssh_mesh_connector.rs` para gerenciar a conectividade. 
- **Watchdog**: O motor Rust monitora a saúde do túnel a cada 30s.
- **Hot-Reload**: Alterações no IP do Nó Oracle via UI resultam na queda e reconstrução imediata do túnel sem reiniciar o serviço.
