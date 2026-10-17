
"""
sistema de monitorias
"""
 
import unicodedata
from datetime import date, datetime
 
 
class Materia:
 
    # crea una materia con sus prerrequisitos (otras materias)
    def __init__(self, nombre, tasa_reprobacion_alta=False, prerrequisitos=None):
        self.nombre = nombre
        self.tasa_reprobacion_alta = tasa_reprobacion_alta
 
        # guarda las materias que se deben ver antes
        self.prerrequisitos = prerrequisitos if prerrequisitos is not None else []
 
    # permite mostrar el nombre de la materia
    def __str__(self):
        return self.nombre
 
 
def nivel_prioridad(promedio):
 
    # revisa si existe un promedio
    if promedio is None:
        return "No definida"
 
    # promedio menor a 3 tiene prioridad alta
    if promedio < 3.0:
        return "Alta"
 
    # promedio entre 3 y 4 tiene prioridad media
    elif promedio < 4.0:
        return "Media"
 
    # promedio de 4 o mas tiene prioridad baja
    else:
        return "Baja"
 
 
class Estudiante:
 
    # crea un estudiante con sus datos
    def __init__(self, nombre, semestre, horario_disponible="",
                 materias=None, promedio_en_materia=None,
                 minutos_disponibles=0):
        self.nombre = nombre
        self.semestre = semestre
        self.horario_disponible = horario_disponible
 
        # guarda las materias del estudiante
        self.materias = materias if materias is not None else []
 
        # guarda el promedio de la materia
        self.promedio_en_materia = promedio_en_materia
 
        # guarda el tiempo total que tiene libre para monitorias
        self.minutos_disponibles = minutos_disponibles
 
    def calcular_nivel_prioridad(self):
 
        # usa la misma regla de prioridad para cualquier promedio
        return nivel_prioridad(self.promedio_en_materia)
 
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
 
    # cuenta cuantas solicitudes se han creado (sirve para numerarlas)
    contador = 0
 
    # crea una solicitud con todos los datos necesarios
    def __init__(self, estudiante, materia, tema, nivel_conocimiento, monitoria,
                 fecha=None):
        self.estudiante = estudiante
        self.materia = materia
        self.tema = tema
        self.nivel_conocimiento = nivel_conocimiento
        self.monitoria = monitoria
 
        # fecha en que se hizo la solicitud (hoy si no se indica)
        self.fecha = fecha if fecha is not None else date.today()
 
        # numero consecutivo, tambien sirve para desempatar al ordenar
        SolicitudMonitoria.contador += 1
        self.numero = SolicitudMonitoria.contador
 
        # monitor asignado (None mientras no tenga uno)
        self.monitor = None
 
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
 
        # muestra la fecha de la solicitud
        print(f"Fecha solicitud   : {self.fecha.strftime('%d/%m/%Y')}")
 
        # calcula y muestra la prioridad
        print(f"Nivel de prioridad: {self.estudiante.calcular_nivel_prioridad()}")
 
        print("---------------------------------------------\n")
 
 
# ---------------------------------------------------------------
# BACKTRACKING: COMBINAR MONITORIAS EN EL TIEMPO DISPONIBLE
# ---------------------------------------------------------------
 
def total_minutos(combinacion):
 
    # suma la duracion de todos los elementos de la combinacion
    return sum(m.duracion_minutos for m in combinacion)
 
 
def combinar_monitorias(opciones, minutos_disponibles):
 
    # "opciones" puede ser cualquier lista de objetos con duracion_minutos
    # (monitorias sueltas o sesiones sugeridas)
 
    # aqui se guardan todas las combinaciones validas que se encuentren
    resultados = []
 
    def explorar(inicio, restante, actual):
 
        # si ya hay al menos una opcion elegida, la combinacion es valida
        if actual:
            resultados.append(list(actual))
 
        # prueba cada opcion desde la posicion "inicio"
        # (usar i + 1 evita repetir la misma opcion o el mismo grupo en otro orden)
        for i in range(inicio, len(opciones)):
            opcion = opciones[i]
 
            # poda: si no cabe en el tiempo que queda, no se explora
            if opcion.duracion_minutos > restante:
                continue
 
            # 1. elegir
            actual.append(opcion)
 
            # 2. explorar (llamada recursiva con menos tiempo disponible)
            explorar(i + 1, restante - opcion.duracion_minutos, actual)
 
            # 3. deshacer para probar la siguiente opcion
            actual.pop()
 
    # arranca con la lista vacia y todo el tiempo disponible
    explorar(0, minutos_disponibles, [])
    return resultados
 
 
