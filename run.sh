#!/bin/bash
# Script para ejecutar la aplicación en modo local

cd "$(dirname "$0")"

# Activar entorno virtual si existe
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Ejecutar aplicación
python main.py




