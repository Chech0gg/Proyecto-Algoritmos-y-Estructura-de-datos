# Cambios respecto a la Entrega 2

Cada cambio indica qué estaba mal (con la evidencia con que se detectó), cómo se corrigió y qué prueba lo verifica.

## A. Errores de la Entrega 2 que se corrigieron

| # | Qué estaba mal | Cómo se corrigió | Prueba |
|---|---|---|---|
| 1 | **Bloques de horario contiguos no se unían.** Un monitor libre de 08:00 a 09:00 y de 09:00 a 10:00 se trataba como dos bloques separados, y un estudiante libre de 08:30 a 09:30 quedaba en espera aunque compartían una hora entera | `fusionar_bloques` une los bloques contiguos o solapados de cada día antes de buscar huecos y de comprobar disponibilidad (`tiempo.py`, `sistema.py`) | `test_fusion_de_bloques_contiguos_y_solapados`, `test_bloques_contiguos_se_tratan_como_uno_solo` |
| 2 | **Una asignación revertida a propósito se reasignaba sola** al registrar cualquier monitor o disponibilidad | Las solicitudes revertidas llevan la marca `revertida` y la lista de espera las salta. Para volver a intentarlas hay que pedirlo con `reencolar` | `test_lo_revertido_no_se_reasigna_solo`, `test_reencolar_solo_acepta_revertidas` |
| 3 | **Revertir liberaba un hueco pero nadie lo aprovechaba**: la lista de espera no se reintentaba | Después de revertir se reintenta la lista de espera (sin las revertidas) | `test_al_revertir_el_hueco_pasa_a_quien_esperaba` |
| 4 | **`orden_atencion` guardaba ids repetidos** (por ejemplo `[1, 1]`) y no se actualizaba al revertir | Ahora contiene solo las asignaciones vigentes, en orden, y se actualiza al revertir | `test_orden_de_atencion_sin_repetidos_y_actualizado` |
| 5 | **El ordenamiento rápido se caía con claves iguales**: 2000 claves iguales daban `RecursionError` | Partición en tres vías y sin recursión (usa una lista de rangos pendientes) | `test_quicksort_con_claves_iguales_no_se_cae` (20 000 claves) |
| 6 | **Validaciones incompletas**: pasar `"3"` o `None` daba `TypeError` o `AttributeError` en vez de `error_validacion`; `"8:5"` se aceptaba como hora; `"Lunes"` se rechazaba | Módulo `validaciones.py` con entero, decimal y texto. Las horas exigen `hh:mm`, los días aceptan mayúsculas y tildes y `24:00` solo vale como hora de fin | `prueba_validaciones`, `test_entradas_de_tipo_incorrecto_son_errores_de_validacion`, `test_horas_invalidas` |
| 7 | **No se controlaban solicitudes duplicadas**: un estudiante que pedía 4 veces la misma materia recibía 4 sesiones | Una solicitud activa por estudiante y materia, comprobada en O(1) con una tabla hash | `test_solicitudes_duplicadas_se_rechazan` |
| 8 | **La tabla hash no podía eliminar**, fallaba con claves que no eran texto y `contiene` fallaba con valores `None` | Se agregó `eliminar`, `pasos`, `items`, `claves`; las claves se validan y `contiene` ya no depende del valor | `prueba_tabla_hash` |
| 9 | **Los prerrequisitos no se exigían** al solicitar | Se exige haber cursado los prerrequisitos directos de la materia (se puede desactivar con `exigir_prerrequisitos=False`) | `test_se_exigen_los_prerrequisitos_directos` |
| 10 | **La antigüedad se medía por número de llegada**, no por fecha | Cada solicitud guarda su instante de llegada (el reloj se puede inyectar, lo que permite probar el envejecimiento) | `test_envejecimiento_con_reloj_inyectado` |
| 11 | **Se consumían códigos aunque el registro fallara** (quedaban huecos como `mat-0002`) | Se valida antes de generar el código | `test_codigos_consecutivos_y_sin_huecos_si_falla_la_validacion` |
| 12 | **Todo se perdía al cerrar el programa** | Persistencia en JSON: guardar y cargar devuelve exactamente el mismo estado, incluido el historial de asignaciones y las solicitudes revertidas | `prueba_persistencia` (compara los diccionarios completos) |
| 13 | **La Entrega 1 se caía con `"tres"` o `"4,5"`** y aceptaba semestre -7 o promedio 9.9 | El menú de consola valida cada dato y vuelve a preguntar; acepta coma o punto decimal | `test_entradas_invalidas_se_vuelven_a_pedir`, `test_nota_con_coma_decimal` |
| 14 | **El código estaba triplicado** (en `CodigComp.py`, en los módulos de Sergio y en los de Juan) y `pruebas.py` no podía importar nada por un nombre de carpeta mal escrito | Un solo paquete `monitorias/` con un módulo por tema, y `tests/` que se ejecuta con un solo comando | toda la suite |
| 15 | **El diagrama de clases mostraba clases que no existían** (`ArbolMaterias`, herencia desde `Persona`) y omitía las nuevas | `clase_persona` ahora existe y es la base de estudiante, monitor y profesor; el diagrama se genera desde una definición que se verifica contra el código | `tests/test_diagrama.py` |

## B. Lo que se agregó

