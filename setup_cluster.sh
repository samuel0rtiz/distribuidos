#!/bin/bash
# Script para configurar el cluster y copiar el código a los nodos

# Configuración
NODOS=("diego" "alejandro" "sam" "balam")
USUARIO="${USER}"  # Cambiar si usas otro usuario
RUTA_LOCAL="$(pwd)"
RUTA_REMOTA="${RUTA_LOCAL}"  # Cambiar si la ruta es diferente en los nodos

echo "=== Configuración del Cluster Beowulf ==="
echo "Nodos: ${NODOS[@]}"
echo "Usuario: ${USUARIO}"
echo "Ruta local: ${RUTA_LOCAL}"
echo "Ruta remota: ${RUTA_REMOTA}"
echo ""

# Verificar conexión SSH
echo "1. Verificando conexión SSH a los nodos..."
for nodo in "${NODOS[@]}"; do
    echo -n "  Probando ${nodo}... "
    if ssh -o ConnectTimeout=5 -o BatchMode=yes "${USUARIO}@${nodo}" "echo 'OK'" 2>/dev/null; then
        echo "✓ Conectado"
    else
        echo "✗ Error de conexión"
        echo "    Ejecuta: ssh-copy-id ${USUARIO}@${nodo}"
    fi
done
echo ""

# Verificar OpenMPI
echo "2. Verificando OpenMPI en los nodos..."
for nodo in "${NODOS[@]}"; do
    echo -n "  ${nodo}: "
    if ssh "${USUARIO}@${nodo}" "which mpirun" &>/dev/null; then
        version=$(ssh "${USUARIO}@${nodo}" "mpirun --version | head -1")
        echo "✓ ${version}"
    else
        echo "✗ OpenMPI no instalado"
        echo "    Instala con: sudo apt-get install openmpi-bin (o equivalente)"
    fi
done
echo ""

# Verificar Python
echo "3. Verificando Python en los nodos..."
for nodo in "${NODOS[@]}"; do
    echo -n "  ${nodo}: "
    version=$(ssh "${USUARIO}@${nodo}" "python3 --version 2>&1")
    if [ $? -eq 0 ]; then
        echo "✓ ${version}"
    else
        echo "✗ Python 3 no encontrado"
    fi
done
echo ""

# Copiar código
echo "4. ¿Deseas copiar el código a los nodos? (s/n)"
read -r respuesta
if [[ "$respuesta" =~ ^[Ss]$ ]]; then
    for nodo in "${NODOS[@]}"; do
        echo "  Copiando a ${nodo}..."
        rsync -avz --exclude 'venv' --exclude '__pycache__' --exclude '*.pyc' \
            --exclude '.git' \
            "${RUTA_LOCAL}/" "${USUARIO}@${nodo}:${RUTA_REMOTA}/"
        if [ $? -eq 0 ]; then
            echo "    ✓ Código copiado a ${nodo}"
        else
            echo "    ✗ Error copiando a ${nodo}"
        fi
    done
fi
echo ""

# Instalar dependencias
echo "5. ¿Deseas instalar dependencias en los nodos? (s/n)"
read -r respuesta
if [[ "$respuesta" =~ ^[Ss]$ ]]; then
    for nodo in "${NODOS[@]}"; do
        echo "  Instalando dependencias en ${nodo}..."
        ssh "${USUARIO}@${nodo}" "cd ${RUTA_REMOTA} && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
        if [ $? -eq 0 ]; then
            echo "    ✓ Dependencias instaladas en ${nodo}"
        else
            echo "    ✗ Error instalando dependencias en ${nodo}"
        fi
    done
fi
echo ""

# Verificar configuración final
echo "6. Verificando configuración final..."
echo "  Probando MPI con hostname:"
mpirun --hostfile hosts -np 4 hostname 2>&1 | head -10
echo ""

echo "=== Configuración completada ==="
echo "Para ejecutar el sistema, desde el nodo maestro ejecuta:"
echo "  python3 main.py"


