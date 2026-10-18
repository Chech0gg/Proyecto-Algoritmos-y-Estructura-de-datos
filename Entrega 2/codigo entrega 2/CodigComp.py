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


# =====================================================================
# parte 2 - tabla hash
# sirve para guardar cosas por codigo y encontrarlas rapido
# =====================================================================
class tabla_hash:
    """funciona como un diccionario hecho a mano.

    tiene varias "cubetas" (listas). a cada clave se le calcula un numero
    y ese numero dice en que cubeta guardarla. asi, para buscar, solo hay
    que mirar una cubeta y no toda la tabla.
    si se llena mucho, se duplica la cantidad de cubetas."""

    def __init__(self):
        self.cubetas = []
        for i in range(16):
            self.cubetas.append([])
        self.cantidad = 0

    def calcular_hash(self, clave):
        """convierte un texto en un numero, mezclando el valor de cada letra."""
        numero = 0
        for letra in clave:
            numero = (numero * 31 + ord(letra)) % 2147483647
        return numero

    def buscar_cubeta(self, clave):
        """devuelve la cubeta donde deberia estar la clave."""
        posicion = self.calcular_hash(clave) % len(self.cubetas)
        return self.cubetas[posicion]

    def poner(self, clave, valor):
        """guarda un valor. si la clave ya existia, lo reemplaza."""
        cubeta = self.buscar_cubeta(clave)
        for par in cubeta:
            if par[0] == clave:
                par[1] = valor
                return
        cubeta.append([clave, valor])
        self.cantidad += 1
        if self.cantidad > 0.75 * len(self.cubetas):
            self.agrandar()

    def obtener(self, clave):
        """devuelve el valor de la clave, o nada si no existe."""
        for par in self.buscar_cubeta(clave):
            if par[0] == clave:
                return par[1]
        return None

    def contiene(self, clave):
        """dice si la clave existe."""
        return self.obtener(clave) is not None

    def valores(self):
        """devuelve una lista con todos los valores guardados."""
        lista = []
        for cubeta in self.cubetas:
            for par in cubeta:
                lista.append(par[1])
        return lista

    def agrandar(self):
        """duplica las cubetas y vuelve a guardar todo en su nueva posicion."""
        viejas = self.cubetas
        self.cubetas = []
        for i in range(len(viejas) * 2):
            self.cubetas.append([])
        self.cantidad = 0
        for cubeta in viejas:
            for par in cubeta:
                self.poner(par[0], par[1])

    def __len__(self):
        return self.cantidad


class generador_codigos:
    """crea codigos unicos como e-0001 (estudiante), m-0001 (monitor),
    p-0001 (profesor) y mat-0001 (materia). cada prefijo lleva su propia cuenta."""

    def __init__(self):
        self.contadores = {}

    def nuevo(self, prefijo):
        if prefijo not in self.contadores:
            self.contadores[prefijo] = 0
        self.contadores[prefijo] += 1
        return prefijo + "-" + f"{self.contadores[prefijo]:04d}"


# =====================================================================
# parte 3 - cola de solicitudes
# define en que orden se atienden las solicitudes
# =====================================================================
class clase_nodo:
    """una pieza de la cola: guarda un dato y apunta a la pieza siguiente."""

    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None


class cola:
    """una fila normal: el primero que entra es el primero que sale.
    esta hecha con piezas enlazadas (lista enlazada)."""

    def __init__(self):
        self.frente = None    # primera pieza (la que sale primero)
        self.final = None     # ultima pieza (donde se agrega)
        self.cantidad = 0

    def encolar(self, dato):
        """agrega un dato al final de la fila."""
        nodo = clase_nodo(dato)
        if self.final is None:
            self.frente = nodo
            self.final = nodo
        else:
            self.final.siguiente = nodo
            self.final = nodo
        self.cantidad += 1

    def desencolar(self):
        """saca y devuelve el dato que esta al frente."""
        if self.frente is None:
            raise error_validacion("la cola esta vacia")
        dato = self.frente.dato
        self.frente = self.frente.siguiente
        if self.frente is None:
            self.final = None
        self.cantidad -= 1
        return dato

    def esta_vacia(self):
        return self.cantidad == 0

    def como_lista(self):
        """devuelve los datos en orden sin sacarlos de la cola."""
        lista = []
        actual = self.frente
        while actual is not None:
            lista.append(actual.dato)
            actual = actual.siguiente
        return lista

    def __len__(self):
        return self.cantidad


# las prioridades de la mas urgente a la menos urgente
niveles_prioridad = ["alta", "media", "baja"]


def calcular_prioridad(materia, desempeno):
    """decide que tan urgente es una solicitud con esta cuenta:

        puntaje = dificultad de la materia * 2 + (5 - desempeno) * 2

    el desempeno va de 1 (voy muy mal) a 5 (voy muy bien).
    puntaje 12 o mas -> alta | de 7 a 11 -> media | menos de 7 -> baja

    devuelve el puntaje, el nivel y un texto que explica la cuenta."""
    por_dificultad = materia.dificultad * 2
    por_desempeno = (5 - desempeno) * 2
    puntaje = por_dificultad + por_desempeno
    if puntaje >= 12:
        nivel = "alta"
    elif puntaje >= 7:
        nivel = "media"
    else:
        nivel = "baja"
    explicacion = (f"dificultad {materia.dificultad}*2={por_dificultad} + "
                   f"desempeno {desempeno}->{por_desempeno} = {puntaje}")
    return puntaje, nivel, explicacion


class clase_solicitud:
    """un pedido de monitoria. el estado cambia con el tiempo:
    pendiente (recien creada) -> asignada (ya tiene hora) o en_espera."""

    def __init__(self, id, estudiante, materia, tipo, desempeno, puntaje, prioridad, desglose):
        self.id = id
        self.estudiante = estudiante
        self.materia = materia
        self.tipo = tipo
        self.desempeno = desempeno
        self.puntaje = puntaje
        self.prioridad = prioridad
        self.desglose = desglose
        self.estado = "pendiente"
        self.motivo = ""    # por que esta en espera (o con quien se asigno)