def mejor_combinacion(combinaciones):
 
    # si no hay ninguna combinacion posible, no hay mejor
    if not combinaciones:
        return None
 
    # primero cuenta cuantas sesiones de prioridad alta incluye,
    # luego el tiempo aprovechado y en empate, la de menos elementos
    return max(
        combinaciones,
        key=lambda c: (
            sum(1 for s in c if getattr(s, "prioridad", None) == "Alta"),
            total_minutos(c),
            -len(c),
        ),
    )
 
 
def mostrar_plan_sugerido(estudiante):
 
    # crea una monitoria de cada tipo para poder combinarlas
    tipos = [
        MonitoriaGeneral(),
        MonitoriaPAR(),
        MonitoriaExpress(),
        MonitoriaVirtual(),
    ]
 
    # busca todas las combinaciones que caben en el tiempo del estudiante
    combinaciones = combinar_monitorias(tipos, estudiante.minutos_disponibles)
 
    print(f"--- PLAN SUGERIDO ({estudiante.minutos_disponibles} min disponibles) ---")
 
    # si ni la monitoria mas corta cabe, se avisa
    if not combinaciones:
        print("Ninguna monitoria cabe en el tiempo disponible.\n")
        return
 
    print(f"Combinaciones posibles: {len(combinaciones)}")
 
    # muestra la mejor combinacion
    mejor = mejor_combinacion(combinaciones)
    print(f"Mejor plan ({total_minutos(mejor)} min):")
    for monitoria in mejor:
        print(f"  - {monitoria}")
    print()
 
 
# ---------------------------------------------------------------
# RECURSION Y BACKTRACKING: CADENAS DE PRERREQUISITOS
# ---------------------------------------------------------------
 
def normalizar(texto):
 
    # pasa a minusculas y quita tildes para comparar nombres
    sin_tildes = unicodedata.normalize("NFD", texto.strip().lower())
    return "".join(c for c in sin_tildes if unicodedata.category(c) != "Mn")
 
 
def mostrar_arbol(materia, nivel=0):
 
    # imprime la materia con sangria segun su profundidad
    prefijo = "    " * nivel + ("└─ " if nivel > 0 else "")
    print(prefijo + str(materia))
 
    # caso recursivo: baja un nivel por cada prerrequisito
    # caso base: si no tiene prerrequisitos, el for no hace nada y regresa
    for prerrequisito in materia.prerrequisitos:
        mostrar_arbol(prerrequisito, nivel + 1)
 
 
def listar_prerrequisitos(materia, resultado=None):
 
    # (se asume que no hay ciclos; se revisan antes con tiene_ciclo)
    if resultado is None:
        resultado = []
 
    for prerrequisito in materia.prerrequisitos:
 
        # primero se agregan los prerrequisitos del prerrequisito
        listar_prerrequisitos(prerrequisito, resultado)
 
        # luego el prerrequisito, sin repetirlo si ya estaba
        if prerrequisito not in resultado:
            resultado.append(prerrequisito)
 
    # queda en orden: primero las bases y al final las mas cercanas a la materia
    return resultado
 
 
def tiene_ciclo(materia, en_camino=None):
 
    # "en_camino" guarda las materias del recorrido actual
    if en_camino is None:
        en_camino = set()
 
    # si ya estaba en el camino, hay un ciclo (A pide B y B pide A)
    if materia in en_camino:
        return True
 
    # 1. elegir
    en_camino.add(materia)
 
    # 2. explorar cada prerrequisito
    for prerrequisito in materia.prerrequisitos:
        if tiene_ciclo(prerrequisito, en_camino):
            return True
 
    # 3. deshacer para que otra rama pueda volver a pasar por esta materia
    en_camino.remove(materia)
    return False
 
 
def todas_las_rutas(materia):
 
    # aqui se guardan las cadenas completas, desde la materia hasta una base
    rutas = []
 
    def explorar(actual, ruta):
 
        # 1. elegir
        ruta.append(actual)
 
        # caso base: materia sin prerrequisitos, la ruta esta completa
        if not actual.prerrequisitos:
            rutas.append(list(ruta))
 
        # 2. explorar cada prerrequisito
        else:
            for prerrequisito in actual.prerrequisitos:
                explorar(prerrequisito, ruta)
 
        # 3. deshacer para probar el siguiente prerrequisito
        ruta.pop()
 
    explorar(materia, [])
    return rutas
 
 
class SesionSugerida:
 
    # une una materia debil con la monitoria que se le recomienda
    def __init__(self, materia, monitoria, prioridad):
        self.materia = materia
        self.monitoria = monitoria
        self.prioridad = prioridad
 
        # permite combinarla con combinar_monitorias
        self.duracion_minutos = monitoria.duracion_minutos
 
    # muestra la sesion sugerida
    def __str__(self):
        return (f"{self.monitoria.tipo} de {self.materia} "
                f"({self.duracion_minutos} min) - prioridad {self.prioridad}")
 
 
