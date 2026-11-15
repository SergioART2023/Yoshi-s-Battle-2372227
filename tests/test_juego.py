import unittest
from random import Random

from src.juego import CENTRO, ROJO, VERDE, Estado, jugar, movimientos_legales, nueva_partida


class JuegoTest(unittest.TestCase):
    def test_partida_inicial(self):
        for semilla in range(30):
            with self.subTest(semilla=semilla):
                estado = nueva_partida(Random(semilla))
                monedas = dict(estado.monedas)
                self.assertEqual(estado.turno, VERDE)
                self.assertEqual(estado.puntos, (0, 0))
                self.assertEqual(len(monedas), 13)
                self.assertEqual({p for p, valor in monedas.items() if valor == 3}, set(CENTRO))
                self.assertEqual(sum(valor == 1 for valor in monedas.values()), 9)
                self.assertEqual(len(set(estado.yoshis) | monedas.keys()), 15)

    def test_salto_desde_esquina_y_casilla_ocupada(self):
        estado = Estado(((0, 0), (1, 2)), (((2, 1), 1),))
        self.assertEqual(movimientos_legales(estado), ((2, 1),))
        for destino in ((1, 2), (0, 1), (-2, 1)):
            with self.assertRaises(ValueError):
                jugar(estado, destino)

    def test_turnos_recoleccion_y_ganador(self):
        inicial = Estado(((1, 2), (0, 0)), (((3, 3), 3), ((2, 1), 1)), (8, 9))
        tras_verde = jugar(inicial, (3, 3))
        self.assertEqual(tras_verde.puntos, (11, 9))
        self.assertEqual(tras_verde.turno, ROJO)
        self.assertIsNone(tras_verde.ganador)
        self.assertEqual(len(inicial.monedas), 2)

        final = jugar(tras_verde, (2, 1))
        self.assertEqual(final.puntos, (11, 10))
        self.assertTrue(final.terminado)
        self.assertEqual(final.ganador, VERDE)
        self.assertEqual(movimientos_legales(final), ())
        with self.assertRaises(ValueError):
            jugar(final, (1, 2))

    def test_casilla_sin_moneda(self):
        estado = Estado(((0, 0), (7, 7)), (((3, 3), 3),))
        siguiente = jugar(estado, (1, 2))
        self.assertEqual(siguiente.yoshis, ((1, 2), (7, 7)))
        self.assertEqual(siguiente.monedas, estado.monedas)
        self.assertEqual(siguiente.puntos, estado.puntos)
        self.assertEqual(siguiente.turno, ROJO)
