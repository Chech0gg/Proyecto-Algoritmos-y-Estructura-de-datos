import unittest

from monitorias import cuentas, persistencia, prioridad
from monitorias.cli import aplanar, consola, menu_administrador, menu_estudiante, menu_monitor, menus
from monitorias.errores import error_validacion
from monitorias.sistema import sistema_monitorias
from tests.test_persistencia_cli import guion
from tests.test_sistema import reloj_falso, verificar_invariantes


def armar(general=False):
    s = sistema_monitorias(reloj=reloj_falso())
    s.registrar_materia("calculo i", "matematicas", 1, 4)
    s.registrar_materia("fisica i", "ciencias", 1, 3)
    s.registrar_cuenta_monitor("carlos", "carlos12", "carlos", 6, ["mat-0001"], [("lunes", "08:00", "12:00")])
    disponibilidad = [("lunes", "08:00", "12:00")] if general else [("lunes", "08:00", "10:00")]
    s.registrar_cuenta_estudiante("ana", "ana12345", "ana", 2, "ing", disponibilidad)
    otra = [("lunes", "08:00", "12:00")] if general else [("lunes", "09:00", "11:00")]
    s.registrar_cuenta_estudiante("luis", "luis1234", "luis", 2, "ing", otra)
    s.registrar_cuenta_administrador("admin", "admin12345", "admin")
    return s


def nombres(menu):
    return [metodo for texto, metodo in aplanar(menu)]


class prueba_cuentas(unittest.TestCase):

    def test_la_clave_no_se_guarda_en_claro_y_se_verifica(self):
        s = armar()
        cuenta = s.cuentas.obtener("ana")
        self.assertNotIn("ana12345", cuenta.clave_hash)
        self.assertEqual(len(cuenta.sal), 32)
        self.assertNotEqual(s.cuentas.obtener("luis").clave_hash, cuenta.clave_hash)
        self.assertEqual(s.iniciar_sesion("ANA", "ana12345").rol, "estudiante")
        self.assertEqual(s.iniciar_sesion("carlos", "carlos12").rol, "monitor")
        self.assertEqual(s.iniciar_sesion("admin", "admin12345").rol, "administrador")

    def test_mismo_mensaje_si_el_usuario_no_existe_o_la_clave_falla(self):
        s = armar()
        with self.assertRaises(error_validacion) as sin_usuario:
            s.iniciar_sesion("nadie", "ana12345")
        with self.assertRaises(error_validacion) as mala_clave:
            s.iniciar_sesion("ana", "otra-cosa")
        self.assertIn("usuario o contrasena incorrectos", str(sin_usuario.exception))
        self.assertIn("usuario o contrasena incorrectos", str(mala_clave.exception))
        with self.assertRaises(error_validacion):
            s.iniciar_sesion("", "x")

    def test_se_bloquea_al_tercer_intento_y_el_administrador_desbloquea(self):
        s = armar()
        for _ in range(2):
            with self.assertRaises(error_validacion):
                s.iniciar_sesion("ana", "mala")
        with self.assertRaises(error_validacion) as bloqueo:
            s.iniciar_sesion("ana", "mala")
        self.assertIn("bloqueada", str(bloqueo.exception))
        with self.assertRaises(error_validacion) as aun:
            s.iniciar_sesion("ana", "ana12345")
        self.assertIn("bloqueada", str(aun.exception))
        s.cuentas.desbloquear("ana")
        self.assertEqual(s.iniciar_sesion("ana", "ana12345").usuario, "ana")

    def test_un_acierto_reinicia_el_conteo(self):
        s = armar()
        with self.assertRaises(error_validacion):
            s.iniciar_sesion("ana", "mala")
        s.iniciar_sesion("ana", "ana12345")
        self.assertEqual(s.cuentas.obtener("ana").intentos, 0)

    def test_validacion_de_usuario_y_clave(self):
        s = armar()
        for usuario in ["ab", "con espacio", "x" * 21, "a/b", 5, None]:
            with self.assertRaises(error_validacion):
                s.registrar_cuenta_administrador(usuario, "clave123", "x")
        for clave in ["corta", "con espacio1", " clave123", None, 123456]:
            with self.assertRaises(error_validacion):
                s.registrar_cuenta_administrador("nuevo", clave, "x")
        with self.assertRaises(error_validacion):
            s.registrar_cuenta_administrador("ANA", "clave123", "x")
        with self.assertRaises(error_validacion):
            s.registrar_cuenta_administrador("nuevo", "clave123", " ")

    def test_si_falla_el_registro_no_queda_ni_persona_ni_cuenta(self):
        s = armar()
        personas = len(s.personas)
        with self.assertRaises(error_validacion):
            s.registrar_cuenta_estudiante("nuevo", "clave123", "pedro", 99, "ing")
        with self.assertRaises(error_validacion):
            s.registrar_cuenta_monitor("nuevo", "clave123", "pedro", 3, [])
        with self.assertRaises(error_validacion):
            s.registrar_cuenta_estudiante("ana", "clave123", "otra ana", 2, "ing")
        self.assertEqual(len(s.personas), personas)
        self.assertFalse(s.cuentas.existe("nuevo"))

    def test_cambiar_y_restablecer_la_clave(self):
        s = armar()
        with self.assertRaises(error_validacion):
            s.cuentas.cambiar_clave("ana", "incorrecta", "nueva123")
        s.cuentas.cambiar_clave("ana", "ana12345", "nueva123")
        with self.assertRaises(error_validacion):
            s.iniciar_sesion("ana", "ana12345")
        self.assertEqual(s.iniciar_sesion("ana", "nueva123").usuario, "ana")
        s.cuentas.restablecer_clave("luis", "reinicio1")
        self.assertEqual(s.iniciar_sesion("luis", "reinicio1").usuario, "luis")
        with self.assertRaises(error_validacion):
            s.cuentas.restablecer_clave("nadie", "reinicio1")
        with self.assertRaises(error_validacion):
            s.cuentas.desbloquear("nadie")

    def test_cuenta_ligada_a_persona_y_listado(self):
        s = armar()
        self.assertEqual(s.cuentas.de_persona("e-0001").usuario, "ana")
        self.assertIsNone(s.cuentas.de_persona("e-0099"))
        self.assertEqual(s.cuentas.contar_administradores(), 1)
        texto = s.mostrar_cuentas()
        self.assertIn("administrador", texto)
        self.assertLess(texto.index("ana"), texto.index("carlos"))
        self.assertLess(texto.index("carlos"), texto.index("admin "))
        self.assertEqual(sistema_monitorias().mostrar_cuentas(), "(sin usuarios)")
        with self.assertRaises(error_validacion):
            cuentas.clase_cuenta("x", "x", "jefe", None, "00", "")
        with self.assertRaises(error_validacion):
            s.cuentas.crear("otro", "clave123", "otro", "estudiante")


