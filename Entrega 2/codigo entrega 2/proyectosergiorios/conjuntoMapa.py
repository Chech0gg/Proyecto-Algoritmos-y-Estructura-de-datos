#conjuntos y mapas
#areas sin repeticion y materias ya cursadas
class tabla_hash:
    """el MAPA: funciona como un diccionario hecho a mano (clave -> valor).
    (copia de la tabla hash de la entrega 2, para que este archivo corra solo)"""
 
    def __init__(self):
        self.cubetas = []
        for i in range(16):
            self.cubetas.append([])
        self.cantidad = 0
 
    def calcular_hash(self, clave):
        numero = 0
        for letra in clave:
            numero = (numero * 31 + ord(letra)) % 2147483647
        return numero
 
    def buscar_cubeta(self, clave):
        posicion = self.calcular_hash(clave) % len(self.cubetas)
        return self.cubetas[posicion]
 
    def poner(self, clave, valor):
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
        for par in self.buscar_cubeta(clave):
            if par[0] == clave:
                return par[1]
        return None
 
    def contiene(self, clave):
        return self.obtener(clave) is not None
 
    def valores(self):
        lista = []
        for cubeta in self.cubetas:
            for par in cubeta:
                lista.append(par[1])
        return lista
 
    def agrandar(self):
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
 
 
# ---------------------------------------------------------------------
# el CONJUNTO: una coleccion sin elementos repetidos
# ---------------------------------------------------------------------
class conjunto:
    """un conjunto: agregar un elemento que ya esta no hace nada, asi que
    nunca hay repetidos. se apoya en la tabla hash: cada elemento se guarda
    como clave (y tambien como valor, para poder listarlos despues).
    los elementos deben ser textos (codigos, nombres de areas, etc.)."""
 
    def __init__(self, elementos=()):
        self.tabla = tabla_hash()
        for elemento in elementos:
            self.agregar(elemento)
 
    def agregar(self, elemento):
        """agrega el elemento. devuelve verdadero si era nuevo y falso si ya estaba."""
        era_nuevo = not self.contiene(elemento)
        self.tabla.poner(elemento, elemento)
        return era_nuevo
 
    def contiene(self, elemento):
        return self.tabla.contiene(elemento)
 
    def elementos(self):
        """lista con los elementos (sin un orden en particular)."""
        return self.tabla.valores()
 
    def union(self, otro):
        """los que estan en uno u otro conjunto."""
        resultado = conjunto(self.elementos())
        for elemento in otro.elementos():
            resultado.agregar(elemento)
        return resultado
 
    def interseccion(self, otro):
        """los que estan en los dos conjuntos."""
        resultado = conjunto()
        for elemento in self.elementos():
            if otro.contiene(elemento):
                resultado.agregar(elemento)
        return resultado
 
    def diferencia(self, otro):
        """los que estan en este conjunto pero NO en el otro."""
        resultado = conjunto()
        for elemento in self.elementos():
            if not otro.contiene(elemento):
                resultado.agregar(elemento)
        return resultado
 
    def __len__(self):
        return len(self.tabla)
 
 
# ---------------------------------------------------------------------
# conjuntos aplicados: areas sin repeticion
# ---------------------------------------------------------------------
def areas_sin_repetir(materias):
    """recibe materias (cada una con .area) y devuelve el conjunto de sus
    areas: 'sistemas' aparece una sola vez aunque haya 10 materias de sistemas."""
    areas = conjunto()
    for materia in materias:
        areas.agregar(materia.area)
    return areas
 
 
# ---------------------------------------------------------------------
# mapas aplicados: contar por area (area -> cantidad)
# ---------------------------------------------------------------------
def contar_por_area(materias):
    """devuelve un mapa area -> cuantas materias tiene."""
    conteo = tabla_hash()
    for materia in materias:
        actual = conteo.obtener(materia.area)
        if actual is None:
            actual = 0
        conteo.poner(materia.area, actual + 1)
    return conteo
 
 
