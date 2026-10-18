# pruebas del sistema de monitorias.
# cada funcion "prueba_..." revisa un caso. se ejecutan con:
#     python test_monitorias.py
# (tambien funcionan con pytest). si una revision falla, se muestra un error.
from ProyectoJuanRuiz.codigocompl import error_validacion, sistema_monitorias, tipo_monitoria

def base():
    """escenario base compartido por todas las pruebas."""
    s = sistema_monitorias()
    m = {
        "calc": s.registrar_materia("calculo i", "matematicas", 1, 4),
        "prog": s.registrar_materia("programacion i", "sistemas", 1, 3),
        "estd": s.registrar_materia("estructuras de datos", "sistemas", 3, 5),
        "fis": s.registrar_materia("fisica i", "ciencias", 1, 3),   # sin monitor
    }
    s.registrar_monitor("carlos", 6, [m["calc"].codigo, m["prog"].codigo],
                        [("lunes", "08:00", "12:00"), ("martes", "14:00", "18:00")])
    s.registrar_monitor("diana", 7, [m["estd"].codigo], [("miercoles", "10:00", "14:00")])
    return s, m


def sin_cruces(agenda):
    """dice si ningun monitor tiene dos sesiones al mismo tiempo."""
    sesiones = agenda.sesiones
    for i in range(len(sesiones)):
        for j in range(i + 1, len(sesiones)):
            a = sesiones[i]
            b = sesiones[j]
            if a.monitor.codigo == b.monitor.codigo and a.se_cruza(b.dia, b.inicio, b.fin):
                return False
    return True


def debe_fallar(funcion, *argumentos):
    """llama a la funcion y dice si fallo con un error de validacion."""
    try:
        funcion(*argumentos)
    except error_validacion:
        return True
    return False


def buscar_monitor(s, nombre):
    """devuelve el monitor con ese nombre."""
    for persona in s.personas.valores():
        if getattr(persona, "nombre", "") == nombre:
            return persona


# ---------------------------------------------------------------------
# caso 1: todo sale bien
# ---------------------------------------------------------------------
def prueba_todas_las_solicitudes_se_asignan():
    s, m = base()
    ana = s.registrar_estudiante("ana", 2, "sistemas", [("lunes", "08:00", "10:00")])
    luis = s.registrar_estudiante("luis", 2, "sistemas", [("lunes", "08:00", "12:00")])
    eva = s.registrar_estudiante("eva", 4, "sistemas", [("miercoles", "10:00", "14:00")])
    tomas = s.registrar_estudiante("tomas", 4, "sistemas", [("miercoles", "10:00", "14:00")])
    s.solicitar(ana.codigo, m["calc"].codigo, tipo_monitoria.par, 1)        # 16 alta
    s.solicitar(luis.codigo, m["prog"].codigo, tipo_monitoria.puntual, 4)   # 8 media
    s.solicitar(eva.codigo, m["estd"].codigo, tipo_monitoria.general, 2)    # 16 alta
    s.solicitar(tomas.codigo, m["estd"].codigo, tipo_monitoria.general, 3)  # 14 alta
    s.generar_agenda()
    r = s.informe_cobertura()
    assert r["porcentaje"] == 100.0
    assert s.orden_atencion == [1, 3, 4, 2]    # alta por llegada, luego media
    assert sin_cruces(s.agenda)
    grupo = None
    for sesion in s.agenda.sesiones:
        if sesion.tipo == tipo_monitoria.general:
            grupo = sesion
    assert len(grupo.estudiantes) == 2         # tomas se unio al grupo de eva
    assert s.buscar(ana.codigo) is ana


# ---------------------------------------------------------------------
# caso 2: todo sale mal (datos invalidos)
# ---------------------------------------------------------------------
def prueba_datos_invalidos_son_rechazados():
    s, m = base()
    e = s.registrar_estudiante("ana", 2, "sistemas", [("lunes", "08:00", "10:00")])
    assert debe_fallar(s.registrar_estudiante, "", 2, "sistemas")                        # nombre vacio
    assert debe_fallar(s.registrar_estudiante, "pepe", 15, "sistemas")                   # semestre invalido
    assert debe_fallar(s.registrar_estudiante, "pepe", 2, "sistemas", [("lunes", "10:00", "08:00")])
    assert debe_fallar(s.registrar_monitor, "ruth", 5, ["mat-999"], [])                  # materia inexistente
    assert debe_fallar(s.solicitar, "e-9999", m["calc"].codigo, tipo_monitoria.par, 2)   # estudiante inexistente
    assert debe_fallar(s.solicitar, e.codigo, m["calc"].codigo, tipo_monitoria.par, 9)   # desempeno fuera de rango
    assert debe_fallar(s.solicitar, e.codigo, m["estd"].codigo, tipo_monitoria.par, 2)   # materia de semestre superior
    assert s.buscar("x-0000") is None
    assert len(s.solicitudes) == 0                                                       # nada entro a la cola


