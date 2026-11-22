# Sistema de monitorías (Entrega 3)

Sistema de apoyo académico que recibe solicitudes de monitoría, las prioriza con un modelo matemático documentado y arma una agenda sin cruces de horario. Reúne las estructuras de datos del curso: tabla hash, pila, colas, montículo, árboles (catálogo y AVL), grafos, conjuntos, ordenamientos y búsqueda.

## Requisitos y uso

Python 3.10 o superior. No necesita instalar nada para ejecutarlo.

```
python ejecutar.py                    # forma más simple: abre el menú con datos de demostración
python -m monitorias --demo            # equivalente
python -m monitorias datos.json        # abre el menú y guarda/carga en datos.json
```

Al abrir el sistema hay que **iniciar sesión**. Con `--demo` se cargan datos de ejemplo y estos usuarios (usuario / contraseña):

| Rol | Usuario | Contraseña |
|---|---|---|
| Administrador | `admin` | `admin123` |
| Monitor | `carlos`, `diana`, `hugo`, `laura` | su nombre + `123` (por ejemplo `carlos123`) |
| Estudiante | `ana`, `luis`, `sara`, `eva`, `beto`, `mateo`, `nora` | su nombre + `123` |

Cada rol ve un menú distinto:

- **Estudiante:** pide monitorías (indica su nota actual y su promedio; el sistema calcula la urgencia y la explica), ve y cancela sus solicitudes, ve su agenda, agrega y quita sus horarios.
- **Monitor:** agrega y quita sus horarios libres y las materias en las que se especializa, y ve sus sesiones.
- **Administrador:** genera la agenda, agenda a mano, modifica y cancela sesiones, ve los horarios de todos, crea y gestiona usuarios, y accede a las consultas de árboles, grafos e informes.

Un estudiante nuevo puede registrarse desde la pantalla de entrada; los monitores y administradores los crea el administrador. Si no hay usuarios, el sistema pide crear el primer administrador. Todo se guarda solo al cerrar sesión, en `monitorias.json` (no suba ese archivo al repositorio; para empezar de cero, bórrelo).

## Pruebas

```
pip install -r requirements-dev.txt
python -m unittest discover -s tests -t .                 # 183 pruebas
coverage run --branch -m unittest discover -s tests -t . && coverage report --include="monitorias/*"   # cobertura 97 %
python -m pyflakes monitorias tests scripts docs
```

Los scripts de evidencia de los modelos están en `scripts/`: `benchmark_avl.py` y `sensibilidad.py`.

## Estructura

| Carpeta o archivo | Contenido |
|---|---|
| `monitorias/` | El sistema, un módulo por tema |
| `tests/` | Pruebas unitarias, contra fuerza bruta y aleatorias de invariantes |
| `scripts/` | Benchmark del AVL y análisis de sensibilidad de la prioridad |
| `docs/cambios.md` | Qué se corrigió y agregó respecto a la Entrega 2, y cómo se verificó |
| `docs/modelos_matematicos.md` | Justificación de los modelos: prioridad, AVL, grafos y complejidad |
| `docs/diagrama_clases.png` | Diagrama de clases (se regenera con `python docs/generar_diagrama.py`, requiere `requirements-docs.txt`) |
| `.github/workflows/` (en la raíz del repositorio) | CI y CD |

## CI/CD

**CI** (`.github/workflows/ci.yml`): en cada push o pull request a `main` se ejecutan el análisis estático y las pruebas con cobertura en Python 3.10, 3.11 y 3.12. El flujo falla si hay pruebas rotas o si la cobertura baja de 90 %.

**CD** (`.github/workflows/cd.yml`): al subir una etiqueta que empiece por `v`, se vuelven a correr las pruebas y, si pasan, se publica un Release de GitHub con el `.zip` del sistema y una imagen Docker en GitHub Container Registry.

```
git tag v1.0.0
git push origin v1.0.0
docker run -it -v "$PWD/datos:/datos" ghcr.io/<usuario>/<repositorio>:v1.0.0 /datos/monitorias.json --demo
```

### Pasos que se hacen a mano en GitHub

1. Subir estos archivos a la rama `main`.
2. En *Settings, Branches, Add branch protection rule* para `main`, activar *Require a pull request before merging* y *Require status checks to pass before merging*, y elegir como obligatorias las comprobaciones `pruebas (3.10)`, `pruebas (3.11)` y `pruebas (3.12)`. Así ningún cambio llega a `main` si las pruebas fallan.
3. En *Settings, Actions, General, Workflow permissions*, permitir lectura y escritura para que el flujo de CD pueda publicar el Release y la imagen.

Los flujos y el `Dockerfile` están escritos y sus YAML son válidos, pero no se pudieron ejecutar fuera de GitHub.