class cola_solicitudes:
    """tiene una fila por cada prioridad (alta, media, baja).
    siempre se atiende primero la fila mas urgente que tenga alguien, y
    dentro de una fila, el que llego primero."""

    def __init__(self):
        self.filas = {"alta": cola(), "media": cola(), "baja": cola()}

    def encolar(self, solicitud):
        """pone la solicitud en la fila de su prioridad."""
        self.filas[solicitud.prioridad].encolar(solicitud)

    def desencolar(self):
        """saca la siguiente solicitud a atender."""
        for nivel in niveles_prioridad:
            if not self.filas[nivel].esta_vacia():
                return self.filas[nivel].desencolar()
        raise error_validacion("no hay solicitudes pendientes")

    def esta_vacia(self):
        return len(self) == 0

    def pendientes(self):
        """lista de todas las solicitudes en el orden en que se atenderian."""
        lista = []
        for nivel in niveles_prioridad:
            lista = lista + self.filas[nivel].como_lista()
        return lista

    def __len__(self):
        total = 0
        for nivel in niveles_prioridad:
            total += len(self.filas[nivel])
        return total


# =====================================================================
# parte 4 - agenda
# guarda las sesiones ya programadas y dice si una hora esta libre
# =====================================================================
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


# =====================================================================
# parte 5 (NUEVA) - prerrequisitos: recursion y backtracking
# guarda que materia necesita cual y recorre la cadena de prerrequisitos
# =====================================================================
class mapa_prerrequisitos:
    """guarda, para cada materia (por su codigo), la lista de materias que
    hay que ver antes (prerrequisitos directos). usa la tabla hash propia.

    ejemplo: fisica 2 necesita fisica 1 y calculo 2
        requisitos["mat-0004"] = ["mat-0003", "mat-0002"]"""

    def __init__(self):
        self.requisitos = tabla_hash()    # codigo de materia -> lista de codigos

    def directos(self, materia):
        """devuelve los prerrequisitos directos (lista vacia si no tiene)."""
        lista = self.requisitos.obtener(materia)
        if lista is None:
            return []
        return lista

    # ---------- backtracking 1: evitar ciclos al registrar ----------
    def hay_camino(self, desde, hasta, camino):
        """dice si siguiendo prerrequisitos se llega de 'desde' a 'hasta'.
        'camino' guarda las materias por las que va pasando esta busqueda."""
        if desde == hasta:                      # caso base: ya llegamos
            return True
        camino.append(desde)                    # elegir: pasar por 'desde'
        for requisito in self.directos(desde):
            if requisito not in camino:
                if self.hay_camino(requisito, hasta, camino):
                    return True
        camino.pop()                            # deshacer: este camino no sirvio
        return False

    def agregar(self, materia, requisito):
        """registra que 'materia' necesita 'requisito'. se rechaza si
        formaria un ciclo (a necesita b y b necesita a, directa o indirectamente)."""
        if requisito in self.directos(materia):
            raise error_validacion(materia + " ya tiene a " + requisito + " como prerrequisito")
        # si desde el requisito ya se llega a la materia, agregarlo crearia un ciclo
        if self.hay_camino(requisito, materia, []):
            raise error_validacion("ciclo: " + requisito + " ya depende de " + materia)
        lista = self.requisitos.obtener(materia)
        if lista is None:
            lista = []
            self.requisitos.poner(materia, lista)
        lista.append(requisito)

    # ---------- recursion: recorrer la cadena completa ----------
    def cadena(self, materia, orden=None):
        """devuelve TODOS los prerrequisitos (directos e indirectos) en el
        orden en que hay que verlos: primero los mas basicos."""
        if orden is None:
            orden = []
        for requisito in self.directos(materia):
            if requisito not in orden:
                self.cadena(requisito, orden)   # primero los requisitos del requisito
                orden.append(requisito)         # y despues el requisito
        return orden

    def profundidad(self, materia):
        """cuantos 'escalones' hay hasta la materia mas basica de su cadena."""
        requisitos = self.directos(materia)
        if len(requisitos) == 0:                # caso base: no necesita nada
            return 0
        mayor = 0
        for requisito in requisitos:
            nivel = self.profundidad(requisito)
            if nivel > mayor:
                mayor = nivel
        return 1 + mayor

    # ---------- backtracking 2: listar todas las rutas ----------
    def rutas(self, materia):
        """devuelve todas las rutas posibles desde la materia hasta una
        materia que no necesita nada. cada ruta es una lista de codigos."""
        resultado = []
        self.explorar(materia, [materia], resultado)
        return resultado

    def explorar(self, materia, camino, resultado):
        requisitos = self.directos(materia)
        if len(requisitos) == 0:                # caso base: llegamos al final de una ruta
            resultado.append(list(camino))      # se guarda una COPIA del camino
            return
        for requisito in requisitos:
            camino.append(requisito)            # elegir
            self.explorar(requisito, camino, resultado)
            camino.pop()                        # deshacer (probar otro requisito)

    def faltantes(self, materia, cursadas):
        """prerrequisitos de la cadena que todavia no se han cursado.
        'cursadas' es un conjunto (parte 8) de codigos de materia: la cadena
        la arma la recursion y el conjunto responde rapido 'ya la curso?'."""
        pendientes = []
        for requisito in self.cadena(materia):
            if not cursadas.contiene(requisito):
                pendientes.append(requisito)
        return pendientes


# =====================================================================
# parte 6 (NUEVA) - ordenamientos
# insertion sort (basico) y merge sort / quick sort (avanzados), para
# hacer listados de solicitudes por urgencia, antiguedad o materia
# =====================================================================
def clave_urgencia(solicitud):
    """primero la prioridad (alta antes que media), luego el puntaje mas
    alto, y si empatan, la que llego primero."""
    return (niveles_prioridad.index(solicitud.prioridad), -solicitud.puntaje, solicitud.id)


def clave_antiguedad(solicitud):
    """la que llego primero (id mas bajo) va primero."""
    return solicitud.id


def clave_materia(solicitud):
    """orden alfabetico por nombre de materia; si empatan, por llegada."""
    return (solicitud.materia.nombre, solicitud.id)


claves = {"urgencia": clave_urgencia, "antiguedad": clave_antiguedad, "materia": clave_materia}


def ordenar_insercion(lista, clave):
    """va tomando cada elemento y lo "inserta" en su lugar dentro de la
    parte que ya esta ordenada (como ordenar cartas en la mano).
    es estable: si dos empatan, conservan su orden original.
    mejor caso (ya ordenada): n comparaciones | peor caso: n al cuadrado."""
    resultado = list(lista)                     # copia, para no dañar la original
    for i in range(1, len(resultado)):
        actual = resultado[i]
        j = i - 1
        # se corren a la derecha los que sean mayores que 'actual'
        while j >= 0 and clave(resultado[j]) > clave(actual):
            resultado[j + 1] = resultado[j]
            j -= 1
        resultado[j + 1] = actual               # aqui queda 'actual'
    return resultado


