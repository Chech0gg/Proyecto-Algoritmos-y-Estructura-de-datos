# ordenamientos
# insertion sort (basico) y merge sort / quick sort (avanzados)
# listados de solicitudes por urgencia, antiguedad o materia

class error_validacion(Exception):
    """se lanza cuando un dato que se quiere registrar no es valido."""
 
 
# las prioridades de la mas urgente a la menos urgente
niveles_prioridad = ["alta", "media", "baja"]
 
 
# ---------------------------------------------------------------------
# las "claves": dicen POR QUE se ordena. cada una recibe una solicitud
# y devuelve lo que se va a comparar (menor valor = va primero)
# ---------------------------------------------------------------------
def clave_urgencia(solicitud):
    """primero la prioridad (alta antes que media), luego el puntaje mas
    alto, y si empatan, la que llego primero."""
    return (niveles_prioridad.index(solicitud.prioridad), -solicitud.puntaje, solicitud.id)
 
 
def clave_antiguedad(solicitud):
    """la que llego primero (id mas bajo) va primero."""
    return solicitud.id
 
 
def clave_materia(solicitud):
    """orden alfabetico por nombre de materia; si empatan, por llegada."""
    return (solicitud.materia.nombre, solicitud.id)
 
 
claves = {"urgencia": clave_urgencia, "antiguedad": clave_antiguedad, "materia": clave_materia}
 
 
# ---------------------------------------------------------------------
# ordenamiento basico: insertion sort
# ---------------------------------------------------------------------
def ordenar_insercion(lista, clave):
    """va tomando cada elemento y lo "inserta" en su lugar dentro de la
    parte que ya esta ordenada (como ordenar cartas en la mano).
    es estable: si dos empatan, conservan su orden original.
    mejor caso (ya ordenada): n comparaciones | peor caso: n al cuadrado."""
    resultado = list(lista)                     # copia, para no dañar la original
    for i in range(1, len(resultado)):
        actual = resultado[i]
        j = i - 1
        # se corren a la derecha los que sean mayores que 'actual'
        while j >= 0 and clave(resultado[j]) > clave(actual):
            resultado[j + 1] = resultado[j]
            j -= 1
        resultado[j + 1] = actual               # aqui queda 'actual'
    return resultado
 
 
# ---------------------------------------------------------------------
# ordenamiento avanzado 1: merge sort (recursivo)
# ---------------------------------------------------------------------
def mezclar(izquierda, derecha, clave):
    """junta dos listas YA ordenadas en una sola ordenada."""
    resultado = []
    i = 0
    j = 0
    while i < len(izquierda) and j < len(derecha):
        # solo pasa la derecha si es estrictamente menor: asi es estable
        if clave(derecha[j]) < clave(izquierda[i]):
            resultado.append(derecha[j])
            j += 1
        else:
            resultado.append(izquierda[i])
            i += 1
    while i < len(izquierda):                   # sobras de la izquierda
        resultado.append(izquierda[i])
        i += 1
    while j < len(derecha):                     # sobras de la derecha
        resultado.append(derecha[j])
        j += 1
    return resultado
 
 
def ordenar_mezcla(lista, clave):
    """divide la lista por la mitad, ordena cada mitad con la misma funcion
    (recursion) y las mezcla. siempre n*log(n); es estable; usa lista extra."""
    if len(lista) <= 1:                         # caso base: ya esta ordenada
        return list(lista)
    medio = len(lista) // 2
    izquierda = ordenar_mezcla(lista[:medio], clave)
    derecha = ordenar_mezcla(lista[medio:], clave)
    return mezclar(izquierda, derecha, clave)
 
 
# ---------------------------------------------------------------------
# ordenamiento avanzado 2: quick sort (recursivo)
# ---------------------------------------------------------------------
def particionar(lista, bajo, alto, clave):
    """elige un pivote y reacomoda la lista: los menores quedan a su
    izquierda y los demas a su derecha. devuelve donde quedo el pivote."""
    medio = (bajo + alto) // 2                  # pivote del medio (evita el peor caso
    lista[medio], lista[alto] = lista[alto], lista[medio]    # en listas ya ordenadas)
    pivote = clave(lista[alto])
    frontera = bajo                             # donde va el proximo "menor"
    for i in range(bajo, alto):
        if clave(lista[i]) < pivote:
            lista[i], lista[frontera] = lista[frontera], lista[i]
            frontera += 1
    lista[frontera], lista[alto] = lista[alto], lista[frontera]   # pivote a su lugar
    return frontera
 
 
