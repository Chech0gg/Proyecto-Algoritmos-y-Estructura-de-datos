from .errores import error_validacion

limite_insercion = 10


def clave_urgencia(solicitud):
    return (-solicitud.urgencia, solicitud.id)


def clave_antiguedad(solicitud):
    return (solicitud.llegada, solicitud.id)


def clave_materia(solicitud):
    return (solicitud.materia.nombre, solicitud.id)


def clave_texto(texto):
    return texto


claves = {"urgencia": clave_urgencia, "antiguedad": clave_antiguedad, "materia": clave_materia}


def ordenar_insercion(lista, clave):
    resultado = list(lista)
    for i in range(1, len(resultado)):
        actual = resultado[i]
        j = i - 1
        while j >= 0 and clave(resultado[j]) > clave(actual):
            resultado[j + 1] = resultado[j]
            j -= 1
        resultado[j + 1] = actual
    return resultado


def mezclar(izquierda, derecha, clave):
    resultado = []
    i = 0
    j = 0
    while i < len(izquierda) and j < len(derecha):
        if clave(derecha[j]) < clave(izquierda[i]):
            resultado.append(derecha[j])
            j += 1
        else:
            resultado.append(izquierda[i])
            i += 1
    return resultado + izquierda[i:] + derecha[j:]


def ordenar_mezcla(lista, clave):
    if len(lista) <= 1:
        return list(lista)
    medio = len(lista) // 2
    return mezclar(ordenar_mezcla(lista[:medio], clave), ordenar_mezcla(lista[medio:], clave), clave)


def ordenar_rapido(lista, clave):
    resultado = list(lista)
    rangos = [(0, len(resultado) - 1)]
    while rangos:
        bajo, alto = rangos.pop()
        if bajo >= alto:
            continue
        pivote = clave(resultado[(bajo + alto) // 2])
        menor = bajo
        i = bajo
        mayor = alto
        while i <= mayor:
            valor = clave(resultado[i])
            if valor < pivote:
                resultado[menor], resultado[i] = resultado[i], resultado[menor]
                menor += 1
                i += 1
            elif valor > pivote:
                resultado[i], resultado[mayor] = resultado[mayor], resultado[i]
                mayor -= 1
            else:
                i += 1
        rangos.append((bajo, menor - 1))
        rangos.append((mayor + 1, alto))
    return resultado


metodos = {"insercion": ordenar_insercion, "mezcla": ordenar_mezcla, "rapido": ordenar_rapido}


def ordenar(lista, criterio, metodo="auto"):
    if criterio not in claves:
        raise error_validacion("criterio invalido: '" + str(criterio) + "' (urgencia, antiguedad o materia)")
    if metodo == "auto":
        metodo = "insercion" if len(lista) <= limite_insercion else "mezcla"
    if metodo not in metodos:
        raise error_validacion("metodo invalido: '" + str(metodo) + "'")
    return metodos[metodo](lista, claves[criterio])


def busqueda_binaria(lista, objetivo, clave):
    bajo = 0
    alto = len(lista) - 1
    comparaciones = 0
    while bajo <= alto:
        medio = (bajo + alto) // 2
        comparaciones += 1
        valor = clave(lista[medio])
        if valor == objetivo:
            return medio, comparaciones
        if valor < objetivo:
            bajo = medio + 1
        else:
            alto = medio - 1
    return -1, comparaciones
