from .errores import error_validacion


class tabla_hash:

    def __init__(self):
        self.cubetas = [[] for _ in range(16)]
        self.cantidad = 0

    def calcular_hash(self, clave):
        numero = 0
        for letra in clave:
            numero = (numero * 31 + ord(letra)) % 2147483647
        return numero

    def revisar(self, clave):
        if not isinstance(clave, str):
            raise error_validacion("la clave de la tabla debe ser texto")

    def buscar_cubeta(self, clave):
        self.revisar(clave)
        return self.cubetas[self.calcular_hash(clave) % len(self.cubetas)]

    def buscar_par(self, clave):
        for par in self.buscar_cubeta(clave):
            if par[0] == clave:
                return par
        return None

    def pasos(self, clave):
        comparaciones = 0
        for par in self.buscar_cubeta(clave):
            comparaciones += 1
            if par[0] == clave:
                return comparaciones
        return comparaciones

    def poner(self, clave, valor):
        par = self.buscar_par(clave)
        if par is not None:
            par[1] = valor
            return
        self.buscar_cubeta(clave).append([clave, valor])
        self.cantidad += 1
        if self.cantidad > 0.75 * len(self.cubetas):
            self.agrandar()

    def obtener(self, clave, defecto=None):
        par = self.buscar_par(clave)
        if par is None:
            return defecto
        return par[1]

    def contiene(self, clave):
        return self.buscar_par(clave) is not None

    def eliminar(self, clave):
        cubeta = self.buscar_cubeta(clave)
        for posicion in range(len(cubeta)):
            if cubeta[posicion][0] == clave:
                cubeta.pop(posicion)
                self.cantidad -= 1
                return True
        return False

    def items(self):
        lista = []
        for cubeta in self.cubetas:
            for par in cubeta:
                lista.append((par[0], par[1]))
        return lista

    def claves(self):
        return [clave for clave, valor in self.items()]

    def valores(self):
        return [valor for clave, valor in self.items()]

    def agrandar(self):
        viejas = self.cubetas
        self.cubetas = [[] for _ in range(len(viejas) * 2)]
        self.cantidad = 0
        for cubeta in viejas:
            for par in cubeta:
                self.poner(par[0], par[1])

    def __len__(self):
        return self.cantidad