def mezclar(izquierda, derecha, clave):
    """junta dos listas YA ordenadas en una sola ordenada."""
    resultado = []
    i = 0
    j = 0
    while i < len(izquierda) and j < len(derecha):
        # solo pasa la derecha si es estrictamente menor: asi es estable
        if clave(derecha[j]) < clave(izquierda[i]):
            resultado.append(derecha[j])
            j += 1
        else:
            resultado.append(izquierda[i])
            i += 1
    while i < len(izquierda):                   # sobras de la izquierda
        resultado.append(izquierda[i])
        i += 1
    while j < len(derecha):                     # sobras de la derecha
        resultado.append(derecha[j])
        j += 1
    return resultado


def ordenar_mezcla(lista, clave):
    """divide la lista por la mitad, ordena cada mitad con la misma funcion
    (recursion) y las mezcla. siempre n*log(n); es estable; usa lista extra."""
    if len(lista) <= 1:                         # caso base: ya esta ordenada
        return list(lista)
    medio = len(lista) // 2
    izquierda = ordenar_mezcla(lista[:medio], clave)
    derecha = ordenar_mezcla(lista[medio:], clave)
    return mezclar(izquierda, derecha, clave)


def particionar(lista, bajo, alto, clave):
    """elige un pivote y reacomoda la lista: los menores quedan a su
    izquierda y los demas a su derecha. devuelve donde quedo el pivote."""
    medio = (bajo + alto) // 2                  # pivote del medio (evita el peor caso
    lista[medio], lista[alto] = lista[alto], lista[medio]    # en listas ya ordenadas)
    pivote = clave(lista[alto])
    frontera = bajo                             # donde va el proximo "menor"
    for i in range(bajo, alto):
        if clave(lista[i]) < pivote:
            lista[i], lista[frontera] = lista[frontera], lista[i]
            frontera += 1
    lista[frontera], lista[alto] = lista[alto], lista[frontera]   # pivote a su lugar
    return frontera


def rapido(lista, bajo, alto, clave):
    """ordena lista[bajo..alto] sobre la misma lista (sin crear otras)."""
    if bajo >= alto:                            # caso base: 0 o 1 elemento
        return
    posicion = particionar(lista, bajo, alto, clave)
    rapido(lista, bajo, posicion - 1, clave)    # lado de los menores
    rapido(lista, posicion + 1, alto, clave)    # lado de los mayores


def ordenar_rapido(lista, clave):
    """promedio n*log(n); peor caso n al cuadrado (poco comun);
    NO es estable, pero con las claves de arriba nunca hay empates
    porque todas terminan comparando el id."""
    resultado = list(lista)
    rapido(resultado, 0, len(resultado) - 1, clave)
    return resultado


metodos = {"insercion": ordenar_insercion, "mezcla": ordenar_mezcla, "rapido": ordenar_rapido}
limite_insercion = 10    # con 10 elementos o menos, insertion sort es suficiente


def ordenar(lista, criterio, metodo="auto"):
    """ordena solicitudes por 'urgencia', 'antiguedad' o 'materia'.
    metodo: 'insercion', 'mezcla', 'rapido' o 'auto' (insercion si la lista
    es pequeña, mezcla si es grande)."""
    if criterio not in claves:
        raise error_validacion("criterio invalido: '" + str(criterio) + "' (urgencia, antiguedad o materia)")
    if metodo == "auto":
        if len(lista) <= limite_insercion:
            metodo = "insercion"
        else:
            metodo = "mezcla"
    if metodo not in metodos:
        raise error_validacion("metodo invalido: '" + str(metodo) + "'")
    return metodos[metodo](lista, claves[criterio])


# =====================================================================
# parte 7 (NUEVA) - pila
# guarda cada asignacion que se hace, para poder revertir la ultima
# =====================================================================
class pila:
    """una pila: el ULTIMO que entra es el PRIMERO que sale (como una pila
    de platos). esta hecha con piezas enlazadas, igual que la cola.

    sirve para deshacer: lo ultimo que se hizo es lo primero que se revierte."""

    def __init__(self):
        self.tope = None      # la pieza de arriba (la ultima que entro)
        self.cantidad = 0

    def apilar(self, dato):
        """pone un dato encima de la pila."""
        nodo = clase_nodo(dato)
        nodo.siguiente = self.tope      # la nueva apunta a la que estaba arriba
        self.tope = nodo                # y pasa a ser la de arriba
        self.cantidad += 1

    def desapilar(self):
        """saca y devuelve el dato de arriba."""
        if self.tope is None:
            raise error_validacion("la pila esta vacia")
        dato = self.tope.dato
        self.tope = self.tope.siguiente
        self.cantidad -= 1
        return dato

    def ver_tope(self):
        """devuelve el dato de arriba SIN sacarlo (nada si esta vacia)."""
        if self.tope is None:
            return None
        return self.tope.dato

    def esta_vacia(self):
        return self.cantidad == 0

    def como_lista(self):
        """devuelve los datos de arriba hacia abajo sin sacarlos."""
        lista = []
        actual = self.tope
        while actual is not None:
            lista.append(actual.dato)
            actual = actual.siguiente
        return lista

    def __len__(self):
        return self.cantidad


class clase_registro_asignacion:
    """lo que hay que recordar de una asignacion para poder deshacerla:
    la solicitud, la sesion y si esa asignacion CREO la sesion o solo
    metio al estudiante en una sesion (grupo) que ya existia."""

    def __init__(self, solicitud, sesion, creo_sesion):
        self.solicitud = solicitud
        self.sesion = sesion
        self.creo_sesion = creo_sesion


def revertir_registro(registro, agenda):
    """deshace una asignacion sobre la agenda y devuelve la solicitud afectada."""
    if registro.creo_sesion:
        agenda.sesiones.remove(registro.sesion)                         # se borra la sesion entera
    else:
        registro.sesion.estudiantes.remove(registro.solicitud.estudiante)   # solo sale del grupo
    return registro.solicitud


