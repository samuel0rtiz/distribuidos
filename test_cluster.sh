#!/bin/bash
# Script para probar la configuración del cluster

echo "=== Prueba de Configuración del Cluster ==="
echo ""

# Verificar que existe el archivo hosts
if [ ! -f "hosts" ]; then
    echo "✗ Error: No se encuentra el archivo 'hosts'"
    exit 1
fi
echo "✓ Archivo 'hosts' encontrado"
echo ""

# Contar procesos totales
TOTAL_PROCESOS=$(grep -v '^#' hosts | grep -v '^$' | awk '{sum += $2; if (NF == 1) sum += 1} END {print sum}')
echo "Procesos totales configurados: ${TOTAL_PROCESOS}"
echo ""

# Probar conexión a cada nodo
echo "Probando conexión SSH a los nodos..."
while IFS= read -r line; do
    if [[ ! "$line" =~ ^# ]] && [ ! -z "$line" ]; then
        nodo=$(echo "$line" | awk '{print $1}')
        echo -n "  ${nodo}: "
        if ssh -o ConnectTimeout=5 -o BatchMode=yes "${USER}@${nodo}" "echo 'OK'" 2>/dev/null; then
            echo "✓ Conectado"
        else
            echo "✗ Error de conexión"
        fi
    fi
done < hosts
echo ""

# Probar MPI básico
echo "Probando MPI (hostname en cada proceso):"
mpirun --hostfile hosts -np ${TOTAL_PROCESOS} hostname 2>&1 | sort | uniq -c
echo ""

# Probar Python en todos los nodos
echo "Probando Python en todos los nodos:"
mpirun --hostfile hosts -np ${TOTAL_PROCESOS} python3 --version 2>&1 | head -5
echo ""

# Probar importación de módulos Python
echo "Probando importación de módulos Python:"
mpirun --hostfile hosts -np ${TOTAL_PROCESOS} python3 -c "import mpi4py; print('mpi4py OK')" 2>&1 | head -5
echo ""

echo "=== Prueba completada ==="

