"""
Modelo: Database Manager
Maneja todas las operaciones de base de datos.
"""
import json
import sys
import os

# Agregar ruta para importar desde Core
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'Core'))

try:
    from Core.db import (
        get_connection, init_db, guardar_resultado, 
        obtener_historial, set_db_config
    )
    CORE_DB_AVAILABLE = True
except ImportError:
    # Si no está disponible, crear versión simplificada
    CORE_DB_AVAILABLE = False


class DatabaseManager:
    """Gestor de base de datos para el sistema."""
    
    def __init__(self, config):
        """
        Inicializa el gestor de base de datos.
        
        Args:
            config: Diccionario con configuración de BD (host, user, password, database, port)
        """
        self.config = config
        self.ejecucion_id = None
        
        if CORE_DB_AVAILABLE:
            # Configurar y inicializar BD usando Core.db
            set_db_config(self.config)
            init_db(self.config)
        else:
            print("[ADVERTENCIA] Core.db no disponible, base de datos deshabilitada")
    
    def save_execution(self, best_route, best_distance, parameters):
        """
        Guarda una ejecución del algoritmo en la base de datos.
        
        Args:
            best_route: Mejor ruta encontrada
            best_distance: Mejor distancia encontrada
            parameters: Parámetros de la ejecución
            
        Returns:
            ID de la ejecución guardada o None si falla
        """
        if not CORE_DB_AVAILABLE:
            print("[ADVERTENCIA] Base de datos no disponible, no se guardó la ejecución")
            return None
        
        mejor_individuo = {
            "ruta": best_route,
            "distancia": best_distance
        }
        
        ejecucion_id = guardar_resultado(
            mejor_individuo, 
            best_distance, 
            parameters, 
            self.config
        )
        
        if ejecucion_id:
            self.ejecucion_id = ejecucion_id
            print(f"[BD] Ejecución guardada con ID: {ejecucion_id}")
        
        return ejecucion_id
    
    def get_history(self, limit=50):
        """
        Obtiene el historial de ejecuciones.
        
        Args:
            limit: Número máximo de resultados a retornar
            
        Returns:
            Lista de ejecuciones guardadas
        """
        if not CORE_DB_AVAILABLE:
            return []
        
        return obtener_historial(limit, self.config)
    
    def is_available(self):
        """Retorna True si la base de datos está disponible."""
        return CORE_DB_AVAILABLE




