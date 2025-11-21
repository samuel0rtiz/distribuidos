# Sistema de Algoritmo Genético TSP - Cluster Beowulf

Sistema completo para resolver el problema del Viajero de Comercio (TSP) usando Algoritmos Genéticos distribuidos en un Cluster Beowulf con MPI.

## Arquitectura MVC

El sistema está organizado siguiendo el patrón Modelo-Vista-Controlador:

```
bueno/
├── models/           # Lógica de negocio
│   ├── genetic_algorithm.py   # Algoritmo genético
│   ├── mpi_handler.py         # Manejo de MPI
│   └── database.py            # Gestión de base de datos
├── views/            # Interfaz gráfica
│   └── gui.py                 # Ventana principal
├── controllers/      # Controladores
│   └── app_controller.py      # Controlador principal
├── utils/            # Utilidades
│   └── matrix_loader.py       # Carga de matrices
├── config/           # Configuración
│   └── config.py              # Configuración centralizada
├── data/             # Datos
│   └── distancias.json        # Matriz de distancias
└── main.py           # Punto de entrada
```

## Requisitos

- Python 3.8+
- OpenMPI (para ejecución distribuida)
- MySQL (opcional, para guardar resultados)

## Instalación

1. Crear entorno virtual:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Ejecución

### Modo Local (sin MPI):
```bash
python3 main.py
```

### Modo Distribuido (con MPI) - Automático:
El sistema detecta automáticamente el archivo `hosts` y se relanza con MPI:
```bash
python3 main.py
```

Esto ejecutará automáticamente:
```bash
mpirun -np 20 --hostfile hosts python3 main.py
```

### Configuración del Cluster

**IMPORTANTE**: Para ejecutar con esclavos remotos, ver la guía completa en [CLUSTER_SETUP.md](CLUSTER_SETUP.md)

**Resumen rápido:**
1. **En el nodo maestro**: Solo ejecuta `python3 main.py`
2. **En los nodos esclavos**: NO necesitas ejecutar nada manualmente
3. **Requisitos**:
   - SSH sin contraseña configurado desde el maestro a los esclavos
   - Código disponible en la misma ruta en todos los nodos
   - OpenMPI y Python instalados en todos los nodos
   - Dependencias Python instaladas en todos los nodos

**Scripts de ayuda:**
- `./setup_cluster.sh` - Configura y copia código a los nodos
- `./test_cluster.sh` - Prueba la configuración del cluster

## Uso

1. Configura el número de ciudades (o carga una matriz desde archivo)
2. Ajusta los parámetros del algoritmo:
   - Tamaño de población
   - Probabilidad de recombinación
   - Probabilidad de mutación
   - Número de generaciones
3. Haz clic en "Ejecutar Algoritmo"
4. Observa la evolución en tiempo real

## Características

- ✅ Arquitectura MVC limpia y organizada
- ✅ Soporte para MPI (cluster Beowulf)
- ✅ Interfaz gráfica simple y funcional
- ✅ Visualización de convergencia en tiempo real
- ✅ Guardado de resultados en base de datos (opcional)
- ✅ Sin dependencias de temas complejos

## Configuración de Base de Datos

Edita `config/config.py` para configurar la conexión a MySQL (opcional).

## Licencia

Este proyecto es para fines educativos.