def sugerir_sesiones(prerrequisitos, promedios):
 
    sesiones = []
 
    for materia in prerrequisitos:
 
        # calcula la prioridad con el promedio que tuvo en esa materia
        prioridad = nivel_prioridad(promedios[materia])
 
        # promedio bajo: monitoria PAR
        if prioridad == "Alta":
            sesiones.append(SesionSugerida(materia, MonitoriaPAR(), prioridad))
 
        # promedio medio: monitoria general de repaso
        elif prioridad == "Media":
            sesiones.append(SesionSugerida(materia, MonitoriaGeneral(), prioridad))
 
    return sesiones
 
 
def mostrar_plan_prerrequisitos(estudiante, sesiones):
 
    print(f"\n--- MONITORIAS SUGERIDAS ({estudiante.minutos_disponibles} min disponibles) ---")
 
    # si ningun prerrequisito esta debil, no hay nada que sugerir
    if not sesiones:
        print("Ningún prerrequisito está débil, no hace falta monitoria.\n")
        return
 
    print("Prerrequisitos débiles:")
    for sesion in sesiones:
        print(f"  - {sesion}")
 
    # busca con backtracking las combinaciones que caben en el tiempo
    combinaciones = combinar_monitorias(sesiones, estudiante.minutos_disponibles)
 
    if not combinaciones:
        print("\nNinguna sesión cabe en el tiempo disponible.\n")
        return
 
    mejor = mejor_combinacion(combinaciones)
    print(f"\nCombinaciones posibles: {len(combinaciones)}")
    print(f"Plan recomendado ({total_minutos(mejor)} min):")
    for sesion in mejor:
        print(f"  - {sesion}")
 
    # avisa lo que no alcanzo a entrar
    sin_cubrir = [s for s in sesiones if s not in mejor]
    if sin_cubrir:
        print("Quedan para otra semana:")
        for sesion in sin_cubrir:
            print(f"  - {sesion}")
    print()
 
 
def pedir_entero(mensaje):
 
    # repite la pregunta hasta que escriba un entero valido
    while True:
        try:
            valor = int(input(mensaje))
            if valor >= 0:
                return valor
        except ValueError:
            pass
        print("  Escribe un número entero válido")
 
 
def pedir_promedio(materia):
 
    # repite la pregunta hasta que escriba un promedio valido o deje vacio
    while True:
        texto = input(
            f"Promedio en {materia} (0.0 a 5.0, Enter si aún no la cursa): "
        ).strip()
 
        # vacio significa que todavia no la ha cursado
        if texto == "":
            return None
 
        try:
            promedio = float(texto.replace(",", "."))
        except ValueError:
            print("  Escribe un número, por ejemplo 3.5")
            continue
 
        if 0.0 <= promedio <= 5.0:
            return promedio
        print("  El promedio debe estar entre 0.0 y 5.0")
 
 
def registrar_materias():
 
    # guarda las materias por nombre normalizado para no duplicarlas
    catalogo = {}
 
    def obtener(nombre):
        clave = normalizar(nombre)
        if clave not in catalogo:
            catalogo[clave] = Materia(nombre.strip())
        return catalogo[clave]
 
    print("\nRegistro de materias")
    print("Escribe una materia por línea con este formato:")
    print("  Materia: prerrequisito1, prerrequisito2")
    print("Si no tiene prerrequisitos, escribe solo el nombre.")
    print("Deja la línea vacía para terminar.")
 
    while True:
        linea = input("> ").strip()
        if linea == "":
            break
 
        # separa el nombre de la materia y la lista de prerrequisitos
        nombre, _, resto = linea.partition(":")
        if nombre.strip() == "":
            continue
 
        materia = obtener(nombre)
        materia.prerrequisitos = [
            obtener(p) for p in resto.split(",") if p.strip() != ""
        ]
 
    return catalogo
 
 