# =====================================================================
# parte 8 (NUEVA) - conjuntos y mapas
# conjunto: coleccion sin repetidos (areas) | mapa: la tabla hash
# =====================================================================
class conjunto:
    """un conjunto: agregar un elemento que ya esta no hace nada, asi que
    nunca hay repetidos. se apoya en la tabla hash: cada elemento se guarda
    como clave (y tambien como valor, para poder listarlos despues).
    los elementos deben ser textos (codigos, nombres de areas, etc.)."""

    def __init__(self, elementos=()):
        self.tabla = tabla_hash()
        for elemento in elementos:
            self.agregar(elemento)

    def agregar(self, elemento):
        """agrega el elemento. devuelve verdadero si era nuevo y falso si ya estaba."""
        era_nuevo = not self.contiene(elemento)
        self.tabla.poner(elemento, elemento)
        return era_nuevo

    def contiene(self, elemento):
        return self.tabla.contiene(elemento)

    def elementos(self):
        """lista con los elementos (sin un orden en particular)."""
        return self.tabla.valores()

    def union(self, otro):
        """los que estan en uno u otro conjunto."""
        resultado = conjunto(self.elementos())
        for elemento in otro.elementos():
            resultado.agregar(elemento)
        return resultado

    def interseccion(self, otro):
        """los que estan en los dos conjuntos."""
        resultado = conjunto()
        for elemento in self.elementos():
            if otro.contiene(elemento):
                resultado.agregar(elemento)
        return resultado

    def diferencia(self, otro):
        """los que estan en este conjunto pero NO en el otro."""
        resultado = conjunto()
        for elemento in self.elementos():
            if not otro.contiene(elemento):
                resultado.agregar(elemento)
        return resultado

    def __len__(self):
        return len(self.tabla)


class registro_cursadas:
    """mapa: codigo de estudiante -> conjunto de codigos de materias cursadas.
    el conjunto evita que una materia se registre dos veces."""

    def __init__(self):
        self.por_estudiante = tabla_hash()

    def registrar(self, estudiante, materia):
        """anota que el estudiante cursó la materia. devuelve verdadero si
        era nueva y falso si ya estaba anotada."""
        cursadas = self.por_estudiante.obtener(estudiante)
        if cursadas is None:
            cursadas = conjunto()
            self.por_estudiante.poner(estudiante, cursadas)
        return cursadas.agregar(materia)

    def de(self, estudiante):
        """el conjunto de materias cursadas (vacio si no ha cursado ninguna)."""
        cursadas = self.por_estudiante.obtener(estudiante)
        if cursadas is None:
            return conjunto()
        return cursadas

    def ha_cursado(self, estudiante, materia):
        return self.de(estudiante).contiene(materia)


def clave_texto(texto):
    """clave para ordenar textos alfabeticamente con los ordenamientos de la parte 6."""
    return texto


