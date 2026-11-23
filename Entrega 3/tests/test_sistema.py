import random
import unittest

from monitorias.errores import error_validacion
from monitorias.sistema import sistema_monitorias
from monitorias.tiempo import cubierto, cupo, duracion_min


class reloj_falso:

    def __init__(self, inicio=100.0):
        self.ahora = inicio

    def __call__(self):
        return self.ahora

    def avanzar(self, dias):
        self.ahora += dias


def base(**opciones):
    s = sistema_monitorias(reloj=reloj_falso(), **opciones)
    calc = s.registrar_materia("calculo i", "matematicas", 1, 4)
    prog = s.registrar_materia("programacion i", "sistemas", 1, 3)
    return s, calc, prog


class prueba_registro(unittest.TestCase):

    def test_codigos_consecutivos_y_sin_huecos_si_falla_la_validacion(self):
        s = sistema_monitorias()
        with self.assertRaises(error_validacion):
            s.registrar_materia("", "x", 1, 3)
        self.assertEqual(s.registrar_materia("a", "x", 1, 3).codigo, "mat-0001")
        with self.assertRaises(error_validacion):
            s.registrar_estudiante("ana", 99, "ing", [])
        self.assertEqual(s.registrar_estudiante("ana", 2, "ing", []).codigo, "e-0001")

    def test_entradas_de_tipo_incorrecto_son_errores_de_validacion(self):
        s, calc, prog = base()
        for args in [("x", "y", "3", 2), ("x", "y", 2, "3"), (None, "y", 1, 1), ("x", "y", 2.5, 4), ("x", None, 1, 1)]:
            with self.assertRaises(error_validacion):
                s.registrar_materia(*args)
        for args in [(None, 2, "ing"), ("ana", "2", "ing"), ("ana", 2, ""), ("ana", True, "ing")]:
            with self.assertRaises(error_validacion):
                s.registrar_estudiante(*args)
        with self.assertRaises(error_validacion):
            s.registrar_monitor("carlos", 5, [], [])
        with self.assertRaises(error_validacion):
            s.registrar_monitor("carlos", 5, ["mat-9999"], [])
        with self.assertRaises(error_validacion):
            s.registrar_estudiante("ana", 2, "ing", [("lunes", "8:5", "9:00")])

    def test_buscar_y_comparaciones(self):
        s, calc, prog = base()
        e = s.registrar_estudiante("ana", 2, "ing", [])
        self.assertIs(s.buscar(e.codigo), e)
        self.assertIs(s.buscar(calc.codigo), calc)
        self.assertIsNone(s.buscar("zzz-1"))
        info = s.buscar_con_comparaciones(e.codigo)
        self.assertIs(info["objeto"], e)
        self.assertLessEqual(info["comparaciones_avl"], info["altura_avl"])
        self.assertIsNone(s.buscar_con_comparaciones("e-0099")["objeto"])
        with self.assertRaises(error_validacion):
            s.buscar_con_comparaciones(5)

    def test_indices_ordenados_por_codigo_aun_pasando_de_9999(self):
        s = sistema_monitorias()
        s.codigos.contadores["mat"] = 9998
        for i in range(3):
            s.registrar_materia("m" + str(i), "x", 1, 3)
        codigos = [m.codigo for m in s.indice_materias.valores()]
        self.assertEqual(codigos, ["mat-9999", "mat-10000", "mat-10001"])