def consultar_prerrequisitos():
 
    # el usuario escribe las materias
    catalogo = registrar_materias()
    if not catalogo:
        print("No registraste ninguna materia.")
        return
 
    # revisa que ninguna cadena sea circular
    for materia in catalogo.values():
        if tiene_ciclo(materia):
            print(f"\nError: {materia} está en un ciclo de prerrequisitos. "
                  "Revisa los datos.")
            return
 
    # pide la materia que quiere cursar
    objetivo = None
    while objetivo is None:
        nombre = input("\n¿Qué materia quiere cursar? ")
        objetivo = catalogo.get(normalizar(nombre))
        if objetivo is None:
            print("  Esa materia no está registrada. Materias: "
                  + ", ".join(str(m) for m in catalogo.values()))
 
    # muestra el arbol de prerrequisitos
    print(f"\n--- ÁRBOL DE PRERREQUISITOS DE {objetivo} ---")
    mostrar_arbol(objetivo)
 
    # lista todos los prerrequisitos sin repetir
    prerrequisitos = listar_prerrequisitos(objetivo)
    if not prerrequisitos:
        print(f"\n{objetivo} no tiene prerrequisitos.\n")
        return
 
    print("\n--- ORDEN EN QUE DEBE VERLAS ---")
    for i, materia in enumerate(prerrequisitos, start=1):
        print(f"{i}. {materia}")
 
    # muestra cada cadena completa
    print("\n--- CADENAS COMPLETAS ---")
    for i, ruta in enumerate(todas_las_rutas(objetivo), start=1):
        print(f"Cadena {i}: " + " -> ".join(str(m) for m in reversed(ruta)))
 
    # pide los datos del estudiante
    print("\n--- DATOS DEL ESTUDIANTE ---")
    nombre_estudiante = input("Nombre del estudiante: ")
    semestre = pedir_entero("Semestre que cursa: ")
    minutos = pedir_entero("Minutos totales disponibles para monitorias (ej: 180): ")
    estudiante = Estudiante(nombre_estudiante, semestre, minutos_disponibles=minutos)
 
    # pide el promedio en cada prerrequisito
    print("\nPromedio en cada prerrequisito:")
    promedios = {}
    for materia in prerrequisitos:
        promedios[materia] = pedir_promedio(materia)
 
    # avisa las que todavia no ha cursado
    pendientes = [m for m in prerrequisitos if promedios[m] is None]
    if pendientes:
        print("\nAún no cursadas (debe verlas primero): "
              + ", ".join(str(m) for m in pendientes))
 
    # sugiere monitorias para los prerrequisitos debiles
    sesiones = sugerir_sesiones(prerrequisitos, promedios)
    mostrar_plan_prerrequisitos(estudiante, sesiones)
 
 
# ---------------------------------------------------------------
# ORDENAMIENTO: LISTADOS POR URGENCIA, ANTIGUEDAD O MATERIA
# ---------------------------------------------------------------
 
def rango_urgencia(solicitud):
 
    # convierte la prioridad en un numero: menor numero = mas urgente
    rangos = {"Alta": 0, "Media": 1, "Baja": 2, "No definida": 3}
    return rangos[solicitud.estudiante.calcular_nivel_prioridad()]
 
 
def clave_urgencia(solicitud):
 
    # sin promedio se manda al final (6.0 es mayor que cualquier promedio)
    promedio = solicitud.estudiante.promedio_en_materia
    if promedio is None:
        promedio = 6.0
 
    # primero la prioridad, luego el promedio mas bajo, luego la mas antigua
    return (rango_urgencia(solicitud), promedio, solicitud.fecha, solicitud.numero)
 
 
def clave_antiguedad(solicitud):
 
    # la fecha mas antigua primero; en empate, la mas urgente
    return (solicitud.fecha, rango_urgencia(solicitud), solicitud.numero)
 
 
def clave_materia(solicitud):
 
    # orden alfabetico sin tildes ni mayusculas; en empate, la mas urgente
    return (normalizar(solicitud.materia.nombre), rango_urgencia(solicitud),
            solicitud.fecha, solicitud.numero)
 
 
# cada algoritmo recibe la lista y una funcion "clave" que dice por que ordenar,
# y devuelve la lista ordenada (sin tocar la original) y cuantas comparaciones hizo
 
def ordenar_burbuja(lista, clave):
 
    datos = list(lista)
    comparaciones = 0
    n = len(datos)
 
    for i in range(n - 1):
        hubo_cambio = False
 
        # compara vecinos; el mayor "sube" hasta el final
        for j in range(n - 1 - i):
            comparaciones += 1
            if clave(datos[j]) > clave(datos[j + 1]):
                datos[j], datos[j + 1] = datos[j + 1], datos[j]
                hubo_cambio = True
 
        # si en una pasada no hubo cambios, ya esta ordenada
        if not hubo_cambio:
            break
 
    return datos, comparaciones
 
 
def ordenar_seleccion(lista, clave):
 
    datos = list(lista)
    comparaciones = 0
    n = len(datos)
 
    for i in range(n - 1):
 
        # busca el menor de la parte que falta por ordenar
        menor = i
        for j in range(i + 1, n):
            comparaciones += 1
            if clave(datos[j]) < clave(datos[menor]):
                menor = j
 
        # lo pone en la posicion i
        datos[i], datos[menor] = datos[menor], datos[i]
 
    return datos, comparaciones
 
 
def ordenar_insercion(lista, clave):
 
    datos = list(lista)
    comparaciones = 0
 
    for i in range(1, len(datos)):
 
        # toma el elemento y lo inserta en su lugar dentro de la parte ya ordenada
        actual = datos[i]
        j = i - 1
        while j >= 0:
            comparaciones += 1
            if clave(datos[j]) > clave(actual):
                datos[j + 1] = datos[j]
                j -= 1
            else:
                break
        datos[j + 1] = actual
 
    return datos, comparaciones
 
 