def rapido(lista, bajo, alto, clave):
    """ordena lista[bajo..alto] sobre la misma lista (sin crear otras)."""
    if bajo >= alto:                            # caso base: 0 o 1 elemento
        return
    posicion = particionar(lista, bajo, alto, clave)
    rapido(lista, bajo, posicion - 1, clave)    # lado de los menores
    rapido(lista, posicion + 1, alto, clave)    # lado de los mayores
 
 
def ordenar_rapido(lista, clave):
    """promedio n*log(n); peor caso n al cuadrado (poco comun);
    NO es estable, pero con las claves de arriba nunca hay empates
    porque todas terminan comparando el id."""
    resultado = list(lista)
    rapido(resultado, 0, len(resultado) - 1, clave)
    return resultado
 
 
# ---------------------------------------------------------------------
# elegir el algoritmo
# ---------------------------------------------------------------------
metodos = {"insercion": ordenar_insercion, "mezcla": ordenar_mezcla, "rapido": ordenar_rapido}
limite_insercion = 10    # con 10 elementos o menos, insertion sort es suficiente
 
 
def ordenar(lista, criterio, metodo="auto"):
    """ordena solicitudes por 'urgencia', 'antiguedad' o 'materia'.
    metodo: 'insercion', 'mezcla', 'rapido' o 'auto' (insercion si la lista
    es pequeña, mezcla si es grande)."""
    if criterio not in claves:
        raise error_validacion("criterio invalido: '" + str(criterio) + "' (urgencia, antiguedad o materia)")
    if metodo == "auto":
        if len(lista) <= limite_insercion:
            metodo = "insercion"
        else:
            metodo = "mezcla"
    if metodo not in metodos:
        raise error_validacion("metodo invalido: '" + str(metodo) + "'")
    return metodos[metodo](lista, claves[criterio])
 
 
# =====================================================================
# ejemplo de uso: se ejecuta con "python ordenamientos.py"
# (se usan datos de mentira con la misma forma que las solicitudes reales)
# =====================================================================
if __name__ == "__main__":
    class materia_demo:
        def __init__(self, nombre):
            self.nombre = nombre
 
    class solicitud_demo:
        def __init__(self, id, estudiante, materia, prioridad, puntaje):
            self.id = id
            self.estudiante = estudiante
            self.materia = materia_demo(materia)
            self.prioridad = prioridad
            self.puntaje = puntaje
 
        def __str__(self):
            return (f"#{self.id} {self.estudiante:<6} {self.materia.nombre:<22} "
                    f"{self.prioridad:<6} ({self.puntaje})")
 
    solicitudes = [
        solicitud_demo(1, "ana", "calculo i", "alta", 16),
        solicitud_demo(2, "luis", "programacion i", "media", 8),
        solicitud_demo(3, "sara", "fisica i", "alta", 12),
        solicitud_demo(4, "eva", "estructuras de datos", "alta", 14),
        solicitud_demo(5, "beto", "calculo i", "media", 8),
    ]
 
    for criterio in ["urgencia", "antiguedad", "materia"]:
        print("\nordenadas por", criterio + ":")
        for solicitud in ordenar(solicitudes, criterio):
            print("  ", solicitud)
 
    # los tres algoritmos dan el mismo resultado
    for criterio in claves:
        a = [x.id for x in ordenar_insercion(solicitudes, claves[criterio])]
        b = [x.id for x in ordenar_mezcla(solicitudes, claves[criterio])]
        c = [x.id for x in ordenar_rapido(solicitudes, claves[criterio])]
        print("\n" + criterio + ": insercion", a, "| mezcla", b, "| rapido", c, "| iguales:", a == b == c)
 