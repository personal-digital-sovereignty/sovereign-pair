#!/bin/bash
set -e

echo "=========================================================="
echo "Sovereign Pair - Manual Binary OCI Injector"
echo "=========================================================="

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: ./deploy_binary_manual.sh <SERVER_IP> <GH_TOKEN> [RELEASE_TAG]"
    echo "Example: ./deploy_binary_manual.sh 129.213.52.11 ghp_YOURTOKEN 0.7.2"
    exit 1
fi

SERVER_IP=$1
GH_TOKEN=$2
RELEASE_TAG=${3:-"nightly"}

echo "🎯 Target IP: $SERVER_IP"
echo "🎯 Release Tag: $RELEASE_TAG"

echo "⏳ Conectando na instância OCI..."

ssh -o StrictHostKeyChecking=no ubuntu@$SERVER_IP << EOF
    set -x
    echo "🛑 Parando Sovereign service se existir..."
    sudo systemctl stop sovereign || true
    
    mkdir -p /tmp/sovereign
    cd /tmp/sovereign
    
    echo "🔽 Baixando release binário da API Github..."
    TAR_URL="\$(curl -sH \"Authorization: Bearer $GH_TOKEN\" https://api.github.com/repos/Personal-Digital-Sovereignty/sovereign-pair/releases/tags/$RELEASE_TAG | grep browser_download_url | grep sovereign-core-linux-arm64-binary | cut -d '\"' -f 4)"
    
    if [ -z "\$TAR_URL" ]; then
        echo "❌ Erro: Não foi possível obter a URL do artefato na Release $RELEASE_TAG."
        exit 1
    fi
    
    echo "🌐 Baixando de \$TAR_URL ..."
    wget -qO sovereign-core --header="Authorization: Bearer $GH_TOKEN" --header="Accept: application/octet-stream" "\$TAR_URL"
    
    chmod +x sovereign-core
    sudo mv sovereign-core /usr/local/bin/sovereign-core
    
    echo "🔄 Reiniciando SystemD..."
    sudo systemctl daemon-reload
    sudo systemctl enable sovereign
    sudo systemctl start sovereign
    
    echo "✅ Binário Injetado e Serviço Iniciado Manualmente!"
EOF

echo "🚀 Processo manual concluído com sucesso."
