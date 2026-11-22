# Acompañamiento académico y bienestar estudiantil

Proyecto de **Algoritmos y Estructuras de Datos**, Universidad del Rosario.

Sistema de consola que organiza las monitorías: los estudiantes piden monitorías, el sistema calcula la urgencia de cada solicitud con un modelo matemático y el administrador arma una agenda sin cruces de horario. Cada persona entra con usuario y contraseña y ve solo las opciones de su rol.

## Integrantes

- Sergio Rios (@Chech0gg)
- Juan Esteban Ruiz (@jruizg17)

## Cómo ejecutarlo (Entrega 3)

Requiere **Python 3.10 o superior**. No hay que instalar nada más.

1. Abra la carpeta del repositorio en Visual Studio Code y abra la terminal.
2. Entre a la carpeta `Entrega 3` y ejecute:

```
cd "Entrega 3"
python ejecutar.py
```

En Windows, si `python` no funciona, use `py ejecutar.py`; en Mac o Linux, `python3 ejecutar.py`. El comando se ejecuta en `Entrega 3`, no dentro de `monitorias`.

| Comando | Qué hace |
|---|---|
| `python ejecutar.py` | Abre el sistema con datos de demostración |
| `python -m monitorias` | Abre el sistema vacío; pide crear el primer administrador |
| `python -m monitorias datos.json` | Usa `datos.json` para guardar y cargar |

Los datos se guardan solos al cerrar sesión en `monitorias.json`. Para empezar de cero, bórrelo.

## Usuarios de demostración

| Rol | Usuarios | Contraseña |
|---|---|---|
| Administrador | `admin` | `admin123` |
| Monitor | `carlos`, `diana`, `hugo`, `laura` | su nombre + `123` (ej. `carlos123`) |
| Estudiante | `ana`, `luis`, `sara`, `eva`, `beto`, `mateo`, `nora` | su nombre + `123` |

La contraseña no se ve al escribirla; es normal. Un estudiante nuevo puede registrarse desde la pantalla de entrada. Monitores y administradores los crea el administrador.

## Qué hace cada rol

En los menús se escribe el número de la opción; `0` cierra la sesión.

- **Estudiante:** pide una monitoría (elige materia, tipo, nota actual y promedio; el sistema calcula y explica la urgencia), ve y cancela sus solicitudes, ve su agenda, gestiona sus horarios libres, consulta materias, monitores y prerrequisitos faltantes, y cambia su contraseña.
- **Monitor:** agrega y quita sus horarios libres y las materias en las que se especializa, ve sus sesiones y cambia su contraseña.
- **Administrador:** genera la agenda automática, agenda a mano, modifica y cancela sesiones, ve los horarios de monitores y estudiantes, gestiona solicitudes (cola, lista de espera, orden por urgencia, rango, revertir y reintentar), crea y gestiona usuarios (desbloquear y restablecer contraseñas), administra materias y prerrequisitos (catálogo, red, rutas, impacto, plan de cursado) y consulta informes.

**Flujo básico:** el estudiante agrega sus horarios y pide la monitoría; el monitor agrega horarios y especialidades; el administrador genera la agenda (opción 1) y la ve (opción 2). Con los datos de demostración queda así:

```
lunes      08:00-09:00 | par     | calculo i | monitor: carlos | estudiantes: ana
lunes      10:00-10:30 | puntual | fisica i | monitor: hugo | estudiantes: sara
martes     08:00-08:30 | puntual | programacion i | monitor: laura | estudiantes: luis
miercoles  10:00-11:30 | general | estructuras de datos | monitor: diana | estudiantes: eva
jueves     09:00-10:30 | general | algoritmos | monitor: diana | estudiantes: nora, mateo
```

Lo que no se puede agendar queda en la lista de espera con el motivo.

## Formatos que pide el programa

| Dato | Formato | Ejemplo |
|---|---|---|
| Horario | `día hh:mm hh:mm` (lunes a sábado, pasos de 30 min); Enter vacío para terminar | `lunes 08:00 12:00` |
| Tipo de monitoría | `par` (60 min, 1 estudiante), `general` (90 min, hasta 5), `puntual` (30 min, 1 duda) | `par` |
| Nota y promedio | de 0 a 5, con punto o coma | `3.4` |
| Materia | número de la lista o código | `2` o `mat-0002` |

## Cómo se calcula la prioridad