| Tema | Qué se implementó | Dónde |
|---|---|---|
| Fórmula de prioridad | Reemplazo completo por riesgo x impacto con envejecimiento. Justificación en `modelos_matematicos.md` | `prioridad.py`, `cola_solicitudes.py` |
| Montículo binario | Cola de prioridad con clave fija; reemplaza las tres filas por nivel | `monticulo.py` |
| Árbol de catálogo | Jerarquía área -> materia, con `imprimir_jerarquia`, espejo (vista inversa) y `son_iguales` | `arboles.py` |
| Árbol AVL | Índices por código y por urgencia, con listado ordenado, búsqueda con conteo de comparaciones, rangos, eliminación y verificación de las propiedades | `avl.py` |
| Grafo de prerrequisitos | Grafo dirigido con lista y matriz, densidad, islas (DFS), ciclos (tres estados), orden topológico, cadena más larga, ruta más corta, diámetro e impacto por olas (BFS) | `grafos.py`, `prerrequisitos.py` |
| Búsqueda binaria | Búsqueda de una solicitud por número | `ordenamientos.py` |
| Cola FIFO | Notificaciones de asignación y cancelación | `listas.py`, `sistema.py` |
| Menú de consola | Menús por rol (estudiante, monitor, administrador) con validación de entradas | `cli.py` |
| Persistencia | Guardado atómico y carga con validación de cada referencia | `persistencia.py` |
| CI/CD | Pruebas y análisis en cada cambio; publicación de versión e imagen Docker al crear una etiqueta | `.github/workflows/` |

## C. Cómo se verificó

- `python -m unittest discover -s tests -t .` ejecuta toda la suite, con pruebas unitarias, pruebas contra fuerza bruta (camino más largo, rangos, orden) y una prueba aleatoria de invariantes: con 150 configuraciones al azar de monitores, estudiantes y solicitudes, después de asignar y de revertir nunca hay cruces de horario, cupos excedidos ni sesiones fuera de la disponibilidad.
- `python -m pyflakes monitorias tests scripts docs` no reporta nada.
- El código es compatible con Python 3.10 a 3.12 (el CI prueba las tres versiones).

## E. Inicio de sesión y roles (agregado después de la revisión del equipo)

El equipo pidió que el sistema distinga entre estudiante, monitor y administrador. Lo que cambió:

**Código nuevo**

- `monitorias/cuentas.py`: cuentas de usuario. La contraseña se guarda con sal y hash PBKDF2-SHA256 (nunca en claro); la cuenta se bloquea al tercer intento fallido; el mensaje de error es el mismo si el usuario no existe o la clave es mala, para no revelar qué usuarios existen.
- `monitorias/gestion.py`: las operaciones de los tres paneles (cancelar solicitudes, agendar a mano, modificar y cancelar sesiones, horarios, especialidades, vistas de agenda).
- `monitorias/cli.py`: pantalla de entrada (iniciar sesión, registrarse como estudiante, salir) y un menú distinto por rol.

**Qué ve cada rol**

| Rol | Opciones |
|---|---|
| Estudiante | Pedir monitoría (con nota actual y promedio), ver y cancelar sus solicitudes, ver su agenda, agregar y quitar sus horarios, ver materias con monitor, ver prerrequisitos faltantes, cambiar contraseña |
| Monitor | Agregar y quitar horarios libres, agregar y quitar las materias que apoya, ver sus sesiones, cambiar contraseña |
| Administrador | Generar la agenda, agendar a mano, modificar y cancelar sesiones, ver horarios de todos, gestionar usuarios, cancelar solicitudes, materias y malla, informes, guardar y cargar |

**Reglas de seguridad**

- Un estudiante solo puede registrarse a sí mismo; los monitores y administradores los crea el administrador.
- Cada rol solo ejecuta las opciones de su menú; un número fuera de su menú da "opcion no valida".
- Un estudiante solo puede cancelar sus propias solicitudes y solo pide monitorías con su propio código (no elige a quién).
- La primera vez que se abre el sistema, sin usuarios, se pide crear el administrador.

**Cambios en lo que ya existía**

- `solicitar` recibe también el promedio acumulado y `calcular_prioridad` lo usa (ver `modelos_matematicos.md`, sección 2.b).
- `cola_solicitudes.quitar` y `monticulo.quitar` permiten sacar una solicitud de la cola al cancelarla o agendarla a mano.
- Estado nuevo de solicitud, `cancelada`: no cuenta en el informe de cobertura, no aparece en el rango de urgencia y libera al estudiante para pedir de nuevo la misma materia.
- Al revertir la asignación del último estudiante de una sesión se elimina la sesión vacía (antes podía quedar sesión sin estudiantes).
- El archivo JSON guarda las cuentas y el promedio; los archivos de la versión anterior (sin cuentas) se siguen cargando y, al abrirlos, el sistema pide crear el administrador.
- El sistema guarda solo al cerrar sesión o salir.

**Verificación:** 183 pruebas (50 nuevas de cuentas, roles, paneles y persistencia), cobertura 97 %.

**Límites**

- No hay recuperación de contraseña por correo: la restablece el administrador.
- La contraseña se pide oculta en la terminal normal; algunos entornos (por ejemplo, ciertas consolas de depuración) la muestran en pantalla.
- La contraseña y el hash viajan en el archivo `monitorias.json`: no se debe publicar ese archivo en el repositorio.

## D. Qué no se pudo verificar aquí

- Los flujos de GitHub Actions (`ci.yml` y `cd.yml`) y el `Dockerfile` están escritos y los YAML son válidos, pero no se ejecutaron: hace falta subirlos a GitHub. La protección de la rama `main` es una configuración del repositorio y se hace a mano (ver el README).
