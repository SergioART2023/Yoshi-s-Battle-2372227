# Yoshi's Battle

Juego de adversarios desarrollado en Python y Pygame para el Proyecto 2 de Inteligencia Artificial de la Universidad del Valle. El jugador controla al Yoshi rojo y compite contra el Yoshi verde mediante Minimax con poda alfa-beta.

## Requisitos

- Python 3.12.
- Una pantalla con espacio para una ventana de 592 × 706 píxeles.
- Pygame 2.6.1 y Pillow 12.2.0, incluidos en requirements.txt.

## Instalación en Windows

Clona el repositorio y entra en su carpeta.

```powershell
git clone https://github.com/SergioART2023/Yoshi-s-Battle-2372227.git
cd Yoshi-s-Battle-2372227
```

Si ya tienes el proyecto, abre una terminal en la carpeta que contiene requirements.txt. Crea el entorno virtual e instala las dependencias.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Cómo ejecutar el juego

Desde la carpeta del proyecto, ejecuta el módulo principal.

```powershell
.\.venv\Scripts\python.exe -m src.main
```

Estos comandos usan directamente el Python del entorno virtual y pueden ejecutarse sin activar el entorno.

Si aparece un error como "No Python at ...", el entorno apunta a una instalación de Python que ya no está disponible. Con Python 3.12 instalado, reconstruye el entorno y reinstala las dependencias.

```powershell
py -3.12 -m venv --clear .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m src.main
```

## Controles

| Acción | Control |
|---|---|
| Elegir dificultad | Clic en el botón o teclas 1, 2 y 3 |
| Mover al Yoshi rojo | Clic en una casilla señalada con el indicador de ataque |
| Volver al menú | Esc durante la partida |
| Cerrar el juego | Esc desde el menú o cerrar la ventana |

Al iniciar una partida hay una espera de dos segundos antes de la primera jugada de la máquina.

## Reglas

- El tablero tiene 8 × 8 casillas.
- Ambos Yoshis se mueven como un caballo de ajedrez, dos casillas sobre un eje y una sobre el otro.
- La máquina juega con el Yoshi verde y siempre comienza.
- Los Yoshis nunca pueden ocupar la misma casilla.
- Las cuatro monedas rojas ocupan el centro y otorgan tres puntos cada una.
- Las nueve monedas normales se distribuyen al azar y otorgan un punto cada una.
- Las posiciones iniciales de los Yoshis son aleatorias y están libres de monedas.
- Los jugadores alternan sus turnos. Las monedas se recogen al aterrizar sobre ellas y el marcador muestra los puntos acumulados.
- La partida termina al recoger todas las monedas. Gana quien obtenga más puntos y se muestra un cartel con el Yoshi ganador.

## Inteligencia artificial

| Nivel | Tecla | Profundidad |
|---|---|---|
| Principiante | 1 | 2 |
| Intermedio | 2 | 4 |
| Experto | 3 | 6 |

Cada nivel de profundidad representa un movimiento de uno de los jugadores. El verde maximiza la utilidad y el rojo la minimiza. La poda alfa-beta descarta ramas que no pueden mejorar la decisión actual.

Al alcanzar el límite de búsqueda, la heurística combina la diferencia de puntos con la proximidad de ambos Yoshis a las monedas restantes, ponderada por el valor de cada moneda. La distancia corresponde al mínimo de saltos de caballo, sin considerar al rival como obstáculo. La contribución de proximidad se normaliza para que pese menos que un punto obtenido. En estados finales, la utilidad es +22 si gana el verde y −22 si gana el rojo.

## Organización del proyecto

| Ruta | Contenido |
|---|---|
| assets/fonts/ | Fuente del juego |
| assets/sprites/ | Yoshis, monedas GIF y elementos de la interfaz |
| src/juego.py | Estados, movimientos, turnos y puntuación |
| src/minimax.py | Búsqueda alfa-beta y evaluación heurística |
| src/sprites.py | Carga, escalado proporcional y animación |
| src/main.py | Menú, tablero e interacción con Pygame |
| tests/ | Pruebas del motor y de Minimax |
| requirements.txt | Dependencias |

Los recursos se cargan desde assets con rutas relativas a los archivos del programa. Los sprites se amplían con escalas enteras y conservan su proporción. Las monedas GIF mantienen su animación durante la partida.

## Pruebas

Desde la carpeta del proyecto, ejecuta:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Las pruebas comprueban la distribución inicial, los saltos legales, la recolección de monedas, los turnos, el ganador y las decisiones de Minimax en las tres profundidades.