class prueba_prioridad_con_promedio(unittest.TestCase):

    def test_la_nota_esperada_es_una_combinacion_convexa(self):
        self.assertAlmostEqual(prioridad.nota_esperada(2.0, 4.0), 0.7 * 2.0 + 0.3 * 4.0)
        self.assertEqual(prioridad.nota_esperada(3.0, 3.0), 3.0)
        with self.assertRaises(error_validacion):
            prioridad.nota_esperada(6, 3)
        with self.assertRaises(error_validacion):
            prioridad.nota_esperada(3, -1)

    def test_un_buen_promedio_baja_el_riesgo_y_uno_malo_lo_sube(self):
        solo = prioridad.calcular_prioridad(2.5, None, 3, 6)
        bueno = prioridad.calcular_prioridad(2.5, None, 3, 6, 4.5)
        malo = prioridad.calcular_prioridad(2.5, None, 3, 6, 1.5)
        self.assertLess(bueno.urgencia, solo.urgencia)
        self.assertGreater(malo.urgencia, solo.urgencia)
        self.assertIn("ponderados", bueno.desglose)

    def test_el_riesgo_sigue_siendo_monotono_en_la_nota_con_promedio_fijo(self):
        anterior = 2.0
        for nota in [0, 1, 2, 3, 4, 5]:
            actual = prioridad.calcular_prioridad(nota, None, 2, 5, 3.5).riesgo
            self.assertLessEqual(actual, anterior)
            anterior = actual

    def test_sin_nota_se_usa_la_tasa_y_en_ultimo_caso_el_promedio(self):
        con_tasa = prioridad.calcular_prioridad(None, 0.4, 1, 3, 4.0)
        self.assertIn("tasa historica", con_tasa.desglose)
        solo_promedio = prioridad.calcular_prioridad(None, None, 1, 3, 2.0)
        self.assertIn("promedio 2.0", solo_promedio.desglose)
        with self.assertRaises(error_validacion):
            prioridad.calcular_prioridad(None, None, 1, 3)
        with self.assertRaises(error_validacion):
            prioridad.calcular_prioridad(3.0, None, 1, 3, 7)

    def test_el_sistema_guarda_el_promedio_de_la_solicitud(self):
        s = armar()
        solicitud = s.solicitar("e-0001", "mat-0001", "par", 2.5, 3.8)
        self.assertEqual(solicitud.promedio, 3.8)
        self.assertIn("ponderados", solicitud.desglose)
        with self.assertRaises(error_validacion):
            s.solicitar("e-0002", "mat-0001", "par", 2.5, 9)


