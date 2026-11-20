from .tabla_hash import tabla_hash


class conjunto:

    def __init__(self, elementos=()):
        self.tabla = tabla_hash()
        for elemento in elementos:
            self.agregar(elemento)

    def agregar(self, elemento):
        era_nuevo = not self.contiene(elemento)
        self.tabla.poner(elemento, elemento)
        return era_nuevo

    def contiene(self, elemento):
        return self.tabla.contiene(elemento)

    def elementos(self):
        return self.tabla.valores()

    def union(self, otro):
        resultado = conjunto(self.elementos())
        for elemento in otro.elementos():
            resultado.agregar(elemento)
        return resultado

    def interseccion(self, otro):
        resultado = conjunto()
        for elemento in self.elementos():
            if otro.contiene(elemento):
                resultado.agregar(elemento)
        return resultado

    def diferencia(self, otro):
        resultado = conjunto()
        for elemento in self.elementos():
            if not otro.contiene(elemento):
                resultado.agregar(elemento)
        return resultado

    def __len__(self):
        return len(self.tabla)


class registro_cursadas:

    def __init__(self):
        self.por_estudiante = tabla_hash()

    def registrar(self, estudiante, materia):
        cursadas = self.por_estudiante.obtener(estudiante)
        if cursadas is None:
            cursadas = conjunto()
            self.por_estudiante.poner(estudiante, cursadas)
        return cursadas.agregar(materia)

    def de(self, estudiante):
        cursadas = self.por_estudiante.obtener(estudiante)
        if cursadas is None:
            return conjunto()
        return cursadas

    def ha_cursado(self, estudiante, materia):
        return self.de(estudiante).contiene(materia)
