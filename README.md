# GrafosColoreados

Aplicación de escritorio interactiva en Python para la **coloración de grafos no dirigidos** mediante un **algoritmo voraz (Welsh-Powell)**.

## Descripción

**GrafosColoreados** permite construir, visualizar y colorear grafos de hasta 12 vértices a través de una interfaz gráfica desarrollada con **PyQt6**, **NetworkX** y **Matplotlib**.

### Características principales
- **Matriz de adyacencia interactiva:** Define el número de vértices (de 1 a 12) y edita las conexiones directamente en la tabla. La matriz se mantiene simétrica automáticamente y sin lazos (grafo simple no dirigido).
- **Algoritmo voraz (Welsh-Powell):** Ordena los vértices de mayor a menor grado (desempatando por índice menor) y asigna a cada vértice el primer color disponible (del `0` al `11`) que no esté siendo utilizado por sus vecinos adyacentes.
- **Visualización en tiempo real:** Dibuja el grafo automáticamente conforme se edita la matriz y muestra los colores asignados junto con su leyenda tras ejecutar el algoritmo.
- **Registro paso a paso (Log):** Muestra en consola integrada el orden de evaluación de los vértices, el grado de cada uno, los colores prohibidos por sus vecinos, el color asignado y la validación final de la coloración.
- **Grafo de ejemplo incluido:** Permite cargar con un clic un grafo predefinido de 7 vértices y 10 aristas para pruebas rápidas.

---

## Requisitos previos

- **Python** `>= 3.14` (según la configuración en `pyproject.toml`).
- **uv** (opcional, recomendado) o **pip** con el módulo `venv`.

---

## Instalación y puesta en marcha

Puedes ejecutar el proyecto utilizando **uv** o mediante el flujo tradicional con **venv y pip**.

### Opción 1: Usando `uv` (Recomendado)

[uv](https://docs.astral.sh/uv/) gestiona automáticamente la versión de Python, el entorno virtual y las dependencias definidas en `uv.lock`.

1. **Sincronizar el entorno e instalar dependencias:**
   ```bash
   uv sync
   ```

2. **Ejecutar la aplicación:**
   ```bash
   uv run grafoscoloreados
   ```
   *(También puedes ejecutarla como módulo con `uv run python -m grafoscoloreados`).*

---

### Opción 2: Usando `venv` y `pip`

1. **Crear el entorno virtual:**
   ```bash
   python -m venv .venv
   ```

2. **Activar el entorno virtual:**
   - En **Linux / macOS**:
     ```bash
     source .venv/bin/activate
     ```
   - En **Windows (CMD)**:
     ```cmd
     .venv\Scripts\activate
     ```
   - En **Windows (PowerShell)**:
     ```powershell
     Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
     .venv\Scripts\Activate.ps1
     ```

3. **Instalar el proyecto y sus dependencias:**
   ```bash
   python -m pip install --upgrade pip # Actualizar pip, opcional
   pip install -e .  # Instalar las librerías en el entorno virtual (Importante incluir el punto '.' al final)
   ```

4. **Ejecutar la aplicación:**
   ```bash
   grafoscoloreados
   ```
   *(O bien ejecutando el módulo directamente: `python -m grafoscoloreados`).*

---

## Estructura del proyecto

```text
GrafosColoreados/
├── pyproject.toml          # Configuración del proyecto y dependencias
├── uv.lock                 # Archivo de bloqueo de dependencias para uv
├── README.md               # Documentación del proyecto
└── src/
    └── grafoscoloreados/
        ├── __init__.py     # Interfaz gráfica (PyQt6 + Matplotlib) y punto de entrada
        ├── __main__.py     # Ejecución como módulo (python -m grafoscoloreados)
        ├── classes.py      # Estructura InternalGraph y algoritmo voraz de coloración
        └── constans.py     # Constantes y paleta de colores de los nodos
```