def ordenar_mezcla(lista, clave):
 
    # merge sort: divide la lista, ordena cada mitad y las mezcla
    comparaciones = 0
 
    def mezclar(izquierda, derecha):
        nonlocal comparaciones
        resultado = []
        i = 0
        j = 0
 
        # va tomando el menor de los dos primeros elementos
        while i < len(izquierda) and j < len(derecha):
            comparaciones += 1
            if clave(izquierda[i]) <= clave(derecha[j]):
                resultado.append(izquierda[i])
                i += 1
            else:
                resultado.append(derecha[j])
                j += 1
 
        # agrega lo que sobre de cualquiera de las dos mitades
        resultado.extend(izquierda[i:])
        resultado.extend(derecha[j:])
        return resultado
 
    def dividir(datos):
 
        # caso base: una lista de 0 o 1 elementos ya esta ordenada
        if len(datos) <= 1:
            return datos
 
        # caso recursivo: ordena cada mitad y las mezcla
        medio = len(datos) // 2
        return mezclar(dividir(datos[:medio]), dividir(datos[medio:]))
 
    return dividir(list(lista)), comparaciones
 
 
def ordenar_rapido(lista, clave):
 
    # quick sort: elige un pivote y separa menores y mayores
    comparaciones = 0
 
    def ordenar(datos):
        nonlocal comparaciones
 
        # caso base: una lista de 0 o 1 elementos ya esta ordenada
        if len(datos) <= 1:
            return datos
 
        # el pivote es el elemento del medio
        medio = len(datos) // 2
        pivote = datos[medio]
        resto = datos[:medio] + datos[medio + 1:]
 
        # reparte el resto segun sea menor o no que el pivote
        menores = []
        mayores = []
        for elemento in resto:
            comparaciones += 1
            if clave(elemento) < clave(pivote):
                menores.append(elemento)
            else:
                mayores.append(elemento)
 
        # caso recursivo: ordena cada lado y pone el pivote en medio
        return ordenar(menores) + [pivote] + ordenar(mayores)
 
    return ordenar(list(lista)), comparaciones
 
 
# criterios y algoritmos disponibles en el menu
CRITERIOS = {
    "1": ("Urgencia", clave_urgencia, "más urgente primero"),
    "2": ("Antigüedad", clave_antiguedad, "más antigua primero"),
    "3": ("Materia", clave_materia, "orden alfabético"),
}
 
ALGORITMOS = {
    "1": ("Burbuja", ordenar_burbuja, "básico"),
    "2": ("Selección", ordenar_seleccion, "básico"),
    "3": ("Inserción", ordenar_insercion, "básico"),
    "4": ("Mezcla (merge sort)", ordenar_mezcla, "avanzado"),
    "5": ("Rápido (quick sort)", ordenar_rapido, "avanzado"),
}
 
 
def pedir_opcion(mensaje, opciones):
 
    # repite la pregunta hasta que elija una opcion que exista
    while True:
        opcion = input(mensaje).strip()
        if opcion in opciones:
            return opcion
        print("  Opción no válida")
 
 
def pedir_fecha(mensaje):
 
    # repite la pregunta hasta que escriba una fecha valida (vacio = hoy)
    while True:
        texto = input(mensaje).strip()
        if texto == "":
            return date.today()
        try:
            return datetime.strptime(texto, "%d/%m/%Y").date()
        except ValueError:
            print("  Escribe la fecha como dd/mm/aaaa, por ejemplo 15/10/2026")
 
 
def mostrar_listado(solicitudes):
 
    # encabezado de la tabla
    print(f"{'N°':>3}  {'Fecha':<10}  {'Estudiante':<16}  {'Materia':<28}  "
          f"{'Prioridad':<9}  {'Prom.':<5}  Monitoria")
 
    # una linea por solicitud
    for s in solicitudes:
        promedio = s.estudiante.promedio_en_materia
        texto_promedio = "-" if promedio is None else f"{promedio:.1f}"
        print(f"{s.numero:>3}  {s.fecha.strftime('%d/%m/%Y'):<10}  "
              f"{s.estudiante.nombre:<16}  {str(s.materia):<28}  "
              f"{s.estudiante.calcular_nivel_prioridad():<9}  "
              f"{texto_promedio:<5}  {s.monitoria.tipo}")
    print()
 
 
