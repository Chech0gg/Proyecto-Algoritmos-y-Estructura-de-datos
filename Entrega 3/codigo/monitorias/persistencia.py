import json
import os

from .agenda import clase_registro_asignacion, clase_sesion
from .errores import error_validacion
from .modelos import clase_estudiante, clase_monitor, clase_profesor, clase_solicitud
from .prioridad import resultado_prioridad
from .sistema import sistema_monitorias
from .tiempo import minutos_a_hora

version = 1


def campo(diccionario, nombre):
    if not isinstance(diccionario, dict) or nombre not in diccionario:
        raise error_validacion("falta el campo '" + nombre + "' en el archivo")
    return diccionario[nombre]


def bloques_a_lista(bloques):
    return [[b.dia, minutos_a_hora(b.inicio), minutos_a_hora(b.fin)] for b in bloques]


def a_diccionario(s):
    materias = []
    for m in s.indice_materias.valores():
        materias.append({"codigo": m.codigo, "nombre": m.nombre, "area": m.area, "nivel": m.nivel,
                         "dificultad": m.dificultad, "tasa_reprobacion": m.tasa_reprobacion})
    prerrequisitos = []
    for m in s.indice_materias.valores():
        for requisito in s.prerrequisitos.directos(m.codigo):
            prerrequisitos.append([m.codigo, requisito])
    personas = []
    for p in s.indice_personas.valores():
        if isinstance(p, clase_estudiante):
            personas.append({"tipo": "estudiante", "codigo": p.codigo, "nombre": p.nombre, "semestre": p.semestre,
                             "carrera": p.carrera, "disponibilidad": bloques_a_lista(p.disponibilidad)})
        elif isinstance(p, clase_monitor):
            personas.append({"tipo": "monitor", "codigo": p.codigo, "nombre": p.nombre, "semestre": p.semestre,
                             "materias": list(p.materias), "disponibilidad": bloques_a_lista(p.disponibilidad)})
        else:
            personas.append({"tipo": "profesor", "codigo": p.codigo, "nombre": p.nombre, "materias": list(p.materias)})
    cursadas = sorted([clave, materia] for clave, conjunto_materias in s.cursadas.por_estudiante.items()
                      for materia in conjunto_materias.elementos())
    solicitudes = []
    for x in s.solicitudes:
        solicitudes.append({"id": x.id, "estudiante": x.estudiante.codigo, "materia": x.materia.codigo,
                            "tipo": x.tipo, "nota": x.nota, "llegada": x.llegada, "riesgo": x.riesgo,
                            "impacto": x.impacto, "urgencia": x.urgencia, "prioridad": x.prioridad,
                            "desglose": x.desglose, "estado": x.estado, "motivo": x.motivo,
                            "revertida": x.revertida})
    posicion = {id(sesion): i for i, sesion in enumerate(s.agenda.sesiones)}
    sesiones = []
    for x in s.agenda.sesiones:
        sesiones.append({"monitor": x.monitor.codigo, "materia": x.materia.codigo, "tipo": x.tipo, "dia": x.dia,
                         "inicio": x.inicio, "fin": x.fin, "estudiantes": [e.codigo for e in x.estudiantes]})
    historial = []
    for registro in reversed(s.historial.como_lista()):
        historial.append({"solicitud": registro.solicitud.id, "sesion": posicion[id(registro.sesion)],
                          "creo_sesion": registro.creo_sesion})
    return {"version": version, "dias_envejecimiento": s.dias_envejecimiento,
            "exigir_prerrequisitos": s.exigir_prerrequisitos, "contadores": dict(s.codigos.contadores),
            "materias": materias, "prerrequisitos": prerrequisitos, "personas": personas,
            "cursadas": cursadas, "solicitudes": solicitudes, "sesiones": sesiones,
            "historial": historial, "orden_atencion": list(s.orden_atencion),
            "notificaciones": s.notificaciones.como_lista()}


def objeto(s, codigo, tipo_esperado, nombre):
    encontrado = s.personas.obtener(codigo)
    if not isinstance(encontrado, tipo_esperado):
        raise error_validacion("el archivo hace referencia a " + nombre + " '" + str(codigo) + "' que no existe")
    return encontrado


