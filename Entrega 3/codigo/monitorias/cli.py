import os
import re
import sys

from . import persistencia
from .datos_demo import cargar_demo
from .errores import error_validacion
from .modelos import clase_estudiante, clase_monitor
from .sistema import sistema_monitorias
from .tiempo import crear_bloque, duracion_min

archivo_por_defecto = "monitorias.json"

menu = [
    ("registrar materia", "registrar_materia"),
    ("agregar prerrequisito", "agregar_prerrequisito"),
    ("registrar estudiante", "registrar_estudiante"),
    ("registrar monitor", "registrar_monitor"),
    ("registrar materia ya cursada", "registrar_cursada"),
    ("solicitar monitoria", "solicitar"),
    ("generar agenda", "generar_agenda"),
    ("ver agenda", "ver_agenda"),
    ("ver cola y lista de espera", "ver_cola"),
    ("listar solicitudes ordenadas", "listar"),
    ("revertir ultima asignacion", "revertir"),
    ("volver a intentar una solicitud revertida", "reencolar"),
    ("informe de cobertura", "informe"),
    ("buscar por codigo (hash frente a avl)", "buscar"),
    ("solicitudes por rango de urgencia", "rango_urgencia"),
    ("catalogo de materias (arbol)", "catalogo"),
    ("red de prerrequisitos (grafo)", "red"),
    ("ruta entre dos materias", "ruta"),
    ("impacto de reprobar una materia", "impacto"),
    ("plan de cursado de un estudiante", "plan"),
    ("areas y monitores", "areas"),
    ("cargar datos de demostracion", "demo"),
    ("guardar en archivo", "guardar"),
    ("cargar desde archivo", "cargar"),
    ("ver notificaciones pendientes", "notificaciones"),
]


class consola:

    def __init__(self, sistema=None, entrada=None, salida=None, archivo=archivo_por_defecto):
        self.sistema = sistema if sistema is not None else sistema_monitorias()
        self.entrada = entrada if entrada is not None else input
        self.salida = salida if salida is not None else print
        self.archivo = archivo

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

    def leer_bloques(self, mensaje):
        bloques = []
        self.decir(mensaje + " (formato: dia hh:mm hh:mm, enter para terminar)")
        while True:
            texto = self.preguntar("  bloque:")
            if texto == "":
                return bloques
            partes = texto.split()
            if len(partes) != 3:
                self.decir("  use el formato: lunes 08:00 10:00")
                continue
            try:
                crear_bloque(partes[0], partes[1], partes[2])
            except error_validacion as problema:
                self.decir("  " + str(problema))
                continue
            bloques.append((partes[0], partes[1], partes[2]))

    def elegir(self, titulo, plural, objetos, descripcion):
        if len(objetos) == 0:
            raise error_validacion("no hay " + plural + " registrados")
        for objeto in objetos:
            self.decir(f"  {objeto.codigo}  {descripcion(objeto)}")
        codigos = [o.codigo for o in objetos]
        while True:
            texto = self.preguntar("codigo de " + titulo + ":")
            if texto in codigos:
                return texto
            self.decir("  codigo no valido")

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

    def registrar_estudiante(self):
        nombre = self.leer_texto("nombre:")
        semestre = self.leer_entero("semestre", 1, 12)
        carrera = self.leer_texto("carrera:")
        bloques = self.leer_bloques("disponibilidad del estudiante")
        estudiante = self.sistema.registrar_estudiante(nombre, semestre, carrera, bloques)
        self.decir("estudiante registrado con codigo " + estudiante.codigo)

    def registrar_monitor(self):
        nombre = self.leer_texto("nombre:")
        semestre = self.leer_entero("semestre", 1, 12)
        self.decir("materias que apoya (escriba un codigo por vez, enter para terminar):")
        materias = []
        for materia in self.sistema.indice_materias.valores():
            self.decir(f"  {materia.codigo}  {materia.nombre}")
        while True:
            codigo = self.preguntar("  codigo de materia:")
            if codigo == "":
                break
            if self.sistema.materias.contiene(codigo):
                materias.append(codigo)
            else:
                self.decir("  codigo no valido")
        bloques = self.leer_bloques("disponibilidad del monitor")
        monitor = self.sistema.registrar_monitor(nombre, semestre, materias, bloques)
        self.decir("monitor registrado con codigo " + monitor.codigo)

    def registrar_cursada(self):
        estudiante = self.elegir_estudiante()
        materia = self.elegir_materia()
        nueva = self.sistema.registrar_cursada(estudiante, materia)
        self.decir("registrada" if nueva else "ya estaba registrada")

    def solicitar(self):
        estudiante = self.elegir_estudiante()
        materia = self.elegir_materia()
        tipo = self.leer_opcion("tipo de monitoria", list(duracion_min))
        nota = self.leer_decimal("nota actual en la materia", 0, 5, opcional=True)
        solicitud = self.sistema.solicitar(estudiante, materia, tipo, nota)
        self.decir(f"solicitud #{solicitud.id} creada: prioridad {solicitud.prioridad}")
        self.decir("  " + solicitud.desglose)

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
        self.decir("cargado desde " + self.archivo)

    def notificaciones(self):
        mensajes = self.sistema.entregar_notificaciones()
        if len(mensajes) == 0:
            self.decir("no hay notificaciones pendientes")
        for mensaje in mensajes:
            self.decir("  " + mensaje)

    def mostrar_menu(self):
        self.decir("")
        self.decir("=== sistema de monitorias ===")
        for numero, (titulo, nombre) in enumerate(menu, 1):
            self.decir(f"{numero:>2}. {titulo}")
        self.decir(" 0. salir")

    def ejecutar(self):
        while True:
            self.mostrar_menu()
            try:
                texto = self.preguntar("opcion:")
            except EOFError:
                return
            if texto == "0":
                self.decir("hasta luego")
                return
            if not re.fullmatch(r"\d+", texto) or not 1 <= int(texto) <= len(menu):
                self.decir("opcion no valida")
                continue
            try:
                getattr(self, menu[int(texto) - 1][1])()
            except error_validacion as problema:
                self.decir("error: " + str(problema))
            except EOFError:
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
    app = consola(sistema, archivo=archivo)
    if demo and len(app.sistema.materias) == 0:
        cargar_demo(app.sistema)
    app.ejecutar()