class prueba_cancelar_solicitud(unittest.TestCase):

    def test_cancelar_una_pendiente_la_saca_de_la_cola_y_libera_el_cupo(self):
        s = armar()
        s.solicitar("e-0001", "mat-0001", "par", 2.0)
        s.cancelar_solicitud(1, "e-0001")
        self.assertEqual(s.solicitudes[0].estado, "cancelada")
        self.assertEqual(len(s.cola), 0)
        s.solicitar("e-0001", "mat-0001", "par", 2.0)
        self.assertEqual(s.solicitudes[1].estado, "pendiente")
        verificar_invariantes(self, s)

    def test_cancelar_una_en_espera(self):
        s = armar()
        s.solicitar("e-0001", "mat-0002", "par", 2.0)
        s.generar_agenda()
        self.assertEqual(len(s.lista_espera), 1)
        s.cancelar_solicitud(1, "e-0001")
        self.assertEqual(len(s.lista_espera), 0)

    def test_cancelar_una_asignada_deshace_la_sesion_y_el_historial(self):
        s = armar()
        s.solicitar("e-0001", "mat-0001", "par", 2.0)
        s.generar_agenda()
        self.assertEqual(len(s.agenda.sesiones), 1)
        s.cancelar_solicitud(1, "e-0001")
        self.assertEqual(s.agenda.sesiones, [])
        self.assertTrue(s.historial.esta_vacia())
        self.assertEqual(s.orden_atencion, [])
        self.assertEqual(s.informe_cobertura()["total"], 0)
        self.assertEqual(s.informe_cobertura()["canceladas"], 1)
        self.assertIn("canceladas", s.mostrar_informe())
        self.assertEqual(s.solicitudes_por_urgencia(0, 1)[0], [])
        verificar_invariantes(self, s)

    def test_no_se_puede_cancelar_lo_ajeno_ni_dos_veces(self):
        s = armar()
        s.solicitar("e-0001", "mat-0001", "par", 2.0)
        with self.assertRaises(error_validacion):
            s.cancelar_solicitud(1, "e-0002")
        with self.assertRaises(error_validacion):
            s.cancelar_solicitud(99, "e-0001")
        s.cancelar_solicitud(1, "e-0001")
        with self.assertRaises(error_validacion):
            s.cancelar_solicitud(1, "e-0001")

    def test_al_cancelar_se_libera_el_hueco_para_la_lista_de_espera(self):
        s = armar()
        s.solicitar("e-0001", "mat-0001", "par", 2.0)
        s.solicitar("e-0002", "mat-0001", "par", 3.0)
        s.registrar_cuenta_monitor("hugo", "hugo1234", "hugo", 5, ["mat-0001"], [])
        s.generar_agenda()
        self.assertEqual(s.solicitudes[1].estado, "asignada")
        s.cancelar_solicitud(1, "e-0001", por_administrador=True)
        self.assertIn("cancelada por el administrador", s.entregar_notificaciones()[-1])

    def test_cancelar_a_quien_creo_el_grupo_no_deja_sesiones_vacias(self):
        s = armar(general=True)
        s.solicitar("e-0001", "mat-0001", "general", 2.0)
        s.solicitar("e-0002", "mat-0001", "general", 2.5)
        s.generar_agenda()
        self.assertEqual(len(s.agenda.sesiones), 1)
        self.assertEqual(len(s.agenda.sesiones[0].estudiantes), 2)
        s.cancelar_solicitud(1, "e-0001")
        self.assertEqual(len(s.agenda.sesiones), 1)
        self.assertEqual(s.agenda.sesiones[0].estudiantes[0].nombre, "luis")
        s.revertir_ultima_asignacion()
        self.assertEqual(s.agenda.sesiones, [])
        verificar_invariantes(self, s)


class prueba_agenda_del_administrador(unittest.TestCase):

    def test_agendar_a_mano(self):
        s = armar()
        s.solicitar("e-0001", "mat-0001", "par", 2.0)
        sesion = s.agendar_manual(1, "m-0001", "lunes", "09:00")
        self.assertEqual((sesion.inicio, sesion.fin), (540, 600))
        self.assertEqual(s.solicitudes[0].estado, "asignada")
        self.assertEqual(len(s.cola), 0)
        self.assertIn("agendada por el administrador", s.solicitudes[0].motivo)
        s.generar_agenda()
        self.assertEqual(len(s.agenda.sesiones), 1)
        self.assertIn("fue asignada", s.entregar_notificaciones()[0])
        verificar_invariantes(self, s)

    def test_agendar_a_mano_rechaza_lo_imposible(self):
        s = armar()
        s.solicitar("e-0001", "mat-0001", "par", 2.0)
        s.solicitar("e-0002", "mat-0002", "par", 2.0)
        s.solicitar("e-0002", "mat-0001", "par", 2.0)
        casos = [(5, "m-0001", "lunes", "09:00"), (1, "m-0009", "lunes", "09:00"), (2, "m-0001", "lunes", "09:00"),
                 (1, "m-0001", "lunes", "10:00"), (1, "m-0001", "martes", "09:00"), (1, "m-0001", "lunes", "ab"),
                 (1, "m-0001", "domingo", "09:00"), (1, "m-0001", "lunes", "23:30")]
        for caso in casos:
            with self.assertRaises(error_validacion, msg=str(caso)):
                s.agendar_manual(*caso)
        s.agendar_manual(1, "m-0001", "lunes", "09:00")
        with self.assertRaises(error_validacion):
            s.agendar_manual(1, "m-0001", "lunes", "09:00")
        with self.assertRaises(error_validacion):
            s.agendar_manual(3, "m-0001", "lunes", "09:30")

    def test_modificar_una_sesion(self):
        s = armar()
        s.solicitar("e-0001", "mat-0001", "par", 2.0)
        s.generar_agenda()
        s.entregar_notificaciones()
        s.modificar_sesion(1, "lunes", "09:00")
        self.assertEqual(s.agenda.sesiones[0].inicio, 540)
        self.assertIn("cambio a lunes 09:00", s.entregar_notificaciones()[0])
        for dia, hora in [("lunes", "11:00"), ("martes", "09:00"), ("lunes", "23:30")]:
            with self.assertRaises(error_validacion):
                s.modificar_sesion(1, dia, hora)
        self.assertEqual((s.agenda.sesiones[0].dia, s.agenda.sesiones[0].inicio), ("lunes", 540))
        with self.assertRaises(error_validacion):
            s.modificar_sesion(7, "lunes", "09:00")
        with self.assertRaises(error_validacion):
            s.modificar_sesion(1, "lunes", "09:00", "m-0009")
        verificar_invariantes(self, s)

    def test_modificar_no_puede_chocar_con_otra_sesion(self):
        s = armar()
        s.solicitar("e-0001", "mat-0001", "par", 2.0)
        s.solicitar("e-0002", "mat-0001", "par", 3.0)
        s.generar_agenda()
        self.assertEqual(len(s.agenda.sesiones), 2)
        antes = [(x.dia, x.inicio) for x in s.agenda.ordenadas()]
        with self.assertRaises(error_validacion):
            s.modificar_sesion(1, "lunes", "09:30")
        self.assertEqual([(x.dia, x.inicio) for x in s.agenda.ordenadas()], antes)
        self.assertEqual(len(s.agenda.sesiones), 2)

    def test_cambiar_de_monitor(self):
        s = armar()
        s.registrar_cuenta_monitor("hugo", "hugo1234", "hugo", 5, ["mat-0001"], [("lunes", "08:00", "12:00")])
        s.solicitar("e-0001", "mat-0001", "par", 2.0)
        s.generar_agenda()
        s.modificar_sesion(1, "lunes", "08:00", "m-0002")
        self.assertEqual(s.agenda.sesiones[0].monitor.nombre, "hugo")

    def test_cancelar_una_sesion_deja_a_los_estudiantes_en_espera_hasta_reencolar(self):
        s = armar(general=True)
        s.solicitar("e-0001", "mat-0001", "general", 2.0)
        s.solicitar("e-0002", "mat-0001", "general", 2.5)
        s.generar_agenda()
        s.entregar_notificaciones()
        s.cancelar_sesion(1)
        self.assertEqual(s.agenda.sesiones, [])
        self.assertTrue(s.historial.esta_vacia())
        self.assertEqual([x.estado for x in s.solicitudes], ["en_espera", "en_espera"])
        self.assertEqual(len(s.entregar_notificaciones()), 2)
        s.reintentar_lista_espera()
        self.assertEqual(s.agenda.sesiones, [])
        s.reencolar(1)
        s.reencolar(2)
        self.assertEqual(len(s.agenda.sesiones), 1)
        with self.assertRaises(error_validacion):
            s.cancelar_sesion(5)
        verificar_invariantes(self, s)

    def test_vistas_para_el_administrador(self):
        s = armar()
        self.assertEqual(s.mostrar_agenda_numerada(), "(agenda vacia)")
        s.solicitar("e-0001", "mat-0001", "par", 2.0)
        s.generar_agenda()
        self.assertTrue(s.mostrar_agenda_numerada().startswith(" 1. lunes"))
        horarios = s.mostrar_horarios_monitores()
        self.assertIn("carlos", horarios)
        self.assertIn("horas publicadas: 4.0 | agendadas: 1.0", horarios)
        self.assertIn("e-0001 ana: lunes 08:00-10:00", s.mostrar_horarios_estudiantes())
        self.assertEqual(sistema_monitorias().mostrar_horarios_monitores(), "(no hay monitores)")
        self.assertEqual(sistema_monitorias().mostrar_horarios_estudiantes(), "(no hay estudiantes)")


