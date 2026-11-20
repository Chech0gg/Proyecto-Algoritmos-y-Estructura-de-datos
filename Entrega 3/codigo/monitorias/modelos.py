from . import validaciones


def clave_codigo(codigo):
    prefijo, separador, numero = codigo.rpartition("-")
    if separador == "-" and numero.isdigit():
        return (prefijo, int(numero))
    return (codigo, 0)


class generador_codigos:

    def __init__(self):
        self.contadores = {}

    def nuevo(self, prefijo):
        if prefijo not in self.contadores:
            self.contadores[prefijo] = 0
        self.contadores[prefijo] += 1
        return prefijo + "-" + f"{self.contadores[prefijo]:04d}"


class clase_materia:

    def __init__(self, codigo, nombre, area, nivel, dificultad, tasa_reprobacion=None):
        self.codigo = codigo
        self.nombre = validaciones.texto(nombre, "el nombre de la materia")
        self.area = validaciones.texto(area, "el area de la materia")
        self.nivel = validaciones.entero(nivel, "el nivel", 1, 12)
        self.dificultad = validaciones.entero(dificultad, "la dificultad", 1, 5)
        self.tasa_reprobacion = None
        if tasa_reprobacion is not None:
            self.tasa_reprobacion = validaciones.decimal(tasa_reprobacion, "la tasa de reprobacion", 0.0, 1.0)


class clase_persona:

    def __init__(self, codigo, nombre):
        self.codigo = codigo
        self.nombre = validaciones.texto(nombre, "el nombre")


class clase_estudiante(clase_persona):

    def __init__(self, codigo, nombre, semestre, carrera, disponibilidad):
        clase_persona.__init__(self, codigo, nombre)
        self.semestre = validaciones.entero(semestre, "el semestre", 1, 12)
        self.carrera = validaciones.texto(carrera, "la carrera")
        self.disponibilidad = disponibilidad

    def __str__(self):
        return f"estudiante {self.codigo}: {self.nombre}, semestre {self.semestre}, {self.carrera}"


class clase_monitor(clase_persona):

    def __init__(self, codigo, nombre, semestre, materias, disponibilidad):
        clase_persona.__init__(self, codigo, nombre)
        self.semestre = validaciones.entero(semestre, "el semestre", 1, 12)
        self.materias = materias
        self.disponibilidad = disponibilidad

    def __str__(self):
        return f"monitor {self.codigo}: {self.nombre}, semestre {self.semestre}"


class clase_profesor(clase_persona):

    def __init__(self, codigo, nombre, materias):
        clase_persona.__init__(self, codigo, nombre)
        self.materias = materias

    def __str__(self):
        return f"profesor {self.codigo}: {self.nombre}"


class clase_solicitud:

    def __init__(self, id, estudiante, materia, tipo, nota, llegada, resultado):
        self.id = id
        self.estudiante = estudiante
        self.materia = materia
        self.tipo = tipo
        self.nota = nota
        self.llegada = llegada
        self.riesgo = resultado.riesgo
        self.impacto = resultado.impacto
        self.urgencia = resultado.urgencia
        self.prioridad = resultado.nivel
        self.desglose = resultado.desglose
        self.estado = "pendiente"
        self.motivo = ""
        self.revertida = False
