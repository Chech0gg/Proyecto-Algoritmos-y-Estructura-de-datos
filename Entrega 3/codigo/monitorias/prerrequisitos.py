from .errores import error_validacion
from .grafos import grafo_dirigido


class mapa_prerrequisitos:

    def __init__(self):
        self.grafo = grafo_dirigido()
        self.memoria_profundidad = {}

    def agregar_materia(self, codigo):
        self.grafo.agregar_vertice(codigo)

    def directos(self, materia):
        if materia not in self.grafo.posicion:
            return []
        indice = self.grafo.posicion[materia]
        return [self.grafo.etiquetas[p] for p in self.grafo.predecesores[indice]]

    def agregar(self, materia, requisito):
        u = self.grafo.vertice(materia)
        v = self.grafo.vertice(requisito)
        if u == v:
            raise error_validacion(materia + " no puede ser prerrequisito de si misma")
        if requisito in self.directos(materia):
            raise error_validacion(materia + " ya tiene a " + requisito + " como prerrequisito")
        if self.grafo.alcanzable(u, v):
            raise error_validacion("ciclo: " + requisito + " ya depende de " + materia)
        self.grafo.agregar_arista(requisito, materia)
        self.memoria_profundidad = {}

    def cadena(self, materia, orden=None):
        if orden is None:
            orden = []
        for requisito in self.directos(materia):
            if requisito not in orden:
                self.cadena(requisito, orden)
                orden.append(requisito)
        return orden

    def profundidad(self, materia):
        if materia in self.memoria_profundidad:
            return self.memoria_profundidad[materia]
        mayor = -1
        for requisito in self.directos(materia):
            mayor = max(mayor, self.profundidad(requisito))
        self.memoria_profundidad[materia] = 1 + mayor
        return 1 + mayor

    def rutas(self, materia):
        resultado = []
        self.explorar(materia, [materia], resultado)
        return resultado

    def explorar(self, materia, camino, resultado):
        requisitos = self.directos(materia)
        if len(requisitos) == 0:
            resultado.append(list(camino))
            return
        for requisito in requisitos:
            camino.append(requisito)
            self.explorar(requisito, camino, resultado)
            camino.pop()

    def faltantes(self, materia, cursadas):
        return [r for r in self.cadena(materia) if not cursadas.contiene(r)]

    def faltantes_directos(self, materia, cursadas):
        return [r for r in self.directos(materia) if not cursadas.contiene(r)]

    def dependientes(self, materia):
        return self.grafo.descendientes(materia)

    def maximo_dependientes(self):
        conteos = self.grafo.conteo_dependientes()
        if len(conteos) == 0:
            return 0
        return max(conteos.values())