class prueba_paneles_de_estudiante_y_monitor(unittest.TestCase):

    def test_sesiones_y_solicitudes_de_cada_uno(self):
        s = armar()
        self.assertEqual(s.mostrar_solicitudes_de("e-0001"), "(no ha pedido monitorias)")
        self.assertEqual(s.mostrar_sesiones_de("e-0001"), "(sin sesiones agendadas)")
        s.solicitar("e-0001", "mat-0001", "par", 2.0)
        s.generar_agenda()
        self.assertIn("asignada", s.mostrar_solicitudes_de("e-0001"))
        self.assertIn("monitor: carlos", s.mostrar_sesiones_de("e-0001"))
        self.assertIn("estudiantes: ana", s.mostrar_sesiones_de("m-0001"))
        self.assertEqual(s.mostrar_sesiones_de("e-0002"), "(sin sesiones agendadas)")
        with self.assertRaises(error_validacion):
            s.mostrar_sesiones_de("mat-0001")
        with self.assertRaises(error_validacion):
            s.solicitudes_de("m-0001")

    def test_el_monitor_agrega_y_quita_horarios(self):
        s = armar()
        s.solicitar("e-0001", "mat-0001", "par", 2.0)
        s.generar_agenda()
        self.assertIn(" 1. lunes 08:00-12:00", s.mostrar_disponibilidad("m-0001"))
        with self.assertRaises(error_validacion):
            s.quitar_disponibilidad("m-0001", 1)
        s.agregar_disponibilidad_monitor("m-0001", [("martes", "08:00", "10:00")])
        s.quitar_disponibilidad("m-0001", 2)
        self.assertEqual(len(s.exigir_monitor("m-0001").disponibilidad), 1)
        for numero in [0, 5, "1", True]:
            with self.assertRaises(error_validacion):
                s.quitar_disponibilidad("m-0001", numero)
        with self.assertRaises(error_validacion):
            s.quitar_disponibilidad("mat-0001", 1)
        with self.assertRaises(error_validacion):
            s.quitar_disponibilidad("e-0001", 1)
        s.agregar_disponibilidad_estudiante("e-0002", [("martes", "08:00", "09:00")])
        s.quitar_disponibilidad("e-0002", 2)
        self.assertEqual(s.mostrar_disponibilidad("e-0002").count("lunes"), 1)
        s.exigir_estudiante("e-0002").disponibilidad = []
        self.assertEqual(s.mostrar_disponibilidad("e-0002"), "(sin horarios libres registrados)")

    def test_el_estudiante_no_puede_quitar_el_horario_de_una_sesion(self):
        s = armar()
        s.solicitar("e-0001", "mat-0001", "par", 2.0)
        s.generar_agenda()
        with self.assertRaises(error_validacion):
            s.quitar_disponibilidad("e-0001", 1)

    def test_especialidades_del_monitor(self):
        s = armar()
        s.solicitar("e-0001", "mat-0002", "par", 2.0)
        s.generar_agenda()
        self.assertEqual(s.solicitudes[0].estado, "en_espera")
        asignadas = s.agregar_especialidad("m-0001", "mat-0002")
        self.assertEqual(len(asignadas), 1)
        self.assertEqual(s.solicitudes[0].estado, "asignada")
        self.assertIn("fisica i", s.mostrar_especialidades("m-0001"))
        with self.assertRaises(error_validacion):
            s.agregar_especialidad("m-0001", "mat-0002")
        with self.assertRaises(error_validacion):
            s.agregar_especialidad("m-0001", "mat-0099")
        with self.assertRaises(error_validacion):
            s.quitar_especialidad("m-0001", "mat-0002")
        s.cancelar_solicitud(1, "e-0001")
        s.quitar_especialidad("m-0001", "mat-0002")
        with self.assertRaises(error_validacion):
            s.quitar_especialidad("m-0001", "mat-0002")
        with self.assertRaises(error_validacion):
            s.quitar_especialidad("m-0001", "mat-0001")
        self.assertEqual(s.mostrar_especialidades("m-0001").count("mat-"), 1)


