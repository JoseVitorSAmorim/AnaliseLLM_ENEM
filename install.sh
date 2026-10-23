#!/bin/bash

echo "============================================================"
echo " Instalador de Dependências"
echo "============================================================"

# 1. Detecta o Sistema Operacional
OS="$(uname -s)"
case "${OS}" in
    Linux*)     machine=Linux;;
    CYGWIN*)    machine=Windows;;
    MINGW*)     machine=Windows;;
    MSYS*)      machine=Windows;;
    *)          machine="Desconhecido"
esac

echo "-> Sistema operacional detectado: $machine"

# 2. Atualizar e verificar o PIP
echo "-> Verificando e atualizando o PIP..."
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo "[ERRO] Python não encontrado! Instale o Python antes de continuar."
    exit 1
fi

$PYTHON_CMD -m pip install --upgrade pip

# 3. Instalar Dependências Python (Bibliotecas)
echo "-> Instalando pacotes Python..."
# google-genai já está aqui! Adicionei o python-dotenv para garantir a leitura do seu arquivo .env
$PYTHON_CMD -m pip install google-genai python-dotenv

echo "============================================================"
echo " Processo finalizado!"
echo "============================================================"