#!/usr/bin/env python3
"""
Script de prueba para verificar que los esclavos están funcionando correctamente.
"""
import sys
import os

try:
    from mpi4py import MPI
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    MPI_AVAILABLE = True
except ImportError:
    print("ERROR: mpi4py no está instalado")
    sys.exit(1)

if rank == 0:
    # MAESTRO
    print(f"[MAESTRO] Total de procesos: {size}")
    print(f"[MAESTRO] Enviando mensaje de prueba a cada esclavo...")
    
    for slave_rank in range(1, size):
        try:
            comm.send(f"Mensaje de prueba para esclavo {slave_rank}", dest=slave_rank, tag=1)
            print(f"[MAESTRO] Mensaje enviado a esclavo {slave_rank}")
        except Exception as e:
            print(f"[MAESTRO] Error enviando a esclavo {slave_rank}: {e}")
    
    # Recibir respuestas
    print(f"[MAESTRO] Esperando respuestas de los esclavos...")
    for slave_rank in range(1, size):
        try:
            respuesta = comm.recv(source=slave_rank, tag=2)
            print(f"[MAESTRO] Respuesta de esclavo {slave_rank}: {respuesta}")
        except Exception as e:
            print(f"[MAESTRO] Error recibiendo de esclavo {slave_rank}: {e}")
    
    print(f"[MAESTRO] Prueba completada")
else:
    # ESCLAVO
    print(f"[ESCLAVO Rank {rank}] Iniciado y esperando mensaje del maestro...")
    sys.stdout.flush()
    
    try:
        mensaje = comm.recv(source=0, tag=1)
        print(f"[ESCLAVO Rank {rank}] Mensaje recibido: {mensaje}")
        sys.stdout.flush()
        
        respuesta = f"ESCLAVO {rank} funcionando correctamente"
        comm.send(respuesta, dest=0, tag=2)
        print(f"[ESCLAVO Rank {rank}] Respuesta enviada al maestro")
        sys.stdout.flush()
    except Exception as e:
        print(f"[ESCLAVO Rank {rank}] ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.stdout.flush()


