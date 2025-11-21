"""
Punto de entrada principal de la aplicación.
Sistema de Algoritmo Genético TSP con Cluster Beowulf (MPI)
Arquitectura MVC
"""
import sys
import os
import subprocess

def check_and_relaunch_with_mpi():
    """
    Verifica si debe ejecutarse con MPI y relanza automáticamente.
    Busca archivos de configuración: hosts, mpi_hostfile, hostfile
    """
    # Buscar archivos de configuración de cluster (prioridad: hosts)
    hostfile_candidates = ["hosts", "mpi_hostfile", "hostfile", "mpi_hostfile_local"]
    hostfile_path = None
    
    for candidate in hostfile_candidates:
        if os.path.exists(candidate):
            hostfile_path = candidate
            break
    
    if not hostfile_path:
        # No hay configuración de cluster, ejecutar en modo local
        return False
    
    # Leer configuración del hostfile para determinar número de procesos
    try:
        total_slots = 0
        with open(hostfile_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split()
                    if len(parts) >= 2:
                        # Formato: hostname slots=N
                        slots_str = parts[1].split('=')[1] if '=' in parts[1] else parts[1]
                        total_slots += int(slots_str)
                    elif len(parts) == 1:
                        # Formato simple: solo hostname (asume 1 slot)
                        total_slots += 1
        
        if total_slots == 0:
            # No se pudo determinar, usar valor por defecto 20
            total_slots = 20
        
        # Relanzar con mpirun
        print(f"[INFO] Detectado archivo de configuración: {hostfile_path}")
        print(f"[INFO] Relanzando con MPI: {total_slots} procesos")
        
        script_path = os.path.abspath(__file__)
        cmd = ["mpirun", "-np", str(total_slots), "--hostfile", hostfile_path, 
               sys.executable, script_path] + sys.argv[1:]
        
        # Ejecutar y esperar
        result = subprocess.run(cmd)
        sys.exit(result.returncode)
        
    except Exception as e:
        print(f"[ERROR] Error al relanzar con MPI: {e}")
        print("[INFO] Continuando en modo local...")
        return False

# Importar MPI primero para determinar si somos maestro o esclavo
try:
    from mpi4py import MPI
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    MPI_AVAILABLE = True
except ImportError:
    MPI_AVAILABLE = False
    rank = 0
    size = 1
    comm = None

# Verificar y relanzar con MPI si es necesario (solo si no estamos ya en MPI)
if __name__ == "__main__":
    if not MPI_AVAILABLE:
        check_and_relaunch_with_mpi()

# Si somos esclavo, no importar tkinter
if MPI_AVAILABLE and rank != 0:
    # ESCLAVO: Entrar en bucle de procesamiento
    print(f"[ESCLAVO Rank {rank}] Iniciando proceso esclavo...")
    
    try:
        from models.mpi_handler import MPIHandler
        mpi_handler = MPIHandler()
        
        # Variable para almacenar la matriz de distancias
        dist_matrix = None
        
        # Función de evaluación local
        def eval_tsp_local(individual):
            """Evalúa un individuo usando la matriz de distancias recibida."""
            if dist_matrix is None:
                return float('inf'),
            distance = dist_matrix[individual[-1]][individual[0]]
            for gene1, gene2 in zip(individual[0:-1], individual[1:]):
                distance += dist_matrix[gene1][gene2]
            return distance,
        
        # Bucle principal de esclavo
        print(f"[ESCLAVO Rank {rank}] Esperando mensajes del maestro...")
        task_count = 0
        
        while True:
            try:
                status = MPI.Status()
                message = comm.recv(source=0, tag=MPI.ANY_TAG, status=status)
                tag_received = status.Get_tag()
                
                if tag_received == 99:
                    # Señal de terminación - NO terminar, solo continuar esperando
                    print(f"[ESCLAVO Rank {rank}] Recibida señal de terminación, esperando siguiente ejecución...")
                    continue
                elif tag_received == 100:
                    # Matriz de distancias
                    dist_matrix = message
                    print(f"[ESCLAVO Rank {rank}] Matriz recibida: {len(dist_matrix)}x{len(dist_matrix)}")
                    continue
                elif tag_received == 1:
                    # Tarea
                    if isinstance(message, tuple) and len(message) == 2:
                        task_idx, task = message
                        if task_idx == -1 and task is None:
                            # Fin de lote - continuar esperando siguiente ejecución
                            print(f"[ESCLAVO Rank {rank}] Fin de lote, esperando siguiente ejecución...")
                            continue
                        
                        if dist_matrix is None:
                            comm.send((task_idx, (float('inf'),)), dest=0, tag=2)
                            continue
                        
                        # Procesar tarea
                        result = eval_tsp_local(task)
                        comm.send((task_idx, result), dest=0, tag=2)
                        task_count += 1
            
            except Exception as e:
                print(f"[ESCLAVO Rank {rank}] Error: {e}")
                break
        
        print(f"[ESCLAVO Rank {rank}] Procesadas {task_count} tareas, finalizando...")
    
    except KeyboardInterrupt:
        print(f"[ESCLAVO Rank {rank}] Interrumpido por el usuario")
    except Exception as e:
        print(f"[ESCLAVO Rank {rank}] Error crítico: {e}")
        import traceback
        traceback.print_exc()

else:
    # MAESTRO o modo local: Ejecutar interfaz gráfica
    import tkinter as tk
    from views.gui import MainWindow
    from controllers.app_controller import AppController
    
    if __name__ == "__main__":
        if MPI_AVAILABLE:
            print(f"[MAESTRO Rank {rank}] Iniciando aplicación con {size - 1} esclavos...")
        else:
            print("[MAESTRO] Iniciando aplicación en modo local...")
        
        # Crear ventana principal
        root = tk.Tk()
        
        # Crear vista
        view = MainWindow(root, None)
        
        # Crear controlador
        controller = AppController(view)
        
        # Conectar vista con controlador
        view.controller = controller
        
        # Ejecutar interfaz
        root.mainloop()




