from . import prioridad
from .errores import error_validacion
from .monticulo import monticulo


class cola_solicitudes:

    def __init__(self, dias=prioridad.dias_envejecimiento):
        self.dias = dias
        self.monticulo = monticulo()

    def encolar(self, solicitud):
        clave = prioridad.clave_cola(solicitud.urgencia, solicitud.llegada, self.dias)
        self.monticulo.insertar(clave, solicitud)

    def desencolar(self):
        if self.monticulo.esta_vacio():
            raise error_validacion("no hay solicitudes pendientes")
        return self.monticulo.extraer()

    def quitar(self, solicitud):
        return self.monticulo.quitar(solicitud)

    def esta_vacia(self):
        return self.monticulo.esta_vacio()

    def pendientes(self):
        return self.monticulo.como_lista()

    def __len__(self):
        return len(self.monticulo)
