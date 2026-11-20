class nodo_arbol:

    def __init__(self, nombre, tipo, codigo=""):
        self.nombre = nombre
        self.tipo = tipo
        self.codigo = codigo
        self.hijos = []

    def etiqueta(self):
        if self.codigo != "":
            return self.nombre + " [" + self.codigo + "]"
        return self.nombre


def imprimir_jerarquia(nodo, nivel=0, lineas=None):
    if lineas is None:
        lineas = []
    if nodo is None:
        return lineas
    lineas.append("  " * nivel + nodo.etiqueta())
    for hijo in nodo.hijos:
        imprimir_jerarquia(hijo, nivel + 1, lineas)
    return lineas


def copiar(nodo):
    nuevo = nodo_arbol(nodo.nombre, nodo.tipo, nodo.codigo)
    for hijo in nodo.hijos:
        nuevo.hijos.append(copiar(hijo))
    return nuevo


def espejo(nodo):
    if nodo is None:
        return
    nodo.hijos.reverse()
    for hijo in nodo.hijos:
        espejo(hijo)


def son_iguales(a, b):
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    if a.nombre != b.nombre or a.tipo != b.tipo or a.codigo != b.codigo:
        return False
    if len(a.hijos) != len(b.hijos):
        return False
    for hijo_a, hijo_b in zip(a.hijos, b.hijos):
        if not son_iguales(hijo_a, hijo_b):
            return False
    return True


class arbol_materias:

    def __init__(self, nombre="catalogo"):
        self.raiz = nodo_arbol(nombre, "catalogo")

    def buscar_area(self, area):
        for hijo in self.raiz.hijos:
            if hijo.nombre == area:
                return hijo
        return None

    def agregar_area(self, area):
        existente = self.buscar_area(area)
        if existente is not None:
            return existente
        nodo = nodo_arbol(area, "area")
        self.raiz.hijos.append(nodo)
        return nodo

    def agregar_materia(self, area, nombre, codigo):
        self.agregar_area(area).hijos.append(nodo_arbol(nombre, "materia", codigo))

    def areas(self):
        return [hijo.nombre for hijo in self.raiz.hijos]

    def materias_de_area(self, area):
        nodo = self.buscar_area(area)
        if nodo is None:
            return []
        return [hijo.nombre for hijo in nodo.hijos]

    def mostrar(self, invertido=False):
        raiz = copiar(self.raiz)
        if invertido:
            espejo(raiz)
        return "\n".join(imprimir_jerarquia(raiz))
