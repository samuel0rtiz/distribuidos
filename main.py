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
    Verifica si existe el archivo hosts y relanza automáticamente con MPI.
    Busca el archivo hosts en el directorio actual o en /clusterdir/distribuidos/
    """
    # Buscar archivo hosts en posibles ubicaciones
    hosts_path = None
    possible_paths = [
        "hosts",  # Directorio actual
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "hosts"),  # Mismo directorio que main.py
        "/clusterdir/distribuidos/hosts"  # Ruta específica del cluster
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            hosts_path = path
            break
    
    if not hosts_path:
        # No hay archivo hosts, ejecutar en modo local
        return False
    
    # Relanzar con mpirun usando el comando exacto especificado
    try:
        script_path = os.path.abspath(__file__)
        # Usar ruta absoluta del archivo hosts
        hosts_abs_path = os.path.abspath(hosts_path)
        cmd = ["mpirun", "-np", "20", "--hostfile", hosts_abs_path, 
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
    import sys
    sys.stdout.flush()  # Asegurar que los mensajes se muestren inmediatamente
    print(f"[ESCLAVO Rank {rank}/{size-1}] ===== INICIANDO PROCESO ESCLAVO =====")
    print(f"[ESCLAVO Rank {rank}] Total de procesos MPI: {size}")
    print(f"[ESCLAVO Rank {rank}] Proceso esclavo activo y listo para recibir trabajo")
    sys.stdout.flush()
    
    try:
        from models.mpi_handler import MPIHandler
        mpi_handler = MPIHandler()
        
        print(f"[ESCLAVO Rank {rank}] MPIHandler inicializado correctamente")
        sys.stdout.flush()
        
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
        print(f"[ESCLAVO Rank {rank}] Entrando en bucle de espera de mensajes del maestro...")
        print(f"[ESCLAVO Rank {rank}] Esperando mensajes (tag 100: matriz, tag 1: tareas, tag 99: terminación)")
        sys.stdout.flush()
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
                    print(f"[ESCLAVO Rank {rank}] ✓ Matriz recibida: {len(dist_matrix)}x{len(dist_matrix)}")
                    sys.stdout.flush()
                    continue
                elif tag_received == 1:
                    # Tarea
                    if isinstance(message, tuple) and len(message) == 2:
                        task_idx, task = message
                        if task_idx == -1 and task is None:
                            # Fin de lote - continuar esperando siguiente ejecución
                            print(f"[ESCLAVO Rank {rank}] Fin de lote recibido. Total tareas procesadas: {task_count}. Esperando siguiente ejecución...")
                            sys.stdout.flush()
                            task_count = 0  # Resetear contador para siguiente ejecución
                            continue
                        
                        if dist_matrix is None:
                            print(f"[ESCLAVO Rank {rank}] ⚠ ADVERTENCIA: Recibida tarea pero matriz no disponible")
                            comm.send((task_idx, (float('inf'),)), dest=0, tag=2)
                            sys.stdout.flush()
                            continue
                        
                        # Procesar tarea
                        print(f"[ESCLAVO Rank {rank}] Procesando tarea {task_idx}...")
                        sys.stdout.flush()
                        result = eval_tsp_local(task)
                        comm.send((task_idx, result), dest=0, tag=2)
                        task_count += 1
                        if task_count % 10 == 0:  # Mostrar cada 10 tareas
                            print(f"[ESCLAVO Rank {rank}] Procesadas {task_count} tareas hasta ahora...")
                            sys.stdout.flush()
            
            except Exception as e:
                import traceback
                print(f"[ESCLAVO Rank {rank}] ✗ ERROR en bucle principal: {e}")
                traceback.print_exc()
                sys.stdout.flush()
                break
        
        print(f"[ESCLAVO Rank {rank}] ===== FINALIZANDO PROCESO ESCLAVO =====")
        print(f"[ESCLAVO Rank {rank}] Total de tareas procesadas: {task_count}")
        sys.stdout.flush()
    
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
            print(f"[MAESTRO Rank {rank}] ===== INICIANDO APLICACIÓN =====")
            print(f"[MAESTRO Rank {rank}] Total de procesos MPI: {size}")
            print(f"[MAESTRO Rank {rank}] Número de esclavos: {size - 1}")
            print(f"[MAESTRO Rank {rank}] Esperando a que los esclavos se inicialicen...")
            import time
            time.sleep(1)  # Dar tiempo a que los esclavos muestren sus mensajes
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




