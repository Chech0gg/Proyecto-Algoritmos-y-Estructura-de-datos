import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from definicion_diagrama import cajas, posiciones as posiciones_fijas, relaciones

ancho_lienzo = 32.0
alto_lienzo = 19.0
tamano_letra = 7.2
ancho_caracter = 0.70 * tamano_letra / 72
alto_linea = 1.32 * tamano_letra / 72
margen = 0.10

colores = {
    "fachada": ("#fde68a", "#92400e"),
    "dominio": ("#dbeafe", "#1e3a8a"),
    "estructura": ("#dcfce7", "#166534"),
    "modulo": ("#f3e8ff", "#6b21a8"),
    "excepcion": ("#fee2e2", "#991b1b"),
}
etiquetas_estilo = {
    "fachada": "fachada del sistema",
    "dominio": "clases del dominio",
    "estructura": "estructuras de datos",
    "modulo": "modulos y consola",
    "excepcion": "excepcion",
}


def etiqueta_de(nombre, datos):
    if datos["estilo"] == "modulo" and nombre != "consola":
        return "<<modulo>> " + nombre
    return nombre


def medir(nombre, datos):
    atributos = datos["atributos"]
    metodos = datos["metodos"]
    largo = max([len(etiqueta_de(nombre, datos)) * 1.12] + [len(x) for x in atributos + metodos])
    ancho = largo * ancho_caracter + 2 * margen + 0.1
    alto = 2 * margen + alto_linea * (1 + max(len(atributos), 1) + max(len(metodos), 1)) + 0.6 * alto_linea
    return ancho, alto


def posicionar():
    posiciones = {}
    for nombre, datos in cajas.items():
        x, y = posiciones_fijas[nombre]
        ancho, alto = medir(nombre, datos)
        posiciones[nombre] = (x, y, ancho, alto)
    return posiciones


def borde(caja, destino):
    cx, cy, ancho, alto = caja
    dx = destino[0] - cx
    dy = destino[1] - cy
    if dx == 0 and dy == 0:
        return cx, cy
    tx = (ancho / 2) / abs(dx) if dx != 0 else float("inf")
    ty = (alto / 2) / abs(dy) if dy != 0 else float("inf")
    t = min(tx, ty)
    return cx + dx * t, cy + dy * t


def dibujar_caja(eje, nombre, caja, datos):
    cx, cy, ancho, alto = caja
    relleno, trazo = colores[datos["estilo"]]
    izquierda = cx - ancho / 2
    derecha = cx + ancho / 2
    eje.add_patch(Rectangle((izquierda, cy - alto / 2), ancho, alto, facecolor=relleno, edgecolor=trazo,
                            linewidth=1.1, zorder=3))
    y = cy + alto / 2 - margen
    eje.text(cx, y - alto_linea / 2, etiqueta_de(nombre, datos), ha="center", va="center", fontsize=tamano_letra,
             fontweight="bold", family="monospace", color=trazo, zorder=5)
    y -= alto_linea
    eje.plot([izquierda, derecha], [y - 0.15 * alto_linea] * 2, color=trazo, linewidth=0.7, zorder=4)
    y -= 0.3 * alto_linea
    for atributo in datos["atributos"] or [""]:
        eje.text(izquierda + margen, y - alto_linea / 2, atributo, ha="left", va="center", fontsize=tamano_letra,
                 family="monospace", color="#111827", zorder=5)
        y -= alto_linea
    eje.plot([izquierda, derecha], [y - 0.15 * alto_linea] * 2, color=trazo, linewidth=0.7, zorder=4)
    y -= 0.3 * alto_linea
    for metodo in datos["metodos"] or [""]:
        eje.text(izquierda + margen, y - alto_linea / 2, metodo, ha="left", va="center", fontsize=tamano_letra,
                 family="monospace", color="#111827", zorder=5)
        y -= alto_linea


def unitario(p, q):
    dx = q[0] - p[0]
    dy = q[1] - p[1]
    largo = math.hypot(dx, dy) or 1.0
    return dx / largo, dy / largo


