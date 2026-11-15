from dataclasses import dataclass
from random import Random

LADO = 8
VERDE, ROJO = 0, 1
Posicion = tuple[int, int]
CENTRO = tuple((fila, columna) for fila in (3, 4) for columna in (3, 4))
SALTOS = ((-2, -1), (-2, 1), (-1, -2), (-1, 2),
          (1, -2), (1, 2), (2, -1), (2, 1))


@dataclass(frozen=True)
class Estado:
    yoshis: tuple[Posicion, Posicion]
    monedas: tuple[tuple[Posicion, int], ...]
    puntos: tuple[int, int] = (0, 0)
    turno: int = VERDE

    @property
    def terminado(self) -> bool:
        return not self.monedas

    @property
    def ganador(self) -> int | None:
        if not self.terminado:
            return None
        return VERDE if self.puntos[VERDE] > self.puntos[ROJO] else ROJO


def nueva_partida(azar: Random | None = None) -> Estado:
    if azar is None:
        azar = Random()
    disponibles = [
        (fila, columna)
        for fila in range(LADO)
        for columna in range(LADO)
        if (fila, columna) not in CENTRO
    ]
    posiciones = azar.sample(disponibles, 11)
    monedas = tuple((casilla, 3) for casilla in CENTRO)
    monedas += tuple((casilla, 1) for casilla in posiciones[2:])
    return Estado((posiciones[0], posiciones[1]), monedas)


def movimientos_legales(estado: Estado) -> tuple[Posicion, ...]:
    if estado.terminado:
        return ()
    fila, columna = estado.yoshis[estado.turno]
    rival = estado.yoshis[1 - estado.turno]
    destinos = ((fila + df, columna + dc) for df, dc in SALTOS)
    return tuple(
        (f, c) for f, c in destinos
        if 0 <= f < LADO and 0 <= c < LADO and (f, c) != rival
    )


def jugar(estado: Estado, destino: Posicion) -> Estado:
    if destino not in movimientos_legales(estado):
        raise ValueError("Movimiento ilegal")

    yoshis = list(estado.yoshis)
    puntos = list(estado.puntos)
    monedas = dict(estado.monedas)
    yoshis[estado.turno] = destino
    puntos[estado.turno] += monedas.pop(destino, 0)
    return Estado(
        (yoshis[VERDE], yoshis[ROJO]),
        tuple(monedas.items()),
        (puntos[VERDE], puntos[ROJO]),
        1 - estado.turno,
    )
