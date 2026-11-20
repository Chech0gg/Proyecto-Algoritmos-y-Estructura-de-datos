import random
import unittest

from monitorias.conjuntos import conjunto, registro_cursadas
from monitorias.errores import error_validacion
from monitorias.listas import cola, pila
from monitorias.monticulo import monticulo
from monitorias.ordenamientos import (busqueda_binaria, ordenar, ordenar_insercion,
                                      ordenar_mezcla, ordenar_rapido)
from monitorias.tabla_hash import tabla_hash
from monitorias.tiempo import (cubierto, crear_bloque, fusionar_bloques, hora_a_minutos,
                               minutos_a_hora, normalizar_dia)
from monitorias import validaciones


class prueba_tiempo(unittest.TestCase):

    def test_horas_validas(self):
        self.assertEqual(hora_a_minutos("08:30"), 510)
        self.assertEqual(hora_a_minutos("8:30"), 510)
        self.assertEqual(hora_a_minutos("23:59"), 1439)
        self.assertEqual(minutos_a_hora(510), "08:30")

    def test_horas_invalidas(self):
        for malo in ["24:00", "8:5", "08:60", "-1:30", "abc", "", "8:30:00", None, 830, "٣:٠٠"]:
            with self.assertRaises(error_validacion):
                hora_a_minutos(malo)

    def test_medianoche_solo_como_fin(self):
        self.assertEqual(crear_bloque("lunes", "22:00", "24:00").fin, 1440)
        with self.assertRaises(error_validacion):
            crear_bloque("lunes", "24:00", "24:00")

    def test_dias_con_mayusculas_y_tildes(self):
        self.assertEqual(normalizar_dia("Lunes"), "lunes")
        self.assertEqual(normalizar_dia(" MIÉRCOLES "), "miercoles")
        with self.assertRaises(error_validacion):
            normalizar_dia("domingo")
        with self.assertRaises(error_validacion):
            normalizar_dia(None)

    def test_bloque_invertido(self):
        with self.assertRaises(error_validacion):
            crear_bloque("lunes", "10:00", "09:00")
        with self.assertRaises(error_validacion):
            crear_bloque("lunes", 800, 900)

    def test_fusion_de_bloques_contiguos_y_solapados(self):
        bloques = [crear_bloque("lunes", "08:00", "09:00"), crear_bloque("lunes", "09:00", "10:00"),
                   crear_bloque("lunes", "09:30", "11:00"), crear_bloque("lunes", "14:00", "15:00"),
                   crear_bloque("martes", "08:00", "09:00")]
        fusion = [(b.dia, b.inicio, b.fin) for b in fusionar_bloques(bloques)]
        self.assertEqual(fusion, [("lunes", 480, 660), ("lunes", 840, 900), ("martes", 480, 540)])

    def test_cubierto_a_traves_de_bloques_contiguos(self):
        bloques = [crear_bloque("lunes", "08:00", "09:00"), crear_bloque("lunes", "09:00", "10:00")]
        self.assertTrue(cubierto(bloques, "lunes", 510, 570))
        self.assertFalse(cubierto(bloques, "lunes", 510, 630))
        self.assertFalse(cubierto(bloques, "martes", 510, 570))


class prueba_validaciones(unittest.TestCase):

    def test_entero(self):
        self.assertEqual(validaciones.entero(3, "x", 1, 5), 3)
        for malo in ["3", None, 2.5, True, 0, 9]:
            with self.assertRaises(error_validacion):
                validaciones.entero(malo, "x", 1, 5)

    def test_decimal(self):
        self.assertEqual(validaciones.decimal(2, "n", 0, 5), 2.0)
        for malo in ["3", None, True, -0.1, 5.1, float("nan"), float("inf")]:
            with self.assertRaises(error_validacion):
                validaciones.decimal(malo, "n", 0, 5)

    def test_texto(self):
        self.assertEqual(validaciones.texto("  hola ", "t"), "hola")
        for malo in ["", "   ", None, 5]:
            with self.assertRaises(error_validacion):
                validaciones.texto(malo, "t")


class prueba_tabla_hash(unittest.TestCase):

    def test_muchas_claves_y_reemplazo(self):
        tabla = tabla_hash()
        for i in range(5000):
            tabla.poner("k" + str(i), i)
        self.assertEqual(len(tabla), 5000)
        self.assertTrue(all(tabla.obtener("k" + str(i)) == i for i in range(5000)))
        tabla.poner("k1", 99)
        self.assertEqual(len(tabla), 5000)
        self.assertEqual(tabla.obtener("k1"), 99)

    def test_eliminar(self):
        tabla = tabla_hash()
        tabla.poner("a", 1)
        self.assertTrue(tabla.eliminar("a"))
        self.assertFalse(tabla.eliminar("a"))
        self.assertEqual(len(tabla), 0)
        self.assertIsNone(tabla.obtener("a"))
        self.assertEqual(tabla.obtener("a", "x"), "x")

    def test_contiene_con_valor_none(self):
        tabla = tabla_hash()
        tabla.poner("a", None)
        self.assertTrue(tabla.contiene("a"))

    def test_clave_no_texto(self):
        tabla = tabla_hash()
        for malo in [123, None, ("a",)]:
            with self.assertRaises(error_validacion):
                tabla.poner(malo, 1)
            with self.assertRaises(error_validacion):
                tabla.obtener(malo)

    def test_items_claves_valores(self):
        tabla = tabla_hash()
        for i in range(30):
            tabla.poner("c" + str(i), i)
        self.assertEqual(sorted(tabla.valores()), list(range(30)))
        self.assertEqual(len(tabla.claves()), 30)
        self.assertEqual(len(tabla.items()), 30)