def comparar_algoritmos(solicitudes, clave):
 
    print(f"\n{'Algoritmo':<24}{'Tipo':<10}Comparaciones")
 
    orden_referencia = None
    todos_iguales = True
 
    for nombre, funcion, tipo in ALGORITMOS.values():
        ordenada, comparaciones = funcion(solicitudes, clave)
        print(f"{nombre:<24}{tipo:<10}{comparaciones}")
 
        # revisa que todos dejen la lista en el mismo orden
        orden = [s.numero for s in ordenada]
        if orden_referencia is None:
            orden_referencia = orden
        elif orden != orden_referencia:
            todos_iguales = False
 
    if todos_iguales:
        print(f"\nCon {len(solicitudes)} solicitudes, todos dejan la lista en el mismo orden.\n")
    else:
        print("\nAviso: los algoritmos dejaron la lista en órdenes distintos.\n")
 
 
def listar_solicitudes(solicitudes):
 
    # si no hay solicitudes, no hay nada que ordenar
    if not solicitudes:
        print("\nNo hay solicitudes registradas. Registra una o carga las de ejemplo.")
        return
 
    # elige el criterio
    print("\nOrdenar por:")
    for numero, (nombre, _, descripcion) in CRITERIOS.items():
        print(f"{numero}. {nombre} ({descripcion})")
    opcion = pedir_opcion("Elige el criterio: ", CRITERIOS)
    nombre_criterio, clave, descripcion = CRITERIOS[opcion]
 
    # elige el algoritmo
    print("\nAlgoritmo de ordenamiento:")
    for numero, (nombre, _, tipo) in ALGORITMOS.items():
        print(f"{numero}. {nombre} ({tipo})")
    print("6. Comparar todos (cuántas comparaciones hace cada uno)")
    opcion = pedir_opcion("Elige el algoritmo: ", list(ALGORITMOS) + ["6"])
 
    # opcion 6: compara todos los algoritmos y termina
    if opcion == "6":
        comparar_algoritmos(solicitudes, clave)
        return
 
    nombre_algoritmo, funcion, _ = ALGORITMOS[opcion]
    invertir = input("¿Invertir el orden? (s/n): ").strip().lower() == "s"
 
    # ordena y, si se pidio, invierte el resultado
    ordenadas, comparaciones = funcion(solicitudes, clave)
    if invertir:
        ordenadas = ordenadas[::-1]
        descripcion = "orden invertido"
 
    print(f"\n--- SOLICITUDES POR {nombre_criterio.upper()} ({descripcion}) ---")
    print(f"Algoritmo: {nombre_algoritmo} | Comparaciones: {comparaciones}\n")
    mostrar_listado(ordenadas)
 
 
def crear_solicitudes_ejemplo():
 
    # nombre, semestre, materia, tema, nivel, promedio, tipo de monitoria, fecha
    datos = [
        ("Ana Torres", 3, "Cálculo 1", "Límites", "Bajo", 2.4, MonitoriaPAR, date(2026, 10, 2)),
        ("Carlos Ruiz", 2, "Física 1", "Cinemática", "Medio", 3.6, MonitoriaGeneral, date(2026, 9, 28)),
        ("Laura Gómez", 4, "Álgebra lineal", "Espacios vectoriales", "Bajo", 2.8, MonitoriaPAR, date(2026, 10, 10)),
        ("Diego Pardo", 1, "Introducción a programación", "Ciclos", "Medio", 4.2, MonitoriaExpress, date(2026, 10, 5)),
        ("Sofía Castro", 5, "Lógica y teoría de conjuntos", "Demostraciones", "Medio", 3.1, MonitoriaGeneral, date(2026, 9, 20)),
        ("Andrés Mejía", 3, "Cálculo 1", "Derivadas", "Alto", 4.5, MonitoriaVirtual, date(2026, 10, 14)),
        ("Valentina Rojas", 4, "Probabilidad 1", "Variables aleatorias", "Bajo", 2.9, MonitoriaPAR, date(2026, 9, 25)),
        ("Mateo Vargas", 2, "Física 1", "Leyes de Newton", "Bajo", 3.9, MonitoriaGeneral, date(2026, 10, 12)),
    ]
 
    solicitudes = []
    for nombre, semestre, nombre_materia, tema, nivel, promedio, clase, fecha in datos:
        materia = Materia(nombre_materia)
        estudiante = Estudiante(nombre, semestre, materias=[materia],
                                promedio_en_materia=promedio)
        solicitudes.append(
            SolicitudMonitoria(estudiante, materia, tema, nivel, clase(), fecha)
        )
    return solicitudes
 
 
# ---------------------------------------------------------------
# PILA: DESHACER LA ULTIMA ASIGNACION DE MONITOR
# ---------------------------------------------------------------
 
