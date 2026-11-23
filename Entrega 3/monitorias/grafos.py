from .errores import error_validacion


def matriz_a_lista(matriz):
    n = len(matriz)
    for fila in matriz:
        if len(fila) != n:
            raise error_validacion("la matriz debe ser cuadrada")
        for valor in fila:
            if valor != 0 and valor != 1:
                raise error_validacion("la matriz solo puede tener ceros y unos")
    return [[j for j in range(n) if matriz[i][j] == 1] for i in range(n)]


def lista_a_matriz(lista):
    n = len(lista)
    matriz = [[0] * n for _ in range(n)]
    for u in range(n):
        for v in lista[u]:
            if not isinstance(v, int) or isinstance(v, bool) or v < 0 or v >= n:
                raise error_validacion("la lista tiene un vecino invalido: " + str(v))
            matriz[u][v] = 1
    return matriz


class grafo_dirigido:

    def __init__(self):
        self.etiquetas = []
        self.posicion = {}
        self.sucesores = []
        self.predecesores = []
        self.aristas = 0

    def __len__(self):
        return len(self.etiquetas)

    def vertice(self, etiqueta):
        if etiqueta not in self.posicion:
            raise error_validacion("vertice desconocido: '" + str(etiqueta) + "'")
        return self.posicion[etiqueta]

    def agregar_vertice(self, etiqueta):
        if etiqueta in self.posicion:
            return self.posicion[etiqueta]
        self.posicion[etiqueta] = len(self.etiquetas)
        self.etiquetas.append(etiqueta)
        self.sucesores.append([])
        self.predecesores.append([])
        return self.posicion[etiqueta]

    def alcanzable(self, u, v):
        visitado = [False] * len(self.etiquetas)
        pendientes = [u]
        visitado[u] = True
        while pendientes:
            actual = pendientes.pop()
            if actual == v:
                return True
            for siguiente in self.sucesores[actual]:
                if not visitado[siguiente]:
                    visitado[siguiente] = True
                    pendientes.append(siguiente)
        return False

    def agregar_arista(self, origen, destino, validar_ciclos=True):
        u = self.vertice(origen)
        v = self.vertice(destino)
        if v in self.sucesores[u]:
            raise error_validacion("la arista " + str(origen) + " -> " + str(destino) + " ya existe")
        if validar_ciclos and (u == v or self.alcanzable(v, u)):
            raise error_validacion("la arista " + str(origen) + " -> " + str(destino) + " crearia un ciclo")
        self.sucesores[u].append(v)
        self.predecesores[v].append(u)
        self.aristas += 1

    def a_lista(self):
        return [list(vecinos) for vecinos in self.sucesores]

    def a_matriz(self):
        return lista_a_matriz(self.sucesores)

    def densidad(self):
        n = len(self.etiquetas)
        if n < 2:
            return 0.0
        return self.aristas / (n * (n - 1))

    def justificar_representacion(self):
        n = len(self.etiquetas)
        densidad = self.densidad()
        celdas_matriz = n * n
        celdas_lista = n + self.aristas
        if densidad < 0.3:
            decision = "lista de adyacencia"
            motivo = "el grafo es disperso: la lista guarda solo las aristas que existen"
        else:
            decision = "matriz de adyacencia"
            motivo = "el grafo es denso: la matriz permite consultar una arista en tiempo constante"
        return {"vertices": n, "aristas": self.aristas, "densidad": densidad,
                "celdas_matriz": celdas_matriz, "celdas_lista": celdas_lista,
                "decision": decision, "motivo": motivo}

    def vecinos(self, u, dirigido):
        if dirigido:
            return self.sucesores[u]
        return self.sucesores[u] + self.predecesores[u]

    def componentes(self):
        n = len(self.etiquetas)
        visitado = [False] * n
        resultado = []
        for inicio in range(n):
            if visitado[inicio]:
                continue
            visitado[inicio] = True
            pendientes = [inicio]
            miembros = []
            while pendientes:
                actual = pendientes.pop()
                miembros.append(actual)
                for vecino in self.vecinos(actual, False):
                    if not visitado[vecino]:
                        visitado[vecino] = True
                        pendientes.append(vecino)
            miembros.sort()
            resultado.append([self.etiquetas[i] for i in miembros])
        return resultado

    def detectar_ciclos(self):
        n = len(self.etiquetas)
        estado = [0] * n
        ciclos = []
        for inicio in range(n):
            if estado[inicio] != 0:
                continue
            camino = [inicio]
            indices = [0]
            estado[inicio] = 1
            while camino:
                actual = camino[-1]
                if indices[-1] < len(self.sucesores[actual]):
                    vecino = self.sucesores[actual][indices[-1]]
                    indices[-1] += 1
                    if estado[vecino] == 0:
                        estado[vecino] = 1
                        camino.append(vecino)
                        indices.append(0)
                    elif estado[vecino] == 1:
                        i = camino.index(vecino)
                        ciclos.append([self.etiquetas[x] for x in camino[i:]] + [self.etiquetas[vecino]])
                else:
                    estado[actual] = 2
                    camino.pop()
                    indices.pop()
        return ciclos

    def indices_topologicos(self):
        n = len(self.etiquetas)
        grado = [len(self.predecesores[v]) for v in range(n)]
        listos = [v for v in range(n) if grado[v] == 0]
        i = 0
        while i < len(listos):
            actual = listos[i]
            i += 1
            for vecino in self.sucesores[actual]:
                grado[vecino] -= 1
                if grado[vecino] == 0:
                    listos.append(vecino)
        if len(listos) != n:
            raise error_validacion("el grafo tiene ciclos: no existe un orden topologico")
        return listos

    def orden_topologico(self):
        return [self.etiquetas[i] for i in self.indices_topologicos()]

    def longitudes_y_padres(self):
        n = len(self.etiquetas)
        mejor = [0] * n
        padre = [-1] * n
        for u in self.indices_topologicos():
            for v in self.sucesores[u]:
                if mejor[u] + 1 > mejor[v]:
                    mejor[v] = mejor[u] + 1
                    padre[v] = u
        return mejor, padre

    def niveles(self):
        mejor, padre = self.longitudes_y_padres()
        return {self.etiquetas[v]: mejor[v] for v in range(len(self.etiquetas))}

    def camino_mas_largo(self):
        if len(self.etiquetas) == 0:
            return []
        mejor, padre = self.longitudes_y_padres()
        fin = 0
        for v in range(len(self.etiquetas)):
            if mejor[v] > mejor[fin]:
                fin = v
        ruta = []
        while fin != -1:
            ruta.append(self.etiquetas[fin])
            fin = padre[fin]
        ruta.reverse()
        return ruta

    def bfs(self, inicio, dirigido):
        n = len(self.etiquetas)
        distancia = [-1] * n
        padre = [-1] * n
        distancia[inicio] = 0
        cola = [inicio]
        i = 0
        while i < len(cola):
            actual = cola[i]
            i += 1
            for vecino in self.vecinos(actual, dirigido):
                if distancia[vecino] == -1:
                    distancia[vecino] = distancia[actual] + 1
                    padre[vecino] = actual
                    cola.append(vecino)
        return distancia, padre

    def distancias_desde(self, etiqueta, dirigido=True):
        distancia, padre = self.bfs(self.vertice(etiqueta), dirigido)
        return {self.etiquetas[v]: distancia[v] for v in range(len(self.etiquetas))}

    def ruta_mas_corta(self, origen, destino, dirigido=True):
        u = self.vertice(origen)
        v = self.vertice(destino)
        distancia, padre = self.bfs(u, dirigido)
        if distancia[v] == -1:
            return None
        ruta = []
        while v != -1:
            ruta.append(self.etiquetas[v])
            v = padre[v]
        ruta.reverse()
        return ruta

    def diametro(self, dirigido=False):
        n = len(self.etiquetas)
        mayor = 0
        par = None
        for u in range(n):
            distancia, padre = self.bfs(u, dirigido)
            for v in range(n):
                if distancia[v] > mayor:
                    mayor = distancia[v]
                    par = (self.etiquetas[u], self.etiquetas[v])
        return mayor, par

    def olas_desde(self, etiqueta, hacia="dependientes"):
        u = self.vertice(etiqueta)
        dirigido_sucesores = hacia == "dependientes"
        n = len(self.etiquetas)
        distancia = [-1] * n
        distancia[u] = 0
        cola = [u]
        i = 0
        while i < len(cola):
            actual = cola[i]
            i += 1
            vecinos = self.sucesores[actual] if dirigido_sucesores else self.predecesores[actual]
            for vecino in vecinos:
                if distancia[vecino] == -1:
                    distancia[vecino] = distancia[actual] + 1
                    cola.append(vecino)
        olas = []
        for v in cola:
            while len(olas) <= distancia[v]:
                olas.append([])
            olas[distancia[v]].append(self.etiquetas[v])
        return olas

    def descendientes(self, etiqueta):
        olas = self.olas_desde(etiqueta, "dependientes")
        resultado = set()
        for ola in olas[1:]:
            resultado.update(ola)
        return resultado

    def conteo_dependientes(self):
        return {etiqueta: len(self.descendientes(etiqueta)) for etiqueta in self.etiquetas}


def grafo_desde_matriz(matriz, etiquetas=None):
    lista = matriz_a_lista(matriz)
    grafo = grafo_dirigido()
    n = len(lista)
    if etiquetas is None:
        etiquetas = [str(i) for i in range(n)]
    if len(etiquetas) != n:
        raise error_validacion("la cantidad de etiquetas no coincide con la matriz")
    for etiqueta in etiquetas:
        grafo.agregar_vertice(etiqueta)
    for u in range(n):
        for v in lista[u]:
            grafo.agregar_arista(etiquetas[u], etiquetas[v], validar_ciclos=False)
    return grafo
