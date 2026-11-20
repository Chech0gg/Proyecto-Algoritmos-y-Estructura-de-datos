import copy
import json
import os
import tempfile
import unittest

from monitorias import persistencia
from monitorias.arboles import son_iguales
from monitorias.cli import consola
from monitorias.datos_demo import cargar_demo
from monitorias.errores import error_validacion
from monitorias.sistema import sistema_monitorias
from tests.test_sistema import reloj_falso, verificar_invariantes


def demo_trabajada():
    s = sistema_monitorias(reloj=reloj_falso())
    codigo = cargar_demo(s)
    s.generar_agenda()
    s.revertir_ultima_asignacion()
    s.revertir_ultima_asignacion()
    return s, codigo


class prueba_persistencia(unittest.TestCase):

    def test_guardar_y_cargar_da_el_mismo_estado(self):
        s, codigo = demo_trabajada()
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = os.path.join(carpeta, "datos.json")
            persistencia.guardar(s, ruta)
            self.assertEqual(os.listdir(carpeta), ["datos.json"])
            cargado = persistencia.cargar(ruta, reloj=reloj_falso())
        self.assertEqual(persistencia.a_diccionario(cargado), persistencia.a_diccionario(s))
        self.assertEqual(cargado.mostrar_informe(), s.mostrar_informe())
        self.assertEqual(cargado.agenda.mostrar(), s.agenda.mostrar())
        self.assertEqual(cargado.mostrar_cola(), s.mostrar_cola())
        self.assertEqual(cargado.mostrar_historial(), s.mostrar_historial())
        self.assertEqual(cargado.mostrar_red(), s.mostrar_red())
        self.assertTrue(son_iguales(cargado.catalogo.raiz, s.catalogo.raiz))
        self.assertEqual(len(cargado.indice_materias), len(s.indice_materias))
        self.assertTrue(cargado.indice_personas.es_avl())

    def test_el_sistema_cargado_sigue_funcionando(self):
        s, codigo = demo_trabajada()
        cargado = persistencia.desde_diccionario(json.loads(json.dumps(persistencia.a_diccionario(s))), reloj_falso())
        verificar_invariantes(self, cargado)
        revertidas = [x for x in cargado.solicitudes if x.revertida]
        self.assertEqual(len(revertidas), 2)
        cargado.registrar_estudiante("nuevo", 2, "ing", [("viernes", "08:00", "10:00")])
        self.assertEqual(cargado.registrar_estudiante("otro", 2, "ing", []).codigo, "e-0009")
        cargado.reencolar(revertidas[0].id)
        verificar_invariantes(self, cargado)
        while not cargado.historial.esta_vacia():
            cargado.revertir_ultima_asignacion()
        self.assertEqual(len(cargado.agenda.sesiones), 0)

    def test_sistema_vacio(self):
        s = sistema_monitorias()
        copia = persistencia.desde_diccionario(json.loads(json.dumps(persistencia.a_diccionario(s))))
        self.assertEqual(persistencia.a_diccionario(copia), persistencia.a_diccionario(s))

    def test_archivos_danados(self):
        s, codigo = demo_trabajada()
        bueno = json.loads(json.dumps(persistencia.a_diccionario(s)))
        casos = []
        malo = copy.deepcopy(bueno)
        malo["version"] = 99
        casos.append(malo)
        malo = copy.deepcopy(bueno)
        del malo["materias"]
        casos.append(malo)
        malo = copy.deepcopy(bueno)
        malo["personas"][0]["tipo"] = "extraterrestre"
        casos.append(malo)
        malo = copy.deepcopy(bueno)
        malo["solicitudes"][0]["estudiante"] = "e-9999"
        casos.append(malo)
        malo = copy.deepcopy(bueno)
        malo["prerrequisitos"].append([codigo["calculo i"], codigo["aprendizaje automatico"]])
        casos.append(malo)
        malo = copy.deepcopy(bueno)
        malo["historial"][0]["sesion"] = 99
        casos.append(malo)
        malo = copy.deepcopy(bueno)
        malo["materias"][0]["nivel"] = "uno"
        casos.append(malo)
        for malo in casos:
            with self.assertRaises(error_validacion):
                persistencia.desde_diccionario(malo)

    def test_errores_de_archivo(self):
        with tempfile.TemporaryDirectory() as carpeta:
            with self.assertRaises(error_validacion):
                persistencia.cargar(os.path.join(carpeta, "no_existe.json"))
            ruta = os.path.join(carpeta, "roto.json")
            with open(ruta, "w") as archivo:
                archivo.write("{esto no es json")
            with self.assertRaises(error_validacion):
                persistencia.cargar(ruta)
            with open(ruta, "w") as archivo:
                archivo.write("[1, 2, 3]")
            with self.assertRaises(error_validacion):
                persistencia.cargar(ruta)


def guion(*respuestas):
    pendientes = list(respuestas)

    def entrada(mensaje):
        if len(pendientes) == 0:
            raise EOFError
        return pendientes.pop(0)
    return entrada


