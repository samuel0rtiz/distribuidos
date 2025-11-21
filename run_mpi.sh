#!/bin/bash
# Script para ejecutar la aplicación con MPI

cd "$(dirname "$0")"

# Activar entorno virtual si existe
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Número de procesos (por defecto 4: 1 maestro + 3 esclavos)
NP=${1:-4}

# Verificar si hay hostfile
HOSTFILE="mpi_hostfile"
if [ -f "$HOSTFILE" ]; then
    echo "Ejecutando con hostfile: $HOSTFILE"
    mpirun --hostfile "$HOSTFILE" -np "$NP" python main.py
else
    echo "Ejecutando localmente con $NP procesos"
    mpirun -np "$NP" python main.py
fi




