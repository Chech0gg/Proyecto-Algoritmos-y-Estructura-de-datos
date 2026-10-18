#recursion y backtracking
# recorrido de la cadena de prerrequisitos 
class error_validacion(Exception):
    """se lanza cuando un dato que se quiere registrar no es valido."""
 
 
class mapa_prerrequisitos:
    """guarda, para cada materia, las materias que hay que ver antes
    (sus prerrequisitos directos) y las recorre con recursion y backtracking.
 
    ejemplo: fisica 2 necesita fisica 1 y calculo 2
        requisitos = {"fisica 2": ["fisica 1", "calculo 2"], ...}"""
 
    def __init__(self):
        self.requisitos = {}    # materia -> lista de prerrequisitos directos
 
    def directos(self, materia):
        """devuelve los prerrequisitos directos (lista vacia si no tiene)."""
        if materia in self.requisitos:
            return self.requisitos[materia]
        return []
 
    # -----------------------------------------------------------------
    # backtracking 1: evitar ciclos al registrar
    # -----------------------------------------------------------------
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
        if materia not in self.requisitos:
            self.requisitos[materia] = []
        self.requisitos[materia].append(requisito)
 
    # -----------------------------------------------------------------
    # recursion: recorrer la cadena completa
    # -----------------------------------------------------------------
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
 
    # -----------------------------------------------------------------
    # backtracking 2: listar todas las rutas
    # -----------------------------------------------------------------
    def rutas(self, materia):
        """devuelve todas las rutas posibles desde la materia hasta una
        materia que no necesita nada. cada ruta es una lista."""
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
 
    def faltantes(self, materia, aprobadas):
        """prerrequisitos de la cadena que todavia no se han aprobado."""
        pendientes = []
        for requisito in self.cadena(materia):
            if requisito not in aprobadas:
                pendientes.append(requisito)
        return pendientes
 
 
# =====================================================================
# ejemplo de uso: se ejecuta con "python recursion_backtracking.py"
# usa la tabla de prerrequisitos del plan de estudios
# =====================================================================
if __name__ == "__main__":
    m = mapa_prerrequisitos()
    tabla = [
        ("calculo 2", ["calculo 1"]),
        ("calculo 3", ["calculo 2"]),
        ("fisica 1", ["calculo 1"]),
        ("fisica 2", ["fisica 1", "calculo 2"]),
        ("fisica 3", ["fisica 2", "calculo 3"]),
        ("algoritmos y estructuras de datos", ["introduccion a programacion"]),
        ("ingenieria de datos", ["algoritmos y estructuras de datos"]),
        ("analisis y diseno de algoritmos", ["algoritmos y estructuras de datos", "logica y teoria de conjuntos"]),
        ("algebra lineal", ["precalculo"]),
        ("logica para ciencias de la computacion", ["logica y teoria de conjuntos"]),
        ("ecuaciones diferenciales", ["calculo 3", "algebra lineal"]),
        ("analisis real", ["calculo 3", "logica y teoria de conjuntos"]),
        ("probabilidad 1", ["calculo 2"]),
        ("probabilidad 2", ["probabilidad 1", "calculo 3"]),
    ]
    for materia, requisitos in tabla:
        for requisito in requisitos:
            m.agregar(materia, requisito)
 
    print("cadena de fisica 3:")
    print("  ", m.cadena("fisica 3"))
    print("profundidad de fisica 3:", m.profundidad("fisica 3"))
    print("rutas de fisica 3:")
    for ruta in m.rutas("fisica 3"):
        print("  ", " -> ".join(ruta))
    print("le faltan a quien aprobo calculo 1 y calculo 2:")
    print("  ", m.faltantes("fisica 3", ["calculo 1", "calculo 2"]))
 
    # intento de ciclo: calculo 1 necesitaria fisica 3, que ya depende de calculo 1
    try:
        m.agregar("calculo 1", "fisica 3")
    except error_validacion as e:
        print("rechazado:", e)
 