def dibujar_relacion(eje, posiciones, origen, destino, tipo, texto, multiplicidad):
    a = posiciones[origen]
    b = posiciones[destino]
    p0 = borde(a, (b[0], b[1]))
    p1 = borde(b, (a[0], a[1]))
    ux, uy = unitario(p0, p1)
    nx, ny = -uy, ux
    estilo = "--" if tipo == "dependencia" else "-"
    color = "#374151"
    inicio = p0
    fin = p1
    largo = 0.20
    ancho = 0.075
    if tipo in ("composicion", "agregacion"):
        punta = (p0[0] + ux * largo, p0[1] + uy * largo)
        centro = (p0[0] + ux * largo / 2, p0[1] + uy * largo / 2)
        rombo = [p0, (centro[0] + nx * ancho, centro[1] + ny * ancho), punta,
                 (centro[0] - nx * ancho, centro[1] - ny * ancho)]
        eje.add_patch(Polygon(rombo, closed=True, facecolor=color if tipo == "composicion" else "white",
                              edgecolor=color, linewidth=0.9, zorder=6))
        inicio = punta
    if tipo == "herencia":
        base = (p1[0] - ux * largo * 1.2, p1[1] - uy * largo * 1.2)
        triangulo = [p1, (base[0] + nx * ancho * 1.3, base[1] + ny * ancho * 1.3),
                     (base[0] - nx * ancho * 1.3, base[1] - ny * ancho * 1.3)]
        eje.add_patch(Polygon(triangulo, closed=True, facecolor="white", edgecolor=color, linewidth=0.9, zorder=6))
        fin = base
    if tipo in ("asociacion", "dependencia"):
        base = (p1[0] - ux * largo, p1[1] - uy * largo)
        eje.plot([base[0] + nx * ancho, p1[0], base[0] - nx * ancho], [base[1] + ny * ancho, p1[1], base[1] - ny * ancho],
                 color=color, linewidth=0.9, zorder=6)
    eje.plot([inicio[0], fin[0]], [inicio[1], fin[1]], linestyle=estilo, color=color, linewidth=0.9, zorder=2)
    if multiplicidad:
        eje.text(p1[0] - ux * 0.32 + nx * 0.14, p1[1] - uy * 0.32 + ny * 0.14, multiplicidad, fontsize=6.2,
                 color="#b91c1c", ha="center", va="center", zorder=7)
    if texto:
        mx = (p0[0] + p1[0]) / 2
        my = (p0[1] + p1[1]) / 2
        eje.text(mx, my, texto, fontsize=6.0, color="#4b5563", ha="center", va="center", style="italic", zorder=7,
                 bbox={"facecolor": "white", "edgecolor": "none", "pad": 0.4, "alpha": 0.85})


def generar(ruta_salida):
    figura, eje = plt.subplots(figsize=(ancho_lienzo, alto_lienzo), dpi=100)
    eje.set_xlim(0, ancho_lienzo)
    eje.set_ylim(0, alto_lienzo)
    eje.axis("off")
    posiciones = posicionar()
    for origen, destino, tipo, texto, m_origen, m_destino in relaciones:
        dibujar_relacion(eje, posiciones, origen, destino, tipo, texto, m_destino)
    for nombre, datos in cajas.items():
        dibujar_caja(eje, nombre, posiciones[nombre], datos)
    eje.text(0.4, alto_lienzo - 0.4, "diagrama de clases - sistema de monitorias (entrega 3)", fontsize=14,
             fontweight="bold", color="#111827", va="center")
    x = 0.4
    for estilo, (relleno, trazo) in colores.items():
        eje.add_patch(Rectangle((x, alto_lienzo - 1.05), 0.32, 0.22, facecolor=relleno, edgecolor=trazo, linewidth=1))
        eje.text(x + 0.42, alto_lienzo - 0.94, etiquetas_estilo[estilo], fontsize=7.5, va="center", color="#111827")
        x += 3.0
    leyenda = "rombo negro: composicion | rombo blanco: agregacion | triangulo blanco: herencia | flecha: asociacion | punteada: dependencia"
    eje.text(ancho_lienzo - 0.4, alto_lienzo - 0.94, leyenda, fontsize=7.5, va="center", ha="right", color="#374151")
    figura.savefig(ruta_salida, bbox_inches="tight", pad_inches=0.2, facecolor="white")
    plt.close(figura)


if __name__ == "__main__":
    destino = os.path.join(os.path.dirname(os.path.abspath(__file__)), "diagrama_clases.png")
    generar(destino)
    print("diagrama guardado en", destino)
