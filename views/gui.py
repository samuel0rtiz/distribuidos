"""
Vista: Interfaz Gráfica Principal
Interfaz simple y funcional usando tkinter.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading


class MainWindow:
    """Ventana principal de la aplicación."""
    
    def __init__(self, root, controller):
        """
        Inicializa la ventana principal.
        
        Args:
            root: Ventana raíz de tkinter
            controller: Controlador principal de la aplicación
        """
        self.root = root
        self.controller = controller
        self.root.title("Algoritmo Genético TSP - Cluster Beowulf")
        self.root.geometry("1400x800")
        self.root.minsize(1200, 700)
        
        # Variables de estado
        self.is_running = False
        
        # Datos para gráfica
        self.generations_data = []
        self.best_fitness_data = []
        self.worst_fitness_data = []
        
        # Crear interfaz
        self._create_ui()
    
    def _create_ui(self):
        """Crea todos los componentes de la interfaz."""
        # Frame principal dividido en dos columnas
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Columna izquierda: Configuración
        config_frame = ttk.LabelFrame(main_frame, text="Configuración", padding="15")
        config_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ns")
        main_frame.grid_columnconfigure(0, weight=0)
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Columna derecha: Resultados
        results_frame = ttk.Frame(main_frame, padding="10")
        results_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        results_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_rowconfigure(0, weight=1)
        
        # Crear componentes
        self._create_config_panel(config_frame)
        self._create_results_panel(results_frame)
    
    def _create_config_panel(self, parent):
        """Crea el panel de configuración."""
        row = 0
        
        # Número de ciudades
        tk.Label(parent, text="🌺 Número de ciudades:", bg="#FFB6C1", fg="#8B008B", 
                font=("", 10)).grid(row=row, column=0, sticky="w", pady=5)
        self.num_cities_var = tk.StringVar(value="17")
        num_cities_entry = ttk.Spinbox(parent, from_=3, to=100, textvariable=self.num_cities_var, width=10)
        num_cities_entry.grid(row=row, column=1, pady=5)
        row += 1
        
        # Cargar matriz
        load_btn = ttk.Button(parent, text="🌷 Cargar Matriz", command=self._load_matrix)
        load_btn.grid(row=row, column=0, columnspan=2, pady=10, sticky="ew")
        row += 1
        
        # Separador
        tk.Frame(parent, bg="#FF69B4", height=2).grid(row=row, column=0, columnspan=2, sticky="ew", pady=10)
        row += 1
        
        # Título de parámetros
        tk.Label(parent, text="🌸 Parámetros del Algoritmo 🌸", bg="#FFB6C1", fg="#8B008B",
                font=("", 11, "bold")).grid(row=row, column=0, columnspan=2, pady=5)
        row += 1
        
        # Tamaño de población
        tk.Label(parent, text="🌹 Tamaño de población:", bg="#FFB6C1", fg="#8B008B",
                font=("", 10)).grid(row=row, column=0, sticky="w", pady=5)
        self.pop_size_var = tk.StringVar(value="50")
        pop_size_entry = ttk.Spinbox(parent, from_=10, to=1000, increment=10, 
                                     textvariable=self.pop_size_var, width=10)
        pop_size_entry.grid(row=row, column=1, pady=5)
        row += 1
        
        # Probabilidad de cruce
        tk.Label(parent, text="🌻 Prob. Recombinación:", bg="#FFB6C1", fg="#8B008B",
                font=("", 10)).grid(row=row, column=0, sticky="w", pady=5)
        self.crossover_var = tk.DoubleVar(value=0.8)
        crossover_scale = ttk.Scale(parent, from_=0.0, to=1.0, orient="horizontal",
                                    variable=self.crossover_var, length=150,
                                    command=self._update_crossover_label)
        crossover_scale.grid(row=row, column=1, pady=5, sticky="ew")
        self.crossover_label = tk.Label(parent, text="80%", bg="#FFB6C1", fg="#8B008B",
                                        font=("", 10, "bold"))
        self.crossover_label.grid(row=row, column=2, padx=5, pady=5)
        row += 1
        
        # Probabilidad de mutación
        tk.Label(parent, text="🌼 Prob. Mutación:", bg="#FFB6C1", fg="#8B008B",
                font=("", 10)).grid(row=row, column=0, sticky="w", pady=5)
        self.mutation_var = tk.DoubleVar(value=0.1)
        mutation_scale = ttk.Scale(parent, from_=0.0, to=1.0, orient="horizontal",
                                   variable=self.mutation_var, length=150,
                                   command=self._update_mutation_label)
        mutation_scale.grid(row=row, column=1, pady=5, sticky="ew")
        self.mutation_label = tk.Label(parent, text="10%", bg="#FFB6C1", fg="#8B008B",
                                       font=("", 10, "bold"))
        self.mutation_label.grid(row=row, column=2, padx=5, pady=5)
        row += 1
        
        # Número de generaciones
        tk.Label(parent, text="🌺 Número de generaciones:", bg="#FFB6C1", fg="#8B008B",
                font=("", 10)).grid(row=row, column=0, sticky="w", pady=5)
        self.generations_var = tk.StringVar(value="100")
        generations_entry = ttk.Spinbox(parent, from_=10, to=1000, increment=10,
                                       textvariable=self.generations_var, width=10)
        generations_entry.grid(row=row, column=1, pady=5)
        row += 1
        
        # Separador
        tk.Frame(parent, bg="#FF69B4", height=2).grid(row=row, column=0, columnspan=2, sticky="ew", pady=15)
        row += 1
        
        # Configuración del cluster distribuido
        cluster_config_frame = tk.LabelFrame(parent, text="🌺 Configuración del Cluster 🌺", 
                                             bg="#FFB6C1", fg="#8B008B", 
                                             font=("", 10, "bold"), padx=10, pady=10,
                                             relief="raised", bd=3)
        cluster_config_frame.grid(row=row, column=0, columnspan=2, pady=10, sticky="ew")
        row += 1
        
        # Número de nodos
        tk.Label(cluster_config_frame, text="🌹 Número de nodos:", bg="#FFB6C1", fg="#8B008B",
                font=("", 10)).grid(row=0, column=0, sticky="w", pady=5)
        self.num_nodes_var = tk.StringVar(value="1")
        num_nodes_entry = ttk.Spinbox(cluster_config_frame, from_=1, to=32, 
                                      textvariable=self.num_nodes_var, width=10)
        num_nodes_entry.grid(row=0, column=1, pady=5, padx=5)
        
        # Núcleos por nodo
        tk.Label(cluster_config_frame, text="🌻 Núcleos por nodo:", bg="#FFB6C1", fg="#8B008B",
                font=("", 10)).grid(row=1, column=0, sticky="w", pady=5)
        self.cores_per_node_var = tk.StringVar(value="4")
        cores_per_node_entry = ttk.Spinbox(cluster_config_frame, from_=1, to=64, 
                                           textvariable=self.cores_per_node_var, width=10)
        cores_per_node_entry.grid(row=1, column=1, pady=5, padx=5)
        
        # Etiqueta informativa de procesos totales
        self.total_processes_label = tk.Label(cluster_config_frame, 
                                               text="Procesos totales: 4 (1 maestro + 3 esclavos)",
                                               bg="#FFB6C1", fg="#8B008B",
                                               font=("", 9, "italic"))
        self.total_processes_label.grid(row=2, column=0, columnspan=2, pady=5)
        
        # Actualizar etiqueta cuando cambien los valores
        num_nodes_entry.config(command=self._update_total_processes)
        cores_per_node_entry.config(command=self._update_total_processes)
        self.num_nodes_var.trace('w', lambda *args: self._update_total_processes())
        self.cores_per_node_var.trace('w', lambda *args: self._update_total_processes())
        
        # Actualizar etiqueta inicialmente
        self._update_total_processes()
        
        # Separador
        tk.Frame(parent, bg="#FF69B4", height=2).grid(row=row, column=0, columnspan=2, sticky="ew", pady=15)
        row += 1
        
        # Botón de ejecución
        self.execute_btn = ttk.Button(parent, text="🌸 Ejecutar Algoritmo 🌸", command=self._on_execute)
        self.execute_btn.grid(row=row, column=0, columnspan=2, pady=10, sticky="ew")
        row += 1
        
        # Información del cluster
        cluster_frame = tk.LabelFrame(parent, text="🌺 Información del Cluster 🌺", 
                                     bg="#FFB6C1", fg="#8B008B", 
                                     font=("", 10, "bold"), padx=10, pady=10,
                                     relief="raised", bd=3)
        cluster_frame.grid(row=row, column=0, columnspan=2, pady=10, sticky="ew")
        row += 1
        
        self.cluster_info_label = tk.Label(cluster_frame, text="Modo: Local\nProcesos: 1",
                                          bg="#FFB6C1", fg="#8B008B", font=("", 9))
        self.cluster_info_label.pack()
    
    def _update_crossover_label(self, value=None):
        """Actualiza la etiqueta del porcentaje de recombinación."""
        percentage = int(self.crossover_var.get() * 100)
        self.crossover_label.config(text=f"{percentage}%", bg="#FFB6C1", fg="#8B008B")
    
    def _update_mutation_label(self, value=None):
        """Actualiza la etiqueta del porcentaje de mutación."""
        percentage = int(self.mutation_var.get() * 100)
        self.mutation_label.config(text=f"{percentage}%", bg="#FFB6C1", fg="#8B008B")
    
    def _update_total_processes(self):
        """Actualiza la etiqueta de procesos totales basado en nodos y núcleos."""
        try:
            num_nodes = int(self.num_nodes_var.get())
            cores_per_node = int(self.cores_per_node_var.get())
            total_processes = num_nodes * cores_per_node
            slaves = total_processes - 1
            if slaves > 0:
                self.total_processes_label.config(
                    text=f"Procesos totales: {total_processes} (1 maestro + {slaves} esclavos)",
                    bg="#FFB6C1", fg="#8B008B"
                )
            else:
                self.total_processes_label.config(
                    text="Procesos totales: 1 (modo local)",
                    bg="#FFB6C1", fg="#8B008B"
                )
        except ValueError:
            pass
    
    def _create_results_panel(self, parent):
        """Crea el panel de resultados."""
        # Frame para gráfica y solución
        top_frame = tk.Frame(parent, bg="#FFE4E1")
        top_frame.grid(row=0, column=0, sticky="nsew", pady=5)
        top_frame.grid_columnconfigure(0, weight=2)
        top_frame.grid_columnconfigure(1, weight=1)
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=0)
        
        # Gráfica de convergencia
        graph_frame = tk.LabelFrame(top_frame, text="🌺 Gráfica de Convergencia 🌺", 
                                    bg="#FFB6C1", fg="#8B008B", 
                                    font=("", 11, "bold"), padx=10, pady=10,
                                    relief="raised", bd=3)
        graph_frame.grid(row=0, column=0, padx=5, sticky="nsew")
        graph_frame.grid_rowconfigure(0, weight=1)
        graph_frame.grid_columnconfigure(0, weight=1)
        
        self.fig = Figure(figsize=(7, 5), dpi=100, facecolor='#FFE4E1')
        self.ax = self.fig.add_subplot(111, facecolor='#FFF0F5')
        self.ax.set_title("Evolución de la Aptitud", color='#8B008B', fontweight='bold')
        self.ax.set_xlabel("Generación", color='#8B008B')
        self.ax.set_ylabel("Distancia", color='#8B008B')
        self.ax.tick_params(colors='#8B008B')
        self.ax.grid(True, alpha=0.3, color='#FF69B4')
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        
        # Panel de solución
        solution_frame = tk.LabelFrame(top_frame, text="🌷 Solución Final 🌷", 
                                      bg="#FFB6C1", fg="#8B008B", 
                                      font=("", 11, "bold"), padx=10, pady=10,
                                      relief="raised", bd=3)
        solution_frame.grid(row=0, column=1, padx=5, sticky="nsew")
        
        # Tiempo de ejecución
        tk.Label(solution_frame, text="🌻 Tiempo de ejecución:", bg="#FFB6C1", fg="#8B008B",
                font=("", 10, "bold")).pack(anchor="w", pady=5)
        self.time_label = tk.Label(solution_frame, text="0.00 s", bg="#FFB6C1", fg="#8B008B",
                                   font=("", 14, "bold"))
        self.time_label.pack(anchor="w", pady=5)
        
        # Mejor solución
        tk.Label(solution_frame, text="🌼 Mejor Solución:", bg="#FFB6C1", fg="#8B008B",
                font=("", 10, "bold")).pack(anchor="w", pady=(10, 5))
        self.solution_text = tk.Text(solution_frame, height=15, width=35, wrap="word", 
                                    state="disabled", bg="#FFF0F5", fg="#8B008B",
                                    font=("", 9))
        self.solution_text.pack(fill="both", expand=True, pady=5)
        
        # Progreso
        tk.Label(solution_frame, text="🌸 Progreso:", bg="#FFB6C1", fg="#8B008B",
                font=("", 10, "bold")).pack(anchor="w", pady=(10, 5))
        self.progress_var = tk.DoubleVar(value=0.0)
        progress_bar = ttk.Progressbar(solution_frame, variable=self.progress_var, maximum=1.0, length=300)
        progress_bar.pack(fill="x", pady=5)
        
        # Tabla de estadísticas
        stats_frame = tk.LabelFrame(parent, text="🌺 Estadísticas por Generación 🌺", 
                                    bg="#FFB6C1", fg="#8B008B", 
                                    font=("", 11, "bold"), padx=10, pady=10,
                                    relief="raised", bd=3)
        stats_frame.grid(row=1, column=0, sticky="ew", pady=5)
        stats_frame.grid_columnconfigure(0, weight=1)
        
        columns = ("gen", "mejor", "peor", "promedio", "desv")
        self.stats_table = ttk.Treeview(stats_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.stats_table.heading(col, text=col.capitalize())
            self.stats_table.column(col, width=100, anchor="center")
        
        self.stats_table.heading("gen", text="Generación")
        self.stats_table.heading("mejor", text="Mejor")
        self.stats_table.heading("peor", text="Peor")
        self.stats_table.heading("promedio", text="Promedio")
        self.stats_table.heading("desv", text="Desv. Est.")
        
        scrollbar = ttk.Scrollbar(stats_frame, orient="vertical", command=self.stats_table.yview)
        self.stats_table.configure(yscrollcommand=scrollbar.set)
        
        self.stats_table.grid(row=0, column=0, sticky="ew")
        scrollbar.grid(row=0, column=1, sticky="ns")
    
    def _load_matrix(self):
        """Carga una matriz de distancias desde archivo."""
        filepath = filedialog.askopenfilename(
            title="Seleccionar matriz de distancias",
            filetypes=(("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*"))
        )
        if filepath:
            self.controller.load_matrix(filepath)
    
    def _on_execute(self):
        """Maneja el evento de ejecutar algoritmo."""
        if self.is_running:
            return
        
        # Obtener parámetros
        params = {
            'num_cities': int(self.num_cities_var.get()),
            'pop_size': int(self.pop_size_var.get()),
            'crossover_rate': self.crossover_var.get(),
            'mutation_rate': self.mutation_var.get(),
            'generations': int(self.generations_var.get()),
            'num_nodes': int(self.num_nodes_var.get()),
            'cores_per_node': int(self.cores_per_node_var.get())
        }
        
        # Limpiar resultados anteriores
        self.clear_results()
        
        # Ejecutar en hilo separado
        self.is_running = True
        self.execute_btn.config(state="disabled", text="Ejecutando...")
        
        thread = threading.Thread(target=self.controller.execute_algorithm, args=(params,), daemon=True)
        thread.start()
    
    def clear_results(self):
        """Limpia los resultados anteriores."""
        self.generations_data.clear()
        self.best_fitness_data.clear()
        self.worst_fitness_data.clear()
        self.stats_table.delete(*self.stats_table.get_children())
        self.solution_text.config(state="normal")
        self.solution_text.delete("1.0", tk.END)
        self.solution_text.config(state="disabled")
        self.time_label.config(text="0.00 s", bg="#FFB6C1", fg="#8B008B")
        self.progress_var.set(0.0)
        self.ax.clear()
        self.ax.set_facecolor('#FFF0F5')
        self.ax.set_title("Evolución de la Aptitud", color='#8B008B', fontweight='bold')
        self.ax.set_xlabel("Generación", color='#8B008B')
        self.ax.set_ylabel("Distancia", color='#8B008B')
        self.ax.tick_params(colors='#8B008B')
        self.ax.grid(True, alpha=0.3, color='#FF69B4')
        self.canvas.draw()
    
    def update_progress(self, generation, best, worst, avg, std_dev, total_generations):
        """
        Actualiza el progreso del algoritmo.
        
        Args:
            generation: Número de generación actual
            best: Mejor fitness
            worst: Peor fitness
            avg: Promedio de fitness
            std_dev: Desviación estándar
            total_generations: Total de generaciones
        """
        # Actualizar progreso
        progress = min(generation / total_generations, 1.0)
        self.progress_var.set(progress)
        
        # Agregar datos para gráfica
        self.generations_data.append(generation)
        self.best_fitness_data.append(best)
        self.worst_fitness_data.append(worst)
        
        # Actualizar tabla
        self.stats_table.insert("", "end", values=(
            f"{generation}",
            f"{best:.2f}",
            f"{worst:.2f}",
            f"{avg:.2f}",
            f"{std_dev:.2f}"
        ))
        self.stats_table.see(self.stats_table.get_children()[-1])
        
        # Actualizar gráfica
        self.ax.clear()
        self.ax.set_facecolor('#FFF0F5')
        if len(self.generations_data) > 0:
            self.ax.plot(self.generations_data, self.best_fitness_data, color='#FF1493', 
                        label="Mejor", linewidth=2)
            self.ax.plot(self.generations_data, self.worst_fitness_data, color='#FF69B4', 
                        label="Peor", linewidth=2)
            self.ax.legend(facecolor='#FFE4E1', edgecolor='#FF69B4')
        self.ax.set_title("Evolución de la Aptitud", color='#8B008B', fontweight='bold')
        self.ax.set_xlabel("Generación", color='#8B008B')
        self.ax.set_ylabel("Distancia", color='#8B008B')
        self.ax.tick_params(colors='#8B008B')
        self.ax.grid(True, alpha=0.3, color='#FF69B4')
        self.canvas.draw()
    
    def show_final_results(self, best_route, best_distance, total_time):
        """
        Muestra los resultados finales.
        
        Args:
            best_route: Mejor ruta encontrada
            best_distance: Mejor distancia encontrada
            total_time: Tiempo total de ejecución
        """
        # Actualizar tiempo
        self.time_label.config(text=f"{total_time:.2f} s", bg="#FFB6C1", fg="#8B008B")
        
        # Actualizar solución
        route_str = " -> ".join(str(city + 1) for city in best_route) + f" -> {best_route[0] + 1}"
        solution_text = f"Ruta: {route_str}\n\nDistancia Total: {best_distance:.2f}"
        
        self.solution_text.config(state="normal", bg="#FFF0F5", fg="#8B008B")
        self.solution_text.delete("1.0", tk.END)
        self.solution_text.insert("1.0", solution_text)
        self.solution_text.config(state="disabled")
        
        # Reactivar botón
        self.is_running = False
        self.execute_btn.config(state="normal", text="🌸 Ejecutar Algoritmo 🌸")
    
    def update_cluster_info(self, info_text):
        """
        Actualiza la información del cluster.
        
        Args:
            info_text: Texto con información del cluster
        """
        self.cluster_info_label.config(text=info_text, bg="#FFB6C1", fg="#8B008B")
    
    def show_error(self, message):
        """Muestra un mensaje de error."""
        tk.messagebox.showerror("Error", message)
        self.is_running = False
        self.execute_btn.config(state="normal", text="🌸 Ejecutar Algoritmo 🌸")

