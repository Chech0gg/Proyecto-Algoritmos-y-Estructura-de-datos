import math
import random
import unittest

from monitorias.arboles import arbol_materias, copiar, espejo, son_iguales
from monitorias.avl import indice_avl
from monitorias.conjuntos import conjunto
from monitorias.errores import error_validacion
from monitorias.grafos import (grafo_desde_matriz, grafo_dirigido, lista_a_matriz,
                               matriz_a_lista)
from monitorias.prerrequisitos import mapa_prerrequisitos


class prueba_avl(unittest.TestCase):

    def test_claves_en_orden_creciente_quedan_balanceadas(self):
        arbol = indice_avl()
        n = 2000
        for i in range(n):
            arbol.insertar(i, i)
        self.assertTrue(arbol.es_avl())
        self.assertLessEqual(arbol.altura() + 1, 1.4405 * math.log2(n + 2))
        self.assertEqual(arbol.claves(), list(range(n)))

    def test_sin_balancear_se_vuelve_lista(self):
        arbol = indice_avl(balanceado=False)
        for i in range(500):
            arbol.insertar(i, i)
        self.assertTrue(arbol.es_bst())
        self.assertFalse(arbol.es_avl())
        self.assertEqual(arbol.altura(), 499)

    def test_insertar_y_eliminar_al_azar(self):
        random.seed(11)
        arbol = indice_avl()
        referencia = set()
        for paso in range(3000):
            clave = random.randint(0, 300)
            if random.random() < 0.55:
                self.assertEqual(arbol.insertar(clave, clave * 2), clave not in referencia)
                referencia.add(clave)
            else:
                self.assertEqual(arbol.eliminar(clave), clave in referencia)
                referencia.discard(clave)
            if paso % 50 == 0:
                self.assertTrue(arbol.es_avl())
        self.assertTrue(arbol.es_avl())
        self.assertEqual(arbol.claves(), sorted(referencia))
        self.assertEqual(len(arbol), len(referencia))

    def test_buscar_cuenta_comparaciones(self):
        arbol = indice_avl()
        for i in range(1000):
            arbol.insertar(i, "v" + str(i))
        valor, comparaciones = arbol.buscar(777)
        self.assertEqual(valor, "v777")
        self.assertLessEqual(comparaciones, arbol.altura() + 1)
        self.assertEqual(arbol.buscar(5000)[0], None)
        self.assertFalse(arbol.contiene(-1))

    def test_en_rango_contra_fuerza_bruta(self):
        random.seed(5)
        arbol = indice_avl()
        claves = random.sample(range(1000), 200)
        for c in claves:
            arbol.insertar(c, c)
        for a, b in [(0, 999), (100, 200), (500, 500), (-5, 3), (990, 2000), (300, 100)]:
            resultado, visitados = arbol.en_rango(a, b)
            self.assertEqual([c for c, v in resultado], sorted(c for c in claves if a <= c <= b))
            self.assertLessEqual(visitados, len(arbol))
        angosto, visitados = arbol.en_rango(400, 410)
        self.assertLess(visitados, 40)

    def test_claves_compuestas(self):
        arbol = indice_avl()
        for i, u in enumerate([0.5, 0.1, 0.9, 0.5]):
            arbol.insertar((u, i), i)
        resultado, visitados = arbol.en_rango((0.4, 0), (0.6, 10 ** 9))
        self.assertEqual([v for c, v in resultado], [0, 3])

    def test_es_bst_detecta_un_impostor(self):
        arbol = indice_avl()
        for c in [50, 30, 70, 20, 40, 60, 80]:
            arbol.insertar(c, c)
        arbol.raiz.izq.der.clave = 60
        self.assertFalse(arbol.es_bst())

    def test_vacio(self):
        arbol = indice_avl()
        self.assertEqual(arbol.listar_ordenado(), [])
        self.assertEqual(arbol.en_rango(0, 1), ([], 0))
        self.assertFalse(arbol.eliminar(1))
        self.assertTrue(arbol.es_avl())
        self.assertEqual(arbol.altura(), -1)

    def test_reemplazar_valor(self):
        arbol = indice_avl()
        arbol.insertar("a", 1)
        self.assertFalse(arbol.insertar("a", 2))
        self.assertEqual(arbol.buscar("a")[0], 2)
        self.assertEqual(len(arbol), 1)


