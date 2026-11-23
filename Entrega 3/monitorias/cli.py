import getpass
import os
import re
import sys

from . import persistencia
from .cuentas import rol_administrador, rol_estudiante, rol_monitor, revisar_clave
from .datos_demo import cargar_demo
from .errores import error_validacion
from .modelos import clase_estudiante, clase_monitor
from .sistema import sistema_monitorias
from .tiempo import crear_bloque, duracion_min

archivo_por_defecto = "monitorias.json"

menu_estudiante = [
    ("mis monitorias", [
        ("pedir una monitoria", "solicitar_propia"),
        ("ver mis solicitudes y su estado", "mis_solicitudes"),
        ("cancelar una solicitud", "cancelar_propia"),
        ("ver mi agenda de monitorias", "mi_agenda"),
    ]),
    ("mis horarios", [
        ("agregar horarios en los que puedo asistir", "agregar_mi_horario"),
        ("ver mis horarios", "ver_mi_horario"),
        ("quitar un horario", "quitar_mi_horario"),
    ]),
    ("consultas", [
        ("ver las materias y sus monitores", "materias_y_monitores"),
        ("ver que prerrequisitos me faltan para una materia", "plan_propio"),
    ]),
    ("mi cuenta", [
        ("cambiar mi contrasena", "cambiar_clave"),
    ]),
]

menu_monitor = [
    ("mis horarios libres", [
        ("agregar horarios libres", "agregar_mi_horario"),
        ("ver mis horarios libres", "ver_mi_horario"),
        ("quitar un horario", "quitar_mi_horario"),
    ]),
    ("en que me especializo", [
        ("agregar una materia que apoyo", "agregar_mi_especialidad"),
        ("ver las materias que apoyo", "ver_mis_especialidades"),
        ("quitar una materia", "quitar_mi_especialidad"),
    ]),
    ("mis monitorias", [
        ("ver mis sesiones agendadas", "mi_agenda"),
    ]),
    ("mi cuenta", [
        ("cambiar mi contrasena", "cambiar_clave"),
    ]),
]

menu_administrador = [
    ("agenda y horarios", [
        ("generar la agenda automaticamente", "generar_agenda"),
        ("ver la agenda completa", "ver_agenda"),
        ("agendar una monitoria a mano", "agendar_manual"),
        ("modificar una sesion (dia, hora o monitor)", "modificar_sesion"),
        ("cancelar una sesion", "cancelar_sesion"),
        ("ver los horarios libres de los monitores", "horarios_monitores"),
        ("ver los horarios de los estudiantes", "horarios_estudiantes"),
        ("agregar un horario a un monitor o estudiante", "agregar_horario_de"),
        ("quitar un horario a un monitor o estudiante", "quitar_horario_de"),
    ]),
    ("solicitudes", [
        ("ver cola y lista de espera", "ver_cola"),
        ("listar solicitudes ordenadas", "listar"),
        ("solicitudes por rango de urgencia", "rango_urgencia"),
        ("cancelar una solicitud", "cancelar_solicitud_admin"),
        ("revertir ultima asignacion", "revertir"),
        ("volver a intentar una solicitud revertida", "reencolar"),
        ("ver notificaciones pendientes", "notificaciones"),
    ]),
    ("usuarios", [
        ("crear cuenta de estudiante", "crear_estudiante"),
        ("crear cuenta de monitor", "crear_monitor"),
        ("crear cuenta de administrador", "crear_administrador"),
        ("ver usuarios", "ver_usuarios"),
        ("desbloquear una cuenta", "desbloquear"),
        ("restablecer la contrasena de un usuario", "restablecer_clave"),
    ]),
    ("materias y malla curricular", [
        ("registrar materia", "registrar_materia"),
        ("agregar prerrequisito", "agregar_prerrequisito"),
        ("registrar materia ya cursada", "registrar_cursada"),
        ("catalogo de materias (arbol)", "catalogo"),
        ("red de prerrequisitos (grafo)", "red"),
        ("ruta entre dos materias", "ruta"),
        ("impacto de reprobar una materia", "impacto"),
        ("plan de cursado de un estudiante", "plan"),
        ("areas y monitores", "areas"),
    ]),
    ("informes y datos", [
        ("informe de cobertura", "informe"),
        ("buscar por codigo (hash frente a avl)", "buscar"),
        ("cargar datos de demostracion", "demo"),
        ("guardar en archivo", "guardar"),
        ("cargar desde archivo", "cargar"),
        ("cambiar mi contrasena", "cambiar_clave"),
    ]),
]