class prueba_persistencia_de_cuentas(unittest.TestCase):

    def test_las_cuentas_el_promedio_y_las_canceladas_sobreviven(self):
        s = armar()
        s.solicitar("e-0001", "mat-0001", "par", 2.0, 3.5)
        s.solicitar("e-0002", "mat-0001", "par", 3.0, 4.0)
        s.cancelar_solicitud(2, "e-0002")
        for _ in range(3):
            with self.assertRaises(error_validacion):
                s.iniciar_sesion("luis", "mala")
        copia = persistencia.desde_diccionario(persistencia.a_diccionario(s), reloj_falso())
        self.assertEqual(copia.cuentas.obtener("luis").bloqueada, True)
        self.assertEqual(copia.iniciar_sesion("ana", "ana12345").codigo_persona, "e-0001")
        self.assertEqual(copia.iniciar_sesion("admin", "admin12345").rol, "administrador")
        self.assertEqual([x.promedio for x in copia.solicitudes], [3.5, 4.0])
        self.assertEqual(copia.solicitudes[1].estado, "cancelada")
        copia.solicitar("e-0002", "mat-0001", "par", 3.0)
        self.assertEqual(persistencia.a_diccionario(copia)["cuentas"], persistencia.a_diccionario(s)["cuentas"])

    def test_un_archivo_viejo_sin_cuentas_se_carga(self):
        datos = persistencia.a_diccionario(armar())
        del datos["cuentas"]
        for x in datos["solicitudes"]:
            x.pop("promedio", None)
        self.assertEqual(len(persistencia.desde_diccionario(datos).cuentas), 0)

    def test_una_cuenta_ligada_a_alguien_que_no_existe_se_rechaza(self):
        datos = persistencia.a_diccionario(armar())
        datos["cuentas"][0]["codigo_persona"] = "e-0099"
        datos["cuentas"][2]["codigo_persona"] = "m-0099"
        with self.assertRaises(error_validacion):
            persistencia.desde_diccionario(datos)
        datos = persistencia.a_diccionario(armar())
        for cuenta in datos["cuentas"]:
            if cuenta["rol"] == "monitor":
                cuenta["codigo_persona"] = "m-0099"
        with self.assertRaises(error_validacion):
            persistencia.desde_diccionario(datos)


def opcion(menu, nombre):
    return str(nombres(menu).index(nombre) + 1)


def ejecutar(s, *teclas):
    salidas = []
    app = consola(s, entrada=guion(*teclas), salida=salidas.append)
    app.ejecutar()
    return app, "\n".join(salidas)