class prueba_listas(unittest.TestCase):

    def test_pila_lifo(self):
        p = pila()
        for i in range(3):
            p.apilar(i)
        self.assertEqual(p.ver_tope(), 2)
        self.assertEqual([p.desapilar() for _ in range(3)], [2, 1, 0])
        self.assertTrue(p.esta_vacia())
        self.assertIsNone(p.ver_tope())
        with self.assertRaises(error_validacion):
            p.desapilar()

    def test_cola_fifo(self):
        c = cola()
        for i in range(3):
            c.encolar(i)
        self.assertEqual(c.como_lista(), [0, 1, 2])
        self.assertEqual([c.desencolar() for _ in range(3)], [0, 1, 2])
        with self.assertRaises(error_validacion):
            c.desencolar()
        c.encolar(7)
        self.assertEqual(len(c), 1)


class prueba_monticulo(unittest.TestCase):

    def test_extrae_en_orden(self):
        random.seed(3)
        m = monticulo()
        numeros = [random.randint(0, 50) for _ in range(300)]
        for n in numeros:
            m.insertar((n,), n)
            self.assertTrue(m.es_valido())
        self.assertEqual([m.extraer() for _ in range(300)], sorted(numeros))

    def test_empates_salen_por_orden_de_llegada(self):
        m = monticulo()
        for nombre in ["a", "b", "c", "d"]:
            m.insertar((1,), nombre)
        self.assertEqual([m.extraer() for _ in range(4)], ["a", "b", "c", "d"])

    def test_vacio_y_listado(self):
        m = monticulo()
        self.assertTrue(m.esta_vacio())
        self.assertIsNone(m.ver_menor())
        with self.assertRaises(error_validacion):
            m.extraer()
        m.insertar((2,), "x")
        m.insertar((1,), "y")
        self.assertEqual(m.como_lista(), ["y", "x"])
        self.assertEqual(len(m), 2)


class prueba_conjuntos(unittest.TestCase):

    def test_operaciones(self):
        a = conjunto(["x", "y", "z"])
        b = conjunto(["y", "z", "w"])
        self.assertEqual(sorted(a.union(b).elementos()), ["w", "x", "y", "z"])
        self.assertEqual(sorted(a.interseccion(b).elementos()), ["y", "z"])
        self.assertEqual(a.diferencia(b).elementos(), ["x"])
        self.assertFalse(a.agregar("x"))
        self.assertTrue(a.agregar("q"))

    def test_registro_cursadas(self):
        r = registro_cursadas()
        self.assertTrue(r.registrar("e-1", "mat-1"))
        self.assertFalse(r.registrar("e-1", "mat-1"))
        self.assertTrue(r.ha_cursado("e-1", "mat-1"))
        self.assertFalse(r.ha_cursado("e-2", "mat-1"))
        self.assertEqual(len(r.de("e-2")), 0)


class falsa:

    def __init__(self, id, urgencia, llegada, nombre):
        self.id = id
        self.urgencia = urgencia
        self.llegada = llegada
        self.materia = type("m", (), {"nombre": nombre})()


class prueba_ordenamientos(unittest.TestCase):

    def lista(self, n, semilla):
        random.seed(semilla)
        return [falsa(i, random.randint(0, 5) / 5, random.randint(0, 9), random.choice("abc")) for i in range(n)]

    def test_los_tres_metodos_coinciden_con_sorted(self):
        for n in (0, 1, 2, 10, 11, 300):
            lista = self.lista(n, n)
            for criterio, clave in [("urgencia", lambda s: (-s.urgencia, s.id)),
                                    ("antiguedad", lambda s: (s.llegada, s.id)),
                                    ("materia", lambda s: (s.materia.nombre, s.id))]:
                esperado = [s.id for s in sorted(lista, key=clave)]
                for metodo in ("insercion", "mezcla", "rapido", "auto"):
                    self.assertEqual([s.id for s in ordenar(lista, criterio, metodo)], esperado)

    def test_quicksort_con_claves_iguales_no_se_cae(self):
        lista = list(range(20000))
        self.assertEqual(ordenar_rapido(lista, lambda x: 0), lista)

    def test_quicksort_ordenado_e_inverso(self):
        self.assertEqual(ordenar_rapido(list(range(5000)), lambda x: x), list(range(5000)))
        self.assertEqual(ordenar_rapido(list(range(5000, 0, -1)), lambda x: x), list(range(1, 5001)))

    def test_estabilidad_de_insercion_y_mezcla(self):
        pares = [(1, "a"), (0, "b"), (1, "c"), (0, "d")]
        esperado = [(0, "b"), (0, "d"), (1, "a"), (1, "c")]
        self.assertEqual(ordenar_insercion(pares, lambda p: p[0]), esperado)
        self.assertEqual(ordenar_mezcla(pares, lambda p: p[0]), esperado)

    def test_criterio_y_metodo_invalidos(self):
        with self.assertRaises(error_validacion):
            ordenar([], "color")
        with self.assertRaises(error_validacion):
            ordenar([], "urgencia", "burbuja")

    def test_busqueda_binaria(self):
        datos = list(range(0, 1000, 2))
        posicion, comparaciones = busqueda_binaria(datos, 500, lambda x: x)
        self.assertEqual(datos[posicion], 500)
        self.assertLessEqual(comparaciones, 10)
        self.assertEqual(busqueda_binaria(datos, 501, lambda x: x)[0], -1)
        self.assertEqual(busqueda_binaria([], 1, lambda x: x), (-1, 0))


if __name__ == "__main__":
    unittest.main()
