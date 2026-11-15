from collections import deque
from functools import cache
from math import inf

from .juego import LADO, ROJO, SALTOS, VERDE, Estado, Posicion, jugar, movimientos_legales

PROFUNDIDADES = {"principiante": 2, "intermedio": 4, "experto": 6}


@cache
def _distancias(origen: Posicion) -> dict[Posicion, int]:
    """Devuelve la cantidad mínima de saltos de caballo a cada casilla."""
    distancias = {origen: 0}
    pendientes = deque([origen])
    while pendientes:
        fila, columna = pendientes.popleft()
        for df, dc in SALTOS:
            destino = f, c = fila + df, columna + dc
            if 0 <= f < LADO and 0 <= c < LADO and destino not in distancias:
                distancias[destino] = distancias[fila, columna] + 1
                pendientes.append(destino)
    return distancias


def evaluar(estado: Estado) -> float:
    """Utilidad desde el punto de vista del Yoshi verde."""
    diferencia = estado.puntos[VERDE] - estado.puntos[ROJO]
    if estado.terminado:
        return 22 if estado.ganador == VERDE else -22

    verde = _distancias(estado.yoshis[VERDE])
    rojo = _distancias(estado.yoshis[ROJO])
    ventaja = sum(
        valor * (1 / (1 + verde[casilla]) - 1 / (1 + rojo[casilla]))
        for casilla, valor in estado.monedas
    )
    # La proximidad pesa menos que un punto ya obtenido.
    return diferencia + ventaja / sum(valor for _, valor in estado.monedas)


def _buscar(
    estado: Estado, profundidad: int, alfa: float, beta: float
) -> tuple[float, Posicion | None]:
    if profundidad == 0 or estado.terminado:
        return evaluar(estado), None

    maximiza = estado.turno == VERDE
    mejor_valor = -inf if maximiza else inf
    mejor_destino = None
    for destino in movimientos_legales(estado):
        valor, _ = _buscar(jugar(estado, destino), profundidad - 1, alfa, beta)
        if maximiza:
            if valor > mejor_valor:
                mejor_valor, mejor_destino = valor, destino
            alfa = max(alfa, mejor_valor)
        else:
            if valor < mejor_valor:
                mejor_valor, mejor_destino = valor, destino
            beta = min(beta, mejor_valor)
        if alfa >= beta:
            break
    return mejor_valor, mejor_destino


def elegir_movimiento(estado: Estado, nivel: str) -> Posicion | None:
    """Elige un salto según el nivel, o devuelve None si terminó la partida."""
    if nivel not in PROFUNDIDADES:
        raise ValueError(f"Nivel desconocido: {nivel}")
    _, destino = _buscar(estado, PROFUNDIDADES[nivel], -inf, inf)
    return destino
