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