class Pila:
 
    # crea una pila vacia
    def __init__(self):
        self.elementos = []
 
    # agrega un elemento en el tope
    def apilar(self, elemento):
        self.elementos.append(elemento)
 
    # quita y devuelve el elemento del tope (el ultimo que entro)
    def desapilar(self):
        if self.esta_vacia():
            return None
        return self.elementos.pop()
 
    # devuelve el elemento del tope sin quitarlo
    def ver_tope(self):
        if self.esta_vacia():
            return None
        return self.elementos[-1]
 
    # dice si no hay ningun elemento
    def esta_vacia(self):
        return len(self.elementos) == 0
 
    # devuelve una copia de la pila, del tope hacia la base
    def desde_el_tope(self):
        return self.elementos[::-1]
 
    # permite usar len(pila)
    def __len__(self):
        return len(self.elementos)
 
 
class Asignacion:
 
    # guarda que monitor se le asigno a que solicitud
    def __init__(self, solicitud, monitor):
        self.solicitud = solicitud
        self.monitor = monitor
 
    # muestra la asignacion
    def __str__(self):
        return (f"Solicitud {self.solicitud.numero} "
                f"({self.solicitud.estudiante.nombre}, {self.solicitud.materia})"
                f" -> {self.monitor.nombre}")
 
 
def monitores_compatibles(solicitud, monitores):
 
    # solo sirven los monitores cuya especialidad es la materia de la solicitud
    materia = normalizar(solicitud.materia.nombre)
    return [m for m in monitores
            if normalizar(m.materia_especialidad) == materia]
 
 
def clave_monitor(monitor):
 
    # mejor calificacion primero (por eso va negativa), luego orden alfabetico
    return (-monitor.calificacion, normalizar(monitor.nombre))
 
 
def asignar_monitor(solicitud, monitor, historial):
 
    # asigna el monitor a la solicitud
    solicitud.monitor = monitor
 
    # guarda la asignacion en la pila para poder deshacerla
    historial.apilar(Asignacion(solicitud, monitor))
 
 
def deshacer_ultima_asignacion(historial):
 
    # saca de la pila la ultima asignacion que se hizo
    asignacion = historial.desapilar()
 
    # si la pila estaba vacia, no hay nada que deshacer
    if asignacion is None:
        return None
 
    # revierte la asignacion: la solicitud vuelve a quedar sin monitor
    asignacion.solicitud.monitor = None
    return asignacion
 
 
def mostrar_asignaciones(historial, solicitudes):
 
    print(f"\n--- ASIGNACIONES ({len(historial)}) ---")
 
    if historial.esta_vacia():
        print("Todavía no hay asignaciones.")
    else:
        print("De la más reciente (tope de la pila) a la más antigua:")
        for i, asignacion in enumerate(historial.desde_el_tope(), start=1):
            print(f"{i}. {asignacion}")
 
    # cuenta las solicitudes que siguen sin monitor
    pendientes = sum(1 for s in solicitudes if s.monitor is None)
    print(f"Solicitudes sin monitor: {pendientes}\n")
 
 
def menu_asignar_monitor(solicitudes, monitores, historial):
 
    # solo se pueden asignar las solicitudes que todavia no tienen monitor
    pendientes = [s for s in solicitudes if s.monitor is None]
    if not pendientes:
        print("\nNo hay solicitudes sin monitor. Registra una o carga los ejemplos.")
        return
 
    # las muestra de la mas urgente a la menos urgente
    ordenadas, _ = ordenar_mezcla(pendientes, clave_urgencia)
    print("\nSolicitudes sin monitor (más urgentes primero):\n")
    mostrar_listado(ordenadas)
 
    # elige la solicitud por su numero
    por_numero = {s.numero: s for s in ordenadas}
    numero = pedir_entero("Número de la solicitud (0 para cancelar): ")
    if numero == 0:
        return
    solicitud = por_numero.get(numero)
    if solicitud is None:
        print("  Ese número no está en la lista")
        return
 
    # busca los monitores de esa materia, del mejor calificado al peor
    candidatos, _ = ordenar_mezcla(
        monitores_compatibles(solicitud, monitores), clave_monitor
    )
    if not candidatos:
        print(f"\nNo hay monitores registrados de {solicitud.materia}.")
        return
 
    print(f"\nMonitores de {solicitud.materia} (mejor calificación primero):")
    for i, monitor in enumerate(candidatos, start=1):
        print(f"{i}. {monitor.nombre} | calificación {monitor.calificacion} "
              f"| {monitor.disponibilidad}")
    opcion = pedir_opcion(
        "Elige el monitor: ", [str(i) for i in range(1, len(candidatos) + 1)]
    )
 
    # asigna y apila
    asignar_monitor(solicitud, candidatos[int(opcion) - 1], historial)
    print(f"\nAsignado: {historial.ver_tope()}")
 
 
