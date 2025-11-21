"""
Modelo: MPI Handler
Maneja la comunicación MPI entre maestro y esclavos.
"""
try:
    from mpi4py import MPI
    MPI_AVAILABLE = True
except ImportError:
    MPI_AVAILABLE = False
    MPI = None


class MPIHandler:
    """Maneja la comunicación y distribución de tareas usando MPI."""
    
    def __init__(self):
        """Inicializa el handler MPI."""
        self.comm = None
        self.rank = 0
        self.size = 1
        self.is_available = MPI_AVAILABLE
        
        if MPI_AVAILABLE:
            self.comm = MPI.COMM_WORLD
            self.rank = self.comm.Get_rank()
            self.size = self.comm.Get_size()
    
    def is_master(self):
        """Retorna True si este proceso es el maestro (rank 0)."""
        return self.rank == 0
    
    def is_slave(self):
        """Retorna True si este proceso es un esclavo (rank > 0)."""
        return self.rank > 0
    
    def get_size(self):
        """Retorna el número total de procesos."""
        return self.size
    
    def get_rank(self):
        """Retorna el rango de este proceso."""
        return self.rank
    
    def send_matrix_to_slaves(self, dist_matrix):
        """Envía la matriz de distancias a todos los esclavos."""
        if not self.is_master() or not MPI_AVAILABLE:
            return
        
        print(f"[MAESTRO] ===== ENVIANDO MATRIZ A ESCLAVOS =====")
        print(f"[MAESTRO] Tamaño de matriz: {len(dist_matrix)}x{len(dist_matrix)}")
        print(f"[MAESTRO] Enviando a {self.size - 1} esclavos (ranks 1-{self.size-1})...")
        import sys
        sys.stdout.flush()
        
        for slave_rank in range(1, self.size):
            try:
                self.comm.send(dist_matrix, dest=slave_rank, tag=100)
                print(f"[MAESTRO] ✓ Matriz enviada a esclavo {slave_rank}/{self.size-1}")
                sys.stdout.flush()
            except Exception as e:
                print(f"[MAESTRO] ✗ Error enviando matriz a esclavo {slave_rank}: {e}")
                import traceback
                traceback.print_exc()
                sys.stdout.flush()
    
    def create_mpi_map(self, dist_matrix):
        """
        Crea una función mapper personalizada para MPI.
        
        Args:
            dist_matrix: Matriz de distancias a usar en los esclavos
            
        Returns:
            Función mapper compatible con DEAP
        """
        if not MPI_AVAILABLE or self.size == 1:
            # Sin MPI o solo un proceso, usar mapper secuencial
            return map
        
        comm = self.comm
        rank = self.rank
        
        # Enviar matriz a esclavos si somos maestro
        if self.is_master():
            self.send_matrix_to_slaves(dist_matrix)
        
        def mpi_map(func, tasks):
            """
            Función mapper que distribuye tareas entre procesos MPI.
            
            Args:
                func: Función a ejecutar en cada tarea
                tasks: Lista de tareas a procesar
                
            Returns:
                Lista de resultados en el mismo orden que las tareas
            """
            # Solo el maestro ejecuta este código
            # Los esclavos procesan tareas en el bucle principal de main.py
            if rank == 0:
                # MAESTRO: Distribuir tareas y recopilar resultados
                results = [None] * len(tasks)
                task_index = 0
                workers_busy = set()
                
                # Enviar tareas iniciales a todos los esclavos
                print(f"[MAESTRO] Distribuyendo {len(tasks)} tareas entre {min(self.size-1, len(tasks))} esclavos...")
                import sys
                sys.stdout.flush()
                
                for worker_rank in range(1, min(self.size, len(tasks) + 1)):
                    if task_index < len(tasks):
                        task = list(tasks[task_index]) if hasattr(tasks[task_index], '__iter__') and not isinstance(tasks[task_index], (str, bytes)) else tasks[task_index]
                        comm.send((task_index, task), dest=worker_rank, tag=1)
                        workers_busy.add(worker_rank)
                        print(f"[MAESTRO] Tarea {task_index} enviada a esclavo {worker_rank}")
                        sys.stdout.flush()
                        task_index += 1
                
                # Recibir resultados y enviar nuevas tareas
                while len(workers_busy) > 0:
                    status = MPI.Status()
                    result_data = comm.recv(source=MPI.ANY_SOURCE, tag=2, status=status)
                    worker_rank = status.Get_source()
                    
                    if isinstance(result_data, tuple) and len(result_data) == 2:
                        task_idx, result = result_data
                        results[task_idx] = result
                        
                        # Asignar nueva tarea si hay más
                        if task_index < len(tasks):
                            task = list(tasks[task_index]) if hasattr(tasks[task_index], '__iter__') and not isinstance(tasks[task_index], (str, bytes)) else tasks[task_index]
                            comm.send((task_index, task), dest=worker_rank, tag=1)
                            task_index += 1
                        else:
                            workers_busy.remove(worker_rank)
                            # Enviar señal de fin de lote
                            comm.send((-1, None), dest=worker_rank, tag=1)
                
                return results
            else:
                # ESCLAVO: Los esclavos procesan tareas en el bucle principal de main.py
                # Este código no se ejecuta porque los esclavos no llaman a mpi_map
                # El mpi_map solo se ejecuta en el maestro
                return []  # Los esclavos no retornan resultados directamente
        
        return mpi_map
    
    def send_termination_signal(self):
        """Envía señal de terminación a todos los esclavos."""
        if not self.is_master() or not MPI_AVAILABLE:
            return
        
        print(f"[MAESTRO] Enviando señal de terminación a {self.size - 1} esclavos...")
        for slave_rank in range(1, self.size):
            try:
                self.comm.send(None, dest=slave_rank, tag=99)
            except Exception as e:
                print(f"[MAESTRO] Error enviando señal de terminación a esclavo {slave_rank}: {e}")




