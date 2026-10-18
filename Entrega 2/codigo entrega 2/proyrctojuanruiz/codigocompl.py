
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
# parte 5 - sistema principal
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
# ejemplo de uso: se ejecuta con "python monitorias.py"
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