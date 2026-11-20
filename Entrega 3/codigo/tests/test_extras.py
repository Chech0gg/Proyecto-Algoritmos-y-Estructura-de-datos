import contextlib
import io
import os
import tempfile
import unittest
from unittest import mock

from monitorias import cli, persistencia
from monitorias.datos_demo import cargar_demo
from monitorias.errores import error_validacion
from monitorias.sistema import sistema_monitorias
from tests.test_persistencia_cli import correr
from tests.test_sistema import reloj_falso


class prueba_sistema_completo_desde_el_menu(unittest.TestCase):

    def test_todo_se_puede_hacer_desde_la_consola(self):
        s = sistema_monitorias(reloj=reloj_falso())
        app, texto = correr(
            s,
            "1", "calculo i", "matematicas", "1", "4", "0,3",
            "1", "calculo ii", "matematicas", "2", "4", "",
            "2", "mat-0002", "mat-0001",
            "3", "ana", "3", "ing", "lunes 08:00 10:00", "",
            "4", "carlos", "6", "mat-0002", "zzz", "", "lunes 08:00 12:00", "",
            "5", "e-0001", "mat-0001",
            "5", "e-0001", "mat-0001",
            "6", "e-0001", "mat-0002", "par", "3,5",
            "7", "13", "0")
        self.assertIn("materia registrada con codigo mat-0001", texto)
        self.assertIn("prerrequisito agregado", texto)
        self.assertIn("monitor registrado con codigo m-0001", texto)
        self.assertIn("codigo no valido", texto)
        self.assertIn("registrada\n", texto)
        self.assertIn("ya estaba registrada", texto)
        self.assertEqual(s.materias.obtener("mat-0001").tasa_reprobacion, 0.3)
        sesion = s.agenda.sesiones[0]
        self.assertEqual((sesion.dia, sesion.inicio, sesion.fin), ("lunes", 480, 540))
        self.assertIn("cobertura: 100.0%", texto)

    def test_la_demostracion_solo_entra_en_un_sistema_vacio(self):
        app, texto = correr(sistema_monitorias(reloj=reloj_falso()), "22", "22", "0")
        self.assertIn("error: la demostracion solo se puede cargar en un sistema vacio", texto)

    def test_rango_sin_resultados_y_reencolar_invalido(self):
        app, texto = correr(sistema_monitorias(), "15", "0.5", "0.9", "12", "3", "0")
        self.assertIn("0 solicitudes", texto)
        self.assertIn("error: la solicitud 3 no es una asignacion revertida", texto)