class prueba_asignacion(unittest.TestCase):

    def test_flujo_basico_y_lista_de_espera(self):
        s, calc, prog = base()
        fis = s.registrar_materia("fisica i", "ciencias", 1, 3)
        s.registrar_monitor("carlos", 6, [calc.codigo, prog.codigo], [("lunes", "08:00", "12:00")])
        ana = s.registrar_estudiante("ana", 2, "ing", [("lunes", "08:00", "10:00")])
        sara = s.registrar_estudiante("sara", 2, "ing", [("lunes", "10:00", "12:00")])
        s.solicitar(ana.codigo, calc.codigo, "par", 2.0)
        s.solicitar(sara.codigo, fis.codigo, "puntual", 3.0)
        s.generar_agenda()
        estados = {x.estudiante.nombre: x.estado for x in s.solicitudes}
        self.assertEqual(estados, {"ana": "asignada", "sara": "en_espera"})
        self.assertEqual(s.solicitudes[1].motivo, "no hay monitor para la materia")
        s.registrar_monitor("hugo", 5, [fis.codigo], [("lunes", "10:00", "12:00")])
        self.assertEqual(s.solicitudes[1].estado, "asignada")
        self.assertEqual(len(s.agenda.sesiones), 2)
        self.assertEqual(s.informe_cobertura()["porcentaje"], 100.0)

    def test_bloques_contiguos_se_tratan_como_uno_solo(self):
        s, calc, prog = base()
        s.registrar_monitor("mon", 5, [calc.codigo], [("lunes", "08:00", "09:00"), ("lunes", "09:00", "10:00")])
        e = s.registrar_estudiante("est", 2, "ing", [("lunes", "08:30", "09:30")])
        s.solicitar(e.codigo, calc.codigo, "par", 3.0)
        s.generar_agenda()
        self.assertEqual(s.solicitudes[0].estado, "asignada")
        sesion = s.agenda.sesiones[0]
        self.assertEqual((sesion.inicio, sesion.fin), (510, 570))

    def test_bloque_agregado_despues_contiguo_al_anterior(self):
        s, calc, prog = base()
        m = s.registrar_monitor("mon", 5, [calc.codigo], [("lunes", "08:00", "09:00")])
        e = s.registrar_estudiante("est", 2, "ing", [("lunes", "08:30", "09:30")])
        s.solicitar(e.codigo, calc.codigo, "par", 3.0)
        s.generar_agenda()
        self.assertEqual(s.solicitudes[0].estado, "en_espera")
        s.agregar_disponibilidad_monitor(m.codigo, [("lunes", "09:00", "10:00")])
        self.assertEqual(s.solicitudes[0].estado, "asignada")

    def test_grupos_con_cupo_de_cinco(self):
        s, calc, prog = base()
        s.registrar_monitor("mon", 5, [calc.codigo], [("lunes", "08:00", "12:00")])
        for i in range(7):
            e = s.registrar_estudiante("e" + str(i), 2, "ing", [("lunes", "08:00", "12:00")])
            s.solicitar(e.codigo, calc.codigo, "general", 3.0)
        s.generar_agenda()
        tamanos = sorted(len(x.estudiantes) for x in s.agenda.sesiones)
        self.assertEqual(tamanos, [2, 5])
        self.assertTrue(all(x.estado == "asignada" for x in s.solicitudes))

    def test_el_mas_urgente_se_atiende_primero(self):
        s, calc, prog = base()
        s.registrar_monitor("mon", 5, [calc.codigo], [("lunes", "08:00", "09:00")])
        tranquilo = s.registrar_estudiante("tranquilo", 2, "ing", [("lunes", "08:00", "09:00")])
        apurado = s.registrar_estudiante("apurado", 2, "ing", [("lunes", "08:00", "09:00")])
        s.solicitar(tranquilo.codigo, calc.codigo, "par", 4.8)
        s.solicitar(apurado.codigo, calc.codigo, "par", 1.5)
        s.generar_agenda()
        estados = {x.estudiante.nombre: x.estado for x in s.solicitudes}
        self.assertEqual(estados, {"tranquilo": "en_espera", "apurado": "asignada"})

    def test_envejecimiento_con_reloj_inyectado(self):
        for dias, esperado in [(3.0, ["b", "a"]), (7.0, ["a", "b"])]:
            s, calc, prog = base()
            a = s.registrar_estudiante("a", 2, "ing", [])
            b = s.registrar_estudiante("b", 2, "ing", [])
            s.solicitar(a.codigo, calc.codigo, "par", 4.5)
            s.reloj.avanzar(dias)
            s.solicitar(b.codigo, prog.codigo, "par", 1.0)
            self.assertEqual([x.estudiante.nombre for x in s.cola.pendientes()], esperado)

    def test_solicitud_vieja_de_baja_urgencia_termina_pasando_al_frente(self):
        s, calc, prog = base()
        reloj = s.reloj
        viejo = s.registrar_estudiante("viejo", 2, "ing", [])
        s.solicitar(viejo.codigo, calc.codigo, "par", 4.9)
        reloj.avanzar(8.0)
        nuevo = s.registrar_estudiante("nuevo", 2, "ing", [])
        s.solicitar(nuevo.codigo, prog.codigo, "par", 0.0)
        self.assertEqual(s.cola.pendientes()[0].estudiante.nombre, "viejo")

    def test_solicitudes_duplicadas_se_rechazan(self):
        s, calc, prog = base()
        e = s.registrar_estudiante("ana", 2, "ing", [])
        s.solicitar(e.codigo, calc.codigo, "par", 3.0)
        with self.assertRaises(error_validacion):
            s.solicitar(e.codigo, calc.codigo, "puntual", 2.0)
        s.solicitar(e.codigo, prog.codigo, "par", 2.0)
        self.assertEqual(len(s.solicitudes), 2)

    def test_validaciones_de_solicitar(self):
        s, calc, prog = base()
        e = s.registrar_estudiante("ana", 1, "ing", [])
        avanzada = s.registrar_materia("avanzada", "x", 5, 3)
        for args in [("e-9999", calc.codigo, "par", 3.0), (e.codigo, "mat-9999", "par", 3.0),
                     (e.codigo, calc.codigo, "raro", 3.0), (e.codigo, calc.codigo, ["par"], 3.0),
                     (e.codigo, calc.codigo, "par", 7.0), (e.codigo, calc.codigo, "par", "3"),
                     (e.codigo, calc.codigo, "par", None), (e.codigo, avanzada.codigo, "par", 3.0),
                     (5, calc.codigo, "par", 3.0), (e.codigo, 5, "par", 3.0)]:
            with self.assertRaises(error_validacion):
                s.solicitar(*args)
        self.assertEqual(len(s.solicitudes), 0)

    def test_tasa_historica_cuando_no_hay_nota(self):
        s = sistema_monitorias()
        m = s.registrar_materia("calculo", "mat", 1, 4, tasa_reprobacion=0.4)
        e = s.registrar_estudiante("ana", 1, "ing", [])
        sol = s.solicitar(e.codigo, m.codigo, "par")
        self.assertAlmostEqual(sol.riesgo, 0.4)


