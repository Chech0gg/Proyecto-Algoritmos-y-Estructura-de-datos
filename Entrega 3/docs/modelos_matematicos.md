# Modelos matemáticos del sistema de monitorías

Este documento justifica cada modelo implementado: qué problema resuelve, por qué se eligió, qué propiedades se demuestran y cuáles son sus límites. Todo lo numérico se puede reproducir con `python scripts/benchmark_avl.py`, `python scripts/sensibilidad.py` y la suite de pruebas.

## 1. Por qué se reemplazó la fórmula de prioridad

La fórmula de la entrega anterior era:

    puntaje = 2 * dificultad + 2 * (5 - desempeño)      alta: >= 12   media: 7 a 11   baja: < 7

Se revisó ejecutándola sobre las 25 combinaciones posibles (dificultad 1 a 5 por desempeño 1 a 5) y no tiene una base que la sustente:

| Problema | Evidencia |
|---|---|
| El factor 2 no cambia nada | Ordenar por puntaje es idéntico a ordenar por `dificultad - desempeño` |
| Es compensatoria | (dificultad 5, desempeño 5) da 10, "media", igual que (1, 1), que también da 10. Quien va muy bien en la materia más difícil queda como prioridad media |
| Los cortes 12 y 7 son arbitrarios | Reparten las 25 combinaciones en 10 altas, 9 medias y 6 bajas, sin criterio |
| Puede dejar solicitudes esperando para siempre | Tres filas con prioridad estricta: mientras lleguen solicitudes "altas", las "bajas" no se atienden |
| El dato de entrada es subjetivo | "Desempeño de 1 a 5" lo declara el propio estudiante |

Lo único con respaldo en la fórmula anterior es su estructura general, una suma ponderada de criterios, que es un método clásico de decisión multicriterio. Ese método exige normalizar los criterios a una escala comparable y justificar los pesos, y la fórmula no hacía ninguna de las dos cosas.

## 2. Modelo de prioridad implementado

Archivo: `monitorias/prioridad.py`. Entradas: la nota actual `g` del estudiante en la materia (de 0.0 a 5.0, escala en la que 3.0 es la nota aprobatoria) y la posición de la materia en el grafo de prerrequisitos.

### 2.1 Riesgo de reprobar

    R(g) = 1 / (1 + e^(k * (g - 3.0))),      k = ln 9 / ancho,      ancho = 1.0

Es la probabilidad estimada de reprobar. Se fija con tres anclas: nota 3.0 da 50 %, nota 2.0 da 90 % y nota 4.0 da 10 %.

Propiedades (verificadas en `tests/test_prioridad.py`): R está estrictamente entre 0 y 1, es estrictamente decreciente en la nota y es simétrica alrededor de 3.0 (R(g) + R(6 - g) = 1).

Por qué una curva logística: es el modelo habitual para la probabilidad de un resultado de sí o no, aquí aprobar o reprobar. Se centra en la nota aprobatoria porque en ese punto la probabilidad de reprobar se asume del 50 %.

Límite que hay que declarar: las anclas del 90 % y del 10 % son supuestos de modelado, no estimaciones hechas con datos. Cuando existan notas históricas se pueden calibrar con una regresión logística. Mientras tanto se muestra el análisis de sensibilidad (sección 2.6).

Si no hay nota, se usa como riesgo la tasa histórica de reprobación de la materia (un dato observable, entre 0 y 1). Si no hay ninguna de las dos, el sistema rechaza la solicitud.

### 2.2 Impacto

    I(m) = (1 + d(m)) / (1 + d_max)

`d(m)` es la cantidad de materias que dependen de `m`, directa o indirectamente, en el grafo de prerrequisitos, y `d_max` es el mayor valor de `d` en toda la malla. I está entre 0 y 1 y vale 1 para la materia más "estructural". Si la malla no tiene prerrequisitos, I vale 1 para todas y la urgencia depende solo del riesgo.

Justificación: reprobar una materia retrasa a todas las que dependen de ella, así que el costo de fallar crece con ese número.

### 2.3 Urgencia

    U = R * I

Es una pérdida esperada: probabilidad de fallar por consecuencia de fallar. A diferencia de la suma, no es compensatoria: si el riesgo es casi cero, la urgencia es casi cero, sin importar qué tan difícil o importante sea la materia. Con la malla de ejemplo:

| Caso | R | I | U |
|---|---|---|---|
| Nota 2.5 en una materia que bloquea 2 (la mayor de la malla) | 0.75 | 1.00 | 0.750 |
| Nota 2.5 en una materia que no bloquea ninguna | 0.75 | 0.33 | 0.250 |
| Nota 4.8 en la materia que bloquea más | 0.019 | 1.00 | 0.019 |
| Nota 5.0 en la materia que bloquea más | 0.012 | 1.00 | 0.012 |

