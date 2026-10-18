class clase_nodo:
    """una pieza de la cola: guarda un dato y apunta a la pieza siguiente."""
 
    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None
 
 
class cola:
    """una fila normal: el primero que entra es el primero que sale.
    esta hecha con piezas enlazadas (lista enlazada)."""
 
    def __init__(self):
        self.frente = None    # primera pieza (la que sale primero)
        self.final = None     # ultima pieza (donde se agrega)
        self.cantidad = 0
 
    def encolar(self, dato):
        """agrega un dato al final de la fila."""
        nodo = clase_nodo(dato)
        if self.final is None:
            self.frente = nodo
            self.final = nodo
        else:
            self.final.siguiente = nodo
            self.final = nodo
        self.cantidad += 1
 
    def desencolar(self):
        """saca y devuelve el dato que esta al frente."""
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
        """devuelve los datos en orden sin sacarlos de la cola."""
        lista = []
        actual = self.frente
        while actual is not None:
            lista.append(actual.dato)
            actual = actual.siguiente
        return lista
 
    def __len__(self):
        return self.cantidad
 
 
# las prioridades de la mas urgente a la menos urgente
niveles_prioridad = ["alta", "media", "baja"]
 
 
def calcular_prioridad(materia, desempeno):
    """decide que tan urgente es una solicitud con esta cuenta:
 
        puntaje = dificultad de la materia * 2 + (5 - desempeno) * 2
 
    el desempeno va de 1 (voy muy mal) a 5 (voy muy bien).
    puntaje 12 o mas -> alta | de 7 a 11 -> media | menos de 7 -> baja
 
    devuelve el puntaje, el nivel y un texto que explica la cuenta."""
    por_dificultad = materia.dificultad * 2
    por_desempeno = (5 - desempeno) * 2
    puntaje = por_dificultad + por_desempeno
    if puntaje >= 12:
        nivel = "alta"
    elif puntaje >= 7:
        nivel = "media"
    else:
        nivel = "baja"
    explicacion = (f"dificultad {materia.dificultad}*2={por_dificultad} + "
                   f"desempeno {desempeno}->{por_desempeno} = {puntaje}")
    return puntaje, nivel, explicacion
 
 
class clase_solicitud:
    """un pedido de monitoria. el estado cambia con el tiempo:
    pendiente (recien creada) -> asignada (ya tiene hora) o en_espera."""
 
    def __init__(self, id, estudiante, materia, tipo, desempeno, puntaje, prioridad, desglose):
        self.id = id
        self.estudiante = estudiante
        self.materia = materia
        self.tipo = tipo
        self.desempeno = desempeno
        self.puntaje = puntaje
        self.prioridad = prioridad
        self.desglose = desglose
        self.estado = "pendiente"
        self.motivo = ""    # por que esta en espera (o con quien se asigno)
 
 
class cola_solicitudes:
    """tiene una fila por cada prioridad (alta, media, baja).
    siempre se atiende primero la fila mas urgente que tenga alguien, y
    dentro de una fila, el que llego primero."""
 
    def __init__(self):
        self.filas = {"alta": cola(), "media": cola(), "baja": cola()}
 
    def encolar(self, solicitud):
        """pone la solicitud en la fila de su prioridad."""
        self.filas[solicitud.prioridad].encolar(solicitud)
 
    def desencolar(self):
        """saca la siguiente solicitud a atender."""
        for nivel in niveles_prioridad:
            if not self.filas[nivel].esta_vacia():
                return self.filas[nivel].desencolar()
        raise error_validacion("no hay solicitudes pendientes")
 
    def esta_vacia(self):
        return len(self) == 0
 
    def pendientes(self):
        """lista de todas las solicitudes en el orden en que se atenderian."""
        lista = []
        for nivel in niveles_prioridad:
            lista = lista + self.filas[nivel].como_lista()
        return lista
 
    def __len__(self):
        total = 0
        for nivel in niveles_prioridad:
            total += len(self.filas[nivel])
        return total
 