# =====================================================================
# parte 9 - sistema principal
# junta todas las partes y ofrece las funciones que usa el usuario
# =====================================================================
class sistema_monitorias:
    def __init__(self):
        self.personas = tabla_hash()            # estudiantes, monitores y profesores por codigo
        self.materias = tabla_hash()            # materias por codigo
        self.codigos = generador_codigos()
        self.cola = cola_solicitudes()          # solicitudes nuevas que faltan por atender
        self.lista_espera = cola_solicitudes()  # solicitudes que no se pudieron asignar
        self.agenda = agenda()
        self.prerrequisitos = mapa_prerrequisitos()   # NUEVO: que materia necesita cual
        self.historial = pila()                 # NUEVO: asignaciones hechas, la ultima arriba
        self.cursadas = registro_cursadas()     # NUEVO: materias ya cursadas por estudiante
        self.solicitudes = []                  # todas las solicitudes (historial)
        self.orden_atencion = []               # ids de las solicitudes en el orden en que se atendieron

    # ---------- registros ----------
    def crear_bloques(self, disponibilidad):
        """convierte una lista de tuplas (dia, inicio, fin) en una lista de bloques."""
        bloques = []
        for dia, inicio, fin in disponibilidad:
            bloques.append(crear_bloque(dia, inicio, fin))
        return bloques

    def revisar_materias(self, codigos_materias):
        """revisa que todos los codigos de materia existan."""
        for codigo in codigos_materias:
            if not self.materias.contiene(codigo):
                raise error_validacion("la materia '" + codigo + "' no existe")

    def registrar_materia(self, nombre, area, nivel, dificultad):
        codigo = self.codigos.nuevo("mat")
        materia = clase_materia(codigo, nombre, area, nivel, dificultad)
        self.materias.poner(codigo, materia)
        return materia

    def registrar_estudiante(self, nombre, semestre, carrera, disponibilidad=()):
        if carrera.strip() == "":
            raise error_validacion("el estudiante necesita una carrera")
        bloques = self.crear_bloques(disponibilidad)
        estudiante = clase_estudiante(self.codigos.nuevo("e"), nombre, semestre, carrera, bloques)
        self.personas.poner(estudiante.codigo, estudiante)
        return estudiante

    def registrar_monitor(self, nombre, semestre, codigos_materias, disponibilidad=()):
        if len(codigos_materias) == 0:
            raise error_validacion("el monitor debe apoyar al menos una materia")
        self.revisar_materias(codigos_materias)
        bloques = self.crear_bloques(disponibilidad)
        monitor = clase_monitor(self.codigos.nuevo("m"), nombre, semestre, list(codigos_materias), bloques)
        self.personas.poner(monitor.codigo, monitor)
        self.reintentar_lista_espera()    # un monitor nuevo puede resolver solicitudes en espera
        return monitor

    def registrar_profesor(self, nombre, codigos_materias=()):
        if nombre.strip() == "":
            raise error_validacion("el nombre no puede estar vacio")
        self.revisar_materias(codigos_materias)
        profesor = clase_profesor(self.codigos.nuevo("p"), nombre, list(codigos_materias))
        self.personas.poner(profesor.codigo, profesor)
        return profesor

    # ---------- busqueda ----------
    def buscar(self, codigo):
        """busca por codigo un estudiante, monitor, profesor o materia.
        devuelve nada si no existe."""
        persona = self.personas.obtener(codigo)
        if persona is not None:
            return persona
        return self.materias.obtener(codigo)

    # ---------- prerrequisitos (NUEVO) ----------
    def agregar_prerrequisito(self, codigo_materia, codigo_requisito):
        """registra que una materia necesita otra. revisa que existan las
        dos y que no se forme un ciclo."""
        self.revisar_materias([codigo_materia, codigo_requisito])
        self.prerrequisitos.agregar(codigo_materia, codigo_requisito)

    def nombres(self, codigos):
        """convierte una lista de codigos de materia en una lista de nombres."""
        lista = []
        for codigo in codigos:
            lista.append(self.materias.obtener(codigo).nombre)
        return lista

    def cadena_de(self, codigo_materia):
        """nombres de todos los prerrequisitos de la materia, en orden de estudio."""
        self.revisar_materias([codigo_materia])
        return self.nombres(self.prerrequisitos.cadena(codigo_materia))

    def rutas_de(self, codigo_materia):
        """todas las rutas de prerrequisitos de la materia, con nombres."""
        self.revisar_materias([codigo_materia])
        rutas = []
        for ruta in self.prerrequisitos.rutas(codigo_materia):
            rutas.append(self.nombres(ruta))
        return rutas

    # ---------- materias cursadas (NUEVO: mapa de conjuntos) ----------
    def revisar_estudiante(self, codigo_estudiante):
        """revisa que el codigo sea de un estudiante registrado."""
        if not isinstance(self.personas.obtener(codigo_estudiante), clase_estudiante):
            raise error_validacion("'" + str(codigo_estudiante) + "' no es un estudiante registrado")

    def registrar_cursada(self, codigo_estudiante, codigo_materia):
        """anota que el estudiante ya curso la materia. devuelve verdadero si
        era nueva y falso si ya estaba anotada (no se repite)."""
        self.revisar_estudiante(codigo_estudiante)
        self.revisar_materias([codigo_materia])
        return self.cursadas.registrar(codigo_estudiante, codigo_materia)

    def ha_cursado(self, codigo_estudiante, codigo_materia):
        self.revisar_estudiante(codigo_estudiante)
        return self.cursadas.ha_cursado(codigo_estudiante, codigo_materia)

    def materias_cursadas(self, codigo_estudiante):
        """nombres de las materias que el estudiante ya curso, en orden alfabetico."""
        self.revisar_estudiante(codigo_estudiante)
        nombres = self.nombres(self.cursadas.de(codigo_estudiante).elementos())
        return ordenar_insercion(nombres, clave_texto)

    def areas_cursadas(self, codigo_estudiante):
        """conjunto con las areas de las materias que el estudiante ya curso."""
        self.revisar_estudiante(codigo_estudiante)
        return self.areas_de_materias(self.cursadas.de(codigo_estudiante).elementos())

    def faltantes_de(self, codigo_estudiante, codigo_materia):
        """nombres de los prerrequisitos que el estudiante aun no ha cursado."""
        self.revisar_estudiante(codigo_estudiante)
        self.revisar_materias([codigo_materia])
        cursadas = self.cursadas.de(codigo_estudiante)
        return self.nombres(self.prerrequisitos.faltantes(codigo_materia, cursadas))

    # ---------- areas sin repeticion (NUEVO: conjuntos y mapas) ----------
    def areas_de_materias(self, codigos_materias):
        """conjunto con las areas de esas materias (cada area una sola vez)."""
        areas = conjunto()
        for codigo in codigos_materias:
            areas.agregar(self.materias.obtener(codigo).area)
        return areas

    def areas_del_sistema(self):
        """todas las areas que existen, sin repetir."""
        areas = conjunto()
        for materia in self.materias.valores():
            areas.agregar(materia.area)
        return areas

    def areas_de_monitor(self, codigo_monitor):
        """areas que cubre un monitor, sin repetir."""
        monitor = self.personas.obtener(codigo_monitor)
        if not isinstance(monitor, clase_monitor):
            raise error_validacion("'" + str(codigo_monitor) + "' no es un monitor registrado")
        return self.areas_de_materias(monitor.materias)

    def areas_cubiertas(self):
        """areas que tienen al menos un monitor (union de las areas de cada monitor)."""
        areas = conjunto()
        for persona in self.personas.valores():
            if isinstance(persona, clase_monitor):
                areas = areas.union(self.areas_de_materias(persona.materias))
        return areas

    def areas_sin_monitor(self):
        """areas que existen pero ningun monitor cubre (diferencia de conjuntos)."""
        return self.areas_del_sistema().diferencia(self.areas_cubiertas())

    def monitores_por_area(self):
        """mapa: area -> conjunto con los nombres de los monitores que la cubren."""
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
        """mapa: area -> cuantas solicitudes se han hecho en esa area."""
        mapa = tabla_hash()
        for solicitud in self.solicitudes:
            area = solicitud.materia.area
            actual = mapa.obtener(area)
            if actual is None:
                actual = 0
            mapa.poner(area, actual + 1)
        return mapa

    def mostrar_areas(self):
        """devuelve un resumen por area (alfabetico): monitores y solicitudes."""
        monitores = self.monitores_por_area()
        solicitudes = self.solicitudes_por_area()
        lineas = []
        for area in ordenar_mezcla(self.areas_del_sistema().elementos(), clave_texto):
            nombres = monitores.obtener(area)
            if nombres is None:
                texto_monitores = "ninguno"
            else:
                texto_monitores = ", ".join(ordenar_insercion(nombres.elementos(), clave_texto))
            cantidad = solicitudes.obtener(area)
            if cantidad is None:
                cantidad = 0
            lineas.append(f"{area:<12} | monitores: {texto_monitores} | solicitudes: {cantidad}")
        return "\n".join(lineas)

    # ---------- solicitudes ----------
    def solicitar(self, codigo_estudiante, codigo_materia, tipo, desempeno):
        """un estudiante pide una monitoria. se revisan los datos, se calcula
        la prioridad y la solicitud entra a la cola."""
        estudiante = self.personas.obtener(codigo_estudiante)
        if not isinstance(estudiante, clase_estudiante):
            raise error_validacion("'" + str(codigo_estudiante) + "' no es un estudiante registrado")
        materia = self.materias.obtener(codigo_materia)
        if materia is None:
            raise error_validacion("la materia '" + str(codigo_materia) + "' no existe")
        if tipo not in duracion_min:
            raise error_validacion("tipo de monitoria invalido")
        if desempeno < 1 or desempeno > 5:
            raise error_validacion("el desempeno debe estar entre 1 (muy mal) y 5 (muy bien)")
        if materia.nivel > estudiante.semestre:
            raise error_validacion(materia.nombre + " es de nivel " + str(materia.nivel) +
                                  " y el estudiante va en semestre " + str(estudiante.semestre))
        puntaje, prioridad, desglose = calcular_prioridad(materia, desempeno)
        solicitud = clase_solicitud(len(self.solicitudes) + 1, estudiante, materia, tipo,
                              desempeno, puntaje, prioridad, desglose)
        self.solicitudes.append(solicitud)
        self.cola.encolar(solicitud)
        return solicitud

    # ---------- revertir asignaciones (NUEVO) ----------
    def ultima_asignacion(self):
        """devuelve la solicitud de la ultima asignacion hecha, sin revertirla
        (nada si no hay asignaciones)."""
        registro = self.historial.ver_tope()
        if registro is None:
            return None
        return registro.solicitud

    def revertir_ultima_asignacion(self):
        """deshace la ultima asignacion: quita la sesion (o saca al estudiante
        del grupo) y manda la solicitud a la lista de espera con el motivo
        'asignacion revertida'. devuelve la solicitud afectada."""
        if self.historial.esta_vacia():
            raise error_validacion("no hay asignaciones para revertir")
        registro = self.historial.desapilar()
        solicitud = revertir_registro(registro, self.agenda)
        self.marcar(solicitud, "en_espera", "asignacion revertida")
        self.lista_espera.encolar(solicitud)
        return solicitud

    def mostrar_historial(self):
        """devuelve las asignaciones que se pueden revertir, de la mas
        reciente a la mas antigua."""
        if self.historial.esta_vacia():
            return "(sin asignaciones)"
        lineas = []
        for registro in self.historial.como_lista():
            s = registro.solicitud
            if registro.creo_sesion:
                accion = "sesion nueva"
            else:
                accion = "se unio a un grupo"
            lineas.append(f"#{s.id} {s.estudiante.nombre:<6} {s.materia.nombre:<22} {accion}")
        return "\n".join(lineas)

    # ---------- listados ordenados (NUEVO) ----------
    def listar_solicitudes(self, criterio, metodo="auto", estado=None):
        """devuelve las solicitudes ordenadas por 'urgencia', 'antiguedad' o
        'materia'. si se da un estado ('pendiente', 'asignada' o 'en_espera')
        solo se listan las de ese estado. no cambia el orden de atencion."""
        lista = []
        for solicitud in self.solicitudes:
            if estado is None or solicitud.estado == estado:
                lista.append(solicitud)
        return ordenar(lista, criterio, metodo)

    def mostrar_listado(self, criterio, metodo="auto", estado=None):
        """devuelve el listado como texto, una solicitud por linea."""
        lista = self.listar_solicitudes(criterio, metodo, estado)
        if len(lista) == 0:
            return "(sin solicitudes)"
        lineas = []
        for s in lista:
            lineas.append(f"#{s.id} {s.estudiante.nombre:<6} {s.materia.nombre:<22} "
                          f"{s.prioridad:<6} ({s.puntaje:>2}) {s.estado}")
        return "\n".join(lineas)

    # ---------- agenda ----------
    def generar_agenda(self):
        """atiende todas las solicitudes de la cola (prioridad primero, luego
        orden de llegada). las que no se pueden asignar pasan a la lista de espera."""
        while not self.cola.esta_vacia():
            solicitud = self.cola.desencolar()
            self.orden_atencion.append(solicitud.id)
            if not self.asignar(solicitud):
                self.lista_espera.encolar(solicitud)
        return self.agenda

    # ---------- lista de espera ----------
    def reintentar_lista_espera(self):
        """vuelve a intentar asignar las solicitudes en espera, con el mismo
        orden de siempre. devuelve las que si quedaron asignadas."""
        # primero se vacia la lista de espera en una lista normal
        en_espera = []
        while not self.lista_espera.esta_vacia():
            en_espera.append(self.lista_espera.desencolar())
        # luego se intenta cada una; las que fallan vuelven a la lista de espera
        asignadas = []
        for solicitud in en_espera:
            if self.asignar(solicitud):
                self.orden_atencion.append(solicitud.id)
                asignadas.append(solicitud)
            else:
                self.lista_espera.encolar(solicitud)
        return asignadas

    def agregar_disponibilidad_monitor(self, codigo, disponibilidad):
        """el monitor publica horarios nuevos y se reintenta la lista de espera."""
        monitor = self.personas.obtener(codigo)
        if not isinstance(monitor, clase_monitor):
            raise error_validacion("'" + str(codigo) + "' no es un monitor registrado")
        monitor.disponibilidad.extend(self.crear_bloques(disponibilidad))
        return self.reintentar_lista_espera()

    def agregar_disponibilidad_estudiante(self, codigo, disponibilidad):
        """el estudiante agrega horarios nuevos y se reintenta la lista de espera."""
        estudiante = self.personas.obtener(codigo)
        if not isinstance(estudiante, clase_estudiante):
            raise error_validacion("'" + str(codigo) + "' no es un estudiante registrado")
        estudiante.disponibilidad.extend(self.crear_bloques(disponibilidad))
        return self.reintentar_lista_espera()

    # ---------- como se asigna una solicitud ----------
    def monitores_de(self, materia):
        """devuelve los monitores que apoyan la materia, ordenados por codigo."""
        encontrados = []
        for persona in self.personas.valores():
            if isinstance(persona, clase_monitor) and materia.codigo in persona.materias:
                encontrados.append(persona)

        def por_codigo(monitor):
            return monitor.codigo
        return sorted(encontrados, key=por_codigo)

    def estudiante_puede(self, estudiante, dia, inicio, fin):
        """dice si el estudiante tiene ese rango en su disponibilidad
        y no tiene otra sesion al mismo tiempo."""
        en_su_horario = False
        for bloque in estudiante.disponibilidad:
            if bloque.cubre(dia, inicio, fin):
                en_su_horario = True
        return en_su_horario and self.agenda.estudiante_libre(estudiante, dia, inicio, fin)

    def unirse_a_grupo(self, solicitud):
        """solo para monitorias generales: busca un grupo que ya exista con la
        misma materia, que tenga cupo y que le sirva al estudiante.
        devuelve si logro unirse o no."""
        estudiante = solicitud.estudiante
        for sesion in self.agenda.sesiones:
            if sesion.tipo != "general" or sesion.materia.codigo != solicitud.materia.codigo:
                continue
            if len(sesion.estudiantes) >= cupo[sesion.tipo]:
                continue
            if self.estudiante_puede(estudiante, sesion.dia, sesion.inicio, sesion.fin):
                sesion.estudiantes.append(estudiante)
                self.historial.apilar(clase_registro_asignacion(solicitud, sesion, False))   # NUEVO
                self.marcar(solicitud, "asignada", "se unio al grupo de " + sesion.monitor.nombre)
                return True
        return False

    def buscar_hueco(self, monitor, estudiante, duracion):
        """busca la primera hora en la que el monitor y el estudiante pueden
        reunirse. devuelve (dia, inicio) o nada si no hay ninguna."""
        for bloque_monitor in monitor.disponibilidad:
            for bloque_estudiante in estudiante.disponibilidad:
                if bloque_monitor.dia != bloque_estudiante.dia:
                    continue
                # el rango en el que los dos estan libres
                desde = max(bloque_monitor.inicio, bloque_estudiante.inicio)
                hasta = min(bloque_monitor.fin, bloque_estudiante.fin)
                dia = bloque_monitor.dia
                # se prueba cada hora posible hasta que la sesion ya no quepa
                inicio = desde
                while inicio + duracion <= hasta:
                    fin = inicio + duracion
                    if (self.agenda.monitor_libre(monitor, dia, inicio, fin)
                            and self.agenda.estudiante_libre(estudiante, dia, inicio, fin)):
                        return dia, inicio
                    inicio += paso_min
        return None

    def asignar(self, solicitud):
        """intenta darle hora a la solicitud. si lo logra, queda asignada y
        devuelve verdadero. si no, queda en_espera con el motivo y devuelve falso."""
        estudiante = solicitud.estudiante
        duracion = duracion_min[solicitud.tipo]

        # paso 1: si es general, intentar unirse a un grupo que ya existe
        if solicitud.tipo == "general" and self.unirse_a_grupo(solicitud):
            return True

        # paso 2: revisar que haya con que trabajar
        monitores = self.monitores_de(solicitud.materia)
        if len(monitores) == 0:
            self.marcar(solicitud, "en_espera", "no hay monitor para la materia")
            return False
        if len(estudiante.disponibilidad) == 0:
            self.marcar(solicitud, "en_espera", "el estudiante no registro disponibilidad")
            return False
        algun_horario = False
        for monitor in monitores:
            if len(monitor.disponibilidad) > 0:
                algun_horario = True
        if not algun_horario:
            self.marcar(solicitud, "en_espera", "el monitor aun no publica horarios")
            return False

        # paso 3: buscar una hora con cada monitor, en orden, y crear la sesion
        for monitor in monitores:
            hueco = self.buscar_hueco(monitor, estudiante, duracion)
            if hueco is not None:
                dia, inicio = hueco
                sesion = clase_sesion(monitor, solicitud.materia, solicitud.tipo,
                                dia, inicio, inicio + duracion, [estudiante])
                self.agenda.sesiones.append(sesion)
                self.historial.apilar(clase_registro_asignacion(solicitud, sesion, True))    # NUEVO
                self.marcar(solicitud, "asignada", "monitor " + monitor.nombre)
                return True

        self.marcar(solicitud, "en_espera", "no hay horarios o cupos compatibles entre estudiante y monitor")
        return False

    def marcar(self, solicitud, estado, motivo):
        """cambia el estado de la solicitud y guarda la razon."""
        solicitud.estado = estado
        solicitud.motivo = motivo

    # ---------- informe ----------
    def informe_cobertura(self):
        """cuenta cuantas solicitudes se atendieron y devuelve los datos en un diccionario."""
        asignadas = 0
        en_espera = 0
        pendientes = 0
        detalle_en_espera = []
        por_materia = {}    # nombre de materia -> (solicitudes, atendidas)

        for solicitud in self.solicitudes:
            nombre = solicitud.materia.nombre
            if nombre not in por_materia:
                por_materia[nombre] = (0, 0)
            total_materia, atendidas = por_materia[nombre]

            if solicitud.estado == "asignada":
                asignadas += 1
                atendidas += 1
            elif solicitud.estado == "en_espera":
                en_espera += 1
                detalle_en_espera.append((solicitud.id, solicitud.estudiante.nombre,
                                          nombre, solicitud.motivo))
            else:
                pendientes += 1
            por_materia[nombre] = (total_materia + 1, atendidas)

        horas_monitor = {}    # nombre del monitor -> horas agendadas
        for sesion in self.agenda.sesiones:
            nombre = sesion.monitor.nombre
            if nombre not in horas_monitor:
                horas_monitor[nombre] = 0
            horas_monitor[nombre] += (sesion.fin - sesion.inicio) / 60

        total = len(self.solicitudes)
        if total > 0:
            porcentaje = round(100 * asignadas / total, 1)
        else:
            porcentaje = 0.0

        return {"total": total, "asignadas": asignadas, "en_espera": en_espera,
                "pendientes": pendientes, "porcentaje": porcentaje,
                "por_materia": por_materia, "horas_monitor": horas_monitor,
                "detalle_en_espera": detalle_en_espera}

    def mostrar_informe(self):
        """devuelve el informe como texto para imprimir."""
        r = self.informe_cobertura()
        lineas = [f"solicitudes: {r['total']} | asignadas: {r['asignadas']} | "
                  f"en espera: {r['en_espera']} | cobertura: {r['porcentaje']}%"]
        for materia, (total, atendidas) in r["por_materia"].items():
            lineas.append(f"  - {materia}: {atendidas}/{total} atendidas")
        for monitor, horas in r["horas_monitor"].items():
            lineas.append(f"  - monitor {monitor}: {horas:.1f} h agendadas")
        for id, estudiante, materia, motivo in r["detalle_en_espera"]:
            lineas.append(f"  ! solicitud {id} ({estudiante}, {materia}): {motivo}")
        return "\n".join(lineas)


