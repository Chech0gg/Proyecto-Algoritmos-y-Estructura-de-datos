from .errores import error_validacion


class clase_nodo:

    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None


class pila:

    def __init__(self):
        self.tope = None
        self.cantidad = 0

    def apilar(self, dato):
        nodo = clase_nodo(dato)
        nodo.siguiente = self.tope
        self.tope = nodo
        self.cantidad += 1

    def desapilar(self):
        if self.tope is None:
            raise error_validacion("la pila esta vacia")
        dato = self.tope.dato
        self.tope = self.tope.siguiente
        self.cantidad -= 1
        return dato

    def ver_tope(self):
        if self.tope is None:
            return None
        return self.tope.dato

    def esta_vacia(self):
        return self.cantidad == 0

    def como_lista(self):
        lista = []
        actual = self.tope
        while actual is not None:
            lista.append(actual.dato)
            actual = actual.siguiente
        return lista

    def __len__(self):
        return self.cantidad


class cola:

    def __init__(self):
        self.frente = None
        self.final = None
        self.cantidad = 0

    def encolar(self, dato):
        nodo = clase_nodo(dato)
        if self.final is None:
            self.frente = nodo
        else:
            self.final.siguiente = nodo
        self.final = nodo
        self.cantidad += 1

    def desencolar(self):
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
        lista = []
        actual = self.frente
        while actual is not None:
            lista.append(actual.dato)
            actual = actual.siguiente
        return lista

    def __len__(self):
        return self.cantidad