class prueba_arboles(unittest.TestCase):

    def construir(self):
        arbol = arbol_materias()
        arbol.agregar_materia("matematicas", "calculo i", "mat-0001")
        arbol.agregar_materia("sistemas", "programacion i", "mat-0002")
        arbol.agregar_materia("matematicas", "algebra", "mat-0003")
        return arbol

    def test_jerarquia(self):
        arbol = self.construir()
        self.assertEqual(arbol.mostrar().split("\n"), [
            "catalogo", "  matematicas", "    calculo i [mat-0001]", "    algebra [mat-0003]",
            "  sistemas", "    programacion i [mat-0002]"])
        self.assertEqual(arbol.areas(), ["matematicas", "sistemas"])
        self.assertEqual(arbol.materias_de_area("matematicas"), ["calculo i", "algebra"])
        self.assertEqual(arbol.materias_de_area("nada"), [])

    def test_espejo_e_invertido(self):
        arbol = self.construir()
        invertido = arbol.mostrar(invertido=True).split("\n")
        self.assertEqual(invertido[1], "  sistemas")
        self.assertEqual(arbol.areas(), ["matematicas", "sistemas"])

    def test_son_iguales(self):
        a = self.construir()
        b = self.construir()
        self.assertTrue(son_iguales(a.raiz, b.raiz))
        espejado = copiar(a.raiz)
        espejo(espejado)
        self.assertFalse(son_iguales(a.raiz, espejado))
        b.agregar_materia("sistemas", "otra", "mat-0009")
        self.assertFalse(son_iguales(a.raiz, b.raiz))
        self.assertTrue(son_iguales(None, None))
        self.assertFalse(son_iguales(a.raiz, None))


class prueba_grafos(unittest.TestCase):

    def malla(self):
        g = grafo_dirigido()
        for v in "abcdefgh":
            g.agregar_vertice(v)
        for u, v in [("a", "b"), ("a", "c"), ("b", "d"), ("c", "d"), ("d", "e"), ("f", "g")]:
            g.agregar_arista(u, v)
        return g

    def test_ida_y_vuelta_matriz_lista(self):
        random.seed(2)
        for _ in range(300):
            n = random.randint(0, 9)
            m = [[random.randint(0, 1) for _ in range(n)] for _ in range(n)]
            self.assertEqual(lista_a_matriz(matriz_a_lista(m)), m)
        with self.assertRaises(error_validacion):
            matriz_a_lista([[0, 1], [0]])
        with self.assertRaises(error_validacion):
            matriz_a_lista([[0, 2], [0, 0]])
        with self.assertRaises(error_validacion):
            lista_a_matriz([[5]])

    def test_representaciones_y_densidad(self):
        g = self.malla()
        self.assertEqual(g.a_matriz()[0], [0, 1, 1, 0, 0, 0, 0, 0])
        self.assertEqual(g.a_lista()[0], [1, 2])
        self.assertAlmostEqual(g.densidad(), 6 / 56)
        info = g.justificar_representacion()
        self.assertEqual(info["decision"], "lista de adyacencia")
        self.assertEqual(info["celdas_matriz"], 64)
        self.assertEqual(info["celdas_lista"], 14)
        completo = grafo_desde_matriz([[0, 1], [1, 0]], ["x", "y"])
        self.assertEqual(completo.justificar_representacion()["decision"], "matriz de adyacencia")

    def test_islas(self):
        g = self.malla()
        self.assertEqual(g.componentes(), [["a", "b", "c", "d", "e"], ["f", "g"], ["h"]])
        g.agregar_arista("e", "f")
        self.assertEqual(len(g.componentes()), 2)

    def test_rechaza_ciclos_y_duplicados(self):
        g = self.malla()
        for u, v in [("e", "a"), ("a", "a"), ("d", "a")]:
            with self.assertRaises(error_validacion):
                g.agregar_arista(u, v)
        with self.assertRaises(error_validacion):
            g.agregar_arista("a", "b")
        with self.assertRaises(error_validacion):
            g.agregar_arista("a", "zzz")

    def test_detectar_ciclos_con_tres_estados(self):
        g = self.malla()
        self.assertEqual(g.detectar_ciclos(), [])
        g.agregar_arista("e", "b", validar_ciclos=False)
        ciclos = g.detectar_ciclos()
        self.assertEqual(ciclos, [["b", "d", "e", "b"]])
        with self.assertRaises(error_validacion):
            g.orden_topologico()
        rombo = grafo_dirigido()
        for v in "abcd":
            rombo.agregar_vertice(v)
        for u, v in [("a", "b"), ("a", "c"), ("b", "d"), ("c", "d")]:
            rombo.agregar_arista(u, v)
        self.assertEqual(rombo.detectar_ciclos(), [])
        dos = grafo_dirigido()
        dos.agregar_vertice("x")
        dos.agregar_vertice("y")
        dos.agregar_arista("x", "y")
        dos.agregar_arista("y", "x", validar_ciclos=False)
        self.assertEqual(len(dos.detectar_ciclos()), 1)
        propio = grafo_dirigido()
        propio.agregar_vertice("z")
        propio.agregar_arista("z", "z", validar_ciclos=False)
        self.assertEqual(propio.detectar_ciclos(), [["z", "z"]])

    def test_orden_topologico_respeta_las_aristas(self):
        g = self.malla()
        orden = g.orden_topologico()
        posicion = {v: i for i, v in enumerate(orden)}
        for u in range(len(g)):
            for v in g.sucesores[u]:
                self.assertLess(posicion[g.etiquetas[u]], posicion[g.etiquetas[v]])
        self.assertEqual(len(orden), 8)

    def test_camino_mas_largo_contra_fuerza_bruta(self):
        random.seed(9)
        for _ in range(200):
            n = random.randint(1, 8)
            g = grafo_dirigido()
            for i in range(n):
                g.agregar_vertice(i)
            for u in range(n):
                for v in range(u + 1, n):
                    if random.random() < 0.35:
                        g.agregar_arista(u, v)

            def mas_largo(u):
                mejor = 0
                for v in g.sucesores[u]:
                    mejor = max(mejor, 1 + mas_largo(v))
                return mejor
            esperado = max(mas_largo(u) for u in range(n))
            ruta = g.camino_mas_largo()
            self.assertEqual(len(ruta) - 1, esperado)
            for a, b in zip(ruta, ruta[1:]):
                self.assertIn(g.vertice(b), g.sucesores[g.vertice(a)])
        self.assertEqual(grafo_dirigido().camino_mas_largo(), [])

    def test_niveles(self):
        g = self.malla()
        self.assertEqual(g.niveles(), {"a": 0, "b": 1, "c": 1, "d": 2, "e": 3, "f": 0, "g": 1, "h": 0})

    def test_ruta_mas_corta(self):
        g = self.malla()
        self.assertEqual(g.ruta_mas_corta("a", "e"), ["a", "b", "d", "e"])
        self.assertEqual(g.ruta_mas_corta("a", "a"), ["a"])
        self.assertIsNone(g.ruta_mas_corta("a", "g"))
        self.assertIsNone(g.ruta_mas_corta("e", "a"))
        self.assertEqual(len(g.ruta_mas_corta("e", "a", dirigido=False)), 4)
        with self.assertRaises(error_validacion):
            g.ruta_mas_corta("a", "zzz")

    def test_diametro_y_distancias(self):
        g = self.malla()
        self.assertEqual(g.diametro(dirigido=False)[0], 3)
        self.assertEqual(g.diametro(dirigido=True)[0], 3)
        self.assertEqual(g.distancias_desde("a")["e"], 3)
        self.assertEqual(g.distancias_desde("a")["g"], -1)
        self.assertEqual(grafo_dirigido().diametro(), (0, None))

    def test_olas_de_impacto(self):
        g = self.malla()
        self.assertEqual(g.olas_desde("a"), [["a"], ["b", "c"], ["d"], ["e"]])
        self.assertEqual(g.olas_desde("e", "requisitos"), [["e"], ["d"], ["b", "c"], ["a"]])
        self.assertEqual(g.olas_desde("h"), [["h"]])
        self.assertEqual(g.descendientes("a"), {"b", "c", "d", "e"})
        self.assertEqual(g.conteo_dependientes()["a"], 4)


