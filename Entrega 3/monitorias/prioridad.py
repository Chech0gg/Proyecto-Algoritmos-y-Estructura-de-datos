import math

from .errores import error_validacion
from . import validaciones

nota_maxima = 5.0
nota_aprobatoria = 3.0
ancho_riesgo = 1.0
dias_envejecimiento = 7.0
umbral_alta = 0.5
umbral_media = 0.1
niveles_prioridad = ["alta", "media", "baja"]
peso_nota_materia = 0.7


def constante_k(ancho=ancho_riesgo):
    return math.log(9) / ancho


def riesgo(nota, aprobatoria=nota_aprobatoria, ancho=ancho_riesgo):
    nota = validaciones.decimal(nota, "la nota", 0.0, nota_maxima)
    return 1 / (1 + math.exp(constante_k(ancho) * (nota - aprobatoria)))


def impacto(dependientes, maximo):
    if dependientes < 0 or maximo < dependientes:
        raise error_validacion("conteo de materias dependientes invalido")
    return (1 + dependientes) / (1 + maximo)


def urgencia(riesgo_valor, impacto_valor):
    return riesgo_valor * impacto_valor


def nivel_por_riesgo(riesgo_valor):
    if riesgo_valor >= umbral_alta - 1e-9:
        return "alta"
    if riesgo_valor >= umbral_media - 1e-9:
        return "media"
    return "baja"


def clave_cola(urgencia_valor, llegada, dias=dias_envejecimiento):
    return llegada / dias - urgencia_valor


def prioridad_efectiva(urgencia_valor, llegada, ahora, dias=dias_envejecimiento):
    return urgencia_valor + (ahora - llegada) / dias


def cota_adelantamiento(urgencia_valor, dias=dias_envejecimiento):
    return dias * (1 - urgencia_valor)


class resultado_prioridad:

    def __init__(self, riesgo_valor, impacto_valor, urgencia_valor, nivel, desglose):
        self.riesgo = riesgo_valor
        self.impacto = impacto_valor
        self.urgencia = urgencia_valor
        self.nivel = nivel
        self.desglose = desglose


def nota_esperada(nota, promedio, peso=peso_nota_materia):
    nota = validaciones.decimal(nota, "la nota", 0.0, nota_maxima)
    promedio = validaciones.decimal(promedio, "el promedio", 0.0, nota_maxima)
    return peso * nota + (1 - peso) * promedio


def calcular_prioridad(nota, tasa_reprobacion, dependientes, maximo, promedio=None):
    if nota is not None and promedio is not None:
        esperada = nota_esperada(nota, promedio)
        r = riesgo(esperada)
        fuente = (f"nota {float(nota):.1f} y promedio {float(promedio):.1f}, "
                  f"ponderados {peso_nota_materia:.1f}/{1 - peso_nota_materia:.1f} = {esperada:.2f}")
    elif nota is not None:
        r = riesgo(nota)
        fuente = f"nota {float(nota):.1f}"
    elif tasa_reprobacion is not None:
        r = validaciones.decimal(tasa_reprobacion, "la tasa de reprobacion", 0.0, 1.0)
        fuente = f"tasa historica {r:.2f}"
    elif promedio is not None:
        r = riesgo(promedio)
        fuente = f"promedio {float(promedio):.1f}"
    else:
        raise error_validacion("se necesita la nota actual, el promedio o la tasa de reprobacion de la materia")
    i = impacto(dependientes, maximo)
    u = urgencia(r, i)
    desglose = (f"riesgo {r:.3f} ({fuente}) x impacto {i:.3f} "
                f"({dependientes} de {maximo} materias dependientes) = urgencia {u:.3f}")
    return resultado_prioridad(r, i, u, nivel_por_riesgo(r), desglose)
