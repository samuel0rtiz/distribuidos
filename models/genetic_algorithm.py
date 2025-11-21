"""
Modelo: Algoritmo Genético TSP
Contiene toda la lógica del algoritmo genético para resolver TSP.
"""
import random
import numpy as np
from deap import algorithms, base, creator, tools

try:
    from mpi4py import MPI
    MPI_AVAILABLE = True
except ImportError:
    MPI_AVAILABLE = False
    MPI = None


# Configurar DEAP solo una vez
if not hasattr(creator, "FitnessMin"):
    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
if not hasattr(creator, "Individual"):
    creator.create("Individual", list, fitness=creator.FitnessMin)


class GeneticAlgorithmTSP:
    """Algoritmo Genético para resolver el problema del Viajero de Comercio (TSP)."""
    
    def __init__(self, dist_matrix, pop_size=50, crossover_rate=0.8, 
                 mutation_rate=0.1, num_generations=100, mpi_map=None):
        """
        Inicializa el algoritmo genético.
        
        Args:
            dist_matrix: Matriz de distancias entre ciudades
            pop_size: Tamaño de la población
            crossover_rate: Probabilidad de cruce
            mutation_rate: Probabilidad de mutación
            num_generations: Número de generaciones
            mpi_map: Función mapper para MPI (opcional)
        """
        self.dist_matrix = dist_matrix
        self.num_cities = len(dist_matrix)
        self.pop_size = pop_size
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.num_generations = num_generations
        
        # Configurar toolbox
        self.toolbox = base.Toolbox()
        self._setup_toolbox(mpi_map)
        
        # Estadísticas para callback
        self.callback = None
    
    def _setup_toolbox(self, mpi_map=None):
        """Configura las operaciones genéticas en el toolbox."""
        # Crear individuos y población
        self.toolbox.register("indices", random.sample, range(self.num_cities), self.num_cities)
        self.toolbox.register("individual", tools.initIterate, creator.Individual, self.toolbox.indices)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        
        # Operadores genéticos
        self.toolbox.register("mate", tools.cxOrdered)
        self.toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.05)
        self.toolbox.register("select", tools.selTournament, tournsize=3)
        self.toolbox.register("evaluate", self._eval_tsp)
        
        # Mapper (paralelo si hay MPI, secuencial si no)
        if mpi_map:
            self.toolbox.register("map", mpi_map)
        else:
            self.toolbox.register("map", map)
    
    def _eval_tsp(self, individual):
        """
        Evalúa un individuo calculando la distancia total del recorrido.
        
        Args:
            individual: Lista que representa el orden de visita de ciudades
            
        Returns:
            Tupla con la distancia total
        """
        distance = self.dist_matrix[individual[-1]][individual[0]]  # Regreso al inicio
        for gene1, gene2 in zip(individual[0:-1], individual[1:]):
            distance += self.dist_matrix[gene1][gene2]
        return distance,
    
    def set_callback(self, callback):
        """Establece una función callback para actualizar la interfaz después de cada generación."""
        self.callback = callback
    
    def run(self):
        """
        Ejecuta el algoritmo genético.
        
        Returns:
            Tupla (mejor_ruta, mejor_distancia, tiempo_total, estadisticas)
        """
        import time
        start_time = time.time()
        
        # Inicializar población
        random.seed(42)
        population = self.toolbox.population(n=self.pop_size)
        
        # Configurar estadísticas
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", np.mean)
        stats.register("std", np.std)
        stats.register("min", np.min)
        stats.register("max", np.max)
        
        # Hall of Fame para guardar el mejor
        hof = tools.HallOfFame(1)
        
        # Logbook para estadísticas
        logbook = tools.Logbook()
        
        # Evaluar población inicial
        fitnesses = list(self.toolbox.map(self.toolbox.evaluate, population))
        for ind, fit in zip(population, fitnesses):
            ind.fitness.values = fit
        
        # Registrar estadísticas iniciales
        record = stats.compile(population)
        logbook.record(gen=0, **record)
        
        # Llamar callback si existe
        if self.callback:
            best = min(ind.fitness.values[0] for ind in population)
            worst = max(ind.fitness.values[0] for ind in population)
            avg = np.mean([ind.fitness.values[0] for ind in population])
            std = np.std([ind.fitness.values[0] for ind in population])
            self.callback(0, best, worst, avg, std)
        
        # Evolución generacional
        for generation in range(1, self.num_generations + 1):
            # Seleccionar próxima generación
            offspring = self.toolbox.select(population, len(population))
            offspring = list(map(self.toolbox.clone, offspring))
            
            # Aplicar cruce
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < self.crossover_rate:
                    self.toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values
            
            # Aplicar mutación
            for mutant in offspring:
                if random.random() < self.mutation_rate:
                    self.toolbox.mutate(mutant)
                    del mutant.fitness.values
            
            # Evaluar individuos sin fitness
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = list(self.toolbox.map(self.toolbox.evaluate, invalid_ind))
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit
            
            # Actualizar población
            population[:] = offspring
            
            # Actualizar Hall of Fame
            hof.update(population)
            
            # Registrar estadísticas
            record = stats.compile(population)
            logbook.record(gen=generation, **record)
            
            # Llamar callback si existe
            if self.callback:
                best = min(ind.fitness.values[0] for ind in population)
                worst = max(ind.fitness.values[0] for ind in population)
                avg = np.mean([ind.fitness.values[0] for ind in population])
                std = np.std([ind.fitness.values[0] for ind in population])
                self.callback(generation, best, worst, avg, std)
        
        # Obtener mejor solución
        best_individual = hof[0]
        best_route = list(best_individual)
        best_distance = best_individual.fitness.values[0]
        
        total_time = time.time() - start_time
        
        # Convertir estadísticas a lista de diccionarios
        stats_list = []
        for entry in logbook:
            stats_list.append({
                'generation': entry['gen'],
                'best': entry['min'],
                'worst': entry['max'],
                'avg': entry['avg'],
                'std': entry['std']
            })
        
        return best_route, best_distance, total_time, stats_list




