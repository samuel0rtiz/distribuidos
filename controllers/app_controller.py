"""
Controlador: App Controller
Orquesta la comunicación entre modelos y vistas.
"""
import sys
import os
import threading

# Agregar ruta para importar desde raíz
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from models.genetic_algorithm import GeneticAlgorithmTSP
from models.mpi_handler import MPIHandler
from models.database import DatabaseManager
from utils.matrix_loader import MatrixLoader, create_random_matrix
from utils.mpi_config import MPIConfig
from config.config import DB_CONFIG, DEFAULT_POP_SIZE, DEFAULT_CROSSOVER_RATE, DEFAULT_MUTATION_RATE, DEFAULT_GENERATIONS


class AppController:
    """Controlador principal de la aplicación."""
    
    def __init__(self, view):
        """
        Inicializa el controlador.
        
        Args:
            view: Vista principal de la aplicación
        """
        self.view = view
        self.dist_matrix = None
        self.mpi_handler = MPIHandler()
        self.db_manager = None
        
        # Inicializar base de datos si está disponible
        try:
            self.db_manager = DatabaseManager(DB_CONFIG)
        except Exception as e:
            print(f"[ADVERTENCIA] No se pudo inicializar la base de datos: {e}")
            self.db_manager = None
        
        # Actualizar información del cluster
        self._update_cluster_info()
        
        # Cargar matriz por defecto
        self.load_default_matrix()
        
        # Configuración de MPI
        self.mpi_config = MPIConfig()
        self.current_hostfile = None
    
    def _update_cluster_info(self):
        """Actualiza la información del cluster en la vista."""
        if self.mpi_handler.is_available:
            if self.mpi_handler.is_master():
                info = f"Modo: Cluster MPI\nNodo: Maestro (Rank {self.mpi_handler.get_rank()})\nProcesos: {self.mpi_handler.get_size()}\nEsclavos: {self.mpi_handler.get_size() - 1}"
            else:
                info = f"Modo: Cluster MPI\nNodo: Esclavo (Rank {self.mpi_handler.get_rank()})\nProcesos: {self.mpi_handler.get_size()}"
        else:
            info = "Modo: Local\nProcesos: 1"
        
        self.view.update_cluster_info(info)
    
    def configure_cluster(self, num_nodes, cores_per_node, use_localhost=True):
        """
        Configura el cluster y genera el hostfile.
        
        Args:
            num_nodes: Número de nodos
            cores_per_node: Número de núcleos por nodo
            use_localhost: Si True, genera hostfile para localhost, si False, usa nombres de nodos
            
        Returns:
            Ruta al hostfile generado o None si falla
        """
        try:
            total_processes = num_nodes * cores_per_node
            
            if use_localhost:
                # Para ejecución local, usar localhost con todos los slots
                hostfile_path = self.mpi_config.generate_local_hostfile(
                    cores_per_node=total_processes,
                    hostfile_path="mpi_hostfile"
                )
            else:
                # Para cluster real, generar hostfile con nombres de nodos
                hostfile_path = self.mpi_config.generate_hostfile(
                    num_nodes=num_nodes,
                    cores_per_node=cores_per_node,
                    hostfile_path="mpi_hostfile"
                )
            
            self.current_hostfile = hostfile_path
            
            # Actualizar información del cluster
            info = f"Modo: Cluster MPI (Configurado)\nNodos: {num_nodes}\nNúcleos/nodo: {cores_per_node}\nProcesos totales: {total_processes}\nHostfile: {hostfile_path if hostfile_path else 'No generado'}"
            self.view.update_cluster_info(info)
            
            return hostfile_path
        except Exception as e:
            print(f"[ERROR] Error configurando cluster: {e}")
            return None
    
    def load_default_matrix(self):
        """Carga la matriz de distancias por defecto."""
        matrix, num_cities = MatrixLoader.load_default()
        if matrix:
            self.dist_matrix = matrix
            self.view.num_cities_var.set(str(num_cities))
            print(f"[INFO] Matriz cargada: {num_cities} ciudades")
        else:
            print("[ADVERTENCIA] No se pudo cargar la matriz por defecto")
    
    def load_matrix(self, filepath):
        """
        Carga una matriz de distancias desde archivo.
        
        Args:
            filepath: Ruta al archivo de matriz
        """
        if filepath.endswith('.json'):
            matrix, num_cities = MatrixLoader.load_from_json(filepath)
            if matrix:
                self.dist_matrix = matrix
                self.view.num_cities_var.set(str(num_cities))
                print(f"[INFO] Matriz cargada desde JSON: {num_cities} ciudades")
            else:
                self.view.show_error("Error cargando matriz desde JSON")
        else:
            matrix = MatrixLoader.load_from_file(filepath)
            if matrix:
                self.dist_matrix = matrix
                self.view.num_cities_var.set(str(len(matrix)))
                print(f"[INFO] Matriz cargada desde archivo: {len(matrix)} ciudades")
            else:
                self.view.show_error("Error cargando matriz desde archivo")
    
    def execute_algorithm(self, params):
        """
        Ejecuta el algoritmo genético con los parámetros dados.
        
        Args:
            params: Diccionario con parámetros del algoritmo
        """
        try:
            # Obtener configuración de cluster (solo informativo, no generar hostfile)
            num_nodes = params.get('num_nodes', 1)
            cores_per_node = params.get('cores_per_node', 4)
            
            # NO generar hostfile - usar el archivo 'hosts' existente
            # El sistema usa automáticamente el archivo 'hosts' en /clusterdir/distribuidos/
            
            # Verificar que tenemos una matriz
            if self.dist_matrix is None:
                # Crear matriz aleatoria si no hay una cargada
                num_cities = params.get('num_cities', 17)
                self.dist_matrix = create_random_matrix(num_cities)
                print(f"[INFO] Matriz aleatoria creada: {num_cities} ciudades")
            
            # Obtener parámetros
            pop_size = params.get('pop_size', DEFAULT_POP_SIZE)
            crossover_rate = params.get('crossover_rate', DEFAULT_CROSSOVER_RATE)
            mutation_rate = params.get('mutation_rate', DEFAULT_MUTATION_RATE)
            num_generations = params.get('generations', DEFAULT_GENERATIONS)
            
            # Crear mapper MPI si está disponible
            mpi_map = None
            if self.mpi_handler.is_available and self.mpi_handler.get_size() > 1:
                mpi_map = self.mpi_handler.create_mpi_map(self.dist_matrix)
                print(f"[INFO] Usando MPI con {self.mpi_handler.get_size()} procesos")
            else:
                print("[INFO] Ejecutando en modo secuencial")
                if num_nodes > 1 or cores_per_node > 1:
                    print("[ADVERTENCIA] La configuración de cluster se generó, pero la aplicación")
                    print("              está ejecutándose en modo local. Para usar el cluster,")
                    print("              reinicie la aplicación con mpirun usando el hostfile generado.")
            
            # Crear algoritmo genético
            ga = GeneticAlgorithmTSP(
                dist_matrix=self.dist_matrix,
                pop_size=pop_size,
                crossover_rate=crossover_rate,
                mutation_rate=mutation_rate,
                num_generations=num_generations,
                mpi_map=mpi_map
            )
            
            # Configurar callback para actualizar la vista
            def update_callback(generation, best, worst, avg, std_dev):
                """Callback para actualizar la vista después de cada generación."""
                self.view.root.after(0, self.view.update_progress, 
                                   generation, best, worst, avg, std_dev, num_generations)
            
            ga.set_callback(update_callback)
            
            # Ejecutar algoritmo
            print("[INFO] Iniciando algoritmo genético...")
            best_route, best_distance, total_time, stats = ga.run()
            
            print(f"[INFO] Algoritmo completado. Mejor distancia: {best_distance:.2f}")
            print(f"[INFO] Tiempo total: {total_time:.2f} segundos")
            
            # Guardar en base de datos si está disponible
            if self.db_manager and self.db_manager.is_available():
                execution_params = {
                    'pop_size': pop_size,
                    'crossover_rate': crossover_rate,
                    'mutation_rate': mutation_rate,
                    'num_generations': num_generations,
                    'num_cities': len(self.dist_matrix)
                }
                self.db_manager.save_execution(best_route, best_distance, execution_params)
            
            # NO enviar señal de terminación - los esclavos deben permanecer activos
            # para permitir múltiples ejecuciones
            # if self.mpi_handler.is_available and self.mpi_handler.get_size() > 1:
            #     self.mpi_handler.send_termination_signal()
            
            # Mostrar resultados finales en la vista
            self.view.root.after(0, self.view.show_final_results, 
                               best_route, best_distance, total_time)
        
        except Exception as e:
            print(f"[ERROR] Error ejecutando algoritmo: {e}")
            import traceback
            traceback.print_exc()
            self.view.root.after(0, self.view.show_error, f"Error ejecutando algoritmo: {str(e)}")




