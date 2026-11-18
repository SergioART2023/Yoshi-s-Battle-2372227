from pathlib import Path

import pygame

from .juego import LADO, ROJO, VERDE, Estado, Posicion, jugar, movimientos_legales, nueva_partida
from .minimax import PROFUNDIDADES, elegir_movimiento
from .sprites import DIRECCIONES, cargar_gif, cargar_png, direccion_salto

CASILLA = 74
ANCHO = LADO * CASILLA
CABECERA = 72
ALTO = CABECERA + ANCHO + 42
ALTO_MENU = 430
BORDE = (202, 73, 84)
FONDO = (248, 203, 161)
TEXTO = (0, 0, 0)
COLORES = ((34, 121, 71), (164, 48, 53))
NOMBRES = ("Verde", "Rojo")
TECLAS = dict(zip((pygame.K_1, pygame.K_2, pygame.K_3), PROFUNDIDADES))
BOTONES = {
    nivel: pygame.Rect((ANCHO - 260) // 2, 242 + indice * 57, 260, 46)
    for indice, nivel in enumerate(PROFUNDIDADES)
}
RUTA_SPRITES = Path(__file__).resolve().parents[1] / "assets" / "sprites"
RUTA_ICONO = RUTA_SPRITES / "icono.png"
RUTA_FUENTE = RUTA_SPRITES.parent / "fonts" / "Mario64.ttf"


def texto(pantalla, fuente, mensaje, y):
    imagen = fuente.render(mensaje, True, TEXTO)
    pantalla.blit(imagen, imagen.get_rect(center=(ANCHO // 2, y)))


def centro(posicion: Posicion) -> tuple[int, int]:
    fila, columna = posicion
    return columna * CASILLA + CASILLA // 2, CABECERA + fila * CASILLA + CASILLA // 2


def dibujar_partida(pantalla, fuente, estado: Estado, nivel: str, piso, monedas, yoshis, direcciones, ataque, fondo_marcador, fondo_inferior, fuente_ganador, fondo_ganador):
    pantalla.fill(FONDO)
    for jugador in (VERDE, ROJO):
        rect = pygame.Rect(0, 4, 260, 32)
        rect.centerx = jugador * (ANCHO // 2) + ANCHO // 4
        if fondo_marcador is not None:
            pantalla.blit(fondo_marcador, rect)
        imagen = fuente.render(
            f"Yoshi {NOMBRES[jugador]} - {estado.puntos[jugador]}", True, COLORES[jugador]
        )
        pantalla.blit(imagen, imagen.get_rect(center=rect.center))
    if estado.terminado:
        mensaje = "Partida terminada"
    elif estado.turno == VERDE:
        mensaje = "Turno de la maquina"
    else:
        mensaje = "Tu turno - Haz clic en una casilla marcada"
    texto(pantalla, fuente, mensaje, 49)

    for fila in range(LADO):
        for columna in range(LADO):
            rect = pygame.Rect(columna * CASILLA, CABECERA + fila * CASILLA, CASILLA, CASILLA)
            pygame.draw.rect(pantalla, FONDO, rect)
            if piso is not None:
                pantalla.blit(piso, piso.get_rect(center=rect.center))

    if estado.turno == ROJO:
        for casilla in movimientos_legales(estado):
            if ataque is not None:
                pantalla.blit(ataque, ataque.get_rect(center=centro(casilla)))
                continue
            x, y = centro(casilla)
            rect = pygame.Rect(x - 24, y - 24, 48, 48)
            pygame.draw.rect(pantalla, COLORES[ROJO], rect, width=3, border_radius=6)

    tiempo = pygame.time.get_ticks()
    for casilla, valor in estado.monedas:
        animacion = monedas[valor]
        if animacion is not None:
            imagen = animacion.fotograma(tiempo)
            pantalla.blit(imagen, imagen.get_rect(center=centro(casilla)))
            continue
        color = (171, 46, 45) if valor == 3 else (140, 95, 16)
        pygame.draw.circle(pantalla, color, centro(casilla), 13)
        imagen = fuente.render(str(valor), True, TEXTO)
        pantalla.blit(imagen, imagen.get_rect(center=centro(casilla)))

    for jugador, casilla in enumerate(estado.yoshis):
        imagen = yoshis[jugador, direcciones[jugador]]
        if imagen is not None:
            pantalla.blit(imagen, imagen.get_rect(center=centro(casilla)))
            continue
        pygame.draw.circle(pantalla, COLORES[jugador], centro(casilla), 20)
        imagen = fuente.render(NOMBRES[jugador][0], True, TEXTO)
        pantalla.blit(imagen, imagen.get_rect(center=centro(casilla)))

    if fondo_inferior is not None:
        pantalla.blit(fondo_inferior, (0, CABECERA + ANCHO + 4))
    pygame.draw.rect(pantalla, BORDE, (0, CABECERA - 4, ANCHO, 4))
    pygame.draw.rect(pantalla, BORDE, (0, CABECERA + ANCHO, ANCHO, 4))
    texto(pantalla, fuente, f"{nivel.capitalize()} - Presiona ESC para volver al menu", ALTO - 21)
    if estado.terminado:
        centro_cartel = (ANCHO // 2, CABECERA + ANCHO // 2)
        rect = pygame.Rect(0, 0, ANCHO - 48, 100)
        rect.center = centro_cartel
        if fondo_ganador is None:
            pygame.draw.rect(pantalla, FONDO, rect)
        else:
            pantalla.blit(fondo_ganador, rect)
        imagen = fuente_ganador.render(
            f"Gana Yoshi {NOMBRES[estado.ganador]}", True, COLORES[estado.ganador]
        )
        rect_texto = imagen.get_rect(center=centro_cartel)
        pantalla.blit(imagen, rect_texto)
        izquierdo = yoshis[estado.ganador, "left"]
        derecho = yoshis[estado.ganador, "right"]
        if izquierdo is not None:
            pantalla.blit(
                izquierdo, izquierdo.get_rect(midright=(rect_texto.left - 8, rect.centery))
            )
        if derecho is not None:
            pantalla.blit(
                derecho, derecho.get_rect(midleft=(rect_texto.right + 8, rect.centery))
            )


def main():
    pygame.display.init()
    pygame.font.init()
    try:
        if RUTA_ICONO.is_file():
            pygame.display.set_icon(pygame.image.load(str(RUTA_ICONO)))
        pantalla = pygame.display.set_mode((ANCHO, ALTO_MENU))
        pygame.display.set_caption("Yoshi's Battle")
        ruta_fuente = str(RUTA_FUENTE) if RUTA_FUENTE.is_file() else None
        fuente = pygame.font.Font(ruta_fuente, 16)
        fuente_botones = pygame.font.Font(ruta_fuente, 20)
        fuente_ganador = pygame.font.Font(ruta_fuente, 36)
        reloj = pygame.time.Clock()
        piso = cargar_png(RUTA_SPRITES / "piso.png", CASILLA)
        ataque = cargar_png(RUTA_SPRITES / "ataque.png", CASILLA)
        titulo = cargar_png(RUTA_SPRITES / "titulo.png", 320)
        fuente_titulo = pygame.font.Font(ruta_fuente, 36)
        fondo_menu = pantalla.copy()
        fondo_menu.fill(FONDO)
        textura_boton = cargar_png(RUTA_SPRITES / "boton.png", 260)
        fondo_marcador = cargar_png(RUTA_SPRITES / "marcador.png", 260)
        fondo_inferior = None
        fondo_ganador = None
        if textura_boton is not None:
            if fondo_marcador is None:
                fondo_marcador = pygame.transform.scale(textura_boton, (260, 32))
            fondo_inferior = pygame.transform.scale(textura_boton, (ANCHO, 38))
            fondo_ganador = pygame.transform.scale(textura_boton, (ANCHO - 48, 100))
        if piso is not None:
            for y in range(0, ALTO_MENU, piso.get_height()):
                for x in range(0, ANCHO, piso.get_width()):
                    fondo_menu.blit(piso, (x, y))
        fondo_personalizado = cargar_png(RUTA_SPRITES / "fondocompleto.png", ANCHO)
        if fondo_personalizado is not None:
            fondo_menu.blit(
                fondo_personalizado,
                fondo_personalizado.get_rect(center=(ANCHO // 2, ALTO_MENU // 2)),
            )

        monedas = {
            1: cargar_gif(RUTA_SPRITES / "moneda.gif", 64),
            3: cargar_gif(RUTA_SPRITES / "monedaroja.gif", 64),
        }
        yoshis = {
            (jugador, direccion): cargar_png(
                RUTA_SPRITES / f"yoshi{nombre.lower()}{direccion}.png", CASILLA
            )
            for jugador, nombre in enumerate(NOMBRES)
            for direccion in DIRECCIONES
        }
        yoshis_menu = (
            cargar_png(RUTA_SPRITES / "yoshiverdedown.png", 111),
            cargar_png(RUTA_SPRITES / "yoshirojodown.png", 111),
        )
        direcciones = ["down", "down"]
        estado = None
        nivel = None
        inicio_verde_ms = 0

        while True:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    return
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        if estado is None:
                            return
                        estado = None
                        pantalla = pygame.display.set_mode((ANCHO, ALTO_MENU))
                if estado is None:
                    seleccion = None
                    if evento.type == pygame.KEYDOWN:
                        seleccion = TECLAS.get(evento.key)
                    elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                        seleccion = next(
                            (nombre for nombre, rect in BOTONES.items() if rect.collidepoint(evento.pos)),
                            None,
                        )
                    if seleccion is not None:
                        nivel = seleccion
                        estado = nueva_partida()
                        pantalla = pygame.display.set_mode((ANCHO, ALTO))
                        inicio_verde_ms = pygame.time.get_ticks() + 2000
                        direcciones = ["down", "down"]
                elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1 and estado.turno == ROJO:
                    x, y = evento.pos
                    destino = (y - CABECERA) // CASILLA, x // CASILLA
                    if destino in movimientos_legales(estado):
                        direcciones[ROJO] = direccion_salto(estado.yoshis[ROJO], destino)
                        estado = jugar(estado, destino)

            if estado is None:
                pantalla.blit(fondo_menu, (0, 0))
                if titulo is None:
                    texto(pantalla, fuente_titulo, "Yoshi's Battle", 112)
                else:
                    pantalla.blit(titulo, titulo.get_rect(center=(ANCHO // 2, 112)))
                texto(pantalla, fuente, "Elige la dificultad", 224)
                for imagen, x in zip(yoshis_menu, (ANCHO // 2 - 204, ANCHO // 2 + 204)):
                    if imagen is not None:
                        pantalla.blit(imagen, imagen.get_rect(center=(x, 322)))
                for numero, (nombre, rect) in enumerate(BOTONES.items(), start=1):
                    if textura_boton is None:
                        pygame.draw.rect(pantalla, FONDO, rect)
                    else:
                        pantalla.blit(textura_boton, textura_boton.get_rect(center=rect.center))
                    texto(pantalla, fuente_botones, f"{numero} - {nombre.capitalize()}", rect.centery)
            else:
                dibujar_partida(
                    pantalla, fuente, estado, nivel, piso, monedas, yoshis, direcciones,
                    ataque, fondo_marcador, fondo_inferior, fuente_ganador, fondo_ganador,
                )
            pygame.display.flip()

            if (
                estado is not None
                and estado.turno == VERDE
                and not estado.terminado
                and pygame.time.get_ticks() >= inicio_verde_ms
            ):
                destino = elegir_movimiento(estado, nivel)
                direcciones[VERDE] = direccion_salto(estado.yoshis[VERDE], destino)
                estado = jugar(estado, destino)
            reloj.tick(60)
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
