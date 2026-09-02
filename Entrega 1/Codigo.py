
"""
sistema de monitorias
"""

class Materia:

    # crea una materia
    def __init__(self, nombre, tasa_reprobacion_alta=False):
        self.nombre = nombre
        self.tasa_reprobacion_alta = tasa_reprobacion_alta

    # permite mostrar el nombre de la materia
    def __str__(self):
        return self.nombre


class Estudiante:

    # crea un estudiante con sus datos
    def __init__(self, nombre, semestre, horario_disponible="",
                 materias=None, promedio_en_materia=None):
        self.nombre = nombre
        self.semestre = semestre
        self.horario_disponible = horario_disponible

        # guarda las materias del estudiante
        self.materias = materias if materias is not None else []

        # guarda el promedio de la materia
        self.promedio_en_materia = promedio_en_materia

    def calcular_nivel_prioridad(self):

        # revisa si existe un promedio
        if self.promedio_en_materia is None:
            return "No definida"

        # promedio menor a 3 tiene prioridad alta
        if self.promedio_en_materia < 3.0:
            return "Alta"

        # promedio entre 3 y 4 tiene prioridad media
        elif self.promedio_en_materia < 4.0:
            return "Media"

        # promedio de 4 o mas tiene prioridad baja
        else:
            return "Baja"

    # muestra el nombre y semestre del estudiante
    def __str__(self):
        return f"{self.nombre} (semestre {self.semestre})"


class Monitor:

    # crea un monitor con sus datos
    def __init__(self, nombre, materia_especialidad, disponibilidad="",
                 calificacion=5.0):
        self.nombre = nombre
        self.materia_especialidad = materia_especialidad
        self.disponibilidad = disponibilidad
        self.calificacion = calificacion

    # muestra el nombre y especialidad del monitor
    def __str__(self):
        return f"{self.nombre} - especialista en {self.materia_especialidad}"


class Monitoria:

    # crea una monitoria con su tipo y duracion
    def __init__(self, tipo, duracion_minutos, descripcion):
        self.tipo = tipo
        self.duracion_minutos = duracion_minutos
        self.descripcion = descripcion

    # muestra la informacion de la monitoria
    def __str__(self):
        return f"{self.tipo} ({self.duracion_minutos} min) - {self.descripcion}"


# tipos de monitoria disponibles
class MonitoriaGeneral(Monitoria):

    def __init__(self):

        # define las caracteristicas de la monitoria general
        super().__init__(
            tipo="Monitoria General",
            duracion_minutos=90,
            descripcion="Temas recién vistos, para varios estudiantes a la vez"
        )


class MonitoriaPAR(Monitoria):

    def __init__(self):

        # define las caracteristicas de la monitoria par
        super().__init__(
            tipo="Monitoria PAR",
            duracion_minutos=120,
            descripcion="Mayor urgencia, para materias con alta reprobación"
        )


class MonitoriaExpress(Monitoria):

    def __init__(self):

        # define las caracteristicas de la monitoria express
        super().__init__(
            tipo="Monitoria Express",
            duracion_minutos=30,
            descripcion="Dudas rápidas y puntuales"
        )


class MonitoriaVirtual(Monitoria):

    def __init__(self):

        # define las caracteristicas de la monitoria virtual
        super().__init__(
            tipo="Monitoria Virtual",
            duracion_minutos=60,
            descripcion="Para casos especiales, se dicta en línea"
        )


class SolicitudMonitoria:

    # crea una solicitud con todos los datos necesarios
    def __init__(self, estudiante, materia, tema, nivel_conocimiento, monitoria):
        self.estudiante = estudiante
        self.materia = materia
        self.tema = tema
        self.nivel_conocimiento = nivel_conocimiento
        self.monitoria = monitoria

    def mostrar_resumen(self):

        # muestra los datos de la solicitud
        print("\n--- RESUMEN DE LA SOLICITUD DE MONITORIA ---")

        # muestra el estudiante
        print(f"Estudiante        : {self.estudiante}")

        # muestra la materia
        print(f"Materia           : {self.materia}")

        # muestra el tema que se le dificulta
        print(f"Tema puntual      : {self.tema}")

        # muestra el nivel de conocimiento
        print(f"Nivel conocimiento: {self.nivel_conocimiento}")

        # muestra el tipo de monitoria
        print(f"Tipo de monitoria : {self.monitoria}")

        # calcula y muestra la prioridad
        print(f"Nivel de prioridad: {self.estudiante.calcular_nivel_prioridad()}")

        print("---------------------------------------------\n")


def preguntar_datos_estudiante():

    # inicia el proceso de registro
    print(" solicitud de monitoria")

    # pide el nombre del estudiante
    nombre = input("Nombre del estudiante: ")

    # pide el semestre
    semestre = int(input("Semestre que cursa: "))

    # pide el horario disponible
    horario = input("Horario disponible (ej: Lunes 2-4pm): ")


    # pide el nombre de la materia
    nombre_materia = input("Materia en la que se le complica: ")

    # crea la materia
    materia = Materia(nombre_materia)


    # pide el tema que presenta dificultad
    tema = input("Tema puntual de la dificultad: ")

    # pide el nivel de conocimiento
    nivel_conocimiento = input(
        "Nivel de conocimiento en el tema (Bajo/Medio/Alto): "
    )


    # pide el promedio de la materia
    promedio = float(
        input("Promedio actual en la materia (0.0 a 5.0): ")
    )


    # crea el objeto estudiante
    estudiante = Estudiante(
        nombre=nombre,
        semestre=semestre,
        horario_disponible=horario,
        materias=[materia],
        promedio_en_materia=promedio
    )


    # muestra las opciones de monitoria
    print("\nTipos de monitoria disponibles:")
    print("1. General  (temas recientes, grupal, 1h30)")
    print("2. PAR      (dificultades anteriores/notas bajas, hasta 2h)")
    print("3. Express  (dudas puntuales, 30 min)")
    print("4. Virtual  (casos especiales, en línea)")

    # pide al usuario que elija una opcion
    opcion = input("Elige el número del tipo de monitoria: ")


    # relaciona cada numero con un tipo de monitoria
    tipos_disponibles = {
        "1": MonitoriaGeneral,
        "2": MonitoriaPAR,
        "3": MonitoriaExpress,
        "4": MonitoriaVirtual,
    }


    # busca el tipo de monitoria seleccionado
    clase_monitoria = tipos_disponibles.get(opcion, MonitoriaExpress)

    # crea la monitoria seleccionada
    monitoria = clase_monitoria()


    # crea la solicitud con los datos anteriores
    solicitud = SolicitudMonitoria(
        estudiante=estudiante,
        materia=materia,
        tema=tema,
        nivel_conocimiento=nivel_conocimiento,
        monitoria=monitoria
    )


    # devuelve la solicitud creada
    return solicitud


# verifica que el programa se este ejecutando directamente
if __name__ == "__main__":

    # pide los datos y crea la solicitud
    solicitud = preguntar_datos_estudiante()

    # muestra el resumen final
    solicitud.mostrar_resumen()