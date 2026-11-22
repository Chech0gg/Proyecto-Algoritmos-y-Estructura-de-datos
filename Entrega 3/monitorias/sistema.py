import time

from . import prioridad
from .agenda import agenda, clase_registro_asignacion, clase_sesion, revertir_registro
from .arboles import arbol_materias
from .avl import indice_avl
from .cola_solicitudes import cola_solicitudes
from .conjuntos import conjunto, registro_cursadas
from .cuentas import registro_cuentas
from .errores import error_validacion
from .gestion import gestion_usuarios
from .listas import cola, pila
from .modelos import (clase_estudiante, clase_materia, clase_monitor, clase_profesor,
                      clase_solicitud, clave_codigo, generador_codigos)
from .ordenamientos import busqueda_binaria, clave_texto, ordenar, ordenar_insercion, ordenar_mezcla
from .prerrequisitos import mapa_prerrequisitos
from .tabla_hash import tabla_hash
from .tiempo import cubierto, crear_bloque, cupo, duracion_min, fusionar_bloques, minutos_a_hora, paso_min


def reloj_real():
    return time.time() / 86400.0


class sistema_monitorias(gestion_usuarios):

    def __init__(self, reloj=None, dias_envejecimiento=prioridad.dias_envejecimiento,
                 exigir_prerrequisitos=True):
        self.reloj = reloj if reloj is not None else reloj_real
        self.dias_envejecimiento = dias_envejecimiento
        self.exigir_prerrequisitos = exigir_prerrequisitos
        self.personas = tabla_hash()
        self.materias = tabla_hash()
        self.indice_personas = indice_avl()
        self.indice_materias = indice_avl()
        self.indice_urgencia = indice_avl()
        self.catalogo = arbol_materias()
        self.codigos = generador_codigos()
        self.cola = cola_solicitudes(dias_envejecimiento)
        self.lista_espera = cola_solicitudes(dias_envejecimiento)
        self.agenda = agenda()
        self.prerrequisitos = mapa_prerrequisitos()
        self.historial = pila()
        self.cursadas = registro_cursadas()
        self.solicitudes = []
        self.activas = tabla_hash()
        self.orden_atencion = []
        self.notificaciones = cola()
        self.cuentas = registro_cuentas()

    def crear_bloques(self, disponibilidad):
        return [crear_bloque(dia, inicio, fin) for dia, inicio, fin in disponibilidad]

    def revisar_materias(self, codigos_materias):
        for codigo in codigos_materias:
            if not isinstance(codigo, str) or not self.materias.contiene(codigo):
                raise error_validacion("la materia '" + str(codigo) + "' no existe")

    def exigir_estudiante(self, codigo):
        if not isinstance(codigo, str) or not isinstance(self.personas.obtener(codigo), clase_estudiante):
            raise error_validacion("'" + str(codigo) + "' no es un estudiante registrado")
        return self.personas.obtener(codigo)

    def exigir_monitor(self, codigo):
        if not isinstance(codigo, str) or not isinstance(self.personas.obtener(codigo), clase_monitor):
            raise error_validacion("'" + str(codigo) + "' no es un monitor registrado")
        return self.personas.obtener(codigo)

    def agregar_materia(self, codigo, nombre, area, nivel, dificultad, tasa_reprobacion=None):
        materia = clase_materia(codigo, nombre, area, nivel, dificultad, tasa_reprobacion)
        self.materias.poner(codigo, materia)
        self.indice_materias.insertar(clave_codigo(codigo), materia)
        self.catalogo.agregar_materia(materia.area, materia.nombre, codigo)
        self.prerrequisitos.agregar_materia(codigo)
        return materia

    def registrar_materia(self, nombre, area, nivel, dificultad, tasa_reprobacion=None):
        clase_materia("mat-0000", nombre, area, nivel, dificultad, tasa_reprobacion)
        return self.agregar_materia(self.codigos.nuevo("mat"), nombre, area, nivel, dificultad, tasa_reprobacion)

    def guardar_persona(self, persona):
        self.personas.poner(persona.codigo, persona)
        self.indice_personas.insertar(clave_codigo(persona.codigo), persona)
        return persona

    def agregar_estudiante(self, codigo, nombre, semestre, carrera, disponibilidad=()):
        bloques = self.crear_bloques(disponibilidad)
        return self.guardar_persona(clase_estudiante(codigo, nombre, semestre, carrera, bloques))

    def registrar_estudiante(self, nombre, semestre, carrera, disponibilidad=()):
        clase_estudiante("e-0000", nombre, semestre, carrera, [])
        return self.agregar_estudiante(self.codigos.nuevo("e"), nombre, semestre, carrera, disponibilidad)

    def agregar_monitor(self, codigo, nombre, semestre, codigos_materias, disponibilidad=()):
        if len(codigos_materias) == 0:
            raise error_validacion("el monitor debe apoyar al menos una materia")
        self.revisar_materias(codigos_materias)
        bloques = self.crear_bloques(disponibilidad)
        return self.guardar_persona(clase_monitor(codigo, nombre, semestre, list(codigos_materias), bloques))

    def registrar_monitor(self, nombre, semestre, codigos_materias, disponibilidad=()):
        clase_monitor("m-0000", nombre, semestre, [], [])
        monitor = self.agregar_monitor(self.codigos.nuevo("m"), nombre, semestre, codigos_materias, disponibilidad)
        self.reintentar_lista_espera()
        return monitor

    def registrar_profesor(self, nombre, codigos_materias=()):
        self.revisar_materias(codigos_materias)
        profesor = clase_profesor(self.codigos.nuevo("p"), nombre, list(codigos_materias))
        return self.guardar_persona(profesor)

    def buscar(self, codigo):
        persona = self.personas.obtener(codigo)
        if persona is not None:
            return persona
        return self.materias.obtener(codigo)

    def buscar_con_comparaciones(self, codigo):
        if not isinstance(codigo, str):
            raise error_validacion("el codigo debe ser texto")
        objeto, comparaciones_avl = self.indice_personas.buscar(clave_codigo(codigo))
        if objeto is None:
            objeto, comparaciones_avl = self.indice_materias.buscar(clave_codigo(codigo))
        return {"objeto": objeto, "comparaciones_avl": comparaciones_avl,
                "pasos_hash": self.personas.pasos(codigo) if self.personas.contiene(codigo) else self.materias.pasos(codigo),
                "total_registros": len(self.indice_personas) + len(self.indice_materias),
                "altura_avl": max(self.indice_personas.altura(), self.indice_materias.altura()) + 1}

    def agregar_prerrequisito(self, codigo_materia, codigo_requisito):
        self.revisar_materias([codigo_materia, codigo_requisito])
        self.prerrequisitos.agregar(codigo_materia, codigo_requisito)

    def nombres(self, codigos):
        return [self.materias.obtener(codigo).nombre for codigo in codigos]

    def cadena_de(self, codigo_materia):
        self.revisar_materias([codigo_materia])
        return self.nombres(self.prerrequisitos.cadena(codigo_materia))

    def rutas_de(self, codigo_materia):
        self.revisar_materias([codigo_materia])
        return [self.nombres(ruta) for ruta in self.prerrequisitos.rutas(codigo_materia)]

    def registrar_cursada(self, codigo_estudiante, codigo_materia):
        self.exigir_estudiante(codigo_estudiante)
        self.revisar_materias([codigo_materia])
        return self.cursadas.registrar(codigo_estudiante, codigo_materia)

    def ha_cursado(self, codigo_estudiante, codigo_materia):
        self.exigir_estudiante(codigo_estudiante)
        return self.cursadas.ha_cursado(codigo_estudiante, codigo_materia)

    def materias_cursadas(self, codigo_estudiante):
        self.exigir_estudiante(codigo_estudiante)
        nombres = self.nombres(self.cursadas.de(codigo_estudiante).elementos())
        return ordenar_insercion(nombres, clave_texto)

    def areas_cursadas(self, codigo_estudiante):
        self.exigir_estudiante(codigo_estudiante)
        return self.areas_de_materias(self.cursadas.de(codigo_estudiante).elementos())

    def faltantes_de(self, codigo_estudiante, codigo_materia):
        self.exigir_estudiante(codigo_estudiante)
        self.revisar_materias([codigo_materia])
        cursadas = self.cursadas.de(codigo_estudiante)
        return self.nombres(self.prerrequisitos.faltantes(codigo_materia, cursadas))

    def areas_de_materias(self, codigos_materias):
        areas = conjunto()
        for codigo in codigos_materias:
            areas.agregar(self.materias.obtener(codigo).area)
        return areas

    def areas_del_sistema(self):
        areas = conjunto()
        for materia in self.materias.valores():
            areas.agregar(materia.area)
        return areas

    def areas_de_monitor(self, codigo_monitor):
        return self.areas_de_materias(self.exigir_monitor(codigo_monitor).materias)

    def areas_cubiertas(self):
        areas = conjunto()
        for persona in self.personas.valores():
            if isinstance(persona, clase_monitor):
                areas = areas.union(self.areas_de_materias(persona.materias))
        return areas

    def areas_sin_monitor(self):
        return self.areas_del_sistema().diferencia(self.areas_cubiertas())

    def monitores_por_area(self):
        mapa = tabla_hash()
        for persona in self.personas.valores():
            if isinstance(persona, clase_monitor):
                for codigo in persona.materias:
                    area = self.materias.obtener(codigo).area
                    nombres = mapa.obtener(area)
                    if nombres is None:
                        nombres = conjunto()
                        mapa.poner(area, nombres)
                    nombres.agregar(persona.nombre)
        return mapa

    def solicitudes_por_area(self):
        mapa = tabla_hash()
        for solicitud in self.solicitudes:
            mapa.poner(solicitud.materia.area, mapa.obtener(solicitud.materia.area, 0) + 1)
        return mapa

    def mostrar_areas(self):
        monitores = self.monitores_por_area()
        solicitudes = self.solicitudes_por_area()
        lineas = []
        for area in ordenar_mezcla(self.areas_del_sistema().elementos(), clave_texto):
            nombres = monitores.obtener(area)
            if nombres is None:
                texto_monitores = "ninguno"
            else:
                texto_monitores = ", ".join(ordenar_insercion(nombres.elementos(), clave_texto))
            lineas.append(f"{area:<12} | monitores: {texto_monitores} | solicitudes: {solicitudes.obtener(area, 0)}")
        return "\n".join(lineas)

    def solicitar(self, codigo_estudiante, codigo_materia, tipo, nota=None, promedio=None):
        estudiante = self.exigir_estudiante(codigo_estudiante)
        if not isinstance(codigo_materia, str) or not self.materias.contiene(codigo_materia):
            raise error_validacion("la materia '" + str(codigo_materia) + "' no existe")
        materia = self.materias.obtener(codigo_materia)
        if not isinstance(tipo, str) or tipo not in duracion_min:
            raise error_validacion("tipo de monitoria invalido (par, general o puntual)")
        if materia.nivel > estudiante.semestre:
            raise error_validacion(materia.nombre + " es de nivel " + str(materia.nivel) +
                                   " y el estudiante va en semestre " + str(estudiante.semestre))
        if self.exigir_prerrequisitos:
            faltan = self.prerrequisitos.faltantes_directos(materia.codigo, self.cursadas.de(estudiante.codigo))
            if len(faltan) > 0:
                raise error_validacion(estudiante.nombre + " no ha cursado los prerrequisitos de " + materia.nombre +
                                       ": " + ", ".join(self.nombres(faltan)))
        if self.activas.contiene(estudiante.codigo + "|" + materia.codigo):
            raise error_validacion(estudiante.nombre + " ya tiene una solicitud activa para " + materia.nombre)
        dependientes = len(self.prerrequisitos.dependientes(materia.codigo))
        resultado = prioridad.calcular_prioridad(nota, materia.tasa_reprobacion, dependientes,
                                                 self.prerrequisitos.maximo_dependientes(), promedio)
        solicitud = clase_solicitud(len(self.solicitudes) + 1, estudiante, materia, tipo, nota,
                                    self.reloj(), resultado, promedio)
        self.registrar_solicitud(solicitud)
        self.cola.encolar(solicitud)
        return solicitud

    def registrar_solicitud(self, solicitud):
        self.solicitudes.append(solicitud)
        self.activas.poner(solicitud.estudiante.codigo + "|" + solicitud.materia.codigo, solicitud.id)
        self.indice_urgencia.insertar((solicitud.urgencia, solicitud.id), solicitud)

    def buscar_solicitud(self, id):
        posicion, comparaciones = busqueda_binaria(self.solicitudes, id, lambda s: s.id)
        if posicion == -1:
            return None, comparaciones
        return self.solicitudes[posicion], comparaciones

    def solicitudes_por_urgencia(self, minimo, maximo):
        pares, visitados = self.indice_urgencia.en_rango((minimo, 0), (maximo, float("inf")))
        return [solicitud for clave, solicitud in pares if solicitud.estado != "cancelada"], visitados

    def ultima_asignacion(self):
        registro = self.historial.ver_tope()
        if registro is None:
            return None
        return registro.solicitud

    def revertir_ultima_asignacion(self):
        if self.historial.esta_vacia():
            raise error_validacion("no hay asignaciones para revertir")
        registro = self.historial.desapilar()
        solicitud = revertir_registro(registro, self.agenda)
        solicitud.revertida = True
        self.marcar(solicitud, "en_espera", "asignacion revertida")
        if solicitud.id in self.orden_atencion:
            self.orden_atencion.remove(solicitud.id)
        self.notificaciones.encolar(f"{solicitud.estudiante.nombre}: su monitoria de {solicitud.materia.nombre} "
                                    f"fue cancelada y quedo en espera")
        self.lista_espera.encolar(solicitud)
        self.reintentar_lista_espera()
        return solicitud

    def reencolar(self, id_solicitud):
        solicitud, comparaciones = self.buscar_solicitud(id_solicitud)
        if solicitud is None or not solicitud.revertida:
            raise error_validacion("la solicitud " + str(id_solicitud) + " no es una asignacion revertida")
        solicitud.revertida = False
        self.reintentar_lista_espera()
        return solicitud

    def mostrar_historial(self):
        if self.historial.esta_vacia():
            return "(sin asignaciones)"
        lineas = []
        for registro in self.historial.como_lista():
            s = registro.solicitud
            accion = "sesion nueva" if registro.creo_sesion else "se unio a un grupo"
            lineas.append(f"#{s.id} {s.estudiante.nombre:<6} {s.materia.nombre:<22} {accion}")
        return "\n".join(lineas)

    def listar_solicitudes(self, criterio, metodo="auto", estado=None):
        lista = [s for s in self.solicitudes if estado is None or s.estado == estado]
        return ordenar(lista, criterio, metodo)

    def mostrar_listado(self, criterio, metodo="auto", estado=None):
        lista = self.listar_solicitudes(criterio, metodo, estado)
        if len(lista) == 0:
            return "(sin solicitudes)"
        lineas = []
        for s in lista:
            lineas.append(f"#{s.id} {s.estudiante.nombre:<6} {s.materia.nombre:<22} "
                          f"{s.prioridad:<6} (u={s.urgencia:.3f}) {s.estado}")
        return "\n".join(lineas)

    def mostrar_cola(self):
        ahora = self.reloj()
        lineas = []
        for titulo, fila in [("pendientes", self.cola), ("en espera", self.lista_espera)]:
            lineas.append(titulo + " (de mayor a menor prioridad efectiva):")
            if len(fila) == 0:
                lineas.append("  (ninguna)")
            for s in fila.pendientes():
                efectiva = prioridad.prioridad_efectiva(s.urgencia, s.llegada, ahora, self.dias_envejecimiento)
                extra = " [revertida]" if s.revertida else ""
                lineas.append(f"  #{s.id} {s.estudiante.nombre:<6} {s.materia.nombre:<22} "
                              f"u={s.urgencia:.3f} efectiva={efectiva:.3f}{extra}")
        return "\n".join(lineas)

    def generar_agenda(self):
        while not self.cola.esta_vacia():
            solicitud = self.cola.desencolar()
            if not self.asignar(solicitud):
                self.lista_espera.encolar(solicitud)
        return self.agenda

    def reintentar_lista_espera(self):
        en_espera = []
        while not self.lista_espera.esta_vacia():
            en_espera.append(self.lista_espera.desencolar())
        asignadas = []
        for solicitud in en_espera:
            if solicitud.revertida:
                self.lista_espera.encolar(solicitud)
            elif self.asignar(solicitud):
                asignadas.append(solicitud)
            else:
                self.lista_espera.encolar(solicitud)
        return asignadas

    def agregar_disponibilidad_monitor(self, codigo, disponibilidad):
        monitor = self.exigir_monitor(codigo)
        monitor.disponibilidad.extend(self.crear_bloques(disponibilidad))
        return self.reintentar_lista_espera()

    def agregar_disponibilidad_estudiante(self, codigo, disponibilidad):
        estudiante = self.exigir_estudiante(codigo)
        estudiante.disponibilidad.extend(self.crear_bloques(disponibilidad))
        return self.reintentar_lista_espera()

    def monitores_de(self, materia):
        encontrados = [p for p in self.personas.valores()
                       if isinstance(p, clase_monitor) and materia.codigo in p.materias]
        return sorted(encontrados, key=lambda monitor: monitor.codigo)

    def estudiante_puede(self, estudiante, dia, inicio, fin):
        return (cubierto(estudiante.disponibilidad, dia, inicio, fin)
                and self.agenda.estudiante_libre(estudiante, dia, inicio, fin))

    def confirmar(self, solicitud, sesion, creo_sesion, motivo):
        self.historial.apilar(clase_registro_asignacion(solicitud, sesion, creo_sesion))
        self.orden_atencion.append(solicitud.id)
        self.marcar(solicitud, "asignada", motivo)
        self.notificaciones.encolar(f"{solicitud.estudiante.nombre}: su monitoria de {solicitud.materia.nombre} "
                                    f"fue asignada ({sesion.dia} {minutos_a_hora(sesion.inicio)}, "
                                    f"monitor {sesion.monitor.nombre})")

    def entregar_notificaciones(self):
        entregadas = []
        while not self.notificaciones.esta_vacia():
            entregadas.append(self.notificaciones.desencolar())
        return entregadas

    def unirse_a_grupo(self, solicitud):
        estudiante = solicitud.estudiante
        for sesion in self.agenda.sesiones:
            if sesion.tipo != "general" or sesion.materia.codigo != solicitud.materia.codigo:
                continue
            if len(sesion.estudiantes) >= cupo[sesion.tipo]:
                continue
            if self.estudiante_puede(estudiante, sesion.dia, sesion.inicio, sesion.fin):
                sesion.estudiantes.append(estudiante)
                self.confirmar(solicitud, sesion, False, "se unio al grupo de " + sesion.monitor.nombre)
                return True
        return False

    def buscar_hueco(self, monitor, estudiante, duracion):
        for bloque_monitor in fusionar_bloques(monitor.disponibilidad):
            for bloque_estudiante in fusionar_bloques(estudiante.disponibilidad):
                if bloque_monitor.dia != bloque_estudiante.dia:
                    continue
                desde = max(bloque_monitor.inicio, bloque_estudiante.inicio)
                hasta = min(bloque_monitor.fin, bloque_estudiante.fin)
                dia = bloque_monitor.dia
                inicio = desde
                while inicio + duracion <= hasta:
                    fin = inicio + duracion
                    if (self.agenda.monitor_libre(monitor, dia, inicio, fin)
                            and self.agenda.estudiante_libre(estudiante, dia, inicio, fin)):
                        return dia, inicio
                    inicio += paso_min
        return None

    def asignar(self, solicitud):
        estudiante = solicitud.estudiante
        duracion = duracion_min[solicitud.tipo]
        if solicitud.tipo == "general" and self.unirse_a_grupo(solicitud):
            return True
        monitores = self.monitores_de(solicitud.materia)
        if len(monitores) == 0:
            self.marcar(solicitud, "en_espera", "no hay monitor para la materia")
            return False
        if len(estudiante.disponibilidad) == 0:
            self.marcar(solicitud, "en_espera", "el estudiante no registro disponibilidad")
            return False
        if all(len(monitor.disponibilidad) == 0 for monitor in monitores):
            self.marcar(solicitud, "en_espera", "el monitor aun no publica horarios")
            return False
        for monitor in monitores:
            hueco = self.buscar_hueco(monitor, estudiante, duracion)
            if hueco is not None:
                dia, inicio = hueco
                sesion = clase_sesion(monitor, solicitud.materia, solicitud.tipo, dia, inicio,
                                      inicio + duracion, [estudiante])
                self.agenda.sesiones.append(sesion)
                self.confirmar(solicitud, sesion, True, "monitor " + monitor.nombre)
                return True
        self.marcar(solicitud, "en_espera", "no hay horarios o cupos compatibles entre estudiante y monitor")
        return False

    def marcar(self, solicitud, estado, motivo):
        solicitud.estado = estado
        solicitud.motivo = motivo

    def informe_cobertura(self):
        asignadas = 0
        en_espera = 0
        pendientes = 0
        detalle_en_espera = []
        por_materia = {}
        canceladas = 0
        for solicitud in self.solicitudes:
            if solicitud.estado == "cancelada":
                canceladas += 1
                continue
            nombre = solicitud.materia.nombre
            total_materia, atendidas = por_materia.get(nombre, (0, 0))
            if solicitud.estado == "asignada":
                asignadas += 1
                atendidas += 1
            elif solicitud.estado == "en_espera":
                en_espera += 1
                detalle_en_espera.append((solicitud.id, solicitud.estudiante.nombre, nombre, solicitud.motivo))
            else:
                pendientes += 1
            por_materia[nombre] = (total_materia + 1, atendidas)
        horas_monitor = {}
        for sesion in self.agenda.sesiones:
            nombre = sesion.monitor.nombre
            horas_monitor[nombre] = horas_monitor.get(nombre, 0) + (sesion.fin - sesion.inicio) / 60
        total = len(self.solicitudes) - canceladas
        porcentaje = round(100 * asignadas / total, 1) if total > 0 else 0.0
        return {"total": total, "asignadas": asignadas, "en_espera": en_espera,
                "pendientes": pendientes, "canceladas": canceladas, "porcentaje": porcentaje,
                "por_materia": por_materia, "horas_monitor": horas_monitor,
                "detalle_en_espera": detalle_en_espera}

    def mostrar_informe(self):
        r = self.informe_cobertura()
        lineas = [f"solicitudes: {r['total']} | asignadas: {r['asignadas']} | "
                  f"en espera: {r['en_espera']} | pendientes: {r['pendientes']} | cobertura: {r['porcentaje']}%"]
        if r["canceladas"] > 0:
            lineas[0] += f" | canceladas (no cuentan): {r['canceladas']}"
        for materia, (total, atendidas) in r["por_materia"].items():
            lineas.append(f"  - {materia}: {atendidas}/{total} atendidas")
        for monitor, horas in r["horas_monitor"].items():
            lineas.append(f"  - monitor {monitor}: {horas:.1f} h agendadas")
        for id, estudiante, materia, motivo in r["detalle_en_espera"]:
            lineas.append(f"  ! solicitud {id} ({estudiante}, {materia}): {motivo}")
        return "\n".join(lineas)

    def mostrar_catalogo(self, invertido=False):
        return self.catalogo.mostrar(invertido)

    def informe_red(self):
        grafo = self.prerrequisitos.grafo
        componentes = [self.nombres(c) for c in grafo.componentes()]
        diametro, par = grafo.diametro(False)
        return {"materias": len(grafo), "relaciones": grafo.aristas,
                "representacion": grafo.justificar_representacion(),
                "islas": sorted(componentes, key=lambda c: (-len(c), c)),
                "ciclos": [self.nombres(c) for c in grafo.detectar_ciclos()],
                "ruta_critica": self.nombres(grafo.camino_mas_largo()),
                "diametro": diametro,
                "par_diametro": None if par is None else (self.nombres([par[0]])[0], self.nombres([par[1]])[0])}

    def mostrar_red(self):
        r = self.informe_red()
        rep = r["representacion"]
        lineas = [f"materias: {r['materias']} | relaciones: {r['relaciones']} | densidad: {rep['densidad']:.3f}",
                  f"representacion: {rep['decision']} ({rep['celdas_lista']} celdas frente a {rep['celdas_matriz']} "
                  f"de la matriz): {rep['motivo']}",
                  f"islas desconectadas: {len(r['islas'])}"]
        for i, isla in enumerate(r["islas"], 1):
            lineas.append(f"  isla {i} ({len(isla)}): " + ", ".join(isla))
        lineas.append("ciclos: " + ("ninguno" if len(r["ciclos"]) == 0 else str(r["ciclos"])))
        if len(r["ruta_critica"]) > 0:
            lineas.append(f"cadena de prerrequisitos mas larga ({len(r['ruta_critica'])} materias, "
                          f"minimo {len(r['ruta_critica'])} semestres): " + " -> ".join(r["ruta_critica"]))
        if r["par_diametro"] is not None:
            lineas.append(f"diametro (grados de separacion): {r['diametro']} entre "
                          f"{r['par_diametro'][0]} y {r['par_diametro'][1]}")
        return "\n".join(lineas)

    def ruta_entre(self, codigo_origen, codigo_destino):
        self.revisar_materias([codigo_origen, codigo_destino])
        grafo = self.prerrequisitos.grafo
        dirigida = grafo.ruta_mas_corta(codigo_origen, codigo_destino, True)
        sin_direccion = grafo.ruta_mas_corta(codigo_origen, codigo_destino, False)
        return {"dirigida": None if dirigida is None else self.nombres(dirigida),
                "sin_direccion": None if sin_direccion is None else self.nombres(sin_direccion)}

    def impacto_de(self, codigo_materia):
        self.revisar_materias([codigo_materia])
        olas = self.prerrequisitos.grafo.olas_desde(codigo_materia, "dependientes")
        return [self.nombres(ola) for ola in olas]

    def orden_de_cursado(self):
        return self.nombres(self.prerrequisitos.grafo.orden_topologico())

    def plan_para(self, codigo_estudiante, codigo_materia):
        self.exigir_estudiante(codigo_estudiante)
        self.revisar_materias([codigo_materia])
        cursadas = self.cursadas.de(codigo_estudiante)
        return self.nombres(self.prerrequisitos.faltantes(codigo_materia, cursadas))
