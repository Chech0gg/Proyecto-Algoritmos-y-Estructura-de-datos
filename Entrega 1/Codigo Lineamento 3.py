"""
 SISTEMA DE MONITORIAS - CODIGO BASE
"""

class Materia:

    def __init__(self, nombre, tasa_reprobacion_alta=False):
        self.nombre = nombre
        self.tasa_reprobacion_alta = tasa_reprobacion_alta

    def __str__(self):
        return self.nombre


class Estudiante:

    def __init__(self, nombre, semestre, horario_disponible="",
                 materias=None, promedio_en_materia=None):
        self.nombre = nombre
        self.semestre = semestre
        self.horario_disponible = horario_disponible
        # Si no se manda una lista de materias, se crea una vacía
        self.materias = materias if materias is not None else []
        self.promedio_en_materia = promedio_en_materia

    def calcular_nivel_prioridad(self):

        # Si el estudiante no dio promedio, no se puede calcular
        if self.promedio_en_materia is None:
            return "No definida"

        if self.promedio_en_materia < 3.0:
            return "Alta"
        elif self.promedio_en_materia < 4.0:
            return "Media"
        else:
            return "Baja"

    def __str__(self):
        return f"{self.nombre} (semestre {self.semestre})"

class Monitor:
 
    def __init__(self, nombre, materia_especialidad, disponibilidad="",
                 calificacion=5.0):
        self.nombre = nombre
        self.materia_especialidad = materia_especialidad
        self.disponibilidad = disponibilidad
        self.calificacion = calificacion

    def __str__(self):
        return f"{self.nombre} - especialista en {self.materia_especialidad}"


class Monitoria:

    def __init__(self, tipo, duracion_minutos, descripcion):
        self.tipo = tipo
        self.duracion_minutos = duracion_minutos
        self.descripcion = descripcion

    def __str__(self):
        return f"{self.tipo} ({self.duracion_minutos} min) - {self.descripcion}"


class MonitoriaGeneral(Monitoria):
   
    def __init__(self):
        super().__init__(
            tipo="Monitoria General",
            duracion_minutos=90,  # 1h 30m
            descripcion="Temas recién vistos, para varios estudiantes a la vez"
        )


class MonitoriaPAR(Monitoria):
    
    def __init__(self):
        super().__init__(
            tipo="Monitoria PAR",
            duracion_minutos=120,  # hasta 2h
            descripcion="Mayor urgencia, para materias con alta reprobación"
        )


class MonitoriaExpress(Monitoria):
   
    def __init__(self):
        super().__init__(
            tipo="Monitoria Express",
            duracion_minutos=30,
            descripcion="Dudas rápidas y puntuales"
        )


class MonitoriaVirtual(Monitoria):
   
    def __init__(self):
        super().__init__(
            tipo="Monitoria Virtual",
            duracion_minutos=60,
            descripcion="Para casos especiales, se dicta en línea"
        )


class SolicitudMonitoria:

    def __init__(self, estudiante, materia, tema, nivel_conocimiento, monitoria):
        self.estudiante = estudiante
        self.materia = materia
        self.tema = tema
        self.nivel_conocimiento = nivel_conocimiento
        self.monitoria = monitoria

    def mostrar_resumen(self):
        """Imprime en pantalla un resumen legible de la solicitud."""
        print("\n--- RESUMEN DE LA SOLICITUD DE MONITORIA ---")
        print(f"Estudiante        : {self.estudiante}")
        print(f"Materia           : {self.materia}")
        print(f"Tema puntual      : {self.tema}")
        print(f"Nivel conocimiento: {self.nivel_conocimiento}")
        print(f"Tipo de monitoria : {self.monitoria}")
        print(f"Nivel de prioridad: {self.estudiante.calcular_nivel_prioridad()}")
        print("---------------------------------------------\n")


# ------------------------------------------------------------------
def preguntar_datos_estudiante():

    print(" solicitud de monitoria")

    nombre = input("Nombre del estudiante: ")
    semestre = int(input("Semestre que cursa: "))
    horario = input("Horario disponible (ej: Lunes 2-4pm): ")

    # --- Datos de la materia ---
    nombre_materia = input("Materia en la que se le complica: ")
    materia = Materia(nombre_materia)

    tema = input("Tema puntual de la dificultad: ")
    nivel_conocimiento = input(
        "Nivel de conocimiento en el tema (Bajo/Medio/Alto): "
    )

    promedio = float(
        input("Promedio actual en la materia (0.0 a 5.0): ")
    )


    estudiante = Estudiante(
        nombre=nombre,
        semestre=semestre,
        horario_disponible=horario,
        materias=[materia],
        promedio_en_materia=promedio
    )

    print("\nTipos de monitoria disponibles:")
    print("1. General  (temas recientes, grupal, 1h30)")
    print("2. PAR      (dificultades anteriores/notas bajas, hasta 2h)")
    print("3. Express  (dudas puntuales, 30 min)")
    print("4. Virtual  (casos especiales, en línea)")
    opcion = input("Elige el número del tipo de monitoria: ")

    tipos_disponibles = {
        "1": MonitoriaGeneral,
        "2": MonitoriaPAR,
        "3": MonitoriaExpress,
        "4": MonitoriaVirtual,
    }
 
    clase_monitoria = tipos_disponibles.get(opcion, MonitoriaExpress)
    monitoria = clase_monitoria()


    solicitud = SolicitudMonitoria(
        estudiante=estudiante,
        materia=materia,
        tema=tema,
        nivel_conocimiento=nivel_conocimiento,
        monitoria=monitoria
    )

    return solicitud

if __name__ == "__main__":

    solicitud = preguntar_datos_estudiante()

    solicitud.mostrar_resumen()