# Guía de Diagnóstico: Esclavos No Muestran Procesos

## Pasos de Diagnóstico

### 1. Verificar que los esclavos se están iniciando

Ejecuta el script de prueba:
```bash
mpirun -np 20 --hostfile hosts python3 test_slaves.py
```

**Resultado esperado:**
- Deberías ver mensajes de cada esclavo indicando que se iniciaron
- Cada esclavo debería recibir un mensaje y responder

**Si NO ves mensajes de los esclavos:**
- Los esclavos no se están iniciando correctamente
- Verifica la conexión SSH
- Verifica que Python esté instalado en todos los nodos
- Verifica que el código esté en la misma ruta en todos los nodos

### 2. Verificar que el código está disponible en todos los nodos

En cada nodo esclavo, verifica:
```bash
ssh usuario@diego "ls -la /ruta/al/proyecto/bueno/"
ssh usuario@alejandro "ls -la /ruta/al/proyecto/bueno/"
ssh usuario@sam "ls -la /ruta/al/proyecto/bueno/"
ssh usuario@balam "ls -la /ruta/al/proyecto/bueno/"
```

**Debe mostrar:**
- main.py
- models/
- views/
- controllers/
- etc.

### 3. Verificar que las dependencias están instaladas

En cada nodo esclavo:
```bash
ssh usuario@diego "cd /ruta/al/proyecto/bueno && python3 -c 'import mpi4py; print(\"OK\")'"
```

Repite para cada nodo. Si falla, instala las dependencias:
```bash
ssh usuario@diego "cd /ruta/al/proyecto/bueno && pip install -r requirements.txt"
```

### 4. Verificar que MPI puede ejecutar procesos en los nodos remotos

```bash
mpirun --hostfile hosts -np 20 hostname
```

**Resultado esperado:**
- Deberías ver los nombres de los nodos repetidos según los slots

**Si falla:**
- Verifica SSH sin contraseña
- Verifica que los nombres en `hosts` coincidan con los hostnames reales
- Verifica que OpenMPI esté instalado en todos los nodos

### 5. Verificar que Python puede ejecutarse en los nodos remotos

```bash
mpirun --hostfile hosts -np 20 python3 --version
```

**Resultado esperado:**
- Deberías ver la versión de Python de cada nodo

### 6. Ejecutar el programa principal con más verbosidad

```bash
mpirun -np 20 --hostfile hosts python3 main.py 2>&1 | tee salida.log
```

Luego revisa `salida.log` para ver:
- ¿Los esclavos muestran el mensaje de inicio?
- ¿Hay errores de importación?
- ¿Los esclavos están esperando mensajes?

## Problemas Comunes

### Problema 1: Los esclavos no muestran ningún mensaje

**Causas posibles:**
1. Los esclavos no se están iniciando (problema de MPI/SSH)
2. Los esclavos fallan al importar módulos
3. Los esclavos fallan silenciosamente

**Solución:**
- Ejecuta `test_slaves.py` primero para verificar comunicación básica
- Verifica que el código esté en la misma ruta en todos los nodos
- Verifica que las dependencias estén instaladas

### Problema 2: Los esclavos muestran errores de importación

**Causas posibles:**
1. El código no está en la misma ruta en todos los nodos
2. Las dependencias no están instaladas
3. El PYTHONPATH no está configurado

**Solución:**
- Asegúrate de que el código esté en la misma ruta absoluta en todos los nodos
- Instala las dependencias en todos los nodos
- O usa un sistema de archivos compartido (NFS)

### Problema 3: Los esclavos se inician pero no reciben trabajo

**Causas posibles:**
1. El algoritmo genético no se está ejecutando
2. El maestro no está enviando tareas
3. Hay un problema en la comunicación MPI

**Solución:**
- Verifica que estés ejecutando el algoritmo desde la interfaz gráfica
- Revisa los mensajes del maestro para ver si está enviando tareas
- Verifica que el tamaño de la población sea mayor que el número de esclavos

### Problema 4: Los esclavos muestran "Esperando mensajes" pero no procesan nada

**Causas posibles:**
1. El maestro no está enviando la matriz primero
2. El maestro no está enviando tareas
3. Hay un deadlock en la comunicación

**Solución:**
- Verifica que el maestro envíe la matriz (tag 100) antes de enviar tareas
- Verifica que el algoritmo genético esté usando el mapper MPI
- Revisa los logs del maestro para ver qué está enviando

## Comandos Útiles

### Ver todos los procesos MPI en ejecución:
```bash
ps aux | grep python3 | grep main.py
```

### Matar todos los procesos MPI:
```bash
pkill -f "python3 main.py"
```

### Verificar conexiones SSH:
```bash
for nodo in diego alejandro sam balam; do
    echo "Probando $nodo..."
    ssh usuario@$nodo "echo 'OK'"
done
```

### Verificar que los nodos pueden ejecutar Python:
```bash
for nodo in diego alejandro sam balam; do
    echo "Python en $nodo:"
    ssh usuario@$nodo "python3 --version"
done
```

## Próximos Pasos

1. Ejecuta `test_slaves.py` para verificar comunicación básica
2. Si funciona, ejecuta `main.py` y revisa los mensajes
3. Si los esclavos no muestran mensajes, verifica los pasos 1-5 arriba
4. Si los esclavos muestran mensajes pero no procesan, verifica el problema 3 o 4

