import unittest
from random import Random

from src.juego import ROJO, VERDE, Estado, jugar, movimientos_legales, nueva_partida
from src.minimax import PROFUNDIDADES, elegir_movimiento, evaluar


def valor_sin_poda(estado, profundidad):
    if profundidad == 0 or estado.terminado:
        return evaluar(estado)
    valores = (
        valor_sin_poda(jugar(estado, destino), profundidad - 1)
        for destino in movimientos_legales(estado)
    )
    return max(valores) if estado.turno == VERDE else min(valores)


class MinimaxTest(unittest.TestCase):
    def test_niveles_coinciden_con_minimax_sin_poda(self):
        estado = nueva_partida(Random(7))
        for nivel, profundidad in (("principiante", 2), ("intermedio", 4), ("experto", 6)):
            with self.subTest(nivel=nivel):
                self.assertEqual(PROFUNDIDADES[nivel], profundidad)
                destino = elegir_movimiento(estado, nivel)
                self.assertIn(destino, movimientos_legales(estado))
                valor = valor_sin_poda(jugar(estado, destino), profundidad - 1)
                self.assertEqual(valor, valor_sin_poda(estado, profundidad))

    def test_gana_al_recoger_la_ultima_moneda(self):
        for turno in (VERDE, ROJO):
            with self.subTest(turno=turno):
                yoshis = ((0, 0), (7, 7)) if turno == VERDE else ((7, 7), (0, 0))
                estado = Estado(yoshis, (((1, 2), 3),), (9, 9), turno)
                destino = elegir_movimiento(estado, "principiante")
                self.assertEqual(destino, (1, 2))
                final = jugar(estado, destino)
                self.assertEqual(final.ganador, turno)
                self.assertIsNone(elegir_movimiento(final, "experto"))

    def test_heuristica_favorece_cercania_a_una_moneda(self):
        monedas = (((1, 2), 3),)
        cerca_verde = Estado(((0, 0), (7, 7)), monedas)
        cerca_rojo = Estado(((7, 7), (0, 0)), monedas)
        self.assertGreater(evaluar(cerca_verde), 0)
        self.assertEqual(evaluar(cerca_verde), -evaluar(cerca_rojo))

    def test_nivel_invalido(self):
        with self.assertRaises(ValueError):
            elegir_movimiento(nueva_partida(), "imposible")
