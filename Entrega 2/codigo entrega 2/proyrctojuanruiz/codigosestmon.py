class tabla_hash:
    """funciona como un diccionario hecho a mano.
 
    tiene varias "cubetas" (listas). a cada clave se le calcula un numero
    y ese numero dice en que cubeta guardarla. asi, para buscar, solo hay
    que mirar una cubeta y no toda la tabla.
    si se llena mucho, se duplica la cantidad de cubetas."""
 
    def __init__(self):
        self.cubetas = []
        for i in range(16):
            self.cubetas.append([])
        self.cantidad = 0
 
    def calcular_hash(self, clave):
        """convierte un texto en un numero, mezclando el valor de cada letra."""
        numero = 0
        for letra in clave:
            numero = (numero * 31 + ord(letra)) % 2147483647
        return numero
 
    def buscar_cubeta(self, clave):
        """devuelve la cubeta donde deberia estar la clave."""
        posicion = self.calcular_hash(clave) % len(self.cubetas)
        return self.cubetas[posicion]
 
    def poner(self, clave, valor):
        """guarda un valor. si la clave ya existia, lo reemplaza."""
        cubeta = self.buscar_cubeta(clave)
        for par in cubeta:
            if par[0] == clave:
                par[1] = valor
                return
        cubeta.append([clave, valor])
        self.cantidad += 1
        if self.cantidad > 0.75 * len(self.cubetas):
            self.agrandar()
 
    def obtener(self, clave):
        """devuelve el valor de la clave, o nada si no existe."""
        for par in self.buscar_cubeta(clave):
            if par[0] == clave:
                return par[1]
        return None
 
    def contiene(self, clave):
        """dice si la clave existe."""
        return self.obtener(clave) is not None
 
    def valores(self):
        """devuelve una lista con todos los valores guardados."""
        lista = []
        for cubeta in self.cubetas:
            for par in cubeta:
                lista.append(par[1])
        return lista
 
    def agrandar(self):
        """duplica las cubetas y vuelve a guardar todo en su nueva posicion."""
        viejas = self.cubetas
        self.cubetas = []
        for i in range(len(viejas) * 2):
            self.cubetas.append([])
        self.cantidad = 0
        for cubeta in viejas:
            for par in cubeta:
                self.poner(par[0], par[1])
 
    def __len__(self):
        return self.cantidad
 
 
class generador_codigos:
    """crea codigos unicos como e-0001 (estudiante), m-0001 (monitor),
    p-0001 (profesor) y mat-0001 (materia). cada prefijo lleva su propia cuenta."""
 
    def __init__(self):
        self.contadores = {}
 
    def nuevo(self, prefijo):
        if prefijo not in self.contadores:
            self.contadores[prefijo] = 0
        self.contadores[prefijo] += 1
        return prefijo + "-" + f"{self.contadores[prefijo]:04d}"