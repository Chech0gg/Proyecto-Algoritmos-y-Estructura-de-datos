from . import validaciones
from .agenda import clase_sesion
from .cuentas import rol_administrador, rol_estudiante, rol_monitor
from .errores import error_validacion
from .listas import pila
from .modelos import clase_estudiante, clase_monitor
from .tiempo import cubierto, duracion_min, fusionar_bloques, hora_a_minutos, minutos_a_hora, normalizar_dia


class gestion_usuarios:

    def registrar_cuenta_estudiante(self, usuario, contrasena, nombre, semestre, carrera, disponibilidad=()):
        self.cuentas.revisar_disponible(usuario, contrasena)
        estudiante = self.registrar_estudiante(nombre, semestre, carrera, disponibilidad)
        self.cuentas.crear(usuario, contrasena, estudiante.nombre, rol_estudiante, estudiante.codigo)
        return estudiante

    def registrar_cuenta_monitor(self, usuario, contrasena, nombre, semestre, codigos_materias, disponibilidad=()):
        self.cuentas.revisar_disponible(usuario, contrasena)
        monitor = self.registrar_monitor(nombre, semestre, codigos_materias, disponibilidad)
        self.cuentas.crear(usuario, contrasena, monitor.nombre, rol_monitor, monitor.codigo)
        return monitor

    def registrar_cuenta_administrador(self, usuario, contrasena, nombre):
        nombre = validaciones.texto(nombre, "el nombre")
        return self.cuentas.crear(usuario, contrasena, nombre, rol_administrador)

    def iniciar_sesion(self, usuario, contrasena):
        return self.cuentas.iniciar_sesion(usuario, contrasena)

    def mostrar_cuentas(self):
        lineas = []
        for cuenta in self.cuentas.todas():
            estado = "BLOQUEADA" if cuenta.bloqueada else "activa"
            ligada = "" if cuenta.codigo_persona is None else f" ({cuenta.codigo_persona})"
            lineas.append(f"{cuenta.usuario:<14} {cuenta.rol:<14} {cuenta.nombre}{ligada} - {estado}")
        return "\n".join(lineas) if len(lineas) > 0 else "(sin usuarios)"

    def solicitudes_de(self, codigo_estudiante):
        self.exigir_estudiante(codigo_estudiante)
        return [s for s in self.solicitudes if s.estudiante.codigo == codigo_estudiante]

    def mostrar_solicitudes_de(self, codigo_estudiante):
        lista = self.solicitudes_de(codigo_estudiante)
        if len(lista) == 0:
            return "(no ha pedido monitorias)"
        lineas = []
        for s in lista:
            motivo = f" - {s.motivo}" if s.motivo != "" else ""
            lineas.append(f"#{s.id} {s.materia.nombre:<22} {s.tipo:<7} prioridad {s.prioridad:<5} "
                          f"(urgencia {s.urgencia:.3f}) {s.estado}{motivo}")
        return "\n".join(lineas)

    def texto_sesion(self, sesion):
        nombres = ", ".join([e.nombre for e in sesion.estudiantes])
        return (f"{sesion.dia:<10} {minutos_a_hora(sesion.inicio)}-{minutos_a_hora(sesion.fin)}"
                f" | {sesion.tipo:<7} | {sesion.materia.nombre}"
                f" | monitor: {sesion.monitor.nombre} | estudiantes: {nombres}")

    def sesiones_de(self, codigo_persona):
        persona = self.personas.obtener(codigo_persona)
        if isinstance(persona, clase_monitor):
            return [s for s in self.agenda.ordenadas() if s.monitor.codigo == codigo_persona]
        if isinstance(persona, clase_estudiante):
            return [s for s in self.agenda.ordenadas() if any(e.codigo == codigo_persona for e in s.estudiantes)]
        raise error_validacion("'" + str(codigo_persona) + "' no es un estudiante ni un monitor")

    def mostrar_sesiones_de(self, codigo_persona):
        sesiones = self.sesiones_de(codigo_persona)
        if len(sesiones) == 0:
            return "(sin sesiones agendadas)"
        return "\n".join(self.texto_sesion(s) for s in sesiones)

    def mostrar_agenda_numerada(self):
        sesiones = self.agenda.ordenadas()
        if len(sesiones) == 0:
            return "(agenda vacia)"
        return "\n".join(f"{i:>2}. {self.texto_sesion(s)}" for i, s in enumerate(sesiones, 1))

    def sesion_por_numero(self, numero):
        sesiones = self.agenda.ordenadas()
        if not isinstance(numero, int) or isinstance(numero, bool) or not 1 <= numero <= len(sesiones):
            raise error_validacion("no existe la sesion numero " + str(numero))
        return sesiones[numero - 1]

    def persona_con_horario(self, codigo):
        persona = self.personas.obtener(codigo) if isinstance(codigo, str) else None
        if not isinstance(persona, (clase_monitor, clase_estudiante)):
            raise error_validacion("'" + str(codigo) + "' no es un estudiante ni un monitor")
        return persona

    def mostrar_disponibilidad(self, codigo):
        persona = self.persona_con_horario(codigo)
        if len(persona.disponibilidad) == 0:
            return "(sin horarios libres registrados)"
        return "\n".join(f"{i:>2}. {b.dia} {minutos_a_hora(b.inicio)}-{minutos_a_hora(b.fin)}"
                         for i, b in enumerate(persona.disponibilidad, 1))

    def quitar_disponibilidad(self, codigo, numero):
        persona = self.persona_con_horario(codigo)
        if not isinstance(numero, int) or isinstance(numero, bool) or not 1 <= numero <= len(persona.disponibilidad):
            raise error_validacion("no existe el horario numero " + str(numero))
        restantes = persona.disponibilidad[:numero - 1] + persona.disponibilidad[numero:]
        for sesion in self.agenda.sesiones:
            participa = sesion.monitor.codigo == codigo or any(e.codigo == codigo for e in sesion.estudiantes)
            if participa and not cubierto(restantes, sesion.dia, sesion.inicio, sesion.fin):
                raise error_validacion(f"no se puede quitar: hay una sesion agendada el {sesion.dia} "
                                       f"{minutos_a_hora(sesion.inicio)}-{minutos_a_hora(sesion.fin)} que usa ese horario")
        persona.disponibilidad = restantes

    def agregar_especialidad(self, codigo_monitor, codigo_materia):
        monitor = self.exigir_monitor(codigo_monitor)
        self.revisar_materias([codigo_materia])
        if codigo_materia in monitor.materias:
            raise error_validacion("ya apoya esa materia")
        monitor.materias.append(codigo_materia)
        return self.reintentar_lista_espera()

    def quitar_especialidad(self, codigo_monitor, codigo_materia):
        monitor = self.exigir_monitor(codigo_monitor)
        if codigo_materia not in monitor.materias:
            raise error_validacion("el monitor no apoya esa materia")
        if len(monitor.materias) == 1:
            raise error_validacion("el monitor debe apoyar al menos una materia")
        for sesion in self.agenda.sesiones:
            if sesion.monitor.codigo == codigo_monitor and sesion.materia.codigo == codigo_materia:
                raise error_validacion("no se puede quitar: tiene sesiones agendadas de esa materia")
        monitor.materias.remove(codigo_materia)

    def mostrar_especialidades(self, codigo_monitor):
        monitor = self.exigir_monitor(codigo_monitor)
        if len(monitor.materias) == 0:
            return "(ninguna)"
        return "\n".join(f"  {c}  {self.materias.obtener(c).nombre} ({self.materias.obtener(c).area})"
                         for c in sorted(monitor.materias))

    def mostrar_horarios_monitores(self):
        monitores = sorted([p for p in self.personas.valores() if isinstance(p, clase_monitor)],
                           key=lambda m: m.codigo)
        if len(monitores) == 0:
            return "(no hay monitores)"
        lineas = []
        for m in monitores:
            ocupados = sum(s.fin - s.inicio for s in self.agenda.sesiones if s.monitor.codigo == m.codigo)
            libres = sum(b.fin - b.inicio for b in fusionar_bloques(m.disponibilidad))
            lineas.append(f"{m.codigo} {m.nombre} - apoya: " + ", ".join(self.nombres(sorted(m.materias))))
            bloques = fusionar_bloques(m.disponibilidad)
            if len(bloques) == 0:
                lineas.append("    sin horarios libres registrados")
            for b in bloques:
                lineas.append(f"    {b.dia:<10} {minutos_a_hora(b.inicio)}-{minutos_a_hora(b.fin)}")
            lineas.append(f"    horas publicadas: {libres / 60:.1f} | agendadas: {ocupados / 60:.1f}")
        return "\n".join(lineas)

    def mostrar_horarios_estudiantes(self):
        estudiantes = sorted([p for p in self.personas.valores() if isinstance(p, clase_estudiante)],
                             key=lambda e: e.codigo)
        if len(estudiantes) == 0:
            return "(no hay estudiantes)"
        lineas = []
        for e in estudiantes:
            bloques = fusionar_bloques(e.disponibilidad)
            texto = ", ".join(f"{b.dia} {minutos_a_hora(b.inicio)}-{minutos_a_hora(b.fin)}" for b in bloques)
            lineas.append(f"{e.codigo} {e.nombre}: " + (texto if texto != "" else "sin horarios registrados"))
        return "\n".join(lineas)

    def purgar_historial(self, quitar):
        nueva = pila()
        for registro in reversed(self.historial.como_lista()):
            if not quitar(registro):
                nueva.apilar(registro)
        self.historial = nueva

    def sacar_de_sesion(self, solicitud):
        codigo = solicitud.estudiante.codigo
        for sesion in list(self.agenda.sesiones):
            if sesion.materia.codigo == solicitud.materia.codigo and any(e.codigo == codigo for e in sesion.estudiantes):
                sesion.estudiantes = [e for e in sesion.estudiantes if e.codigo != codigo]
                if len(sesion.estudiantes) == 0:
                    self.agenda.sesiones.remove(sesion)

    def cancelar_solicitud(self, id_solicitud, codigo_estudiante=None, por_administrador=False):
        solicitud, comparaciones = self.buscar_solicitud(id_solicitud)
        if solicitud is None:
            raise error_validacion("no existe la solicitud " + str(id_solicitud))
        if codigo_estudiante is not None and solicitud.estudiante.codigo != codigo_estudiante:
            raise error_validacion("esa solicitud no es suya")
        if solicitud.estado == "cancelada":
            raise error_validacion("la solicitud ya estaba cancelada")
        if solicitud.estado == "asignada":
            self.sacar_de_sesion(solicitud)
            self.purgar_historial(lambda registro: registro.solicitud is solicitud)
            if solicitud.id in self.orden_atencion:
                self.orden_atencion.remove(solicitud.id)
        else:
            self.cola.quitar(solicitud)
            self.lista_espera.quitar(solicitud)
        self.activas.eliminar(solicitud.estudiante.codigo + "|" + solicitud.materia.codigo)
        self.marcar(solicitud, "cancelada", "cancelada por el administrador" if por_administrador else "cancelada por el estudiante")
        if por_administrador:
            self.notificaciones.encolar(f"{solicitud.estudiante.nombre}: su solicitud de {solicitud.materia.nombre} "
                                        f"fue cancelada por el administrador")
        self.reintentar_lista_espera()
        return solicitud

    def agendar_manual(self, id_solicitud, codigo_monitor, dia, hora_inicio):
        solicitud, comparaciones = self.buscar_solicitud(id_solicitud)
        if solicitud is None:
            raise error_validacion("no existe la solicitud " + str(id_solicitud))
        if solicitud.estado not in ("pendiente", "en_espera"):
            raise error_validacion("solo se pueden agendar solicitudes pendientes o en espera (esta esta " + solicitud.estado + ")")
        monitor = self.exigir_monitor(codigo_monitor)
        if solicitud.materia.codigo not in monitor.materias:
            raise error_validacion(monitor.nombre + " no apoya " + solicitud.materia.nombre)
        dia = normalizar_dia(dia)
        inicio = hora_a_minutos(hora_inicio)
        fin = inicio + duracion_min[solicitud.tipo]
        if fin > 1440:
            raise error_validacion("la sesion terminaria despues de medianoche")
        estudiante = solicitud.estudiante
        if not cubierto(monitor.disponibilidad, dia, inicio, fin):
            raise error_validacion(monitor.nombre + " no tiene ese horario libre")
        if not cubierto(estudiante.disponibilidad, dia, inicio, fin):
            raise error_validacion(estudiante.nombre + " no tiene ese horario libre")
        if not self.agenda.monitor_libre(monitor, dia, inicio, fin):
            raise error_validacion(monitor.nombre + " ya tiene una sesion que se cruza con ese horario")
        if not self.agenda.estudiante_libre(estudiante, dia, inicio, fin):
            raise error_validacion(estudiante.nombre + " ya tiene una sesion que se cruza con ese horario")
        self.cola.quitar(solicitud)
        self.lista_espera.quitar(solicitud)
        solicitud.revertida = False
        sesion = clase_sesion(monitor, solicitud.materia, solicitud.tipo, dia, inicio, fin, [estudiante])
        self.agenda.sesiones.append(sesion)
        self.confirmar(solicitud, sesion, True, "agendada por el administrador con " + monitor.nombre)
        return sesion

    def modificar_sesion(self, numero, dia, hora_inicio, codigo_monitor=None):
        sesion = self.sesion_por_numero(numero)
        monitor = sesion.monitor if codigo_monitor is None else self.exigir_monitor(codigo_monitor)
        if sesion.materia.codigo not in monitor.materias:
            raise error_validacion(monitor.nombre + " no apoya " + sesion.materia.nombre)
        dia = normalizar_dia(dia)
        inicio = hora_a_minutos(hora_inicio)
        fin = inicio + (sesion.fin - sesion.inicio)
        if fin > 1440:
            raise error_validacion("la sesion terminaria despues de medianoche")
        if not cubierto(monitor.disponibilidad, dia, inicio, fin):
            raise error_validacion(monitor.nombre + " no tiene ese horario libre")
        for estudiante in sesion.estudiantes:
            if not cubierto(estudiante.disponibilidad, dia, inicio, fin):
                raise error_validacion(estudiante.nombre + " no tiene ese horario libre")
        posicion = self.agenda.sesiones.index(sesion)
        self.agenda.sesiones.pop(posicion)
        try:
            if not self.agenda.monitor_libre(monitor, dia, inicio, fin):
                raise error_validacion(monitor.nombre + " ya tiene una sesion que se cruza con ese horario")
            for estudiante in sesion.estudiantes:
                if not self.agenda.estudiante_libre(estudiante, dia, inicio, fin):
                    raise error_validacion(estudiante.nombre + " ya tiene una sesion que se cruza con ese horario")
        except error_validacion:
            self.agenda.sesiones.insert(posicion, sesion)
            raise
        sesion.monitor = monitor
        sesion.dia = dia
        sesion.inicio = inicio
        sesion.fin = fin
        self.agenda.sesiones.insert(posicion, sesion)
        for estudiante in sesion.estudiantes:
            self.notificaciones.encolar(f"{estudiante.nombre}: su monitoria de {sesion.materia.nombre} cambio a "
                                        f"{dia} {minutos_a_hora(inicio)} (monitor {monitor.nombre})")
        return sesion

    def cancelar_sesion(self, numero):
        sesion = self.sesion_por_numero(numero)
        for estudiante in list(sesion.estudiantes):
            for solicitud in self.solicitudes:
                if (solicitud.estudiante.codigo == estudiante.codigo and solicitud.estado == "asignada"
                        and solicitud.materia.codigo == sesion.materia.codigo):
                    solicitud.revertida = True
                    self.marcar(solicitud, "en_espera", "sesion cancelada por el administrador")
                    if solicitud.id in self.orden_atencion:
                        self.orden_atencion.remove(solicitud.id)
                    self.lista_espera.encolar(solicitud)
                    self.notificaciones.encolar(f"{estudiante.nombre}: su monitoria de {sesion.materia.nombre} "
                                                f"fue cancelada por el administrador y quedo en espera")
        self.agenda.sesiones.remove(sesion)
        self.purgar_historial(lambda registro: registro.sesion is sesion)
        return sesion
