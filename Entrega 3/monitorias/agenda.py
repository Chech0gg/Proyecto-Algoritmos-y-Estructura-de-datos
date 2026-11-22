from .tiempo import dias, minutos_a_hora


class clase_sesion:

    def __init__(self, monitor, materia, tipo, dia, inicio, fin, estudiantes):
        self.monitor = monitor
        self.materia = materia
        self.tipo = tipo
        self.dia = dia
        self.inicio = inicio
        self.fin = fin
        self.estudiantes = estudiantes

    def se_cruza(self, dia, inicio, fin):
        return self.dia == dia and inicio < self.fin and self.inicio < fin


class clase_registro_asignacion:

    def __init__(self, solicitud, sesion, creo_sesion):
        self.solicitud = solicitud
        self.sesion = sesion
        self.creo_sesion = creo_sesion


def revertir_registro(registro, agenda_actual):
    if registro.creo_sesion:
        agenda_actual.sesiones.remove(registro.sesion)
    else:
        registro.sesion.estudiantes.remove(registro.solicitud.estudiante)
        if len(registro.sesion.estudiantes) == 0:
            agenda_actual.sesiones.remove(registro.sesion)
    return registro.solicitud


class agenda:

    def __init__(self):
        self.sesiones = []

    def monitor_libre(self, monitor, dia, inicio, fin):
        for sesion in self.sesiones:
            if sesion.monitor.codigo == monitor.codigo and sesion.se_cruza(dia, inicio, fin):
                return False
        return True

    def estudiante_libre(self, estudiante, dia, inicio, fin):
        for sesion in self.sesiones:
            if not sesion.se_cruza(dia, inicio, fin):
                continue
            for otro in sesion.estudiantes:
                if otro.codigo == estudiante.codigo:
                    return False
        return True

    def ordenadas(self):
        return sorted(self.sesiones, key=lambda sesion: (dias.index(sesion.dia), sesion.inicio))

    def mostrar(self):
        if len(self.sesiones) == 0:
            return "(agenda vacia)"
        lineas = []
        for sesion in self.ordenadas():
            nombres = ", ".join([e.nombre for e in sesion.estudiantes])
            lineas.append(f"{sesion.dia:<10} {minutos_a_hora(sesion.inicio)}-{minutos_a_hora(sesion.fin)}"
                          f" | {sesion.tipo:<7} | {sesion.materia.nombre}"
                          f" | monitor: {sesion.monitor.nombre} | estudiantes: {nombres}")
        return "\n".join(lineas)
