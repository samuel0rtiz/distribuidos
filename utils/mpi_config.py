"""
Utilidades para configuración de MPI y generación de hostfiles.
"""
import os


class MPIConfig:
    """Maneja la configuración de MPI y generación de hostfiles."""
    
    @staticmethod
    def generate_hostfile(num_nodes, cores_per_node, hostfile_path="mpi_hostfile", 
                         hostname_prefix="node", start_index=1):
        """
        Genera un archivo hostfile para MPI.
        
        Args:
            num_nodes: Número de nodos
            cores_per_node: Número de núcleos por nodo
            hostfile_path: Ruta donde guardar el hostfile
            hostname_prefix: Prefijo para los nombres de host (ej: "node" -> node1, node2, ...)
            start_index: Índice inicial para los nombres de host (por defecto 1)
            
        Returns:
            Ruta al archivo hostfile generado
        """
        try:
            with open(hostfile_path, 'w') as f:
                for i in range(num_nodes):
                    node_name = f"{hostname_prefix}{i + start_index}"
                    f.write(f"{node_name} slots={cores_per_node}\n")
            
            print(f"[INFO] Hostfile generado: {hostfile_path}")
            print(f"[INFO] Configuración: {num_nodes} nodos x {cores_per_node} núcleos = {num_nodes * cores_per_node} procesos")
            return hostfile_path
        except Exception as e:
            print(f"[ERROR] Error generando hostfile: {e}")
            return None
    
    @staticmethod
    def generate_local_hostfile(cores_per_node, hostfile_path="mpi_hostfile_local"):
        """
        Genera un hostfile para ejecución local (localhost).
        
        Args:
            cores_per_node: Número de núcleos a usar
            hostfile_path: Ruta donde guardar el hostfile
            
        Returns:
            Ruta al archivo hostfile generado
        """
        try:
            with open(hostfile_path, 'w') as f:
                f.write(f"localhost slots={cores_per_node}\n")
            
            print(f"[INFO] Hostfile local generado: {hostfile_path}")
            return hostfile_path
        except Exception as e:
            print(f"[ERROR] Error generando hostfile local: {e}")
            return None
    
    @staticmethod
    def get_total_processes(num_nodes, cores_per_node):
        """
        Calcula el número total de procesos.
        
        Args:
            num_nodes: Número de nodos
            cores_per_node: Número de núcleos por nodo
            
        Returns:
            Número total de procesos
        """
        return num_nodes * cores_per_node
    
    @staticmethod
    def get_hostfile_info(hostfile_path):
        """
        Lee información de un hostfile existente.
        
        Args:
            hostfile_path: Ruta al hostfile
            
        Returns:
            Diccionario con información del hostfile o None si no existe
        """
        if not os.path.exists(hostfile_path):
            return None
        
        try:
            total_slots = 0
            nodes = []
            
            with open(hostfile_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split()
                        if len(parts) >= 2:
                            node_name = parts[0]
                            slots = int(parts[1].split('=')[1])
                            total_slots += slots
                            nodes.append({'name': node_name, 'slots': slots})
            
            return {
                'total_slots': total_slots,
                'num_nodes': len(nodes),
                'nodes': nodes
            }
        except Exception as e:
            print(f"[ERROR] Error leyendo hostfile: {e}")
            return None