def desde_diccionario(datos, reloj=None):
    if campo(datos, "version") != version:
        raise error_validacion("version de archivo no soportada: " + str(datos["version"]))
    s = sistema_monitorias(reloj=reloj, dias_envejecimiento=campo(datos, "dias_envejecimiento"),
                           exigir_prerrequisitos=campo(datos, "exigir_prerrequisitos"))
    for m in campo(datos, "materias"):
        s.agregar_materia(campo(m, "codigo"), campo(m, "nombre"), campo(m, "area"), campo(m, "nivel"),
                          campo(m, "dificultad"), campo(m, "tasa_reprobacion"))
    for materia, requisito in campo(datos, "prerrequisitos"):
        s.agregar_prerrequisito(materia, requisito)
    for p in campo(datos, "personas"):
        tipo = campo(p, "tipo")
        if tipo == "estudiante":
            s.agregar_estudiante(campo(p, "codigo"), campo(p, "nombre"), campo(p, "semestre"),
                                 campo(p, "carrera"), campo(p, "disponibilidad"))
        elif tipo == "monitor":
            s.agregar_monitor(campo(p, "codigo"), campo(p, "nombre"), campo(p, "semestre"),
                              campo(p, "materias"), campo(p, "disponibilidad"))
        elif tipo == "profesor":
            s.revisar_materias(campo(p, "materias"))
            s.guardar_persona(clase_profesor(campo(p, "codigo"), campo(p, "nombre"), list(campo(p, "materias"))))
        else:
            raise error_validacion("tipo de persona desconocido: '" + str(tipo) + "'")
    for estudiante, materia in campo(datos, "cursadas"):
        s.registrar_cursada(estudiante, materia)
    for x in campo(datos, "solicitudes"):
        resultado = resultado_prioridad(campo(x, "riesgo"), campo(x, "impacto"), campo(x, "urgencia"),
                                        campo(x, "prioridad"), campo(x, "desglose"))
        solicitud = clase_solicitud(campo(x, "id"), objeto(s, campo(x, "estudiante"), clase_estudiante, "el estudiante"),
                                    s.materias.obtener(campo(x, "materia")), campo(x, "tipo"), campo(x, "nota"),
                                    campo(x, "llegada"), resultado)
        if solicitud.materia is None:
            raise error_validacion("el archivo hace referencia a una materia que no existe")
        solicitud.estado = campo(x, "estado")
        solicitud.motivo = campo(x, "motivo")
        solicitud.revertida = campo(x, "revertida")
        s.registrar_solicitud(solicitud)
        if solicitud.estado == "pendiente":
            s.cola.encolar(solicitud)
        elif solicitud.estado == "en_espera":
            s.lista_espera.encolar(solicitud)
    for x in campo(datos, "sesiones"):
        estudiantes = [objeto(s, c, clase_estudiante, "el estudiante") for c in campo(x, "estudiantes")]
        s.agenda.sesiones.append(clase_sesion(objeto(s, campo(x, "monitor"), clase_monitor, "el monitor"),
                                              s.materias.obtener(campo(x, "materia")), campo(x, "tipo"),
                                              campo(x, "dia"), campo(x, "inicio"), campo(x, "fin"), estudiantes))
    for registro in campo(datos, "historial"):
        solicitud, comparaciones = s.buscar_solicitud(campo(registro, "solicitud"))
        indice = campo(registro, "sesion")
        if solicitud is None or not isinstance(indice, int) or indice < 0 or indice >= len(s.agenda.sesiones):
            raise error_validacion("el historial del archivo es inconsistente")
        s.historial.apilar(clase_registro_asignacion(solicitud, s.agenda.sesiones[indice], campo(registro, "creo_sesion")))
    s.codigos.contadores = dict(campo(datos, "contadores"))
    s.orden_atencion = list(campo(datos, "orden_atencion"))
    for mensaje in campo(datos, "notificaciones"):
        s.notificaciones.encolar(mensaje)
    return s


def guardar(s, ruta):
    temporal = ruta + ".tmp"
    with open(temporal, "w", encoding="utf-8") as archivo:
        json.dump(a_diccionario(s), archivo, ensure_ascii=False, indent=2)
    os.replace(temporal, ruta)


def cargar(ruta, reloj=None):
    try:
        with open(ruta, encoding="utf-8") as archivo:
            datos = json.load(archivo)
    except OSError:
        raise error_validacion("no se pudo abrir el archivo '" + ruta + "'")
    except ValueError:
        raise error_validacion("el archivo '" + ruta + "' no es un json valido")
    try:
        return desde_diccionario(datos, reloj)
    except error_validacion:
        raise
    except Exception as problema:
        raise error_validacion("el archivo '" + ruta + "' esta danado: " + str(problema))