# =====================================================================
# ejemplo de uso: se ejecuta con "python codigo_completo_recursion.py"
# =====================================================================
if __name__ == "__main__":
    s = sistema_monitorias()

    # materias y monitores
    calc = s.registrar_materia("calculo i", "matematicas", 1, 4)
    prog = s.registrar_materia("programacion i", "sistemas", 1, 3)
    est_d = s.registrar_materia("estructuras de datos", "sistemas", 3, 5)
    s.registrar_monitor("carlos", 6, [calc.codigo, prog.codigo],
                        [("lunes", "08:00", "12:00"), ("martes", "14:00", "18:00")])
    s.registrar_monitor("diana", 7, [est_d.codigo], [("miercoles", "10:00", "14:00")])

    # estudiantes y solicitudes
    ana = s.registrar_estudiante("ana", 2, "ing. sistemas", [("lunes", "08:00", "10:00")])
    luis = s.registrar_estudiante("luis", 2, "ing. sistemas", [("lunes", "08:00", "12:00")])
    s.solicitar(ana.codigo, calc.codigo, tipo_monitoria.par, 1)
    s.solicitar(luis.codigo, prog.codigo, tipo_monitoria.puntual, 4)
    fis = s.registrar_materia("fisica i", "ciencias", 1, 3)
    sara = s.registrar_estudiante("sara", 2, "ing. sistemas", [("lunes", "10:00", "12:00")])
    s.solicitar(sara.codigo, fis.codigo, tipo_monitoria.puntual, 2)    # todavia no hay monitor de fisica

    s.generar_agenda()
    print(s.agenda.mostrar())
    print(s.mostrar_informe())
    print(s.buscar(ana.codigo))
    print("\nen espera:", [(x.estudiante.nombre, x.motivo) for x in s.lista_espera.pendientes()])

    # al llegar un monitor de fisica, sara sale de la lista de espera sola
    s.registrar_monitor("hugo", 5, [fis.codigo], [("lunes", "10:00", "12:00")])
    print("tras registrar monitor de fisica:")
    print(s.agenda.mostrar())
    print(s.mostrar_informe())

    # prerrequisitos (recursion y backtracking)
    print("\n--- prerrequisitos ---")
    calc2 = s.registrar_materia("calculo ii", "matematicas", 2, 4)
    fis2 = s.registrar_materia("fisica ii", "ciencias", 3, 4)
    s.agregar_prerrequisito(calc2.codigo, calc.codigo)    # calculo ii necesita calculo i
    s.agregar_prerrequisito(fis2.codigo, fis.codigo)      # fisica ii necesita fisica i
    s.agregar_prerrequisito(fis2.codigo, calc2.codigo)    # fisica ii necesita calculo ii
    print("cadena de fisica ii:", s.cadena_de(fis2.codigo))
    for ruta in s.rutas_de(fis2.codigo):
        print("  ruta:", " -> ".join(ruta))
    s.registrar_cursada(ana.codigo, calc.codigo)
    print("a ana le faltan para fisica ii:", s.faltantes_de(ana.codigo, fis2.codigo))
    try:
        s.agregar_prerrequisito(calc.codigo, fis2.codigo)  # formaria un ciclo
    except error_validacion as e:
        print("rechazado:", e)

    # listados ordenados (insertion, merge y quick sort)
    print("\n--- listados ordenados ---")
    eva = s.registrar_estudiante("eva", 4, "ing. sistemas", [("miercoles", "10:00", "12:00")])
    beto = s.registrar_estudiante("beto", 2, "ing. sistemas", [("lunes", "08:00", "09:00")])
    s.solicitar(eva.codigo, est_d.codigo, tipo_monitoria.general, 3)
    s.solicitar(beto.codigo, calc.codigo, tipo_monitoria.puntual, 5)
    for criterio in ["urgencia", "antiguedad", "materia"]:
        print("\npor", criterio, "(insercion):")
        print(s.mostrar_listado(criterio, "insercion"))
    print("\nsolo las pendientes por urgencia (mezcla):")
    print(s.mostrar_listado("urgencia", "mezcla", "pendiente"))
    iguales = True
    for criterio in claves:
        a = [x.id for x in s.listar_solicitudes(criterio, "insercion")]
        b = [x.id for x in s.listar_solicitudes(criterio, "mezcla")]
        c = [x.id for x in s.listar_solicitudes(criterio, "rapido")]
        if not (a == b == c):
            iguales = False
    print("\nlos tres metodos dan el mismo orden:", iguales)

    # pila, revertir la ultima asignacion 
    print("\n--- revertir la ultima asignacion ---")
    s.generar_agenda()
    print("historial (la mas reciente primero):")
    print(s.mostrar_historial())
    for _ in range(2):
        s_rev = s.revertir_ultima_asignacion()
        print("\nrevertida #" + str(s_rev.id), s_rev.estudiante.nombre, "->", s_rev.estado + ":", s_rev.motivo)
    print("\nagenda despues de revertir:")
    print(s.agenda.mostrar())
    print("en espera:", [(x.estudiante.nombre, x.motivo) for x in s.lista_espera.pendientes()])
    while not s.historial.esta_vacia():
        s.revertir_ultima_asignacion()
    try:
        s.revertir_ultima_asignacion()
    except error_validacion as e:
        print("rechazado:", e)

    # conjuntos y mapas 
    print("\n--- areas sin repeticion ---")
    s.registrar_materia("etica", "humanidades", 1, 2)    # un area que ningun monitor cubre
    s.registrar_materia("algebra lineal", "matematicas", 2, 3)    # area que ya existe: no se repite
    print("materias registradas:", len(s.materias), "| areas distintas:", len(s.areas_del_sistema()))
    print("areas del sistema:", ordenar_mezcla(s.areas_del_sistema().elementos(), clave_texto))
    carlos = s.personas.obtener("m-0001")
    print("areas de carlos:", ordenar_mezcla(s.areas_de_monitor(carlos.codigo).elementos(), clave_texto))
    print("areas sin monitor:", s.areas_sin_monitor().elementos())
    print(s.mostrar_areas())

    print("\n--- materias ya cursadas ---")
    print("registrar programacion i:", s.registrar_cursada(ana.codigo, prog.codigo))
    print("registrarla otra vez:", s.registrar_cursada(ana.codigo, prog.codigo))
    print("ana ya curso:", s.materias_cursadas(ana.codigo))
    print("areas cursadas por ana:", ordenar_mezcla(s.areas_cursadas(ana.codigo).elementos(), clave_texto))
    print("ana ya curso fisica i?", s.ha_cursado(ana.codigo, fis.codigo))
    print("a ana le faltan para fisica ii:", s.faltantes_de(ana.codigo, fis2.codigo))