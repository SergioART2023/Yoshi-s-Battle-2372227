from bisect import bisect_right
from dataclasses import dataclass
from pathlib import Path

import pygame
from PIL import Image, ImageSequence

from .juego import Posicion

DIRECCIONES = ("up", "down", "left", "right")


@dataclass(frozen=True)
class Animacion:
    imagenes: tuple[pygame.Surface, ...]
    finales_ms: tuple[int, ...]

    def fotograma(self, tiempo_ms: int) -> pygame.Surface:
        fase = tiempo_ms % self.finales_ms[-1]
        return self.imagenes[bisect_right(self.finales_ms, fase)]


def direccion_salto(origen: Posicion, destino: Posicion) -> str:
    filas = destino[0] - origen[0]
    columnas = destino[1] - origen[1]
    if abs(filas) > abs(columnas):
        return "down" if filas > 0 else "up"
    return "right" if columnas > 0 else "left"


def _escalar(imagen: pygame.Surface, tamano: int) -> pygame.Surface:
    ancho, alto = imagen.get_size()
    factor = tamano / max(ancho, alto)
    medidas = max(1, round(ancho * factor)), max(1, round(alto * factor))
    if factor < 1:
        return pygame.transform.smoothscale(imagen, medidas)
    return pygame.transform.scale(imagen, medidas)


def cargar_png(ruta: Path, tamano: int) -> pygame.Surface | None:
    if not ruta.is_file():
        return None
    imagen = pygame.image.load(str(ruta)).convert_alpha()
    return _escalar(imagen, tamano)


def cargar_gif(ruta: Path, tamano: int) -> Animacion | None:
    if not ruta.is_file():
        return None

    imagenes = []
    finales_ms = []
    acumulado = 0
    with Image.open(ruta) as gif:
        for cuadro in ImageSequence.Iterator(gif):
            rgba = cuadro.convert("RGBA")
            superficie = pygame.image.frombytes(rgba.tobytes(), rgba.size, "RGBA")
            imagenes.append(_escalar(superficie.convert_alpha(), tamano))
            acumulado += cuadro.info.get("duration") or 100
            finales_ms.append(acumulado)
    return Animacion(tuple(imagenes), tuple(finales_ms))