class prueba_prerrequisitos_en_el_sistema(unittest.TestCase):

    def armar(self, **opciones):
        s = sistema_monitorias(reloj=reloj_falso(), **opciones)
        c1 = s.registrar_materia("calculo i", "mat", 1, 4)
        c2 = s.registrar_materia("calculo ii", "mat", 2, 4)
        f2 = s.registrar_materia("fisica ii", "cie", 2, 4)
        s.agregar_prerrequisito(c2.codigo, c1.codigo)
        s.agregar_prerrequisito(f2.codigo, c2.codigo)
        e = s.registrar_estudiante("ana", 3, "ing", [])
        return s, c1, c2, f2, e

    def test_se_exigen_los_prerrequisitos_directos(self):
        s, c1, c2, f2, e = self.armar()
        with self.assertRaises(error_validacion) as contexto:
            s.solicitar(e.codigo, c2.codigo, "par", 2.0)
        self.assertIn("calculo i", str(contexto.exception))
        s.registrar_cursada(e.codigo, c1.codigo)
        self.assertEqual(s.solicitar(e.codigo, c2.codigo, "par", 2.0).estado, "pendiente")

    def test_se_puede_desactivar_la_exigencia(self):
        s, c1, c2, f2, e = self.armar(exigir_prerrequisitos=False)
        self.assertEqual(s.solicitar(e.codigo, f2.codigo, "par", 2.0).estado, "pendiente")

    def test_impacto_en_la_urgencia(self):
        s, c1, c2, f2, e = self.armar(exigir_prerrequisitos=False)
        otra = s.registrar_estudiante("beto", 3, "ing", [])
        base_malla = s.solicitar(e.codigo, c1.codigo, "par", 2.5)
        final = s.solicitar(otra.codigo, f2.codigo, "par", 2.5)
        self.assertAlmostEqual(base_malla.urgencia, 0.75)
        self.assertAlmostEqual(final.urgencia, 0.25)

    def test_cadena_rutas_y_faltantes(self):
        s, c1, c2, f2, e = self.armar()
        self.assertEqual(s.cadena_de(f2.codigo), ["calculo i", "calculo ii"])
        self.assertEqual(s.rutas_de(f2.codigo), [["fisica ii", "calculo ii", "calculo i"]])
        self.assertEqual(s.faltantes_de(e.codigo, f2.codigo), ["calculo i", "calculo ii"])
        self.assertEqual(s.plan_para(e.codigo, f2.codigo), ["calculo i", "calculo ii"])
        with self.assertRaises(error_validacion):
            s.agregar_prerrequisito(c1.codigo, f2.codigo)

    def test_informes_de_la_red(self):
        s, c1, c2, f2, e = self.armar()
        s.registrar_materia("etica", "hum", 1, 2)
        r = s.informe_red()
        self.assertEqual((r["materias"], r["relaciones"]), (4, 2))
        self.assertEqual(r["islas"], [["calculo i", "calculo ii", "fisica ii"], ["etica"]])
        self.assertEqual(r["ciclos"], [])
        self.assertEqual(r["ruta_critica"], ["calculo i", "calculo ii", "fisica ii"])
        self.assertEqual(s.ruta_entre(c1.codigo, f2.codigo)["dirigida"], ["calculo i", "calculo ii", "fisica ii"])
        self.assertIsNone(s.ruta_entre(f2.codigo, c1.codigo)["dirigida"])
        self.assertEqual(len(s.ruta_entre(f2.codigo, c1.codigo)["sin_direccion"]), 3)
        self.assertEqual(s.impacto_de(c1.codigo), [["calculo i"], ["calculo ii"], ["fisica ii"]])
        orden = s.orden_de_cursado()
        self.assertTrue(orden.index("calculo i") < orden.index("calculo ii") < orden.index("fisica ii"))
        self.assertIn("islas desconectadas: 2", s.mostrar_red())