class prueba_principal(unittest.TestCase):

    def ejecutar(self, argumentos, teclas):
        salida = io.StringIO()
        with mock.patch("builtins.input", side_effect=teclas), contextlib.redirect_stdout(salida):
            cli.principal(argumentos)
        return salida.getvalue()

    def test_arranque_con_demostracion(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = os.path.join(carpeta, "nuevo.json")
            texto = self.ejecutar([ruta, "--demo"], ["7", "23", "0"])
            self.assertIn("cobertura: 85.7%", texto)
            self.assertIn("guardado en", texto)
            otra = self.ejecutar([ruta], ["13", "0"])
            self.assertIn("solicitudes: 7", otra)

    def test_opcion_invalida_no_cierra(self):
        texto = self.ejecutar([], ["x", "0"])
        self.assertIn("opcion no valida", texto)


class prueba_notificaciones(unittest.TestCase):

    def test_se_avisa_al_asignar_y_al_cancelar_en_orden_de_llegada(self):
        s = sistema_monitorias(reloj=reloj_falso())
        cargar_demo(s)
        s.generar_agenda()
        self.assertEqual(len(s.notificaciones), 6)
        s.revertir_ultima_asignacion()
        mensajes = s.entregar_notificaciones()
        self.assertEqual(len(mensajes), 7)
        self.assertIn("fue asignada", mensajes[0])
        self.assertIn("cancelada", mensajes[-1])
        self.assertEqual(s.entregar_notificaciones(), [])

    def test_las_pendientes_se_guardan_y_se_cargan(self):
        s = sistema_monitorias(reloj=reloj_falso())
        cargar_demo(s)
        s.generar_agenda()
        copia = persistencia.desde_diccionario(persistencia.a_diccionario(s))
        self.assertEqual(copia.entregar_notificaciones(), s.entregar_notificaciones())

    def test_desde_el_menu(self):
        app, texto = correr(sistema_monitorias(reloj=reloj_falso()), "22", "7", "25", "25", "0")
        self.assertIn("su monitoria de calculo i fue asignada", texto)
        self.assertIn("no hay notificaciones pendientes", texto)


class prueba_api_restante(unittest.TestCase):

    def armar(self):
        s = sistema_monitorias(reloj=reloj_falso())
        calc = s.registrar_materia("calculo i", "matematicas", 1, 4)
        prog = s.registrar_materia("programacion i", "sistemas", 1, 3)
        monitor = s.registrar_monitor("carlos", 6, [calc.codigo], [])
        ana = s.registrar_estudiante("ana", 2, "ing", [])
        return s, calc, prog, monitor, ana

    def test_profesor_y_busqueda(self):
        s, calc, prog, monitor, ana = self.armar()
        profesor = s.registrar_profesor("marta", [calc.codigo])
        self.assertEqual(profesor.codigo, "p-0001")
        self.assertIn("profesor", str(profesor))
        self.assertIs(s.buscar(profesor.codigo), profesor)
        with self.assertRaises(error_validacion):
            s.registrar_profesor("marta", ["mat-9999"])
        with self.assertRaises(error_validacion):
            s.registrar_profesor("", [])

    def test_cursadas_y_areas(self):
        s, calc, prog, monitor, ana = self.armar()
        self.assertFalse(s.ha_cursado(ana.codigo, calc.codigo))
        s.registrar_cursada(ana.codigo, prog.codigo)
        s.registrar_cursada(ana.codigo, calc.codigo)
        self.assertTrue(s.ha_cursado(ana.codigo, calc.codigo))
        self.assertEqual(s.materias_cursadas(ana.codigo), ["calculo i", "programacion i"])
        self.assertEqual(sorted(s.areas_cursadas(ana.codigo).elementos()), ["matematicas", "sistemas"])
        self.assertEqual(s.areas_de_monitor(monitor.codigo).elementos(), ["matematicas"])
        self.assertEqual(s.areas_sin_monitor().elementos(), ["sistemas"])
        with self.assertRaises(error_validacion):
            s.areas_de_monitor(ana.codigo)
        with self.assertRaises(error_validacion):
            s.registrar_cursada("e-9999", calc.codigo)
        with self.assertRaises(error_validacion):
            s.registrar_cursada(ana.codigo, "mat-9999")

    def test_disponibilidad_del_estudiante_desbloquea_la_espera(self):
        s, calc, prog, monitor, ana = self.armar()
        s.agregar_disponibilidad_monitor(monitor.codigo, [("lunes", "08:00", "10:00")])
        s.solicitar(ana.codigo, calc.codigo, "par", 2.0)
        s.generar_agenda()
        self.assertEqual(s.solicitudes[0].motivo, "el estudiante no registro disponibilidad")
        asignadas = s.agregar_disponibilidad_estudiante(ana.codigo, [("lunes", "08:00", "10:00")])
        self.assertEqual(len(asignadas), 1)
        with self.assertRaises(error_validacion):
            s.agregar_disponibilidad_monitor(ana.codigo, [])
        with self.assertRaises(error_validacion):
            s.agregar_disponibilidad_estudiante(monitor.codigo, [])

    def test_monitor_sin_horarios(self):
        s, calc, prog, monitor, ana = self.armar()
        s.agregar_disponibilidad_estudiante(ana.codigo, [("lunes", "08:00", "10:00")])
        s.solicitar(ana.codigo, calc.codigo, "par", 2.0)
        s.generar_agenda()
        self.assertEqual(s.solicitudes[0].motivo, "el monitor aun no publica horarios")

    def test_ultima_asignacion_y_listados(self):
        s, calc, prog, monitor, ana = self.armar()
        self.assertIsNone(s.ultima_asignacion())
        s.agregar_disponibilidad_monitor(monitor.codigo, [("lunes", "08:00", "10:00")])
        s.agregar_disponibilidad_estudiante(ana.codigo, [("lunes", "08:00", "10:00")])
        s.solicitar(ana.codigo, calc.codigo, "par", 2.0)
        s.generar_agenda()
        self.assertEqual(s.ultima_asignacion().id, 1)
        self.assertIn("sesion nueva", s.mostrar_historial())
        self.assertEqual(s.mostrar_listado("urgencia", estado="en_espera"), "(sin solicitudes)")

    def test_persistencia_con_profesor(self):
        s, calc, prog, monitor, ana = self.armar()
        s.registrar_profesor("marta", [calc.codigo])
        copia = persistencia.desde_diccionario(persistencia.a_diccionario(s))
        self.assertEqual(persistencia.a_diccionario(copia), persistencia.a_diccionario(s))


if __name__ == "__main__":
    unittest.main()
