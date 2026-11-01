# Space Defender 2D

Proyecto de juego 2D desarrollado con Python y Pygame.

## Requisitos

- Python 3.10 o posterior para Windows, macOS o Linux.
- Conexión a Internet en la primera ejecución para instalar Pygame CE.

## Instalación y ejecución rápida

Descarga o copia la carpeta completa del proyecto a cualquier ubicación. No
copies el entorno `.venv` de otra computadora: los entornos virtuales dependen
del sistema operativo, la versión de Python y la ruta donde se crearon. La
carpeta del proyecto debe permitir escritura para que el iniciador pueda crear
su entorno local e instalar el juego automáticamente la primera vez:

```powershell
.\run_game.bat
```

En macOS o Linux:

```sh
sh ./run_game.sh
```

Se requiere conexión a Internet durante la primera ejecución para descargar
las dependencias definidas en `pyproject.toml`. Las ejecuciones siguientes
usan el entorno local y no necesitan reinstalar el juego.

## Instalación manual

Desde la carpeta del proyecto, crea un entorno virtual e instala el juego:

```sh
python3 -m venv .venv
```

En Windows, usa `py -3 -m venv .venv` si el lanzador `py` está instalado.
Después activa el entorno e instala el proyecto con `python -m pip install -e .`,
o ejecuta directamente el intérprete del entorno:

```powershell
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m spacedefender
```

En macOS o Linux:

```sh
.venv/bin/python -m pip install -e .
.venv/bin/python -m spacedefender
```

La carpeta `.venv` no es portable ni debe compartirse entre equipos; cada
máquina debe crear la suya. No es necesario activar el entorno para usar los
lanzadores.

## Características

El fondo espacial incluye estrellas lejanas y dos planetas pequeños y tenues
para dar la impresión de que están a gran distancia.
El nivel 2 se juega sobre un océano al atardecer, con islas y embarcaciones en
el horizonte.
Las naves, proyectiles y cargas usan bordes suavizados y más detalles de luz y
volumen para que sus formas se distingan mejor durante el combate.
El audio se genera al iniciar: incluye efectos para los disparos, música de
suspenso durante las batallas, redobles al completar los niveles 1 y 2, y
fuegos artificiales con una melodía de triunfo al terminar el nivel 3. No se
requieren archivos de sonido adicionales.

El nivel 1 presenta tres oleadas de cinco Troyanos. Al destruir una oleada,
aparece la siguiente. Los Troyanos se desplazan de lado a lado, descienden al
tocar los bordes y disparan hacia Hércules. Cuando destruye las tres oleadas,
aparece Vulcano. Su duración depende del tiempo que tardes en eliminar a los
Troyanos; no hay un temporizador fijo. Vulcano se desplaza y dispara más rápido,
apuntando a Hércules; sus proyectiles solo dañan al héroe y necesita recibir
diez impactos para ser destruido.

Muévete con **WASD** o las **flechas** y dispara con **espacio**. Mantén espacio
para disparar repetidamente. Las mejoras de energía permiten disparos dobles y
triples; cada proyectil acertado cuenta como un impacto individual contra
Vulcano.

Desde el inicio, Hércules recibe una cápsula de combate: activa cuatro torretas
y dispara dos misiles adicionales cada cinco disparos normales. Usa
**espacio + Shift** para lanzar un láser; cada impacto resta dos puntos de
resistencia a la Medusa final.

Al derrotar a Vulcano, Hércules recibe una transformación de energía: su nave
se alarga, gana dos cañones en las alas y aumenta ligeramente su velocidad. Así
recupera una vida si había perdido alguna (hasta sus tres vidas iniciales) y
comienza el nivel 2, con tres
oleadas de dos filas de cinco Troyanos. Después de destruir las tres oleadas,
aparecen dos Vulcanos; cada uno necesita diez
impactos para ser derrotado. Al destruir a ambos aparece **YOU WIN! NEXT LEVEL!**.
Al completar el nivel 2 para pasar al tercero, Hércules recibe tres vidas extra.

El nivel 3 es la batalla final sobre una ciudad terrestre al atardecer, con
edificios, horizonte y carreteras. Hércules combate cinco oleadas de Troyanos,
seguidas por dos oleadas de Vulcanos (uno por oleada). Después aparece la
Medusa, una nave nodriza que se mueve, dispara y necesita veinte impactos para
explotar. Al destruirla, aparece **YOU WIN THE GAME!**.

La partida termina si los Troyanos alcanzan la altura de Hércules o si se
destruyen sus tres naves. Hércules empieza con una nave y dos de reserva; cada
impacto de un disparo enemigo consume una nave y la siguiente reaparece en su
posición inicial. Tras reaparecer, tiene un breve período de invulnerabilidad.
El HUD muestra cuántas naves quedan y, al perder la última, aparece **GAME OVER**.
Cada minuto aproximadamente aparece una carga aleatoria que cae desde arriba:
la de energía mejora la velocidad y las armas de Hércules, y la de escudo lo
protege de los disparos Troyanos durante 10 segundos. Recoge una carga tocándola
con la nave. También pueden aparecer pociones al azar; cada una agrega una vida
extra. El HUD muestra el nivel de armas, la velocidad, las vidas y el tiempo de
escudo restante.
Cierra la ventana para salir.

## Estructura

```text
assets/
  fonts/
  images/
  sounds/
src/
  spacedefender/
    background.py
    enemy.py
    enemy_projectile.py
    level.py
    mothership.py
    player.py
    power_up.py
    projectile.py
    vulcano.py
    main.py
tests/
run_game.bat
run_game.sh
pyproject.toml
```