class prueba_reversion(unittest.TestCase):

    def armar(self):
        s, calc, prog = base()
        s.registrar_monitor("mon", 5, [calc.codigo], [("lunes", "08:00", "09:00")])
        a = s.registrar_estudiante("a", 2, "ing", [("lunes", "08:00", "09:00")])
        b = s.registrar_estudiante("b", 2, "ing", [("lunes", "08:00", "09:00")])
        return s, calc, a, b

    def test_lo_revertido_no_se_reasigna_solo(self):
        s, calc, a, b = self.armar()
        s.solicitar(a.codigo, calc.codigo, "par", 3.0)
        s.generar_agenda()
        s.revertir_ultima_asignacion()
        solicitud = s.solicitudes[0]
        self.assertEqual((solicitud.estado, solicitud.motivo), ("en_espera", "asignacion revertida"))
        s.registrar_monitor("otro", 6, [calc.codigo], [("martes", "08:00", "09:00")])
        self.assertEqual(solicitud.estado, "en_espera")
        self.assertEqual(len(s.agenda.sesiones), 0)
        s.reencolar(solicitud.id)
        self.assertEqual(solicitud.estado, "asignada")

    def test_reencolar_solo_acepta_revertidas(self):
        s, calc, a, b = self.armar()
        s.solicitar(a.codigo, calc.codigo, "par", 3.0)
        with self.assertRaises(error_validacion):
            s.reencolar(1)
        with self.assertRaises(error_validacion):
            s.reencolar(99)

    def test_al_revertir_el_hueco_pasa_a_quien_esperaba(self):
        s, calc, a, b = self.armar()
        s.solicitar(a.codigo, calc.codigo, "par", 1.0)
        s.solicitar(b.codigo, calc.codigo, "par", 4.0)
        s.generar_agenda()
        self.assertEqual([x.estado for x in s.solicitudes], ["asignada", "en_espera"])
        s.revertir_ultima_asignacion()
        self.assertEqual([x.estado for x in s.solicitudes], ["en_espera", "asignada"])
        self.assertEqual(s.agenda.sesiones[0].estudiantes[0].nombre, "b")

    def test_orden_de_atencion_sin_repetidos_y_actualizado(self):
        s, calc, a, b = self.armar()
        s.solicitar(a.codigo, calc.codigo, "par", 1.0)
        s.generar_agenda()
        s.registrar_monitor("otro", 6, [calc.codigo], [("lunes", "08:00", "09:00")])
        self.assertEqual(s.orden_atencion, [1])
        s.revertir_ultima_asignacion()
        self.assertEqual(s.orden_atencion, [])

    def test_revertir_todo_en_cadena(self):
        s, calc, prog = base()
        s.registrar_monitor("mon", 5, [calc.codigo], [("lunes", "08:00", "12:00")])
        for i in range(4):
            e = s.registrar_estudiante("e" + str(i), 2, "ing", [("lunes", "08:00", "12:00")])
            s.solicitar(e.codigo, calc.codigo, "general", 3.0)
        s.generar_agenda()
        self.assertEqual(len(s.historial), 4)
        while not s.historial.esta_vacia():
            s.revertir_ultima_asignacion()
        self.assertEqual(len(s.agenda.sesiones), 0)
        self.assertTrue(all(x.estado == "en_espera" and x.revertida for x in s.solicitudes))
        with self.assertRaises(error_validacion):
            s.revertir_ultima_asignacion()


