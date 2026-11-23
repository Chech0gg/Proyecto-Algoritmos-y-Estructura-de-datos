import importlib
import importlib.util
import inspect
import os
import pkgutil
import unittest

import monitorias

ruta = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "definicion_diagrama.py")
especificacion = importlib.util.spec_from_file_location("definicion_diagrama", ruta)
definicion = importlib.util.module_from_spec(especificacion)
especificacion.loader.exec_module(definicion)


def modulos():
    return [importlib.import_module("monitorias." + m.name) for m in pkgutil.iter_modules(monitorias.__path__)
            if m.name != "__main__"]


def buscar_clase(nombre):
    for modulo in modulos():
        encontrado = getattr(modulo, nombre, None)
        if inspect.isclass(encontrado):
            return encontrado
    return None


class prueba_diagrama(unittest.TestCase):

    def test_toda_caja_existe_en_el_codigo(self):
        nombres_modulos = [m.name for m in pkgutil.iter_modules(monitorias.__path__)]
        for nombre in definicion.cajas:
            self.assertTrue(nombre in nombres_modulos or buscar_clase(nombre) is not None,
                            nombre + " no existe en el codigo")

    def test_todo_metodo_del_diagrama_existe(self):
        for nombre, datos in definicion.cajas.items():
            clase = buscar_clase(nombre)
            modulo = importlib.import_module("monitorias." + nombre) if clase is None else None
            for metodo in datos["metodos"]:
                limpio = metodo.split("(")[0]
                destino = clase if clase is not None else modulo
                self.assertTrue(hasattr(destino, limpio), nombre + "." + limpio + " no existe")

    def test_las_relaciones_usan_cajas_definidas(self):
        for origen, destino, tipo, texto, m_origen, m_destino in definicion.relaciones:
            self.assertIn(origen, definicion.cajas)
            self.assertIn(destino, definicion.cajas)
            self.assertIn(tipo, ["herencia", "composicion", "agregacion", "asociacion", "dependencia"])

    def test_cada_caja_tiene_posicion(self):
        self.assertEqual(sorted(definicion.cajas), sorted(definicion.posiciones))

    def test_las_herencias_del_diagrama_son_reales(self):
        for origen, destino, tipo, texto, m_origen, m_destino in definicion.relaciones:
            if tipo == "herencia":
                self.assertTrue(issubclass(buscar_clase(origen), buscar_clase(destino)))

    def test_las_clases_del_codigo_estan_en_el_diagrama(self):
        ignoradas = {"tipo_monitoria"}
        propias = set()
        for modulo in modulos():
            for nombre, objeto in inspect.getmembers(modulo, inspect.isclass):
                if objeto.__module__ == modulo.__name__ and nombre not in ignoradas:
                    propias.add(nombre)
        faltan = propias - set(definicion.cajas)
        self.assertEqual(faltan, set(), "clases sin dibujar: " + str(sorted(faltan)))


if __name__ == "__main__":
    unittest.main()
