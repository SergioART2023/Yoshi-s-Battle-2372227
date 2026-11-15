from pathlib import Path

import pygame

from .juego import LADO, ROJO, VERDE, Estado, Posicion, jugar, movimientos_legales, nueva_partida
from .minimax import PROFUNDIDADES, elegir_movimiento
from .sprites import DIRECCIONES, cargar_gif, cargar_png, direccion_salto

CASILLA = 56
ANCHO = LADO * CASILLA
CABECERA = 72
ALTO = CABECERA + ANCHO + 42
FONDO = (23, 34, 31)
TEXTO = (248, 244, 226)
PISO = ((236, 218, 176), (205, 180, 134))
COLORES = ((34, 121, 71), (164, 48, 53))
NOMBRES = ("Verde", "Rojo")
TECLAS = dict(zip((pygame.K_1, pygame.K_2, pygame.K_3), PROFUNDIDADES))
BOTONES = {
    nivel: pygame.Rect((ANCHO - 260) // 2, 242 + indice * 57, 260, 46)
    for indice, nivel in enumerate(PROFUNDIDADES)
}
RUTA_SPRITES = Path(__file__).resolve().parents[1] / "assets" / "sprites"


def texto(pantalla, fuente, mensaje, y):
    imagen = fuente.render(mensaje, True, TEXTO)
    pantalla.blit(imagen, imagen.get_rect(center=(ANCHO // 2, y)))


def centro(posicion: Posicion) -> tuple[int, int]:
    fila, columna = posicion
    return columna * CASILLA + CASILLA // 2, CABECERA + fila * CASILLA + CASILLA // 2


def dibujar_partida(pantalla, fuente, estado: Estado, nivel: str, piso, monedas, yoshis, direcciones):
    pantalla.fill(FONDO)
    texto(pantalla, fuente, f"Verde {estado.puntos[VERDE]}     Rojo {estado.puntos[ROJO]}", 20)
    if estado.terminado:
        mensaje = f"Gana el Yoshi {NOMBRES[estado.ganador].lower()}"
    elif estado.turno == VERDE:
        mensaje = "Turno de la máquina"
    else:
        mensaje = "Tu turno · Haz clic en una casilla marcada"
    texto(pantalla, fuente, mensaje, 49)

    for fila in range(LADO):
        for columna in range(LADO):
            rect = pygame.Rect(columna * CASILLA, CABECERA + fila * CASILLA, CASILLA, CASILLA)
            pygame.draw.rect(pantalla, PISO[(fila + columna) % 2], rect)
            if piso is not None:
                pantalla.blit(piso, rect)

    if estado.turno == ROJO:
        for casilla in movimientos_legales(estado):
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

    texto(pantalla, fuente, f"{nivel.capitalize()} · Esc para volver al menú", ALTO - 21)


def main():
    pygame.display.init()
    pygame.font.init()
    try:
        pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("Yoshi's Battle")
        titulo = pygame.font.Font(None, 52)
        fuente = pygame.font.Font(None, 25)
        reloj = pygame.time.Clock()
        piso = cargar_png(RUTA_SPRITES / "piso.png", CASILLA, baldosa=True)
        monedas = {
            1: cargar_gif(RUTA_SPRITES / "moneda.gif", 30),
            3: cargar_gif(RUTA_SPRITES / "monedaroja.gif", 30),
        }
        yoshis = {
            (jugador, direccion): cargar_png(
                RUTA_SPRITES / f"yoshi{nombre.lower()}{direccion}.png", 48
            )
            for jugador, nombre in enumerate(NOMBRES)
            for direccion in DIRECCIONES
        }
        direcciones = ["down", "down"]
        estado = None
        nivel = None

        while True:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    return
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        if estado is None:
                            return
                        estado = None
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
                        direcciones = ["down", "down"]
                elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1 and estado.turno == ROJO:
                    x, y = evento.pos
                    destino = (y - CABECERA) // CASILLA, x // CASILLA
                    if destino in movimientos_legales(estado):
                        direcciones[ROJO] = direccion_salto(estado.yoshis[ROJO], destino)
                        estado = jugar(estado, destino)

            if estado is None:
                pantalla.fill(FONDO)
                texto(pantalla, titulo, "Yoshi's Battle", 145)
                texto(pantalla, fuente, "Elige la dificultad", 209)
                mouse = pygame.mouse.get_pos()
                for numero, (nombre, rect) in enumerate(BOTONES.items(), start=1):
                    color = (52, 105, 79) if rect.collidepoint(mouse) else (40, 72, 58)
                    pygame.draw.rect(pantalla, color, rect, border_radius=8)
                    texto(pantalla, fuente, f"{numero}  {nombre.capitalize()}", rect.centery)
            else:
                dibujar_partida(pantalla, fuente, estado, nivel, piso, monedas, yoshis, direcciones)
            pygame.display.flip()

            if estado is not None and estado.turno == VERDE and not estado.terminado:
                destino = elegir_movimiento(estado, nivel)
                direcciones[VERDE] = direccion_salto(estado.yoshis[VERDE], destino)
                estado = jugar(estado, destino)
            reloj.tick(60)
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