menus = {rol_estudiante: menu_estudiante, rol_monitor: menu_monitor, rol_administrador: menu_administrador}


def aplanar(menu):
    return [opcion for titulo, opciones in menu for opcion in opciones]


class consola:

    def __init__(self, sistema=None, entrada=None, salida=None, archivo=archivo_por_defecto,
                 entrada_clave=None, autoguardar=False, pista_demo=False):
        self.sistema = sistema if sistema is not None else sistema_monitorias()
        self.entrada = entrada if entrada is not None else input
        self.salida = salida if salida is not None else print
        if entrada_clave is not None:
            self.entrada_clave = entrada_clave
        elif entrada is not None:
            self.entrada_clave = entrada
        else:
            self.entrada_clave = getpass.getpass
        self.archivo = archivo
        self.autoguardar = autoguardar
        self.pista_demo = pista_demo
        self.cuenta = None

    def decir(self, texto):
        self.salida(texto)

    def preguntar(self, mensaje):
        return self.entrada(mensaje + " ").strip()

    def leer_texto(self, mensaje):
        while True:
            texto = self.preguntar(mensaje)
            if texto != "":
                return texto
            self.decir("  no puede estar vacio")

    def leer_entero(self, mensaje, minimo, maximo):
        while True:
            texto = self.preguntar(f"{mensaje} ({minimo}-{maximo}):")
            if re.fullmatch(r"-?\d+", texto) and minimo <= int(texto) <= maximo:
                return int(texto)
            self.decir(f"  escriba un numero entero entre {minimo} y {maximo}")

    def leer_decimal(self, mensaje, minimo, maximo, opcional=False):
        sufijo = ", enter para omitir" if opcional else ""
        while True:
            texto = self.preguntar(f"{mensaje} ({minimo}-{maximo}{sufijo}):").replace(",", ".")
            if opcional and texto == "":
                return None
            if re.fullmatch(r"-?\d+(\.\d+)?", texto) and minimo <= float(texto) <= maximo:
                return float(texto)
            self.decir(f"  escriba un numero entre {minimo} y {maximo} (puede usar coma o punto)")

    def leer_opcion(self, mensaje, opciones):
        while True:
            texto = self.preguntar(f"{mensaje} ({'/'.join(opciones)}):").lower()
            if texto in opciones:
                return texto
            self.decir("  opcion no valida")

    def leer_bloque(self):
        """Pide un horario. Devuelve None si la persona quiere terminar (enter, 0 o salir)."""
        while True:
            texto = self.preguntar("  horario (o 0 / enter para salir):")
            if texto.lower() in ("", "0", "salir", "listo", "fin"):
                return None
            partes = texto.split()
            if len(partes) != 3:
                self.decir("  use el formato: lunes 08:00 10:00   (o escriba 0 para salir)")
                continue
            try:
                crear_bloque(partes[0], partes[1], partes[2])
            except error_validacion as problema:
                self.decir("  " + str(problema))
                continue
            return (partes[0], partes[1], partes[2])

    def leer_bloques(self, mensaje):
        bloques = []
        self.decir(mensaje + " (formato: dia hh:mm hh:mm; escriba 0 o enter para terminar)")
        while True:
            bloque = self.leer_bloque()
            if bloque is None:
                return bloques
            bloques.append(bloque)

    def elegir(self, titulo, plural, objetos, descripcion):
        if len(objetos) == 0:
            raise error_validacion("no hay " + plural + " registrados")
        for posicion, objeto in enumerate(objetos, 1):
            self.decir(f"  {posicion:>2}. {objeto.codigo}  {descripcion(objeto)}")
        codigos = [o.codigo for o in objetos]
        while True:
            texto = self.preguntar("numero o codigo de " + titulo + ":")
            if texto in codigos:
                return texto
            if texto.isdecimal() and 1 <= int(texto) <= len(codigos):
                return codigos[int(texto) - 1]
            self.decir("  opcion no valida")

    def elegir_materia(self):
        return self.elegir("materia", "materias", self.sistema.indice_materias.valores(), lambda m: f"{m.nombre} (nivel {m.nivel})")

    def elegir_estudiante(self):
        estudiantes = [p for p in self.sistema.indice_personas.valores() if isinstance(p, clase_estudiante)]
        return self.elegir("estudiante", "estudiantes", estudiantes, lambda e: f"{e.nombre} (semestre {e.semestre})")

    def elegir_monitor(self):
        monitores = [p for p in self.sistema.indice_personas.valores() if isinstance(p, clase_monitor)]
        return self.elegir("monitor", "monitores", monitores, lambda m: m.nombre)

    def registrar_materia(self):
        nombre = self.leer_texto("nombre de la materia:")
        area = self.leer_texto("area:")
        nivel = self.leer_entero("nivel", 1, 12)
        dificultad = self.leer_entero("dificultad", 1, 5)
        tasa = self.leer_decimal("tasa historica de reprobacion", 0, 1, opcional=True)
        materia = self.sistema.registrar_materia(nombre, area, nivel, dificultad, tasa)
        self.decir("materia registrada con codigo " + materia.codigo)

    def agregar_prerrequisito(self):
        self.decir("materia que tiene el prerrequisito:")
        materia = self.elegir_materia()
        self.decir("materia que es prerrequisito:")
        requisito = self.elegir_materia()
        self.sistema.agregar_prerrequisito(materia, requisito)
        self.decir("prerrequisito agregado")

    def registrar_cursada(self):
        estudiante = self.elegir_estudiante()
        materia = self.elegir_materia()
        nueva = self.sistema.registrar_cursada(estudiante, materia)
        self.decir("registrada" if nueva else "ya estaba registrada")

    def generar_agenda(self):
        self.sistema.generar_agenda()
        self.decir(self.sistema.agenda.mostrar())
        self.decir(self.sistema.mostrar_informe())

    def ver_agenda(self):
        self.decir(self.sistema.agenda.mostrar())

    def ver_cola(self):
        self.decir(self.sistema.mostrar_cola())

    def listar(self):
        criterio = self.leer_opcion("criterio", ["urgencia", "antiguedad", "materia"])
        metodo = self.leer_opcion("metodo de ordenamiento", ["auto", "insercion", "mezcla", "rapido"])
        self.decir(self.sistema.mostrar_listado(criterio, metodo))

    def revertir(self):
        solicitud = self.sistema.revertir_ultima_asignacion()
        self.decir(f"revertida la solicitud #{solicitud.id} de {solicitud.estudiante.nombre}")

    def reencolar(self):
        numero = self.leer_entero("numero de solicitud", 1, 1000000)
        solicitud = self.sistema.reencolar(numero)
        self.decir(f"solicitud #{solicitud.id}: {solicitud.estado} ({solicitud.motivo})")

    def informe(self):
        self.decir(self.sistema.mostrar_informe())

    def buscar(self):
        codigo = self.leer_texto("codigo a buscar:")
        info = self.sistema.buscar_con_comparaciones(codigo)
        if info["objeto"] is None:
            self.decir("no existe ese codigo")
        else:
            self.decir(str(getattr(info["objeto"], "nombre", info["objeto"])))
        self.decir(f"  avl: {info['comparaciones_avl']} comparaciones (altura {info['altura_avl']}, "
                   f"{info['total_registros']} registros)")
        self.decir(f"  tabla hash: {info['pasos_hash']} comparaciones dentro de la cubeta")

    def rango_urgencia(self):
        minimo = self.leer_decimal("urgencia minima", 0, 1)
        maximo = self.leer_decimal("urgencia maxima", 0, 1)
        encontradas, visitados = self.sistema.solicitudes_por_urgencia(minimo, maximo)
        for s in encontradas:
            self.decir(f"  #{s.id} {s.estudiante.nombre} {s.materia.nombre} u={s.urgencia:.3f}")
        self.decir(f"{len(encontradas)} solicitudes; el arbol visito {visitados} de {len(self.sistema.solicitudes)} nodos")

    def catalogo(self):
        invertido = self.leer_opcion("orden", ["normal", "inverso"]) == "inverso"
        self.decir(self.sistema.mostrar_catalogo(invertido))

    def red(self):
        self.decir(self.sistema.mostrar_red())

    def ruta(self):
        self.decir("materia de origen:")
        origen = self.elegir_materia()
        self.decir("materia de destino:")
        destino = self.elegir_materia()
        r = self.sistema.ruta_entre(origen, destino)
        if r["dirigida"] is not None:
            self.decir("ruta de prerrequisitos: " + " -> ".join(r["dirigida"]))
        else:
            self.decir("no hay una ruta de prerrequisitos de la primera a la segunda")
        if r["sin_direccion"] is not None:
            self.decir(f"conexion sin importar la direccion ({len(r['sin_direccion']) - 1} pasos): "
                       + " - ".join(r["sin_direccion"]))
        else:
            self.decir("las dos materias estan en islas distintas de la malla")

    def impacto(self):
        materia = self.elegir_materia()
        olas = self.sistema.impacto_de(materia)
        if len(olas) == 1:
            self.decir("ninguna materia depende de esta")
        for i, ola in enumerate(olas[1:], 1):
            self.decir(f"  ola {i}: " + ", ".join(ola))
        self.decir(f"materias bloqueadas en total: {sum(len(o) for o in olas[1:])}")

    def plan(self):
        estudiante = self.elegir_estudiante()
        materia = self.elegir_materia()
        faltan = self.sistema.plan_para(estudiante, materia)
        if len(faltan) == 0:
            self.decir("no le falta ningun prerrequisito")
        else:
            self.decir("debe cursar, en este orden: " + " -> ".join(faltan))

    def areas(self):
        self.decir(self.sistema.mostrar_areas())
        sin = self.sistema.areas_sin_monitor().elementos()
        self.decir("areas sin monitor: " + (", ".join(sin) if len(sin) > 0 else "ninguna"))

    def demo(self):
        if len(self.sistema.materias) > 0:
            raise error_validacion("la demostracion solo se puede cargar en un sistema vacio")
        cargar_demo(self.sistema)
        self.decir("datos de demostracion cargados")

    def guardar(self):
        persistencia.guardar(self.sistema, self.archivo)
        self.decir("guardado en " + self.archivo)

    def cargar(self):
        self.sistema = persistencia.cargar(self.archivo)
        self.cuenta = None
        self.decir("cargado desde " + self.archivo + "; vuelva a iniciar sesion")

    def notificaciones(self):
        mensajes = self.sistema.entregar_notificaciones()
        if len(mensajes) == 0:
            self.decir("no hay notificaciones pendientes")
        for mensaje in mensajes:
            self.decir("  " + mensaje)

    def leer_clave(self, mensaje):
        try:
            return self.entrada_clave(mensaje + " ")
        except (getpass.GetPassWarning, OSError):
            return self.preguntar(mensaje)

    def leer_clave_nueva(self):
        while True:
            primera = self.leer_clave("contrasena (minimo 8 caracteres, sin espacios):")
            try:
                revisar_clave(primera)
            except error_validacion as problema:
                self.decir("  " + str(problema))
                continue
            if self.leer_clave("repita la contrasena:") == primera:
                return primera
            self.decir("  las contrasenas no coinciden")

    def leer_usuario_nuevo(self):
        while True:
            usuario = self.leer_texto("nombre de usuario:")
            try:
                if self.sistema.cuentas.existe(usuario):
                    self.decir("  ese usuario ya existe, elija otro")
                    continue
            except error_validacion as problema:
                self.decir("  " + str(problema))
                continue
            return usuario

    def leer_materias_apoyadas(self):
        self.decir("materias que apoya (escriba un codigo por vez, enter para terminar):")
        materias = []
        for materia in self.sistema.indice_materias.valores():
            self.decir(f"  {materia.codigo}  {materia.nombre}")
        while True:
            codigo = self.preguntar("  codigo de materia:")
            if codigo == "":
                return materias
            if self.sistema.materias.contiene(codigo):
                materias.append(codigo)
            else:
                self.decir("  codigo no valido")

    def codigo_propio(self):
        return self.cuenta.codigo_persona

    def elegir_numero(self, mensaje, minimo, maximo):
        return self.leer_entero(mensaje, minimo, maximo)

    def solicitar_propia(self):
        estudiante = self.sistema.exigir_estudiante(self.codigo_propio())
        if len(estudiante.disponibilidad) == 0:
            self.decir("aviso: todavia no tiene horarios; agreguelos (menu 'mis horarios') para que se pueda agendar")

        def descripcion(m):
            sin = "" if len(self.sistema.monitores_de(m)) > 0 else " - sin monitor por ahora"
            return f"{m.nombre} (nivel {m.nivel}){sin}"
        materia = self.elegir("materia", "materias", self.sistema.indice_materias.valores(), descripcion)
        self.decir("tipos: par (60 min, 1 estudiante), general (90 min, hasta 5), puntual (30 min, una duda)")
        tipo = self.leer_opcion("tipo de monitoria", list(duracion_min))
        nota = self.leer_decimal("nota actual en la materia", 0, 5)
        promedio = self.leer_decimal("promedio acumulado de la carrera", 0, 5)
        solicitud = self.sistema.solicitar(estudiante.codigo, materia, tipo, nota, promedio)
        self.decir(f"solicitud #{solicitud.id} creada: prioridad {solicitud.prioridad} (urgencia {solicitud.urgencia:.2f} de 1)")
        self.decir("  " + solicitud.desglose)
        self.decir("  quedo en la cola; el administrador genera la agenda o se agenda sola si hay monitor y horario")

    def mis_solicitudes(self):
        self.decir(self.sistema.mostrar_solicitudes_de(self.codigo_propio()))

    def cancelar_propia(self):
        activas = [s for s in self.sistema.solicitudes_de(self.codigo_propio()) if s.estado != "cancelada"]
        if len(activas) == 0:
            raise error_validacion("no tiene solicitudes para cancelar")
        for s in activas:
            self.decir(f"  #{s.id} {s.materia.nombre} ({s.estado})")
        numero = self.leer_entero("numero de la solicitud a cancelar", 1, 1000000)
        self.sistema.cancelar_solicitud(numero, self.codigo_propio())
        self.decir("solicitud cancelada")

    def mi_agenda(self):
        self.decir(self.sistema.mostrar_sesiones_de(self.codigo_propio()))

    def agregar_mi_horario(self):
        self.decir("horarios libres (formato: dia hh:mm hh:mm, por ejemplo lunes 08:00 10:00)")
        self.decir("cada horario se guarda apenas lo escribe; escriba 0 (o enter) para salir")
        agregados = 0
        agendadas = 0
        while True:
            bloque = self.leer_bloque()
            if bloque is None:
                break
            try:
                if self.cuenta.rol == rol_estudiante:
                    asignadas = self.sistema.agregar_disponibilidad_estudiante(self.codigo_propio(), [bloque])
                else:
                    asignadas = self.sistema.agregar_disponibilidad_monitor(self.codigo_propio(), [bloque])
            except error_validacion as problema:
                self.decir("  " + str(problema))
                continue
            agregados += 1
            agendadas += len(asignadas)
            self.guardar_automatico()
            self.decir(f"  guardado: {bloque[0]} {bloque[1]} a {bloque[2]}")
        if agregados == 0:
            self.decir("no se agrego ningun horario")
            return
        self.decir("se guardo 1 horario" if agregados == 1 else f"se guardaron {agregados} horarios")
        if agendadas > 0:
            self.decir(f"con ellos se agendaron {agendadas} solicitudes que estaban en espera")

    def ver_mi_horario(self):
        self.decir(self.sistema.mostrar_disponibilidad(self.codigo_propio()))

    def quitar_mi_horario(self):
        self.decir(self.sistema.mostrar_disponibilidad(self.codigo_propio()))
        total = len(self.sistema.persona_con_horario(self.codigo_propio()).disponibilidad)
        if total == 0:
            return
        self.sistema.quitar_disponibilidad(self.codigo_propio(), self.leer_entero("numero del horario a quitar", 1, total))
        self.decir("horario quitado")

    def materias_y_monitores(self):
        for materia in self.sistema.indice_materias.valores():
            nombres = [m.nombre for m in self.sistema.monitores_de(materia)]
            self.decir(f"  {materia.nombre:<24} nivel {materia.nivel} | monitores: " + (", ".join(nombres) if nombres else "ninguno"))

    def plan_propio(self):
        materia = self.elegir_materia()
        faltan = self.sistema.plan_para(self.codigo_propio(), materia)
        if len(faltan) == 0:
            self.decir("no le falta ningun prerrequisito")
        else:
            self.decir("debe cursar, en este orden: " + " -> ".join(faltan))

    def agregar_mi_especialidad(self):
        materia = self.elegir_materia()
        asignadas = self.sistema.agregar_especialidad(self.codigo_propio(), materia)
        self.decir("materia agregada a sus especialidades")
        if len(asignadas) > 0:
            self.decir(f"se agendaron {len(asignadas)} solicitudes que estaban en espera")

    def ver_mis_especialidades(self):
        self.decir(self.sistema.mostrar_especialidades(self.codigo_propio()))

    def quitar_mi_especialidad(self):
        monitor = self.sistema.exigir_monitor(self.codigo_propio())
        self.decir(self.sistema.mostrar_especialidades(monitor.codigo))
        codigo = self.leer_texto("codigo de la materia a quitar:")
        self.sistema.quitar_especialidad(monitor.codigo, codigo)
        self.decir("materia quitada")

    def cambiar_clave(self):
        actual = self.leer_clave("contrasena actual:")
        nueva = self.leer_clave_nueva()
        self.sistema.cuentas.cambiar_clave(self.cuenta.usuario, actual, nueva)
        self.decir("contrasena cambiada")

    def agendar_manual(self):
        self.decir(self.sistema.mostrar_cola())
        numero = self.leer_entero("numero de la solicitud a agendar", 1, 1000000)
        solicitud, comparaciones = self.sistema.buscar_solicitud(numero)
        if solicitud is None:
            raise error_validacion("no existe la solicitud " + str(numero))
        monitores = self.sistema.monitores_de(solicitud.materia)
        if len(monitores) == 0:
            raise error_validacion("ningun monitor apoya " + solicitud.materia.nombre)
        self.decir("monitores de " + solicitud.materia.nombre + ":")
        for monitor in monitores:
            self.decir(f"  {monitor.codigo} {monitor.nombre}:")
            self.decir("    " + self.sistema.mostrar_disponibilidad(monitor.codigo).replace("\n", "\n    "))
        self.decir(f"horarios de {solicitud.estudiante.nombre}:")
        self.decir("    " + self.sistema.mostrar_disponibilidad(solicitud.estudiante.codigo).replace("\n", "\n    "))
        codigo = self.leer_texto("codigo del monitor:")
        dia = self.leer_texto("dia (lunes a sabado):")
        hora = self.leer_texto("hora de inicio (hh:mm):")
        sesion = self.sistema.agendar_manual(numero, codigo, dia, hora)
        self.decir("agendada: " + self.sistema.texto_sesion(sesion))

    def modificar_sesion(self):
        self.decir(self.sistema.mostrar_agenda_numerada())
        total = len(self.sistema.agenda.sesiones)
        if total == 0:
            return
        numero = self.leer_entero("numero de la sesion", 1, total)
        dia = self.leer_texto("nuevo dia:")
        hora = self.leer_texto("nueva hora de inicio (hh:mm):")
        codigo = self.preguntar("codigo de otro monitor (enter para dejar el mismo):")
        sesion = self.sistema.modificar_sesion(numero, dia, hora, codigo if codigo != "" else None)
        self.decir("modificada: " + self.sistema.texto_sesion(sesion))

    def cancelar_sesion(self):
        self.decir(self.sistema.mostrar_agenda_numerada())
        total = len(self.sistema.agenda.sesiones)
        if total == 0:
            return
        numero = self.leer_entero("numero de la sesion a cancelar", 1, total)
        sesion = self.sistema.cancelar_sesion(numero)
        self.decir("cancelada: " + self.sistema.texto_sesion(sesion))
        self.decir("sus estudiantes quedaron en espera (use 'volver a intentar' para reagendarlos)")

    def horarios_monitores(self):
        self.decir(self.sistema.mostrar_horarios_monitores())

    def horarios_estudiantes(self):
        self.decir(self.sistema.mostrar_horarios_estudiantes())

    def elegir_persona(self):
        codigo = self.leer_texto("codigo del estudiante o monitor (e-0001, m-0001):")
        self.sistema.persona_con_horario(codigo)
        return codigo

    def agregar_horario_de(self):
        codigo = self.elegir_persona()
        bloques = self.leer_bloques("horarios a agregar")
        if len(bloques) == 0:
            self.decir("no se agrego ningun horario")
            return
        if codigo.startswith("m-"):
            asignadas = self.sistema.agregar_disponibilidad_monitor(codigo, bloques)
        else:
            asignadas = self.sistema.agregar_disponibilidad_estudiante(codigo, bloques)
        self.decir(f"se agregaron {len(bloques)} horarios; se agendaron {len(asignadas)} solicitudes en espera")

    def quitar_horario_de(self):
        codigo = self.elegir_persona()
        self.decir(self.sistema.mostrar_disponibilidad(codigo))
        total = len(self.sistema.persona_con_horario(codigo).disponibilidad)
        if total == 0:
            return
        self.sistema.quitar_disponibilidad(codigo, self.leer_entero("numero del horario a quitar", 1, total))
        self.decir("horario quitado")

    def cancelar_solicitud_admin(self):
        numero = self.leer_entero("numero de la solicitud a cancelar", 1, 1000000)
        solicitud = self.sistema.cancelar_solicitud(numero, por_administrador=True)
        self.decir(f"solicitud #{solicitud.id} de {solicitud.estudiante.nombre} cancelada")

    def crear_estudiante(self):
        nombre = self.leer_texto("nombre:")
        semestre = self.leer_entero("semestre", 1, 12)
        carrera = self.leer_texto("carrera:")
        bloques = self.leer_bloques("disponibilidad del estudiante")
        usuario = self.leer_usuario_nuevo()
        clave = self.leer_clave_nueva()
        estudiante = self.sistema.registrar_cuenta_estudiante(usuario, clave, nombre, semestre, carrera, bloques)
        self.decir(f"estudiante registrado con codigo {estudiante.codigo} y usuario {usuario}")

    def crear_monitor(self):
        nombre = self.leer_texto("nombre:")
        semestre = self.leer_entero("semestre", 1, 12)
        materias = self.leer_materias_apoyadas()
        bloques = self.leer_bloques("horarios libres del monitor")
        usuario = self.leer_usuario_nuevo()
        clave = self.leer_clave_nueva()
        monitor = self.sistema.registrar_cuenta_monitor(usuario, clave, nombre, semestre, materias, bloques)
        self.decir(f"monitor registrado con codigo {monitor.codigo} y usuario {usuario}")

    def crear_administrador(self):
        nombre = self.leer_texto("nombre:")
        usuario = self.leer_usuario_nuevo()
        clave = self.leer_clave_nueva()
        self.sistema.registrar_cuenta_administrador(usuario, clave, nombre)
        self.decir("administrador creado con el usuario " + usuario)

    def ver_usuarios(self):
        self.decir(self.sistema.mostrar_cuentas())

    def desbloquear(self):
        self.sistema.cuentas.desbloquear(self.leer_texto("usuario a desbloquear:"))
        self.decir("cuenta desbloqueada")

    def restablecer_clave(self):
        usuario = self.leer_texto("usuario:")
        if self.sistema.cuentas.obtener(usuario) is None:
            raise error_validacion("no existe el usuario '" + usuario + "'")
        self.sistema.cuentas.restablecer_clave(usuario, self.leer_clave_nueva())
        self.decir("contrasena restablecida")

    def mostrar_menu(self, menu):
        self.decir("")
        self.decir(f"=== {self.cuenta.rol}: {self.cuenta.nombre} ===")
        numero = 1
        for titulo, opciones in menu:
            self.decir(f"-- {titulo}")
            for texto, nombre in opciones:
                self.decir(f"{numero:>2}. {texto}")
                numero += 1
        self.decir(" 0. cerrar sesion")

    def sesion(self, cuenta):
        self.cuenta = cuenta
        menu = aplanar(menus[cuenta.rol])
        while True:
            self.mostrar_menu(menus[cuenta.rol])
            try:
                texto = self.preguntar("opcion:")
            except EOFError:
                return False
            if texto == "0":
                self.decir("sesion cerrada")
                self.cuenta = None
                return True
            if not re.fullmatch(r"\d+", texto) or not 1 <= int(texto) <= len(menu):
                self.decir("opcion no valida")
                continue
            try:
                getattr(self, menu[int(texto) - 1][1])()
            except error_validacion as problema:
                self.decir("error: " + str(problema))
            except EOFError:
                return False
            if self.cuenta is None:
                return True

    def guardar_automatico(self):
        if self.autoguardar:
            try:
                persistencia.guardar(self.sistema, self.archivo)
            except OSError:
                self.decir("aviso: no se pudo guardar en " + self.archivo)

    def crear_primer_administrador(self):
        self.decir("")
        self.decir("no hay usuarios todavia: cree la cuenta del primer administrador")
        nombre = self.leer_texto("nombre:")
        usuario = self.leer_usuario_nuevo()
        clave = self.leer_clave_nueva()
        self.sistema.registrar_cuenta_administrador(usuario, clave, nombre)
        self.decir("administrador creado; ahora inicie sesion")

    def registrarse(self):
        self.decir("registro de estudiante nuevo")
        nombre = self.leer_texto("nombre:")
        semestre = self.leer_entero("semestre", 1, 12)
        carrera = self.leer_texto("carrera:")
        usuario = self.leer_usuario_nuevo()
        clave = self.leer_clave_nueva()
        self.sistema.registrar_cuenta_estudiante(usuario, clave, nombre, semestre, carrera)
        self.decir("registro exitoso; agregue sus horarios dentro del menu para poder pedir monitorias")
        return self.sistema.iniciar_sesion(usuario, clave)

    def ingresar(self):
        usuario = self.preguntar("usuario:")
        clave = self.leer_clave("contrasena (no se ve lo que escribe):")
        return self.sistema.iniciar_sesion(usuario, clave)

    def ejecutar(self):
        while True:
            try:
                if len(self.sistema.cuentas) == 0:
                    self.crear_primer_administrador()
                self.decir("")
                self.decir("=== sistema de monitorias ===")
                if self.pista_demo:
                    self.decir("usuarios de demostracion (usuario / contrasena): admin / admin12345 (administrador), "
                               "carlos / carlos12345 (monitor), ana / ana12345 (estudiante)")
                self.decir(" 1. iniciar sesion")
                self.decir(" 2. registrarme como estudiante")
                self.decir(" 0. salir")
                texto = self.preguntar("opcion:")
                if texto == "0":
                    self.guardar_automatico()
                    self.decir("hasta luego")
                    return
                if texto not in ("1", "2"):
                    self.decir("opcion no valida")
                    continue
                cuenta = self.ingresar() if texto == "1" else self.registrarse()
            except error_validacion as problema:
                self.decir("error: " + str(problema))
                continue
            except EOFError:
                self.guardar_automatico()
                return
            continuar = self.sesion(cuenta)
            self.guardar_automatico()
            if not continuar:
                return


def principal(argumentos=None):
    argumentos = sys.argv[1:] if argumentos is None else argumentos
    archivo = archivo_por_defecto
    demo = False
    for argumento in argumentos:
        if argumento == "--demo":
            demo = True
        else:
            archivo = argumento
    sistema = None
    if os.path.exists(archivo):
        sistema = persistencia.cargar(archivo)
    app = consola(sistema, archivo=archivo, autoguardar=True, pista_demo=demo)
    if demo and len(app.sistema.materias) == 0:
        cargar_demo(app.sistema)
    app.ejecutar()