# ---------------------------------------------------------------------
# caso 3: a medias (cobertura parcial)
# ---------------------------------------------------------------------
def prueba_cobertura_parcial():
    s, m = base()
    ana = s.registrar_estudiante("ana", 2, "sistemas", [("lunes", "08:00", "10:00")])
    luis = s.registrar_estudiante("luis", 2, "sistemas", [("lunes", "08:00", "12:00")])
    pedro = s.registrar_estudiante("pedro", 2, "sistemas", [("viernes", "08:00", "12:00")])
    sara = s.registrar_estudiante("sara", 2, "sistemas", [("lunes", "08:00", "12:00")])
    s.solicitar(ana.codigo, m["calc"].codigo, tipo_monitoria.par, 1)
    s.solicitar(luis.codigo, m["prog"].codigo, tipo_monitoria.puntual, 4)
    s.solicitar(pedro.codigo, m["calc"].codigo, tipo_monitoria.par, 2)    # horarios no coinciden
    s.solicitar(sara.codigo, m["fis"].codigo, tipo_monitoria.par, 2)      # sin monitor
    s.generar_agenda()
    r = s.informe_cobertura()
    assert (r["asignadas"], r["en_espera"]) == (2, 2)
    assert r["porcentaje"] == 50.0
    motivos = {}
    for detalle in r["detalle_en_espera"]:
        motivos[detalle[1]] = detalle[3]
    assert "horarios" in motivos["pedro"]
    assert "monitor" in motivos["sara"]
    assert sin_cruces(s.agenda)
    assert len(s.lista_espera) == 2       # pedro y sara quedan en espera


# ---------------------------------------------------------------------
# caso 4: la lista de espera
# ---------------------------------------------------------------------
def prueba_la_lista_de_espera_se_resuelve_sola():
    s, m = base()
    pedro = s.registrar_estudiante("pedro", 2, "sistemas", [("viernes", "08:00", "12:00")])
    sara = s.registrar_estudiante("sara", 2, "sistemas", [("lunes", "10:00", "12:00")])
    s.solicitar(pedro.codigo, m["calc"].codigo, tipo_monitoria.par, 2)
    s.solicitar(sara.codigo, m["fis"].codigo, tipo_monitoria.puntual, 2)
    s.generar_agenda()
    assert len(s.lista_espera) == 2
    # nada cambia si se reintenta sin novedades
    assert s.reintentar_lista_espera() == []
    assert len(s.lista_espera) == 2
    # se registra un monitor de fisica -> sara sale de la espera
    s.registrar_monitor("hugo", 5, [m["fis"].codigo], [("lunes", "10:00", "12:00")])
    assert len(s.lista_espera) == 1
    assert s.solicitudes[1].estado == "asignada"
    # el monitor de calculo publica un viernes -> pedro sale de la espera
    carlos = buscar_monitor(s, "carlos")
    asignadas = s.agregar_disponibilidad_monitor(carlos.codigo, [("viernes", "09:00", "11:00")])
    nombres = []
    for x in asignadas:
        nombres.append(x.estudiante.nombre)
    assert nombres == ["pedro"]
    assert len(s.lista_espera) == 0
    assert s.informe_cobertura()["porcentaje"] == 100.0
    assert sin_cruces(s.agenda)


def prueba_espera_respeta_prioridad_y_llegada():
    s, m = base()
    a = s.registrar_estudiante("ana", 2, "sistemas", [("jueves", "08:00", "09:00")])
    b = s.registrar_estudiante("beto", 2, "sistemas", [("jueves", "08:00", "09:00")])
    s.solicitar(a.codigo, m["calc"].codigo, tipo_monitoria.par, 3)    # 14 alta, llega primero
    s.solicitar(b.codigo, m["calc"].codigo, tipo_monitoria.par, 1)    # 16 alta, llega segundo
    s.generar_agenda()
    carlos = buscar_monitor(s, "carlos")
    # solo cabe una hora el jueves: gana quien llego primero (mismo nivel)
    s.agregar_disponibilidad_monitor(carlos.codigo, [("jueves", "08:00", "09:00")])
    assert s.solicitudes[0].estado == "asignada"
    assert s.solicitudes[1].estado == "en_espera"


# ---------------------------------------------------------------------
# ejecutor: corre todas las pruebas y cuenta cuantas pasan
# ---------------------------------------------------------------------
if __name__ == "__main__":
    pruebas = [prueba_todas_las_solicitudes_se_asignan, prueba_datos_invalidos_son_rechazados,
               prueba_cobertura_parcial, prueba_la_lista_de_espera_se_resuelve_sola,
               prueba_espera_respeta_prioridad_y_llegada]
    fallidas = 0
    for prueba in pruebas:
        try:
            prueba()
            print("ok     ", prueba.__name__)
        except AssertionError:
            fallidas += 1
            print("falla  ", prueba.__name__)
    print()
    print("todas las pruebas pasaron" if fallidas == 0 else str(fallidas) + " prueba(s) fallaron")