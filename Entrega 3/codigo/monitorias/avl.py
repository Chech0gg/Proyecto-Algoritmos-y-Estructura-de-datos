class nodo_avl:

    def __init__(self, clave, valor):
        self.clave = clave
        self.valor = valor
        self.izq = None
        self.der = None
        self.altura = 0


def altura_de(nodo):
    if nodo is None:
        return -1
    return nodo.altura


def recalcular(nodo):
    nodo.altura = 1 + max(altura_de(nodo.izq), altura_de(nodo.der))


def factor(nodo):
    if nodo is None:
        return 0
    return altura_de(nodo.izq) - altura_de(nodo.der)


def rotar_derecha(y):
    x = y.izq
    b = x.der
    x.der = y
    y.izq = b
    recalcular(y)
    recalcular(x)
    return x


def rotar_izquierda(x):
    y = x.der
    b = y.izq
    y.izq = x
    x.der = b
    recalcular(x)
    recalcular(y)
    return y


def balancear(nodo):
    recalcular(nodo)
    f = factor(nodo)
    if f > 1:
        if factor(nodo.izq) < 0:
            nodo.izq = rotar_izquierda(nodo.izq)
        return rotar_derecha(nodo)
    if f < -1:
        if factor(nodo.der) > 0:
            nodo.der = rotar_derecha(nodo.der)
        return rotar_izquierda(nodo)
    return nodo


class indice_avl:

    def __init__(self, balanceado=True):
        self.raiz = None
        self.cantidad = 0
        self.balanceado = balanceado
        self.rotaciones = 0

    def arreglar(self, nodo):
        if not self.balanceado:
            recalcular(nodo)
            return nodo
        nuevo = balancear(nodo)
        if nuevo is not nodo:
            self.rotaciones += 1
        return nuevo

    def reparar(self, camino):
        while camino:
            nodo = camino.pop()
            nuevo = self.arreglar(nodo)
            if camino:
                padre = camino[-1]
                if padre.izq is nodo:
                    padre.izq = nuevo
                else:
                    padre.der = nuevo
            else:
                self.raiz = nuevo

    def insertar(self, clave, valor):
        camino = []
        actual = self.raiz
        while actual is not None:
            camino.append(actual)
            if clave == actual.clave:
                actual.valor = valor
                return False
            actual = actual.izq if clave < actual.clave else actual.der
        nuevo = nodo_avl(clave, valor)
        if len(camino) == 0:
            self.raiz = nuevo
        elif clave < camino[-1].clave:
            camino[-1].izq = nuevo
        else:
            camino[-1].der = nuevo
        self.cantidad += 1
        self.reparar(camino)
        return True

    def buscar(self, clave):
        actual = self.raiz
        comparaciones = 0
        while actual is not None:
            comparaciones += 1
            if clave == actual.clave:
                return actual.valor, comparaciones
            actual = actual.izq if clave < actual.clave else actual.der
        return None, comparaciones

    def contiene(self, clave):
        return self.buscar(clave)[0] is not None

    def eliminar(self, clave):
        camino = []
        actual = self.raiz
        while actual is not None and actual.clave != clave:
            camino.append(actual)
            actual = actual.izq if clave < actual.clave else actual.der
        if actual is None:
            return False
        if actual.izq is not None and actual.der is not None:
            camino.append(actual)
            sucesor = actual.der
            while sucesor.izq is not None:
                camino.append(sucesor)
                sucesor = sucesor.izq
            actual.clave = sucesor.clave
            actual.valor = sucesor.valor
            actual = sucesor
        hijo = actual.izq if actual.izq is not None else actual.der
        if len(camino) == 0:
            self.raiz = hijo
        elif camino[-1].izq is actual:
            camino[-1].izq = hijo
        else:
            camino[-1].der = hijo
        self.cantidad -= 1
        self.reparar(camino)
        return True

    def listar_ordenado(self):
        resultado = []
        pendientes = []
        actual = self.raiz
        while pendientes or actual is not None:
            while actual is not None:
                pendientes.append(actual)
                actual = actual.izq
            actual = pendientes.pop()
            resultado.append((actual.clave, actual.valor))
            actual = actual.der
        return resultado

    def claves(self):
        return [clave for clave, valor in self.listar_ordenado()]

    def valores(self):
        return [valor for clave, valor in self.listar_ordenado()]

    def en_rango(self, a, b):
        resultado = []
        visitados = 0
        pendientes = []
        actual = self.raiz
        while pendientes or actual is not None:
            while actual is not None:
                visitados += 1
                pendientes.append(actual)
                actual = actual.izq if actual.clave > a else None
            actual = pendientes.pop()
            if a <= actual.clave <= b:
                resultado.append((actual.clave, actual.valor))
            actual = actual.der if actual.clave < b else None
        return resultado, visitados

    def altura(self):
        return altura_de(self.raiz)

    def es_bst(self):
        pendientes = [(self.raiz, None, None)]
        while pendientes:
            nodo, minimo, maximo = pendientes.pop()
            if nodo is None:
                continue
            if minimo is not None and not nodo.clave > minimo:
                return False
            if maximo is not None and not nodo.clave < maximo:
                return False
            pendientes.append((nodo.izq, minimo, nodo.clave))
            pendientes.append((nodo.der, nodo.clave, maximo))
        return True

    def es_avl(self):
        if not self.es_bst():
            return False
        alturas = {}
        pendientes = [(self.raiz, False)]
        while pendientes:
            nodo, visitado = pendientes.pop()
            if nodo is None:
                continue
            if visitado:
                izquierda = alturas[id(nodo.izq)] if nodo.izq is not None else -1
                derecha = alturas[id(nodo.der)] if nodo.der is not None else -1
                if abs(izquierda - derecha) > 1:
                    return False
                alturas[id(nodo)] = 1 + max(izquierda, derecha)
                if alturas[id(nodo)] != nodo.altura:
                    return False
            else:
                pendientes.append((nodo, True))
                pendientes.append((nodo.izq, False))
                pendientes.append((nodo.der, False))
        return True

    def __len__(self):
        return self.cantidad