class prueba_consultas(unittest.TestCase):

    def armar(self):
        s, calc, prog = base()
        est = []
        for i, nota in enumerate([1.0, 2.0, 3.0, 4.0, 5.0]):
            e = s.registrar_estudiante("e" + str(i), 2, "ing", [])
            est.append(s.solicitar(e.codigo, calc.codigo if i % 2 == 0 else prog.codigo, "par", nota))
        return s, est

    def test_buscar_solicitud_por_busqueda_binaria(self):
        s, est = self.armar()
        encontrada, comparaciones = s.buscar_solicitud(4)
        self.assertEqual(encontrada.id, 4)
        self.assertLessEqual(comparaciones, 3)
        self.assertIsNone(s.buscar_solicitud(99)[0])

    def test_rango_de_urgencia_contra_fuerza_bruta(self):
        s, est = self.armar()
        for a, b in [(0.0, 1.0), (0.2, 0.6), (0.9, 1.0), (0.5, 0.5)]:
            encontradas, visitados = s.solicitudes_por_urgencia(a, b)
            esperadas = sorted((x for x in s.solicitudes if a <= x.urgencia <= b), key=lambda x: (x.urgencia, x.id))
            self.assertEqual([x.id for x in encontradas], [x.id for x in esperadas])
            self.assertLessEqual(visitados, len(s.solicitudes))

    def test_listados_ordenados_coinciden_entre_metodos(self):
        s, est = self.armar()
        for criterio in ["urgencia", "antiguedad", "materia"]:
            resultados = [[x.id for x in s.listar_solicitudes(criterio, m)] for m in ("insercion", "mezcla", "rapido")]
            self.assertTrue(resultados[0] == resultados[1] == resultados[2])
        primero = s.listar_solicitudes("urgencia")[0]
        self.assertEqual(primero.estudiante.nombre, "e0")
        self.assertIn("pendiente", s.mostrar_listado("urgencia", estado="pendiente"))

    def test_textos_de_apoyo(self):
        s, est = self.armar()
        self.assertIn("pendientes", s.mostrar_cola())
        self.assertIn("calculo i", s.mostrar_catalogo())
        self.assertIn("matematicas", s.mostrar_areas())
        self.assertEqual(s.mostrar_historial(), "(sin asignaciones)")
        self.assertIn("solicitudes: 5", s.mostrar_informe())