1. **Nota esperada** = 0,7 · nota actual + 0,3 · promedio acumulado.
2. **Riesgo** de reprobar: función logística; nota 3,0 → 50 %, 2,0 → 90 %, 4,0 → 10 %.
3. **Impacto**: crece con el número de materias que dependen de la solicitada (grafo de prerrequisitos).
4. **Urgencia** = riesgo × impacto. Con el tiempo de espera la solicitud gana peso, para que ninguna se quede atrás.

El estudiante no declara la urgencia; la calcula el sistema. Detalle y justificación: `Entrega 3/docs/modelos_matematicos.md`.

## Estructuras de datos

Tabla hash (búsqueda por código), pila (revertir asignación), colas, montículo binario (cola de prioridad), conjuntos y mapas, árbol general (catálogo), AVL (índice ordenado), grafo dirigido (prerrequisitos: DFS, BFS, orden topológico), recursión y backtracking, ordenamientos (inserción, mezcla, rápido) y búsqueda binaria.

## Seguridad

Contraseñas con hash PBKDF2-SHA256 y sal (nunca en texto plano), mensaje de error igual para usuario inexistente o contraseña incorrecta, bloqueo tras 3 intentos fallidos (el administrador desbloquea), mínimo 6 caracteres sin espacios.

## Pruebas y calidad

Desde `Entrega 3`:

```
pip install -r requirements-dev.txt
python -m unittest discover -s tests -t .                                      # 183 pruebas
coverage run --branch -m unittest discover -s tests -t .
coverage report --include="monitorias/*"                                       # cobertura 97 %
python -m pyflakes monitorias tests scripts docs
```

## CI/CD y Docker

- **CI** (`.github/workflows/ci.yml`): en cada push o pull request a `main` corre el análisis estático y las pruebas en Python 3.10, 3.11 y 3.12; falla si la cobertura baja de 90 %.
- **CD** (`.github/workflows/cd.yml`): al subir una etiqueta `v*` (por ejemplo `git tag v1.0.0` y `git push origin v1.0.0`) repite las pruebas y publica un Release con el `.zip` y una imagen Docker.
- **Docker:** `docker build -t monitorias "Entrega 3"` y `docker run -it monitorias --demo`.

La carpeta `.github/` debe estar en la raíz del repositorio. En *Settings → Actions → General → Workflow permissions* hay que permitir lectura y escritura para que el CD pueda publicar.

## Estructura del repositorio

```
Entrega 1/                documento, diagrama de flujo, presentación y primer código
Entrega 2/                código de la Entrega 2, tabla de complejidad y diagrama de clases
Entrega 3/
    ejecutar.py           archivo para ejecutar el sistema
    monitorias/           el sistema, un módulo por tema (cli, sistema, gestion, cuentas, prioridad, agenda, avl, grafos...)
    tests/                183 pruebas
    scripts/              benchmark del AVL y sensibilidad de la prioridad
    docs/                 cambios, modelos matemáticos y diagrama de clases
    Dockerfile
.github/workflows/        CI y CD
```

## Problemas frecuentes

| Síntoma | Solución |
|---|---|
| `No module named monitorias` | Está en la carpeta equivocada; entre a `Entrega 3` |
| Solo veo la carpeta `monitorias` | Esa carpeta guarda los módulos; el archivo que se ejecuta es `ejecutar.py` |
| Cuenta bloqueada | Un administrador la desbloquea (opción 21 de su menú) |
| Olvidé la contraseña | Un administrador la restablece (opción 22); si fue la del administrador, borre `monitorias.json` |
| Mi solicitud queda en espera | No hay monitor de esa materia o los horarios no coinciden; agregue horarios (estudiante) o especialidades y horarios (monitor) |
| Salen datos raros | Borre `monitorias.json` y ejecute de nuevo |

## Límites conocidos

- La nota y el promedio los escribe el estudiante; el sistema no puede verificarlos.
- Los horarios son por día de la semana, no por fecha de calendario.
- Es una aplicación de consola con un solo archivo JSON de datos.
- Los flujos de CI/CD están escritos pero aún no se han ejecutado en GitHub.

## Historial de cada integrante

**Sergio Rios:** creó el repositorio y subió la Entrega 1 (2 y 4 de septiembre); subió y reorganizó el código de la Entrega 2 con sus cuatro módulos (recursión y backtracking, ordenamientos, pila, conjuntos y mapas) y la tabla de complejidad (17 al 19 de octubre).

**Juan Esteban Ruiz:** subió su sistema de monitorías de la Entrega 2 (18 de octubre): tabla hash, cola de solicitudes por prioridad, agenda sin cruces, lista de espera, informe de cobertura y pruebas.
