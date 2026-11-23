from .errores import error_validacion


def es_numero(valor):
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


def texto(valor, nombre):
    if not isinstance(valor, str) or valor.strip() == "":
        raise error_validacion(nombre + " no puede estar vacio")
    return valor.strip()


def entero(valor, nombre, minimo, maximo):
    if not isinstance(valor, int) or isinstance(valor, bool):
        raise error_validacion(nombre + " debe ser un numero entero")
    if valor < minimo or valor > maximo:
        raise error_validacion(f"{nombre} debe estar entre {minimo} y {maximo}")
    return valor


def decimal(valor, nombre, minimo, maximo):
    if not es_numero(valor) or valor != valor:
        raise error_validacion(nombre + " debe ser un numero")
    if valor < minimo or valor > maximo:
        raise error_validacion(f"{nombre} debe estar entre {minimo} y {maximo}")
    return float(valor)