def menu_deshacer_asignacion(historial):
 
    asignacion = deshacer_ultima_asignacion(historial)
 
    # si no habia nada, lo avisa
    if asignacion is None:
        print("\nNo hay asignaciones para deshacer.")
        return
 
    print("\nSe deshizo la última asignación:")
    print(f"  {asignacion}")
    print(f"La solicitud {asignacion.solicitud.numero} vuelve a quedar sin monitor.")
 
    # muestra cual es ahora la ultima asignacion
    if not historial.esta_vacia():
        print(f"Ahora la última asignación es: {historial.ver_tope()}")
 
 
def crear_monitores_ejemplo():
 
    # nombre, materia de especialidad, disponibilidad, calificacion
    datos = [
        ("Camila Ortiz", "Cálculo 1", "Lunes y miércoles 2-6pm", 4.8),
        ("Julián Herrera", "Cálculo 1", "Martes 10am-2pm", 4.5),
        ("Natalia Pinzón", "Física 1", "Jueves 2-6pm", 4.7),
        ("Felipe Duarte", "Álgebra lineal", "Viernes 8am-12pm", 4.6),
        ("Tomás Ramírez", "Introducción a programación", "Lunes 8am-12pm", 4.9),
        ("Isabela Cruz", "Lógica y teoría de conjuntos", "Miércoles 10am-2pm", 4.4),
    ]
    return [Monitor(nombre, materia, disponibilidad, calificacion)
            for nombre, materia, disponibilidad, calificacion in datos]
 
 
def preguntar_datos_estudiante():
 
    # inicia el proceso de registro
    print(" solicitud de monitoria")
 
    # pide el nombre del estudiante
    nombre = input("Nombre del estudiante: ")
 
    # pide el semestre
    semestre = int(input("Semestre que cursa: "))
 
    # pide el horario disponible
    horario = input("Horario disponible (ej: Lunes 2-4pm): ")
 
    # pide cuantos minutos en total tiene libres
    minutos = int(input("Minutos totales disponibles para monitorias (ej: 180): "))
 
 
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
        promedio_en_materia=promedio,
        minutos_disponibles=minutos
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
 
 
    # pide la fecha de la solicitud (sirve para ordenar por antiguedad)
    fecha = pedir_fecha("Fecha de la solicitud (dd/mm/aaaa, Enter para hoy): ")
 
 
    # crea la solicitud con los datos anteriores
    solicitud = SolicitudMonitoria(
        estudiante=estudiante,
        materia=materia,
        tema=tema,
        nivel_conocimiento=nivel_conocimiento,
        monitoria=monitoria,
        fecha=fecha
    )
 
 
    # devuelve la solicitud creada
    return solicitud
 
 
# verifica que el programa se este ejecutando directamente
if __name__ == "__main__":
 
    # aqui se guardan los datos mientras el programa esta abierto
    solicitudes = []
    monitores = []
 
    # pila con las asignaciones hechas (la ultima queda en el tope)
    historial = Pila()
 
    # menu principal: se repite hasta que elija salir
    while True:
        print("\n===== SISTEMA DE MONITORIAS =====")
        print("1. Registrar una solicitud de monitoria")
        print("2. Consultar la cadena de prerrequisitos de una materia")
        print("3. Listar solicitudes ordenadas")
        print("4. Cargar datos de ejemplo (solicitudes y monitores)")
        print("5. Asignar un monitor a una solicitud")
        print("6. Deshacer la última asignación")
        print("7. Ver asignaciones")
        print("0. Salir")
        opcion_menu = input("Elige una opción: ").strip()
 
        if opcion_menu == "1":
 
            # pide los datos y crea la solicitud
            solicitud = preguntar_datos_estudiante()
 
            # muestra el resumen final
            solicitud.mostrar_resumen()
 
            # muestra las combinaciones de monitorias que caben en su tiempo
            mostrar_plan_sugerido(solicitud.estudiante)
 
            # guarda la solicitud para poder listarla despues
            solicitudes.append(solicitud)
 
        elif opcion_menu == "2":
            consultar_prerrequisitos()
 
        elif opcion_menu == "3":
            listar_solicitudes(solicitudes)
 
        elif opcion_menu == "4":
            solicitudes.extend(crear_solicitudes_ejemplo())
 
            # los monitores de ejemplo se cargan una sola vez
            if not monitores:
                monitores.extend(crear_monitores_ejemplo())
            print(f"Datos cargados: {len(solicitudes)} solicitudes "
                  f"y {len(monitores)} monitores")
 
        elif opcion_menu == "5":
            menu_asignar_monitor(solicitudes, monitores, historial)
 
        elif opcion_menu == "6":
            menu_deshacer_asignacion(historial)
 
        elif opcion_menu == "7":
            mostrar_asignaciones(historial, solicitudes)
 
        elif opcion_menu == "0":
            print("Hasta luego.")
            break
 
        else:
            print("Opción no válida.")