import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from monitorias.avl import indice_avl
from monitorias.modelos import generador_codigos
from monitorias.tabla_hash import tabla_hash


def medir(n):
    generador = generador_codigos()
    codigos = [generador.nuevo("e") for _ in range(n)]
    balanceado = indice_avl(balanceado=True)
    simple = indice_avl(balanceado=False)
    tabla = tabla_hash()
    for codigo in codigos:
        clave = (codigo.split("-")[0], int(codigo.split("-")[1]))
        balanceado.insertar(clave, codigo)
        simple.insertar(clave, codigo)
        tabla.poner(codigo, codigo)
    ultimo = codigos[-1]
    clave_ultimo = ("e", n)
    return {
        "n": n,
        "altura_avl": balanceado.altura() + 1,
        "cota_teorica": math.floor(1.4405 * math.log2(n + 2)),
        "altura_sin_balancear": simple.altura() + 1,
        "comparaciones_avl": balanceado.buscar(clave_ultimo)[1],
        "comparaciones_sin_balancear": simple.buscar(clave_ultimo)[1],
        "pasos_hash": tabla.pasos(ultimo),
        "rotaciones": balanceado.rotaciones,
    }


def main():
    print("insercion de codigos consecutivos (e-0001, e-0002, ...), como los genera el sistema")
    print(f"{'n':>6} {'h avl':>6} {'cota':>5} {'h sin balancear':>16} {'comp avl':>9} {'comp sin bal.':>14} {'hash':>5} {'rotaciones':>11}")
    for n in (10, 100, 500, 1000, 2000):
        r = medir(n)
        print(f"{r['n']:>6} {r['altura_avl']:>6} {r['cota_teorica']:>5} {r['altura_sin_balancear']:>16} "
              f"{r['comparaciones_avl']:>9} {r['comparaciones_sin_balancear']:>14} {r['pasos_hash']:>5} {r['rotaciones']:>11}")


if __name__ == "__main__":
    main()