# ---------------------------------------------------------------------
# mapa de conjuntos: materias ya cursadas por cada estudiante
# ---------------------------------------------------------------------
class registro_cursadas:
    """mapa: codigo de estudiante -> conjunto de codigos de materias cursadas.
    el conjunto evita que una materia se registre dos veces."""
 
    def __init__(self):
        self.por_estudiante = tabla_hash()
 
    def registrar(self, estudiante, materia):
        """anota que el estudiante cursó la materia. devuelve verdadero si
        era nueva y falso si ya estaba anotada."""
        cursadas = self.por_estudiante.obtener(estudiante)
        if cursadas is None:
            cursadas = conjunto()
            self.por_estudiante.poner(estudiante, cursadas)
        return cursadas.agregar(materia)
 
    def de(self, estudiante):
        """el conjunto de materias cursadas (vacio si no ha cursado ninguna)."""
        cursadas = self.por_estudiante.obtener(estudiante)
        if cursadas is None:
            return conjunto()
        return cursadas
 
    def ha_cursado(self, estudiante, materia):
        return self.de(estudiante).contiene(materia)
 
    def pendientes(self, estudiante, requeridas):
        """de una lista de materias requeridas, cuales NO ha cursado
        (diferencia entre los dos conjuntos)."""
        return conjunto(requeridas).diferencia(self.de(estudiante))
 
 
# =====================================================================
# ejemplo de uso: se ejecuta con "python conjuntos_mapas.py"
# (se usan datos de mentira con la misma forma que los reales)
# =====================================================================
if __name__ == "__main__":
    class materia_demo:
        def __init__(self, nombre, area):
            self.nombre = nombre
            self.area = area
 
    materias = [
        materia_demo("calculo i", "matematicas"),
        materia_demo("calculo ii", "matematicas"),
        materia_demo("programacion i", "sistemas"),
        materia_demo("estructuras de datos", "sistemas"),
        materia_demo("fisica i", "ciencias"),
        materia_demo("algebra lineal", "matematicas"),
    ]
 
    print("--- conjunto: sin repetidos ---")
    c = conjunto()
    print("agregar 'a':", c.agregar("a"), "| agregar 'a' otra vez:", c.agregar("a"), "| tamano:", len(c))
 
    print("\n--- areas sin repeticion ---")
    print("materias:", len(materias), "| areas:", sorted(areas_sin_repetir(materias).elementos()))
    conteo = contar_por_area(materias)
    for area in sorted(areas_sin_repetir(materias).elementos()):
        print("  ", area, "->", conteo.obtener(area), "materias")
 
    print("\n--- operaciones entre conjuntos ---")
    monitor_a = conjunto(["matematicas", "sistemas"])
    monitor_b = conjunto(["sistemas", "ciencias"])
    print("union:", sorted(monitor_a.union(monitor_b).elementos()))
    print("interseccion:", sorted(monitor_a.interseccion(monitor_b).elementos()))
    print("solo el monitor a:", sorted(monitor_a.diferencia(monitor_b).elementos()))
 
    print("\n--- materias ya cursadas ---")
    registro = registro_cursadas()
    print("registrar calculo i:", registro.registrar("e-0001", "mat-0001"))
    print("registrar calculo i otra vez:", registro.registrar("e-0001", "mat-0001"))
    registro.registrar("e-0001", "mat-0002")
    print("ha cursado mat-0002:", registro.ha_cursado("e-0001", "mat-0002"))
    print("ha cursado mat-0009:", registro.ha_cursado("e-0001", "mat-0009"))
    print("cursadas por e-0001:", sorted(registro.de("e-0001").elementos()))
    print("cursadas por e-0002 (nuevo):", registro.de("e-0002").elementos())
    print("pendientes de e-0001 entre mat-0001..mat-0004:",
          sorted(registro.pendientes("e-0001", ["mat-0001", "mat-0002", "mat-0003", "mat-0004"]).elementos()))
 