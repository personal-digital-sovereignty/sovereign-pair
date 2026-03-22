#!/bin/bash
echo "Instalando o Widget Plasma Nativo do Sovereign Pair..."

# Verifica se o kpackagetool6 (Plasma 6) existe, se não, cai pro 5 (kpackagetool5)
if command -v kpackagetool6 &> /dev/null; then
    KPACKAGETOOL="kpackagetool6"
elif command -v kpackagetool5 &> /dev/null; then
    KPACKAGETOOL="kpackagetool5"
else
    echo "Erro: kpackagetool não encontrado. O KDE Plasma Tools está instalado?"
    exit 1
fi

$KPACKAGETOOL -t Plasma/Applet -u . || $KPACKAGETOOL -t Plasma/Applet -i .

echo "Sucesso! O Widget 'Sovereign Pair' foi instalado no modo usuário."
echo "Botão Direito no Painel do KDE -> Adicionar Widgets -> Procure por 'Sovereign'"