### 2.4 Niveles alta, media y baja

Se derivan de las anclas, no de cortes elegidos a mano: alta si R >= 0.5 (nota <= 3.0), media si 0.1 <= R < 0.5 (nota hasta 4.0) y baja si R < 0.1. Coinciden con los umbrales de 3.0 y 4.0 que ya usaba la Entrega 1.

### 2.5 Envejecimiento y garantía contra la inanición

La prioridad efectiva de una solicitud con urgencia `U` que llegó en el instante `a` es, en el instante `t`:

    P(t) = U + (t - a) / T          T = 7 días por defecto

**Orden estático.** Para dos solicitudes i y j, la diferencia P_i(t) - P_j(t) = (U_i - a_i/T) - (U_j - a_j/T) no depende de `t`. Por tanto el orden entre ellas nunca cambia con el tiempo y basta una cola con la clave fija `a/T - U` (el menor primero). Se implementó con un montículo binario, de modo que insertar y extraer cuestan O(log n).

**Teorema de adelantamiento acotado.** Una solicitud j que llega después que i (a_j > a_i) solo puede atenderse antes que i si

    a_j - a_i  <  T * (U_j - U_i)  <=  T * (1 - U_i)

*Demostración.* j precede a i si y solo si la clave de j es menor, es decir a_j/T - U_j < a_i/T - U_i, lo que equivale a a_j - a_i < T (U_j - U_i). Como U_j < 1, se cumple T (U_j - U_i) < T (1 - U_i). Cualquier solicitud que llegue después de pasados T (1 - U_i) días de la llegada de i ya no puede adelantarla.

**Consecuencia.** Solo un conjunto finito de solicitudes puede adelantar a i, así que ninguna solicitud espera indefinidamente. Con T = 7: una solicitud de urgencia 0.05 puede ser adelantada durante 6.65 días como máximo, una de 0.5 durante 3.5 días y una de 0.95 durante 0.35 días.

Verificación: `test_cota_de_adelantamiento` comprueba la cota sobre 300 solicitudes al azar, y `test_ninguna_solicitud_se_queda_esperando_para_siempre` simula un flujo continuo de solicitudes urgentes. Sin envejecimiento la solicitud de baja urgencia no se atiende en ninguno de los 399 turnos simulados, y con T = 7 se atiende exactamente en el turno 7.

### 2.6 Sensibilidad a los parámetros

`scripts/sensibilidad.py` compara el orden de la cola con distintos parámetros, sobre 200 solicitudes sintéticas (notas, impactos y llegadas al azar). Se mide con el tau de Kendall (1.0 es el mismo orden) y con cuántas de las 20 primeras coinciden con la configuración base.

| ancho | T = 3 | T = 7 | T = 14 |
|---|---|---|---|
| 0.5 | 0.871 (15/20) | 0.952 (19/20) | 0.782 (15/20) |
| 0.75 | 0.866 (14/20) | 0.979 (19/20) | 0.806 (15/20) |
| **1.0** | 0.860 (13/20) | **1.000 (20/20)** | 0.821 (15/20) |
| 1.5 | 0.846 (12/20) | 0.964 (20/20) | 0.848 (15/20) |
| 2.0 | 0.832 (12/20) | 0.935 (20/20) | 0.859 (15/20) |

Lectura: el orden es muy estable frente al ancho de la curva (tau >= 0.93 con T = 7) y más sensible a T (tau entre 0.78 y 0.88 con T = 3 o 14). Por eso T no se puede decidir solo con matemáticas: es una decisión de política, cuántos días puede esperar una solicitud poco urgente antes de competir con las urgentes. Conviene fijarla con quien coordina las monitorías.

### 2.7 Alternativas consideradas

- **Suma ponderada normalizada con pesos por AHP.** Es un método reconocido: los pesos salen del vector propio de una matriz de comparaciones por pares y la matriz se acepta si su razón de consistencia es 0.1 o menos. Con un ejemplo ilustrativo de cuatro criterios (riesgo, impacto, espera, dificultad) se obtuvo 0.52, 0.20, 0.20 y 0.08, con razón de consistencia 0.016. Se descartó como modelo principal porque sigue siendo compensatoria y depende de juicios subjetivos que habría que levantar con los monitores. Queda como alternativa si la coordinación prefiere pesos explícitos.
- **Regla de Smith (razón entre peso y duración).** Es óptima para minimizar la suma ponderada de tiempos de finalización en una sola máquina cuando todas las tareas están disponibles desde el inicio. Con varios monitores y restricciones de horario solo sería una heurística, y no se implementó.

