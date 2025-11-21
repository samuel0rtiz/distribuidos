"""
Configuración centralizada del sistema.
"""
import os

# Configuración de Base de Datos
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "aguser"),
    "password": os.getenv("DB_PASSWORD", "password123"),
    "database": os.getenv("DB_NAME", "base_de_datos_replicacion"),
    "port": int(os.getenv("DB_PORT", "3306"))
}

# Configuración de MPI
MPI_ENABLED = True  # Se detectará automáticamente si mpi4py está disponible

# Rutas de archivos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DISTANCIAS_FILE = os.path.join(DATA_DIR, "distancias.json")

# Configuración por defecto del algoritmo
DEFAULT_POP_SIZE = 50
DEFAULT_CROSSOVER_RATE = 0.8
DEFAULT_MUTATION_RATE = 0.1
DEFAULT_GENERATIONS = 100




