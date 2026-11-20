from .errores import error_validacion


class monticulo:

    def __init__(self):
        self.datos = []
        self.contador = 0

    def insertar(self, clave, dato):
        self.contador += 1
        self.datos.append((clave, self.contador, dato))
        self.subir(len(self.datos) - 1)

    def menor(self, i, j):
        return self.datos[i][:2] < self.datos[j][:2]

    def subir(self, i):
        while i > 0:
            padre = (i - 1) // 2
            if not self.menor(i, padre):
                break
            self.datos[i], self.datos[padre] = self.datos[padre], self.datos[i]
            i = padre

    def bajar(self, i):
        total = len(self.datos)
        while True:
            izquierdo = 2 * i + 1
            derecho = izquierdo + 1
            elegido = i
            if izquierdo < total and self.menor(izquierdo, elegido):
                elegido = izquierdo
            if derecho < total and self.menor(derecho, elegido):
                elegido = derecho
            if elegido == i:
                break
            self.datos[i], self.datos[elegido] = self.datos[elegido], self.datos[i]
            i = elegido

    def extraer(self):
        if len(self.datos) == 0:
            raise error_validacion("el monticulo esta vacio")
        raiz = self.datos[0]
        ultimo = self.datos.pop()
        if len(self.datos) > 0:
            self.datos[0] = ultimo
            self.bajar(0)
        return raiz[2]

    def ver_menor(self):
        if len(self.datos) == 0:
            return None
        return self.datos[0][2]

    def esta_vacio(self):
        return len(self.datos) == 0

    def como_lista(self):
        ordenados = sorted(self.datos, key=lambda x: x[:2])
        return [x[2] for x in ordenados]

    def es_valido(self):
        for i in range(1, len(self.datos)):
            if self.menor(i, (i - 1) // 2):
                return False
        return True

    def __len__(self):
        return len(self.datos)
