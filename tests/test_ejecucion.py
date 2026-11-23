"""Pruebas reales con spawn: cancelación, memoria y salida acotada."""
import os
import time
import unittest

from src.core import limites
from src.core.ejecucion import ErrorEjecucion, Supervisor


def dormir(segundos):
    time.sleep(segundos)
    return os.getpid()


def reservar_megabytes(cantidad):
    return len(bytearray(cantidad * 1024 * 1024))


def salida_grande():
    return "x" * limites.RESPUESTA_MAX_BYTES


class TestEjecucion(unittest.TestCase):
    def test_tiempo_termina_proceso_y_reemplaza(self):
        with Supervisor(trabajadores=1) as supervisor:
            anterior = supervisor.procesos[0]
            with self.assertRaises(ErrorEjecucion) as error:
                supervisor.ejecutar("tests.test_ejecucion:dormir", 30, tiempo=0.1)
            self.assertEqual(error.exception.tipo, "tiempo")
            self.assertFalse(anterior.is_alive())
            nuevo = supervisor.ejecutar("os:getpid")
            self.assertNotEqual(nuevo, anterior.pid)
            self.assertEqual(supervisor.ejecutar("os:getpid"), nuevo)

    def test_memoria_limitada_y_siguiente_calculo(self):
        with Supervisor(trabajadores=1, memoria_mb=128) as supervisor:
            with self.assertRaises(ErrorEjecucion) as error:
                supervisor.ejecutar("tests.test_ejecucion:reservar_megabytes", 256)
            self.assertEqual(error.exception.tipo, "limite")
            self.assertGreater(supervisor.ejecutar("os:getpid"), 0)

    def test_salida_maxima_no_viaja_al_servidor(self):
        with Supervisor(trabajadores=1) as supervisor:
            with self.assertRaises(ErrorEjecucion) as error:
                supervisor.ejecutar("tests.test_ejecucion:salida_grande")
            self.assertEqual(error.exception.codigo, "respuesta_grande")
            self.assertGreater(supervisor.ejecutar("os:getpid"), 0)

    def test_cierre_termina_todos_los_procesos(self):
        supervisor = Supervisor()
        procesos = supervisor.procesos
        supervisor.cerrar()
        supervisor.cerrar()
        self.assertTrue(all(not proceso.is_alive() for proceso in procesos))
