# Guía de Configuración del Cluster Beowulf

## Requisitos Previos en TODOS los Nodos

### 1. Instalar OpenMPI
En cada nodo (diego, alejandro, sam, balam):
```bash
# En sistemas basados en Debian/Ubuntu
sudo apt-get update
sudo apt-get install openmpi-bin openmpi-common libopenmpi-dev

# En sistemas basados en Arch/Manjaro
sudo pacman -S openmpi
```

### 2. Instalar Python y Dependencias
En cada nodo:
```bash
# Instalar Python 3.8+ si no está instalado
python3 --version

# Instalar pip si no está instalado
sudo apt-get install python3-pip  # Debian/Ubuntu
# o
sudo pacman -S python-pip  # Arch/Manjaro
```

### 3. Configurar Acceso SSH sin Contraseña
**IMPORTANTE**: El nodo maestro debe poder conectarse a los esclavos sin contraseña.

En el nodo maestro (donde ejecutarás el programa):
```bash
# Generar clave SSH si no tienes una
ssh-keygen -t rsa

# Copiar la clave a cada nodo esclavo
ssh-copy-id usuario@diego
ssh-copy-id usuario@alejandro
ssh-copy-id usuario@sam
ssh-copy-id usuario@balam
```

Verificar que puedes conectarte sin contraseña:
```bash
ssh usuario@diego "echo 'Conexión exitosa'"
ssh usuario@alejandro "echo 'Conexión exitosa'"
ssh usuario@sam "echo 'Conexión exitosa'"
ssh usuario@balam "echo 'Conexión exitosa'"
```

### 4. Compartir el Código entre Nodos

Tienes dos opciones:

#### Opción A: Sistema de Archivos Compartido (NFS)
Montar el mismo directorio en todos los nodos usando NFS.

#### Opción B: Copiar el Código a Cada Nodo (Recomendado para empezar)
En el nodo maestro:
```bash
# Crear un script para copiar el código
rsync -avz --exclude 'venv' --exclude '__pycache__' \
  /ruta/al/proyecto/bueno/ usuario@diego:/ruta/destino/bueno/
rsync -avz --exclude 'venv' --exclude '__pycache__' \
  /ruta/al/proyecto/bueno/ usuario@alejandro:/ruta/destino/bueno/
rsync -avz --exclude 'venv' --exclude '__pycache__' \
  /ruta/al/proyecto/bueno/ usuario@sam:/ruta/destino/bueno/
rsync -avz --exclude 'venv' --exclude '__pycache__' \
  /ruta/al/proyecto/bueno/ usuario@balam:/ruta/destino/bueno/
```

**IMPORTANTE**: El código debe estar en la **misma ruta** en todos los nodos.

### 5. Instalar Dependencias Python en Cada Nodo
En cada nodo esclavo, ejecutar:
```bash
cd /ruta/al/proyecto/bueno
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuración del Archivo hosts

El archivo `hosts` debe estar en el nodo maestro y debe usar los nombres de host correctos:

```bash
diego slots=5
alejandro slots=5
sam slots=5
balam slots=5
```

**Nota**: Los nombres deben coincidir con los nombres de host de los nodos. Verificar con:
```bash
hostname  # En cada nodo
```

## Ejecución

### Desde el Nodo Maestro ÚNICAMENTE

1. **Asegúrate de estar en el directorio del proyecto:**
```bash
cd /ruta/al/proyecto/bueno
```

2. **Activa el entorno virtual (si usas uno):**
```bash
source venv/bin/activate
```

3. **Ejecuta el programa:**
```bash
python3 main.py
```

El sistema detectará automáticamente el archivo `hosts` y relanzará con:
```bash
mpirun -np 20 --hostfile hosts python3 main.py
```

### ¿Qué Pasa en los Esclavos?

**NO necesitas ejecutar nada manualmente en los esclavos**. Cuando ejecutas `mpirun`:

1. `mpirun` se conecta vía SSH a cada nodo esclavo
2. Lanza el proceso `python3 main.py` en cada nodo
3. Los esclavos detectan que son procesos con `rank > 0` y entran en modo esclavo
4. Esperan instrucciones del maestro (rank 0)

## Verificación

### Verificar que MPI funciona:
```bash
# Desde el nodo maestro
mpirun --hostfile hosts -np 20 hostname
```

Deberías ver los nombres de los nodos repetidos según los slots.

### Verificar que Python está disponible en todos los nodos:
```bash
mpirun --hostfile hosts -np 20 python3 --version
```

## Solución de Problemas

### Error: "Permission denied (publickey)"
- Verifica que la clave SSH esté copiada a todos los nodos
- Prueba conectarte manualmente: `ssh usuario@diego`

### Error: "No route to host"
- Verifica que los nodos estén accesibles en la red
- Verifica que los nombres de host en `hosts` sean correctos

### Error: "python3: command not found"
- Verifica que Python 3 esté instalado en todos los nodos
- Verifica que esté en el PATH

### Error: "ModuleNotFoundError"
- Verifica que las dependencias estén instaladas en todos los nodos
- Asegúrate de usar el mismo entorno virtual o instalar globalmente

### Los esclavos no reciben trabajo
- Verifica que el archivo `hosts` esté en el directorio correcto
- Verifica que los nombres de host coincidan
- Revisa los logs de MPI para ver errores de conexión

## Resumen

**En el nodo maestro:**
1. ✅ Instalar OpenMPI
2. ✅ Instalar Python y dependencias
3. ✅ Configurar SSH sin contraseña
4. ✅ Tener el código del proyecto
5. ✅ Ejecutar: `python3 main.py`

**En los nodos esclavos:**
1. ✅ Instalar OpenMPI
2. ✅ Instalar Python y dependencias
3. ✅ Permitir conexión SSH desde el maestro
4. ✅ Tener el código del proyecto en la misma ruta
5. ✅ **NO ejecutar nada manualmente** - `mpirun` lo hace automáticamente

