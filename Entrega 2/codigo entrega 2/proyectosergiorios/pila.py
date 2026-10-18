#pila
#revertir la ultima asignacion de monitoria

class error_validacion(Exception):
    """se lanza cuando un dato que se quiere registrar no es valido."""
 
 
class clase_nodo:
    """una pieza de la pila: guarda un dato y apunta a la pieza de abajo."""
 
    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None
 
 
class pila:
    def __init__(self):
        self.tope = None      # la pieza de arriba (la ultima que entro)
        self.cantidad = 0
 
    def apilar(self, dato):
        """pone un dato encima de la pila."""
        nodo = clase_nodo(dato)
        nodo.siguiente = self.tope      # la nueva apunta a la que estaba arriba
        self.tope = nodo                # y pasa a ser la de arriba
        self.cantidad += 1
 
    def desapilar(self):
        """saca y devuelve el dato de arriba."""
        if self.tope is None:
            raise error_validacion("la pila esta vacia")
        dato = self.tope.dato
        self.tope = self.tope.siguiente
        self.cantidad -= 1
        return dato
 
    def ver_tope(self):
        """devuelve el dato de arriba SIN sacarlo (nada si esta vacia)."""
        if self.tope is None:
            return None
        return self.tope.dato
 
    def esta_vacia(self):
        return self.cantidad == 0
 
    def como_lista(self):
        """devuelve los datos de arriba hacia abajo sin sacarlos."""
        lista = []
        actual = self.tope
        while actual is not None:
            lista.append(actual.dato)
            actual = actual.siguiente
        return lista
 
    def __len__(self):
        return self.cantidad
 
 
class clase_registro_asignacion:
    """lo que hay que recordar de una asignacion para poder deshacerla:
    la solicitud, la sesion y si esa asignacion CREO la sesion o solo
    metio al estudiante en una sesion (grupo) que ya existia."""
 
    def __init__(self, solicitud, sesion, creo_sesion):
        self.solicitud = solicitud
        self.sesion = sesion
        self.creo_sesion = creo_sesion
 
 
def revertir_registro(registro, agenda):
    """deshace una asignacion sobre la agenda y devuelve la solicitud afectada."""
    if registro.creo_sesion:
        agenda.sesiones.remove(registro.sesion)                         # se borra la sesion entera
    else:
        registro.sesion.estudiantes.remove(registro.solicitud.estudiante)   # solo sale del grupo
    return registro.solicitud
 
 
# =====================================================================
# ejemplo de uso: se ejecuta con "python pila.py"
# (se usan datos de mentira con la misma forma que los reales)
# =====================================================================
if __name__ == "__main__":
    class estudiante_demo:
        def __init__(self, nombre):
            self.nombre = nombre
 
    class solicitud_demo:
        def __init__(self, id, nombre):
            self.id = id
            self.estudiante = estudiante_demo(nombre)
            self.estado = "pendiente"
            self.motivo = ""
 
    class sesion_demo:
        def __init__(self, estudiantes):
            self.estudiantes = estudiantes
 
    class agenda_demo:
        def __init__(self):
            self.sesiones = []
 
        def mostrar(self):
            if len(self.sesiones) == 0:
                return "  (agenda vacia)"
            return "\n".join(["  sesion con: " + ", ".join([e.nombre for e in s.estudiantes])
                              for s in self.sesiones])
 
    agenda = agenda_demo()
    historial = pila()
 
    # 1) ana pide y se le crea una sesion
    ana = solicitud_demo(1, "ana")
    sesion_ana = sesion_demo([ana.estudiante])
    agenda.sesiones.append(sesion_ana)
    historial.apilar(clase_registro_asignacion(ana, sesion_ana, True))
    # 2) luis pide y se une al grupo de ana (no se crea sesion)
    luis = solicitud_demo(2, "luis")
    sesion_ana.estudiantes.append(luis.estudiante)
    historial.apilar(clase_registro_asignacion(luis, sesion_ana, False))
    # 3) eva pide y se le crea otra sesion
    eva = solicitud_demo(3, "eva")
    sesion_eva = sesion_demo([eva.estudiante])
    agenda.sesiones.append(sesion_eva)
    historial.apilar(clase_registro_asignacion(eva, sesion_eva, True))
 
    print("agenda inicial:")
    print(agenda.mostrar())
    print("tope de la pila: solicitud", historial.ver_tope().solicitud.id, "| tamano:", len(historial))
 
    # se revierte de la ultima a la primera
    while not historial.esta_vacia():
        afectada = revertir_registro(historial.desapilar(), agenda)
        print("\nrevertida la solicitud", afectada.id, "(" + afectada.estudiante.nombre + ")")
        print(agenda.mostrar())
 
    try:
        historial.desapilar()
    except error_validacion as e:
        print("\nrechazado:", e)
 