Fuentes consultadas: [suma ponderada y MCDM](https://en.wikipedia.org/wiki/Weighted_sum_model) y [su tratamiento en la literatura](https://arxiv.org/pdf/2509.06388); [envejecimiento en planificación](https://en.wikipedia.org/wiki/Aging_(scheduling)); [regla de Smith](https://metricgate.com/docs/wspt-smith-rule-single-machine/); [AHP y razón de consistencia](https://arxiv.org/pdf/2306.00718).

## 2.b Ponderación con el promedio acumulado

Cuando el estudiante pide una monitoría, el sistema le pide dos datos: su **nota actual en la materia** y su **promedio acumulado**. La nota de la materia es la mejor señal de si va a perderla, pero es ruidosa a mitad de semestre; el promedio acumulado dice qué tan bien le va en general. Se combinan en una *nota esperada*:

    nota_esperada = w · nota_materia + (1 − w) · promedio,   con w = 0.7

y el riesgo es el mismo de la sección 2: R = 1 / (1 + e^(k (nota_esperada − 3.0))).

Por qué esta forma:

- Es una **combinación convexa**: el resultado queda siempre entre la nota y el promedio, así que sigue dentro de [0, 5] y no hace falta rehacer las validaciones.
- Conserva la **monotonía**: con el promedio fijo, una nota más baja nunca da un riesgo menor (hay una prueba que lo comprueba para notas de 0 a 5).
- Si el promedio coincide con la nota, el resultado es exactamente el modelo anterior, así que el modelo nuevo **contiene** al viejo.
- Un buen promedio baja el riesgo y uno malo lo sube, que es lo que se espera de un estimador que usa más información.

El peso w = 0.7 es un **parámetro de diseño**, no un valor demostrado: se eligió para que la nota de la materia pese más que el historial. La sensibilidad, para un estudiante con promedio 4.0:

| w | riesgo con nota 2.0 | riesgo con nota 3.0 |
|---|---|---|
| 0.5 | 0.500 | 0.250 |
| 0.7 (elegido) | 0.707 | 0.341 |
| 0.9 | 0.853 | 0.445 |
| 1.0 (sin promedio) | 0.900 | 0.500 |

Si en el futuro hay datos reales de aprobación, w se puede ajustar por regresión; mientras tanto la tabla muestra cuánto cambia el resultado si el equipo prefiere otro valor.

**Qué no se pide:** una "urgencia" que el estudiante declare por sí mismo. Si la urgencia la escribe quien se beneficia de ella, todos pondrían el máximo y el orden de prioridad dejaría de tener sentido. Por eso la urgencia se calcula con datos (nota, promedio) y con la importancia de la materia en la malla, que el estudiante no puede modificar.

## 3. Árbol AVL como índice

Archivo: `monitorias/avl.py`. El sistema mantiene tres índices (personas, materias y solicitudes por urgencia) además de las tablas hash.

**Por qué dos estructuras.** La tabla hash busca por código en O(1) promedio, pero no sabe ordenar ni responder rangos. El AVL lista en orden sin ordenar (O(n)), responde rangos en O(log n + k) y busca en O(log n).

**Por qué balanceado.** `generador_codigos` produce códigos consecutivos (`e-0001`, `e-0002`, ...), que son el peor caso para un árbol binario de búsqueda: cada inserción cuelga a la derecha y el árbol se vuelve una lista. Medido con `scripts/benchmark_avl.py`:

| n | altura AVL | altura sin balancear | comparaciones AVL | comparaciones sin balancear | pasos hash |
|---|---|---|---|---|---|
| 10 | 4 | 10 | 4 | 10 | 1 |
| 100 | 7 | 100 | 7 | 100 | 2 |
| 500 | 9 | 500 | 9 | 500 | 1 |
| 1000 | 10 | 1000 | 10 | 1000 | 3 |
| 2000 | 11 | 2000 | 11 | 2000 | 2 |

La altura de un AVL con n nodos está acotada por 1.44 log2(n + 2), así que buscar nunca cuesta más de unas pocas comparaciones. Las propiedades se verifican con `es_bst()` y `es_avl()` en `tests/test_estructuras.py`, incluyendo 3000 inserciones y eliminaciones al azar contra un conjunto de referencia.

**Eliminación.** A diferencia de la inserción, una eliminación puede requerir más de una rotación en el camino hacia la raíz. Por eso `eliminar` revisa todo el camino y no se detiene en la primera rotación.

Las claves de los índices no son el texto del código sino la pareja (prefijo, número), para que el orden siga siendo correcto aunque se pase de `mat-9999` a `mat-10000` (hay una prueba para eso).

## 4. Grafo de prerrequisitos

Archivos: `monitorias/grafos.py` y `monitorias/prerrequisitos.py`.

**Modelo.** Grafo dirigido G = (V, E) donde cada vértice es una materia y hay una arista requisito -> materia. Debe ser acíclico. Cada arista nueva se valida antes de agregarse y se rechaza si crea un ciclo.

**Representación.** Se guarda como lista de adyacencia, con una lista de sucesores y otra de predecesores. La densidad es E / (V (V - 1)). En la malla de demostración es 19 / (18 x 17) = 0.062, así que la lista ocupa 37 celdas (V + E) frente a las 324 de la matriz (V al cuadrado). `justificar_representacion()` calcula esto y recomienda la matriz solo si la densidad pasa de 0.3. `a_matriz()` y `grafo_desde_matriz()` convierten entre ambas.

| Operación | Algoritmo | Costo |
|---|---|---|
| Islas desconectadas (componentes) | DFS sobre el grafo sin direcciones | O(V + E) |
| Detección de ciclos | DFS con tres estados (sin visitar, en proceso, terminado) | O(V + E) |
| Orden de cursado | Orden topológico (Kahn) | O(V + E) |
| Cadena de prerrequisitos más larga | Programación dinámica sobre el orden topológico | O(V + E) |
| Ruta más corta entre dos materias | BFS | O(V + E) |
| Diámetro (grados de separación) | BFS desde cada vértice | O(V (V + E)) |
| Impacto de reprobar una materia | BFS por olas sobre los dependientes | O(V + E) |
| Materias que dependen de otra | Alcanzables por BFS | O(V + E) |

**Por qué la cadena más larga es barata aquí.** El camino simple más largo en un grafo cualquiera es un problema NP-difícil, porque incluye como caso particular el camino hamiltoniano. En un grafo dirigido sin ciclos se resuelve en tiempo lineal recorriendo los vértices en orden topológico. Por eso el sistema puede dar siempre el mínimo de semestres necesarios (la longitud de esa cadena) sin riesgo de que el cálculo se dispare. Este es un modelo simplificado: supone que cada materia de la cadena debe cursarse en un semestre distinto y no considera límites de créditos.

**Verificación.** `tests/test_estructuras.py` compara el camino más largo contra fuerza bruta en 200 grafos acíclicos al azar, comprueba que el orden topológico respeta todas las aristas, y prueba los ciclos incluyendo el de dos vértices y el auto-ciclo. También se prueba un rombo (dos caminos al mismo destino), que no es un ciclo y no debe marcarse como tal.

## 5. Complejidad de las operaciones principales

n es el número de elementos de la estructura. V y E son vértices y aristas del grafo.

| Estructura u operación | Costo |
|---|---|
| Tabla hash: poner, obtener, eliminar | O(1) promedio, O(n) en el peor caso |
| AVL: insertar, buscar, eliminar | O(log n) |
| AVL: listar ordenado / rango con k resultados | O(n) / O(log n + k) |
| Montículo y cola de solicitudes: encolar, desencolar | O(log n) |
| Pila y cola FIFO: apilar, desapilar, encolar, desencolar | O(1) |
| Ordenamiento por inserción | O(n²) peor caso, O(n) si ya está casi ordenado |
| Ordenamiento por mezcla | O(n log n) |
| Ordenamiento rápido (tres vías, iterativo) | O(n log n) promedio, O(n²) peor caso, O(n) si todas las claves son iguales |
| Búsqueda binaria | O(log n) |
| Fusión de bloques de horario | O(b log b) por persona, con b bloques |
| Solicitar monitoría | O(V (V + E)) por recalcular `d_max`, más O(log n) de la cola |
| Asignar una solicitud | Lineal en el número de sesiones por cada hueco que se prueba |

## 6. Limitaciones conocidas

- Las anclas del modelo de riesgo y el valor de T son supuestos declarados, no estimaciones con datos reales.
- `d_max` se recalcula completo en cada solicitud; con mallas de cientos de materias convendría guardarlo y actualizarlo solo cuando cambie el grafo.
- La asignación de horarios es voraz: atiende en orden de prioridad y no busca el emparejamiento óptimo global entre estudiantes y monitores.
- La persistencia guarda el estado completo en un archivo JSON, sin control de acceso concurrente.
- El sistema es de consola; no tiene interfaz web.
