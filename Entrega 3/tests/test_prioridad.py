import math
import random
import unittest

from monitorias import prioridad
from monitorias.errores import error_validacion
from monitorias.monticulo import monticulo


class prueba_riesgo(unittest.TestCase):

    def test_anclas(self):
        self.assertAlmostEqual(prioridad.riesgo(3.0), 0.5)
        self.assertAlmostEqual(prioridad.riesgo(2.0), 0.9)
        self.assertAlmostEqual(prioridad.riesgo(4.0), 0.1)

    def test_simetrica_alrededor_de_la_nota_aprobatoria(self):
        for g in [1.0, 1.5, 2.0, 2.7, 3.0, 3.3, 4.2, 5.0]:
            self.assertAlmostEqual(prioridad.riesgo(g) + prioridad.riesgo(6 - g), 1.0)

    def test_estrictamente_decreciente_y_acotado(self):
        valores = [prioridad.riesgo(n / 10) for n in range(0, 51)]
        for antes, despues in zip(valores, valores[1:]):
            self.assertGreater(antes, despues)
        self.assertTrue(all(0 < v < 1 for v in valores))

    def test_notas_invalidas(self):
        for mala in [-0.1, 5.1, "3", None, True, float("nan")]:
            with self.assertRaises(error_validacion):
                prioridad.riesgo(mala)

    def test_niveles_salen_de_las_anclas(self):
        niveles = {n: prioridad.calcular_prioridad(n, None, 0, 0).nivel for n in [0.0, 2.9, 3.0, 3.01, 4.0, 4.01, 5.0]}
        self.assertEqual(niveles, {0.0: "alta", 2.9: "alta", 3.0: "alta", 3.01: "media", 4.0: "media",
                                   4.01: "baja", 5.0: "baja"})


class prueba_impacto_y_urgencia(unittest.TestCase):

    def test_impacto(self):
        self.assertEqual(prioridad.impacto(0, 0), 1.0)
        self.assertEqual(prioridad.impacto(2, 2), 1.0)
        self.assertAlmostEqual(prioridad.impacto(0, 2), 1 / 3)
        with self.assertRaises(error_validacion):
            prioridad.impacto(3, 2)
        with self.assertRaises(error_validacion):
            prioridad.impacto(-1, 2)

    def test_ejemplo_del_documento(self):
        base = prioridad.calcular_prioridad(2.5, None, 2, 2)
        final = prioridad.calcular_prioridad(2.5, None, 0, 2)
        excelente = prioridad.calcular_prioridad(4.8, None, 2, 2)
        self.assertAlmostEqual(base.urgencia, 0.75)
        self.assertAlmostEqual(final.urgencia, 0.25)
        self.assertAlmostEqual(excelente.urgencia, 0.0188, places=3)

    def test_quien_va_muy_bien_no_es_urgente_aunque_la_materia_sea_importante(self):
        for dependientes in range(0, 6):
            u = prioridad.calcular_prioridad(5.0, None, dependientes, 5).urgencia
            self.assertLess(u, 0.02)

    def test_urgencia_acotada(self):
        random.seed(4)
        for _ in range(500):
            maximo = random.randint(0, 10)
            r = prioridad.calcular_prioridad(random.uniform(0, 5), None, random.randint(0, maximo), maximo)
            self.assertTrue(0 < r.urgencia < 1)

    def test_tasa_historica_si_no_hay_nota(self):
        r = prioridad.calcular_prioridad(None, 0.4, 0, 0)
        self.assertAlmostEqual(r.riesgo, 0.4)
        self.assertEqual(r.nivel, "media")
        with self.assertRaises(error_validacion):
            prioridad.calcular_prioridad(None, None, 0, 0)
        with self.assertRaises(error_validacion):
            prioridad.calcular_prioridad(None, 1.5, 0, 0)

    def test_desglose_legible(self):
        texto = prioridad.calcular_prioridad(2.5, None, 2, 2).desglose
        self.assertIn("nota 2.5", texto)
        self.assertIn("2 de 2", texto)


class prueba_envejecimiento(unittest.TestCase):

    def pedidos(self, n, semilla):
        random.seed(semilla)
        return [(random.random(), random.uniform(0, 60)) for _ in range(n)]

    def test_el_orden_de_la_cola_es_el_de_la_prioridad_efectiva(self):
        for ahora in (60.0, 100.0, 1000.0):
            pedidos = self.pedidos(200, 1)
            por_clave = sorted(range(200), key=lambda i: prioridad.clave_cola(pedidos[i][0], pedidos[i][1]))
            por_efectiva = sorted(range(200), key=lambda i: -prioridad.prioridad_efectiva(pedidos[i][0], pedidos[i][1], ahora))
            self.assertEqual(por_clave, por_efectiva)

    def test_cota_de_adelantamiento(self):
        pedidos = self.pedidos(300, 2)
        for u_i, a_i in pedidos:
            ventana = prioridad.cota_adelantamiento(u_i)
            k_i = prioridad.clave_cola(u_i, a_i)
            for u_j, a_j in pedidos:
                if a_j - a_i >= ventana + 1e-9:
                    self.assertGreaterEqual(prioridad.clave_cola(u_j, a_j), k_i)

    def test_ninguna_solicitud_se_queda_esperando_para_siempre(self):
        def simular(dias):
            cola = monticulo()
            cola.insertar(prioridad.clave_cola(0.05, 0.0, dias), "baja")
            for turno in range(1, 400):
                cola.insertar(prioridad.clave_cola(0.95, float(turno), dias), "alta")
                if cola.extraer() == "baja":
                    return turno
            return None
        self.assertIsNone(simular(1e12))
        self.assertEqual(simular(7.0), 7)
        atendida = simular(7.0)
        self.assertIsNotNone(atendida)
        self.assertLessEqual(atendida, math.ceil(7.0 * (1 - 0.05 + 0.95)) + 1)

    def test_mas_urgente_va_primero_si_llegan_juntas(self):
        cola = monticulo()
        for nombre, u in [("a", 0.2), ("b", 0.9), ("c", 0.5)]:
            cola.insertar(prioridad.clave_cola(u, 10.0), nombre)
        self.assertEqual([cola.extraer() for _ in range(3)], ["b", "c", "a"])


if __name__ == "__main__":
    unittest.main()