def verificar_invariantes(prueba, s):
    sesiones = s.agenda.sesiones
    for i, a in enumerate(sesiones):
        prueba.assertLessEqual(len(a.estudiantes), cupo[a.tipo])
        prueba.assertGreaterEqual(len(a.estudiantes), 1)
        prueba.assertEqual(a.fin - a.inicio, duracion_min[a.tipo])
        prueba.assertTrue(cubierto(a.monitor.disponibilidad, a.dia, a.inicio, a.fin))
        for e in a.estudiantes:
            prueba.assertTrue(cubierto(e.disponibilidad, a.dia, a.inicio, a.fin))
        for b in sesiones[i + 1:]:
            if a.monitor.codigo == b.monitor.codigo:
                prueba.assertFalse(a.se_cruza(b.dia, b.inicio, b.fin))
            for e in a.estudiantes:
                if e in b.estudiantes:
                    prueba.assertFalse(a.se_cruza(b.dia, b.inicio, b.fin))
    asignadas = [x for x in s.solicitudes if x.estado == "asignada"]
    prueba.assertEqual(sum(len(a.estudiantes) for a in sesiones), len(asignadas))
    for x in asignadas:
        donde = [a for a in sesiones if x.estudiante in a.estudiantes and a.materia.codigo == x.materia.codigo]
        prueba.assertEqual(len(donde), 1)
    prueba.assertEqual(len(s.historial), len(asignadas))
    prueba.assertEqual(sorted(s.orden_atencion), sorted(x.id for x in asignadas))


class prueba_aleatoria(unittest.TestCase):

    def bloques(self, azar):
        resultado = []
        for _ in range(azar.randint(1, 3)):
            dia = azar.choice(["lunes", "martes", "miercoles"])
            inicio = azar.choice([8, 9, 10, 11, 13, 14, 15])
            resultado.append((dia, f"{inicio:02d}:00", f"{inicio + azar.randint(1, 3):02d}:00"))
        return resultado

    def test_invariantes_con_muchas_configuraciones(self):
        for semilla in range(150):
            random.seed(semilla)
            azar = random
            s = sistema_monitorias(reloj=reloj_falso())
            materias = [s.registrar_materia("m" + str(i), "area", 1, azar.randint(1, 5)) for i in range(3)]
            for i in range(azar.randint(1, 3)):
                elegidas = [m.codigo for m in azar.sample(materias, azar.randint(1, 3))]
                s.registrar_monitor("mon" + str(i), 5, elegidas, self.bloques(azar))
            for i in range(azar.randint(3, 10)):
                e = s.registrar_estudiante("est" + str(i), 3, "ing", self.bloques(azar))
                for m in azar.sample(materias, azar.randint(1, 2)):
                    s.solicitar(e.codigo, m.codigo, azar.choice(["par", "general", "puntual"]), azar.uniform(0, 5))
            s.generar_agenda()
            verificar_invariantes(self, s)
            total = len(s.solicitudes)
            self.assertEqual(sum(1 for x in s.solicitudes if x.estado in ("asignada", "en_espera")), total)
            self.assertEqual(len(s.cola), 0)
            for _ in range(azar.randint(0, len(s.historial))):
                if not s.historial.esta_vacia():
                    revertida = s.revertir_ultima_asignacion()
                    self.assertTrue(revertida.revertida)
                    verificar_invariantes(self, s)
            s.reintentar_lista_espera()
            verificar_invariantes(self, s)
            for x in s.solicitudes:
                if x.revertida:
                    self.assertEqual(x.estado, "en_espera")


if __name__ == "__main__":
    unittest.main()
