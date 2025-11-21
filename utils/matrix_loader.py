"""
Utilidades para cargar y generar matrices de distancias.
"""
import json
import os
import numpy as np
from config.config import DISTANCIAS_FILE


class MatrixLoader:
    """Cargador de matrices de distancias."""
    
    @staticmethod
    def load_from_json(filepath):
        """
        Carga una matriz de distancias desde un archivo JSON.
        
        Args:
            filepath: Ruta al archivo JSON
            
        Returns:
            Tupla (matriz, num_ciudades) o (None, 0) si falla
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                if "Distancias" in data:
                    matrix = data["Distancias"]
                    num_cities = len(matrix)
                    return matrix, num_cities
                else:
                    print(f"Error: El archivo {filepath} no contiene 'Distancias'")
                    return None, 0
        except Exception as e:
            print(f"Error cargando matriz desde {filepath}: {e}")
            return None, 0
    
    @staticmethod
    def load_default():
        """
        Carga la matriz de distancias por defecto.
        
        Returns:
            Tupla (matriz, num_ciudades) o (None, 0) si falla
        """
        if os.path.exists(DISTANCIAS_FILE):
            return MatrixLoader.load_from_json(DISTANCIAS_FILE)
        else:
            print(f"Error: No se encontró el archivo {DISTANCIAS_FILE}")
            return None, 0
    
    @staticmethod
    def load_from_file(filepath):
        """
        Carga una matriz desde un archivo de texto.
        
        Args:
            filepath: Ruta al archivo de texto
            
        Returns:
            Matriz como lista de listas o None si falla
        """
        try:
            matrix = []
            with open(filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        row = [float(x) for x in line.split()]
                        matrix.append(row)
            
            # Verificar que sea cuadrada
            n = len(matrix)
            if all(len(row) == n for row in matrix):
                return matrix
            else:
                print(f"Error: La matriz en {filepath} no es cuadrada")
                return None
        except Exception as e:
            print(f"Error cargando matriz desde {filepath}: {e}")
            return None


def create_random_matrix(num_cities):
    """
    Crea una matriz de distancias aleatoria.
    
    Args:
        num_cities: Número de ciudades
        
    Returns:
        Matriz de distancias como lista de listas
    """
    # Generar coordenadas aleatorias
    coords = np.random.rand(num_cities, 2) * 1000
    
    # Calcular matriz de distancias euclidianas
    matrix = np.zeros((num_cities, num_cities))
    for i in range(num_cities):
        for j in range(num_cities):
            if i != j:
                dist = np.sqrt(np.sum((coords[i] - coords[j])**2))
                matrix[i][j] = dist
    
    return matrix.tolist()