class prueba_prerrequisitos(unittest.TestCase):

    def mapa(self):
        m = mapa_prerrequisitos()
        for c in ["a", "b", "c", "d", "e"]:
            m.agregar_materia(c)
        m.agregar("a", "b")
        m.agregar("a", "c")
        m.agregar("b", "d")
        m.agregar("c", "d")
        m.agregar("d", "e")
        return m

    def test_cadena_no_repite_en_rombo(self):
        m = self.mapa()
        cadena = m.cadena("a")
        self.assertEqual(sorted(cadena), ["b", "c", "d", "e"])
        self.assertEqual(len(cadena), len(set(cadena)))
        self.assertLess(cadena.index("d"), cadena.index("b"))
        self.assertLess(cadena.index("e"), cadena.index("d"))

    def test_rutas_y_profundidad(self):
        m = self.mapa()
        self.assertEqual(sorted(m.rutas("a")), [["a", "b", "d", "e"], ["a", "c", "d", "e"]])
        self.assertEqual(m.rutas("e"), [["e"]])
        self.assertEqual(m.profundidad("a"), 3)
        self.assertEqual(m.profundidad("e"), 0)

    def test_rechazos(self):
        m = self.mapa()
        with self.assertRaises(error_validacion):
            m.agregar("e", "a")
        with self.assertRaises(error_validacion):
            m.agregar("a", "a")
        with self.assertRaises(error_validacion):
            m.agregar("a", "b")
        with self.assertRaises(error_validacion):
            m.agregar("a", "zzz")

    def test_faltantes_y_dependientes(self):
        m = self.mapa()
        cursadas = conjunto(["e"])
        self.assertEqual(sorted(m.faltantes("a", cursadas)), ["b", "c", "d"])
        self.assertEqual(m.faltantes_directos("a", cursadas), ["b", "c"])
        self.assertEqual(m.dependientes("e"), {"a", "b", "c", "d"})
        self.assertEqual(m.maximo_dependientes(), 4)
        self.assertEqual(m.directos("zzz"), [])


if __name__ == "__main__":
    unittest.main()