class prueba_roles_en_la_consola(unittest.TestCase):

    def test_cada_rol_solo_ve_sus_opciones(self):
        solo_admin = {"generar_agenda", "agendar_manual", "modificar_sesion", "cancelar_sesion", "crear_estudiante",
                      "crear_monitor", "crear_administrador", "ver_usuarios", "desbloquear", "restablecer_clave",
                      "registrar_materia", "agregar_prerrequisito", "registrar_cursada", "revertir", "guardar",
                      "cargar", "demo", "horarios_monitores", "cancelar_solicitud_admin", "informe", "ver_cola"}
        self.assertEqual(solo_admin & set(nombres(menu_estudiante)), set())
        self.assertEqual(solo_admin & set(nombres(menu_monitor)), set())
        self.assertTrue(solo_admin <= set(nombres(menu_administrador)))
        for menu in menus.values():
            for metodo in nombres(menu):
                self.assertTrue(callable(getattr(consola, metodo)), metodo)

    def test_el_estudiante_no_ve_las_opciones_del_administrador_en_pantalla(self):
        app, texto = ejecutar(armar(), "1", "ana", "ana12345", "0", "0")
        self.assertIn("estudiante: ana", texto)
        self.assertIn("pedir una monitoria", texto)
        self.assertNotIn("generar la agenda", texto)
        self.assertNotIn("crear cuenta", texto)
        app, texto = ejecutar(armar(), "1", "carlos", "carlos12", "0", "0")
        self.assertIn("agregar horarios libres", texto)
        self.assertNotIn("pedir una monitoria", texto)

    def test_numeros_fuera_del_menu_del_rol_no_funcionan(self):
        s = armar()
        total = len(nombres(menu_estudiante))
        app, texto = ejecutar(s, "1", "ana", "ana12345", str(total + 1), "0", "0")
        self.assertIn("opcion no valida", texto)

    def test_tres_claves_malas_bloquean_desde_la_consola(self):
        s = armar()
        app, texto = ejecutar(s, "1", "ana", "x", "1", "ana", "x", "1", "ana", "x", "1", "ana", "ana12345", "0")
        self.assertIn("le quedan 2 intentos", texto)
        self.assertIn("la cuenta quedo bloqueada", texto)
        self.assertIn("pida al administrador que la desbloquee", texto)
        self.assertNotIn("estudiante: ana", texto)

    def test_el_estudiante_pide_una_monitoria_y_ve_la_urgencia(self):
        s = armar()
        app, texto = ejecutar(s, "1", "ana", "ana12345", opcion(menu_estudiante, "solicitar_propia"),
                              "1", "par", "2,5", "4", opcion(menu_estudiante, "mis_solicitudes"),
                              opcion(menu_estudiante, "mi_agenda"), "0", "0")
        self.assertIn("solicitud #1 creada", texto)
        self.assertIn("ponderados 0.7/0.3", texto)
        self.assertIn("calculo i", texto)
        self.assertEqual((s.solicitudes[0].estudiante.nombre, s.solicitudes[0].promedio), ("ana", 4.0))

    def test_el_estudiante_no_puede_pedir_por_otro_ni_cancelar_lo_ajeno(self):
        s = armar()
        s.solicitar("e-0002", "mat-0001", "par", 2.0)
        app, texto = ejecutar(s, "1", "ana", "ana12345", opcion(menu_estudiante, "cancelar_propia"),
                              opcion(menu_estudiante, "mis_solicitudes"), "0", "0")
        self.assertIn("error: no tiene solicitudes para cancelar", texto)
        self.assertIn("(no ha pedido monitorias)", texto)
        self.assertEqual(s.solicitudes[0].estado, "pendiente")

    def test_el_estudiante_cancela_agrega_y_quita_horarios_y_consulta(self):
        s = armar()
        s.solicitar("e-0001", "mat-0001", "par", 2.0)
        app, texto = ejecutar(
            s, "1", "ana", "ana12345",
            opcion(menu_estudiante, "agregar_mi_horario"), "martes 08:00 09:00", "",
            opcion(menu_estudiante, "agregar_mi_horario"), "",
            opcion(menu_estudiante, "ver_mi_horario"),
            opcion(menu_estudiante, "quitar_mi_horario"), "2",
            opcion(menu_estudiante, "materias_y_monitores"),
            opcion(menu_estudiante, "plan_propio"), "1",
            opcion(menu_estudiante, "cancelar_propia"), "1",
            opcion(menu_estudiante, "cambiar_clave"), "ana12345", "nueva123", "nueva123", "0", "0")
        self.assertIn("se guardo 1 horario", texto)
        self.assertIn("no se agrego ningun horario", texto)
        self.assertIn("horario quitado", texto)
        self.assertIn("monitores: carlos", texto)
        self.assertIn("monitores: ninguno", texto)
        self.assertIn("no le falta ningun prerrequisito", texto)
        self.assertIn("solicitud cancelada", texto)
        self.assertIn("contrasena cambiada", texto)
        self.assertEqual(s.solicitudes[0].estado, "cancelada")
        self.assertEqual(len(s.exigir_estudiante("e-0001").disponibilidad), 1)
        s.iniciar_sesion("ana", "nueva123")

    def test_aviso_si_el_estudiante_no_tiene_horarios(self):
        s = armar()
        s.registrar_cuenta_estudiante("sin", "sin12345", "sin horarios", 2, "ing")
        app, texto = ejecutar(s, "1", "sin", "sin12345", opcion(menu_estudiante, "solicitar_propia"),
                              "1", "puntual", "3", "3", "0", "0")
        self.assertIn("todavia no tiene horarios", texto)

    def test_el_monitor_agrega_horarios_y_especialidades_desde_su_panel(self):
        s = armar()
        s.solicitar("e-0001", "mat-0002", "par", 2.0)
        s.generar_agenda()
        app, texto = ejecutar(
            s, "1", "carlos", "carlos12",
            opcion(menu_monitor, "agregar_mi_horario"), "martes 08:00 10:00", "",
            opcion(menu_monitor, "ver_mi_horario"),
            opcion(menu_monitor, "agregar_mi_especialidad"), "2",
            opcion(menu_monitor, "ver_mis_especialidades"),
            opcion(menu_monitor, "mi_agenda"),
            opcion(menu_monitor, "quitar_mi_especialidad"), "mat-0002",
            opcion(menu_monitor, "quitar_mi_horario"), "2", "0", "0")
        self.assertIn("materia agregada a sus especialidades", texto)
        self.assertIn("se agendaron 1 solicitudes", texto)
        self.assertIn("error: no se puede quitar: tiene sesiones agendadas de esa materia", texto)
        self.assertIn("horario quitado", texto)
        self.assertEqual(s.solicitudes[0].estado, "asignada")
        self.assertEqual(sorted(s.exigir_monitor("m-0001").materias), ["mat-0001", "mat-0002"])

    def test_el_monitor_con_horario_nuevo_resuelve_una_espera(self):
        s = armar()
        s.registrar_cuenta_monitor("hugo", "hugo1234", "hugo", 5, ["mat-0001"], [])
        s.agregar_disponibilidad_monitor("m-0001", [])
        s.exigir_monitor("m-0001").disponibilidad = []
        s.solicitar("e-0001", "mat-0001", "par", 2.0)
        s.generar_agenda()
        self.assertEqual(s.solicitudes[0].estado, "en_espera")
        app, texto = ejecutar(s, "1", "hugo", "hugo1234", opcion(menu_monitor, "agregar_mi_horario"),
                              "lunes 08:00 10:00", "", "0", "0")
        self.assertIn("se agendaron 1 solicitudes que estaban en espera", texto)
        self.assertEqual(s.solicitudes[0].estado, "asignada")

    def test_el_administrador_agenda_modifica_y_cancela_desde_su_panel(self):
        s = armar()
        s.solicitar("e-0001", "mat-0001", "par", 2.0)
        app, texto = ejecutar(
            s, "1", "admin", "admin12345",
            opcion(menu_administrador, "agendar_manual"), "1", "m-0001", "lunes", "08:00",
            opcion(menu_administrador, "modificar_sesion"), "1", "lunes", "09:00", "",
            opcion(menu_administrador, "ver_agenda"),
            opcion(menu_administrador, "horarios_monitores"),
            opcion(menu_administrador, "horarios_estudiantes"),
            opcion(menu_administrador, "cancelar_sesion"), "1",
            opcion(menu_administrador, "modificar_sesion"),
            opcion(menu_administrador, "cancelar_sesion"), "0", "0")
        self.assertIn("agendada: lunes", texto)
        self.assertIn("modificada: lunes      09:00-10:00", texto)
        self.assertIn("cancelada: lunes", texto)
        self.assertIn("(agenda vacia)", texto)
        self.assertEqual(s.solicitudes[0].estado, "en_espera")

    def test_el_administrador_gestiona_usuarios_y_horarios_ajenos(self):
        s = armar()
        s.solicitar("e-0001", "mat-0001", "par", 2.0)
        for _ in range(3):
            with self.assertRaises(error_validacion):
                s.iniciar_sesion("luis", "mala")
        app, texto = ejecutar(
            s, "1", "admin", "admin12345",
            opcion(menu_administrador, "ver_usuarios"),
            opcion(menu_administrador, "desbloquear"), "luis",
            opcion(menu_administrador, "restablecer_clave"), "luis", "nueva123", "nueva123",
            opcion(menu_administrador, "restablecer_clave"), "nadie",
            opcion(menu_administrador, "crear_administrador"), "jefa", "jefa", "jefa1234", "jefa1234",
            opcion(menu_administrador, "agregar_horario_de"), "m-0001", "martes 08:00 10:00", "",
            opcion(menu_administrador, "agregar_horario_de"), "e-0002", "martes 08:00 10:00", "",
            opcion(menu_administrador, "agregar_horario_de"), "e-0002", "",
            opcion(menu_administrador, "quitar_horario_de"), "e-0002", "2",
            opcion(menu_administrador, "quitar_horario_de"), "mat-0001",
            opcion(menu_administrador, "cancelar_solicitud_admin"), "1", "0", "0")
        self.assertIn("BLOQUEADA", texto)
        self.assertIn("cuenta desbloqueada", texto)
        self.assertIn("contrasena restablecida", texto)
        self.assertIn("error: no existe el usuario 'nadie'", texto)
        self.assertIn("administrador creado con el usuario jefa", texto)
        self.assertIn("horario quitado", texto)
        self.assertIn("no es un estudiante ni un monitor", texto)
        self.assertEqual(s.iniciar_sesion("luis", "nueva123").usuario, "luis")
        self.assertEqual(s.solicitudes[0].estado, "cancelada")
        self.assertEqual(s.cuentas.contar_administradores(), 2)

    def test_el_administrador_crea_monitores_y_estudiantes(self):
        s = armar()
        app, texto = ejecutar(
            s, "1", "admin", "admin12345",
            opcion(menu_administrador, "crear_monitor"), "hugo", "5", "mat-0002", "", "lunes 08:00 10:00", "", "hugo",
            "hugo1234", "hugo1234",
            opcion(menu_administrador, "crear_estudiante"), "eva", "3", "ing", "", "eva", "eva12345", "eva12345", "0", "0")
        self.assertIn("monitor registrado con codigo m-0002 y usuario hugo", texto)
        self.assertIn("estudiante registrado con codigo e-0003 y usuario eva", texto)
        self.assertEqual(s.iniciar_sesion("hugo", "hugo1234").rol, "monitor")
        self.assertEqual(s.iniciar_sesion("eva", "eva12345").rol, "estudiante")

    def test_registrarse_como_estudiante_desde_la_entrada(self):
        s = armar()
        app, texto = ejecutar(s, "2", "pedro", "3", "ing", "armando", "pedro123", "pedro123", "0", "0")
        self.assertIn("registro exitoso", texto)
        self.assertIn("estudiante: pedro", texto)
        self.assertEqual(s.cuentas.obtener("armando").rol, "estudiante")
        self.assertEqual(s.cuentas.obtener("armando").codigo_persona, "e-0003")

    def test_no_hay_forma_de_registrarse_como_monitor_o_administrador(self):
        app, texto = ejecutar(armar(), "3", "0")
        self.assertIn("opcion no valida", texto)
        self.assertNotIn("monitor", texto.replace("monitorias", ""))

    def test_contrasena_de_menos_de_8_caracteres_se_rechaza_y_la_nueva_cuenta_puede_entrar(self):
        s = armar()
        app, texto = ejecutar(s, "2", "pedro", "3", "ing", "armando", "1234567", "12345678", "12345678", "0",
                              "1", "armando", "12345678", "0", "0")
        self.assertIn("la contrasena debe tener al menos 8 caracteres", texto)
        self.assertEqual(texto.count("estudiante: pedro"), 2)
        with self.assertRaises(error_validacion):
            s.iniciar_sesion("armando", "1234567")
        self.assertEqual(s.iniciar_sesion("armando", "12345678").rol, "estudiante")

    def test_el_administrador_no_puede_crear_cuentas_con_contrasena_corta(self):
        s = armar()
        app, texto = ejecutar(s, "1", "admin", "admin12345", opcion(menu_administrador, "crear_administrador"),
                              "jefa", "jefa", "corta12", "jefa1234", "jefa1234", "0", "0")
        self.assertIn("al menos 8 caracteres", texto)
        self.assertEqual(s.iniciar_sesion("jefa", "jefa1234").rol, "administrador")

    def test_agregar_horarios_se_puede_salir_con_0_salir_o_enter_y_guarda_cada_uno(self):
        for salida in ["0", "salir", "", "SALIR"]:
            s = armar()
            app, texto = ejecutar(s, "1", "ana", "ana12345", opcion(menu_estudiante, "agregar_mi_horario"),
                                  "lunes 14:00 15:00", "martes 14:00 16:00", salida, "0", "0")
            self.assertIn("se guardaron 2 horarios", texto)
            self.assertIn("lunes 14:00-15:00", s.mostrar_disponibilidad("e-0001"))
            self.assertIn("martes 14:00-16:00", s.mostrar_disponibilidad("e-0001"))

    def test_horarios_repetidos_o_que_se_cruzan_se_unen_en_uno_solo(self):
        s = armar()
        s.agregar_disponibilidad_estudiante("e-0001", [("lunes", "14:00", "16:00")])
        s.agregar_disponibilidad_estudiante("e-0001", [("lunes", "14:00", "16:00")])
        s.agregar_disponibilidad_estudiante("e-0001", [("lunes", "15:00", "18:00")])
        texto = s.mostrar_disponibilidad("e-0001")
        self.assertEqual(texto.count("lunes 14:00-18:00"), 1)
        self.assertNotIn("15:00-18:00", texto)

    def test_los_horarios_quedan_guardados_aunque_se_corte_la_entrada(self):
        s = armar()
        # la entrada se acaba (EOFError) sin escribir 0: lo ya escrito no se pierde
        ejecutar(s, "1", "ana", "ana12345", opcion(menu_estudiante, "agregar_mi_horario"), "viernes 09:00 11:00")
        self.assertIn("viernes 09:00-11:00", s.mostrar_disponibilidad("e-0001"))

    def test_un_horario_invalido_no_saca_de_la_opcion_ni_pierde_los_anteriores(self):
        s = armar()
        app, texto = ejecutar(s, "1", "ana", "ana12345", opcion(menu_estudiante, "agregar_mi_horario"),
                              "sabado 10:00 11:00", "lunes 25:00 26:00", "hola", "sabado 09:00 10:30", "0", "0")
        self.assertIn("se guardaron 2 horarios", texto)
        self.assertIn("use el formato", texto)
        self.assertIn("sabado 09:00-11:00", s.mostrar_disponibilidad("e-0001"))

    def test_el_monitor_tambien_puede_salir_y_conserva_lo_agregado(self):
        s = armar()
        s.registrar_cuenta_monitor("hugo", "hugo1234", "hugo", 5, ["mat-0001"], [])
        app, texto = ejecutar(s, "1", "hugo", "hugo1234", opcion(menu_monitor, "agregar_mi_horario"),
                              "jueves 08:00 12:00", "0", "0", "0")
        self.assertIn("se guardo 1 horario", texto)
        self.assertIn("jueves 08:00-12:00", s.mostrar_disponibilidad("m-0002"))

    def test_el_primer_arranque_pide_crear_el_administrador(self):
        s = sistema_monitorias()
        app, texto = ejecutar(s, "jefe", "jefe", "clave123", "clave123", "1", "jefe", "clave123", "0", "0")
        self.assertIn("cree la cuenta del primer administrador", texto)
        self.assertIn("administrador: jefe", texto)

    def test_el_guardado_automatico_conserva_las_cuentas(self):
        import os
        import tempfile
        s = armar()
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = os.path.join(carpeta, "auto.json")
            salidas = []
            app = consola(s, entrada=guion("1", "ana", "ana12345", "0", "0"), salida=salidas.append,
                          archivo=ruta, autoguardar=True)
            app.ejecutar()
            self.assertTrue(os.path.exists(ruta))
            self.assertEqual(persistencia.cargar(ruta).iniciar_sesion("ana", "ana12345").usuario, "ana")
            app = consola(s, entrada=guion("0"), salida=salidas.append, archivo="/no/existe/auto.json",
                          autoguardar=True)
            app.ejecutar()
            self.assertIn("no se pudo guardar", "\n".join(salidas))


if __name__ == "__main__":
    unittest.main()