def correr(sistema, *respuestas, archivo="x.json"):
    salidas = []
    app = consola(sistema, entrada=guion(*respuestas), salida=salidas.append, archivo=archivo)
    app.ejecutar()
    return app, "\n".join(salidas)


class prueba_consola(unittest.TestCase):

    def test_recorrido_completo_con_la_demostracion(self):
        app, texto = correr(sistema_monitorias(reloj=reloj_falso()), "22", "7", "8", "9", "13", "16", "normal", "17", "21", "0")
        self.assertIn("cobertura: 85.7%", texto)
        self.assertIn("islas desconectadas: 3", texto)
        self.assertIn("catalogo", texto)
        self.assertIn("areas sin monitor: humanidades", texto)
        self.assertIn("hasta luego", texto)
        self.assertEqual(len(app.sistema.solicitudes), 7)

    def test_entradas_invalidas_se_vuelven_a_pedir(self):
        app, texto = correr(sistema_monitorias(), "3", "ana", "tres", "99", "3", "ing", "lunes 8:5 9:00",
                            "lunes 08:00 10:00", "abc", "", "0")
        self.assertIn("escriba un numero entero entre 1 y 12", texto)
        self.assertIn("hora invalida", texto)
        self.assertIn("use el formato", texto)
        estudiante = app.sistema.personas.obtener("e-0001")
        self.assertEqual((estudiante.nombre, estudiante.semestre), ("ana", 3))
        self.assertEqual(len(estudiante.disponibilidad), 1)

    def test_nota_con_coma_decimal(self):
        s = sistema_monitorias(reloj=reloj_falso())
        s.registrar_materia("calculo i", "mat", 1, 4)
        s.registrar_estudiante("ana", 2, "ing", [])
        app, texto = correr(s, "6", "e-0001", "mat-0001", "par", "4,5", "0")
        self.assertEqual(s.solicitudes[0].nota, 4.5)
        self.assertIn("solicitud #1 creada", texto)

    def test_errores_del_sistema_no_cierran_el_programa(self):
        s = sistema_monitorias(reloj=reloj_falso())
        a = s.registrar_materia("calculo i", "mat", 1, 4)
        b = s.registrar_materia("calculo ii", "mat", 2, 4)
        s.agregar_prerrequisito(b.codigo, a.codigo)
        s.registrar_estudiante("ana", 3, "ing", [])
        app, texto = correr(s, "6", "e-0001", "mat-0002", "par", "3", "11", "abc", "99", "0")
        self.assertIn("error: ana no ha cursado los prerrequisitos de calculo ii", texto)
        self.assertIn("error: no hay asignaciones para revertir", texto)
        self.assertEqual(texto.count("opcion no valida"), 2)
        self.assertIn("hasta luego", texto)

    def test_sin_datos_los_menus_avisan(self):
        app, texto = correr(sistema_monitorias(), "6", "17", "0")
        self.assertIn("error: no hay estudiantes registrados", texto)
        self.assertIn("materias: 0", texto)

    def test_fin_de_la_entrada_termina_limpio(self):
        correr(sistema_monitorias(), "22")

    def test_guardar_y_cargar_desde_el_menu(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = os.path.join(carpeta, "m.json")
            app, texto = correr(sistema_monitorias(reloj=reloj_falso()), "22", "7", "23", "0", archivo=ruta)
            self.assertIn("guardado en", texto)
            otra, texto = correr(sistema_monitorias(), "24", "13", "0", archivo=ruta)
            self.assertIn("cargado desde", texto)
            self.assertIn("solicitudes: 7", texto)
            self.assertEqual(len(otra.sistema.solicitudes), 7)

    def test_consultas_de_arboles_y_grafos_desde_el_menu(self):
        s = sistema_monitorias(reloj=reloj_falso())
        codigo = cargar_demo(s)
        etica = codigo["etica"]
        calculo = codigo["calculo i"]
        aprendizaje = codigo["aprendizaje automatico"]
        app, texto = correr(s, "14", "e-0003", "15", "0.1", "0.9", "18", calculo, aprendizaje, "19", calculo,
                            "20", "e-0001", aprendizaje, "16", "inverso", "18", etica, calculo, "0")
        self.assertIn("avl:", texto)
        self.assertIn("tabla hash:", texto)
        self.assertIn("el arbol visito", texto)
        self.assertIn("ruta de prerrequisitos: calculo i", texto)
        self.assertIn("ola 1:", texto)
        self.assertIn("materias bloqueadas en total: 9", texto)
        self.assertIn("debe cursar, en este orden:", texto)
        self.assertIn("islas distintas", texto)

    def test_listados_ordenados_y_reencolar(self):
        s = sistema_monitorias(reloj=reloj_falso())
        cargar_demo(s)
        s.generar_agenda()
        s.revertir_ultima_asignacion()
        revertida = [x for x in s.solicitudes if x.revertida][0]
        app, texto = correr(s, "10", "urgencia", "rapido", "12", str(revertida.id), "0")
        self.assertIn("u=", texto)
        self.assertIn(f"solicitud #{revertida.id}", texto)


if __name__ == "__main__":
    unittest.main()
