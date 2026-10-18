paso_min = 30    # se prueban horas de inicio cada 30 minutos
 
 
class clase_sesion:
    """una monitoria ya programada: quien, que materia, cuando y con que estudiantes."""
 
    def __init__(self, monitor, materia, tipo, dia, inicio, fin, estudiantes):
        self.monitor = monitor
        self.materia = materia
        self.tipo = tipo
        self.dia = dia
        self.inicio = inicio
        self.fin = fin
        self.estudiantes = estudiantes    # lista de estudiantes
 
    def se_cruza(self, dia, inicio, fin):
        """dice si el rango pedido choca con esta sesion (comparten algun minuto)."""
        return self.dia == dia and inicio < self.fin and self.inicio < fin
 
 
class agenda:
    def __init__(self):
        self.sesiones = []
 
    def monitor_libre(self, monitor, dia, inicio, fin):
        """dice si el monitor no tiene ninguna sesion que choque con ese rango."""
        for sesion in self.sesiones:
            if sesion.monitor.codigo == monitor.codigo and sesion.se_cruza(dia, inicio, fin):
                return False
        return True
 
    def estudiante_libre(self, estudiante, dia, inicio, fin):
        """dice si el estudiante no tiene ninguna sesion que choque con ese rango."""
        for sesion in self.sesiones:
            if not sesion.se_cruza(dia, inicio, fin):
                continue
            for otro in sesion.estudiantes:
                if otro.codigo == estudiante.codigo:
                    return False
        return True
 
    def ordenadas(self):
        """devuelve las sesiones ordenadas por dia de la semana y luego por hora."""
        def orden(sesion):
            return (dias.index(sesion.dia), sesion.inicio)
        return sorted(self.sesiones, key=orden)
 
    def mostrar(self):
        """devuelve la agenda como texto, una sesion por linea."""
        if len(self.sesiones) == 0:
            return "(agenda vacia)"
        lineas = []
        for sesion in self.ordenadas():
            nombres = ", ".join([e.nombre for e in sesion.estudiantes])
            lineas.append(f"{sesion.dia:<10} {minutos_a_hora(sesion.inicio)}-{minutos_a_hora(sesion.fin)}"
                          f" | {sesion.tipo:<7} | {sesion.materia.nombre}"
                          f" | monitor: {sesion.monitor.nombre} | estudiantes: {nombres}")
        return "\n".join(lineas)