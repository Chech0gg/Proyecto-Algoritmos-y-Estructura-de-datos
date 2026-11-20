from .errores import error_validacion


class tipo_monitoria:
    par = "par"
    general = "general"
    puntual = "puntual"


duracion_min = {"par": 60, "general": 90, "puntual": 30}
cupo = {"par": 1, "general": 5, "puntual": 1}
dias = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado"]
paso_min = 30
acentos = {"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u"}


def normalizar_dia(dia):
    if not isinstance(dia, str):
        raise error_validacion("dia invalido: '" + str(dia) + "'")
    limpio = dia.strip().lower()
    for con, sin in acentos.items():
        limpio = limpio.replace(con, sin)
    if limpio not in dias:
        raise error_validacion("dia invalido: '" + str(dia) + "'")
    return limpio


def solo_digitos(texto):
    return texto != "" and texto.isascii() and texto.isdigit()


def hora_a_minutos(texto, permitir_24=False):
    if not isinstance(texto, str):
        raise error_validacion("hora invalida: '" + str(texto) + "' (use hh:mm)")
    partes = texto.strip().split(":")
    if (len(partes) != 2 or not solo_digitos(partes[0]) or not solo_digitos(partes[1])
            or len(partes[0]) > 2 or len(partes[1]) != 2):
        raise error_validacion("hora invalida: '" + texto + "' (use hh:mm)")
    horas = int(partes[0])
    minutos = int(partes[1])
    if permitir_24 and horas == 24 and minutos == 0:
        return 1440
    if horas > 23 or minutos > 59:
        raise error_validacion("hora fuera de rango: '" + texto + "'")
    return horas * 60 + minutos


def minutos_a_hora(minutos):
    return f"{minutos // 60:02d}:{minutos % 60:02d}"


class clase_bloque:

    def __init__(self, dia, inicio, fin):
        self.dia = dia
        self.inicio = inicio
        self.fin = fin

    def cubre(self, dia, inicio, fin):
        return self.dia == dia and self.inicio <= inicio and fin <= self.fin


def crear_bloque(dia, inicio, fin):
    dia = normalizar_dia(dia)
    minutos_inicio = hora_a_minutos(inicio)
    minutos_fin = hora_a_minutos(fin, permitir_24=True)
    if minutos_inicio >= minutos_fin:
        raise error_validacion("el bloque " + str(inicio) + "-" + str(fin) + " termina antes de empezar")
    return clase_bloque(dia, minutos_inicio, minutos_fin)


def fusionar_bloques(bloques):
    por_dia = {}
    for bloque in bloques:
        if bloque.dia not in por_dia:
            por_dia[bloque.dia] = []
        por_dia[bloque.dia].append((bloque.inicio, bloque.fin))
    resultado = []
    for dia in dias:
        if dia not in por_dia:
            continue
        intervalos = sorted(por_dia[dia])
        inicio, fin = intervalos[0]
        for siguiente_inicio, siguiente_fin in intervalos[1:]:
            if siguiente_inicio <= fin:
                fin = max(fin, siguiente_fin)
            else:
                resultado.append(clase_bloque(dia, inicio, fin))
                inicio, fin = siguiente_inicio, siguiente_fin
        resultado.append(clase_bloque(dia, inicio, fin))
    return resultado


def cubierto(bloques, dia, inicio, fin):
    for bloque in fusionar_bloques(bloques):
        if bloque.cubre(dia, inicio, fin):
            return True
    return False
