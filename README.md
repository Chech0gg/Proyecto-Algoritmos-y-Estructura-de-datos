# Proyecto-Algoritmos-y-Estructura-de-datos
# Acompañamiento académico y bienestar estudiantil

Proyecto de Algoritmos y Estructura de Datos, Universidad del Rosario.

Sistema para organizar las monitorias de una institución: registra estudiantes, monitores y materias, atiende las solicitudes por prioridad y arma la agenda de las sesiones.

## Integrantes

- Sergio Rios (@Chech0gg)
- Juan Esteban Ruiz (@jruizg17)

## Estructura

```
Entrega 1/                         documento, diagrama de flujo, presentación y primer código
Entrega 2/codigo entrega 2/
    CodigComp.py                   sistema completo con todos los temas juntos
    proyectosergiorios/            módulos de Sergio, uno por tema
    proyrctojuanruiz/              sistema de Juan
    Tabla_de_complejidad_Acompanamiento_Academico.xlsx
    Diagrama de clases
    imagen codacy proyecto
```

## Cómo ejecutar

Se necesita Python 3. Desde la carpeta `Entrega 2/codigo entrega 2`:

```
python CodigComp.py                                  # sistema completo
python proyectosergiorios/pila.py                    # un módulo de Sergio (igual con los otros tres)
python proyrctojuanruiz/codigocompl.py               # sistema de Juan
```

## Actualizaciones de cada integrante

### Sergio Rios

- **2 y 4 de septiembre:** creó el repositorio y subió la Entrega 1: el documento del proyecto, el diagrama de flujo, la presentación y el primer código.
- **17 y 18 de octubre:** subió el código de la Entrega 2 y lo reorganizó. Quedó el sistema completo (`CodigComp.py`) y cuatro módulos, uno por tema, en `proyectosergiorios`:
  - `recursionBacktraking.py`: cadena de prerrequisitos de una materia, con recursión y backtracking.
  - `Ordenamientos.py`: listados de solicitudes por urgencia, antigüedad o materia (inserción, mezcla y rápido).
  - `pila.py`: pila para revertir la última asignación de monitoria.
  - `conjuntoMapa.py`: áreas sin repetición y materias ya cursadas, con conjuntos y mapas.
- **18 y 19 de octubre:** subió la tabla de complejidad.

### Juan Esteban Ruiz

- **18 de octubre:** subió su sistema de monitorias (`proyrctojuanruiz`): tabla hash hecha a mano para buscar por código, cola de solicitudes por prioridad, agenda sin cruces de horario, lista de espera, informe de cobertura y pruebas. Está completo en `codigocompl.py` y también dividido en archivos por parte.
