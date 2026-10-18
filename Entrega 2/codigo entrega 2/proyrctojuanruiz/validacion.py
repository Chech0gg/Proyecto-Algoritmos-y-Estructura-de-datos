class error_validacion(Exception):
    """se lanza cuando un dato que se quiere registrar no es valido."""
 
 
class tipo_monitoria:
    """los tres tipos de monitoria que existen (son solo textos)."""
    par = "par"            # uno a uno, personalizada
    general = "general"    # grupo de varios estudiantes
    puntual = "puntual"    # corta y concreta
 
 
# cuanto dura cada tipo de monitoria, en minutos
duracion_min = {"par": 60, "general": 90, "puntual": 30}
 
# cuantos estudiantes caben en cada tipo de monitoria
cupo = {"par": 1, "general": 5, "puntual": 1}
 
# dias en los que se puede dar monitoria
dias = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado"]
 
 
def hora_a_minutos(texto):
    """convierte "08:30" en minutos desde medianoche (510).
    se usan minutos porque es mas facil comparar numeros que textos."""
    partes = str(texto).split(":")
    if len(partes) != 2 or not partes[0].strip().isdigit() or not partes[1].strip().isdigit():
        raise error_validacion("hora invalida: '" + str(texto) + "' (use hh:mm)")
    horas = int(partes[0])
    minutos = int(partes[1])
    if horas > 23 or minutos > 59:
        raise error_validacion("hora fuera de rango: '" + str(texto) + "'")
    return horas * 60 + minutos
 
 
def minutos_a_hora(minutos):
    """lo contrario: convierte 510 en "08:30"."""
    horas = minutos // 60
    resto = minutos % 60
    return f"{horas:02d}:{resto:02d}"
 
 
class clase_bloque:
    """una franja de tiempo libre: un dia, una hora de inicio y una de fin
    (inicio y fin guardados en minutos)."""
 
    def __init__(self, dia, inicio, fin):
        self.dia = dia
        self.inicio = inicio
        self.fin = fin
 
    def cubre(self, dia, inicio, fin):
        """dice si este bloque contiene completo el rango pedido."""
        return self.dia == dia and self.inicio <= inicio and fin <= self.fin
 
 
def crear_bloque(dia, inicio, fin):
    """crea un bloque a partir de textos como ("lunes", "08:00", "10:00")
    y revisa que el dia y las horas tengan sentido."""
    if dia not in dias:
        raise error_validacion("dia invalido: '" + str(dia) + "'")
    minutos_inicio = hora_a_minutos(inicio)
    minutos_fin = hora_a_minutos(fin)
    if minutos_inicio >= minutos_fin:
        raise error_validacion("el bloque " + inicio + "-" + fin + " termina antes de empezar")
    return clase_bloque(dia, minutos_inicio, minutos_fin)
 
 
class clase_materia:
    """una materia. la dificultad va de 1 (facil) a 5 (muy dificil)
    y el nivel es el semestre en el que se ve."""
 
    def __init__(self, codigo, nombre, area, nivel, dificultad):
        if nombre.strip() == "" or area.strip() == "":
            raise error_validacion("la materia necesita nombre y area")
        if nivel < 1 or nivel > 12:
            raise error_validacion("el nivel debe estar entre 1 y 12")
        if dificultad < 1 or dificultad > 5:
            raise error_validacion("la dificultad debe estar entre 1 y 5")
        self.codigo = codigo
        self.nombre = nombre
        self.area = area
        self.nivel = nivel
        self.dificultad = dificultad
 
 
def validar_persona(nombre, semestre):
    """revisa lo que tienen en comun estudiantes y monitores."""
    if nombre.strip() == "":
        raise error_validacion("el nombre no puede estar vacio")
    if semestre < 1 or semestre > 12:
        raise error_validacion("el semestre debe estar entre 1 y 12")
 
 
class clase_estudiante:
    """un estudiante con su carrera y las horas en las que puede asistir."""
 
    def __init__(self, codigo, nombre, semestre, carrera, disponibilidad):
        validar_persona(nombre, semestre)
        self.codigo = codigo
        self.nombre = nombre
        self.semestre = semestre
        self.carrera = carrera
        self.disponibilidad = disponibilidad    # lista de bloques
 
    def __str__(self):
        return f"estudiante {self.codigo}: {self.nombre}, semestre {self.semestre}, {self.carrera}"
 
 
class clase_monitor:
    """un monitor con las materias que apoya (sus codigos) y sus horas libres."""
 
    def __init__(self, codigo, nombre, semestre, materias, disponibilidad):
        validar_persona(nombre, semestre)
        self.codigo = codigo
        self.nombre = nombre
        self.semestre = semestre
        self.materias = materias                # lista de codigos de materia
        self.disponibilidad = disponibilidad    # lista de bloques
 
    def __str__(self):
        return f"monitor {self.codigo}: {self.nombre}, semestre {self.semestre}"
 
 
class clase_profesor:
    """un profesor y las materias que dicta (solo se registra y se busca)."""
 
    def __init__(self, codigo, nombre, materias):
        self.codigo = codigo
        self.nombre = nombre
        self.materias = materias