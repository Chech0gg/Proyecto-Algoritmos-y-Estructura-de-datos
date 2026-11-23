materias_demo = [
    ("calculo i", "matematicas", 1, 4),
    ("programacion i", "sistemas", 1, 3),
    ("fisica i", "ciencias", 1, 3),
    ("etica", "humanidades", 1, 2),
    ("comunicacion oral", "humanidades", 1, 2),
    ("algebra lineal", "matematicas", 2, 3),
    ("calculo ii", "matematicas", 2, 4),
    ("matematicas discretas", "matematicas", 2, 3),
    ("programacion ii", "sistemas", 2, 3),
    ("redaccion academica", "humanidades", 2, 2),
    ("fisica ii", "ciencias", 3, 4),
    ("estructuras de datos", "sistemas", 3, 5),
    ("probabilidad", "matematicas", 3, 4),
    ("ecuaciones diferenciales", "matematicas", 4, 4),
    ("bases de datos", "sistemas", 4, 3),
    ("algoritmos", "sistemas", 4, 5),
    ("ingenieria de software", "sistemas", 5, 3),
    ("aprendizaje automatico", "sistemas", 6, 5),
]

requisitos_demo = [
    ("algebra lineal", "calculo i"),
    ("calculo ii", "calculo i"),
    ("matematicas discretas", "calculo i"),
    ("programacion ii", "programacion i"),
    ("redaccion academica", "comunicacion oral"),
    ("fisica ii", "fisica i"),
    ("fisica ii", "calculo ii"),
    ("estructuras de datos", "programacion ii"),
    ("probabilidad", "calculo ii"),
    ("ecuaciones diferenciales", "calculo ii"),
    ("ecuaciones diferenciales", "algebra lineal"),
    ("bases de datos", "estructuras de datos"),
    ("algoritmos", "estructuras de datos"),
    ("algoritmos", "matematicas discretas"),
    ("ingenieria de software", "bases de datos"),
    ("ingenieria de software", "algoritmos"),
    ("aprendizaje automatico", "algoritmos"),
    ("aprendizaje automatico", "algebra lineal"),
    ("aprendizaje automatico", "probabilidad"),
]


def clave_demo(nombre):
    return nombre + "12345"


def crear_estudiante(s, nombre, semestre, carrera, bloques):
    if s.cuentas.existe(nombre):
        return s.registrar_estudiante(nombre, semestre, carrera, bloques)
    return s.registrar_cuenta_estudiante(nombre, clave_demo(nombre), nombre, semestre, carrera, bloques)


def crear_monitor(s, nombre, semestre, materias, bloques):
    if s.cuentas.existe(nombre):
        return s.registrar_monitor(nombre, semestre, materias, bloques)
    return s.registrar_cuenta_monitor(nombre, clave_demo(nombre), nombre, semestre, materias, bloques)


def cargar_demo(s):
    codigo = {}
    if not s.cuentas.existe("admin"):
        s.registrar_cuenta_administrador("admin", clave_demo("admin"), "administrador")
    for nombre, area, nivel, dificultad in materias_demo:
        codigo[nombre] = s.registrar_materia(nombre, area, nivel, dificultad).codigo
    for materia, requisito in requisitos_demo:
        s.agregar_prerrequisito(codigo[materia], codigo[requisito])
    monitores = [
        ("carlos", 6, ["calculo i", "calculo ii", "algebra lineal"],
         [("lunes", "08:00", "12:00"), ("martes", "14:00", "18:00")]),
        ("diana", 7, ["estructuras de datos", "algoritmos", "programacion ii"],
         [("miercoles", "10:00", "14:00"), ("jueves", "08:00", "10:00"), ("jueves", "10:00", "12:00")]),
        ("hugo", 5, ["fisica i", "fisica ii"], [("lunes", "10:00", "12:00"), ("viernes", "08:00", "12:00")]),
        ("laura", 6, ["programacion i", "bases de datos"], [("martes", "08:00", "12:00")]),
    ]
    for nombre, semestre, materias, bloques in monitores:
        crear_monitor(s, nombre, semestre, [codigo[m] for m in materias], bloques)
    estudiantes = [
        ("ana", 2, [("lunes", "08:00", "10:00"), ("martes", "14:00", "16:00")], [], "calculo i", "par", 2.2),
        ("luis", 2, [("martes", "08:00", "12:00")], [], "programacion i", "puntual", 4.0),
        ("sara", 2, [("lunes", "10:00", "12:00")], [], "fisica i", "puntual", 2.8),
        ("eva", 4, [("miercoles", "10:00", "12:00")], ["programacion i", "programacion ii"],
         "estructuras de datos", "general", 3.1),
        ("beto", 3, [("lunes", "08:00", "09:00")], ["calculo i"], "calculo ii", "par", 2.6),
        ("mateo", 5, [("jueves", "08:00", "12:00")],
         ["programacion i", "programacion ii", "estructuras de datos", "calculo i", "matematicas discretas"],
         "algoritmos", "general", 3.4),
        ("nora", 4, [("jueves", "09:00", "11:00")],
         ["programacion i", "programacion ii", "estructuras de datos", "calculo i", "matematicas discretas"],
         "algoritmos", "general", 2.4),
    ]
    for nombre, semestre, bloques, cursadas, materia, tipo, nota in estudiantes:
        estudiante = crear_estudiante(s, nombre, semestre, "ing. de sistemas", bloques)
        for cursada in cursadas:
            s.registrar_cursada(estudiante.codigo, codigo[cursada])
        s.solicitar(estudiante.codigo, codigo[materia], tipo, nota)
    return codigo
